"""Runtime configuration for an OpenAI-compatible model endpoint."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

GEMINI_PREFIX = "gemini/"
GEMINI_OPENAI_BASE = "https://generativelanguage.googleapis.com/v1beta/openai"
OPENROUTER_OPENAI_BASE = "https://openrouter.ai/api/v1"


@dataclass(frozen=True)
class RuntimeConfig:
    """Connection and generation settings shared by both clinical tasks."""

    base_url: str
    api_key: str = field(repr=False)
    model: str = "openai/deepseek-v4-flash"
    temperature: float = 0.0
    max_tokens: int = 16000
    timeout_seconds: float = 300.0

    @classmethod
    def from_environment(
        cls,
        *,
        environment: Mapping[str, str] | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 16000,
        timeout_seconds: float = 300.0,
    ) -> RuntimeConfig:
        if environment is None:
            _load_repo_dotenv()
            values = os.environ
        else:
            values = environment
        resolved_base = (
            base_url
            if base_url is not None
            else _resolve_alias(values, "CLINICAL_LLM_BASE_URL", "VLLM_BASE_URL")
        ).rstrip("/")
        resolved_key = (
            api_key
            if api_key is not None
            else _resolve_alias(values, "CLINICAL_LLM_API_KEY", "VLLM_API_KEY")
        )
        if model is not None:
            resolved_model = model
        else:
            clinical_model = values.get("CLINICAL_LLM_MODEL")
            vllm_model = values.get("VLLM_MODEL")
            if clinical_model and vllm_model and clinical_model != vllm_model:
                raise ValueError("CLINICAL_LLM_MODEL and VLLM_MODEL disagree")
            resolved_model = clinical_model or vllm_model or "deepseek-v4-flash"
            if vllm_model and "/" not in resolved_model:
                resolved_model = f"vllm/{resolved_model}"
        if resolved_model.startswith(GEMINI_PREFIX):
            openrouter_key = values.get("OPENROUTER_API_KEY", "").strip()
            google_key = (
                values.get("GEMINI_API_KEY", "").strip()
                or values.get("GOOGLE_API_KEY", "").strip()
            )
            if not resolved_base:
                if openrouter_key:
                    resolved_base = OPENROUTER_OPENAI_BASE
                else:
                    resolved_base = GEMINI_OPENAI_BASE
            if not resolved_key:
                if "openrouter.ai" in resolved_base:
                    resolved_key = openrouter_key
                else:
                    resolved_key = google_key
        if not resolved_base:
            raise ValueError(
                "No endpoint configured. Set CLINICAL_LLM_BASE_URL or pass --base-url. "
                "gemini/<model> routes default to OpenRouter when OPENROUTER_API_KEY "
                "is set, otherwise Google's OpenAI-compatible endpoint."
            )
        if not resolved_key and resolved_model.startswith("vllm/"):
            resolved_key = "EMPTY"
        if not resolved_key:
            raise ValueError(
                "No API key configured. Set CLINICAL_LLM_API_KEY or pass --api-key. "
                "gemini/<model> routes also accept OPENROUTER_API_KEY, "
                "GEMINI_API_KEY, or GOOGLE_API_KEY. "
                "Keyless vLLM routes use the vllm/<served-model> identifier."
            )
        if "/" not in resolved_model:
            resolved_model = f"openai/{resolved_model}"
        return cls(
            base_url=resolved_base,
            api_key=resolved_key,
            model=resolved_model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout_seconds=timeout_seconds,
        )

    @property
    def api_model(self) -> str:
        """Return the provider model name without DSPy's routing prefix."""

        return self.model.split("/", 1)[1] if "/" in self.model else self.model


def _load_repo_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    from clinical_extraction.core.paths import discover_repo_root

    env_file = discover_repo_root(start=Path(__file__), require_src=True) / ".env"
    if env_file.is_file():
        load_dotenv(env_file, override=False)


def _resolve_alias(values: Mapping[str, str], primary: str, alias: str) -> str:
    primary_value = values.get(primary, "")
    alias_value = values.get(alias, "")
    if primary_value and alias_value and primary_value != alias_value:
        raise ValueError(f"{primary} and {alias} disagree")
    return primary_value or alias_value
