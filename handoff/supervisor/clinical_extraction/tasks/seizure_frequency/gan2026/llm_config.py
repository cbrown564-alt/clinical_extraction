"""Shared LLM runtime configuration for Gan 2026 experiments."""

from __future__ import annotations

import os
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
    api_key: str | None = None,
    num_retries: int = 2,
    timeout: int | None = None,
) -> dspy.LM:
    """Create a DSPy LM with optional local/OpenAI-compatible endpoint routing."""

    kwargs: dict[str, Any] = {
        "temperature": temperature,
        "max_tokens": max_tokens,
        "cache": cache,
        "num_retries": num_retries,
    }
    if timeout is not None:
        kwargs["timeout"] = timeout
    if api_key is not None:
        kwargs["api_key"] = api_key
    if model.startswith(OLLAMA_CHAT_PREFIX):
        kwargs["api_base"] = (api_base or "http://localhost:11434").removesuffix("/v1")
        extra_body: dict[str, Any] = {"think": False}
        ollama_options = _ollama_options_from_environment()
        if ollama_options:
            extra_body["options"] = ollama_options
        kwargs["extra_body"] = extra_body
        return dspy.LM(model, **kwargs)
    if api_base:
        kwargs["api_base"] = api_base
    return dspy.LM(model, **kwargs)


def _ollama_options_from_environment() -> dict[str, int]:
    options: dict[str, int] = {}
    for env_name, option_name in (
        ("CLINICAL_EXTRACTION_OLLAMA_NUM_GPU", "num_gpu"),
        ("CLINICAL_EXTRACTION_OLLAMA_NUM_CTX", "num_ctx"),
    ):
        raw = os.environ.get(env_name, "").strip()
        if not raw:
            continue
        options[option_name] = int(raw)
    return options
