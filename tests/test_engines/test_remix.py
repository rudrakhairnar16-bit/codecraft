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


def test_find_unused_domains(repo):
    file_path = Path("/test/a.py")
    record = FileRecord(path=file_path, hash="abc", size=10, lines=1)
    repo.upsert_file(record)
    concepts = {
        "for_loop": FileConcept(concept_name="for_loop", occurrences=1),
    }
    repo.upsert_file_concepts(file_path, concepts)

    engine = RemixEngine(repo)
    unused = engine.find_unused_domains("for_loop")
    assert isinstance(unused, list)


def test_generate_exercise_with_domain(repo):
    file_path = Path("/test/a.py")
    record = FileRecord(path=file_path, hash="abc", size=10, lines=1)
    repo.upsert_file(record)
    concepts = {
        "for_loop": FileConcept(concept_name="for_loop", occurrences=1),
    }
    repo.upsert_file_concepts(file_path, concepts)

    engine = RemixEngine(repo)
    challenge = engine.generate_exercise("for_loop", domain_name="gaming")
    assert challenge is not None
    assert challenge.concept_name == "for_loop"


def test_get_domain_stats_with_matches(repo):
    file_path = Path("/test/a.py")
    record = FileRecord(path=file_path, hash="abc", size=10, lines=1)
    repo.upsert_file(record)
    concepts = {
        "for_loop": FileConcept(concept_name="for_loop", occurrences=3),
        "list_comprehension": FileConcept(concept_name="list_comprehension", occurrences=2),
        "if_else": FileConcept(concept_name="if_else", occurrences=5),
    }
    repo.upsert_file_concepts(file_path, concepts)

    engine = RemixEngine(repo)
    stats = engine.get_domain_stats()
    assert len(stats) > 0
    for s in stats:
        assert s["match_ratio"] >= 0
        assert s["match_ratio"] <= 1.0


def test_find_unused_domains_with_used(repo):
    file_path = Path("/test/gaming_data.py")
    record = FileRecord(path=file_path, hash="abc", size=10, lines=1)
    repo.upsert_file(record)
    concepts = {
        "for_loop": FileConcept(concept_name="for_loop", occurrences=3),
    }
    repo.upsert_file_concepts(file_path, concepts)

    engine = RemixEngine(repo)
    unused = engine.find_unused_domains("for_loop")
    assert isinstance(unused, list)
    assert "gaming" not in unused


def test_generate_exercise_with_fallback_domain(repo):
    engine = RemixEngine(repo)
    challenge = engine.generate_exercise("nonexistent_concept_for_testing")
    assert challenge is None


def test_generate_review_exercise_no_unused(repo):
    engine = RemixEngine(repo)
    challenge = engine.generate_review_exercise("nonexistent_concept_for_testing")
    assert challenge is None
