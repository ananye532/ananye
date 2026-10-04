from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import analyses, auth, profile, resumes
from .core.config import get_settings
from .db import Base, engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def create_app() -> FastAPI:
    settings = get_settings()
    if settings.environment == "production" and settings.jwt_secret.startswith("dev-only"):
        raise RuntimeError("Set JWT_SECRET before running in production")
    app = FastAPI(title="Inserto API", version="1.0.0", docs_url="/api/docs", openapi_url="/api/openapi.json")
    app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True,
                       allow_methods=["*"], allow_headers=["*"])
    for r in (auth.router, profile.router, resumes.router, analyses.router):
        app.include_router(r, prefix="/api")

    @app.get("/api/health", tags=["meta"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    # Tables are created on startup for simplicity. Use Alembic migrations for production schema changes.
    Base.metadata.create_all(bind=engine)
    return app


app = create_app()
