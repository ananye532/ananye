from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints


class UserCreate(BaseModel):
    email: EmailStr


class UserCreated(BaseModel):
    id: uuid.UUID
    email: str
    api_key: str = Field(description="Shown once. Only a hash is stored; it cannot be recovered.")


class ResumeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    filename: str
    page_count: int
    word_count: int
    sections: dict[str, Any]
    skills: list[dict[str, Any]]
    text_preview: str
    created_at: datetime


class JobCreate(BaseModel):
    # Whitespace is stripped before the length check, so "   " is rejected.
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
    company: Annotated[str, StringConstraints(strip_whitespace=True, max_length=200)] | None = None
    description: str


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    company: str | None
    skills: list[dict[str, Any]]
    created_at: datetime


class AnalysisCreate(BaseModel):
    resume_id: uuid.UUID
    job_id: uuid.UUID


class AnalysisOut(BaseModel):
    id: uuid.UUID
    resume_id: uuid.UUID
    job_id: uuid.UUID
    created_at: datetime
    result: dict[str, Any]


class ErrorOut(BaseModel):
    detail: str
    code: str | None = None
