import hashlib
import json
import sqlite3
from pathlib import Path

import numpy as np

from app.core.config import Settings
from app.services.embedding_service import EmbeddingService


class RAGService:

    def __init__(
        self,
        settings: Settings,
        embedding_service: EmbeddingService,
    ):
        self.settings = settings
        self.embedding_service = embedding_service

        self.documents_path = Path(
            settings.documents_path
        )

        self._last_modified = None

        self._initialize_database()

        # Initial synchronization only.
        self.sync_documents()

        self._last_modified = (
            self.documents_path.stat().st_mtime
        )

    def _connection(self):
        return sqlite3.connect(
            self.settings.database_path
        )

    def _initialize_database(self):
        with self._connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS document_embeddings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_name TEXT UNIQUE NOT NULL,
                    content_hash TEXT NOT NULL,
                    content TEXT NOT NULL,
                    embedding TEXT NOT NULL,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def _load_documents(self):
        text = self.documents_path.read_text(
            encoding="utf-8"
        )

        documents = [
            chunk.strip()
            for chunk in text.split("\n\n")
            if chunk.strip()
        ]

        return [
            (
                f"{self.documents_path.name}:{index}",
                document,
            )
            for index, document in enumerate(documents)
        ]

    @staticmethod
    def _content_hash(content: str) -> str:
        return hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()

    def sync_documents(self):
        documents = self._load_documents()

        with self._connection() as connection:

            existing_rows = connection.execute(
                """
                SELECT
                    document_name,
                    content_hash
                FROM document_embeddings
                """
            ).fetchall()

            existing = {
                row[0]: row[1]
                for row in existing_rows
            }

            current_names = set()

            for document_name, content in documents:

                current_names.add(document_name)

                content_hash = self._content_hash(
                    content
                )

                # Unchanged → no embedding API call.
                if (
                    document_name in existing
                    and existing[document_name]
                    == content_hash
                ):
                    continue

                # New or modified → create embedding.
                embedding = (
                    self.embedding_service.embed(
                        content
                    )
                )

                connection.execute(
                    """
                    INSERT INTO document_embeddings
                    (
                        document_name,
                        content_hash,
                        content,
                        embedding
                    )
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(document_name)
                    DO UPDATE SET
                        content_hash = excluded.content_hash,
                        content = excluded.content,
                        embedding = excluded.embedding,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (
                        document_name,
                        content_hash,
                        content,
                        json.dumps(
                            embedding.tolist()
                        ),
                    ),
                )

            # Remove deleted documents.
            for document_name in existing:

                if document_name not in current_names:

                    connection.execute(
                        """
                        DELETE FROM document_embeddings
                        WHERE document_name = ?
                        """,
                        (document_name,),
                    )

    def _check_for_document_changes(self):

        current_modified = (
            self.documents_path.stat().st_mtime
        )

        if (
            self._last_modified is None
            or current_modified != self._last_modified
        ):
            self.sync_documents()

            self._last_modified = current_modified

    def retrieve(
        self,
        query_embedding: np.ndarray,
        top_k: int = 3,
    ) -> list[str]:

        # Only synchronize when the file actually changed.
        self._check_for_document_changes()

        with self._connection() as connection:

            rows = connection.execute(
                """
                SELECT
                    content,
                    embedding
                FROM document_embeddings
                """
            ).fetchall()

        scored = []

        for content, embedding_json in rows:

            document_embedding = np.array(
                json.loads(embedding_json),
                dtype=np.float32,
            )

            similarity = (
                self.embedding_service.similarity(
                    query_embedding,
                    document_embedding,
                )
            )

            scored.append(
                (similarity, content)
            )

        scored.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        return [
            content
            for _, content in scored[:top_k]
        ]