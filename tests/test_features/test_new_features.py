from __future__ import annotations

import json
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
from codecraft.models.file import FileConcept, FileRecord
from codecraft.db.migrations import run_migrations
from codecraft.models.review import SpacedRepetitionCard


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


class TestScanCommand:
    def test_scan_dir_dry_run(self, repo, runner, tmp_path):
        d = tmp_path / "project"
        d.mkdir()
        (d / "test.py").write_text("x = 1")
        result = runner.invoke(app, ["scan", "dir", str(d), "--dry-run"])
        assert result.exit_code == 0

    def test_scan_dir_no_supported(self, repo, runner, tmp_path):
        d = tmp_path / "project"
        d.mkdir()
        (d / "readme.md").write_text("# readme")
        result = runner.invoke(app, ["scan", "dir", str(d)])
        assert result.exit_code == 0

    def test_scan_dir_json(self, repo, runner, tmp_path):
        d = tmp_path / "project"
        d.mkdir()
        (d / "test.py").write_text("x = 1")
        result = runner.invoke(app, ["scan", "dir", str(d), "--json"])
        assert result.exit_code == 0

    def test_scan_dir_with_persist(self, db, runner, tmp_path):
        d = tmp_path / "project"
        d.mkdir()
        (d / "test.py").write_text("x = 1")
        result = runner.invoke(app, ["scan", "dir", str(d)])
        assert result.exit_code == 0

    def test_scan_file(self, repo, runner, fixtures_dir):
        result = runner.invoke(app, ["scan", "file", str(fixtures_dir / "beginner.py")])
        assert result.exit_code == 0

    def test_scan_file_syntax_error(self, repo, runner, tmp_path):
        f = tmp_path / "bad.py"
        f.write_text("def broken(:")
        result = runner.invoke(app, ["scan", "file", str(f)])
        assert result.exit_code != 0

    def test_scan_file_not_found(self, repo, runner, tmp_path):
        result = runner.invoke(app, ["scan", "file", str(tmp_path / "nonexistent.py")])
        assert result.exit_code != 0

    def test_scan_file_unsupported_type(self, runner, tmp_path):
        f = tmp_path / "readme.md"
        f.write_text("# hello")
        result = runner.invoke(app, ["scan", "file", str(f)])
        assert result.exit_code != 0

    def test_scan_dir_skip_hidden(self, repo, runner, tmp_path):
        d = tmp_path / "project"
        d.mkdir()
        hidden = d / ".hidden"
        hidden.mkdir()
        (hidden / "test.py").write_text("x = 1")
        result = runner.invoke(app, ["scan", "dir", str(d), "--dry-run"])
        assert result.exit_code == 0




class TestPracticeCommand:
    def test_practice_list(self, repo, runner):
        result = runner.invoke(app, ["practice", "list"])
        assert result.exit_code == 0

    def test_practice_list_search(self, repo, runner):
        result = runner.invoke(app, ["practice", "list", "loop"])
        assert result.exit_code == 0

    def test_practice_list_no_match(self, repo, runner):
        result = runner.invoke(app, ["practice", "list", "zzz_nonexistent"])
        assert result.exit_code == 0

    def test_practice_path(self, repo, runner):
        result = runner.invoke(app, ["practice", "path"])
        assert result.exit_code == 0

    def test_practice_path_with_arg(self, repo, runner):
        result = runner.invoke(app, ["practice", "path", "beginner"])
        assert result.exit_code == 0

    def test_practice_path_create(self, repo, runner):
        result = runner.invoke(app, ["practice", "path-create", "mypath", "--concepts", "for_loop,if_else"])
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

    def test_progress_tree_with_data(self, repo, runner):
        from codecraft.models.review import SpacedRepetitionCard
        for name in ["for_loop", "if_else", "list_comprehension", "dataclass"]:
            repo.upsert_card(SpacedRepetitionCard(
                concept_name=name, ease_factor=2.5, interval_days=1, strength=0.9,
            ))
        result = runner.invoke(app, ["progress", "tree"])
        assert result.exit_code == 0

    def test_progress_tree_with_decaying(self, repo, runner):
        from codecraft.models.review import SpacedRepetitionCard
        repo.upsert_card(SpacedRepetitionCard(
            concept_name="for_loop", ease_factor=1.5, interval_days=10, strength=0.3,
        ))
        result = runner.invoke(app, ["progress", "tree"])
        assert result.exit_code == 0


class TestScheduleCommand:
    def test_schedule_queue(self, repo, runner):
        result = runner.invoke(app, ["schedule", "queue"])
        assert result.exit_code == 0

    def test_schedule_queue_with_data(self, repo, runner):
        repo.upsert_card(SpacedRepetitionCard(
            concept_name="for_loop", ease_factor=2.5, interval_days=1, strength=0.3,
        ))
        result = runner.invoke(app, ["schedule", "queue"])
        assert result.exit_code == 0

    def test_schedule_due(self, repo, runner):
        result = runner.invoke(app, ["schedule", "due"])
        assert result.exit_code == 0

    def test_schedule_due_with_data(self, repo, runner):
        repo.upsert_card(SpacedRepetitionCard(
            concept_name="list_comprehension", ease_factor=2.5, interval_days=0, strength=0.2,
        ))
        result = runner.invoke(app, ["schedule", "due"])
        assert result.exit_code == 0

    def test_schedule_decay(self, repo, runner):
        result = runner.invoke(app, ["schedule", "decay"])
        assert result.exit_code == 0

    def test_schedule_decay_with_data(self, repo, runner):
        repo.upsert_card(SpacedRepetitionCard(
            concept_name="if_else", ease_factor=2.5, interval_days=5, strength=0.5,
        ))
        result = runner.invoke(app, ["schedule", "decay"])
        assert result.exit_code == 0


class TestSuggestCommand:
    def test_suggest_next_empty(self, repo, runner):
        result = runner.invoke(app, ["suggest", "next"])
        assert result.exit_code == 0

    def test_suggest_next_with_data(self, repo, runner):
        repo.upsert_file(FileRecord(path=Path("test.py"), hash="abc", size=100, lines=10))
        repo.upsert_file_concepts(Path("test.py"), {
            "for_loop": FileConcept(concept_name="for_loop", occurrences=3),
        })
        item = DebtItem(
            id=1, file_path=Path("test.py"), pattern_type="bare_except",
            pattern_location="5:0", old_snippet="except:",
            suggestion="Use specific exception", alternative_code="except ValueError:",
            difficulty=1, tier_gap=1, resolved=False, created=datetime.now(),
        )
        repo.insert_debt_item(item)
        repo.upsert_card(SpacedRepetitionCard(
            concept_name="for_loop", ease_factor=2.5, interval_days=5, strength=0.3,
        ))
        result = runner.invoke(app, ["suggest", "next"])
        assert result.exit_code == 0

    def test_suggest_all(self, repo, runner):
        result = runner.invoke(app, ["suggest", "all"])
        assert result.exit_code == 0

    def test_suggest_all_with_data(self, repo, runner):
        repo.upsert_file(FileRecord(path=Path("test.py"), hash="abc", size=100, lines=10))
        repo.upsert_file_concepts(Path("test.py"), {
            "for_loop": FileConcept(concept_name="for_loop", occurrences=3),
        })
        result = runner.invoke(app, ["suggest", "all"])
        assert result.exit_code == 0


class TestSuggestWithAllConcepts:
    def test_suggest_next_all_concepts_known(self, db, runner):
        from codecraft.db.repository import Repository
        from codecraft.models.concept import ConceptTaxonomy
        from codecraft.models.file import FileConcept
        conn = db.connect()
        repo = Repository(conn)
        concepts = {c.name: FileConcept(concept_name=c.name, occurrences=1) for c in ConceptTaxonomy.all()}
        repo.upsert_file_concepts(Path("test.py"), concepts)
        result = runner.invoke(app, ["suggest", "next"])
        assert result.exit_code == 0

    def test_suggest_all_all_concepts_known(self, db, runner):
        from codecraft.db.repository import Repository
        from codecraft.models.concept import ConceptTaxonomy
        from codecraft.models.file import FileConcept
        conn = db.connect()
        repo = Repository(conn)
        concepts = {c.name: FileConcept(concept_name=c.name, occurrences=1) for c in ConceptTaxonomy.all()}
        repo.upsert_file_concepts(Path("test.py"), concepts)
        result = runner.invoke(app, ["suggest", "all"])
        assert result.exit_code == 0


class TestSuggestWithDataViaSingleton:
    def test_suggest_next_with_concepts(self, db, runner):
        from codecraft.db.repository import Repository
        from codecraft.models.file import FileConcept
        from datetime import datetime
        from codecraft.models.debt import DebtItem
        conn = db.connect()
        repo = Repository(conn)
        repo.upsert_file(FileRecord(path=Path("test.py"), hash="abc", size=100, lines=10))
        repo.upsert_file_concepts(Path("test.py"), {
            "for_loop": FileConcept(concept_name="for_loop", occurrences=3),
            "if_else": FileConcept(concept_name="if_else", occurrences=2),
        })
        item = DebtItem(
            id=1, file_path=Path("test.py"), pattern_type="bare_except",
            pattern_location="5:0", old_snippet="except:",
            suggestion="Use specific exception", alternative_code="except ValueError:",
            difficulty=1, tier_gap=1, resolved=False, created=datetime.now(),
        )
        repo.insert_debt_item(item)
        from codecraft.models.review import SpacedRepetitionCard
        repo.upsert_card(SpacedRepetitionCard(
            concept_name="for_loop", ease_factor=2.5, interval_days=5, strength=0.3,
        ))
        result = runner.invoke(app, ["suggest", "next"])
        assert result.exit_code == 0

    def test_suggest_all_with_concepts(self, db, runner):
        from codecraft.db.repository import Repository
        from codecraft.models.file import FileConcept
        from datetime import datetime
        from codecraft.models.debt import DebtItem
        conn = db.connect()
        repo = Repository(conn)
        repo.upsert_file(FileRecord(path=Path("test.py"), hash="abc", size=100, lines=10))
        repo.upsert_file_concepts(Path("test.py"), {
            "for_loop": FileConcept(concept_name="for_loop", occurrences=3),
            "if_else": FileConcept(concept_name="if_else", occurrences=2),
        })
        item = DebtItem(
            id=1, file_path=Path("test.py"), pattern_type="bare_except",
            pattern_location="5:0", old_snippet="except:",
            suggestion="Use specific exception", alternative_code="except ValueError:",
            difficulty=1, tier_gap=1, resolved=False, created=datetime.now(),
        )
        repo.insert_debt_item(item)
        result = runner.invoke(app, ["suggest", "all"])
        assert result.exit_code == 0


class TestDebtCommand:
    def test_debt_report(self, repo, runner):
        result = runner.invoke(app, ["debt", "report"])
        assert result.exit_code == 0

    def test_debt_report_with_data(self, repo, runner):
        item = DebtItem(
            id=1, file_path=Path("test.py"), pattern_type="bare_except",
            pattern_location="5:0", old_snippet="except:",
            suggestion="Use specific exception", alternative_code="except ValueError:",
            difficulty=1, tier_gap=1, resolved=False, created=datetime.now(),
        )
        repo.insert_debt_item(item)
        result = runner.invoke(app, ["debt", "report"])
        assert result.exit_code == 0

    def test_debt_list(self, repo, runner):
        result = runner.invoke(app, ["debt", "list"])
        assert result.exit_code == 0

    def test_debt_list_with_data(self, repo, runner):
        item = DebtItem(
            id=2, file_path=Path("test.py"), pattern_type="bare_except",
            pattern_location="5:0", old_snippet="except:",
            suggestion="Use specific exception", alternative_code="except ValueError:",
            difficulty=1, tier_gap=1, resolved=False, created=datetime.now(),
        )
        repo.insert_debt_item(item)
        result = runner.invoke(app, ["debt", "list"])
        assert result.exit_code == 0

    def test_debt_list_filter(self, repo, runner):
        item = DebtItem(
            id=3, file_path=Path("test.py"), pattern_type="bare_except",
            pattern_location="5:0", old_snippet="except:",
            suggestion="Use specific exception", alternative_code="except ValueError:",
            difficulty=1, tier_gap=1, resolved=False, created=datetime.now(),
        )
        repo.insert_debt_item(item)
        result = runner.invoke(app, ["debt", "list", "--type", "bare_except"])
        assert result.exit_code == 0

    def test_debt_challenge_empty(self, repo, runner):
        result = runner.invoke(app, ["debt", "challenge"])
        assert result.exit_code == 0

    def test_debt_challenge_with_data(self, repo, runner):
        item = DebtItem(
            id=4, file_path=Path("test.py"), pattern_type="bare_except",
            pattern_location="5:0", old_snippet="except:",
            suggestion="Use specific exception", alternative_code="except ValueError:",
            difficulty=1, tier_gap=1, resolved=False, created=datetime.now(),
        )
        repo.insert_debt_item(item)
        result = runner.invoke(app, ["debt", "challenge"])
        assert result.exit_code == 0


class TestDashboardCommand:
    def test_dashboard_summary(self, repo, runner):
        result = runner.invoke(app, ["dashboard", "summary"])
        assert result.exit_code == 0

    def test_dashboard_summary_with_data(self, repo, runner):
        repo.set_setting("initialized", "1")
        repo.upsert_card(SpacedRepetitionCard(
            concept_name="for_loop", ease_factor=2.5, interval_days=1, strength=0.9,
        ))
        result = runner.invoke(app, ["dashboard", "summary"])
        assert result.exit_code == 0

    def test_dashboard_heatmap(self, repo, runner):
        result = runner.invoke(app, ["dashboard", "heatmap"])
        assert result.exit_code == 0

    def test_dashboard_heatmap_with_tier(self, repo, runner):
        repo.upsert_card(SpacedRepetitionCard(
            concept_name="for_loop", ease_factor=2.5, interval_days=1, strength=0.9,
        ))
        result = runner.invoke(app, ["dashboard", "heatmap", "--tier", "1"])
        assert result.exit_code == 0

    def test_dashboard_trends(self, repo, runner):
        result = runner.invoke(app, ["dashboard", "trends"])
        assert result.exit_code == 0

    def test_dashboard_trends_with_data(self, repo, runner):
        repo.conn.execute(
            "INSERT INTO file_concepts (file_path, concept_name, occurrences) VALUES (?, ?, ?)",
            ["test.py", "for_loop", 3],
        )
        result = runner.invoke(app, ["dashboard", "trends"])
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


class TestProfileCommand:
    def test_profile_list(self, repo, runner):
        result = runner.invoke(app, ["profile", "list"])
        assert result.exit_code == 0

    def test_profile_list(self, repo, runner):
        result = runner.invoke(app, ["profile", "list"])
        assert result.exit_code == 0

    def test_profile_create_and_switch(self, repo, runner):
        import os, json
        from pathlib import Path
        pf = Path(os.path.expanduser("~/.codecraft")) / "profiles.json"
        if pf.exists():
            data = json.loads(pf.read_text())
            data["profiles"].pop("testprofile", None)
            pf.write_text(json.dumps(data))
        result = runner.invoke(app, ["profile", "create", "testprofile"])
        assert result.exit_code == 0
        result = runner.invoke(app, ["profile", "switch", "testprofile"])
        assert result.exit_code == 0

    def test_profile_switch_nonexistent(self, repo, runner):
        result = runner.invoke(app, ["profile", "switch", "nonexistent_profile_xyz"])
        assert result.exit_code != 0


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
        assert stats["correct_sessions"] == 3
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


class TestProgressWithDataViaSingleton:
    """Uses db fixture (Database singleton) so CLI commands see the data."""

    def test_progress_overview_with_stats(self, db, runner):
        from codecraft.db.repository import Repository
        conn = db.connect()
        repo = Repository(conn)
        for i in range(3):
            r = ChallengeResult(
                challenge_id=f"p{i}", concept_name="for_loop",
                correct=i % 2 == 0, time_taken_seconds=60 + i * 10, domain="gaming",
            )
            repo.insert_challenge_result(r)
        result = runner.invoke(app, ["progress", "overview"])
        assert result.exit_code == 0

    def test_progress_history_with_real_data(self, db, runner):
        from codecraft.db.repository import Repository
        conn = db.connect()
        repo = Repository(conn)
        r = ChallengeResult(
            challenge_id="hist1", concept_name="list_comprehension",
            correct=True, time_taken_seconds=120, domain="gaming",
        )
        repo.insert_challenge_result(r)
        result = runner.invoke(app, ["progress", "history", "--limit", "5"])
        assert result.exit_code == 0

    def test_progress_tree_with_full_data(self, db, runner):
        from codecraft.db.repository import Repository
        from codecraft.models.review import SpacedRepetitionCard
        from codecraft.models.file import FileConcept
        conn = db.connect()
        repo = Repository(conn)
        for name in ["for_loop", "if_else", "list_comprehension"]:
            repo.upsert_card(SpacedRepetitionCard(
                concept_name=name, ease_factor=2.5, interval_days=1, strength=0.9,
            ))
        repo.upsert_file_concepts(Path("test.py"), {
            name: FileConcept(concept_name=name, occurrences=1)
            for name in ["for_loop", "if_else", "list_comprehension"]
        })
        result = runner.invoke(app, ["progress", "tree"])
        assert result.exit_code == 0

    def test_progress_tree_with_decaying_concept(self, db, runner):
        from codecraft.db.repository import Repository
        from codecraft.models.review import SpacedRepetitionCard
        from codecraft.models.file import FileConcept
        conn = db.connect()
        repo = Repository(conn)
        repo.upsert_card(SpacedRepetitionCard(
            concept_name="for_loop", ease_factor=1.5, interval_days=10, strength=0.3,
        ))
        repo.upsert_file_concepts(Path("test.py"), {
            "for_loop": FileConcept(concept_name="for_loop", occurrences=1),
        })
        result = runner.invoke(app, ["progress", "tree"])
        assert result.exit_code == 0

    def test_progress_tree_with_untracked_concept(self, db, runner):
        from codecraft.db.repository import Repository
        from codecraft.models.review import SpacedRepetitionCard
        conn = db.connect()
        repo = Repository(conn)
        repo.upsert_card(SpacedRepetitionCard(
            concept_name="for_loop", ease_factor=2.5, interval_days=1, strength=0.9,
        ))
        result = runner.invoke(app, ["progress", "tree"])
        assert result.exit_code == 0

    def test_progress_tree_with_stable_concept(self, db, runner):
        from codecraft.db.repository import Repository
        from codecraft.models.review import SpacedRepetitionCard
        from codecraft.models.file import FileConcept
        conn = db.connect()
        repo = Repository(conn)
        repo.upsert_card(SpacedRepetitionCard(
            concept_name="for_loop", ease_factor=2.5, interval_days=1, strength=0.7,
        ))
        repo.upsert_file_concepts(Path("test.py"), {
            "for_loop": FileConcept(concept_name="for_loop", occurrences=1),
        })
        result = runner.invoke(app, ["progress", "tree"])
        assert result.exit_code == 0

    def test_progress_tree_with_untracked_card(self, db, runner):
        from codecraft.db.repository import Repository
        from codecraft.models.file import FileConcept
        conn = db.connect()
        repo = Repository(conn)
        repo.upsert_file_concepts(Path("test.py"), {
            "for_loop": FileConcept(concept_name="for_loop", occurrences=1),
        })
        result = runner.invoke(app, ["progress", "tree"])
        assert result.exit_code == 0


class TestDebtWithDataViaSingleton:
    def test_debt_report_with_data(self, db, runner):
        from codecraft.db.repository import Repository
        conn = db.connect()
        repo = Repository(conn)
        item = DebtItem(
            id=1, file_path=Path("test.py"), pattern_type="bare_except",
            pattern_location="5:0", old_snippet="except:",
            suggestion="Use specific exception", alternative_code="except ValueError:",
            difficulty=1, tier_gap=1, resolved=False, created=datetime.now(),
        )
        repo.insert_debt_item(item)
        result = runner.invoke(app, ["debt", "report"])
        assert result.exit_code == 0

    def test_debt_list_with_data(self, db, runner):
        from codecraft.db.repository import Repository
        conn = db.connect()
        repo = Repository(conn)
        item = DebtItem(
            id=1, file_path=Path("test.py"), pattern_type="bare_except",
            pattern_location="5:0", old_snippet="except:",
            suggestion="Use specific exception", alternative_code="except ValueError:",
            difficulty=1, tier_gap=1, resolved=False, created=datetime.now(),
        )
        repo.insert_debt_item(item)
        result = runner.invoke(app, ["debt", "list"])
        assert result.exit_code == 0

    def test_debt_challenge_with_data(self, db, runner):
        from codecraft.db.repository import Repository
        conn = db.connect()
        repo = Repository(conn)
        item = DebtItem(
            id=1, file_path=Path("test.py"), pattern_type="bare_except",
            pattern_location="5:0", old_snippet="except:",
            suggestion="Use specific exception", alternative_code="except ValueError:",
            difficulty=1, tier_gap=1, resolved=False, created=datetime.now(),
        )
        repo.insert_debt_item(item)
        result = runner.invoke(app, ["debt", "challenge"])
        assert result.exit_code == 0


class TestDashboardWithDataViaSingleton:
    def test_dashboard_summary_with_debt(self, db, runner):
        from codecraft.db.repository import Repository
        conn = db.connect()
        repo = Repository(conn)
        item = DebtItem(
            id=1, file_path=Path("test.py"), pattern_type="bare_except",
            pattern_location="5:0", old_snippet="except:",
            suggestion="Use specific exception", alternative_code="except ValueError:",
            difficulty=1, tier_gap=1, resolved=False, created=datetime.now(),
        )
        repo.insert_debt_item(item)
        result = runner.invoke(app, ["dashboard", "summary"])
        assert result.exit_code == 0

    def test_dashboard_summary_with_full_data(self, db, runner):
        from codecraft.db.repository import Repository
        from codecraft.models.review import SpacedRepetitionCard
        conn = db.connect()
        repo = Repository(conn)
        repo.upsert_file_concepts(Path("test.py"), {
            "for_loop": FileConcept(concept_name="for_loop", occurrences=3),
        })
        repo.upsert_card(SpacedRepetitionCard(
            concept_name="for_loop", ease_factor=2.5, interval_days=1, strength=0.9,
        ))
        result = runner.invoke(app, ["dashboard", "summary"])
        assert result.exit_code == 0

    def test_dashboard_heatmap_with_data(self, db, runner):
        from codecraft.db.repository import Repository
        from codecraft.models.review import SpacedRepetitionCard
        from codecraft.models.file import FileConcept
        conn = db.connect()
        repo = Repository(conn)
        repo.upsert_card(SpacedRepetitionCard(
            concept_name="for_loop", ease_factor=2.5, interval_days=1, strength=0.9,
        ))
        repo.upsert_file_concepts(Path("test.py"), {
            "for_loop": FileConcept(concept_name="for_loop", occurrences=3),
        })
        result = runner.invoke(app, ["dashboard", "heatmap"])
        assert result.exit_code == 0

    def test_dashboard_heatmap_with_tier(self, db, runner):
        from codecraft.db.repository import Repository
        from codecraft.models.review import SpacedRepetitionCard
        from codecraft.models.file import FileConcept
        conn = db.connect()
        repo = Repository(conn)
        repo.upsert_card(SpacedRepetitionCard(
            concept_name="for_loop", ease_factor=2.5, interval_days=1, strength=0.9,
        ))
        repo.upsert_file_concepts(Path("test.py"), {
            "for_loop": FileConcept(concept_name="for_loop", occurrences=3),
        })
        result = runner.invoke(app, ["dashboard", "heatmap", "--tier", "1"])
        assert result.exit_code == 0

    def test_dashboard_trends_with_data(self, db, runner):
        from codecraft.db.repository import Repository
        from codecraft.models.file import FileConcept
        conn = db.connect()
        repo = Repository(conn)
        repo.upsert_file_concepts(Path("test.py"), {
            "for_loop": FileConcept(concept_name="for_loop", occurrences=3),
        })
        result = runner.invoke(app, ["dashboard", "trends"])
        assert result.exit_code == 0

    def test_dashboard_trends_with_gaps(self, db, runner):
        from codecraft.db.repository import Repository
        from codecraft.models.file import FileConcept
        conn = db.connect()
        repo = Repository(conn)
        for c in ["for_loop", "if_else", "list_comprehension", "dataclass"]:
            repo.upsert_file_concepts(Path("test.py"), {
                c: FileConcept(concept_name=c, occurrences=3),
            })
        result = runner.invoke(app, ["dashboard", "trends"])
        assert result.exit_code == 0

    def test_dashboard_trends_with_unknown_concept(self, db, runner):
        from codecraft.db.repository import Repository
        from codecraft.models.file import FileConcept
        conn = db.connect()
        repo = Repository(conn)
        repo.upsert_file_concepts(Path("test.py"), {
            "completely_unknown_concept_xyz": FileConcept(concept_name="completely_unknown_concept_xyz", occurrences=1),
        })
        result = runner.invoke(app, ["dashboard", "trends"])
        assert result.exit_code == 0


class TestRemixCommand:
    def test_remix_gaps(self, repo, runner):
        result = runner.invoke(app, ["remix", "gaps"])
        assert result.exit_code == 0

    def test_remix_gaps_with_data(self, repo, runner):
        from codecraft.models.file import FileRecord, FileConcept
        repo.upsert_file(FileRecord(path=Path("test.py"), hash="abc", size=100, lines=10))
        repo.upsert_file_concepts(Path("test.py"), {
            "for_loop": FileConcept(concept_name="for_loop", occurrences=1),
        })
        result = runner.invoke(app, ["remix", "gaps"])
        assert result.exit_code == 0

    def test_remix_gaps_filter(self, repo, runner):
        from codecraft.models.file import FileRecord, FileConcept
        repo.upsert_file(FileRecord(path=Path("test.py"), hash="abc", size=100, lines=10))
        repo.upsert_file_concepts(Path("test.py"), {
            "for_loop": FileConcept(concept_name="for_loop", occurrences=1),
        })
        result = runner.invoke(app, ["remix", "gaps", "--filter", "for"])
        assert result.exit_code == 0

    def test_remix_domains(self, repo, runner):
        result = runner.invoke(app, ["remix", "domains"])
        assert result.exit_code == 0

    def test_remix_generate_unknown(self, repo, runner):
        result = runner.invoke(app, ["remix", "generate", "nonexistent_xyz"])
        assert result.exit_code == 0

    def test_remix_generate(self, db, runner):
        from codecraft.db.repository import Repository
        from codecraft.models.file import FileConcept
        conn = db.connect()
        repo = Repository(conn)
        repo.upsert_file_concepts(Path("test.py"), {
            "for_loop": FileConcept(concept_name="for_loop", occurrences=1),
        })
        result = runner.invoke(app, ["remix", "generate", "for_loop", "--domain", "gaming"])
        assert result.exit_code == 0

    def test_remix_review_unknown(self, repo, runner):
        result = runner.invoke(app, ["remix", "review", "nonexistent_xyz"])
        assert result.exit_code == 0

    def test_remix_review(self, db, runner):
        from codecraft.db.repository import Repository
        from codecraft.models.file import FileConcept
        conn = db.connect()
        repo = Repository(conn)
        repo.upsert_file_concepts(Path("test.py"), {
            "for_loop": FileConcept(concept_name="for_loop", occurrences=1),
        })
        result = runner.invoke(app, ["remix", "review", "for_loop"])
        assert result.exit_code == 0


class TestRemixWithDataViaSingleton:
    def test_remix_domains_with_data(self, db, runner):
        from codecraft.db.repository import Repository
        conn = db.connect()
        repo = Repository(conn)
        concepts = {
            "for_loop": FileConcept(concept_name="for_loop", occurrences=1),
            "list_comprehension": FileConcept(concept_name="list_comprehension", occurrences=2),
        }
        repo.upsert_file_concepts(Path("test.py"), concepts)
        result = runner.invoke(app, ["remix", "domains"])
        assert result.exit_code == 0

    def test_remix_gaps_with_data(self, db, runner):
        from codecraft.db.repository import Repository
        conn = db.connect()
        repo = Repository(conn)
        concepts = {
            "for_loop": FileConcept(concept_name="for_loop", occurrences=1),
        }
        repo.upsert_file_concepts(Path("test.py"), concepts)
        result = runner.invoke(app, ["remix", "gaps"])
        assert result.exit_code == 0


class TestVacuumCommand:
    def test_vacuum_run(self, repo, runner):
        result = runner.invoke(app, ["vacuum", "run"])
        assert result.exit_code == 0

    def test_vacuum_stats(self, repo, runner):
        result = runner.invoke(app, ["vacuum", "stats"])
        assert result.exit_code == 0


class TestSyncCommand:
    def test_sync_export(self, repo, runner, tmp_path):
        out = tmp_path / "backup.json"
        result = runner.invoke(app, ["sync", "export", str(out)])
        assert result.exit_code == 0
        assert out.exists()

    def test_sync_import(self, repo, runner, tmp_path):
        out = tmp_path / "backup.json"
        runner.invoke(app, ["sync", "export", str(out)])
        result = runner.invoke(app, ["sync", "import", str(out)])
        assert result.exit_code == 0

    def test_sync_import_missing(self, repo, runner):
        result = runner.invoke(app, ["sync", "import", "nonexistent.json"])
        assert result.exit_code != 0


class TestPrecommitCommand:
    def test_precommit_show(self, repo, runner):
        result = runner.invoke(app, ["precommit", "show"])
        assert result.exit_code == 0

    def test_precommit_install(self, repo, runner, tmp_path):
        result = runner.invoke(app, ["precommit", "install"])
        assert result.exit_code == 0


class TestStartWizard:
    def test_start_wizard(self, repo, runner):
        result = runner.invoke(app, ["start"])
        assert result.exit_code == 0

    def test_start_wizard_with_data(self, repo, runner):
        from codecraft.models.file import FileConcept
        repo.conn.execute(
            "INSERT INTO file_concepts (file_path, concept_name, occurrences) VALUES (?, ?, ?)",
            ["test.py", "for_loop", 3],
        )
        result = runner.invoke(app, ["start"])
        assert result.exit_code == 0


class TestStartWizardWithDataViaSingleton:
    def test_start_wizard_with_known_concepts(self, db, runner):
        from codecraft.db.repository import Repository
        from codecraft.models.file import FileConcept
        conn = db.connect()
        repo = Repository(conn)
        repo.upsert_file_concepts(Path("test.py"), {
            "for_loop": FileConcept(concept_name="for_loop", occurrences=3),
        })
        result = runner.invoke(app, ["start"])
        assert result.exit_code == 0


class TestInitReset:
    def test_init_reset(self, repo, runner):
        result = runner.invoke(app, ["init", "reset"], input="y\n")
        assert result.exit_code == 0

    def test_init_reset_cancel(self, repo, runner):
        result = runner.invoke(app, ["init", "reset"], input="n\n")
        assert result.exit_code == 0


class TestLearnCommandExtended:
    def test_learn_concept_partial_match(self, repo, runner):
        result = runner.invoke(app, ["learn", "concept", "list"])
        assert result.exit_code == 0

    def test_learn_concept_already_detected(self, db, runner):
        from codecraft.db.repository import Repository
        from codecraft.models.file import FileConcept
        from codecraft.models.review import SpacedRepetitionCard
        conn = db.connect()
        repo = Repository(conn)
        repo.upsert_file_concepts(Path("test.py"), {
            "list_comprehension": FileConcept(concept_name="list_comprehension", occurrences=3),
        })
        repo.upsert_card(SpacedRepetitionCard(
            concept_name="list_comprehension", ease_factor=2.5, interval_days=1, strength=0.9,
        ))
        result = runner.invoke(app, ["learn", "concept", "list_comprehension"])
        assert result.exit_code == 0


class TestScanCommandExtended:
    def test_scan_dir_with_js_file(self, repo, runner, tmp_path):
        d = tmp_path / "project"
        d.mkdir()
        (d / "test.js").write_text("const x = 1;")
        result = runner.invoke(app, ["scan", "dir", str(d), "--dry-run"])
        assert result.exit_code == 0

    def test_scan_dir_watch_no_files(self, repo, runner, tmp_path):
        from unittest.mock import patch
        d = tmp_path / "empty"
        d.mkdir()
        with patch("codecraft.cli.scan._watch_directory", return_value=None):
            result = runner.invoke(app, ["scan", "dir", str(d), "--watch"])
        assert result.exit_code == 0

    def test_scan_dir_with_results_and_json(self, repo, runner, tmp_path):
        d = tmp_path / "project"
        d.mkdir()
        (d / "test.py").write_text("x = 1")
        result = runner.invoke(app, ["scan", "dir", str(d), "--json"])
        assert result.exit_code == 0


class TestStatsSessionsWithHistory:
    def test_stats_sessions_with_history_via_db(self, db, runner):
        from codecraft.db.repository import Repository
        from codecraft.models.challenge import ChallengeResult
        conn = db.connect()
        repo = Repository(conn)
        for i in range(3):
            r = ChallengeResult(
                challenge_id=f"h{i}", concept_name="list_comprehension",
                correct=True, time_taken_seconds=120 + i * 10, domain="gaming",
            )
            repo.insert_challenge_result(r)
        result = runner.invoke(app, ["stats", "sessions"])
        assert result.exit_code == 0

    def test_stats_sessions_with_mixed_results(self, db, runner):
        from codecraft.db.repository import Repository
        from codecraft.models.challenge import ChallengeResult
        conn = db.connect()
        repo = Repository(conn)
        for i in range(3):
            r = ChallengeResult(
                challenge_id=f"m{i}", concept_name="for_loop",
                correct=i % 2 == 0, time_taken_seconds=60 + i * 30, domain="gaming",
            )
            repo.insert_challenge_result(r)
        result = runner.invoke(app, ["stats", "sessions"])
        assert result.exit_code == 0


class TestScheduleCommandExtended:
    def test_schedule_review_unknown_concept(self, repo, runner):
        result = runner.invoke(app, ["schedule", "review", "nonexistent_xyz"])
        assert result.exit_code != 0

    def test_schedule_review_correct(self, db, runner):
        from codecraft.db.repository import Repository
        conn = db.connect()
        repo = Repository(conn)
        repo.conn.execute(
            "INSERT INTO file_concepts (file_path, concept_name, occurrences) VALUES (?, ?, ?)",
            ["test.py", "for_loop", 1],
        )
        result = runner.invoke(app, ["schedule", "review", "for_loop", "--correct"])
        assert result.exit_code == 0

    def test_schedule_review_incorrect(self, db, runner):
        from codecraft.db.repository import Repository
        conn = db.connect()
        repo = Repository(conn)
        repo.conn.execute(
            "INSERT INTO file_concepts (file_path, concept_name, occurrences) VALUES (?, ?, ?)",
            ["test.py", "for_loop", 1],
        )
        result = runner.invoke(app, ["schedule", "review", "for_loop", "--incorrect"])
        assert result.exit_code == 0

    def test_schedule_queue_no_due(self, repo, runner):
        result = runner.invoke(app, ["schedule", "queue", "--threshold", "1.0"])
        assert result.exit_code == 0

    def test_schedule_due_none(self, repo, runner):
        result = runner.invoke(app, ["schedule", "due"])
        assert result.exit_code == 0

    def test_schedule_decay_filtered(self, repo, runner):
        result = runner.invoke(app, ["schedule", "decay", "--min", "100"])
        assert result.exit_code == 0


class TestSyncCommandExtended:
    def test_sync_export_with_data(self, db, runner, tmp_path):
        from codecraft.db.repository import Repository
        from codecraft.models.challenge import ChallengeResult
        conn = db.connect()
        repo = Repository(conn)
        r = ChallengeResult(
            challenge_id="export_test", concept_name="for_loop",
            correct=True, time_taken_seconds=60, domain="gaming",
        )
        repo.insert_challenge_result(r)
        out = tmp_path / "backup.json"
        result = runner.invoke(app, ["sync", "export", str(out)])
        assert result.exit_code == 0
        assert out.exists()

    def test_sync_export_write_failure(self, repo, runner):
        result = runner.invoke(app, ["sync", "export", "/nonexistent_dir/backup.json"])
        assert result.exit_code != 0

    def test_sync_import_bad_json(self, repo, runner, tmp_path):
        f = tmp_path / "bad.json"
        f.write_text("not a json")
        result = runner.invoke(app, ["sync", "import", str(f)])
        assert result.exit_code != 0

    def test_sync_import_overwrite(self, db, runner, tmp_path):
        from codecraft.db.repository import Repository
        from codecraft.models.file import FileRecord
        conn = db.connect()
        repo = Repository(conn)
        repo.upsert_file(FileRecord(path=Path("test.py"), hash="abc", size=100, lines=10))
        out = tmp_path / "backup.json"
        runner.invoke(app, ["sync", "export", str(out)])
        result = runner.invoke(app, ["sync", "import", str(out), "--mode", "overwrite"])
        assert result.exit_code == 0

    def test_sync_import_merge(self, db, runner, tmp_path):
        from codecraft.db.repository import Repository
        conn = db.connect()
        repo = Repository(conn)
        out = tmp_path / "backup.json"
        result = runner.invoke(app, ["sync", "export", str(out)])
        assert result.exit_code == 0
        result = runner.invoke(app, ["sync", "import", str(out), "--mode", "merge"])
        assert result.exit_code == 0


class TestSuggestCommandExtended:
    def test_suggest_next_no_concepts_via_db(self, db, runner):
        conn = db.connect()
        conn.execute("DELETE FROM file_concepts")
        result = runner.invoke(app, ["suggest", "next"])
        assert result.exit_code == 0

    def test_suggest_all_no_concepts_via_db(self, db, runner):
        conn = db.connect()
        conn.execute("DELETE FROM file_concepts")
        result = runner.invoke(app, ["suggest", "all"])
        assert result.exit_code == 0

    def test_suggest_next_no_suggestions(self, db, runner):
        from codecraft.db.repository import Repository
        from codecraft.models.concept import ConceptTaxonomy
        from codecraft.models.file import FileConcept
        conn = db.connect()
        repo = Repository(conn)
        concepts = {c.name: FileConcept(concept_name=c.name, occurrences=1) for c in ConceptTaxonomy.all()}
        repo.upsert_file_concepts(Path("test.py"), concepts)
        result = runner.invoke(app, ["suggest", "next"])
        assert result.exit_code == 0

    def test_suggest_all_no_suggestions(self, db, runner):
        from codecraft.db.repository import Repository
        from codecraft.models.concept import ConceptTaxonomy
        from codecraft.models.file import FileConcept
        conn = db.connect()
        repo = Repository(conn)
        concepts = {c.name: FileConcept(concept_name=c.name, occurrences=1) for c in ConceptTaxonomy.all()}
        repo.upsert_file_concepts(Path("test.py"), concepts)
        result = runner.invoke(app, ["suggest", "all"])
        assert result.exit_code == 0
