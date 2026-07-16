from __future__ import annotations

from pathlib import Path

from scripts.run_hosted_holdout_panel import _prepare_gan_command


def test_gan_command_uses_model_specific_temperature(tmp_path: Path) -> None:
    command = _prepare_gan_command(
        {
            "slug": "gpt56luna",
            "model": "openai/gpt-5.6-luna",
            "gan_temperature": 1,
            "gan_max_tokens": 12000,
        },
        {
            "runner": "scripts/run_gan2026_hosted_condition.py",
            "pipeline": "llm_with_rules",
            "prompt_version": "gan2026_hybrid_structured_events_v0.7",
            "split": "test",
            "protocol": "docs/protocol.md",
            "max_tokens": 10000,
            "scratch_root": str(tmp_path),
        },
    )

    temperature_index = command.index("--temperature")
    assert command[temperature_index + 1] == "1"
    prompt_index = command.index("--prompt-version")
    assert command[prompt_index + 1] == "gan2026_hybrid_structured_events_v0.7"
    max_tokens_index = command.index("--max-tokens")
    assert command[max_tokens_index + 1] == "12000"
