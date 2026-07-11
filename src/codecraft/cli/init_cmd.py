from __future__ import annotations

from pathlib import Path

import typer
from rich.panel import Panel
from rich.table import Table

from codecraft.cli.deps import get_repo
from codecraft.db.connection import Database
from codecraft.models.concept import ConceptTaxonomy
from codecraft.utils.colors import console

init_app = typer.Typer(name="init", no_args_is_help=True)


@init_app.callback()
def init_callback() -> None:
    pass


@init_app.command("all")
def init_all(
    force: bool = typer.Option(False, "--force", "-f", help="Reinitialize even if already set up"),
) -> None:
    repo = get_repo()
    already = repo.get_setting("initialized", "")
    if already and not force:
        console.print("[warning]CodeCraft is already initialized. Use --force to reinitialize.[/warning]")
        return

    db_path = Database.get_instance().db_path
    console.print(Panel("[title]Initializing CodeCraft...[/title]"))

    seed = repo.get_setting("concepts_seeded", "0")
    if seed != "1" or force:
        count = 0
        for c in ConceptTaxonomy.all():
            repo.conn.execute(
                "INSERT OR IGNORE INTO concepts (name, tier, category, description) VALUES (?, ?, ?, ?)",
                [c.name, c.tier.value, c.category, c.description],
            )
            count += 1
        repo.set_setting("concepts_seeded", "1")
        console.print(f"[success]Seeded {count} concepts into database[/success]")

    repo.set_setting("initialized", "1")
    repo.set_setting("inited_at", str(__import__("datetime").datetime.now()))

    console.print(f"[success]CodeCraft initialized![/success]")
    console.print(f"  Database: [path]{db_path}[/path]")
    console.print(f"  Concepts: {len(ConceptTaxonomy.all())}")
    console.print(f"\n[info]Next steps:[/info]")
    console.print(f"  1. [bold]codecraft scan dir .[/bold] — scan your Python files")
    console.print(f"  2. [bold]codecraft practice path beginner[/bold] — start learning")
    console.print(f"  3. [bold]codecraft suggest next[/bold] — get personalized suggestions")


@init_app.command("reset")
def init_reset() -> None:
    confirm = typer.confirm("This will delete all data. Are you sure?")
    if not confirm:
        console.print("[warning]Reset cancelled.[/warning]")
        return
    db = Database.get_instance()
    db_path = Path(db.db_path)
    if db_path.exists():
        db_path.unlink()
    for tmp in Path(db_path.parent).glob("codecraft*"):
        if tmp.suffix in (".wal", ".tmp"):
            tmp.unlink()
    console.print("[success]Database reset. Run [bold]codecraft init all[/bold] to set up fresh.[/success]")
