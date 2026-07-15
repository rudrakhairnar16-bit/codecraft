from __future__ import annotations

import os
from pathlib import Path

os.environ["NO_COLOR"] = "1"
os.environ["TERM"] = "xterm"

import pytest
from typer.testing import CliRunner

from codecraft.cli.app import app


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_project(tmp_path: Path) -> Path:
    d = tmp_path / "my_project"
    d.mkdir()

    (d / "main.py").write_text('''"""Main module."""
import json
from pathlib import Path

DATA_DIR = Path("data")


def load_config(path: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}") from e


class Stats:
    def __init__(self) -> None:
        self.count = 0
        self.items: list[float] = []

    def add(self, value: float) -> None:
        self.items.append(value)
        self.count += 1

    def average(self) -> float:
        if not self.items:
            return 0.0
        return sum(self.items) / len(self.items)

    def __repr__(self) -> str:
        return f"Stats(count={self.count})"


def compute_metrics(data: list[dict]) -> dict[str, float]:
    result: dict[str, float] = {}
    for entry in data:
        for key, val in entry.items():
            if isinstance(val, (int, float)):
                result[key] = result.get(key, 0) + float(val)
    return result


async def run_async() -> None:
    import asyncio
    await asyncio.sleep(0.01)
    print("done")


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_async())
''')

    (d / "utils.py").write_text('''"""Utility functions."""
from collections.abc import Callable
from functools import wraps


def timer(fn: Callable) -> Callable:
    @wraps(fn)
    def wrapper(*args, **kwargs):
        import time
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{fn.__name__} took {elapsed:.3f}s")
        return result
    return wrapper


@timer
def slow_add(a: int, b: int) -> int:
    total = a
    for _ in range(1000):
        total += 0
    total += b
    return total


def fibonacci(n: int) -> list[int]:
    seq = [0, 1]
    for i in range(2, n):
        seq.append(seq[i - 1] + seq[i - 2])
    return seq


class Stack:
    def __init__(self) -> None:
        self._items: list[int] = []

    def push(self, item: int) -> None:
        self._items.append(item)

    def pop(self) -> int | None:
        return self._items.pop() if self._items else None

    @property
    def size(self) -> int:
        return len(self._items)
''')

    (d / "models.py").write_text('''"""Data models."""
from dataclasses import dataclass
from typing import Protocol


class Serializer(Protocol):
    def serialize(self) -> dict:
        ...


@dataclass
class User:
    name: str
    email: str
    age: int = 0

    def greet(self) -> str:
        return f"Hello, {self.name}!"


class UserManager:
    def __init__(self) -> None:
        self.users: dict[str, User] = {}

    def add(self, user: User) -> None:
        if user.email in self.users:
            raise ValueError(f"Duplicate email: {user.email}")
        self.users[user.email] = user

    def find(self, email: str) -> User | None:
        return self.users.get(email)

    @property
    def count(self) -> int:
        return len(self.users)
''')

    (d / "test_main.py").write_text('''"""Tests."""
def test_stats():
    from main import Stats
    s = Stats()
    s.add(10)
    s.add(20)
    assert s.average() == 15.0
    assert s.count == 2
''')

    return d


class TestSmokeFlow:
    def test_full_flow(self, runner, tmp_path):
        project = tmp_path / "my_project"
        project.mkdir()
        (project / "main.py").write_text("x = 1\ny = 2\nprint(x + y)\n")

        result = runner.invoke(app, ["scan", "dir", str(project)])
        assert result.exit_code == 0

    def test_init_then_scan_file(self, runner, fixtures_dir):
        result = runner.invoke(app, ["init", "all", "--force"])
        assert result.exit_code == 0

        result = runner.invoke(app, ["scan", "file", str(fixtures_dir / "beginner.py")])
        assert result.exit_code == 0

    def test_debt_report_after_scan(self, runner, fixtures_dir):
        runner.invoke(app, ["init", "all", "--force"])
        runner.invoke(app, ["scan", "file", str(fixtures_dir / "beginner.py")])
        result = runner.invoke(app, ["debt", "report"])
        assert result.exit_code == 0

    def test_debt_list_after_scan(self, runner, fixtures_dir):
        runner.invoke(app, ["init", "all", "--force"])
        runner.invoke(app, ["scan", "file", str(fixtures_dir / "beginner.py")])
        result = runner.invoke(app, ["debt", "list"])
        assert result.exit_code == 0

    def test_debt_challenge_after_scan(self, runner, fixtures_dir):
        runner.invoke(app, ["init", "all", "--force"])
        runner.invoke(app, ["scan", "file", str(fixtures_dir / "beginner.py")])
        result = runner.invoke(app, ["debt", "challenge"])
        assert result.exit_code == 0

    def test_remix_gaps_after_scan(self, runner, fixtures_dir):
        runner.invoke(app, ["init", "all", "--force"])
        runner.invoke(app, ["scan", "file", str(fixtures_dir / "beginner.py")])
        result = runner.invoke(app, ["remix", "gaps"])
        assert result.exit_code == 0

    def test_remix_generate_after_scan(self, runner, fixtures_dir):
        runner.invoke(app, ["init", "all", "--force"])
        runner.invoke(app, ["scan", "file", str(fixtures_dir / "beginner.py")])
        result = runner.invoke(app, ["remix", "generate", "for_loop"])
        assert result.exit_code == 0

    def test_remix_domains_after_scan(self, runner, fixtures_dir):
        runner.invoke(app, ["init", "all", "--force"])
        runner.invoke(app, ["scan", "file", str(fixtures_dir / "beginner.py")])
        result = runner.invoke(app, ["remix", "domains"])
        assert result.exit_code == 0

    def test_schedule_queue_after_scan(self, runner, fixtures_dir):
        runner.invoke(app, ["init", "all", "--force"])
        runner.invoke(app, ["scan", "file", str(fixtures_dir / "beginner.py")])
        result = runner.invoke(app, ["schedule", "queue"])
        assert result.exit_code == 0

    def test_schedule_due_after_scan(self, runner, fixtures_dir):
        runner.invoke(app, ["init", "all", "--force"])
        runner.invoke(app, ["scan", "file", str(fixtures_dir / "beginner.py")])
        result = runner.invoke(app, ["schedule", "due"])
        assert result.exit_code == 0

    def test_dashboard_summary_after_scan(self, runner, fixtures_dir):
        runner.invoke(app, ["init", "all", "--force"])
        runner.invoke(app, ["scan", "file", str(fixtures_dir / "beginner.py")])
        result = runner.invoke(app, ["dashboard", "summary"])
        assert result.exit_code == 0

    def test_dashboard_heatmap_after_scan(self, runner, fixtures_dir):
        runner.invoke(app, ["init", "all", "--force"])
        runner.invoke(app, ["scan", "file", str(fixtures_dir / "beginner.py")])
        result = runner.invoke(app, ["dashboard", "heatmap"])
        assert result.exit_code == 0

    def test_dashboard_trends_after_scan(self, runner, fixtures_dir):
        runner.invoke(app, ["init", "all", "--force"])
        runner.invoke(app, ["scan", "file", str(fixtures_dir / "beginner.py")])
        result = runner.invoke(app, ["dashboard", "trends"])
        assert result.exit_code == 0

    def test_practice_list_after_scan(self, runner, fixtures_dir):
        runner.invoke(app, ["init", "all", "--force"])
        runner.invoke(app, ["scan", "file", str(fixtures_dir / "beginner.py")])
        result = runner.invoke(app, ["practice", "list"])
        assert result.exit_code == 0

    def test_practice_path_after_scan(self, runner, fixtures_dir):
        runner.invoke(app, ["init", "all", "--force"])
        runner.invoke(app, ["scan", "file", str(fixtures_dir / "beginner.py")])
        result = runner.invoke(app, ["practice", "path", "beginner"])
        assert result.exit_code == 0

    def test_progress_overview_after_scan(self, runner, fixtures_dir):
        runner.invoke(app, ["init", "all", "--force"])
        runner.invoke(app, ["scan", "file", str(fixtures_dir / "beginner.py")])
        result = runner.invoke(app, ["progress", "overview"])
        assert result.exit_code == 0

    def test_status_after_scan(self, runner, fixtures_dir):
        runner.invoke(app, ["init", "all", "--force"])
        runner.invoke(app, ["scan", "file", str(fixtures_dir / "beginner.py")])
        result = runner.invoke(app, ["status"])
        assert result.exit_code == 0

    def test_suggest_after_scan(self, runner, fixtures_dir):
        runner.invoke(app, ["init", "all", "--force"])
        runner.invoke(app, ["scan", "file", str(fixtures_dir / "beginner.py")])
        result = runner.invoke(app, ["suggest", "next"])
        assert result.exit_code == 0

    def test_learn_after_scan(self, runner, fixtures_dir):
        runner.invoke(app, ["init", "all", "--force"])
        run_result = runner.invoke(app, ["scan", "file", str(fixtures_dir / "beginner.py")])
        result = runner.invoke(app, ["learn", "concept", "for_loop"])
        assert result.exit_code == 0

    def test_stats_after_scan(self, runner, fixtures_dir):
        runner.invoke(app, ["init", "all", "--force"])
        runner.invoke(app, ["scan", "file", str(fixtures_dir / "beginner.py")])
        result = runner.invoke(app, ["stats", "sessions"])
        assert result.exit_code == 0

    def test_export_json_after_scan(self, runner, fixtures_dir, tmp_path):
        runner.invoke(app, ["init", "all", "--force"])
        runner.invoke(app, ["scan", "file", str(fixtures_dir / "beginner.py")])
        out = tmp_path / "export.json"
        result = runner.invoke(app, ["export", "json", "--output", str(out)])
        assert result.exit_code == 0
        assert out.exists()

    def test_export_csv_after_scan(self, runner, fixtures_dir, tmp_path):
        runner.invoke(app, ["init", "all", "--force"])
        runner.invoke(app, ["scan", "file", str(fixtures_dir / "beginner.py")])
        out = tmp_path / "export.csv"
        result = runner.invoke(app, ["export", "csv", "--output", str(out)])
        assert result.exit_code == 0
        assert out.exists()

    def test_sync_export_import_roundtrip(self, runner, fixtures_dir, tmp_path):
        runner.invoke(app, ["init", "all", "--force"])
        runner.invoke(app, ["scan", "file", str(fixtures_dir / "beginner.py")])
        out = tmp_path / "codecraft_backup.json"
        result = runner.invoke(app, ["sync", "export", str(out)])
        assert result.exit_code == 0
        assert out.exists()
        result = runner.invoke(app, ["sync", "import", str(out)])
        assert result.exit_code == 0

    def test_vacuum_after_scan(self, runner, fixtures_dir):
        runner.invoke(app, ["init", "all", "--force"])
        runner.invoke(app, ["scan", "file", str(fixtures_dir / "beginner.py")])
        result = runner.invoke(app, ["vacuum", "run"])
        assert result.exit_code == 0

    def test_full_e2e_flow(self, runner, tmp_path, fixtures_dir):
        project = tmp_path / "e2e_project"
        project.mkdir()
        for f in ["main.py", "utils.py", "models.py"]:
            (project / f).write_text((fixtures_dir / "beginner.py").read_text())

        cmds = [
            (["scan", "dir", str(project)], "scan dir"),
            (["debt", "report"], "debt report"),
            (["debt", "list"], "debt list"),
            (["remix", "gaps"], "remix gaps"),
            (["remix", "generate", "for_loop", "--domain", "gaming"], "remix generate"),
            (["remix", "domains"], "remix domains"),
            (["schedule", "queue"], "schedule queue"),
            (["schedule", "due"], "schedule due"),
            (["dashboard", "summary"], "dashboard summary"),
            (["practice", "list"], "practice list"),
            (["practice", "path", "beginner"], "practice path beginner"),
            (["progress", "overview"], "progress overview"),
            (["status"], "status"),
            (["suggest", "next"], "suggest next"),
            (["learn", "concept", "for_loop"], "learn concept"),
            (["stats", "sessions"], "stats sessions"),
        ]
        for args, label in cmds:
            result = runner.invoke(app, args)
            assert result.exit_code == 0, f"{label} failed: {result.stdout[:200]}"
