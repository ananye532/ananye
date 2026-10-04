from __future__ import annotations

import os
from pathlib import Path

import pytest

os.environ.setdefault("DATABASE_URL", os.environ.get("TEST_DATABASE_URL", "sqlite:///./test_inserto.db"))
os.environ["AI_PROVIDER"] = "none"

from fastapi.testclient import TestClient  # noqa: E402

from app.db import Base, engine  # noqa: E402
from app.main import app  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def _fresh_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def register(client: TestClient, email: str = "ada@example.com") -> dict[str, str]:
    r = client.post("/api/auth/register", json={"email": email, "name": "Ada", "password": "correct-horse"})
    assert r.status_code == 201, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def auth(client: TestClient) -> dict[str, str]:
    return register(client)


@pytest.fixture
def strong_text() -> str:
    return (FIXTURES / "strong_resume.txt").read_text()


@pytest.fixture
def weak_text() -> str:
    return (FIXTURES / "weak_resume.txt").read_text()
