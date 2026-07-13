from __future__ import annotations

import typer
from rich.panel import Panel
from rich.table import Table

from codecraft.cli.deps import get_repo
from codecraft.engines.debt_tracker import DebtTrackerEngine
from codecraft.engines.remix import RemixEngine
from codecraft.engines.scheduler import ForgettingScheduler
from codecraft.models.concept import ConceptTaxonomy
from codecraft.utils.colors import console

learn_app = typer.Typer(name="learn", no_args_is_help=True)


@learn_app.command("concept", epilog="Example: codecraft learn concept list_comprehension --domain finance")
def learn_concept(
    concept: str = typer.Argument(..., help="Concept to learn"),
    domain: str | None = typer.Option(None, "--domain", "-d", help="Domain context"),
) -> None:
    repo = get_repo()
    resolved = _resolve_concept_name(concept)
    if resolved != concept:
        console.print(f"[info]Matched concept:[/info] {resolved}")

    c = ConceptTaxonomy.get(resolved)
    if not c:
        console.print(f"[error]Unknown concept '{resolved}'[/error]")
        raise typer.Exit(1)

    known = set(repo.get_all_concept_names())
    card = repo.get_card(resolved)
    debt = DebtTrackerEngine(repo)
    debt.get_report()
    ForgettingScheduler(repo)
    RemixEngine(repo)

    console.print(Panel(f"[title]Learning: {resolved}[/title]"))
    console.print(f"[info]Tier:[/info] {c.tier.value} ({['Seed', 'Root', 'Branch', 'Canopy'][c.tier.value-1]})")
    console.print(f"[info]Category:[/info] {c.category}")
    console.print(f"[info]Description:[/info] {c.description}")

    if resolved in known:
        exposure = repo.get_exposure_count(resolved)
        last_used = repo.get_last_usage(resolved)
        console.print(f"[success]Already detected[/success] — {exposure} exposure(s)")
        if last_used:
            from datetime import datetime
            days = (datetime.now() - last_used).days
            console.print(f"  Last used: {days} day(s) ago")
        if card:
            console.print(f"  Strength: {card.strength:.0%}")
            console.print(f"  Interval: {card.interval_days} day(s)")
    else:
        console.print("[debt]Not yet detected in your codebase[/debt]")

    console.print("\n[bold]Learning Path:[/bold]")
    table = Table()
    table.add_column("Step", style="bold")
    table.add_column("Action", style="concept")
    table.add_column("Command")

    table.add_row("1", "Understand the concept", "[dim]Read the description above[/dim]")
    table.add_row("2", "Practice with exercise", f"codecraft practice start {resolved} --domain {domain or 'gaming'}")
    table.add_row("3", "Generate transfer exercise", f"codecraft remix generate {resolved}")
    table.add_row("4", "Review with spaced repetition", f"codecraft schedule review {resolved} --correct")
    table.add_row("5", "Check decay over time", "codecraft schedule decay")
    console.print(table)


def _resolve_concept_name(name: str) -> str:
    for cname in list(ConceptTaxonomy._concepts.keys()):
        if name.lower() in cname.lower():
            return cname
    return name

