from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def _now() -> datetime:
    return datetime.now(UTC)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(255))
    headline: Mapped[str | None] = mapped_column(String(200))
    target_role: Mapped[str | None] = mapped_column(String(120))
    preferences: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    resumes: Mapped[list[Resume]] = relationship(back_populates="user", cascade="all, delete-orphan", passive_deletes=True)
    analyses: Mapped[list[Analysis]] = relationship(back_populates="user", cascade="all, delete-orphan", passive_deletes=True)


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    source: Mapped[str] = mapped_column(String(20))  # pdf | docx | txt | paste
    filename: Mapped[str | None] = mapped_column(String(255))
    text: Mapped[str] = mapped_column(Text)
    page_count: Mapped[int | None] = mapped_column(Integer)
    parsed: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    user: Mapped[User] = relationship(back_populates="resumes")
    analyses: Mapped[list[Analysis]] = relationship(back_populates="resume", cascade="all, delete-orphan", passive_deletes=True)


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id", ondelete="CASCADE"), index=True)
    job_title: Mapped[str | None] = mapped_column(String(200))
    job_description: Mapped[str | None] = mapped_column(Text)
    target_role: Mapped[str | None] = mapped_column(String(120))
    overall_score: Mapped[int] = mapped_column(Integer)
    ats_score: Mapped[int] = mapped_column(Integer)
    match_score: Mapped[int | None] = mapped_column(Integer)
    result: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)

    user: Mapped[User] = relationship(back_populates="analyses")
    resume: Mapped[Resume] = relationship(back_populates="analyses")
