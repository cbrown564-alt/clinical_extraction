from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines import (
    key_entities_structured,
)
from scripts import run_exectv2_2call_model_swap as retained_runner
from scripts import run_exectv2_six_model_comparison as six_model_runner

structured_runner = key_entities_structured.runner


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
        "timeout": 300,
    }


def test_sol_respects_an_explicit_timeout(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_lm(model: str, **kwargs):
        captured.update(kwargs)
        return object()

    monkeypatch.setattr(six_model_runner.dspy, "LM", fake_lm)

    six_model_runner.build_six_model_lm(
        "openai/gpt-5.6-sol",
        temperature=1,
        max_tokens=16000,
        cache=False,
        timeout=45,
    )

    assert captured["timeout"] == 45


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


def test_completion_gate_rejects_call_failures() -> None:
    rows = [{"letter_id": "EA1", "call_error": "insufficient_quota", "parse_errors": []}]

    try:
        retained_runner._require_clean_complete_rows(rows, expected_count=1)
    except RuntimeError as exc:
        assert "call failure" in str(exc)
    else:
        raise AssertionError("expected dirty model rows to be rejected")


def test_completion_gate_rejects_missing_rows() -> None:
    try:
        retained_runner._require_clean_complete_rows([], expected_count=1)
    except RuntimeError as exc:
        assert "expected 1" in str(exc)
    else:
        raise AssertionError("expected incomplete model rows to be rejected")


def test_terminal_provider_errors_are_fail_fast() -> None:
    assert structured_runner._is_terminal_provider_error(
        'RateLimitError: {"code":"insufficient_quota"}'
    )
    assert structured_runner._is_terminal_provider_error("AuthenticationError: invalid_api_key")
    assert not structured_runner._is_terminal_provider_error("ReadTimeout: request timed out")
