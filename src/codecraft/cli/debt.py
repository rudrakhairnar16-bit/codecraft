from __future__ import annotations

import typer
from rich.panel import Panel
from rich.table import Table

from codecraft.cli.deps import get_repo
from codecraft.engines.debt_tracker import DebtTrackerEngine
from codecraft.utils.colors import console

DEBT_TO_CONCEPT = {
    "bare_except": "try_except",
    "broad_except": "try_except",
    "mutable_default": "function_def",
    "range_len": "enumerate",
    "if_elif_chain": "dict_comprehension",
    "magic_number": "variable_assignment",
    "too_many_returns": "function_def",
    "nested_conditional": "if_else",
    "unused_variable": "variable_assignment",
    "star_import": "import_basic",
}

debt_app = typer.Typer(name="debt", no_args_is_help=True)


@debt_app.command("report")
def debt_report() -> None:
    repo = get_repo()
    engine = DebtTrackerEngine(repo)
    report = engine.get_report()

    console.print(Panel("[title]Learning Debt Report[/title]"))
    console.print(f"Total debt items: [bold]{report.total_items}[/bold]")
    console.print(f"Resolved: [success]{report.resolved_items}[/success]")
    console.print(f"Unresolved: [debt]{len(report.unresolved)}[/debt]")
    console.print(f"Debt score: [score]{report.score:.1%}[/score]")

    if report.by_type:
        table = Table(title="Debt by Pattern")
        table.add_column("Pattern", style="debt")
        table.add_column("Count", justify="right")
        for pattern, count in sorted(report.by_type.items(), key=lambda x: -x[1]):
            table.add_row(pattern.replace("_", " ").title(), str(count))
        console.print(table)

    if not report.unresolved:
        console.print("[success]No unresolved debt! Great job.[/success]")


@debt_app.command("list")
def debt_list(
    pattern: str | None = typer.Option(None, "--type", "-t", help="Filter by pattern type"),
) -> None:
    repo = get_repo()
    engine = DebtTrackerEngine(repo)
    report = engine.get_report()

    items = report.unresolved
    if pattern:
        items = [i for i in items if i.pattern_type == pattern]

    if not items:
        console.print("[success]No unresolved debt items matching criteria.[/success]")
        return

    table = Table(title=f"Unresolved Debt ({len(items)})")
    table.add_column("ID", style="dim")
    table.add_column("Pattern", style="debt")
    table.add_column("File", style="path")
    table.add_column("Difficulty")
    table.add_column("Suggestion")

    for i, item in enumerate(items, 1):
        table.add_row(
            str(i),
            item.pattern_type.replace("_", " ").title(),
            str(item.file_path.name),
            str(item.difficulty),
            item.suggestion[:50] + "..." if len(item.suggestion) > 50 else item.suggestion,
        )
    console.print(table)


@debt_app.command("challenge")
def debt_challenge(
    item_id: int | None = typer.Argument(None, help="Debt item index from list"),
    domain: str = typer.Option("gaming", "--domain", "-d", help="Domain context for practice"),
) -> None:
    repo = get_repo()
    engine = DebtTrackerEngine(repo)
    report = engine.get_report()

    if not report.unresolved:
        console.print("[success]No unresolved debt! Nothing to challenge.[/success]")
        return

    if item_id is None or item_id < 1 or item_id > len(report.unresolved):
        item = report.unresolved[0]
        console.print("[warning]No item specified, showing first unresolved item[/warning]")
    else:
        item = report.unresolved[item_id - 1]

    challenge = engine.generate_challenge(item)

    console.print(Panel(f"[title]Challenge: {challenge.title}[/title]"))
    console.print(f"[info]Description:[/info] {challenge.description}")
    console.print("\n[debt]Your current code:[/debt]")
    console.print(Panel(challenge.code_snippet, border_style="red"))
    console.print("\n[success]Goal:[/success] Rewrite using the suggested approach")
    console.print(Panel(challenge.expected_solution, border_style="green"))
    console.print("\n[info]Hints:[/info]")
    for h in challenge.hints:
        console.print(f"  [warning]->[/warning] {h}")
    console.print(f"\nSource: [path]{item.file_path}:{item.pattern_location}[/path]")
    concept = DEBT_TO_CONCEPT.get(item.pattern_type, item.pattern_type)
    practice_cmd = f"codecraft practice start {concept} --domain {domain}"
    console.print(f"\n[info]Practice:[/info] {practice_cmd}")
