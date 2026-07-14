from __future__ import annotations

from pathlib import Path

from codecraft.scanner.unified import UnifiedScanner


def test_scan_no_path():
    scanner = UnifiedScanner()
    report = scanner.scan_file(Path("/nonexistent"))
    assert report is None


def test_scan_unknown_lang(tmp_path):
    scanner = UnifiedScanner()
    f = tmp_path / "test.xyz"
    f.write_text("hello")
    report = scanner.scan_file(f)
    assert report is None


def test_fingerprint_python(beginner_file):
    scanner = UnifiedScanner()
    fp = scanner.fingerprint_file(beginner_file)
    assert fp is not None
    assert fp.has_main_guard is not None
    assert fp.complexity >= 1.0


def test_fingerprint_nonexistent():
    scanner = UnifiedScanner()
    fp = scanner.fingerprint_file(Path("/nonexistent/file.py"))
    assert fp is None


def test_fingerprint_unknown_lang(tmp_path):
    scanner = UnifiedScanner()
    f = tmp_path / "test.xyz"
    f.write_text("data")
    fp = scanner.fingerprint_file(f)
    assert fp is None


def test_scan_directory_ignore_hidden(tmp_path):
    scanner = UnifiedScanner()
    d = tmp_path / "project"
    d.mkdir()
    (d / "main.py").write_text("x = 1")
    (d / ".hidden.py").write_text("y = 2")
    reports = scanner.scan_directory(d)
    assert len(reports) == 1


def test_scan_directory_empty(tmp_path):
    scanner = UnifiedScanner()
    reports = scanner.scan_directory(tmp_path)
    assert len(reports) == 0
