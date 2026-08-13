#!/usr/bin/env python3
"""Assemble the living six-model primary panel from current-stack replays.

Copies LLM-only, evidence, and Gan dev750 fields from the 3 Aug snapshot.
Overlays HEAD llm_with_rules fills from the 13 Aug remaining-cell replay,
including the selected DeepSeek 0731 holdout cells.
"""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HISTORICAL = ROOT / "experiments/six_model_final_panel_20260803/panel_aggregate.json"
REPLAY = (
    ROOT
    / "experiments/six_model_current_stack_remaining_cells_replay_20260813"
    / "replay_summary.json"
)
OUT_DIR = ROOT / "experiments/six_model_current_stack_primary_panel_20260813"
OUT_JSON = OUT_DIR / "panel_aggregate.json"

SLUG_BY_MODEL = {
    "openai/gpt-4.1-mini": "gpt41mini",
    "openai/gpt-5.6-luna": "gpt56luna",
    "openai/gpt-5.6-sol": "gpt56sol",
    "deepseek/deepseek-v4-flash": "deepseek_v4_flash",
    "ollama_chat/qwen3.6:35b": "qwen36_35b",
    "ollama_chat/gemma4:26b": "gemma4_26b",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replay", type=Path, default=REPLAY)
    parser.add_argument("--out", type=Path, default=OUT_JSON)
    args = parser.parse_args()
    historical = json.loads(HISTORICAL.read_text(encoding="utf-8"))
    replay = json.loads(args.replay.read_text(encoding="utf-8"))
    panel = deepcopy(historical)
    panel["schema_version"] = "six_model.current_stack_primary_panel.v1"
    panel["generated_on"] = datetime.now(UTC).date().isoformat()
    panel["identity"] = (
        "Selected current-stack llm_with_rules fills (decision 0050) "
        "over the 3 Aug panel's llm-only and evidence fields"
    )
    panel["primary_method"] = "llm_with_rules"
    panel["claim_boundary"] = (
        "Hybrid holdout and ExECT dev140 hybrid are 13 Aug no-call current-stack. "
        "DeepSeek holdout uses 0731 raws. LLM-only, evidence rates, and Gan "
        "dev750 hybrid remain the 3 Aug snapshot. Not clinical validation."
    )

    gan_test = replay["gan2026_test450"]["models"]
    exect_dev = replay["exectv2_dev140"]["models"]
    exect_test = replay["exectv2_test60"]["models"]
    deepseek = replay["deepseek_v4_flash_0731"]

    for condition in panel["conditions"]:
        slug = SLUG_BY_MODEL[condition["model"]]
        gan_cell = (
            deepseek["gan2026_test450"]
            if slug == "deepseek_v4_flash"
            else gan_test[slug]
        )
        condition["gan2026"]["test450"]["llm_with_rules_purist_accuracy"] = round(
            gan_cell["after"]["purist"] / 450, 4
        )
        condition["gan2026"]["test450"]["llm_with_rules_pragmatic_accuracy"] = round(
            gan_cell["after"]["pragmatic"] / 450, 4
        )
        condition["exectv2"]["dev140"]["llm_with_rules_clinical_fact_f1"] = exect_dev[
            slug
        ]["after_four_family_f1"]
        test_cell = (
            deepseek["exectv2_test60"]
            if slug == "deepseek_v4_flash"
            else exect_test[slug]
        )
        condition["exectv2"]["test60"]["llm_with_rules_clinical_fact_f1"] = test_cell[
            "after_four_family_f1"
        ]
        condition["exectv2"]["test60"]["llm_with_rules_by_family"] = {
            family: float(score["f1"])
            for family, score in test_cell["after_by_family"].items()
        }

    provenance = dict(panel.get("provenance") or {})
    provenance["current_stack_replay"] = (
        "experiments/six_model_current_stack_remaining_cells_replay_20260813/replay_summary.json"
    )
    provenance["historical_20260803_panel"] = (
        "experiments/six_model_final_panel_20260803/panel_aggregate.json"
    )
    provenance["decision"] = "docs/decisions/0050-current-stack-hybrid-primary-fills.md"
    provenance["builder"] = "scripts/build_six_model_current_stack_primary_panel.py"
    panel["provenance"] = provenance

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(panel, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {args.out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
