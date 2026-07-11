from __future__ import annotations

import typer

from codecraft.cli.scan import scan_app
from codecraft.cli.debt import debt_app
from codecraft.cli.remix import remix_app
from codecraft.cli.schedule import schedule_app
from codecraft.cli.dashboard import dashboard_app
from codecraft.cli.practice import practice_app
from codecraft.cli.deps import init_db
from codecraft.utils.colors import console

app = typer.Typer(
    name="codecraft",
    help="Your personal Python skill forge — scan, analyze, and master Python concepts.",
    no_args_is_help=True,
)

app.add_typer(scan_app, name="scan", help="Scan Python files and extract concept fingerprints")
app.add_typer(debt_app, name="debt", help="Track and resolve learning debt")
app.add_typer(remix_app, name="remix", help="Generate transfer exercises in new contexts")
app.add_typer(schedule_app, name="schedule", help="Spaced repetition review scheduler")
app.add_typer(dashboard_app, name="dashboard", help="Cross-engine insights and trends")
app.add_typer(practice_app, name="practice", help="Timed practice with solution analysis")


@app.callback()
def main() -> None:
    init_db()


if __name__ == "__main__":
    app()
