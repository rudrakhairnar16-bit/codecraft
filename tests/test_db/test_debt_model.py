from __future__ import annotations

from pathlib import Path

from codecraft.models.debt import DebtItem, DebtReport


def test_debt_item_defaults():
    item = DebtItem()
    assert item.id is None
    assert item.resolved is False


def test_debt_item_with_values():
    item = DebtItem(
        id=1, file_path=Path("test.py"), pattern_type="bare_except",
        pattern_location="5:0", old_snippet="except:",
        suggestion="Use specific", alternative_code="except ValueError:",
        difficulty=1, resolved=False,
    )
    assert item.id == 1
    assert item.pattern_type == "bare_except"


def test_debt_report_empty():
    report = DebtReport()
    assert report.total_items == 0
    assert report.unresolved == []
    assert report.resolution_rate == 1.0


def test_debt_report_with_items():
    items = [
        DebtItem(id=1, resolved=True),
        DebtItem(id=2, resolved=False),
    ]
    report = DebtReport(
        total_items=2, resolved_items=1, by_type={"bare_except": 1},
        items=items, score=0.5,
    )
    assert report.total_items == 2
    assert len(report.unresolved) == 1
    assert report.resolution_rate == 0.5


def test_debt_report_unresolved():
    items = [
        DebtItem(id=1, resolved=True),
        DebtItem(id=2, resolved=False),
        DebtItem(id=3, resolved=False),
    ]
    report = DebtReport(total_items=3, resolved_items=1, items=items)
    unresolved = report.unresolved
    assert len(unresolved) == 2
    assert all(i.resolved is False for i in unresolved)
