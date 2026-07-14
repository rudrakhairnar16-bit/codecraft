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


def test_scan_js_file(tmp_path: Path):
    f = tmp_path / "app.js"
    f.write_text("function hello() { return 1; }")
    scanner = UnifiedScanner()
    report = scanner.scan_file(f)
    assert report is not None


def test_scan_ts_file(tmp_path: Path):
    f = tmp_path / "app.ts"
    f.write_text("const x: number = 1;")
    scanner = UnifiedScanner()
    report = scanner.scan_file(f)
    assert report is not None


def test_fingerprint_js_file(tmp_path: Path):
    f = tmp_path / "app.js"
    f.write_text("function hello() { return 1; }")
    scanner = UnifiedScanner()
    fp = scanner.fingerprint_file(f)
    assert fp is not None
    assert fp.lines > 0


def test_scan_directory_with_mixed_files(tmp_path: Path):
    d = tmp_path / "mixed"
    d.mkdir()
    (d / "main.py").write_text("x = 1")
    (d / "util.js").write_text("function f() { return 1; }")
    (d / "data.ts").write_text("const y: number = 2;")
    (d / "readme.md").write_text("# Docs")
    scanner = UnifiedScanner()
    reports = scanner.scan_directory(d)
    assert len(reports) == 3


def test_fingerprint_multilang_bad_file(tmp_path: Path):
    f = tmp_path / "test.unknown"
    f.write_text("data")
    scanner = UnifiedScanner()
    fp = scanner.fingerprint_file(f)
    assert fp is None


def test_scan_file_with_syntax_error(tmp_path: Path):
    f = tmp_path / "bad.py"
    f.write_text("def foo( bar")
    scanner = UnifiedScanner()
    report = scanner.scan_file(f)
    assert report is not None
    assert "Failed to parse" in (report.errors or [])


def test_fingerprint_python_with_main_guard(tmp_path: Path):
    f = tmp_path / "main.py"
    f.write_text('"""Module docstring."""\ndef main():\n    pass\n\nif __name__ == "__main__":\n    main()\n')
    scanner = UnifiedScanner()
    fp = scanner.fingerprint_file(f)
    assert fp is not None
    assert fp.has_main_guard or fp.has_docstring


def test_fingerprint_non_python_supported(tmp_path: Path):
    f = tmp_path / "data.js"
    f.write_text("const x = 1;")
    scanner = UnifiedScanner()
    fp = scanner.fingerprint_file(f)
    assert fp is not None


def test_scan_directory_with_subdir(tmp_path: Path):
    d = tmp_path / "project"
    d.mkdir()
    sub = d / "sub"
    sub.mkdir()
    (d / "main.py").write_text("x = 1")
    scanner = UnifiedScanner()
    reports = scanner.scan_directory(d)
    assert len(reports) == 1
    assert all(r is not None for r in reports)


def test_scan_malformed_multilang(tmp_path: Path):
    f = tmp_path / "test.js"
    f.write_text("\x00\x00\x00\x00\x00")  # Binary garbage to cause parser error
    scanner = UnifiedScanner()
    report = scanner.scan_file(f)
    assert report is not None
