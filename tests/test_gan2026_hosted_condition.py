from __future__ import annotations

import pytest

from scripts import run_gan2026_hosted_condition as hosted


def test_sol_responses_transport_omits_unsupported_temperature(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_lm(model: str, **kwargs: object) -> object:
        captured["model"] = model
        captured.update(kwargs)
        return object()

    monkeypatch.setattr(hosted.dspy, "LM", fake_lm)

    hosted.build_hosted_lm(
        hosted.SOL_MODEL,
        temperature=0,
        max_tokens=10000,
        cache=False,
    )

    assert captured["model"] == hosted.SOL_MODEL
    assert captured["model_type"] == "responses"
    assert "temperature" not in captured


def test_main_requires_explicit_frozen_prompt(monkeypatch) -> None:
    captured: dict[str, object] = {}
    monkeypatch.setattr(
        hosted.llm_pipeline_cli,
        "main",
        lambda argv: captured.setdefault("argv", argv),
    )
    monkeypatch.setattr(
        hosted.hybrid_structured_events,
        "set_active_prompt_version",
        lambda version: captured.setdefault("prompt_version", version),
    )

    hosted.main(
        [
            "--prompt-version",
            hosted.FROZEN_PROMPT_VERSION,
            "--pipeline",
            "llm_with_rules",
        ]
    )

    assert captured == {
        "prompt_version": hosted.FROZEN_PROMPT_VERSION,
        "argv": ["--pipeline", "llm_with_rules"],
    }
    assert hosted.hybrid_structured_events.build_dspy_lm is hosted.build_hosted_lm
    assert hosted.llm_only_canonical_pipeline.build_dspy_lm is hosted.build_hosted_lm


def test_main_rejects_any_other_prompt() -> None:
    with pytest.raises(SystemExit):
        hosted.main(
            [
                "--prompt-version",
                "gan2026_hybrid_structured_events_v0.6",
                "--pipeline",
                "llm_with_rules",
            ]
        )
