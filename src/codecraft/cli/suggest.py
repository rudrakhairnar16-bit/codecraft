from __future__ import annotations

import typer
from rich.panel import Panel
from rich.table import Table

from codecraft.cli.deps import get_repo
from codecraft.cli.debt import DEBT_TO_CONCEPT
from codecraft.engines.debt_tracker import DebtTrackerEngine
from codecraft.engines.remix import RemixEngine
from codecraft.engines.scheduler import ForgettingScheduler
from codecraft.models.concept import ConceptTaxonomy
from codecraft.utils.colors import console

suggest_app = typer.Typer(name="suggest", no_args_is_help=True)


@suggest_app.callback()
def suggest_callback() -> None:
    pass


@suggest_app.command("next")
def suggest_next(
    count: int = typer.Option(5, "--count", "-c", help="Number of suggestions"),
) -> None:
    repo = get_repo()
    known = set(repo.get_all_concept_names())
    suggestions = _compute_suggestions(repo, known, count)
    _display_suggestions(suggestions)


@suggest_app.command("all")
def suggest_all() -> None:
    repo = get_repo()
    known = set(repo.get_all_concept_names())
    suggestions = _compute_suggestions(repo, known, 50)
    _display_suggestions(suggestions)


def _compute_suggestions(repo, known: set, count: int) -> list[dict]:
    all_c = ConceptTaxonomy.all()
    results = []

    debt = DebtTrackerEngine(repo).get_report()
    scheduler = ForgettingScheduler(repo)
    decay = scheduler.get_decay_report()
    decay_map = {r["concept"]: r for r in decay}

    for unresolved in debt.unresolved:
        concept = DEBT_TO_CONCEPT.get(unresolved.pattern_type, unresolved.pattern_type)
        if concept not in known:
            results.append({
                "concept": concept,
                "reason": f"Debt pattern '{unresolved.pattern_type}' found in {unresolved.file_path.name}",
                "priority": 5,
            })

    for r in decay:
        if r["status"] == "decaying" and r["concept"] in known:
            results.append({
                "concept": r["concept"],
                "reason": f"Concept strength decaying ({r['strength']:.0%}) — needs review",
                "priority": 4,
            })

    remix = RemixEngine(repo)
    gaps = remix.find_gaps()
    for g in gaps:
        results.append({
            "concept": g,
            "reason": "Underused concept — generate transfer exercises",
            "priority": 3,
        })

    for c in all_c:
        if c.name not in known:
            results.append({
                "concept": c.name,
                "reason": f"New concept — Tier {c.tier.value} ({c.category})",
                "priority": 2,
            })

    results.sort(key=lambda x: (-x["priority"], x["concept"]))
    seen = set()
    deduped = []
    for r in results:
        if r["concept"] not in seen:
            seen.add(r["concept"])
            deduped.append(r)
    return deduped[:count]


def _display_suggestions(suggestions: list[dict]) -> None:
    if not suggestions:
        console.print("[success]No suggestions — you're on track![/success]")
        return

    console.print(Panel("[title]Suggested Next Steps[/title]"))
    table = Table()
    table.add_column("#", style="bold")
    table.add_column("Concept", style="concept")
    table.add_column("Priority", style="score")
    table.add_column("Reason")
    table.add_column("Action")

    for i, s in enumerate(suggestions, 1):
        priority_colors = {5: "red", 4: "yellow", 3: "cyan", 2: "blue", 1: "dim"}
        priority_str = f"[{priority_colors.get(s['priority'], 'white')}]P{s['priority']}[/]"
        action = f"codecraft practice start {s['concept']}"
        table.add_row(str(i), s["concept"], priority_str, s["reason"][:60], action)
    console.print(table)
