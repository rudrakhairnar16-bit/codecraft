from __future__ import annotations

import time
from pathlib import Path

import duckdb


class Database:
    _instance: Database | None = None

    def __init__(self, db_path: Path | None = None):
        if db_path is None:
            db_dir = Path.home() / ".codecraft"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = db_dir / "codecraft.duckdb"
        self.db_path = db_path
        self._conn: duckdb.DuckDBPyConnection | None = None
        self._cleaned = False

    def connect(self) -> duckdb.DuckDBPyConnection:
        if self._conn is None:
            self._clean_stale_files()
            self._conn = duckdb.connect(str(self.db_path))
            self._conn.execute("PRAGMA enable_progress_bar")
            self._check_health()
        return self._conn

    def _clean_stale_files(self) -> None:
        for suffix in [".wal", ".tmp", ".db"]:
            stale = self.db_path.parent / f"{self.db_path.stem}{suffix}"
            if stale.exists() and stale != self.db_path:
                try:
                    stale.unlink()
                except OSError:
                    pass

    def _check_health(self, retries: int = 2) -> None:
        for attempt in range(retries):
            try:
                self._conn.execute("SELECT 1").fetchone()
                return
            except duckdb.Error:
                if attempt < retries - 1:
                    self._conn.close()
                    self._conn = None
                    time.sleep(0.5)
                    self._clean_stale_files()
                    self._conn = duckdb.connect(str(self.db_path))
                    self._conn.execute("PRAGMA enable_progress_bar")
                else:
                    self._conn.close()
                    self._conn = None
                    self.reset()
                    self._conn = duckdb.connect(str(self.db_path))
                    self._conn.execute("PRAGMA enable_progress_bar")
                    self._cleaned = True
                    break

    @property
    def was_cleaned(self) -> bool:
        return self._cleaned

    def close(self) -> None:
        if self._conn is not None:
            try:
                self._conn.close()
            except duckdb.Error:
                pass
            self._conn = None

    @classmethod
    def get_instance(cls) -> Database:
        if cls._instance is None:
            cls._instance = Database()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        if cls._instance is not None:
            cls._instance.close()
        db_dir = Path.home() / ".codecraft"
        for f in db_dir.glob("codecraft*"):
            try:
                f.unlink()
            except OSError:
                pass
        cls._instance = None
