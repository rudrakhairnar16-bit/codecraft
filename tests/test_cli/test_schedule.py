from __future__ import annotations

import os
from datetime import datetime, timedelta

os.environ["NO_COLOR"] = "1"
os.environ["TERM"] = "xterm"

import pytest
from typer.testing import CliRunner

from codecraft.cli.app import app
from codecraft.models.review import SpacedRepetitionCard


@pytest.fixture
def runner():
    return CliRunner()


class TestScheduleCLI:
    def test_queue(self, runner):
        result = runner.invoke(app, ["schedule", "queue"])
        assert result.exit_code == 0

    def test_due(self, runner):
        result = runner.invoke(app, ["schedule", "due"])
        assert result.exit_code == 0

    def test_decay_default(self, runner):
        result = runner.invoke(app, ["schedule", "decay"])
        assert result.exit_code == 0

    def test_decay_custom(self, runner):
        result = runner.invoke(app, ["schedule", "decay", "--min", "0.5"])
        assert result.exit_code == 0

    def test_review_with_card(self, repo, runner):
        repo.conn.execute("""
            INSERT INTO spaced_repetition (concept_name, strength, interval_days, next_review)
            VALUES ('for_loop', 0.5, 1, ?)
        """, [datetime.now() - timedelta(days=1)])
        result = runner.invoke(app, ["schedule", "review", "for_loop", "--correct"])
        assert result.exit_code == 0

    def test_review_incorrect(self, repo, runner):
        repo.conn.execute("""
            INSERT INTO spaced_repetition (concept_name, strength, interval_days, next_review)
            VALUES ('if_else', 0.5, 1, ?)
        """, [datetime.now() - timedelta(days=1)])
        result = runner.invoke(app, ["schedule", "review", "if_else", "--incorrect"])
        assert result.exit_code == 0

    def test_review_unknown_concept(self, runner):
        result = runner.invoke(app, ["schedule", "review", "zzz_nonexistent", "--correct"])
        assert result.exit_code != 0
