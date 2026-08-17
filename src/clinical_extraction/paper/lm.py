"""LM construction for paper live cells."""

from __future__ import annotations

from typing import Any

import dspy

from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import (
    OPENROUTER_OPENAI_BASE,
    build_dspy_lm,
)

SOL_MODEL = "openai/gpt-5.6-sol"
SOL_REQUEST_TIMEOUT_SECONDS = 300


def gemini_api_base(api_base: str | None) -> str:
    """Resolve Gemini's OpenRouter endpoint unless a caller overrides it."""

    return api_base or OPENROUTER_OPENAI_BASE


def build_paper_lm(
    model: str,
    *,
    temperature: float,
    max_tokens: int,
    cache: bool,
    api_base: str | None = None,
    api_key: str | None = None,
    num_retries: int = 2,
    timeout: int | None = None,
) -> dspy.LM:
    """Use Responses transport for Sol; keep every other route."""

    if model != SOL_MODEL:
        route_kwargs: dict[str, Any] = {
            "temperature": temperature,
            "max_tokens": max_tokens,
            "cache": cache,
            "api_base": api_base,
            "num_retries": num_retries,
            "timeout": timeout,
        }
        if api_key is not None:
            route_kwargs["api_key"] = api_key
        return build_dspy_lm(model, **route_kwargs)
    sol_kwargs: dict[str, Any] = {
        "model_type": "responses",
        "temperature": temperature,
        "max_tokens": max_tokens,
        "cache": cache,
        "num_retries": num_retries,
    }
    if api_base:
        sol_kwargs["api_base"] = api_base
    if api_key is not None:
        sol_kwargs["api_key"] = api_key
    sol_kwargs["timeout"] = timeout if timeout is not None else SOL_REQUEST_TIMEOUT_SECONDS
    return dspy.LM(model, **sol_kwargs)
