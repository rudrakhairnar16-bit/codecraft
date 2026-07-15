from __future__ import annotations

import duckdb


class SettingsRepo:
    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self.conn = conn

    def get(self, key: str, default: str = "") -> str:
        row = self.conn.execute(
            "SELECT value FROM settings WHERE key = ?", [key]
        ).fetchone()
        return row[0] if row else default

    def set(self, key: str, value: str) -> None:
        self.conn.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
            [key, value],
        )
