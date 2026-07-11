from codecraft.db.connection import Database
from codecraft.db.migrations import run_migrations
from codecraft.db.repository import Repository
from codecraft.utils.colors import console


def init_db() -> Repository:
    db = Database.get_instance()
    conn = db.connect()
    run_migrations(conn)
    if db.was_cleaned:
        console.print("[warning]Database was corrupted — auto-cleaned and recreated.[/warning]")
    return Repository(conn)


def get_repo() -> Repository:
    db = Database.get_instance()
    conn = db.connect()
    return Repository(conn)
