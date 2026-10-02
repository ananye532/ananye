"""ORM tables. See docs/ARCHITECTURE.md §3."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Index, Integer, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base

# JSONB on PostgreSQL, generic JSON elsewhere (SQLite in tests).
JSONType = JSON().with_variant(JSONB(), "postgresql")


def _now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    api_key_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, nullable=False)

    resumes: Mapped[list[Resume]] = relationship(back_populates="user", cascade="all, delete-orphan", passive_deletes=True)
    jobs: Mapped[list[Job]] = relationship(back_populates="user", cascade="all, delete-orphan", passive_deletes=True)
    analyses: Mapped[list[Analysis]] = relationship(cascade="all, delete-orphan", passive_deletes=True)


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    page_count: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    sections: Mapped[dict] = mapped_column(JSONType, nullable=False)
    skills: Mapped[list] = mapped_column(JSONType, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, nullable=False)

    user: Mapped[User] = relationship(back_populates="resumes")
    analyses: Mapped[list[Analysis]] = relationship(back_populates="resume", cascade="all, delete-orphan", passive_deletes=True)


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    company: Mapped[str | None] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, nullable=False)
    skills: Mapped[list] = mapped_column(JSONType, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, nullable=False)

    user: Mapped[User] = relationship(back_populates="jobs")
    analyses: Mapped[list[Analysis]] = relationship(back_populates="job", cascade="all, delete-orphan", passive_deletes=True)


class Analysis(Base):
    __tablename__ = "analyses"
    __table_args__ = (Index("ix_analyses_resume_job", "resume_id", "job_id"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    resume_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    skill_coverage: Mapped[float | None] = mapped_column(Float)
    keyword_coverage: Mapped[float | None] = mapped_column(Float)
    cosine_similarity: Mapped[float] = mapped_column(Float, nullable=False)
    taxonomy_version: Mapped[str] = mapped_column(String(32), nullable=False)
    result: Mapped[dict] = mapped_column(JSONType, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, nullable=False)

    resume: Mapped[Resume] = relationship(back_populates="analyses")
    job: Mapped[Job] = relationship(back_populates="analyses")
