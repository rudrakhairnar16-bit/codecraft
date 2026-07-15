from __future__ import annotations

import datetime
import shutil
from pathlib import Path
from typing import Any

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


def backup_db(label: str = "") -> Path | None:
    db = Database.get_instance()
    src = Path(db.db_path)
    if not src.exists():
        console.print("[warning]No database file found to back up[/warning]")
        return None
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    tag = f"_{label}" if label else ""
    bak = src.with_name(f"codecraft_{ts}{tag}.duckdb.bak")
    try:
        shutil.copy2(str(src), str(bak))
        console.print(f"[info]Backup saved: {bak.name}[/info]")
        return bak
    except Exception as e:
        console.print(f"[error]Backup failed: {e}[/error]")
        return None
