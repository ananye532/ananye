"""Request/response models for the HTTP API."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterIn(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("name")
    @classmethod
    def _strip(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name is required")
        return v


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class Preferences(BaseModel):
    ai_enhancement: bool = True
    default_target_role: str | None = None
    email_digest: bool = False
    theme: Literal["system", "light", "dark"] = "system"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    headline: str | None
    target_role: str | None
    preferences: Preferences
    created_at: datetime

    @field_validator("preferences", mode="before")
    @classmethod
    def _prefs(cls, v: Any) -> Any:
        return v or {}


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class ProfileUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    headline: str | None = Field(default=None, max_length=200)
    target_role: str | None = Field(default=None, max_length=120)


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class ResumeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    source: str
    filename: str | None
    page_count: int | None
    created_at: datetime
    word_count: int = 0
    latest_score: int | None = None
    analysis_count: int = 0


class ResumeDetail(ResumeOut):
    text: str
    parsed: dict[str, Any]


class PasteIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    text: str = Field(min_length=1, max_length=60_000)


class AnalyzeIn(BaseModel):
    resume_id: int
    job_title: str | None = Field(default=None, max_length=200)
    job_description: str | None = Field(default=None, max_length=20_000)
    target_role: str | None = Field(default=None, max_length=120)
    use_ai: bool = True


class AnalysisSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resume_id: int
    resume_title: str
    job_title: str | None
    target_role: str | None
    overall_score: int
    ats_score: int
    match_score: int | None
    created_at: datetime


class AnalysisOut(AnalysisSummary):
    result: dict[str, Any]
    job_description: str | None


class RewriteIn(BaseModel):
    bullet: str = Field(min_length=3, max_length=600)
    context: str | None = Field(default=None, max_length=4000)


class RewriteOut(BaseModel):
    provider: str
    options: list[str]


class CompareIn(BaseModel):
    a: int
    b: int


class DashboardOut(BaseModel):
    resume_count: int
    analysis_count: int
    best_score: int | None
    latest: AnalysisSummary | None
    trend: list[dict[str, Any]]
    recent: list[AnalysisSummary]
    top_recommendations: list[dict[str, Any]]


class MetaOut(BaseModel):
    roles: list[str]
    ai_provider: str
    ai_available: bool
    engine_version: str


class RenameIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
