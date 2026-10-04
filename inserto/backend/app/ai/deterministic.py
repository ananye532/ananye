"""The default provider: no LLM. Uses the rule-based studio rewriter."""

from __future__ import annotations

from ..engine.studio import rewrite
from .base import AIEnhancement, AIProvider


class DeterministicProvider(AIProvider):
    name = "deterministic"

    @property
    def available(self) -> bool:
        return True

    def enhance(self, resume_text: str, analysis: dict, job_description: str | None) -> AIEnhancement | None:
        return None  # the engine's own narrative is already in the analysis

    def rewrite_bullet(self, bullet: str, context: str | None) -> list[str]:
        r = rewrite(bullet)
        return [r.improved] if r else [bullet.strip()]
