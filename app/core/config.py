from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):

    gemini_api_key: str

    small_model: str = "gemini-3.5-flash-lite"
    large_model: str = "gemini-3.8-flash"
    fallback_model: str = "gemini-3.7-flash"

    embedding_model: str = "gemini-embedding-2-preview"

    cache_threshold: float = 0.88

    database_path: str = str(
        BASE_DIR / "metrics.db"
    )

    documents_path: str = str(
        BASE_DIR / "data" / "documents.txt"
    )

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()