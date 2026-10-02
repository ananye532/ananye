from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL, make_url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Either a full DATABASE_URL, or the POSTGRES_* parts (preferred in Docker:
    # the password is escaped properly even if it contains @ : / # etc.).
    database_url: str | None = None
    postgres_host: str | None = None
    postgres_port: int = 5432
    postgres_user: str = "resume_analyzer"
    postgres_password: str = ""
    postgres_db: str = "resume_analyzer"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:8080"]
    max_upload_mb: float = 5.0
    max_pdf_pages: int = 10
    min_job_chars: int = 50
    max_job_chars: int = 20_000
    top_n_keywords: int = 25

    @property
    def sqlalchemy_url(self) -> URL:
        if self.database_url:
            return make_url(self.database_url)
        if self.postgres_host:
            return URL.create(
                "postgresql+psycopg2",
                username=self.postgres_user,
                password=self.postgres_password,
                host=self.postgres_host,
                port=self.postgres_port,
                database=self.postgres_db,
            )
        return make_url("sqlite:///./dev.db")

    @property
    def max_upload_bytes(self) -> int:
        return int(self.max_upload_mb * 1024 * 1024)


@lru_cache
def get_settings() -> Settings:
    return Settings()
