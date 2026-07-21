"""Resolve endpoint settings without exposing credentials."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from urllib.parse import urlsplit, urlunsplit

from .errors import ConfigurationError
from .models import GenerationSettings


def _boolean(value: str, *, name: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ConfigurationError(f"{name} must be true or false")


def _resolve_alias(
    environment: Mapping[str, str], primary: str, alias: str, *, default: str | None = None
) -> tuple[str, str]:
    primary_value = environment.get(primary)
    alias_value = environment.get(alias)
    if primary_value is not None and alias_value is not None and primary_value != alias_value:
        raise ConfigurationError(f"{primary} and {alias} disagree")
    if primary_value is not None:
        return primary_value, primary
    if alias_value is not None:
        return alias_value, alias
    if default is not None:
        return default, "default"
    raise ConfigurationError(f"set {primary}")


def safe_endpoint(value: str) -> str:
    parts = urlsplit(value)
    host = parts.hostname or ""
    if parts.port is not None:
        host = f"{host}:{parts.port}"
    return urlunsplit((parts.scheme, host, parts.path.rstrip("/"), "", ""))


@dataclass(frozen=True)
class EndpointConfig:
    base_url: str
    api_key: str = field(repr=False)
    model: str = "deepseek-v4-flash"
    settings: GenerationSettings = field(default_factory=GenerationSettings)
    sources: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_env(cls, environment: Mapping[str, str] | None = None) -> EndpointConfig:
        values = os.environ if environment is None else environment
        base_url, base_source = _resolve_alias(
            values, "VLLM_BASE_URL", "CLINICAL_LLM_BASE_URL"
        )
        api_key, key_source = _resolve_alias(values, "VLLM_API_KEY", "CLINICAL_LLM_API_KEY")
        model, model_source = _resolve_alias(
            values, "VLLM_MODEL", "CLINICAL_LLM_MODEL", default="deepseek-v4-flash"
        )
        if not base_url.strip() or not api_key:
            raise ConfigurationError("endpoint and API key must be non-empty")
        settings = GenerationSettings(
            temperature=float(values.get("VLLM_TEMPERATURE", "0")),
            seed=int(values["VLLM_SEED"]) if values.get("VLLM_SEED") else 0,
            max_completion_tokens=int(values.get("VLLM_MAX_TOKENS", "16000")),
            timeout_seconds=float(values.get("VLLM_TIMEOUT_SECONDS", "300")),
            retry_count=int(values.get("VLLM_RETRY_COUNT", "1")),
            thinking=_boolean(values.get("VLLM_THINKING", "false"), name="VLLM_THINKING"),
            reasoning_effort=values.get("VLLM_REASONING_EFFORT") or None,
        )
        return cls(
            base_url=base_url.rstrip("/"),
            api_key=api_key,
            model=model,
            settings=settings,
            sources={
                "base_url": base_source,
                "api_key": key_source,
                "model": model_source,
                "thinking": "VLLM_THINKING" if "VLLM_THINKING" in values else "default",
            },
        )

    def public_dict(self) -> dict[str, object]:
        return {
            "endpoint": safe_endpoint(self.base_url),
            "model": self.model,
            "thinking": self.settings.thinking,
            "reasoning_effort": self.settings.reasoning_effort,
            "temperature": self.settings.temperature,
            "seed": self.settings.seed,
            "maximum_completion_tokens": self.settings.max_completion_tokens,
            "timeout_seconds": self.settings.timeout_seconds,
            "retry_count": self.settings.retry_count,
            "json_response_mode": self.settings.json_response_mode,
            "cache": "disabled",
            "sources": {key: value for key, value in self.sources.items() if key != "api_key"},
            "api_key": {"configured": True, "source": self.sources.get("api_key", "unknown")},
        }

