from __future__ import annotations

import ast
import hashlib
from pathlib import Path


class ASTParseError(Exception):
    pass


def parse_file(path: Path) -> ast.Module:
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(path))
        return tree
    except SyntaxError as e:
        raise ASTParseError(f"Syntax error in {path}: {e}") from e
    except Exception as e:
        raise ASTParseError(f"Failed to parse {path}: {e}") from e


def parse_source(source: str, filename: str = "<unknown>") -> ast.Module:
    try:
        return ast.parse(source, filename=filename)
    except SyntaxError as e:
        raise ASTParseError(f"Syntax error: {e}") from e


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()[:16]


def file_stats(path: Path) -> tuple[int, int]:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = len(text.splitlines())
    size = len(text.encode("utf-8"))
    return size, lines


def get_node_name(node: ast.AST) -> str:
    return type(node).__name__


def get_source_segment(source: str, node: ast.AST) -> str:
    lines = source.splitlines()
    if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
        start = node.lineno - 1
        end = node.end_lineno
        return "\n".join(lines[start:end])
    return ""
