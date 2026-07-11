from __future__ import annotations

import typer
from rich.table import Table
from rich.tree import Tree

from codecraft.cli.deps import get_repo
from codecraft.engines.debt_tracker import DebtTrackerEngine
from codecraft.engines.remix import RemixEngine
from codecraft.engines.scheduler import ForgettingScheduler
from codecraft.models.concept import Tier
from codecraft.utils.colors import console

dashboard_app = typer.Typer(name="dashboard", no_args_is_help=True)


@dashboard_app.command("summary")
def show_summary() -> None:
    repo = get_repo()
    files = repo.get_all_files()
    concepts = repo.get_all_concept_names()

    debt_engine = DebtTrackerEngine(repo)
    debt_report = debt_engine.get_report()

    scheduler = ForgettingScheduler(repo)
    decay_report = scheduler.get_decay_report()

    decaying = sum(1 for r in decay_report if r["status"] == "decaying")
    stable = sum(1 for r in decay_report if r["status"] == "stable")
    fresh = sum(1 for r in decay_report if r["status"] == "fresh")

    remix = RemixEngine(repo)
    gaps = remix.find_gaps()
    domains = remix.get_domain_stats()

    tree = Tree("[title]Codecraft Dashboard[/title]")

    stats = tree.add("[bold]Stats[/bold]")
    stats.add(f"Files tracked: {len(files)}")
    stats.add(f"Concepts used: {len(concepts)}")
    stats.add(f"Concept gaps: {len(gaps)}")
    stats.add(f"Domains available: {len(domains)}")

    debt_branch = tree.add("[bold]Learning Debt[/bold]")
    debt_branch.add(f"Total items: {debt_report.total_items}")
    debt_branch.add(f"Resolved: [success]{debt_report.resolved_items}[/success]")
    debt_branch.add(f"Unresolved: [debt]{len(debt_report.unresolved)}[/debt]")
    debt_branch.add(f"Debt score: [score]{debt_report.score:.1%}[/score]")

    decay_branch = tree.add("[bold]Skill Retention[/bold]")
    decay_branch.add(f"[strength.high]Fresh: {fresh}[/strength.high]")
    decay_branch.add(f"[strength.medium]Stable: {stable}[/strength.medium]")
    decay_branch.add(f"[strength.low]Decaying: {decaying}[/strength.low]")

    if gaps:
        gap_branch = tree.add("[bold]Top Gaps to Practice[/bold]")
        for g in gaps[:5]:
            gap_branch.add(g)

    if debt_report.unresolved:
        top_debt = sorted(debt_report.by_type.items(), key=lambda x: -x[1])[:3]
        debt_branch = tree.add("[bold]Top Debt Patterns[/bold]")
        for pattern, count in top_debt:
            debt_branch.add(f"{pattern.replace('_', ' ').title()}: {count}")

    console.print(tree)


@dashboard_app.command("heatmap")
def show_heatmap(
    tier: int = typer.Option(0, "--tier", "-t", help="Filter by tier (1-4, 0=all)"),
) -> None:
    repo = get_repo()
    concepts = repo.get_all_concept_names()

    scheduler = ForgettingScheduler(repo)
    decay_report = scheduler.get_decay_report()

    if tier:
        decay_report = [r for r in decay_report if r["concept"] in concepts]
        from codecraft.models.concept import ConceptTaxonomy
        decay_report = [
            r for r in decay_report
            if ConceptTaxonomy.get(r["concept"]).tier == Tier(tier)
            or r["concept"] not in ConceptTaxonomy._concepts
        ]

    if not decay_report:
        console.print("[warning]No concept data yet. Run 'codecraft scan' first.[/warning]")
        return

    table = Table(title=f"Concept Heatmap{' (Tier ' + str(tier) + ')' if tier else ''}")
    table.add_column("Concept", style="concept")
    table.add_column("Strength", justify="center")
    table.add_column("Bar")

    for r in decay_report[:30]:
        strength = r["strength"]
        bar_len = max(1, int(strength * 20))
        bar = "#" * bar_len + "-" * (20 - bar_len)
        if strength >= 0.8:
            color = "strength.high"
        elif strength >= 0.6:
            color = "strength.medium"
        else:
            color = "strength.low"
        table.add_row(r["concept"], f"[{color}]{strength:.2f}[/{color}]", f"[{color}]{bar}[/{color}]")

    if len(decay_report) > 30:
        console.print(f"[dim]Showing 30 of {len(decay_report)} concepts[/dim]")
    console.print(table)


@dashboard_app.command("trends")
def show_trends() -> None:
    repo = get_repo()
    concepts = repo.get_all_concept_names()

    if not concepts:
        console.print("[warning]No data yet. Scan some files first.[/warning]")
        return

    from codecraft.models.concept import ConceptTaxonomy

    by_tier = {1: [], 2: [], 3: [], 4: []}
    for name in concepts:
        try:
            c = ConceptTaxonomy.get(name)
            by_tier[c.tier].append(name)
        except KeyError:
            by_tier[1].append(name)

    remix = RemixEngine(repo)
    gaps = remix.find_gaps()

    table = Table(title="Learning Trends")
    table.add_column("Metric", style="bold")
    table.add_column("Value")

    table.add_row("Tier 1 (Seed) concepts", str(len(by_tier[1])))
    table.add_row("Tier 2 (Root) concepts", str(len(by_tier[2])))
    table.add_row("Tier 3 (Branch) concepts", str(len(by_tier[3])))
    table.add_row("Tier 4 (Canopy) concepts", str(len(by_tier[4])))
    table.add_row("Total concepts", str(len(concepts)))
    table.add_row("Concept gaps (need practice)", f"[debt]{len(gaps)}[/debt]")
    table.add_row("Domains available", str(len(remix.get_domain_stats())))
    console.print(table)

    if gaps:
        console.print(f"\n[warning]Gaps to fill:[/warning] {', '.join(gaps[:10])}")
        if len(gaps) > 10:
            console.print(f"[dim]... and {len(gaps) - 10} more[/dim]")
