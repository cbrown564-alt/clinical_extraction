"""LM construction for paper live cells."""

from __future__ import annotations

import os
from typing import Any

import dspy

from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import (
    OPENROUTER_OPENAI_BASE,
    build_dspy_lm,
)

SOL_MODEL = "openai/gpt-5.6-sol"
SOL_REQUEST_TIMEOUT_SECONDS = 300
AI_GATEWAY_OPENAI_BASE = "https://ai-gateway.vercel.sh/v1"


def gemini_api_base(api_base: str | None) -> str:
    """Resolve Gemini's OpenRouter endpoint unless a caller overrides it."""

    return api_base or OPENROUTER_OPENAI_BASE


def sol_api_base(api_base: str | None) -> str:
    """Resolve Sol's Vercel AI Gateway endpoint unless a caller overrides it."""

    return api_base or AI_GATEWAY_OPENAI_BASE


def resolve_paper_api_base(slug: str, api_base: str | None) -> str | None:
    """Apply hosted paper-route defaults."""

    if slug == "gpt56sol":
        return sol_api_base(api_base)
    if slug == "gemini37flash":
        return gemini_api_base(api_base)
    return api_base


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
        "api_base": sol_api_base(api_base),
    }
    resolved_key = (
        api_key if api_key is not None else os.environ.get("AI_GATEWAY_API_KEY", "").strip()
    )
    if resolved_key:
        sol_kwargs["api_key"] = resolved_key
    sol_kwargs["timeout"] = timeout if timeout is not None else SOL_REQUEST_TIMEOUT_SECONDS
    return dspy.LM(model, **sol_kwargs)
