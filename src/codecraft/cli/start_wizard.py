from __future__ import annotations

import typer

from codecraft.cli.deps import get_repo
from codecraft.engines.debt_tracker import DebtTrackerEngine
from codecraft.engines.remix import RemixEngine
from codecraft.engines.scheduler import ForgettingScheduler

wizard_app = typer.Typer(name="start", help="Interactive setup wizard")


@wizard_app.callback(invoke_without_command=True)
def start_wizard(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is not None:
        return
    repo = get_repo()
    known = repo.get_all_concept_names()

    print("")
    print("=" * 60)
    print("  CodeCraft Setup Wizard")
    print("=" * 60)

    if not known:
        print("\nStep 1/4: Scan your code")
        print("  Run:  codecraft scan dir .")
        print("  This will scan all Python files in your project")
    else:
        print(f"\nStep 1/4: Scan your code  [already scanned {len(known)} concepts]")
        remix = RemixEngine(repo)
        gaps = remix.find_gaps()
        debt = DebtTrackerEngine(repo)
        scheduler = ForgettingScheduler(repo)
        decay = scheduler.get_decay_report()
        decaying = sum(1 for r in decay if r["status"] == "decaying")
        print(f"  Gaps: {len(gaps)}  |  Decaying: {decaying}  |  Debt: {debt.get_report().score:.0%}")

    print("\nStep 2/4: Learning suggestions")
    print("  Run:  codecraft suggest next")
    if known:
        print("  Analyzes your debt, gaps, and decay to recommend next steps")

    print("\nStep 3/4: Start learning")
    print("  Run:  codecraft practice path beginner")
    print("  Or:   codecraft practice start <concept>")

    print("\nStep 4/4: Check progress")
    print("  Run:  codecraft status")
    print("  Run:  codecraft dashboard summary")

    print("\n" + "=" * 60)
    print("  Wizard complete!")
    print("  Run  codecraft --help  to see all 30+ commands")
    print("=" * 60)
