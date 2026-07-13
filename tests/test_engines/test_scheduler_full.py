from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from codecraft.engines.scheduler import ForgettingScheduler as SchedulerEngine
from codecraft.models.review import SpacedRepetitionCard


class InMemoryRepo:
    """Minimal in-memory repo for scheduler testing."""

    def __init__(self):
        self.cards: dict[str, SpacedRepetitionCard] = {}
        self.concepts = []

    def get_all_cards(self):
        return list(self.cards.values())

    def upsert_card(self, card: SpacedRepetitionCard):
        self.cards[card.concept_name] = card

    def get_card(self, concept_name: str) -> SpacedRepetitionCard | None:
        return self.cards.get(concept_name)

    def get_all_concept_names(self):
        return self.concepts

    def get_last_usage(self, concept_name: str):
        from datetime import datetime
        if concept_name in self.concepts:
            return datetime.now()
        return None

    def get_exposure_count(self, concept_name: str) -> int:
        if concept_name in self.concepts:
            return 3
        return 0

    def get_all_debt_items(self):
        return []

    def get_settings(self, key, default=None):
        return default

    def set_setting(self, key, value):
        pass


@pytest.fixture
def engine():
    repo = InMemoryRepo()
    repo.concepts = ["for_loop", "function_def", "class_basic"]
    return SchedulerEngine(repo)


class TestSchedulerInitialization:
    def test_initial_due_count(self, engine):
        due = engine.get_due_cards()
        assert len(due) == 3

    def test_initial_queue(self, engine):
        cards = engine.get_all_cards()
        assert len(cards) == 0

    def test_initial_concepts_loaded(self, engine):
        concepts = engine.get_scheduled_concepts()
        assert len(concepts) == 0


class TestSchedulerSchedule:
    def test_schedule_new_concept(self, engine):
        card = engine.schedule("for_loop")
        assert card is not None
        assert card.concept_name == "for_loop"
        assert card.ease_factor == 2.5
        assert card.interval_days == 1
        assert card.strength == 1.0

    def test_schedule_unknown_concept(self, engine):
        card = engine.schedule("nonexistent")
        assert card is not None

    def test_schedule_twice_returns_same(self, engine):
        card1 = engine.schedule("for_loop")
        card2 = engine.schedule("for_loop")
        assert card1.concept_name == card2.concept_name


class TestSchedulerReview:
    def test_review_correct_increases_interval(self, engine):
        engine.schedule("for_loop")
        card = engine.review("for_loop", correct=True, time_taken=10)
        assert card.interval_days >= 1
        assert card.repetitions >= 1

    def test_review_incorrect_resets(self, engine):
        engine.schedule("for_loop")
        card = engine.review("for_loop", correct=False, time_taken=30)
        assert card.repetitions == 0

    def test_review_multiple_correct(self, engine):
        engine.schedule("for_loop")
        for _ in range(3):
            card = engine.review("for_loop", correct=True, time_taken=5)
        assert card.repetitions >= 3
        assert card.interval_days > 1

    def test_review_after_incorrect_then_correct(self, engine):
        engine.schedule("for_loop")
        engine.review("for_loop", correct=False, time_taken=10)
        card = engine.review("for_loop", correct=True, time_taken=5)
        assert card.repetitions >= 1


class TestSchedulerDueCards:
    def test_new_card_is_due(self, engine):
        engine.schedule("for_loop")
        due = engine.get_due_cards()
        assert len(due) == 3

    def test_reviewed_card_not_due(self, engine):
        engine.schedule("for_loop")
        engine.review("for_loop", correct=True, time_taken=5)
        due = engine.get_due_cards()
        assert len(due) == 2

    def test_expired_card_is_due(self, engine):
        engine.schedule("for_loop")
        card = engine.get_all_cards()[0]
        card.next_review = datetime.now() - timedelta(hours=1)
        engine.repo.upsert_card(card)
        due = engine.get_due_cards()
        assert len(due) == 3

    def test_multiple_due_cards(self, engine):
        for concept in ["for_loop", "function_def"]:
            engine.schedule(concept)
        due = engine.get_due_cards()
        assert len(due) == 3


class TestSchedulerLabels:
    def test_fresh_label(self, engine):
        engine.schedule("for_loop")
        card = engine.review("for_loop", correct=True, time_taken=5)
        card.strength = 0.9
        status = engine.compute_status("for_loop")
        assert status in ("fresh", "stable")

    def test_decaying_label(self, engine):
        engine.schedule("for_loop")
        card = engine.review("for_loop", correct=True, time_taken=5)
        card.strength = 0.3
        engine.repo.upsert_card(card)
        status = engine.compute_status("for_loop")
        assert status == "decaying"

    def test_unknown_concept_status(self, engine):
        status = engine.compute_status("nothing")
        assert status is None


class TestScheduleDecay:
    def test_decay_all_reduces_strength(self, engine):
        engine.schedule("for_loop")
        engine.review("for_loop", correct=True, time_taken=5)
        engine.apply_decay(factor=0.5)
        card = engine.get_all_cards()[0]
        assert card.strength <= 1.0

    def test_decay_with_zero_factor(self, engine):
        engine.schedule("for_loop")
        engine.apply_decay(factor=0.0)
        card = engine.get_all_cards()[0]
        assert card.strength == 0.0
