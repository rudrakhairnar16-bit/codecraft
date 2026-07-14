from __future__ import annotations

from pathlib import Path

import duckdb
import pytest

from codecraft.db.connection import Database
from codecraft.db.migrations import run_migrations


def test_create_in_memory():
    Database.reset()
    db = Database(Path(":memory:"))
    db.db_path = Path(":memory:")
    conn = db.connect()
    assert conn is not None
    conn.execute("SELECT 1").fetchone()
    db.close()


def test_connect_and_close():
    Database.reset()
    db = Database(Path(":memory:"))
    db.db_path = Path(":memory:")
    conn = db.connect()
    assert conn is not None
    run_migrations(conn)
    db.close()
    assert db._conn is None


def test_reconnect():
    Database.reset()
    db = Database(Path(":memory:"))
    db.db_path = Path(":memory:")
    conn1 = db.connect()
    run_migrations(conn1)
    db.close()
    conn2 = db.connect()
    assert conn2 is not None
    conn2.execute("SELECT 1").fetchone()
    db.close()


def test_get_instance():
    Database.reset()
    db1 = Database.get_instance()
    db2 = Database.get_instance()
    assert db1 is db2
    Database.reset()


def test_reset_singleton():
    Database.reset()
    db1 = Database.get_instance()
    Database.reset()
    db2 = Database.get_instance()
    assert db1 is not db2
    Database.reset()


def test_temp_db_file(tmp_path):
    Database.reset()
    db_path = tmp_path / "test.duckdb"
    db = Database(db_path)
    conn = db.connect()
    run_migrations(conn)
    assert db_path.exists()
    db.close()
    Database.reset()


def test_clean_stale_files(tmp_path):
    Database.reset()
    db_path = tmp_path / "codecraft.duckdb"
    stale_wal = tmp_path / "codecraft.wal"
    stale_tmp = tmp_path / "codecraft.tmp"
    stale_wal.write_text("stale")
    stale_tmp.write_text("stale")
    db = Database(db_path)
    conn = db.connect()
    run_migrations(conn)
    assert not stale_wal.exists()
    assert not stale_tmp.exists()
    db.close()
    Database.reset()


def test_was_cleaned_default():
    Database.reset()
    db = Database(Path(":memory:"))
    db.db_path = Path(":memory:")
    conn = db.connect()
    assert not db.was_cleaned
    db.close()
    Database.reset()


def test_double_close():
    Database.reset()
    db = Database(Path(":memory:"))
    db.db_path = Path(":memory:")
    conn = db.connect()
    run_migrations(conn)
    db.close()
    db.close()
    Database.reset()


def test_get_instance_after_reset():
    Database.reset()
    db = Database.get_instance()
    conn = db.connect()
    run_migrations(conn)
    db.close()
    Database.reset()
    db2 = Database.get_instance()
    conn2 = db2.connect()
    assert conn2 is not None
    conn2.execute("SELECT 1").fetchone()
    db2.close()
    Database.reset()


def test_database_init_without_path(tmp_path):
    Database.reset()
    db = Database(db_path=None)
    conn = db.connect()
    assert conn is not None
    db.close()
    Database.reset()


def test_check_health_retry(monkeypatch, tmp_path):
    Database.reset()
    db_path = tmp_path / "test.duckdb"
    db = Database(db_path)
    original_execute = duckdb.DuckDBPyConnection.execute
    select_calls = [0]

    def broken_execute(self, query, *args, **kwargs):
        q = str(query) if not isinstance(query, str) else query
        if "SELECT 1" in q:
            select_calls[0] += 1
            if select_calls[0] <= 2:
                raise duckdb.Error("connection broken")
        return original_execute(self, query, *args, **kwargs)

    monkeypatch.setattr(duckdb.DuckDBPyConnection, "execute", broken_execute)
    conn = db.connect()
    assert conn is not None
    assert db.was_cleaned
    db.close()
    Database.reset()


def test_close_error(monkeypatch):
    Database.reset()
    db = Database(Path(":memory:"))
    db.db_path = Path(":memory:")
    db.connect()
    original_close = duckdb.DuckDBPyConnection.close

    def broken_close(self):
        raise duckdb.Error("close error")

    monkeypatch.setattr(duckdb.DuckDBPyConnection, "close", broken_close)
    db.close()
    assert db._conn is None
    Database.reset()


def test_clean_stale_files_oserror(tmp_path, monkeypatch):
    Database.reset()
    db_path = tmp_path / "codecraft.duckdb"
    stale_wal = tmp_path / "codecraft.wal"
    stale_wal.write_text("stale")
    original_unlink = type(stale_wal).unlink

    def broken_unlink(self, *args, **kwargs):
        if self.name == "codecraft.wal":
            raise OSError("Permission denied")
        return original_unlink(self, *args, **kwargs)

    monkeypatch.setattr(type(stale_wal), "unlink", broken_unlink)
    db = Database(db_path)
    conn = db.connect()
    assert stale_wal.exists()
    db.close()
    Database.reset()


def test_reset_get_profile_dir_error(monkeypatch):
    Database.reset()
    import codecraft.cli.profile_cmd

    def broken_get_profile_dir():
        raise Exception("oops")

    monkeypatch.setattr(codecraft.cli.profile_cmd, "get_profile_dir", broken_get_profile_dir)
    db = Database(db_path=None)
    assert db.db_path == Path.home() / ".codecraft" / "codecraft.duckdb"
    db.close()
    Database.reset()



