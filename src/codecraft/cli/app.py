from __future__ import annotations

from datetime import datetime

import typer
from rich.panel import Panel
from rich.table import Table

from codecraft.cli.dashboard import dashboard_app
from codecraft.cli.debt import debt_app
from codecraft.cli.deps import get_repo, init_db
from codecraft.cli.practice import practice_app
from codecraft.cli.remix import remix_app
from codecraft.cli.scan import scan_app
from codecraft.cli.schedule import schedule_app
from codecraft.engines.debt_tracker import DebtTrackerEngine
from codecraft.engines.remix import RemixEngine
from codecraft.engines.scheduler import ForgettingScheduler
from codecraft.utils.colors import console

app = typer.Typer(
    name="codecraft",
    help="Your personal Python skill forge — scan, analyze, and master Python concepts.",
    no_args_is_help=True,
)

app.add_typer(scan_app, name="scan", help="Scan Python files and extract concept fingerprints")
app.add_typer(debt_app, name="debt", help="Track and resolve learning debt")
app.add_typer(remix_app, name="remix", help="Generate transfer exercises in new contexts")
app.add_typer(schedule_app, name="schedule", help="Spaced repetition review scheduler")
app.add_typer(dashboard_app, name="dashboard", help="Cross-engine insights and trends")
app.add_typer(practice_app, name="practice", help="Timed practice with solution analysis")


@app.callback()
def main() -> None:
    init_db()


@app.command("status")
def show_status() -> None:
    repo = get_repo()

    files = repo.get_all_files()
    concepts = repo.get_all_concept_names()

    debt_engine = DebtTrackerEngine(repo)
    debt_report = debt_engine.get_report()

    scheduler = ForgettingScheduler(repo)
    decay_report = scheduler.get_decay_report()
    due = scheduler.get_review_queue().due_cards()

    decaying = sum(1 for r in decay_report if r["status"] == "decaying")
    stable = sum(1 for r in decay_report if r["status"] == "stable")

    remix = RemixEngine(repo)
    gaps = remix.find_gaps()

    console.print(Panel(f"[title]CodeCraft Status — {datetime.now().strftime('%Y-%m-%d %H:%M')}[/title]"))

    table = Table(show_header=False)
    table.add_column("Metric", style="bold")
    table.add_column("Value")

    table.add_row("Files scanned", str(len(files)))
    table.add_row("Concepts detected", str(len(concepts)))
    table.add_row("Concept gaps", f"[debt]{len(gaps)}[/debt]")
    table.add_row("Debt score", f"[score]{debt_report.score:.0%}[/score]")
    table.add_row("Unresolved debt items", f"[debt]{len(debt_report.unresolved)}[/debt]")
    table.add_row("Stable concepts", f"[strength.high]{stable}[/strength.high]")
    table.add_row("Decaying concepts", f"[strength.low]{decaying}[/strength.low]")
    table.add_row("Due for review", f"[debt]{len(due)}[/debt]")
    table.add_row("Domains available", "20")
    console.print(table)

    next_steps = []
    if len(debt_report.unresolved) > 0:
        next_steps.append("[warning]codecraft debt list[/warning] to see unresolved items")
    if len(gaps) > 0:
        next_steps.append("[info]codecraft remix generate[/info] to practice gaps")
    if len(due) > 0:
        next_steps.append("[info]codecraft schedule review[/info] for due reviews")

    if next_steps:
        console.print("\n[bold]Suggested next:[/bold]")
        for step in next_steps:
            console.print(f"  → {step}")


if __name__ == "__main__":
    app()
