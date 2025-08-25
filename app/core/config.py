from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration loaded from environment variables (.env)."""

    # SQLAlchemy URL (SQLite by default for local/dev)
    DATABASE_URL: str = "sqlite:///./health.db"

    # External FHIR server base URL (demo)
    EXTERNAL_FHIR_BASE_URL: str = "https://hapi.fhir.org/baseR4"

    # Load from .env (case-insensitive keys)
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance so we don't parse .env repeatedly."""
    return Settings()
