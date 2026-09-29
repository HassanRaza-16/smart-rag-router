import numpy as np

from app.core.config import Settings
from app.services.gemini_service import GeminiService


class EmbeddingService:
    def __init__(
        self,
        settings: Settings,
        gemini: GeminiService,
    ):
        self.settings = settings
        self.gemini = gemini

    def embed(self, text: str) -> np.ndarray:
        response = self.gemini.client.models.embed_content(
            model=self.settings.embedding_model,
            contents=text,
        )

        vector = np.array(
            response.embeddings[0].values,
            dtype=np.float32,
        )

        return self.normalize(vector)

    @staticmethod
    def normalize(vector: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(vector)

        if norm == 0:
            return vector

        return vector / norm

    @staticmethod
    def similarity(
        first: np.ndarray,
        second: np.ndarray,
    ) -> float:
        first_norm = np.linalg.norm(first)
        second_norm = np.linalg.norm(second)

        if first_norm == 0 or second_norm == 0:
            return 0.0

        return float(
            np.dot(first, second)
            / (first_norm * second_norm)
        )