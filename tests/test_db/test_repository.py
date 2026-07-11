from pathlib import Path

from codecraft.db.repository import Repository
from codecraft.models.debt import DebtItem
from codecraft.models.file import FileConcept, FileRecord
from codecraft.models.review import SpacedRepetitionCard


def test_upsert_and_get_file(repo: Repository):
    record = FileRecord(
        path=Path("/test/file.py"),
        hash="abc123",
        size=100,
        lines=10,
    )
    repo.upsert_file(record)

    retrieved = repo.get_file(Path("/test/file.py"))
    assert retrieved is not None
    assert retrieved.path == Path("/test/file.py")
    assert retrieved.hash == "abc123"


def test_upsert_updates_existing(repo: Repository):
    record = FileRecord(path=Path("/test/file.py"), hash="abc", size=100, lines=10)
    repo.upsert_file(record)

    updated = FileRecord(path=Path("/test/file.py"), hash="def", size=200, lines=20)
    repo.upsert_file(updated)

    retrieved = repo.get_file(Path("/test/file.py"))
    assert retrieved.hash == "def"
    assert retrieved.size == 200


def test_file_concepts(repo: Repository):
    file_path = Path("/test/file.py")
    record = FileRecord(path=file_path, hash="abc", size=100, lines=10)
    repo.upsert_file(record)

    concepts = {
        "list_comprehension": FileConcept(concept_name="list_comprehension", occurrences=3),
        "enumerate": FileConcept(concept_name="enumerate", occurrences=1),
    }
    repo.upsert_file_concepts(file_path, concepts)

    retrieved = repo.get_file_concepts(file_path)
    assert len(retrieved) == 2
    assert retrieved["list_comprehension"].occurrences == 3


def test_debt_item_lifecycle(repo: Repository):
    item = DebtItem(
        file_path=Path("/test/file.py"),
        pattern_type="bare_except",
        pattern_location="line 5",
        old_snippet="except:",
        suggestion="Catch specific exception",
        alternative_code="except ValueError:",
        difficulty=1,
        tier_gap=1,
    )
    repo.insert_debt_item(item)

    unresolved = repo.get_unresolved_debt()
    assert len(unresolved) == 1
    assert unresolved[0].pattern_type == "bare_except"

    all_items = repo.get_all_debt_items()
    assert len(all_items) == 1

    repo.resolve_debt_item(all_items[0].id)
    unresolved = repo.get_unresolved_debt()
    assert len(unresolved) == 0


def test_spaced_repetition_card(repo: Repository):
    card = SpacedRepetitionCard(
        concept_name="list_comprehension",
        ease_factor=2.5,
        interval_days=1,
        strength=0.8,
    )
    repo.upsert_card(card)

    retrieved = repo.get_card("list_comprehension")
    assert retrieved is not None
    assert retrieved.ease_factor == 2.5
    assert retrieved.strength == 0.8


def test_get_all_files(repo: Repository):
    files = [
        FileRecord(path=Path(f"/test/{i}.py"), hash=f"hash{i}", size=100, lines=10)
        for i in range(3)
    ]
    for f in files:
        repo.upsert_file(f)

    all_files = repo.get_all_files()
    assert len(all_files) == 3
