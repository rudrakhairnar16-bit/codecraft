from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import typer

from codecraft.cli.deps import get_repo
from codecraft.utils.colors import console

sync_app = typer.Typer(name="sync", no_args_is_help=True)


def _serialize(obj: Any) -> str:
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Path):
        return str(obj)
    return str(obj)


@sync_app.command("export", epilog="Example: codecraft sync export backup.json")
def sync_export(
    output: Path = typer.Argument(
        ..., help="Output JSON file path"
    ),
    pretty: bool = typer.Option(True, "--pretty", "-p", help="Pretty-print JSON"),
) -> None:
    """Export all DB data to a portable JSON file."""
    repo = get_repo()

    try:
        data = {
            "version": 1,
            "exported_at": datetime.now().isoformat(),
            "files": _fetch_rows(repo.conn, "SELECT * FROM files"),
            "file_concepts": _fetch_rows(repo.conn, "SELECT * FROM file_concepts"),
            "debt_items": _fetch_rows(repo.conn, "SELECT * FROM debt_items"),
            "challenge_history": _fetch_rows(repo.conn, "SELECT * FROM challenge_history"),
            "spaced_repetition": _fetch_rows(repo.conn, "SELECT * FROM spaced_repetition"),
            "settings": _fetch_rows(repo.conn, "SELECT * FROM settings"),
            "scan_history": _fetch_rows(repo.conn, "SELECT * FROM scan_history"),
            "suggestions": _fetch_rows(repo.conn, "SELECT * FROM suggestions"),
        }
    except Exception as e:
        console.print(f"[error]Failed to read database: {e}[/error]")
        raise typer.Exit(1)

    try:
        with open(output, "w", encoding="utf-8") as f:
            if pretty:
                json.dump(data, f, default=_serialize, indent=2)
            else:
                json.dump(data, f, default=_serialize)
        console.print(f"[success]Exported {output}[/success]")
    except Exception as e:
        console.print(f"[error]Export failed: {e}[/error]")
        raise typer.Exit(1)


def _fetch_rows(conn: Any, sql: str) -> list[dict[str, Any]]:
    result = conn.execute(sql)
    keys = [desc[0] for desc in result.description]
    return [{k: _serialize(v) for k, v in zip(keys, row)} for row in result.fetchall()]


@sync_app.command("import", epilog="Example: codecraft sync import backup.json --mode overwrite")
def sync_import(
    input_path: Path = typer.Argument(
        ..., help="JSON file to import from"
    ),
    mode: str = typer.Option(
        "merge", "--mode", "-m",
        help="'merge' (keep existing, add new) or 'overwrite' (replace all)"
    ),
) -> None:
    """Import data from a JSON export file."""
    if not input_path.exists():
        console.print(f"[error]File not found: {input_path}[/error]")
        raise typer.Exit(1)

    repo = get_repo()

    try:
        with open(input_path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        console.print(f"[error]Failed to read JSON: {e}[/error]")
        raise typer.Exit(1)

    tables = [
        ("files", "path", False),
        ("file_concepts", "file_path, concept_name", False),
        ("settings", "key", False),
        ("debt_items", "id", True),
        ("challenge_history", "id", True),
        ("spaced_repetition", "concept_name", False),
        ("scan_history", "id", True),
        ("suggestions", "concept_name", False),
    ]

    try:
        counts = {}
        for table_name, pk, _ in tables:
            rows_data = data.get(table_name, [])
            if not rows_data:
                counts[table_name] = (0, 0)
                continue

            inserted = 0
            skipped = 0
            for row_dict in rows_data:
                cols = list(row_dict.keys())
                placeholders = ", ".join(["?" for _ in cols])
                col_names = ", ".join(cols)

                if mode == "overwrite":
                    repo.conn.execute(
                        f"DELETE FROM {table_name} WHERE ({pk})"
                        f" IN (SELECT {pk} FROM (VALUES (?)) AS t({pk.split(',')[0].strip()}))",
                        [row_dict.get(pk.split(",")[0].strip())],
                    )
                    repo.conn.execute(
                        f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})",
                        [row_dict[c] for c in cols],
                    )
                    inserted += 1
                else:
                    try:
                        repo.conn.execute(
                            f"INSERT OR IGNORE INTO {table_name} ({col_names}) VALUES ({placeholders})",
                            [row_dict[c] for c in cols],
                        )
                        change_row = repo.conn.execute("SELECT changes()").fetchone()
                        if change_row is not None and change_row[0] > 0:
                            inserted += 1
                        else:
                            skipped += 1
                    except Exception:
                        skipped += 1

            counts[table_name] = (inserted, skipped)

        console.print("[success]Import complete[/success]")
        for table_name, (ins, skp) in counts.items():
            console.print(f"  {table_name}: {ins} inserted, {skp} skipped")
    except Exception as e:
        console.print(f"[error]Import failed: {e}[/error]")
        raise typer.Exit(1)
