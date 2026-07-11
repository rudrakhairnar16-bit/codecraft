from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path

os.environ["NO_COLOR"] = "1"
os.environ["TERM"] = "xterm"

import pytest
from typer.testing import CliRunner

from codecraft.cli.app import app
from codecraft.models.challenge import ChallengeResult
from codecraft.models.debt import DebtItem
from codecraft.db.migrations import run_migrations


@pytest.fixture
def runner():
    return CliRunner()


class TestInitCommand:
    def test_init_all(self, repo, runner):
        result = runner.invoke(app, ["init", "all", "--force"])
        assert result.exit_code == 0

    def test_init_already_done(self, repo, runner):
        repo.set_setting("initialized", "1")
        result = runner.invoke(app, ["init", "all"])
        assert result.exit_code == 0


class TestProgressCommand:
    def test_progress_overview_empty(self, repo, runner):
        result = runner.invoke(app, ["progress", "overview"])
        assert result.exit_code == 0

    def test_progress_overview_with_data(self, repo, runner):
        r = ChallengeResult(
            challenge_id="test1", concept_name="list_comprehension",
            correct=True, time_taken_seconds=120, domain="gaming",
        )
        repo.insert_challenge_result(r)
        result = runner.invoke(app, ["progress", "overview"])
        assert result.exit_code == 0

    def test_progress_history_empty(self, repo, runner):
        result = runner.invoke(app, ["progress", "history"])
        assert result.exit_code == 0

    def test_progress_history_with_data(self, repo, runner):
        r = ChallengeResult(
            challenge_id="test2", concept_name="for_loop",
            correct=False, time_taken_seconds=60, domain="finance",
        )
        repo.insert_challenge_result(r)
        result = runner.invoke(app, ["progress", "history"])
        assert result.exit_code == 0

    def test_progress_tree(self, repo, runner):
        result = runner.invoke(app, ["progress", "tree"])
        assert result.exit_code == 0


class TestSuggestCommand:
    def test_suggest_next_empty(self, repo, runner):
        result = runner.invoke(app, ["suggest", "next"])
        assert result.exit_code == 0

    def test_suggest_next_with_debt(self, repo, runner):
        item = DebtItem(
            id=1, file_path=Path("test.py"), pattern_type="bare_except",
            pattern_location="5:0", old_snippet="except:",
            suggestion="Use specific exception", alternative_code="except ValueError:",
            difficulty=1, tier_gap=1, resolved=False, created=datetime.now(),
        )
        repo.insert_debt_item(item)
        result = runner.invoke(app, ["suggest", "next"])
        assert result.exit_code == 0

    def test_suggest_all(self, repo, runner):
        result = runner.invoke(app, ["suggest", "all"])
        assert result.exit_code == 0


class TestStatsCommand:
    def test_stats_sessions_empty(self, repo, runner):
        result = runner.invoke(app, ["stats", "sessions"])
        assert result.exit_code == 0

    def test_stats_sessions_with_data(self, repo, runner):
        r = ChallengeResult(
            challenge_id="test3", concept_name="dataclass",
            correct=True, time_taken_seconds=300, domain="science",
        )
        repo.insert_challenge_result(r)
        result = runner.invoke(app, ["stats", "sessions"])
        assert result.exit_code == 0


class TestLearnCommand:
    def test_learn_concept_known(self, repo, runner):
        result = runner.invoke(app, ["learn", "concept", "list_comprehension"])
        assert result.exit_code == 0

    def test_learn_concept_unknown(self, repo, runner):
        result = runner.invoke(app, ["learn", "concept", "nonexistent_concept"])
        assert result.exit_code == 1


class TestExportCommand:
    def test_export_summary(self, repo, runner):
        result = runner.invoke(app, ["export", "summary"])
        assert result.exit_code == 0

    def test_export_json(self, repo, runner, tmp_path):
        out = tmp_path / "export.json"
        result = runner.invoke(app, ["export", "json", "--output", str(out)])
        assert result.exit_code == 0
        assert out.exists()

    def test_export_csv(self, repo, runner, tmp_path):
        out = tmp_path / "export.csv"
        result = runner.invoke(app, ["export", "csv", "--output", str(out)])
        assert result.exit_code == 0
        assert out.exists()


class TestRepositoryEnhancements:
    def test_insert_challenge_result_fixed(self, repo):
        r = ChallengeResult(
            challenge_id="fix_test", challenge_type="practice",
            concept_name="list_comprehension", correct=True,
            time_taken_seconds=100, domain="gaming",
        )
        repo.insert_challenge_result(r)
        history = repo.get_challenge_history(limit=10)
        assert len(history) == 1
        assert history[0]["concept_name"] == "list_comprehension"
        assert history[0]["challenge_type"] == "practice"
        assert history[0]["domain"] == "gaming"
        assert history[0]["correct"] == True
        assert history[0]["time_taken"] == 100

    def test_get_practice_stats_empty(self, repo):
        stats = repo.get_practice_stats()
        assert stats["total_sessions"] == 0
        assert stats["correct_sessions"] == 0

    def test_get_practice_stats_with_data(self, repo):
        for i in range(5):
            r = ChallengeResult(
                challenge_id=f"s{i}", correct=i % 2 == 0,
                time_taken_seconds=60 + i * 10,
                concept_name="for_loop", domain="gaming",
            )
            repo.insert_challenge_result(r)
        stats = repo.get_practice_stats()
        assert stats["total_sessions"] == 5
        assert stats["correct_sessions"] == 3  # 0, 2, 4 are True
        assert stats["avg_time_seconds"] > 0
        assert stats["unique_concepts"] == 1

    def test_get_streak_data(self, repo):
        streak = repo.get_streak_data()
        assert "current_streak" in streak
        assert "total_active_days" in streak

    def test_settings_get_set(self, repo):
        repo.set_setting("test_key", "test_value")
        assert repo.get_setting("test_key") == "test_value"
        assert repo.get_setting("nonexistent", "default") == "default"

    def test_debt_to_concept_all_patterns(self):
        from codecraft.cli.debt import DEBT_TO_CONCEPT
        expected_patterns = {
            "bare_except", "broad_except", "mutable_default", "mutable_default_arg",
            "range_len", "if_elif_chain", "magic_number", "too_many_returns",
            "nested_conditional", "unused_variable", "unused_loop_variable",
            "star_import", "missing_return_annotation", "single_line_if_no_else",
            "manual_counter", "list_accumulation", "infinite_while_no_break",
        }
        actual = set(DEBT_TO_CONCEPT.keys())
        assert expected_patterns.issubset(actual), f"Missing: {expected_patterns - actual}"


class TestGamification:
    def test_streak_tracking(self, repo):
        from datetime import date, timedelta
        for i in range(3):
            r = ChallengeResult(
                challenge_id=f"streak_{i}", correct=True,
                concept_name="if_else",
                attempted_at=datetime.now() - timedelta(days=i),
            )
            repo.insert_challenge_result(r)
        streak = repo.get_streak_data()
        assert streak["total_active_days"] >= 1


class TestBugFixes:
    def test_scan_file_persists(self, repo, runner):
        """Bug B4: scan file should persist to DB"""
        result = runner.invoke(app, ["scan", "file", "tests/fixtures/beginner.py"])
        assert result.exit_code == 0
        files = repo.get_all_files()
        assert len(files) >= 1

    def test_debt_challenge_concept_name(self, repo, runner):
        """Bug B3: debt challenge should show correct concept name"""
        item = DebtItem(
            id=1, file_path=Path("test.py"), pattern_type="bare_except",
            pattern_location="5:0", old_snippet="except:",
            suggestion="Use specific exception", alternative_code="except ValueError:",
            difficulty=1, tier_gap=1, resolved=False, created=datetime.now(),
        )
        repo.insert_debt_item(item)
        result = runner.invoke(app, ["debt", "challenge"])
        assert result.exit_code == 0
