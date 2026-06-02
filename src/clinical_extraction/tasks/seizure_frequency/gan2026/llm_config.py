"""Shared LLM runtime configuration for Gan 2026 experiments."""

from __future__ import annotations

from typing import Any

import dspy

OLLAMA_CHAT_PREFIX = "ollama_chat/"


def build_dspy_lm(
    model: str,
    *,
    temperature: float,
    max_tokens: int,
    cache: bool,
    api_base: str | None = None,
    num_retries: int = 2,
) -> dspy.LM:
    """Create a DSPy LM with optional local/OpenAI-compatible endpoint routing."""

    kwargs: dict[str, Any] = {
        "temperature": temperature,
        "max_tokens": max_tokens,
        "cache": cache,
        "num_retries": num_retries,
    }
    if model.startswith(OLLAMA_CHAT_PREFIX):
        kwargs["api_base"] = (api_base or "http://localhost:11434").removesuffix("/v1")
        kwargs["extra_body"] = {"think": False}
        return dspy.LM(model, **kwargs)
    if api_base:
        kwargs["api_base"] = api_base
    return dspy.LM(model, **kwargs)
