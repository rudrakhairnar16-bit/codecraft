from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import typer
from rich.table import Table

from codecraft.cli.deps import get_repo
from codecraft.engines.debt_tracker import DebtTrackerEngine
from codecraft.engines.scheduler import ForgettingScheduler
from codecraft.models.concept import ConceptTaxonomy
from codecraft.utils.colors import console

export_app = typer.Typer(name="export", no_args_is_help=True)


@export_app.command("json")
def export_json(
    output: str = typer.Option("codecraft_export.json", "--output", "-o", help="Output file path"),
) -> None:
    repo = get_repo()
    data = _build_export_data(repo)
    out = Path(output)
    out.write_text(json.dumps(data, indent=2, default=str))
    console.print(f"[success]Exported to {out.resolve()}[/success]")


@export_app.command("csv")
def export_csv(
    output: str = typer.Option("codecraft_export.csv", "--output", "-o", help="Output file path"),
) -> None:
    repo = get_repo()
    import csv
    out = Path(output)
    history = repo.get_challenge_history(limit=10000)
    with open(out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "concept", "type", "correct", "time_seconds", "domain"])
        writer.writeheader()
        for h in history:
            writer.writerow({
                "date": h["created"].strftime("%Y-%m-%d %H:%M") if hasattr(h["created"], "strftime") else str(h["created"]),
                "concept": h["concept_name"],
                "type": h["challenge_type"],
                "correct": "yes" if h["correct"] else "no",
                "time_seconds": h["time_taken"],
                "domain": h["domain"],
            })
    console.print(f"[success]Exported to {out.resolve()}[/success]")


@export_app.command("summary")
def export_summary() -> None:
    repo = get_repo()
    data = _build_export_data(repo)
    console.print(f"[title]Export Summary[/title]")
    console.print(f"  Files scanned: {len(data['files'])}")
    console.print(f"  Concepts detected: {len(data['concepts'])}")
    console.print(f"  Practice sessions: {data['stats']['total_sessions']}")
    console.print(f"  Debt items: {data['debt']['total']}")
    console.print(f"  Cards tracked: {len(data['cards'])}")
    console.print(f"\n  [info]Export commands:[/info]")
    console.print(f"    codecraft export json -o export.json")
    console.print(f"    codecraft export csv -o export.csv")


def _build_export_data(repo) -> dict:
    files = repo.get_all_files()
    concepts = repo.get_all_concept_names()
    debt = DebtTrackerEngine(repo).get_report()
    scheduler = ForgettingScheduler(repo)
    cards = scheduler.repo.get_all_cards()
    stats = repo.get_practice_stats()
    history = repo.get_challenge_history(limit=1000)

    return {
        "exported_at": datetime.now(),
        "files": [{"path": str(f.path), "hash": f.hash, "lines": f.lines, "complexity": f.complexity} for f in files],
        "concepts": sorted(concepts),
        "stats": stats,
        "debt": {
            "total": debt.total_items,
            "resolved": debt.resolved_items,
            "unresolved": len(debt.unresolved),
            "score": debt.score,
            "items": [
                {"pattern": i.pattern_type, "file": str(i.file_path), "difficulty": i.difficulty}
                for i in debt.items
            ],
        },
        "cards": [
            {"concept": c.concept_name, "strength": c.strength, "interval_days": c.interval_days, "next_review": c.next_review}
            for c in cards
        ],
        "history": [
            {
                "date": h["created"], "concept": h["concept_name"],
                "type": h["challenge_type"], "correct": h["correct"],
                "time": h["time_taken"], "domain": h["domain"],
            }
            for h in history
        ],
    }
