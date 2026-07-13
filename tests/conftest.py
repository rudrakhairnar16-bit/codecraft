import os
from collections.abc import Generator
from pathlib import Path

import duckdb
import pytest

from codecraft.db.connection import Database
from codecraft.db.migrations import run_migrations
from codecraft.db.repository import Repository

os.environ.setdefault("NO_COLOR", "1")


@pytest.fixture
def db() -> Generator[Database, None, None]:
    Database.reset()
    db = Database.get_instance()
    conn = db.connect()
    run_migrations(conn)
    yield db
    Database.reset()


@pytest.fixture
def in_memory_db() -> Generator[duckdb.DuckDBPyConnection, None, None]:
    conn = duckdb.connect(":memory:")
    yield conn
    conn.close()


@pytest.fixture
def repo(db: Database) -> Repository:
    conn = db.connect()
    return Repository(conn)


@pytest.fixture
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def beginner_file(fixtures_dir: Path) -> Path:
    return fixtures_dir / "beginner.py"


@pytest.fixture
def intermediate_file(fixtures_dir: Path) -> Path:
    return fixtures_dir / "intermediate.py"


@pytest.fixture
def advanced_file(fixtures_dir: Path) -> Path:
    return fixtures_dir / "advanced.py"
