from __future__ import annotations

import ast
import time
from pathlib import Path

import typer
from rich.table import Table
from rich.tree import Tree

from codecraft.cli.deps import get_repo
from codecraft.db.repository import Repository
from codecraft.engines.debt_tracker import DebtTrackerEngine
from codecraft.models.file import FileRecord
from codecraft.scanner.ast_parser import file_hash, file_stats
from codecraft.scanner.debt_detector import DebtDetector
from codecraft.scanner.unified import UnifiedScanner
from codecraft.utils.colors import console

scan_app = typer.Typer(name="scan", no_args_is_help=True)


@scan_app.command("dir")
def scan_directory(
    path: Path = typer.Argument(".", help="Directory to scan"),
    recursive: bool = typer.Option(True, "-r", "--recursive", help="Scan recursively"),
    watch: bool = typer.Option(False, "-w", "--watch", help="Watch for file changes"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview without persisting"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    pattern = "**/*.py" if recursive else "*.py"
    scanner = UnifiedScanner()
    repo = get_repo()

    files = list(Path(path).glob(pattern))
    if not files:
        console.print(f"[warning]No .py files found in {path}[/warning]")
        raise typer.Exit()

    if not json_output:
        console.print(f"[title]Scanning {len(files)} Python files...[/title]")

    scanned = 0
    for file in files:
        if any(part.startswith(".") for part in file.parts):
            continue
        report = scanner.scan_file(file)
        if report and not report.errors:
            fhash = file_hash(file)
            size, lines = file_stats(file)

            if dry_run:
                console.print(f"  [dim]{file}[/dim] - {len(report.concepts)} concepts, {len(report.debt_items)} debts")
                scanned += 1
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

            source = file.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source)

            concepts = scanner.concept_extractor.extract(tree)
            if isinstance(concepts, dict):
                repo.upsert_file_concepts(file, concepts)

            debt_detector = DebtDetector(source, file)
            debt_items = debt_detector.detect(tree)

            debt_tracker = DebtTrackerEngine(repo)
            debt_tracker.scan_and_track(debt_items)
            scanned += 1

    if json_output:
        import json as _json
        data = {"files_scanned": scanned}
        console.print(_json.dumps(data))
        return

    if dry_run:
        console.print(f"[info]Dry run complete. {scanned} files would be scanned.[/info]")
        console.print("[info]Remove --dry-run to persist to database.[/info]")
        return

    console.print(f"[success]Scanned {scanned} files successfully[/success]")

    table = Table(title="Scan Summary")
    table.add_column("Metric", style="bold")
    table.add_column("Value")
    table.add_row("Files scanned", str(scanned))
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

    class CodecraftHandler(FileSystemEventHandler):
        def on_modified(self, event):
            if event.src_path.endswith(".py"):
                file = Path(event.src_path)
                report = scanner.scan_file(file)
                if report and not report.errors:
                    console.print(f"[info]Re-scanned: {file.name}[/info]")

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
    observer.join()


@scan_app.command("file")
def scan_single(
    file: Path = typer.Argument(..., help="Python file to scan", exists=True),
) -> None:
    scanner = UnifiedScanner()
    report = scanner.scan_file(file)
    if report is None:
        console.print(f"[error]Could not scan {file}[/error]")
        raise typer.Exit(1)

    repo = get_repo()
    fhash = file_hash(file)
    size, lines = file_stats(file)
    record = FileRecord(path=file, hash=fhash, size=size, lines=lines)
    record.complexity = report.complexity
    record.import_count = len(report.imports)
    repo.upsert_file(record)

    import ast
    source = file.read_text(encoding="utf-8", errors="replace")
    tree_ast = ast.parse(source)
    concepts = scanner.concept_extractor.extract(tree_ast)
    if isinstance(concepts, dict):
        repo.upsert_file_concepts(file, concepts)

    debt_detector = DebtDetector(source, file)
    debt_items = debt_detector.detect(tree_ast)
    debt_tracker = DebtTrackerEngine(repo)
    debt_tracker.scan_and_track(debt_items)

    tree = Tree(f"[title]{file.name}[/title]")
    concepts_node = tree.add("[concept]Concepts[/concept]")
    for c in report.concepts:
        concepts_node.add(c)

    debt_node = tree.add("[debt]Debt Patterns[/debt]")
    for d in report.debt_items:
        debt_node.add(f"[debt]{d}[/debt]")

    info = tree.add("Info")
    info.add(f"Complexity: {report.complexity}")
    info.add(f"Lines: {report.lines}")
    info.add(f"Imports: {len(report.imports)}")

    console.print(tree)
