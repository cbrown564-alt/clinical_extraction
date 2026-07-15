from __future__ import annotations

from scripts import run_exectv2_six_model_comparison as six_model_runner


def test_sol_uses_dspy_responses_transport(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_lm(model: str, **kwargs):
        captured.update({"model": model, **kwargs})
        return object()

    monkeypatch.setattr(six_model_runner.dspy, "LM", fake_lm)

    six_model_runner.build_six_model_lm(
        "openai/gpt-5.6-sol",
        temperature=1,
        max_tokens=16000,
        cache=False,
        api_base=None,
        num_retries=2,
    )

    assert captured == {
        "model": "openai/gpt-5.6-sol",
        "model_type": "responses",
        "temperature": 1,
        "max_tokens": 16000,
        "cache": False,
        "num_retries": 2,
    }


def test_non_sol_routes_keep_the_retained_runtime_builder(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_retained(model: str, **kwargs):
        captured.update({"model": model, **kwargs})
        return object()

    monkeypatch.setattr(six_model_runner, "retained_build_dspy_lm", fake_retained)

    six_model_runner.build_six_model_lm(
        "ollama_chat/qwen3.6:35b",
        temperature=0,
        max_tokens=10000,
        cache=False,
        api_base="http://localhost:11434",
        num_retries=2,
    )

    assert captured == {
        "model": "ollama_chat/qwen3.6:35b",
        "temperature": 0,
        "max_tokens": 10000,
        "cache": False,
        "api_base": "http://localhost:11434",
        "num_retries": 2,
        "timeout": None,
    }
