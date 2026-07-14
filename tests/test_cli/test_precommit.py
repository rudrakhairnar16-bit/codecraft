from __future__ import annotations

import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from codecraft.cli.app import app


@pytest.fixture
def runner():
    return CliRunner()


class TestPrecommitInstall:
    def test_precommit_install_fresh(self, runner, tmp_path):
        old_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["precommit", "install"])
            assert result.exit_code == 0
            assert (tmp_path / ".pre-commit-config.yaml").exists()
            assert (tmp_path / ".hooks" / "codecraft-scan.py").exists()
        finally:
            os.chdir(old_cwd)

    def test_precommit_install_already_exists(self, runner, tmp_path):
        old_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            runner.invoke(app, ["precommit", "install"])
            result = runner.invoke(app, ["precommit", "install"])
            assert result.exit_code == 0
        finally:
            os.chdir(old_cwd)

    def test_precommit_install_force(self, runner, tmp_path):
        old_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            runner.invoke(app, ["precommit", "install"])
            result = runner.invoke(app, ["precommit", "install", "--force"])
            assert result.exit_code == 0
            assert (tmp_path / ".pre-commit-config.yaml").exists()
            assert (tmp_path / ".hooks" / "codecraft-scan.py").exists()
        finally:
            os.chdir(old_cwd)

    def test_precommit_show(self, runner):
        result = runner.invoke(app, ["precommit", "show"])
        assert result.exit_code == 0
