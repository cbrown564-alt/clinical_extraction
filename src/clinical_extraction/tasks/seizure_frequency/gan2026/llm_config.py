"""Shared LLM runtime configuration for Gan 2026 experiments."""

from __future__ import annotations

from typing import Any

import dspy


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
    if api_base:
        kwargs["api_base"] = api_base
    return dspy.LM(model, **kwargs)
