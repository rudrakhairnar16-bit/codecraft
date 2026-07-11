from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import duckdb


class Database:
    _instance: Optional["Database"] = None

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_dir = Path.home() / ".codecraft"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = db_dir / "codecraft.duckdb"
        self.db_path = db_path
        self._conn: Optional[duckdb.DuckDBPyConnection] = None

    def connect(self) -> duckdb.DuckDBPyConnection:
        if self._conn is None:
            self._conn = duckdb.connect(str(self.db_path))
            self._conn.execute("PRAGMA enable_progress_bar")
        return self._conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    @classmethod
    def get_instance(cls) -> "Database":
        if cls._instance is None:
            cls._instance = Database()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        if cls._instance is not None:
            cls._instance.close()
        db_dir = Path.home() / ".codecraft"
        db_path = db_dir / "codecraft.duckdb"
        if db_path.exists():
            db_path.unlink()
        cls._instance = None
