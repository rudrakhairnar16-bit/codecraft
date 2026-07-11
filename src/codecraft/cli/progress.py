from __future__ import annotations

import typer
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from codecraft.cli.deps import get_repo
from codecraft.engines.debt_tracker import DebtTrackerEngine
from codecraft.engines.remix import RemixEngine
from codecraft.engines.scheduler import ForgettingScheduler
from codecraft.models.concept import ConceptTaxonomy
from codecraft.utils.colors import console

progress_app = typer.Typer(name="progress", no_args_is_help=True)


@progress_app.command("overview")
def progress_overview() -> None:
    repo = get_repo()
    stats = repo.get_practice_stats()
    streak = repo.get_streak_data()

    concepts = repo.get_all_concept_names()
    all_concepts = ConceptTaxonomy.all()

    scheduler = ForgettingScheduler(repo)
    decay = scheduler.get_decay_report()
    fresh = sum(1 for r in decay if r["status"] == "fresh")
    stable = sum(1 for r in decay if r["status"] == "stable")
    decaying = sum(1 for r in decay if r["status"] == "decaying")

    debt = DebtTrackerEngine(repo).get_report()
    remix = RemixEngine(repo)
    gaps = remix.find_gaps()

    console.print(Panel("[title]Learning Progress[/title]"))
    table = Table(show_header=False)
    table.add_column("Metric", style="bold")
    table.add_column("Value")
    table.add_row("Concepts detected", str(len(concepts)))
    table.add_row("Total concepts available", str(len(all_concepts)))
    table.add_row("Coverage", f"{len(concepts)}/{len(all_concepts)} ({len(concepts)*100//max(len(all_concepts),1)}%)")
    table.add_row("Practice sessions", str(stats["total_sessions"]))
    table.add_row("Correct sessions", str(stats["correct_sessions"]))
    table.add_row("Accuracy", f"{stats['correct_sessions']*100//max(stats['total_sessions'],1)}%" if stats["total_sessions"] else "N/A")
    table.add_row("Active streak", f"{streak['current_streak']} days")
    table.add_row("Total active days", str(streak["total_active_days"]))
    table.add_row("Fresh concepts", f"[strength.high]{fresh}[/strength.high]")
    table.add_row("Stable concepts", f"[strength.medium]{stable}[/strength.medium]")
    table.add_row("Decaying concepts", f"[strength.low]{decaying}[/strength.low]")
    table.add_row("Concept gaps", f"[debt]{len(gaps)}[/debt]")
    table.add_row("Debt score", f"[score]{debt.score:.0%}[/score]")
    console.print(table)

    if stats["total_sessions"] > 0:
        console.print(f"\n[info]Avg time per session:[/info] {stats['avg_time_seconds']}s")
        console.print(f"[info]Unique concepts practiced:[/info] {stats['unique_concepts']}")
        console.print(f"[info]Unique domains explored:[/info] {stats['unique_domains']}")


@progress_app.command("history")
def progress_history(
    limit: int = typer.Option(20, "--limit", "-l", help="Number of recent sessions"),
) -> None:
    repo = get_repo()
    history = repo.get_challenge_history(limit=limit)

    if not history:
        console.print("[warning]No practice history yet. Run [info]codecraft practice start[/info] to begin![/warning]")
        return

    table = Table(title=f"Recent Practice Sessions ({len(history)})")
    table.add_column("Date", style="dim")
    table.add_column("Concept", style="concept")
    table.add_column("Type")
    table.add_column("Result")
    table.add_column("Time")
    table.add_column("Domain")

    for h in history:
        result = "[success]Correct[/success]" if h["correct"] else "[debt]Incorrect[/debt]"
        mins, secs = divmod(h["time_taken"], 60)
        time_str = f"{mins}m {secs}s" if mins else f"{secs}s"
        table.add_row(
            h["created"].strftime("%Y-%m-%d %H:%M") if hasattr(h["created"], "strftime") else str(h["created"])[:16],
            h["concept_name"],
            h["challenge_type"],
            result,
            time_str,
            h["domain"],
        )
    console.print(table)


@progress_app.command("tree")
def progress_tree() -> None:
    repo = get_repo()
    concepts = repo.get_all_concept_names()
    scheduler = ForgettingScheduler(repo)
    tree = Tree("[title]Concept Mastery Tree[/title]")
    tiers = {1: "Seed", 2: "Root", 3: "Branch", 4: "Canopy"}
    for tier_num in [1, 2, 3, 4]:
        tier_concepts = [c for c in ConceptTaxonomy.all() if c.tier.value == tier_num]
        tier_node = tree.add(f"[tier{tier_num}]Tier {tier_num}: {tiers[tier_num]} ({len(tier_concepts)} concepts)[/tier{tier_num}]")
        for c in tier_concepts:
            if c.name in concepts:
                card = repo.get_card(c.name)
                if card:
                    strength = card.strength
                    if strength >= 0.8:
                        status = "[strength.high]fresh[/strength.high]"
                    elif strength >= 0.6:
                        status = "[strength.medium]stable[/strength.medium]"
                    else:
                        status = f"[strength.low]decaying ({strength:.0%})[/strength.low]"
                else:
                    status = "[dim]untracked[/dim]"
                tier_node.add(f"{c.name} ({status})")
            else:
                tier_node.add(f"[dim]{c.name} (unseen)[/dim]")
    console.print(tree)
