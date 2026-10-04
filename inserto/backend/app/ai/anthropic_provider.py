"""Claude implementation of AIProvider, using the official Anthropic Python SDK.

Enable with AI_PROVIDER=anthropic and ANTHROPIC_API_KEY. Output is constrained to a
JSON schema via structured outputs, then validated with Pydantic.
"""

from __future__ import annotations

import json
import logging

from .base import AIEnhancement, AIProvider, AIProviderError

log = logging.getLogger(__name__)

SYSTEM = (
    "You are an experienced technical recruiter and resume coach. You receive a resume and a deterministic "
    "analysis of it. Add concise, specific, honest feedback. Never invent employers, dates, skills or metrics: "
    "when a rewrite needs a number the resume does not contain, use a bracketed placeholder such as [X%]. "
    "Do not restate the numeric scores."
)

_ENHANCE_SCHEMA = {
    "type": "object",
    "properties": {
        "first_impression": {"type": "string"},
        "strengths": {"type": "array", "items": {"type": "string"}},
        "concerns": {"type": "array", "items": {"type": "string"}},
        "rewrites": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "original": {"type": "string"},
                    "improved": {"type": "string"},
                    "rationale": {"type": "string"},
                },
                "required": ["original", "improved", "rationale"],
                "additionalProperties": False,
            },
        },
        "career_advice": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["first_impression", "strengths", "concerns", "rewrites", "career_advice"],
    "additionalProperties": False,
}

_REWRITE_SCHEMA = {
    "type": "object",
    "properties": {"options": {"type": "array", "items": {"type": "string"}}},
    "required": ["options"],
    "additionalProperties": False,
}


class AnthropicProvider(AIProvider):
    name = "anthropic"

    def __init__(self, api_key: str | None, model: str, timeout: float):
        self._model = model
        self._client = None
        if api_key:
            try:
                import anthropic

                self._client = anthropic.Anthropic(api_key=api_key, timeout=timeout, max_retries=2)
            except ImportError:  # SDK not installed: stay unavailable
                log.warning("anthropic package not installed; AI enhancement disabled")

    @property
    def available(self) -> bool:
        return self._client is not None

    def _json_call(self, prompt: str, schema: dict, max_tokens: int) -> dict:
        if self._client is None:
            raise AIProviderError("Anthropic provider is not configured")
        import anthropic

        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=max_tokens,
                system=SYSTEM,
                messages=[{"role": "user", "content": prompt}],
                output_config={"effort": "low", "format": {"type": "json_schema", "schema": schema}},
            )
        except anthropic.APIStatusError as exc:
            raise AIProviderError(f"Anthropic API error {exc.status_code}") from exc
        except anthropic.APIConnectionError as exc:
            raise AIProviderError("Could not reach the Anthropic API") from exc
        if response.stop_reason == "refusal":
            raise AIProviderError("The model declined this request")
        text = next((b.text for b in response.content if b.type == "text"), None)
        if not text:
            raise AIProviderError("Empty model response")
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise AIProviderError("Model returned invalid JSON") from exc

    def enhance(self, resume_text: str, analysis: dict, job_description: str | None) -> AIEnhancement | None:
        brief = {
            "overall": analysis.get("overall"),
            "subscores": analysis.get("subscores"),
            "recommendations": [r["title"] for r in analysis.get("recommendations", [])][:10],
            "missing_skills": [g["name"] for g in analysis.get("skills", {}).get("missing", [])],
            "weak_bullets": [r["original"] for r in analysis.get("rewrites", [])][:6],
        }
        prompt = (
            "<resume>\n" + resume_text[:30_000] + "\n</resume>\n\n"
            + ("<job_description>\n" + job_description[:12_000] + "\n</job_description>\n\n" if job_description else "")
            + "<deterministic_analysis>\n" + json.dumps(brief) + "\n</deterministic_analysis>\n\n"
            "Return: a two-sentence first impression as a recruiter skimming for six seconds; up to 4 strengths and "
            "4 concerns, each one sentence and specific to this resume; rewrites for up to 5 of the weak bullets; "
            "and up to 4 pieces of career advice."
        )
        data = self._json_call(prompt, _ENHANCE_SCHEMA, max_tokens=4000)
        return AIEnhancement.model_validate(data)

    def rewrite_bullet(self, bullet: str, context: str | None) -> list[str]:
        prompt = (
            f"<bullet>{bullet}</bullet>\n"
            + (f"<context>{context[:4000]}</context>\n" if context else "")
            + "Write three stronger versions: action verb first, one line, outcome-focused. "
            "Keep every fact; use [placeholders] for numbers you do not know."
        )
        data = self._json_call(prompt, _REWRITE_SCHEMA, max_tokens=1000)
        return [o for o in data.get("options", []) if isinstance(o, str)][:3]
