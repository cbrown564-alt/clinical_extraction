"""Shared LLM runtime configuration for Gan 2026 experiments."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import dspy

from clinical_extraction.core.paths import discover_repo_root

OLLAMA_CHAT_PREFIX = "ollama_chat/"
VLLM_PREFIX = "vllm/"
GEMINI_PREFIX = "gemini/"
GEMINI_OPENAI_BASE = "https://generativelanguage.googleapis.com/v1beta/openai/"
GEMINI_ALLOWED_REASONING_EFFORT = frozenset({"low", "medium", "high"})
GEMINI_DEFAULT_REASONING_EFFORT = "low"


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
    if model.startswith(GEMINI_PREFIX):
        _load_repo_dotenv_if_needed()
        model = "openai/" + model.removeprefix(GEMINI_PREFIX)
        api_base = api_base or GEMINI_OPENAI_BASE
        kwargs["api_key"] = api_key or _gemini_api_key_from_environment()
        if not kwargs["api_key"]:
            raise ValueError(
                "gemini/<model> routes require GEMINI_API_KEY or GOOGLE_API_KEY."
            )
        kwargs["extra_body"] = {
            "reasoning_effort": _gemini_reasoning_effort_from_environment(),
        }
    if model.startswith(VLLM_PREFIX):
        model = "openai/" + model.removeprefix(VLLM_PREFIX)
        api_base = api_base or os.environ.get("VLLM_BASE_URL")
        kwargs["api_key"] = api_key or os.environ.get("VLLM_API_KEY", "EMPTY")
        kwargs["extra_body"] = {
            "chat_template_kwargs": _vllm_chat_template_kwargs_from_environment()
        }
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


def _gemini_api_key_from_environment() -> str:
    return (
        os.environ.get("GEMINI_API_KEY", "").strip()
        or os.environ.get("GOOGLE_API_KEY", "").strip()
    )


def _gemini_reasoning_effort_from_environment() -> str:
    effort = os.environ.get(
        "GEMINI_REASONING_EFFORT", GEMINI_DEFAULT_REASONING_EFFORT
    ).strip().lower()
    if effort not in GEMINI_ALLOWED_REASONING_EFFORT:
        allowed = ", ".join(sorted(GEMINI_ALLOWED_REASONING_EFFORT))
        raise ValueError(f"GEMINI_REASONING_EFFORT must be one of: {allowed}")
    return effort


def _load_repo_dotenv_if_needed() -> None:
    if _gemini_api_key_from_environment():
        return
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    env_file = discover_repo_root(start=Path(__file__), require_src=True) / ".env"
    if env_file.is_file():
        load_dotenv(env_file, override=False)


def _vllm_chat_template_kwargs_from_environment() -> dict[str, Any]:
    thinking_raw = os.environ.get("VLLM_THINKING", "false").strip().lower()
    if thinking_raw in {"1", "true", "yes", "on"}:
        thinking = True
    elif thinking_raw in {"0", "false", "no", "off"}:
        thinking = False
    else:
        raise ValueError("VLLM_THINKING must be true or false")
    options: dict[str, Any] = {"thinking": thinking}
    reasoning_effort = os.environ.get("VLLM_REASONING_EFFORT", "").strip()
    if reasoning_effort:
        options["reasoning_effort"] = reasoning_effort
    return options
