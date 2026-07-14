from __future__ import annotations

from pathlib import Path

import pytest

from codecraft.scanner.ast_parser import (
    ASTParseError,
    file_hash,
    file_stats,
    get_node_name,
    get_source_segment,
    parse_file,
    parse_source,
)


def test_parse_source_valid():
    tree = parse_source("x = 1")
    assert tree is not None


def test_parse_source_syntax_error():
    with pytest.raises(ASTParseError):
        parse_source("def foo(:")


def test_parse_file_valid(tmp_path):
    f = tmp_path / "test.py"
    f.write_text("x = 1")
    tree = parse_file(f)
    assert tree is not None


def test_parse_file_syntax_error(tmp_path):
    f = tmp_path / "bad.py"
    f.write_text("def foo(:")
    with pytest.raises(ASTParseError):
        parse_file(f)


def test_parse_file_not_found():
    with pytest.raises(ASTParseError):
        parse_file(Path("/nonexistent/file.py"))


def test_file_hash(tmp_path):
    f = tmp_path / "test.py"
    f.write_text("x = 1")
    h = file_hash(f)
    assert isinstance(h, str)
    assert len(h) == 16


def test_file_stats(tmp_path):
    f = tmp_path / "test.py"
    f.write_text("line1\nline2\nline3\n")
    size, lines = file_stats(f)
    assert lines == 3
    assert size > 0


def test_get_node_name():
    import ast
    node = ast.Name(id="x")
    name = get_node_name(node)
    assert name == "Name"


def test_get_source_segment():
    import ast
    source = "x = 1\ny = 2\nz = 3"
    tree = ast.parse(source)
    node = tree.body[0]
    segment = get_source_segment(source, node)
    assert segment == "x = 1"


def test_get_source_segment_no_lineno():
    import ast
    source = "x = 1"
    node = ast.Name(id="x")
    segment = get_source_segment(source, node)
    assert segment == ""
