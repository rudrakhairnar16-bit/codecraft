from pathlib import Path

from codecraft.engines.remix import RemixEngine
from codecraft.models.file import FileConcept, FileRecord


def test_find_gaps(repo):
    file_path = Path("/test/a.py")
    record = FileRecord(path=file_path, hash="abc", size=10, lines=1)
    repo.upsert_file(record)

    concepts = {
        "list_comprehension": FileConcept(concept_name="list_comprehension", occurrences=1),
        "enumerate": FileConcept(concept_name="enumerate", occurrences=2),
        "context_manager": FileConcept(concept_name="context_manager", occurrences=5),
    }
    repo.upsert_file_concepts(file_path, concepts)

    engine = RemixEngine(repo)
    gaps = engine.find_gaps(threshold=2)
    assert "list_comprehension" in gaps
    assert "enumerate" in gaps
    assert "context_manager" not in gaps


def test_generate_exercise(repo):
    file_path = Path("/test/a.py")
    record = FileRecord(path=file_path, hash="abc", size=10, lines=1)
    repo.upsert_file(record)
    concepts = {
        "list_comprehension": FileConcept(concept_name="list_comprehension", occurrences=1),
    }
    repo.upsert_file_concepts(file_path, concepts)

    engine = RemixEngine(repo)
    challenge = engine.generate_exercise("list_comprehension")
    assert challenge is not None
    assert challenge.concept_name == "list_comprehension"
    assert challenge.domain


def test_domain_stats(repo):
    file_path = Path("/test/a.py")
    record = FileRecord(path=file_path, hash="abc", size=10, lines=1)
    repo.upsert_file(record)
    concepts = {
        "list_comprehension": FileConcept(concept_name="list_comprehension", occurrences=1),
    }
    repo.upsert_file_concepts(file_path, concepts)

    engine = RemixEngine(repo)
    stats = engine.get_domain_stats()
    assert len(stats) > 0
    assert all("domain" in s for s in stats)


def test_generate_review_exercise(repo):
    file_path = Path("/test/a.py")
    record = FileRecord(path=file_path, hash="abc", size=10, lines=1)
    repo.upsert_file(record)
    concepts = {
        "list_comprehension": FileConcept(concept_name="list_comprehension", occurrences=1),
    }
    repo.upsert_file_concepts(file_path, concepts)

    engine = RemixEngine(repo)
    challenge = engine.generate_review_exercise("list_comprehension")
    assert challenge is not None
