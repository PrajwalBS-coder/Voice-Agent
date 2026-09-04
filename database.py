"""PostgreSQL persistence for Jarvis interactions."""

from datetime import datetime, timezone


class InteractionDatabase:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        self._initialize()

    def _connect(self):
        import psycopg

        return psycopg.connect(self.database_url)

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS interactions (
                    id BIGSERIAL PRIMARY KEY,
                    created_at TIMESTAMPTZ NOT NULL,
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
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO interactions
                (created_at, input_text, output_text, action, emotion, input_audio_path, output_audio_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    datetime.now(timezone.utc),
                    input_text,
                    output_text,
                    action,
                    emotion,
                    input_audio_path,
                    output_audio_path,
                ),
            )

