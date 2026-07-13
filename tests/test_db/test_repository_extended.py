from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from codecraft.db.repository import Repository
from codecraft.models.challenge import ChallengeResult
from codecraft.models.debt import DebtItem
from codecraft.models.file import FileConcept, FileRecord
from codecraft.models.review import SpacedRepetitionCard


@pytest.fixture
def repo(in_memory_db):
    conn = in_memory_db
    from codecraft.db.migrations import run_migrations

    run_migrations(conn)
    return Repository(conn)


class TestFileCRUD:
    def test_upsert_file(self, repo):
        record = FileRecord(path=Path("/test/file.py"), hash="abc123", size=100, lines=10)
        repo.upsert_file(record)
        retrieved = repo.get_file(Path("/test/file.py"))
        assert retrieved is not None
        assert retrieved.hash == "abc123"

    def test_upsert_updates_existing(self, repo):
        record = FileRecord(path=Path("/test/file.py"), hash="abc123", size=100, lines=10)
        repo.upsert_file(record)
        record.hash = "def456"
        repo.upsert_file(record)
        retrieved = repo.get_file(Path("/test/file.py"))
        assert retrieved.hash == "def456"

    def test_get_nonexistent_file(self, repo):
        retrieved = repo.get_file(Path("/nonexistent.py"))
        assert retrieved is None

    def test_get_all_files(self, repo):
        for i in range(3):
            repo.upsert_file(
                FileRecord(path=Path(f"/test/file{i}.py"), hash=f"hash{i}", size=10, lines=1)
            )
        files = repo.get_all_files()
        assert len(files) == 3


class TestFileConceptsCRUD:
    def test_upsert_file_concepts(self, repo):
        concepts = {
            "for_loop": FileConcept(concept_name="for_loop", occurrences=5),
            "function_def": FileConcept(concept_name="function_def", occurrences=2),
        }
        repo.upsert_file_concepts(Path("/test/file.py"), concepts)
        names = repo.get_all_concept_names()
        assert "for_loop" in names
        assert "function_def" in names

    def test_upsert_empty_concepts(self, repo):
        repo.upsert_file_concepts(Path("/test/file.py"), {})
        names = repo.get_all_concept_names()
        assert len(names) == 0


class TestDebtCRUD:
    def test_insert_and_list_debt(self, repo):
        item = DebtItem(
            id=1,
            file_path="/test/file.py",
            pattern_type="bare_except",
            pattern_location="line 5",
            old_snippet="except:",
            suggestion="Use specific exception",
            alternative_code="except ValueError:",
            difficulty=2,
            tier_gap=1,
            resolved=False,
            created=datetime.now(),
        )
        repo.conn.execute(
            "INSERT INTO debt_items (id, file_path, pattern_type, pattern_location, old_snippet, suggestion, alternative_code, difficulty, tier_gap, resolved, created) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [item.id, item.file_path, item.pattern_type, item.pattern_location, item.old_snippet, item.suggestion, item.alternative_code, item.difficulty, item.tier_gap, item.resolved, item.created],
        )
        items = repo.get_all_debt_items()
        assert len(items) >= 1
        assert items[0].pattern_type == "bare_except"


class TestChallengeHistory:
    def test_insert_challenge_result(self, repo):
        result = ChallengeResult(
            challenge_id=1,
            challenge_type="refactor",
            concept_name="bare_except",
            correct=True,
            hints_used=0,
            time_taken_seconds=30,
            domain="general",
        )
        repo.insert_challenge_result(result)
        rows = repo.conn.execute("SELECT * FROM challenge_history").fetchall()
        assert len(rows) >= 1
        assert rows[0][1] == "refactor"

    def test_insert_with_different_types(self, repo):
        types = ["refactor", "transfer", "quiz", "code_review"]
        for t in types:
            result = ChallengeResult(
                challenge_id=1,
                challenge_type=t,
                concept_name="for_loop",
                correct=True,
                hints_used=0,
                time_taken_seconds=10,
            )
            repo.insert_challenge_result(result)
        rows = repo.conn.execute("SELECT * FROM challenge_history").fetchall()
        assert len(rows) == 4


class TestSpacedRepetition:
    def test_upsert_card(self, repo):
        card = SpacedRepetitionCard(
            concept_name="for_loop",
            ease_factor=2.5,
            interval_days=1,
            repetitions=0,
            next_review=datetime.now(),
            last_review=datetime.now(),
            strength=1.0,
        )
        repo.upsert_card(card)
        cards = repo.get_all_cards()
        assert len(cards) == 1

    def test_upsert_card_update(self, repo):
        card = SpacedRepetitionCard(
            concept_name="for_loop",
            ease_factor=2.5,
            interval_days=1,
            repetitions=0,
            next_review=datetime.now(),
            last_review=datetime.now(),
            strength=1.0,
        )
        repo.upsert_card(card)
        card.strength = 0.5
        repo.upsert_card(card)
        cards = repo.get_all_cards()
        assert cards[0].strength == 0.5


class TestSettings:
    def test_set_and_get(self, repo):
        repo.set_setting("test_key", "test_value")
        value = repo.get_setting("test_key")
        assert value == "test_value"

    def test_get_nonexistent(self, repo):
        value = repo.get_setting("nonexistent")
        assert value == ""

    def test_get_default(self, repo):
        value = repo.get_setting("nonexistent", "fallback")
        assert value == "fallback"

    def test_update_setting(self, repo):
        repo.set_setting("key", "value1")
        repo.set_setting("key", "value2")
        assert repo.get_setting("key") == "value2"


class TestPracticeStats:
    def test_get_practice_stats_empty(self, repo):
        stats = repo.get_practice_stats()
        assert stats["total_sessions"] == 0

    def test_get_practice_stats_with_data(self, repo):
        for i in range(5):
            result = ChallengeResult(
                challenge_id=i,
                challenge_type="quiz",
                concept_name="for_loop",
                correct=True,
                hints_used=0,
                time_taken_seconds=10,
            )
            repo.insert_challenge_result(result)
        stats = repo.get_practice_stats()
        assert stats["total_sessions"] >= 5
