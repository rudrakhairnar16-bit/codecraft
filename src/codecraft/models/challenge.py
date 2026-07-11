from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


class ChallengeType:
    REFACTOR = "refactor"
    FILL_BLANK = "fill_blank"
    SPOT_BUG = "spot_bug"
    TRANSFER = "transfer"
    REVIEW = "review"


@dataclass
class Challenge:
    id: str
    challenge_type: str
    concept_name: str
    title: str
    description: str
    code_snippet: str
    expected_solution: str
    hints: list[str] = field(default_factory=list)
    domain: str = "general"
    difficulty: int = 1
    source_file: str | None = None


@dataclass
class ChallengeResult:
    challenge_id: str
    correct: bool
    hints_used: int
    time_taken_seconds: int
    attempted_at: datetime = field(default_factory=datetime.now)
