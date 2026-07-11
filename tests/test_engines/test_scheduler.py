from datetime import datetime, timedelta
from pathlib import Path

from codecraft.engines.scheduler import ForgettingScheduler
from codecraft.models.file import FileConcept, FileRecord


def test_strength_decay(repo):
    file_path = Path("/test/a.py")
    record = FileRecord(path=file_path, hash="abc", size=10, lines=1)
    repo.upsert_file(record)

    now = datetime.now()
    old = now - timedelta(days=30)

    concepts = {
        "list_comprehension": FileConcept(
            concept_name="list_comprehension",
            occurrences=5,
            first_seen=old,
            last_seen=old,
        )
    }
    repo.upsert_file_concepts(file_path, concepts)

    scheduler = ForgettingScheduler(repo, decay_constant=7.0)
    strength = scheduler._compute_strength("list_comprehension", now)
    assert strength < 0.5


def test_fresh_concept_high_strength(repo):
    file_path = Path("/test/a.py")
    record = FileRecord(path=file_path, hash="abc", size=10, lines=1)
    repo.upsert_file(record)

    now = datetime.now()
    concepts = {
        "list_comprehension": FileConcept(
            concept_name="list_comprehension",
            occurrences=5,
            first_seen=now,
            last_seen=now,
        )
    }
    repo.upsert_file_concepts(file_path, concepts)

    scheduler = ForgettingScheduler(repo, decay_constant=7.0)
    strength = scheduler._compute_strength("list_comprehension", now)
    assert strength > 0.8


def test_review_improves_interval(repo):
    file_path = Path("/test/a.py")
    record = FileRecord(path=file_path, hash="abc", size=10, lines=1)
    repo.upsert_file(record)

    now = datetime.now()
    concepts = {
        "list_comprehension": FileConcept(
            concept_name="list_comprehension",
            occurrences=3,
            first_seen=now,
            last_seen=now,
        )
    }
    repo.upsert_file_concepts(file_path, concepts)

    scheduler = ForgettingScheduler(repo)

    card = scheduler.after_review("list_comprehension", correct=True)
    assert card.interval_days > 1
    assert card.repetitions == 1
    assert card.ease_factor > 2.5

    card2 = scheduler.after_review("list_comprehension", correct=True)
    assert card2.interval_days > card.interval_days


def test_wrong_review_shortens_interval(repo):
    file_path = Path("/test/a.py")
    record = FileRecord(path=file_path, hash="abc", size=10, lines=1)
    repo.upsert_file(record)
    now = datetime.now()
    concepts = {
        "list_comprehension": FileConcept(
            concept_name="list_comprehension",
            occurrences=3,
            first_seen=now,
            last_seen=now,
        )
    }
    repo.upsert_file_concepts(file_path, concepts)

    scheduler = ForgettingScheduler(repo)
    card = scheduler.after_review("list_comprehension", correct=False)
    assert card.repetitions == 0 or card.interval_days == 1


def test_get_review_queue(repo):
    file_path = Path("/test/a.py")
    record = FileRecord(path=file_path, hash="abc", size=10, lines=1)
    repo.upsert_file(record)
    concepts = {
        "list_comprehension": FileConcept(
            concept_name="list_comprehension",
            occurrences=3,
            last_seen=datetime.now(),
        )
    }
    repo.upsert_file_concepts(file_path, concepts)

    scheduler = ForgettingScheduler(repo)
    queue = scheduler.get_review_queue(threshold=0.0)
    assert len(queue.cards) >= 1
