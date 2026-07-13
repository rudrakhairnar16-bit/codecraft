from __future__ import annotations

import ast
from pathlib import Path

from codecraft.scanner.debt_detector import DebtDetector


def _detect(source: str) -> list[str]:
    tree = ast.parse(source)
    detector = DebtDetector(source, Path("<test>"))
    items = detector.detect(tree)
    return [d.pattern_type for d in items]


class TestWorkingPatterns:
    """Patterns confirmed working in the current detector."""

    def test_mutable_default_arg(self):
        source = """
def add_item(item, items=[]):
    items.append(item)
    return items
"""
        patterns = _detect(source)
        assert "mutable_default_arg" in patterns

    def test_missing_return_annotation(self):
        source = """
def add(a, b):
    return a + b
"""
        patterns = _detect(source)
        assert "missing_return_annotation" in patterns

    def test_bare_except(self):
        source = """
try:
    risky()
except:
    pass
"""
        patterns = _detect(source)
        assert "bare_except" in patterns

    def test_broad_except(self):
        source = """
try:
    risky()
except Exception:
    pass
"""
        patterns = _detect(source)
        assert "broad_except" in patterns

    def test_infinite_while_no_break(self):
        source = """
while True:
    print("looping")
"""
        patterns = _detect(source)
        assert "infinite_while_no_break" in patterns

    def test_single_line_if_no_else(self):
        source = "if True: pass\n"
        patterns = _detect(source)
        assert "single_line_if_no_else" in patterns

    def test_if_elif_chain(self):
        source = """
if x == 1:
    pass
elif x == 2:
    pass
elif x == 3:
    pass
elif x == 4:
    pass
"""
        patterns = _detect(source)
        assert "if_elif_chain" in patterns

    def test_range_len(self):
        source = """
for i in range(len(items)):
    print(i)
"""
        patterns = _detect(source)
        assert "range_len" in patterns


class TestUnusedIndexDetection:
    def test_unused_index_variable(self):
        source = """
for i in range(10):
    print("hello")
"""
        patterns = _detect(source)
        assert "unused_loop_variable" in patterns

    def test_underscore_not_flagged(self):
        """_ is convention for unused, should not be flagged."""
        source = """
for _ in range(10):
    print("hello")
"""
        patterns = _detect(source)
        assert "unused_loop_variable" not in patterns

    def test_used_index_not_flagged(self):
        source = """
for i in range(10):
    print(i)
"""
        patterns = _detect(source)
        assert "unused_loop_variable" not in patterns


class TestNoPatternsCleanCode:
    def test_clean_code_no_debt(self):
        source = """
def add(a: int, b: int) -> int:
    return a + b

result = [i * 2 for i in range(10)]
"""
        patterns = _detect(source)
        assert len(patterns) == 0
