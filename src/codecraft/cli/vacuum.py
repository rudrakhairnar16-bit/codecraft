from __future__ import annotations

from typing import Any

import typer

from codecraft.cli.deps import backup_db, get_repo
from codecraft.utils.colors import console

vacuum_app = typer.Typer(name="vacuum", no_args_is_help=True, help="Compact and deduplicate database")


@vacuum_app.command("run")
def vacuum_run(
    no_backup: bool = typer.Option(False, "--no-backup", help="Skip backup before vacuum"),
) -> None:
    repo = get_repo()
    if not no_backup:
        backup_db("prevacuum")
    from rich.panel import Panel
    console.print(Panel("[title]Vacuuming Database...[/title]"))

    before = _get_db_stats(repo)

    _deduplicate_file_concepts(repo)
    _clean_orphaned_records(repo)
    _rebuild_indices(repo)

    after = _get_db_stats(repo)

    from rich.table import Table
    table = Table(show_header=False)
    table.add_column("Metric", style="bold")
    table.add_column("Before")
    table.add_column("After")
    table.add_row("Files", str(before["files"]), str(after["files"]))
    table.add_row("File-Concept mappings", str(before["mappings"]), str(after["mappings"]))
    table.add_row("Debt items", str(before["debt"]), str(after["debt"]))
    console.print(table)
    console.print("[success]Vacuum complete![/success]")


@vacuum_app.command("stats")
def vacuum_stats() -> None:
    repo = get_repo()
    stats = _get_db_stats(repo)
    from rich.table import Table
    table = Table(title="Database Storage Stats")
    table.add_column("Table", style="bold")
    table.add_column("Rows")
    table.add_column("Size Estimate")
    for tbl, rows, size in stats["tables"]:
        table.add_row(tbl, str(rows), size)
    console.print(table)


def _get_db_stats(repo: Any) -> dict[str, Any]:
    info: dict[str, Any] = {}
    tables_info: list[tuple[str, Any, str]] = []
    for tbl in ["files", "file_concepts", "debt_items", "challenge_history", "spaced_repetition", "settings"]:
        row = repo.conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()
        count = row[0] if row else 0
        tables_info.append((tbl, count, f"{count * 0.5:.0f} KB" if count > 0 else "<1 KB"))
    info["tables"] = tables_info
    row_files = repo.conn.execute("SELECT COUNT(*) FROM files").fetchone()
    info["files"] = row_files[0] if row_files else 0
    row_mappings = repo.conn.execute("SELECT COUNT(*) FROM file_concepts").fetchone()
    info["mappings"] = row_mappings[0] if row_mappings else 0
    row_debt = repo.conn.execute("SELECT COUNT(*) FROM debt_items").fetchone()
    info["debt"] = row_debt[0] if row_debt else 0
    return info


def _deduplicate_file_concepts(repo: Any) -> None:
    repo.conn.execute("""
        DELETE FROM file_concepts
        WHERE (file_path, concept_name, occurrences) IN (
            SELECT file_path, concept_name, occurrences
            FROM (
                SELECT file_path, concept_name, occurrences,
                       ROW_NUMBER() OVER (PARTITION BY file_path, concept_name ORDER BY last_seen DESC) as rn
                FROM file_concepts
            ) sub
            WHERE sub.rn > 1
        )
    """)


def _clean_orphaned_records(repo: Any) -> None:
    repo.conn.execute("""
        DELETE FROM file_concepts
        WHERE file_path NOT IN (SELECT path FROM files)
    """)
    repo.conn.execute("""
        DELETE FROM debt_items
        WHERE file_path NOT IN (SELECT path FROM files)
    """)


def _rebuild_indices(repo: Any) -> None:
    repo.conn.execute("CHECKPOINT")
