"""Persistent interaction storage for Jarvis memory."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class InteractionDatabase:
    """Store interactions in SQLite by default or PostgreSQL when configured."""

    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        self._is_sqlite = database_url.startswith("sqlite:///")
        self._initialize()

    def _connect(self):
        if self._is_sqlite:
            path = Path(self.database_url.removeprefix("sqlite:///"))
            path.parent.mkdir(parents=True, exist_ok=True)
            connection = sqlite3.connect(path)
            connection.row_factory = sqlite3.Row
            return connection
        import psycopg
        from psycopg.rows import dict_row

        return psycopg.connect(self.database_url, row_factory=dict_row)

    @contextmanager
    def _connection(self):
        connection = self._connect()
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def _initialize(self) -> None:
        id_column = "INTEGER PRIMARY KEY AUTOINCREMENT" if self._is_sqlite else "BIGSERIAL PRIMARY KEY"
        timestamp_column = "TEXT" if self._is_sqlite else "TIMESTAMPTZ"
        with self._connection() as connection:
            connection.execute(
                f"""
                CREATE TABLE IF NOT EXISTS interactions (
                    id {id_column},
                    created_at {timestamp_column} NOT NULL,
                    input_text TEXT NOT NULL,
                    output_text TEXT NOT NULL,
                    action TEXT NOT NULL,
                    emotion TEXT NOT NULL,
                    input_audio_path TEXT,
                    output_audio_path TEXT
                )
                """
            )

    def record(
        self,
        input_text: str,
        output_text: str,
        action: str,
        emotion: str,
        input_audio_path: str | None = None,
        output_audio_path: str | None = None,
    ) -> None:
        placeholder = "?" if self._is_sqlite else "%s"
        values = (
            datetime.now(timezone.utc).isoformat() if self._is_sqlite else datetime.now(timezone.utc),
            input_text,
            output_text,
            action,
            emotion,
            input_audio_path,
            output_audio_path,
        )
        with self._connection() as connection:
            connection.execute(
                f"""
                INSERT INTO interactions
                (created_at, input_text, output_text, action, emotion, input_audio_path, output_audio_path)
                VALUES ({", ".join([placeholder] * len(values))})
                """,
                values,
            )

    def recent_interactions(self, limit: int = 6) -> list[dict[str, Any]]:
        """Return the latest turns in chronological order for LLM context."""
        limit = max(1, min(limit, 20))
        placeholder = "?" if self._is_sqlite else "%s"
        with self._connection() as connection:
            cursor = connection.execute(
                f"""
                SELECT input_text, output_text, action, emotion
                FROM interactions
                ORDER BY id DESC
                LIMIT {placeholder}
                """,
                (limit,),
            )
            rows = [dict(row) for row in cursor.fetchall()]
        return list(reversed(rows))
