from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SpacedRepetitionCard:
    concept_name: str
    ease_factor: float = 2.5
    interval_days: int = 1
    repetitions: int = 0
    next_review: datetime | None = None
    last_review: datetime | None = None
    strength: float = 1.0

    def is_due(self, at: datetime | None = None) -> bool:
        if self.next_review is None:
            return True
        check = at or datetime.now()
        return check >= self.next_review

    @property
    def urgency(self) -> float:
        if self.next_review is None:
            return 0.0
        now = datetime.now()
        if now >= self.next_review:
            delta = now - self.next_review
            return min(delta.total_seconds() / 86400, 30.0)
        return 0.0


@dataclass
class ReviewQueue:
    cards: list[SpacedRepetitionCard] = field(default_factory=list)

    def due_cards(self) -> list[SpacedRepetitionCard]:
        return [c for c in self.cards if c.is_due()]

    def sort_by_urgency(self) -> list[SpacedRepetitionCard]:
        return sorted(self.due_cards(), key=lambda c: c.urgency, reverse=True)
