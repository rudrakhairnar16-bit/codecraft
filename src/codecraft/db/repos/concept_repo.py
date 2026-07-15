from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import duckdb

from codecraft.models.file import FileConcept


class ConceptRepo:
    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self.conn = conn

    def upsert_file_concepts(
        self, file_path: Path, concepts: dict[str, FileConcept]
    ) -> None:
        for name, fc in concepts.items():
            self.conn.execute(
                """
                INSERT INTO file_concepts (file_path, concept_name, occurrences, first_seen, last_seen)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT (file_path, concept_name) DO UPDATE SET
                    occurrences = EXCLUDED.occurrences,
                    last_seen = EXCLUDED.last_seen
                """,
                [str(file_path), name, fc.occurrences, fc.first_seen, fc.last_seen],
            )

    def get_file_concepts(self, file_path: Path) -> dict[str, FileConcept]:
        rows = self.conn.execute(
            "SELECT concept_name, occurrences, first_seen, last_seen FROM file_concepts WHERE file_path = ?",
            [str(file_path)],
        ).fetchall()
        return {
            r[0]: FileConcept(
                concept_name=r[0],
                occurrences=r[1],
                first_seen=r[2],
                last_seen=r[3],
            )
            for r in rows
        }

    def get_all_names(self) -> list[str]:
        rows = self.conn.execute(
            "SELECT DISTINCT concept_name FROM file_concepts ORDER BY concept_name"
        ).fetchall()
        return [r[0] for r in rows]

    def get_last_usage(self, concept_name: str) -> datetime | None:
        row = self.conn.execute(
            "SELECT MAX(last_seen) FROM file_concepts WHERE concept_name = ?",
            [concept_name],
        ).fetchone()
        return row[0] if row is not None and row[0] is not None else None

    def get_exposure_count(self, concept_name: str) -> int:
        row = self.conn.execute(
            "SELECT SUM(occurrences) FROM file_concepts WHERE concept_name = ?",
            [concept_name],
        ).fetchone()
        return row[0] if row is not None and row[0] is not None else 0

    def get_timeline(self, concept_name: str) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT f.path, fc.occurrences, fc.first_seen, fc.last_seen
            FROM file_concepts fc
            JOIN files f ON f.path = fc.file_path
            WHERE fc.concept_name = ?
            ORDER BY fc.last_seen DESC
            """,
            [concept_name],
        ).fetchall()
        return [
            {
                "file": r[0],
                "occurrences": r[1],
                "first_seen": r[2],
                "last_seen": r[3],
            }
            for r in rows
        ]
