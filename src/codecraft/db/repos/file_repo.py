from __future__ import annotations

from pathlib import Path
from typing import Any

import duckdb

from codecraft.models.file import FileConcept, FileRecord


class FileRepo:
    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self.conn = conn

    def upsert(self, record: FileRecord) -> None:
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

    def get(self, path: Path) -> FileRecord | None:
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

    def get_all(self) -> list[FileRecord]:
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
