from __future__ import annotations

from functools import lru_cache

from ..core.config import get_settings
from .base import AIProvider
from .deterministic import DeterministicProvider


@lru_cache
def get_provider() -> AIProvider:
    s = get_settings()
    if s.ai_provider == "anthropic":
        from .anthropic_provider import AnthropicProvider

        provider = AnthropicProvider(s.anthropic_api_key, s.anthropic_model, s.ai_timeout_seconds)
        if provider.available:
            return provider
    return DeterministicProvider()
