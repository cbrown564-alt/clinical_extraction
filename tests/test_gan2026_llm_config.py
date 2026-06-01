from __future__ import annotations

from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026 import llm_config


def test_build_dspy_lm_routes_ollama_chat_with_thinking_disabled(monkeypatch) -> None:
    calls: dict[str, Any] = {}

    def fake_lm(model: str, **kwargs):
        calls["model"] = model
        calls["kwargs"] = kwargs
        return object()

    monkeypatch.setattr(llm_config.dspy, "LM", fake_lm)

    llm_config.build_dspy_lm(
        "ollama_chat/qwen3.6:35b",
        temperature=0.0,
        max_tokens=1400,
        cache=False,
        api_base="http://localhost:11434/v1",
    )

    assert calls["model"] == "ollama_chat/qwen3.6:35b"
    assert calls["kwargs"]["api_base"] == "http://localhost:11434"
    assert calls["kwargs"]["extra_body"] == {"think": False}
    assert calls["kwargs"]["cache"] is False


def test_build_dspy_lm_preserves_openai_compatible_route(monkeypatch) -> None:
    calls: dict[str, Any] = {}

    def fake_lm(model: str, **kwargs):
        calls["model"] = model
        calls["kwargs"] = kwargs
        return object()

    monkeypatch.setattr(llm_config.dspy, "LM", fake_lm)

    llm_config.build_dspy_lm(
        "openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=900,
        cache=True,
        api_base="http://localhost:11434/v1",
    )

    assert calls["model"] == "openai/gpt-4.1-mini"
    assert calls["kwargs"]["api_base"] == "http://localhost:11434/v1"
    assert "extra_body" not in calls["kwargs"]
