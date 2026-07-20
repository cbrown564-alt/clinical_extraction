"""Runtime configuration for an OpenAI-compatible model endpoint."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


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
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 16000,
        timeout_seconds: float = 300.0,
    ) -> RuntimeConfig:
        resolved_base = (
            base_url if base_url is not None else os.getenv("CLINICAL_LLM_BASE_URL") or ""
        ).rstrip("/")
        resolved_key = (
            api_key if api_key is not None else os.getenv("CLINICAL_LLM_API_KEY") or ""
        )
        resolved_model = (
            model
            if model is not None
            else os.getenv("CLINICAL_LLM_MODEL") or "deepseek-v4-flash"
        )
        if not resolved_base:
            raise ValueError(
                "No endpoint configured. Set CLINICAL_LLM_BASE_URL or pass --base-url."
            )
        if not resolved_key:
            raise ValueError(
                "No API key configured. Set CLINICAL_LLM_API_KEY or pass --api-key. "
                "Use EMPTY only when the endpoint explicitly permits it."
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
