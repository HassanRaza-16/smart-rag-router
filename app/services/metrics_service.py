import sqlite3
from datetime import datetime

from app.core.config import Settings


class MetricsService:

    def __init__(
        self,
        settings: Settings,
    ):

        self.database_path = (
            settings.database_path
        )

        self._initialize_database()

    def _connection(self):
        return sqlite3.connect(
            self.database_path
        )

    def _initialize_database(self):

        with self._connection() as connection:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    query TEXT,
                    model TEXT,
                    cache_hit INTEGER,
                    latency_ms REAL,
                    estimated_cost REAL
                )
                """
            )

    def record(
        self,
        query: str,
        model: str,
        cache_hit: bool,
        latency_ms: float,
        estimated_cost: float,
    ):

        with self._connection() as connection:

            connection.execute(
                """
                INSERT INTO requests
                (
                    timestamp,
                    query,
                    model,
                    cache_hit,
                    latency_ms,
                    estimated_cost
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.utcnow().isoformat(),
                    query,
                    model,
                    int(cache_hit),
                    latency_ms,
                    estimated_cost,
                ),
            )

    def get_all(self):

        with self._connection() as connection:

            return connection.execute(
                """
                SELECT *
                FROM requests
                ORDER BY id DESC
                """
            ).fetchall()