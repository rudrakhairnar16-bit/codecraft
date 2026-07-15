from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import duckdb

from codecraft.models.challenge import ChallengeResult


class ChallengeRepo:
    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self.conn = conn

    def insert(self, result: ChallengeResult) -> None:
        self.conn.execute(
            """
            INSERT INTO challenge_history (challenge_type, concept_name, correct, hints_used, time_taken_seconds, domain)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                result.challenge_type,
                result.concept_name or "",
                result.correct,
                result.hints_used,
                result.time_taken_seconds,
                result.domain or "general",
            ],
        )

    def get_history(
        self, concept_name: str | None = None, limit: int = 50
    ) -> list[dict[str, Any]]:
        if concept_name:
            rows = self.conn.execute(
                """
                SELECT challenge_type, concept_name, correct, hints_used, time_taken_seconds, domain, created
                FROM challenge_history
                WHERE concept_name = ?
                ORDER BY created DESC
                LIMIT ?
                """,
                [concept_name, limit],
            ).fetchall()
        else:
            rows = self.conn.execute(
                """
                SELECT challenge_type, concept_name, correct, hints_used, time_taken_seconds, domain, created
                FROM challenge_history
                ORDER BY created DESC
                LIMIT ?
                """,
                [limit],
            ).fetchall()
        return [
            {
                "challenge_type": r[0],
                "concept_name": r[1],
                "correct": r[2],
                "hints_used": r[3],
                "time_taken": r[4],
                "domain": r[5],
                "created": r[6],
            }
            for r in rows
        ]

    def get_stats(self) -> dict[str, Any]:
        rows = self.conn.execute(
            """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN correct THEN 1 ELSE 0 END) as correct,
                AVG(time_taken_seconds) as avg_time,
                COUNT(DISTINCT concept_name) as unique_concepts,
                COUNT(DISTINCT domain) as unique_domains
            FROM challenge_history
            """,
        ).fetchone()
        assert rows is not None
        return {
            "total_sessions": rows[0] or 0,
            "correct_sessions": rows[1] or 0,
            "avg_time_seconds": round(rows[2] or 0),
            "unique_concepts": rows[3] or 0,
            "unique_domains": rows[4] or 0,
        }

    def get_streak(self) -> dict[str, Any]:
        rows = self.conn.execute(
            """
            SELECT DISTINCT DATE(created) as day
            FROM challenge_history
            ORDER BY day DESC
            """,
        ).fetchall()
        days = [r[0] for r in rows]
        streak = 0
        today = date.today()
        for i, d in enumerate(days):
            expected = today - timedelta(days=i)
            if d == expected:
                streak += 1
            else:
                break
        return {"current_streak": streak, "total_active_days": len(days)}
