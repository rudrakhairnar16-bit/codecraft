from __future__ import annotations

import typer
from rich.panel import Panel
from rich.table import Table

from codecraft.cli.deps import get_repo
from codecraft.engines.remix import RemixEngine
from codecraft.engines.scheduler import ForgettingScheduler
from codecraft.utils.colors import console

schedule_app = typer.Typer(name="schedule", no_args_is_help=True)


@schedule_app.command("queue")
def show_queue(
    threshold: float = typer.Option(0.6, "--threshold", "-t", help="Strength threshold for decay"),
) -> None:
    repo = get_repo()
    scheduler = ForgettingScheduler(repo)
    queue = scheduler.get_review_queue(threshold)
    sorted_cards = queue.sort_by_urgency()

    if not sorted_cards:
        console.print("[success]No reviews due! All concepts are fresh.[/success]")
        return

    table = Table(title=f"Review Queue ({len(sorted_cards)} due)")
    table.add_column("Concept", style="concept")
    table.add_column("Strength")
    table.add_column("Interval", justify="right")
    table.add_column("Repetitions", justify="right")
    table.add_column("Status")

    for card in sorted_cards:
        strength = card.strength
        if strength >= 0.8:
            color = "strength.high"
            status = "fresh"
        elif strength >= 0.6:
            color = "strength.medium"
            status = "stable"
        else:
            color = "strength.low"
            status = "decaying"
        table.add_row(
            card.concept_name,
            f"[{color}]{strength:.2f}[/{color}]",
            f"{card.interval_days}d",
            str(card.repetitions),
            status,
        )
    console.print(table)


@schedule_app.command("due")
def show_due() -> None:
    repo = get_repo()
    scheduler = ForgettingScheduler(repo)
    queue = scheduler.get_review_queue()
    due = queue.due_cards()

    if not due:
        console.print("[success]Nothing due right now. Enjoy your day![/success]")
        return

    console.print(f"[title]Due for Review: {len(due)} concepts[/title]")
    for card in sorted(due, key=lambda c: c.urgency, reverse=True):
        console.print(f"  [concept]{card.concept_name}[/concept] — urgency: [debt]{card.urgency:.1f}d overdue[/debt]")


@schedule_app.command("review")
def review_concept(
    concept: str = typer.Argument(..., help="Concept to review"),
    correct: bool = typer.Option(True, "--correct/--incorrect", "-c/-i", help="Did you recall correctly?"),
) -> None:
    from codecraft.models.concept import ConceptTaxonomy
    all_concepts = {c.name for c in ConceptTaxonomy.all()}
    if concept not in all_concepts:
        console.print(f"[error]Unknown concept '{concept}'[/error]")
        console.print(f"[warning]Available:[/warning] {', '.join(sorted(all_concepts)[:10])}...")
        raise typer.Exit(1)

    repo = get_repo()
    scheduler = ForgettingScheduler(repo)

    card = scheduler.after_review(concept, correct)
    status = "[success]Correct![/success]" if correct else "[debt]Incorrect — will review sooner.[/debt]"
    console.print(f"[title]Review: {concept}[/title]")
    console.print(status)
    console.print(f"Ease factor: {card.ease_factor:.2f}")
    console.print(f"Interval: [bold]{card.interval_days}d[/bold]")
    next_review = card.next_review.strftime('%Y-%m-%d') if card.next_review else 'ASAP'
    console.print(f"Next review: [info]{next_review}[/info]")
    console.print(f"Repetitions: {card.repetitions}")

    if not correct:
        remix = RemixEngine(repo)
        challenge = remix.generate_review_exercise(concept)
        if challenge:
            console.print("\n[warning]Here's a quick refresher:[/warning]")
            console.print(Panel(challenge.description[:200], border_style="yellow"))


@schedule_app.command("decay")
def show_decay(
    min_strength: float = typer.Option(0.0, "--min", "-m", help="Minimum strength to show"),
) -> None:
    repo = get_repo()
    scheduler = ForgettingScheduler(repo)
    report = scheduler.get_decay_report()

    filtered = [r for r in report if r["strength"] >= min_strength]
    if not filtered:
        console.print("[warning]No concepts meet the minimum strength criteria.[/warning]")
        return

    table = Table(title="Concept Decay Report")
    table.add_column("Concept", style="concept")
    table.add_column("Strength")
    table.add_column("Exposures")
    table.add_column("Days Since Use")
    table.add_column("Status")

    for r in filtered:
        strength = r["strength"]
        if strength >= 0.8:
            color = "strength.high"
        elif strength >= 0.6:
            color = "strength.medium"
        else:
            color = "strength.low"
        table.add_row(
            r["concept"],
            f"[{color}]{strength:.3f}[/{color}]",
            str(r["exposure_count"]),
            str(r["days_since_use"] or "N/A"),
            r["status"],
        )
    console.print(table)

    decaying = [r for r in filtered if r["status"] == "decaying"]
    if decaying:
        console.print(f"\n[debt]{len(decaying)} concepts are decaying.[/debt]")
        console.print("[info]Run 'codecraft schedule queue' to see your review queue.[/info]")
