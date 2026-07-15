from __future__ import annotations

from typing import Any

import duckdb

from codecraft.models.review import SpacedRepetitionCard


class CardRepo:
    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self.conn = conn

    def upsert(self, card: SpacedRepetitionCard) -> None:
        self.conn.execute(
            """
            INSERT INTO spaced_repetition (concept_name, ease_factor, interval_days, repetitions, next_review, last_review, strength)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (concept_name) DO UPDATE SET
                ease_factor = EXCLUDED.ease_factor,
                interval_days = EXCLUDED.interval_days,
                repetitions = EXCLUDED.repetitions,
                next_review = EXCLUDED.next_review,
                last_review = EXCLUDED.last_review,
                strength = EXCLUDED.strength
            """,
            [
                card.concept_name,
                card.ease_factor,
                card.interval_days,
                card.repetitions,
                card.next_review,
                card.last_review,
                card.strength,
            ],
        )

    def get(self, concept_name: str) -> SpacedRepetitionCard | None:
        row = self.conn.execute(
            "SELECT * FROM spaced_repetition WHERE concept_name = ?",
            [concept_name],
        ).fetchone()
        if row is None:
            return None
        return SpacedRepetitionCard(
            concept_name=row[0],
            ease_factor=row[1],
            interval_days=row[2],
            repetitions=row[3],
            next_review=row[4],
            last_review=row[5],
            strength=row[6],
        )

    def get_all(self) -> list[SpacedRepetitionCard]:
        rows = self.conn.execute(
            "SELECT * FROM spaced_repetition ORDER BY next_review ASC"
        ).fetchall()
        return [
            SpacedRepetitionCard(
                concept_name=r[0],
                ease_factor=r[1],
                interval_days=r[2],
                repetitions=r[3],
                next_review=r[4],
                last_review=r[5],
                strength=r[6],
            )
            for r in rows
        ]
