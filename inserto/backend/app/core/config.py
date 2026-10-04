"""Application settings, loaded from environment variables (prefix-free) or a .env file."""

from __future__ import annotations

from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Inserto"
    environment: str = "development"

    # Database. DATABASE_URL wins; otherwise POSTGRES_* parts; otherwise local SQLite.
    database_url: str | None = None
    postgres_host: str | None = None
    postgres_port: int = 5432
    postgres_user: str = "inserto"
    postgres_password: str = ""
    postgres_db: str = "inserto"

    # Auth
    jwt_secret: str = Field(default="dev-only-change-me-0123456789abcdef", min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60 * 24 * 7

    # Uploads
    max_upload_bytes: int = 5 * 1024 * 1024
    max_pdf_pages: int = 10
    max_text_chars: int = 60_000

    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # AI provider: "none" (deterministic only) or "anthropic".
    ai_provider: str = "none"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-opus-5-5"
    ai_timeout_seconds: float = 60.0

    @property
    def sqlalchemy_url(self) -> str:
        if self.database_url:
            return self.database_url
        if self.postgres_host:
            return (
                f"postgresql+psycopg2://{quote_plus(self.postgres_user)}:{quote_plus(self.postgres_password)}"
                f"@{self.postgres_host}:{self.postgres_port}/{quote_plus(self.postgres_db)}"
            )
        return "sqlite:///./inserto.db"


@lru_cache
def get_settings() -> Settings:
    return Settings()
