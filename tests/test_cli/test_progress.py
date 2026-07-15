from __future__ import annotations

import os
from datetime import datetime

os.environ["NO_COLOR"] = "1"
os.environ["TERM"] = "xterm"

import pytest
from typer.testing import CliRunner

from codecraft.cli.app import app
from codecraft.models.challenge import ChallengeResult


@pytest.fixture
def runner():
    return CliRunner()


class TestProgressCLI:
    def test_overview_empty(self, runner):
        result = runner.invoke(app, ["progress", "overview"])
        assert result.exit_code == 0

    def test_overview_with_data(self, repo, runner):
        repo.insert_challenge_result(ChallengeResult(
            challenge_id="t1", concept_name="for_loop",
            correct=True, time_taken_seconds=120, domain="gaming",
        ))
        result = runner.invoke(app, ["progress", "overview"])
        assert result.exit_code == 0

    def test_history_empty(self, runner):
        result = runner.invoke(app, ["progress", "history"])
        assert result.exit_code == 0

    def test_history_with_data(self, repo, runner):
        repo.insert_challenge_result(ChallengeResult(
            challenge_id="t2", concept_name="if_else",
            correct=False, time_taken_seconds=60, domain="gaming",
        ))
        result = runner.invoke(app, ["progress", "history"])
        assert result.exit_code == 0

    def test_history_limit(self, repo, runner):
        for i in range(5):
            repo.insert_challenge_result(ChallengeResult(
                challenge_id=f"t{i}", concept_name="for_loop",
                correct=True, time_taken_seconds=30, domain="gaming",
            ))
        result = runner.invoke(app, ["progress", "history", "--limit", "3"])
        assert result.exit_code == 0
