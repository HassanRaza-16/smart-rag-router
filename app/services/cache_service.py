import json
import sqlite3

import numpy as np

from app.core.config import Settings
from app.services.embedding_service import EmbeddingService


class CacheService:
    def __init__(
        self,
        settings: Settings,
        embedding_service: EmbeddingService,
    ):
        self.settings = settings
        self.embedding_service = embedding_service

        self._initialize_database()

    def _connection(self):
        return sqlite3.connect(
            self.settings.database_path
        )

    def _initialize_database(self):
        with self._connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS semantic_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    embedding TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    model TEXT NOT NULL
                )
                """
            )

    def search(
        self,
        query_embedding: np.ndarray,
    ):
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    query,
                    embedding,
                    answer,
                    model
                FROM semantic_cache
                """
            ).fetchall()

        best_match = None
        best_similarity = 0.0

        for row in rows:
            stored_embedding = np.array(
                json.loads(row[2]),
                dtype=np.float32,
            )

            similarity = (
                self.embedding_service.similarity(
                    query_embedding,
                    stored_embedding,
                )
            )

            if similarity > best_similarity:
                best_similarity = similarity

                best_match = {
                    "query": row[1],
                    "answer": row[3],
                    "model": row[4],
                    "similarity": similarity,
                }

        if (
            best_match
            and best_similarity
            >= self.settings.cache_threshold
        ):
            return best_match

        return None

    def save(
        self,
        query: str,
        query_embedding: np.ndarray,
        answer: str,
        model: str,
    ):
        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO semantic_cache
                (query, embedding, answer, model)
                VALUES (?, ?, ?, ?)
                """,
                (
                    query,
                    json.dumps(
                        query_embedding.tolist()
                    ),
                    answer,
                    model,
                ),
            )