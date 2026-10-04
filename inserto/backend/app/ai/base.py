"""Provider-agnostic interface for optional LLM enhancement.

The deterministic engine always runs first and is the source of truth for scores.
A provider may only *add* narrative (recruiter feedback, rewrite suggestions,
career insights). It never changes numeric scores, so results stay reproducible.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, Field


class AIRewrite(BaseModel):
    original: str
    improved: str
    rationale: str


class AIEnhancement(BaseModel):
    first_impression: str | None = None
    strengths: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)
    rewrites: list[AIRewrite] = Field(default_factory=list)
    career_advice: list[str] = Field(default_factory=list)


class AIProviderError(RuntimeError):
    pass


class AIProvider(ABC):
    """Implement this to plug in any LLM backend."""

    name: str = "base"

    @property
    @abstractmethod
    def available(self) -> bool:
        """True when the provider is configured and can be called."""

    @abstractmethod
    def enhance(self, resume_text: str, analysis: dict, job_description: str | None) -> AIEnhancement | None:
        """Return narrative additions for an analysis, or None when there is nothing to add."""

    @abstractmethod
    def rewrite_bullet(self, bullet: str, context: str | None) -> list[str]:
        """Return up to three improved versions of one bullet. Must not invent metrics."""
