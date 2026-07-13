from __future__ import annotations

import typer
from rich.panel import Panel
from rich.table import Table

from codecraft.cli.deps import get_repo
from codecraft.utils.colors import console

stats_app = typer.Typer(name="stats", no_args_is_help=True)


@stats_app.command("sessions", epilog="Example: codecraft stats sessions --limit 10")
def stats_sessions(
    limit: int = typer.Option(20, "--limit", "-l", help="Number of sessions"),
) -> None:
    repo = get_repo()
    stats = repo.get_practice_stats()
    streak = repo.get_streak_data()
    history = repo.get_challenge_history(limit=limit)

    console.print(Panel("[title]Session Statistics[/title]"))
    table = Table(show_header=False)
    table.add_column("Metric", style="bold")
    table.add_column("Value")
    table.add_row("Total sessions", str(stats["total_sessions"]))
    table.add_row("Correct", str(stats["correct_sessions"]))
    table.add_row("Incorrect", str(stats["total_sessions"] - stats["correct_sessions"]))
    rate = stats["correct_sessions"] * 100 // max(stats["total_sessions"], 1)
    table.add_row("Accuracy", f"{rate}%")
    table.add_row("Avg time", f"{stats['avg_time_seconds']}s")
    table.add_row("Concepts practiced", str(stats["unique_concepts"]))
    table.add_row("Domains explored", str(stats["unique_domains"]))
    table.add_row("Current streak", f"{streak['current_streak']} days")
    table.add_row("Active days", str(streak["total_active_days"]))
    console.print(table)

    if history:
        console.print("\n[info]Recent sessions:[/info]")
        recent = Table()
        recent.add_column("Date", style="dim")
        recent.add_column("Concept", style="concept")
        recent.add_column("Result")
        recent.add_column("Time")
        for h in history[:5]:
            result = "[success]Correct[/success]" if h["correct"] else "[debt]Incorrect[/debt]"
            mins, secs = divmod(h["time_taken"], 60)
            time_str = f"{mins}m {secs}s" if mins else f"{secs}s"
            recent.add_row(
                h["created"].strftime("%Y-%m-%d %H:%M")
                if hasattr(h["created"], "strftime")
                else str(h["created"])[:16],
                h["concept_name"],
                result,
                time_str,
            )
        console.print(recent)
