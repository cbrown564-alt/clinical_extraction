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


def test_build_dspy_lm_routes_gemini_through_openai_compatible_endpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_lm(model: str, **kwargs: Any) -> object:
        captured["model"] = model
        captured.update(kwargs)
        return object()

    monkeypatch.setattr(llm_config.dspy, "LM", fake_lm)
    monkeypatch.setattr(llm_config, "_load_repo_dotenv_if_needed", lambda: None)
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-secret")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_REASONING_EFFORT", raising=False)

    llm_config.build_dspy_lm(
        "gemini/gemini-3.7-flash",
        temperature=0.0,
        max_tokens=16_000,
        cache=False,
        timeout=300,
    )

    assert captured == {
        "model": "openai/gemini-3.7-flash",
        "temperature": 0.0,
        "max_tokens": 16_000,
        "cache": False,
        "num_retries": 2,
        "timeout": 300,
        "api_key": "gemini-secret",
        "api_base": llm_config.GEMINI_OPENAI_BASE,
        "extra_body": {"reasoning_effort": "low"},
    }


def test_build_dspy_lm_routes_gemini_through_openrouter_when_key_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_lm(model: str, **kwargs: Any) -> object:
        captured["model"] = model
        captured.update(kwargs)
        return object()

    monkeypatch.setattr(llm_config.dspy, "LM", fake_lm)
    monkeypatch.setattr(llm_config, "_load_repo_dotenv_if_needed", lambda: None)
    monkeypatch.setenv("OPENROUTER_API_KEY", "openrouter-secret")
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-secret")
    monkeypatch.delenv("GEMINI_REASONING_EFFORT", raising=False)

    llm_config.build_dspy_lm(
        "gemini/gemini-3.7-flash",
        temperature=0.0,
        max_tokens=16_000,
        cache=False,
        timeout=300,
    )

    assert captured == {
        "model": "openai/google/gemini-3.7-flash",
        "temperature": 0.0,
        "max_tokens": 16_000,
        "cache": False,
        "num_retries": 2,
        "timeout": 300,
        "api_key": "openrouter-secret",
        "api_base": llm_config.OPENROUTER_OPENAI_BASE,
        "extra_body": {"reasoning": {"effort": "low"}},
    }


def test_gemini_reasoning_effort_is_read_from_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}
    monkeypatch.setattr(llm_config, "_load_repo_dotenv_if_needed", lambda: None)
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-secret")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setenv("GEMINI_REASONING_EFFORT", "medium")
    monkeypatch.setattr(
        llm_config.dspy,
        "LM",
        lambda _model, **kwargs: captured.update(kwargs) or object(),
    )

    llm_config.build_dspy_lm(
        "gemini/gemini-3.7-flash",
        temperature=0.0,
        max_tokens=900,
        cache=False,
    )

    assert captured["extra_body"] == {"reasoning_effort": "medium"}


def test_openrouter_gemini_sends_medium_reasoning_effort(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}
    monkeypatch.setattr(llm_config, "_load_repo_dotenv_if_needed", lambda: None)
    monkeypatch.setenv("OPENROUTER_API_KEY", "openrouter-secret")
    monkeypatch.setenv("GEMINI_REASONING_EFFORT", "medium")
    monkeypatch.setattr(
        llm_config.dspy,
        "LM",
        lambda _model, **kwargs: captured.update(kwargs) or object(),
    )

    llm_config.build_dspy_lm(
        "gemini/gemini-3.7-flash",
        temperature=0.0,
        max_tokens=900,
        cache=False,
    )

    assert captured["api_base"] == llm_config.OPENROUTER_OPENAI_BASE
    assert captured["extra_body"] == {"reasoning": {"effort": "medium"}}


def test_gemini_route_rejects_unsupported_reasoning_effort(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(llm_config, "_load_repo_dotenv_if_needed", lambda: None)
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-secret")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setenv("GEMINI_REASONING_EFFORT", "minimal")
    monkeypatch.setattr(llm_config.dspy, "LM", lambda *_args, **_kwargs: object())

    with pytest.raises(ValueError, match="GEMINI_REASONING_EFFORT"):
        llm_config.build_dspy_lm(
            "gemini/gemini-3.7-flash",
            temperature=0.0,
            max_tokens=900,
            cache=False,
        )


def test_deepseek_thinking_disabled_is_sent_in_extra_body(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_lm(model: str, **kwargs: Any) -> object:
        captured["model"] = model
        captured.update(kwargs)
        return object()

    monkeypatch.setattr(llm_config.dspy, "LM", fake_lm)

    llm_config.build_dspy_lm(
        "deepseek/deepseek-v4-flash",
        temperature=0.0,
        max_tokens=16000,
        cache=False,
        thinking_type="disabled",
    )

    assert captured["model"] == "deepseek/deepseek-v4-flash"
    assert captured["extra_body"] == {"thinking": {"type": "disabled"}}


def test_deepseek_living_low_sends_thinking_and_effort(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_lm(model: str, **kwargs: Any) -> object:
        captured["model"] = model
        captured.update(kwargs)
        return object()

    monkeypatch.setattr(llm_config.dspy, "LM", fake_lm)

    llm_config.build_dspy_lm(
        "deepseek/deepseek-v4-flash",
        temperature=0.0,
        max_tokens=16000,
        cache=False,
        thinking_type="enabled",
        reasoning_effort="low",
    )

    assert captured["model"] == "deepseek/deepseek-v4-flash"
    assert captured["extra_body"] == {
        "thinking": {"type": "enabled"},
        "reasoning_effort": "low",
    }


def test_ollama_chat_defaults_to_think_false(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}
    monkeypatch.setattr(
        llm_config.dspy,
        "LM",
        lambda _model, **kwargs: captured.update(kwargs) or object(),
    )

    llm_config.build_dspy_lm(
        "ollama_chat/qwen3.8:27b",
        temperature=0.0,
        max_tokens=5000,
        cache=False,
    )

    assert captured["extra_body"]["think"] is False


def test_ollama_chat_sends_think_true_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}
    monkeypatch.setattr(
        llm_config.dspy,
        "LM",
        lambda _model, **kwargs: captured.update(kwargs) or object(),
    )

    llm_config.build_dspy_lm(
        "ollama_chat/qwen3.8:27b",
        temperature=0.0,
        max_tokens=5000,
        cache=False,
        thinking_type="enabled",
    )

    assert captured["extra_body"]["think"] is True


def test_deepseek_omits_thinking_toggle_when_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}
    monkeypatch.setattr(
        llm_config.dspy,
        "LM",
        lambda _model, **kwargs: captured.update(kwargs) or object(),
    )

    llm_config.build_dspy_lm(
        "deepseek/deepseek-v4-flash",
        temperature=0.0,
        max_tokens=16000,
        cache=False,
    )

    assert "extra_body" not in captured


def test_gemini_route_requires_an_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setattr(llm_config, "_load_repo_dotenv_if_needed", lambda: None)
    monkeypatch.setattr(llm_config.dspy, "LM", lambda *_args, **_kwargs: object())

    with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
        llm_config.build_dspy_lm(
            "gemini/gemini-3.7-flash",
            temperature=0.0,
            max_tokens=900,
            cache=False,
        )
