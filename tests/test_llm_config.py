from __future__ import annotations

from typing import Any

import pytest

from clinical_extraction.tasks.seizure_frequency.gan2026 import llm_config


def test_build_dspy_lm_configures_vllm_chat_template(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_lm(model: str, **kwargs: Any) -> object:
        captured["model"] = model
        captured.update(kwargs)
        return object()

    monkeypatch.setattr(llm_config.dspy, "LM", fake_lm)
    monkeypatch.setenv("VLLM_THINKING", "true")
    monkeypatch.setenv("VLLM_REASONING_EFFORT", "medium")

    llm_config.build_dspy_lm(
        "vllm/deepseek-v4-flash",
        temperature=0.0,
        max_tokens=16_000,
        cache=False,
        api_base="https://vllm.example/v1",
        api_key="secret",
        timeout=300,
    )

    assert captured == {
        "model": "openai/deepseek-v4-flash",
        "temperature": 0.0,
        "max_tokens": 16_000,
        "cache": False,
        "num_retries": 2,
        "api_base": "https://vllm.example/v1",
        "api_key": "secret",
        "timeout": 300,
        "extra_body": {
            "chat_template_kwargs": {
                "thinking": True,
                "reasoning_effort": "medium",
            }
        },
    }


def test_build_dspy_lm_leaves_standard_openai_request_unchanged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_lm(model: str, **kwargs: Any) -> object:
        captured.update(kwargs)
        return object()

    monkeypatch.setattr(llm_config.dspy, "LM", fake_lm)

    llm_config.build_dspy_lm(
        "openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=900,
        cache=False,
    )

    assert "extra_body" not in captured


def test_vllm_thinking_settings_are_read_from_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}
    monkeypatch.setenv("VLLM_THINKING", "false")
    monkeypatch.delenv("VLLM_REASONING_EFFORT", raising=False)
    monkeypatch.setattr(
        llm_config.dspy,
        "LM",
        lambda _model, **kwargs: captured.update(kwargs) or object(),
    )

    llm_config.build_dspy_lm(
        "vllm/deepseek-v4-flash",
        temperature=0.0,
        max_tokens=900,
        cache=False,
    )

    assert captured["extra_body"] == {
        "chat_template_kwargs": {"thinking": False}
    }


def test_vllm_route_and_key_default_to_vllm_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}
    monkeypatch.setenv("VLLM_BASE_URL", "https://vllm.example/v1")
    monkeypatch.setenv("VLLM_API_KEY", "secret")
    monkeypatch.setattr(
        llm_config.dspy,
        "LM",
        lambda _model, **kwargs: captured.update(kwargs) or object(),
    )

    llm_config.build_dspy_lm(
        "vllm/deepseek-v4-flash",
        temperature=0.0,
        max_tokens=900,
        cache=False,
    )

    assert captured["api_base"] == "https://vllm.example/v1"
    assert captured["api_key"] == "secret"
