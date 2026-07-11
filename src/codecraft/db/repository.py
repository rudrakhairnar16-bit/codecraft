from __future__ import annotations

from datetime import datetime
from pathlib import Path

import duckdb

from codecraft.models.challenge import ChallengeResult
from codecraft.models.debt import DebtItem
from codecraft.models.file import FileConcept, FileRecord
from codecraft.models.review import SpacedRepetitionCard


class Repository:
    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self.conn = conn

    def upsert_file(self, record: FileRecord) -> None:
        self.conn.execute(
            """
            INSERT INTO files (path, hash, size, lines, first_scanned, last_modified, last_scanned, complexity, import_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (path) DO UPDATE SET
                hash = EXCLUDED.hash,
                size = EXCLUDED.size,
                lines = EXCLUDED.lines,
                last_modified = EXCLUDED.last_modified,
                last_scanned = EXCLUDED.last_scanned,
                complexity = EXCLUDED.complexity,
                import_count = EXCLUDED.import_count
            """,
            [
                str(record.path),
                record.hash,
                record.size,
                record.lines,
                record.first_scanned,
                record.last_modified,
                record.last_scanned,
                record.complexity,
                record.import_count,
            ],
        )

    def get_file(self, path: Path) -> FileRecord | None:
        row = self.conn.execute(
            "SELECT * FROM files WHERE path = ?", [str(path)]
        ).fetchone()
        if row is None:
            return None
        return FileRecord(
            path=Path(row[0]),
            hash=row[1],
            size=row[2],
            lines=row[3],
            first_scanned=row[4],
            last_modified=row[5],
            last_scanned=row[6],
            complexity=row[7],
            import_count=row[8],
        )

    def get_all_files(self) -> list[FileRecord]:
        rows = self.conn.execute("SELECT * FROM files ORDER BY path").fetchall()
        return [
            FileRecord(
                path=Path(r[0]),
                hash=r[1],
                size=r[2],
                lines=r[3],
                first_scanned=r[4],
                last_modified=r[5],
                last_scanned=r[6],
                complexity=r[7],
                import_count=r[8],
            )
            for r in rows
        ]

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

    def get_all_concept_names(self) -> list[str]:
        rows = self.conn.execute(
            "SELECT DISTINCT concept_name FROM file_concepts ORDER BY concept_name"
        ).fetchall()
        return [r[0] for r in rows]

    def get_last_usage(self, concept_name: str) -> datetime | None:
        row = self.conn.execute(
            "SELECT MAX(last_seen) FROM file_concepts WHERE concept_name = ?",
            [concept_name],
        ).fetchone()
        return row[0] if row[0] else None

    def get_exposure_count(self, concept_name: str) -> int:
        row = self.conn.execute(
            "SELECT SUM(occurrences) FROM file_concepts WHERE concept_name = ?",
            [concept_name],
        ).fetchone()
        return row[0] if row[0] else 0

    def insert_debt_item(self, item: DebtItem) -> None:
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

    def resolve_debt_item(self, item_id: int) -> None:
        self.conn.execute(
            "UPDATE debt_items SET resolved = TRUE, resolved_at = ? WHERE id = ?",
            [datetime.now(), item_id],
        )

    def get_unresolved_debt(self) -> list[DebtItem]:
        rows = self.conn.execute(
            "SELECT * FROM debt_items WHERE resolved = FALSE ORDER BY difficulty DESC"
        ).fetchall()
        return [self._row_to_debt_item(r) for r in rows]

    def get_all_debt_items(self) -> list[DebtItem]:
        rows = self.conn.execute(
            "SELECT * FROM debt_items ORDER BY created DESC"
        ).fetchall()
        return [self._row_to_debt_item(r) for r in rows]

    def _row_to_debt_item(self, row) -> DebtItem:
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

    def insert_challenge_result(self, result: ChallengeResult) -> None:
        self.conn.execute(
            """
            INSERT INTO challenge_history (challenge_type, concept_name, correct, hints_used, time_taken_seconds, domain)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                result.challenge_id,
                "",
                result.correct,
                result.hints_used,
                result.time_taken_seconds,
                "general",
            ],
        )

    def get_challenge_history(
        self, concept_name: str, limit: int = 20
    ) -> list[dict]:
        rows = self.conn.execute(
            """
            SELECT correct, hints_used, time_taken_seconds, created
            FROM challenge_history
            WHERE concept_name = ?
            ORDER BY created DESC
            LIMIT ?
            """,
            [concept_name, limit],
        ).fetchall()
        return [
            {
                "correct": r[0],
                "hints_used": r[1],
                "time_taken": r[2],
                "created": r[3],
            }
            for r in rows
        ]

    def upsert_card(self, card: SpacedRepetitionCard) -> None:
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

    def get_card(self, concept_name: str) -> SpacedRepetitionCard | None:
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

    def get_all_cards(self) -> list[SpacedRepetitionCard]:
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

    def get_concept_timeline(self, concept_name: str) -> list[dict]:
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
