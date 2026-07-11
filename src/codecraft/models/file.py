from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List


@dataclass
class FileConcept:
    concept_name: str
    occurrences: int = 1
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)


@dataclass
class FileRecord:
    path: Path
    hash: str
    size: int
    lines: int
    first_scanned: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    last_scanned: datetime = field(default_factory=datetime.now)
    concepts: Dict[str, FileConcept] = field(default_factory=dict)
    complexity: float = 0.0
    import_count: int = 0


@dataclass
class FileReport:
    path: Path
    concepts: List[str]
    debt_items: List[str]
    complexity: float
    lines: int
    imports: List[str]
    errors: List[str] = field(default_factory=list)
