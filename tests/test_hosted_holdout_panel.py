from __future__ import annotations

import json
from pathlib import Path

from scripts.run_hosted_holdout_panel import _prepare_gan_command

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "experiments" / "hosted_holdout_panels_20260715.json"


def test_retained_holdout_panels_include_all_six_models_at_equal_status() -> None:
    payload = json.loads(PANEL.read_text(encoding="utf-8"))
    assert payload["panel_status"] == "retained_six_model_aggregate_only"
    expected = {
        "openai/gpt-4.1-mini",
        "openai/gpt-5.6-luna",
        "openai/gpt-5.6-sol",
        "deepseek/deepseek-v4-flash",
        "ollama_chat/qwen3.6:35b",
        "ollama_chat/gemma4:26b",
    }
    for panel in payload["panels"].values():
        assert {condition["model"] for condition in panel["conditions"]} == expected

    serialized = PANEL.read_text(encoding="utf-8")
    for forbidden in ("row_id", "letter_id", "source_text", "prediction"):
        assert forbidden not in serialized


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
