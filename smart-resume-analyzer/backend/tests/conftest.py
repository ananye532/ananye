import io
import os
import tempfile

# Configure the app before it is imported: an isolated SQLite DB and small limits.
_DB_DIR = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_DB_DIR}/test.db"
os.environ["MAX_UPLOAD_MB"] = "1"
os.environ["MAX_PDF_PAGES"] = "3"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from reportlab.lib.pagesizes import LETTER  # noqa: E402
from reportlab.pdfgen import canvas  # noqa: E402

from app.db import Base, engine  # noqa: E402
from app.main import app  # noqa: E402

RESUME_TEXT = """Jane Doe
jane.doe@example.com | +1 555 123 4567 | linkedin.com/in/janedoe
Summary
Backend engineer with 5 years of experience building REST APIs in Python.
Experience
Senior Software Engineer, Acme Corp, London 2021 - Present
Built FastAPI microservices on AWS serving 2M users and cut p95 latency by 40%.
Led a team of 4 engineers and introduced CI/CD with GitHub Actions and Docker.
Designed PostgreSQL schemas and Redis caching for a payments platform.
Software Engineer, Beta Ltd 2018 - 2021
Developed data pipelines with pandas and Apache Airflow processing 500 GB daily.
Education
BSc Computer Science, University of Leeds, 2018
Skills
Python, Go, PostgreSQL, Redis, Docker, Kubernetes, Git, pytest
"""

JOB_TEXT = """Senior Backend Engineer
We are looking for a backend engineer with strong Python and FastAPI experience.
You will design REST APIs, work with PostgreSQL and Kafka, and deploy services on Kubernetes using Terraform.
Experience with machine learning pipelines is a plus.
Excellent communication skills and experience mentoring engineers are required.
"""


def make_pdf(text: str = RESUME_TEXT, pages: int = 1, encrypt: str | None = None) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=LETTER, encrypt=encrypt)
    for _ in range(pages):
        y = 750
        for line in text.split("\n"):
            c.drawString(50, y, line)
            y -= 14
        c.showPage()
    c.save()
    return buf.getvalue()


def make_blank_pdf() -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    c.rect(100, 100, 200, 200)  # a drawing with no text, like a scanned image
    c.showPage()
    c.save()
    return buf.getvalue()


@pytest.fixture(autouse=True)
def _fresh_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth(client):
    def _register(email: str = "jane@example.com") -> dict:
        r = client.post("/api/users", json={"email": email})
        assert r.status_code == 201, r.text
        return {"X-API-Key": r.json()["api_key"]}

    return _register
