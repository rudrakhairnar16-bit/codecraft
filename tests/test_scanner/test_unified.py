from pathlib import Path

from codecraft.scanner.unified import UnifiedScanner


def test_scan_beginner_file(beginner_file: Path):
    scanner = UnifiedScanner()
    report = scanner.scan_file(beginner_file)
    assert report is not None
    assert len(report.errors) == 0
    assert len(report.concepts) > 0
    assert report.lines > 0
    assert report.complexity >= 1.0


def test_scan_intermediate_file(intermediate_file: Path):
    scanner = UnifiedScanner()
    report = scanner.scan_file(intermediate_file)
    assert report is not None
    assert len(report.errors) == 0
    assert "list_comprehension" in report.concepts
    assert "enumerate" in report.concepts
    assert "context_manager" in report.concepts


def test_scan_advanced_file(advanced_file: Path):
    scanner = UnifiedScanner()
    report = scanner.scan_file(advanced_file)
    assert report is not None
    assert len(report.errors) == 0
    assert "async_await" in report.concepts
    assert "dataclass" in report.concepts
    assert "match_case" in report.concepts


def test_fingerprint_beginner(beginner_file: Path):
    scanner = UnifiedScanner()
    fp = scanner.fingerprint_file(beginner_file)
    assert fp is not None
    assert fp.hash
    assert fp.lines > 0
    assert fp.complexity >= 1.0
    assert fp.function_count >= 0


def test_scan_nonexistent_file():
    scanner = UnifiedScanner()
    report = scanner.scan_file(Path("/nonexistent/file.py"))
    assert report is None


def test_scan_non_python_file(tmp_path: Path):
    f = tmp_path / "data.txt"
    f.write_text("hello world")
    scanner = UnifiedScanner()
    report = scanner.scan_file(f)
    assert report is None


def test_scan_directory(fixtures_dir: Path):
    scanner = UnifiedScanner()
    reports = scanner.scan_directory(fixtures_dir)
    assert len(reports) == 3
    assert all(r is not None for r in reports)
