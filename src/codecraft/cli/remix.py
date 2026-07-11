from __future__ import annotations

import typer
from rich.panel import Panel
from rich.table import Table

from codecraft.cli.deps import get_repo
from codecraft.engines.remix import RemixEngine
from codecraft.utils.colors import console

remix_app = typer.Typer(name="remix", no_args_is_help=True)


@remix_app.command("gaps")
def show_gaps(
    threshold: int = typer.Option(3, "--threshold", "-t", help="Max exposures to count as a gap"),
) -> None:
    repo = get_repo()
    engine = RemixEngine(repo)
    gaps = engine.find_gaps(threshold)

    if not gaps:
        console.print("[success]No concept gaps found! You're exploring deeply.[/success]")
        return

    table = Table(title=f"Concept Gaps (used ≤{threshold} times)")
    table.add_column("Concept", style="concept")
    table.add_column("Exposures")
    table.add_column("Days since last use")
    table.add_column("Suggested domain")

    for name in gaps:
        exposure = repo.get_exposure_count(name)
        last = repo.get_last_usage(name)
        days = (__import__("datetime").datetime.now() - last).days if last else "N/A"
        unused_domains = engine.find_unused_domains(name)
        suggested = unused_domains[0] if unused_domains else "any"
        table.add_row(name, str(exposure), str(days), suggested)

    console.print(table)


@remix_app.command("generate")
def generate_exercise(
    concept: str = typer.Argument(..., help="Concept to practice"),
    domain: str | None = typer.Option(None, "--domain", "-d", help="Target domain"),
) -> None:
    repo = get_repo()
    engine = RemixEngine(repo)

    challenge = engine.generate_exercise(concept, domain)
    if challenge is None:
        console.print(f"[error]Could not generate exercise for '{concept}'[/error]")
        console.print("[warning]Try scanning some files first with: codecraft scan dir[/warning]")
        return

    console.print(Panel(f"[title]Transfer Exercise: {challenge.title}[/title]"))
    console.print(f"[domain]Domain:[/domain] {challenge.domain}")
    console.print(f"[info]Concept:[/info] {challenge.concept_name}")
    console.print("\n[bold]Description:[/bold]")
    console.print(challenge.description)
    console.print("\n[bold]Code Stub:[/bold]")
    console.print(Panel(challenge.code_snippet, border_style="cyan"))
    console.print("\n[info]Hints:[/info]")
    for h in challenge.hints:
        console.print(f"  [warning]->[/warning] {h}")


@remix_app.command("domains")
def domain_stats() -> None:
    repo = get_repo()
    engine = RemixEngine(repo)
    stats = engine.get_domain_stats()

    table = Table(title="Domain Coverage")
    table.add_column("Domain", style="domain")
    table.add_column("Concepts Available")
    table.add_column("Your Concepts")
    table.add_column("Match Ratio")

    for s in stats:
        ratio = s["match_ratio"]
        ratio_str = (
            f"[strength.high]{ratio:.0%}[/strength.high]"
            if ratio >= 0.5
            else f"[strength.medium]{ratio:.0%}[/strength.medium]"
            if ratio >= 0.2
            else f"[strength.low]{ratio:.0%}[/strength.low]"
        )
        table.add_row(
            s["domain"],
            str(s["supported_concepts"]),
            str(s["your_concepts_matched"]),
            ratio_str,
        )
    console.print(table)


@remix_app.command("review")
def generate_review(
    concept: str = typer.Argument(..., help="Concept to review"),
) -> None:
    repo = get_repo()
    engine = RemixEngine(repo)

    challenge = engine.generate_review_exercise(concept)
    if challenge is None:
        console.print(f"[error]Could not generate review for '{concept}'[/error]")
        return

    console.print(Panel(f"[title]Review Exercise: {challenge.title}[/title]"))
    console.print(f"[domain]Domain:[/domain] {challenge.domain}")
    console.print("\n[bold]Description:[/bold]")
    console.print(challenge.description)
    console.print("\n[bold]Code Stub:[/bold]")
    console.print(Panel(challenge.code_snippet, border_style="cyan"))
