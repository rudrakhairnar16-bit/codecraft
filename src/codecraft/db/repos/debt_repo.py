from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import duckdb

from codecraft.models.debt import DebtItem


class DebtRepo:
    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self.conn = conn

    def insert(self, item: DebtItem) -> None:
        self.conn.execute(
            """
            INSERT INTO debt_items (file_path, pattern_type, pattern_location, old_snippet, suggestion, alternative_code, difficulty, tier_gap, resolved, created)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                str(item.file_path),
                item.pattern_type,
                item.pattern_location,
                item.old_snippet,
                item.suggestion,
                item.alternative_code,
                item.difficulty,
                item.tier_gap,
                item.resolved,
                item.created,
            ],
        )

    def resolve(self, item_id: int) -> None:
        self.conn.execute(
            "UPDATE debt_items SET resolved = TRUE, resolved_at = ? WHERE id = ?",
            [datetime.now(), item_id],
        )

    def get_unresolved(self) -> list[DebtItem]:
        rows = self.conn.execute(
            "SELECT * FROM debt_items WHERE resolved = FALSE ORDER BY difficulty DESC"
        ).fetchall()
        return [self._row_to_item(r) for r in rows]

    def get_all(self) -> list[DebtItem]:
        rows = self.conn.execute(
            "SELECT * FROM debt_items ORDER BY created DESC"
        ).fetchall()
        return [self._row_to_item(r) for r in rows]

    @staticmethod
    def _row_to_item(row: tuple[Any, ...]) -> DebtItem:
        return DebtItem(
            id=row[0],
            file_path=Path(row[1]),
            pattern_type=row[2],
            pattern_location=row[3],
            old_snippet=row[4],
            suggestion=row[5],
            alternative_code=row[6],
            difficulty=row[7],
            tier_gap=row[8],
            resolved=row[9],
            created=row[10],
            resolved_at=row[11],
        )
