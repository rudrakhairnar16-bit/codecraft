from __future__ import annotations

import json as _json
import time
from pathlib import Path
from typing import Any

import typer
from rich.table import Table
from rich.tree import Tree

from codecraft.cli.deps import get_repo
from codecraft.db.repository import Repository
from codecraft.engines.debt_tracker import DebtTrackerEngine
from codecraft.models.file import FileRecord
from codecraft.scanner.ast_parser import file_hash, file_stats
from codecraft.scanner.multilang import Language, LanguageDetector
from codecraft.scanner.unified import UnifiedScanner
from codecraft.utils.colors import console

_IGNORE_DIRS: set[str] = {".git", "node_modules", "__pycache__", "venv", ".venv", "env", ".env", ".tox", "build", "dist", ".eggs", "eggs", "__pypackages__"}


def _load_gitignore(path: Path) -> list[str] | None:
    gitignore = path / ".gitignore"
    if not gitignore.exists():
        return None
    try:
        return [line.strip() for line in gitignore.read_text(encoding="utf-8", errors="replace").splitlines()
                if line.strip() and not line.strip().startswith("#")]
    except Exception:
        return None


def _is_ignored(file: Path, gitignore_patterns: list[str] | None) -> bool:
    if any(part in _IGNORE_DIRS for part in file.parts):
        return True
    if any(part.startswith(".") for part in file.parts):
        return True
    if gitignore_patterns:
        try:
            import pathspec
            spec = pathspec.PathSpec.from_lines("gitwildmatch", gitignore_patterns)
            if spec.match_file(str(file)):
                return True
        except Exception:
            pass
    return False


def _is_changed(repo: Any, file: Path) -> bool:
    from codecraft.models.file import FileRecord
    stored = repo.files.get(file)
    if stored is None:
        return True
    try:
        current = file_hash(file)
    except Exception:
        return True
    return stored.hash != current
from rich.progress import Progress

scan_app = typer.Typer(name="scan", no_args_is_help=True)


@scan_app.command("dir", epilog="Example: codecraft scan dir . --dry-run")
def scan_directory(
    path: Path = typer.Argument(".", help="Directory to scan"),
    recursive: bool = typer.Option(True, "-r", "--recursive", help="Scan recursively"),
    watch: bool = typer.Option(False, "-w", "--watch", help="Watch for file changes"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview without persisting"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
    no_gitignore: bool = typer.Option(False, "--no-gitignore", help="Ignore .gitignore rules"),
    incremental: bool = typer.Option(False, "--incremental", "-i", help="Skip files with unchanged hash"),
) -> None:
    supported_exts = set(LanguageDetector.supported_extensions())
    _patterns = ["**/*"] if recursive else ["*"]
    scanner = UnifiedScanner()
    repo = get_repo()

    gitignore_patterns = None if no_gitignore else _load_gitignore(Path(path))

    files = []
    for p in Path(path).rglob("*") if recursive else Path(path).glob("*"):
        if p.suffix.lower() in supported_exts and p.is_file() and not _is_ignored(p, gitignore_patterns):
            files.append(p)
    files.sort()

    if incremental:
        before = len(files)
        files = [f for f in files if _is_changed(repo, f)]
        skipped = before - len(files)
    else:
        skipped = 0

    if not files:
        exts = ", ".join(supported_exts)
        console.print(f"[warning]No supported files ({exts}) found in {path}[/warning]")
        raise typer.Exit()

    if not json_output:
        lang_count = len([f for f in files if f.suffix == ".py"])
        other_count = len(files) - lang_count
        msg = f"[title]Scanning {len(files)} files ({lang_count} Python, {other_count} other)"
        if skipped:
            msg += f", {skipped} skipped (unchanged)"
        msg += "...[/title]"
        console.print(msg)

    scanned = 0
    progress: Progress | None = None
    task_id: Any = None
    if not json_output and not dry_run:
        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            transient=True,
        )
        progress.start()
        task_id = progress.add_task("Scanning...", total=len(files))

    for file in files:
        try:
            report = scanner.scan_file(file)
        except Exception as e:
            console.print(f"[error]Failed to scan {file}: {e}[/error]")
            if progress and task_id is not None:
                progress.advance(task_id)
            continue
        if report and not report.errors:
            fhash = file_hash(file)
            size, lines = file_stats(file)

            if dry_run:
                console.print(f"  [dim]{file}[/dim] - {len(report.concepts)} concepts, {len(report.debt_items)} debts")
                scanned += 1
                if progress and task_id is not None:
                    progress.advance(task_id)
                continue

            record = FileRecord(
                path=file,
                hash=fhash,
                size=size,
                lines=lines,
            )
            record.complexity = report.complexity
            record.import_count = len(report.imports)
            repo.upsert_file(record)

            lang = LanguageDetector.detect(str(file))
            if lang == Language.PYTHON:
                import ast
                source = file.read_text(encoding="utf-8", errors="replace")
                try:
                    tree = ast.parse(source)
                    concepts = scanner.concept_extractor.extract(tree)
                    if isinstance(concepts, dict):
                        repo.upsert_file_concepts(file, concepts)

                    from codecraft.scanner.debt_detector import DebtDetector
                    debt_detector = DebtDetector(source, file)
                    debt_items = debt_detector.detect(tree)
                    debt_tracker = DebtTrackerEngine(repo)
                    debt_tracker.scan_and_track(debt_items)
                except SyntaxError:
                    pass
            else:
                try:
                    concepts = scanner.multi_scanner.parse_file(str(file))
                    if concepts:
                        repo.upsert_file_concepts(file, concepts)
                except Exception as e:
                    console.print(f"[error]Failed to parse {file}: {e}[/error]")

            scanned += 1

        if progress and task_id is not None:
            progress.advance(task_id)

    if progress:
        progress.stop()

    if json_output:
        data = {"files_scanned": scanned}
        console.print(_json.dumps(data))
        return

    if dry_run:
        console.print(f"[info]Dry run complete. {scanned} files would be scanned.[/info]")
        console.print("[info]Remove --dry-run to persist to database.[/info]")
        return

    console.print(f"[success]Scanned {scanned} files successfully" + (f" ({skipped} skipped)" if skipped else "") + "[/success]")

    table = Table(title="Scan Summary")
    table.add_column("Metric", style="bold")
    table.add_column("Value")
    table.add_row("Files scanned", str(scanned))
    if skipped:
        table.add_row("Skipped (unchanged)", str(skipped))
    table.add_row("Concepts tracked", str(len(repo.get_all_concept_names())))

    debt_report = DebtTrackerEngine(repo).get_report()
    table.add_row("Debt items", str(debt_report.total_items))
    table.add_row("Resolved", str(debt_report.resolved_items))
    table.add_row("Debt score", f"{debt_report.score:.1%}")
    console.print(table)

    if watch:
        _watch_directory(path, scanner, repo)


def _watch_directory(path: Path, scanner: UnifiedScanner, repo: Repository) -> None:
    try:
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
    except ImportError:
        console.print("[error]watchdog not installed. Run: pip install watchdog[/error]")
        raise typer.Exit(1)

    supported_exts = set(LanguageDetector.supported_extensions())
    from codecraft.engines.debt_tracker import DebtTrackerEngine

    class CodecraftHandler(FileSystemEventHandler):
        def _rescan(self, src_path: str) -> None:
            file = Path(src_path)
            if file.suffix.lower() not in supported_exts:
                return
            try:
                report = scanner.scan_file(file)
            except Exception as e:
                console.print(f"[error]Failed to scan {file}: {e}[/error]")
                return
            if report is None or report.errors:
                return

            import ast
            from codecraft.scanner.debt_detector import DebtDetector

            fhash = file_hash(file)
            size, lines = file_stats(file)
            record = FileRecord(path=file, hash=fhash, size=size, lines=lines)
            record.complexity = report.complexity
            record.import_count = len(report.imports)
            repo.upsert_file(record)

            lang = LanguageDetector.detect(str(file))
            if lang == Language.PYTHON:
                source = file.read_text(encoding="utf-8", errors="replace")
                try:
                    tree = ast.parse(source)
                    concepts = scanner.concept_extractor.extract(tree)
                    if isinstance(concepts, dict):
                        repo.upsert_file_concepts(file, concepts)
                    debt_detector = DebtDetector(source, file)
                    debt_items = debt_detector.detect(tree)
                    DebtTrackerEngine(repo).scan_and_track(debt_items)
                except SyntaxError:
                    pass
            else:
                concepts = scanner.multi_scanner.parse_file(str(file))
                if concepts:
                    repo.upsert_file_concepts(file, concepts)

            console.print(f"[info]Re-scanned: {file.name}[/info]")

        def on_modified(self, event: Any) -> None:
            self._rescan(event.src_path)

        def on_created(self, event: Any) -> None:
            self._rescan(event.src_path)

        def on_moved(self, event: Any) -> None:
            self._rescan(event.dest_path)

    handler = CodecraftHandler()
    observer = Observer()
    observer.schedule(handler, str(path), recursive=True)
    observer.start()
    console.print(f"[info]Watching {path} for changes... Press Ctrl+C to stop[/info]")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    console.print("[success]Watch stopped.[/success]")
    observer.join()


@scan_app.command("file", epilog="Example: codecraft scan file main.py")
def scan_single(
    file: Path = typer.Argument(..., help="Python file to scan", exists=True),
) -> None:

    scanner = UnifiedScanner()
    report = scanner.scan_file(file)
    if report is None:
        console.print(f"[error]Could not scan {file}[/error]")
        raise typer.Exit(1)

    repo = get_repo()

    try:
        fhash = file_hash(file)
        size, lines = file_stats(file)
        record = FileRecord(path=file, hash=fhash, size=size, lines=lines)
        record.complexity = report.complexity
        record.import_count = len(report.imports)
        repo.upsert_file(record)

        import ast

        from codecraft.engines.debt_tracker import DebtTrackerEngine
        from codecraft.scanner.debt_detector import DebtDetector
        source = file.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)
        concepts = scanner.concept_extractor.extract(tree)
        if isinstance(concepts, dict):
            repo.upsert_file_concepts(file, concepts)

        debt_detector = DebtDetector(source, file)
        debt_items = debt_detector.detect(tree)
        debt_tracker = DebtTrackerEngine(repo)
        debt_tracker.scan_and_track(debt_items)
    except SyntaxError:
        console.print(f"[error]Syntax error in {file}[/error]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[error]Failed to process {file}: {e}[/error]")
        raise typer.Exit(1)

    output = Tree(f"[title]{file.name}[/title]")
    concepts_node = output.add("[concept]Concepts[/concept]")
    for c in report.concepts:
        concepts_node.add(c)

    debt_node = output.add("[debt]Debt Patterns[/debt]")
    for d in report.debt_items:
        debt_node.add(f"[debt]{d}[/debt]")

    info = output.add("Info")
    info.add(f"Complexity: {report.complexity}")
    info.add(f"Lines: {report.lines}")
    info.add(f"Imports: {len(report.imports)}")

    console.print(output)


