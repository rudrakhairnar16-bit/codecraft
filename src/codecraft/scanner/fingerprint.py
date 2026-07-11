from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


@dataclass
class FileFingerprint:
    path: Path
    hash: str
    size: int
    lines: int
    concepts: Dict[str, int]
    debt_patterns: List[str]
    complexity: float
    imports: List[str]
    import_count: int
    has_main_guard: bool
    has_docstring: bool
    function_count: int
    class_count: int
    avg_function_length: float
