from __future__ import annotations

from datetime import datetime

import typer
from rich.panel import Panel
from rich.table import Table

from codecraft.cli.deps import get_repo, init_db
from codecraft.utils.colors import console

app = typer.Typer(
    name="codecraft",
    help="Your personal Python skill forge - scan, analyze, and master Python concepts.",
    no_args_is_help=True,
    pretty_exceptions_enable=False,
)

IS_QUIET = False


def _lazy_import(name: str):
    import importlib
    return importlib.import_module(name)


def _quiet() -> bool:
    global IS_QUIET
    return IS_QUIET


@app.callback()
def main(
    ctx: typer.Context,
    quiet: bool = typer.Option(False, "--quiet", help="Minimal output mode", is_eager=True),
    lang: str | None = typer.Option(None, "--lang", help="Language locale (en, hi)", is_eager=True),
) -> None:
    global IS_QUIET
    IS_QUIET = quiet
    if lang:
        from codecraft.utils.i18n import set_locale
        set_locale(lang)
    repo = init_db()
    if not _quiet():
        _check_onboarding(repo)


def _check_onboarding(repo) -> None:
    inited = repo.get_setting("onboarded", "")
    if inited:
        return
    console.print(Panel("[title]Welcome to CodeCraft![/title]\n\n"
                        "Your personal Python skill forge.\n\n"
                        "[info]Quick start:[/info]\n"
                        "  1. [bold]codecraft scan dir .[/bold] - scan your Python files\n"
                        "  2. [bold]codecraft suggest next[/bold] - see what to learn next\n"
                        "  3. [bold]codecraft practice path beginner[/bold] - start learning\n"
                        "  4. [bold]codecraft dashboard summary[/bold] - see your progress\n\n"
                        "Run [bold]codecraft --help[/bold] for all commands."))
    repo.set_setting("onboarded", "1")


@app.command("status", help="Show aggregated learning status")
def show_status(
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    repo = get_repo()

    files = repo.get_all_files()
    concepts = repo.get_all_concept_names()

    debt_mod = _lazy_import("codecraft.engines.debt_tracker")
    debt_engine = debt_mod.DebtTrackerEngine(repo)
    debt_report = debt_engine.get_report()

    sched_mod = _lazy_import("codecraft.engines.scheduler")
    scheduler = sched_mod.ForgettingScheduler(repo)
    decay_report = scheduler.get_decay_report()
    due = scheduler.get_review_queue().due_cards()

    decaying = sum(1 for r in decay_report if r["status"] == "decaying")
    stable = sum(1 for r in decay_report if r["status"] == "stable")

    remix_mod = _lazy_import("codecraft.engines.remix")
    remix = remix_mod.RemixEngine(repo)
    gaps = remix.find_gaps()

    stats = repo.get_practice_stats()
    streak = repo.get_streak_data()

    if json_output:
        import json as _json
        data = {
            "files": len(files),
            "concepts": len(concepts),
            "gaps": len(gaps),
            "debt_score": round(debt_report.score, 2),
            "unresolved_debt": len(debt_report.unresolved),
            "sessions": stats["total_sessions"],
            "accuracy": round(stats['correct_sessions'] * 100 / max(stats['total_sessions'], 1)),
            "streak_days": streak["current_streak"],
            "stable": stable,
            "decaying": decaying,
            "due_reviews": len(due),
        }
        print(_json.dumps(data, indent=2))
        return

    if _quiet():
        print(f"files={len(files)} concepts={len(concepts)} gaps={len(gaps)} debt={debt_report.score:.0%} sessions={stats['total_sessions']} streak={streak['current_streak']}d decaying={decaying}")
        return

    console.print(Panel(f"[title]CodeCraft Status - {datetime.now().strftime('%Y-%m-%d %H:%M')}[/title]"))

    table = Table(show_header=False)
    table.add_column("Metric", style="bold")
    table.add_column("Value")

    table.add_row("Files scanned", str(len(files)))
    table.add_row("Concepts detected", str(len(concepts)))
    table.add_row("Concept gaps", f"[debt]{len(gaps)}[/debt]")
    table.add_row("Debt score", f"[score]{debt_report.score:.0%}[/score]")
    table.add_row("Unresolved debt", f"[debt]{len(debt_report.unresolved)}[/debt]")
    table.add_row("Practice sessions", str(stats["total_sessions"]))
    table.add_row("Accuracy", f"{stats['correct_sessions'] * 100 // max(stats['total_sessions'], 1)}%" if stats["total_sessions"] else "N/A")
    table.add_row("Streak", f"{streak['current_streak']} days")
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
    if not concepts:
        next_steps.append("[info]codecraft scan dir .[/info] to scan your Python files")

    if next_steps:
        console.print("\n[bold]Suggested next:[/bold]")
        for step in next_steps:
            console.print(f"  -> {step}")


# Lazy registration to avoid circular imports
def _register_apps():
    import codecraft.cli.scan as sc
    import codecraft.cli.debt as dt
    import codecraft.cli.remix as rx
    import codecraft.cli.schedule as sch
    import codecraft.cli.dashboard as db
    import codecraft.cli.practice as pr
    import codecraft.cli.progress as pg
    import codecraft.cli.suggest as sg
    import codecraft.cli.learn as ln
    import codecraft.cli.stats_cmd as st
    import codecraft.cli.export_data as ex
    import codecraft.cli.init_cmd as ic
    import codecraft.cli.start_wizard as wz
    import codecraft.cli.vacuum as vc
    import codecraft.cli.precommit_hook as pc

    app.add_typer(sc.scan_app, name="scan", help="Scan Python files and extract concept fingerprints")
    app.add_typer(dt.debt_app, name="debt", help="Track and resolve learning debt")
    app.add_typer(rx.remix_app, name="remix", help="Generate transfer exercises in new contexts")
    app.add_typer(sch.schedule_app, name="schedule", help="Spaced repetition review scheduler")
    app.add_typer(db.dashboard_app, name="dashboard", help="Cross-engine insights and trends")
    app.add_typer(pr.practice_app, name="practice", help="Timed practice with solution analysis")
    app.add_typer(pg.progress_app, name="progress", help="Track your learning progress and streaks")
    app.add_typer(sg.suggest_app, name="suggest", help="Get personalized next-step suggestions")
    app.add_typer(ln.learn_app, name="learn", help="Guided learning for any concept")
    app.add_typer(st.stats_app, name="stats", help="Session statistics and accuracy tracking")
    app.add_typer(ex.export_app, name="export", help="Export your data to JSON or CSV")
    app.add_typer(ic.init_app, name="init", help="Initialize or reset CodeCraft")
    app.add_typer(wz.wizard_app, name="start", help="Interactive setup wizard")
    app.add_typer(vc.vacuum_app, name="vacuum", help="Compact and deduplicate database")
    app.add_typer(pc.precommit_app, name="precommit", help="Generate pre-commit hook config")


_register_apps()


if __name__ == "__main__":
    app()
