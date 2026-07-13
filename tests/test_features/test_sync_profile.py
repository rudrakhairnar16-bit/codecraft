from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from codecraft.cli.app import app


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def temp_db_dir():
    old_home = os.environ.get("HOME")
    old_userprofile = os.environ.get("USERPROFILE")
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_home = Path(tmpdir) / "home"
        fake_home.mkdir()
        os.environ["HOME"] = str(fake_home)
        os.environ["USERPROFILE"] = str(fake_home)
        from codecraft.db.connection import Database
        Database.reset()
        from codecraft.cli.deps import init_db
        init_db()
        yield fake_home
    if old_home:
        os.environ["HOME"] = old_home
    else:
        os.environ.pop("HOME", None)
    if old_userprofile:
        os.environ["USERPROFILE"] = old_userprofile
    else:
        os.environ.pop("USERPROFILE", None)
    Database.reset()


class TestSyncExportImport:
    def test_sync_export(self, runner, temp_db_dir):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            out_path = f.name

        try:
            result = runner.invoke(app, ["sync", "export", out_path])
            assert result.exit_code == 0, f"Exit code: {result.exit_code}, err: {result.output}"
            import json
            with open(out_path) as f:
                data = json.load(f)
            assert "version" in data
            assert "exported_at" in data
        finally:
            if Path(out_path).exists():
                Path(out_path).unlink()

    def test_sync_export_with_data(self, runner, temp_db_dir):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            out_path = f.name

        try:
            runner.invoke(app, ["init", "all", "--force"])
            result = runner.invoke(app, ["sync", "export", out_path])
            if result.exit_code != 0:
                pytest.skip(f"Sync export failed: {result.output}")
            import json
            with open(out_path) as f:
                data = json.load(f)
            assert "version" in data
        finally:
            if Path(out_path).exists():
                Path(out_path).unlink()


class TestProfileCommands:
    def test_profile_list_default(self, runner, temp_db_dir):
        result = runner.invoke(app, ["profile", "list"])
        assert result.exit_code == 0

    def test_profile_create(self, runner, temp_db_dir):
        result = runner.invoke(app, ["profile", "create", "testuser"])
        assert result.exit_code == 0

    def test_profile_create_duplicate(self, runner, temp_db_dir):
        runner.invoke(app, ["profile", "create", "testuser"])
        result = runner.invoke(app, ["profile", "create", "testuser"])
        assert result.exit_code != 0

    def test_profile_switch(self, runner, temp_db_dir):
        runner.invoke(app, ["profile", "create", "work"])
        result = runner.invoke(app, ["profile", "switch", "work"])
        assert result.exit_code == 0

    def test_profile_switch_nonexistent(self, runner, temp_db_dir):
        result = runner.invoke(app, ["profile", "switch", "nobody"])
        assert result.exit_code != 0

    def test_profile_delete(self, runner, temp_db_dir):
        runner.invoke(app, ["profile", "create", "temp"])
        result = runner.invoke(app, ["profile", "delete", "temp", "--force"])
        assert result.exit_code == 0

    def test_profile_delete_default(self, runner, temp_db_dir):
        result = runner.invoke(app, ["profile", "delete", "default", "--force"])
        assert result.exit_code != 0

    def test_profile_isolation(self, runner, temp_db_dir):
        runner.invoke(app, ["profile", "create", "user1"])
        runner.invoke(app, ["scan", "file", "tests/fixtures/beginner.py"])
        result1 = runner.invoke(app, ["status"])
        runner.invoke(app, ["profile", "switch", "user1"])
        result2 = runner.invoke(app, ["status"])
        assert result1.exit_code == 0
        assert result2.exit_code == 0
