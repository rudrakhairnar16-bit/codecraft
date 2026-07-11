from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class FileFingerprint:
    path: Path
    hash: str
    size: int
    lines: int
    concepts: dict[str, int]
    debt_patterns: list[str]
    complexity: float
    imports: list[str]
    import_count: int
    has_main_guard: bool
    has_docstring: bool
    function_count: int
    class_count: int
    avg_function_length: float
