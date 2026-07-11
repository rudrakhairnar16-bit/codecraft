from __future__ import annotations

import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from codecraft.db.repository import Repository
from codecraft.models.review import ReviewQueue, SpacedRepetitionCard


class ForgettingScheduler:
    def __init__(self, repo: Repository, decay_constant: float = 7.0):
        self.repo = repo
        self.decay_constant = decay_constant

    def _compute_strength(
        self, concept_name: str, current_time: Optional[datetime] = None
    ) -> float:
        now = current_time or datetime.now()
        last_usage = self.repo.get_last_usage(concept_name)
        exposure = self.repo.get_exposure_count(concept_name)

        if last_usage is None:
            return 1.0

        days_since = (now - last_usage).total_seconds() / 86400
        initial = min(exposure / 5.0, 1.0)
        return initial * math.exp(-days_since / self.decay_constant)

    def update_all_strengths(self) -> None:
        concepts = self.repo.get_all_concept_names()
        now = datetime.now()
        for name in concepts:
            strength = self._compute_strength(name, now)
            card = self.repo.get_card(name)
            if card:
                card.strength = strength
                self.repo.upsert_card(card)

    def get_review_queue(self, threshold: float = 0.6) -> ReviewQueue:
        self.update_all_strengths()
        cards = self.repo.get_all_cards()
        all_concepts = self.repo.get_all_concept_names()

        existing = {c.concept_name for c in cards}
        for name in all_concepts:
            if name not in existing:
                strength = self._compute_strength(name)
                card = SpacedRepetitionCard(
                    concept_name=name,
                    strength=strength,
                    next_review=datetime.now() if strength < threshold else None,
                )
                self.repo.upsert_card(card)
                cards.append(card)

        return ReviewQueue(cards=cards)

    def after_review(
        self, concept_name: str, correct: bool, time_taken: int = 0
    ) -> SpacedRepetitionCard:
        card = self.repo.get_card(concept_name)
        if card is None:
            card = SpacedRepetitionCard(concept_name=concept_name)

        now = datetime.now()

        if correct:
            card.interval_days = int(card.interval_days * card.ease_factor)
            card.ease_factor = min(card.ease_factor + 0.15, 3.0)
            card.repetitions += 1
        else:
            card.interval_days = max(1, int(card.interval_days / 2))
            card.ease_factor = max(1.3, card.ease_factor - 0.2)
            card.repetitions = max(0, card.repetitions - 1)

        card.last_review = now
        card.next_review = now + timedelta(days=card.interval_days)
        card.strength = self._compute_strength(concept_name, now)

        self.repo.upsert_card(card)
        return card

    def get_decay_report(self) -> List[dict]:
        concepts = self.repo.get_all_concept_names()
        now = datetime.now()
        report = []
        for name in concepts:
            strength = self._compute_strength(name, now)
            last_usage = self.repo.get_last_usage(name)
            exposure = self.repo.get_exposure_count(name)
            report.append(
                {
                    "concept": name,
                    "strength": round(strength, 3),
                    "exposure_count": exposure,
                    "days_since_use": (
                        (now - last_usage).days if last_usage else None
                    ),
                    "status": (
                        "decaying"
                        if strength < 0.6
                        else "stable" if strength < 0.8
                        else "fresh"
                    ),
                }
            )
        return sorted(report, key=lambda r: r["strength"])
