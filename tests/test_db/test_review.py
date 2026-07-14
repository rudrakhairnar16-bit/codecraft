from __future__ import annotations

from datetime import datetime, timedelta

from codecraft.models.review import ReviewQueue, SpacedRepetitionCard


def test_card_is_due_no_review():
    card = SpacedRepetitionCard(concept_name="for_loop")
    assert card.is_due() is True


def test_card_is_due_future():
    card = SpacedRepetitionCard(
        concept_name="for_loop",
        next_review=datetime.now() + timedelta(hours=24),
    )
    assert card.is_due() is False


def test_card_is_due_past():
    card = SpacedRepetitionCard(
        concept_name="for_loop",
        next_review=datetime.now() - timedelta(hours=1),
    )
    assert card.is_due() is True


def test_is_due_at():
    card = SpacedRepetitionCard(
        concept_name="for_loop",
        next_review=datetime(2025, 1, 1),
    )
    assert card.is_due(at=datetime(2025, 6, 1)) is True
    assert card.is_due(at=datetime(2024, 12, 31)) is False


def test_urgency_not_due():
    card = SpacedRepetitionCard(
        concept_name="for_loop",
        next_review=datetime.now() + timedelta(days=1),
    )
    assert card.urgency == 0.0


def test_urgency_no_review():
    card = SpacedRepetitionCard(concept_name="for_loop")
    assert card.urgency == 0.0


def test_urgency_overdue():
    card = SpacedRepetitionCard(
        concept_name="for_loop",
        next_review=datetime.now() - timedelta(days=5),
    )
    assert card.urgency >= 4.9
    assert card.urgency <= 5.1


def test_urgency_capped():
    card = SpacedRepetitionCard(
        concept_name="for_loop",
        next_review=datetime.now() - timedelta(days=60),
    )
    assert card.urgency == 30.0


def test_review_queue_empty():
    q = ReviewQueue()
    assert q.due_cards() == []
    assert q.sort_by_urgency() == []


def test_review_queue_due_cards():
    due = SpacedRepetitionCard(
        concept_name="for_loop",
        next_review=datetime.now() - timedelta(hours=1),
    )
    not_due = SpacedRepetitionCard(
        concept_name="if_else",
        next_review=datetime.now() + timedelta(days=1),
    )
    q = ReviewQueue(cards=[due, not_due])
    due_list = q.due_cards()
    assert len(due_list) == 1
    assert due_list[0].concept_name == "for_loop"


def test_review_queue_sort_by_urgency():
    less_urgent = SpacedRepetitionCard(
        concept_name="for_loop",
        next_review=datetime.now() - timedelta(days=1),
    )
    more_urgent = SpacedRepetitionCard(
        concept_name="if_else",
        next_review=datetime.now() - timedelta(days=10),
    )
    q = ReviewQueue(cards=[less_urgent, more_urgent])
    sorted_cards = q.sort_by_urgency()
    assert len(sorted_cards) == 2
    assert sorted_cards[0].concept_name == "if_else"
    assert sorted_cards[1].concept_name == "for_loop"
