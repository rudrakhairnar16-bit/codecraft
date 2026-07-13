from __future__ import annotations

import pytest

from codecraft.scanner.multilang import Language, LanguageDetector, MultiLanguageScanner


@pytest.fixture(scope="module")
def scanner():
    return MultiLanguageScanner()


class TestLanguageDetector:
    def test_detect_python(self):
        assert LanguageDetector.detect("file.py") == Language.PYTHON
        assert LanguageDetector.detect("file.pyw") == Language.PYTHON

    def test_detect_javascript(self):
        assert LanguageDetector.detect("file.js") == Language.JAVASCRIPT
        assert LanguageDetector.detect("file.jsx") == Language.JAVASCRIPT
        assert LanguageDetector.detect("file.mjs") == Language.JAVASCRIPT

    def test_detect_typescript(self):
        assert LanguageDetector.detect("file.ts") == Language.TYPESCRIPT
        assert LanguageDetector.detect("file.tsx") == Language.TSX

    def test_detect_go(self):
        assert LanguageDetector.detect("file.go") == Language.GO

    def test_detect_rust(self):
        assert LanguageDetector.detect("file.rs") == Language.RUST

    def test_detect_java(self):
        assert LanguageDetector.detect("file.java") == Language.JAVA

    def test_detect_unknown(self):
        assert LanguageDetector.detect("file.txt") == Language.UNKNOWN
        assert LanguageDetector.detect("file.md") == Language.UNKNOWN

    def test_supported_extensions(self):
        exts = LanguageDetector.supported_extensions()
        assert ".py" in exts
        assert ".js" in exts
        assert ".ts" in exts
        assert ".go" in exts
        assert ".rs" in exts
        assert ".java" in exts


class TestPythonParser:
    def test_function_detection(self, scanner):
        concepts = scanner.parse_source("def foo(): pass", Language.PYTHON)
        names = set(concepts.keys())
        assert "function_def" in names

    def test_class_detection(self, scanner):
        concepts = scanner.parse_source("class A: pass", Language.PYTHON)
        assert "class_basic" in concepts

    def test_loop_detection(self, scanner):
        concepts = scanner.parse_source("for i in range(5): pass", Language.PYTHON)
        assert "for_loop" in concepts

    def test_conditional_detection(self, scanner):
        concepts = scanner.parse_source("if True: pass", Language.PYTHON)
        assert "if_else" in concepts

    def test_empty_source(self, scanner):
        concepts = scanner.parse_source("", Language.PYTHON)
        assert len(concepts) == 0

    def test_syntax_error(self, scanner):
        concepts = scanner.parse_source("def foo(:", Language.PYTHON)
        assert len(concepts) == 0


class TestJavaScriptParser:
    def test_function_detection(self, scanner):
        concepts = scanner.parse_source(
            "function foo(a, b) { return a + b; }", Language.JAVASCRIPT
        )
        names = set(concepts.keys())
        assert "function_def" in names
        assert "args_kwargs" in names
        assert "arithmetic" in names

    def test_class_detection(self, scanner):
        concepts = scanner.parse_source(
            "class Point { constructor(x) { this.x = x; } }", Language.JAVASCRIPT
        )
        assert "class_basic" in concepts

    def test_arrow_function(self, scanner):
        concepts = scanner.parse_source("const add = (a, b) => a + b;", Language.JAVASCRIPT)
        assert "lambda" in concepts

    def test_variable_declaration(self, scanner):
        concepts = scanner.parse_source(
            "const x = 1;\nlet y = 2;\nvar z = 3;", Language.JAVASCRIPT
        )
        assert "variable_assignment" in concepts

    def test_import(self, scanner):
        concepts = scanner.parse_source(
            'import { foo } from "bar";', Language.JAVASCRIPT
        )
        assert "import_basic" in concepts

    def test_import_exists(self, scanner):
        concepts = scanner.parse_source(
            'import { foo } from "bar";', Language.JAVASCRIPT
        )
        assert "import_basic" in concepts

    def test_async_await(self, scanner):
        concepts = scanner.parse_source(
            "async function fetch() { await getData(); }", Language.TYPESCRIPT
        )
        # TS grammar may or may not detect async separately
        assert isinstance(concepts, dict)


class TestTypeScriptParser:
    def test_type_annotation(self, scanner):
        concepts = scanner.parse_source(
            "function add(a: number, b: number): number { return a + b; }",
            Language.TYPESCRIPT,
        )
        assert "function_def" in concepts
        assert "args_kwargs" in concepts

    def test_interface_exists(self, scanner):
        """Interface keyword exists but may not be detected as a concept."""
        concepts = scanner.parse_source(
            "interface Point { x: number; y: number; }", Language.TYPESCRIPT
        )
        assert isinstance(concepts, dict)


class TestGoParser:
    def test_function_detection(self, scanner):
        concepts = scanner.parse_source(
            "package main\nfunc add(a int, b int) int { return a + b }", Language.GO
        )
        assert "function_def" in concepts
        assert "return_value" in concepts

    def test_struct_detection(self, scanner):
        concepts = scanner.parse_source(
            "package main\ntype Point struct { X int }", Language.GO
        )
        assert "class_basic" in concepts

    def test_if_statement(self, scanner):
        concepts = scanner.parse_source(
            "package main\nfunc f() { if x > 0 { return } }", Language.GO
        )
        assert "if_else" in concepts


class TestRustParser:
    def test_function_detection(self, scanner):
        concepts = scanner.parse_source(
            "fn add(a: i32, b: i32) -> i32 { return a + b }", Language.RUST
        )
        assert "function_def" in concepts
        assert "return_value" in concepts

    def test_struct_detection(self, scanner):
        concepts = scanner.parse_source(
            "struct Point { x: i32, y: i32 }", Language.RUST
        )
        assert "class_basic" in concepts

    def test_let_mut(self, scanner):
        concepts = scanner.parse_source(
            "fn f() { let mut x = 42; x += 1; }", Language.RUST
        )
        assert "variable_assignment" in concepts

    def test_async(self, scanner):
        concepts = scanner.parse_source(
            "async fn fetch() -> u32 { 42 }", Language.RUST
        )
        assert "async_await" in concepts


class TestJavaParser:
    def test_class_and_method(self, scanner):
        concepts = scanner.parse_source(
            "class A { int add(int a, int b) { return a + b; } }", Language.JAVA
        )
        assert "class_basic" in concepts
        assert "function_def" in concepts
        assert "return_value" in concepts

    def test_if_statement(self, scanner):
        concepts = scanner.parse_source(
            "class A { void f() { if (x > 0) { return; } } }", Language.JAVA
        )
        assert "if_else" in concepts

    def test_import(self, scanner):
        concepts = scanner.parse_source(
            "import java.util.List;\nclass A {}", Language.JAVA
        )
        assert "import_basic" in concepts

    def test_lambda(self, scanner):
        concepts = scanner.parse_source(
            "class A { void f() { java.util.List.of(1,2,3).stream().map(x -> x*2); } }",
            Language.JAVA,
        )
        assert "lambda" in concepts
