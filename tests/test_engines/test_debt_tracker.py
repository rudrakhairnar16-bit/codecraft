from pathlib import Path

from codecraft.db.repository import Repository
from codecraft.engines.debt_tracker import DebtTrackerEngine
from codecraft.models.debt import DebtItem


def test_track_new_debt(repo: Repository):
    engine = DebtTrackerEngine(repo)
    items = [
        DebtItem(
            file_path=Path("/test/a.py"),
            pattern_type="bare_except",
            pattern_location="line 3",
            old_snippet="except:",
            suggestion="Use specific exception",
            alternative_code="except ValueError:",
            difficulty=1,
            tier_gap=1,
        ),
        DebtItem(
            file_path=Path("/test/b.py"),
            pattern_type="range_len",
            pattern_location="line 10",
            old_snippet="for i in range(len(x)):",
            suggestion="Use enumerate",
            alternative_code="for i, item in enumerate(x):",
            difficulty=1,
            tier_gap=1,
        ),
    ]

    report = engine.scan_and_track(items)
    assert report.total_items >= 2
    assert "bare_except" in report.by_type


def test_no_duplicates(repo: Repository):
    engine = DebtTrackerEngine(repo)
    item = DebtItem(
        file_path=Path("/test/a.py"),
        pattern_type="bare_except",
        pattern_location="line 3",
        old_snippet="except:",
        suggestion="Use specific exception",
        alternative_code="except ValueError:",
        difficulty=1,
        tier_gap=1,
    )

    engine.scan_and_track([item])
    engine.scan_and_track([item])

    report = engine.get_report()
    assert report.total_items == 1


def test_generate_challenge(repo: Repository):
    engine = DebtTrackerEngine(repo)
    item = DebtItem(
        file_path=Path("/test/a.py"),
        pattern_type="bare_except",
        pattern_location="line 3",
        old_snippet="except:",
        suggestion="Catch specific exceptions",
        alternative_code="except (ValueError, TypeError) as e:",
        difficulty=1,
        tier_gap=1,
    )

    challenge = engine.generate_challenge(item)
    assert challenge.concept_name == "bare_except"
    assert challenge.description == "Catch specific exceptions"
    assert challenge.difficulty == 1


def test_get_report_empty(repo: Repository):
    engine = DebtTrackerEngine(repo)
    report = engine.get_report()
    assert report.total_items == 0
    assert report.score == 0.0
