from pathlib import Path

from codecraft.scanner.debt_detector import DebtDetector


def _detect(source: str, path: Path) -> list:
    tree = __import__("ast").parse(source)
    detector = DebtDetector(source, path)
    return detector.detect(tree)


def test_bare_except_detected(tmp_path: Path):
    source = """
try:
    result = 10 / 0
except:
    print("error")
"""
    items = _detect(source, tmp_path / "test.py")
    types = [i.pattern_type for i in items]
    assert "bare_except" in types


def test_mutable_default_detected(tmp_path: Path):
    source = """
def process(items=[]):
    items.append(1)
    return items
"""
    items = _detect(source, tmp_path / "test.py")
    types = [i.pattern_type for i in items]
    assert "mutable_default_arg" in types


def test_range_len_detected(tmp_path: Path):
    source = """
data = [1, 2, 3]
for i in range(len(data)):
    print(data[i])
"""
    items = _detect(source, tmp_path / "test.py")
    types = [i.pattern_type for i in items]
    assert "range_len" in types


def test_if_elif_chain_detected(tmp_path: Path):
    source = """
def handle(x):
    if x == "a":
        return 1
    elif x == "b":
        return 2
    elif x == "c":
        return 3
    elif x == "d":
        return 4
    else:
        return 0
"""
    items = _detect(source, tmp_path / "test.py")
    types = [i.pattern_type for i in items]
    assert "if_elif_chain" in types


def test_no_false_positives(tmp_path: Path):
    source = """
def process(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item)
    return result
"""
    items = _detect(source, tmp_path / "test.py")
    assert len(items) == 0 or all(
        i.pattern_type not in ["bare_except", "mutable_default_arg", "range_len", "if_elif_chain"]
        for i in items
    )


def test_broad_except_detected(tmp_path: Path):
    source = """
try:
    risky_operation()
except Exception:
    pass
"""
    items = _detect(source, tmp_path / "test.py")
    types = [i.pattern_type for i in items]
    assert "broad_except" in types
