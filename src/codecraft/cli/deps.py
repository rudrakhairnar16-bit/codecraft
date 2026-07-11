from codecraft.db.connection import Database
from codecraft.db.migrations import run_migrations
from codecraft.db.repository import Repository


def init_db() -> Repository:
    db = Database.get_instance()
    conn = db.connect()
    run_migrations(conn)
    return Repository(conn)


def get_repo() -> Repository:
    db = Database.get_instance()
    conn = db.connect()
    return Repository(conn)
