from __future__ import annotations

import typer
from rich.table import Table
from rich.tree import Tree

import time
from datetime import datetime

from codecraft.cli.deps import get_repo
from codecraft.engines.debt_tracker import DebtTrackerEngine
from codecraft.engines.remix import RemixEngine
from codecraft.engines.scheduler import ForgettingScheduler
from codecraft.models.concept import Tier
from codecraft.utils.colors import console

dashboard_app = typer.Typer(name="dashboard", no_args_is_help=True)


@dashboard_app.command("summary", epilog="Example: codecraft dashboard summary")
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


@dashboard_app.command("heatmap", epilog="Example: codecraft dashboard heatmap --tier 1")
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


@dashboard_app.command("trends", epilog="Example: codecraft dashboard trends")
def show_trends() -> None:
    repo = get_repo()
    concepts = repo.get_all_concept_names()

    if not concepts:
        console.print("[warning]No data yet. Scan some files first.[/warning]")
        return

    from codecraft.models.concept import ConceptTaxonomy

    by_tier: dict[int, list[str]] = {1: [], 2: [], 3: [], 4: []}
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


@dashboard_app.command("live", epilog="Example: codecraft dashboard live --interval 3")
def show_live(
    interval: int = typer.Option(2, "--interval", "-i", help="Refresh interval in seconds"),
    max_loops: int = typer.Option(0, "--max", "-m", help="Max refreshes (0=infinite)"),
) -> None:
    from rich.layout import Layout
    from rich.live import Live
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    repo = get_repo()

    def _build_layout() -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="top", size=3),
            Layout(name="body"),
        )
        layout["body"].split_row(
            Layout(name="left"),
            Layout(name="right"),
        )
        layout["body"]["left"].split_column(
            Layout(name="stats"),
            Layout(name="concepts"),
        )
        layout["body"]["right"].split_column(
            Layout(name="debt"),
            Layout(name="reviews"),
        )

        files = repo.get_all_files()
        concepts = repo.get_all_concept_names()
        scheduler = ForgettingScheduler(repo)
        debt_engine = DebtTrackerEngine(repo)
        debt_report = debt_engine.get_report()
        decay_report = scheduler.get_decay_report()
        remix = RemixEngine(repo)
        gaps = remix.find_gaps()
        stats = repo.get_practice_stats()
        streak = repo.get_streak_data()
        decaying = sum(1 for r in decay_report if r["status"] == "decaying")
        stable = sum(1 for r in decay_report if r["status"] == "stable")
        fresh = sum(1 for r in decay_report if r["status"] == "fresh")
        due = scheduler.get_review_queue().due_cards()

        top = Panel(
            Text.assemble(
                (" CodeCraft ", "bold cyan"),
                ("Live Dashboard", "white"),
                (" │ ", "dim"),
                (f"{len(files)} files", "green"),
                (" │ ", "dim"),
                (f"{len(concepts)} concepts", "blue"),
                (" │ ", "dim"),
                (f"{debt_report.score:.0%} debt", "yellow"),
                (" │ ", "dim"),
                (f"{streak['current_streak']}d streak", "magenta"),
                (" │ ", "dim"),
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "bold cyan"),
            ),
            style="bold",
        )
        layout["top"].update(top)

        s = Table(show_header=False, box=None, padding=(0, 2))
        s.add_column()
        s.add_column()
        s.add_row("[bold]Files Scanned[/bold]", str(len(files)))
        s.add_row("[bold]Concepts Detected[/bold]", str(len(concepts)))
        s.add_row("[bold]Concept Gaps[/bold]", f"[debt]{len(gaps)}[/debt]")
        s.add_row("[bold]Practice Sessions[/bold]", str(stats["total_sessions"]))
        s.add_row("[bold]Accuracy[/bold]", f"{stats['correct_sessions'] * 100 // max(stats['total_sessions'], 1)}%" if stats["total_sessions"] else "N/A")
        s.add_row("[bold]Current Streak[/bold]", f"{streak['current_streak']} days")
        s.add_row("[bold]Active Days[/bold]", str(streak["total_active_days"]))
        layout["stats"].update(Panel(s, title="📊 Overview", border_style="cyan"))

        c = Table(show_header=False, box=None, padding=(0, 2))
        c.add_column()
        c.add_column()
        c.add_row("[bold]Fresh[/bold]", f"[strength.high]{fresh}[/strength.high]")
        c.add_row("[bold]Stable[/bold]", f"[strength.medium]{stable}[/strength.medium]")
        c.add_row("[bold]Decaying[/bold]", f"[strength.low]{decaying}[/strength.low]")
        c.add_row("[bold]Due for Review[/bold]", f"[debt]{len(due)}[/debt]")
        layout["concepts"].update(Panel(c, title="🧠 Concept Retention", border_style="green"))

        d = Table(show_header=False, box=None, padding=(0, 2))
        d.add_column()
        d.add_column()
        d.add_row("[bold]Total Items[/bold]", str(debt_report.total_items))
        d.add_row("[bold]Resolved[/bold]", f"[success]{debt_report.resolved_items}[/success]")
        d.add_row("[bold]Unresolved[/bold]", f"[debt]{len(debt_report.unresolved)}[/debt]")
        d.add_row("[bold]Debt Score[/bold]", f"[score]{debt_report.score:.1%}[/score]")

        if debt_report.unresolved:
            top_patterns = sorted(debt_report.by_type.items(), key=lambda x: -x[1])[:4]
            d.add_section()
            d.add_row("[bold]Top Patterns[/bold]", "")
            for pattern, count in top_patterns:
                d.add_row(f"  {pattern.replace('_', ' ').title()}", str(count))
        layout["debt"].update(Panel(d, title="💳 Learning Debt", border_style="yellow"))

        r = Table(show_header=False, box=None, padding=(0, 2))
        r.add_column()
        r.add_column()
        for card in due[:6]:
            status = "fresh" if card.strength >= 0.8 else ("stable" if card.strength >= 0.6 else "decaying")
            color = "strength.high" if status == "fresh" else ("strength.medium" if status == "stable" else "strength.low")
            r.add_row(card.concept_name, f"[{color}]{card.strength:.0%}[/{color}]")
        if not due:
            r.add_row("[dim]No reviews due[/dim]", "")
        layout["reviews"].update(Panel(r, title="📅 Due for Review", border_style="magenta"))

        return layout

    loop = 0
    with Live(_build_layout(), refresh_per_second=1 / interval, screen=True) as live:
        try:
            while True:
                loop += 1
                if max_loops and loop > max_loops:
                    break
                time.sleep(interval)
                live.update(_build_layout())
        except KeyboardInterrupt:
            pass

    console.print("[success]Live dashboard closed.[/success]")
