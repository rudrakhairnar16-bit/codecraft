from __future__ import annotations

from pathlib import Path

import pytest

from codecraft.scanner.multilang import Language, LanguageDetector
from codecraft.scanner.multilang.scanner import MultiLanguageScanner


@pytest.fixture
def scanner():
    return MultiLanguageScanner()


def test_parsers_initialized(scanner):
    langs = scanner.supported_languages
    assert Language.PYTHON in langs


def test_parse_source_python(scanner):
    concepts = scanner.parse_source("def foo(): pass\nx = 1", Language.PYTHON)
    assert isinstance(concepts, dict)
    assert "function_def" in concepts


def test_parse_source_unknown_language(scanner):
    concepts = scanner.parse_source("hello world", Language.UNKNOWN)
    assert concepts == {}


def test_parse_file_python(tmp_path, scanner):
    f = tmp_path / "test.py"
    f.write_text("class A: pass")
    concepts = scanner.parse_file(str(f))
    assert isinstance(concepts, dict)
    assert "class_basic" in concepts


def test_parse_file_nonexistent(scanner):
    concepts = scanner.parse_file("/nonexistent/file.py")
    assert concepts == {}


def test_parse_file_unknown_ext(tmp_path, scanner):
    f = tmp_path / "test.txt"
    f.write_text("hello")
    concepts = scanner.parse_file(str(f))
    assert concepts == {}


def test_parse_file_js(tmp_path, scanner):
    f = tmp_path / "test.js"
    f.write_text("function hello() { return 1; }")
    concepts = scanner.parse_file(str(f))
    assert isinstance(concepts, dict)


def test_parse_file_ts(tmp_path, scanner):
    f = tmp_path / "test.ts"
    f.write_text("function add(a: number): number { return a; }")
    concepts = scanner.parse_file(str(f))
    assert isinstance(concepts, dict)


def test_parse_file_go(tmp_path, scanner):
    f = tmp_path / "test.go"
    f.write_text("package main\nfunc main() {}")
    concepts = scanner.parse_file(str(f))
    assert isinstance(concepts, dict)


def test_parse_file_rs(tmp_path, scanner):
    f = tmp_path / "test.rs"
    f.write_text("fn main() {}")
    concepts = scanner.parse_file(str(f))
    assert isinstance(concepts, dict)


def test_parse_file_java(tmp_path, scanner):
    f = tmp_path / "Test.java"
    f.write_text("class Test { void run() {} }")
    concepts = scanner.parse_file(str(f))
    assert isinstance(concepts, dict)


def test_supported_extensions(scanner):
    exts = scanner.supported_extensions
    assert ".py" in exts
    assert ".js" in exts
    assert ".ts" in exts
    assert ".go" in exts
    assert ".rs" in exts
    assert ".java" in exts


def test_parse_source_javascript(scanner):
    concepts = scanner.parse_source(
        "const x = 1; function foo() { return x; }", Language.JAVASCRIPT
    )
    assert "function_def" in concepts
    assert "variable_assignment" in concepts


def test_parse_source_typescript(scanner):
    concepts = scanner.parse_source(
        "let x: number = 1;", Language.TYPESCRIPT
    )
    assert isinstance(concepts, dict)


def test_parse_source_go(scanner):
    concepts = scanner.parse_source(
        "package main\nfunc main() {\n\tprintln(\"hello\")\n}", Language.GO
    )
    assert "function_def" in concepts


def test_parse_source_rust(scanner):
    concepts = scanner.parse_source(
        "fn main() { let x = 42; }", Language.RUST
    )
    assert "function_def" in concepts


def test_parse_source_java(scanner):
    concepts = scanner.parse_source(
        "class A { void m() {} }", Language.JAVA
    )
    assert "class_basic" in concepts
    assert "function_def" in concepts
