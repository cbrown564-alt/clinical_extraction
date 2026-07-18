from __future__ import annotations

from scripts import run_gan2026_v05_hosted_condition as hosted


def test_v05_main_installs_transport_builder_on_pipeline_module(monkeypatch) -> None:
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
