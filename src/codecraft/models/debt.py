from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class DebtItem:
    id: int | None = None
    file_path: Path | None = None
    pattern_type: str = ""
    pattern_location: str = ""
    old_snippet: str = ""
    suggestion: str = ""
    alternative_code: str = ""
    difficulty: int = 1
    tier_gap: int = 1
    resolved: bool = False
    created: datetime = field(default_factory=datetime.now)
    resolved_at: datetime | None = None


@dataclass
class DebtReport:
    total_items: int = 0
    resolved_items: int = 0
    by_type: dict[str, int] = field(default_factory=dict)
    items: list[DebtItem] = field(default_factory=list)
    score: float = 0.0

    @property
    def unresolved(self) -> list[DebtItem]:
        return [i for i in self.items if not i.resolved]

    @property
    def resolution_rate(self) -> float:
        if self.total_items == 0:
            return 1.0
        return self.resolved_items / self.total_items
