"""Materialize the clean six-model final panel used by the comparison report.

Assembles aggregate-only ExECT and Gan scores for LLM only and LLM with rules
into one directory. Supervisor-facing docs cite this panel as the final results
on the selected codebase; provenance pointers stay inside the JSON.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "experiments/six_model_final_panel_20260803"
OUT_JSON = OUT_DIR / "panel_aggregate.json"

SCORECARD = ROOT / "experiments/shared_reliability_scorecard_20260718.json"
EXECT_TEST60 = (
    ROOT / "experiments/exectv2_six_model_test60_stage_panel_20260801/panel_aggregate.json"
)
GAN_FLOORS = (
    ROOT / "experiments/gan2026_six_model_current_floors_replay_20260731/replay_summary.json"
)
GAN_LLM_ONLY_TEST450 = (
    ROOT / "experiments/gan2026_six_model_llm_only_test450_20260801/panel_aggregate.json"
)
DEEPSEEK_0731 = ROOT / "experiments/deepseek_v4_flash_0731_matched_comparison_20260803.json"

MODELS = [
    ("openai/gpt-4.1-mini", "gpt41mini", "GPT-4.1-mini"),
    ("openai/gpt-5.6-luna", "gpt56luna", "GPT-5.6 Luna"),
    ("openai/gpt-5.6-sol", "gpt56sol", "GPT-5.6 Sol"),
    ("deepseek/deepseek-v4-flash", "deepseek_v4_flash", "DeepSeek V4 Flash"),
    ("ollama_chat/qwen3.6:35b", "qwen36_35b", "Qwen 3.6:35B"),
    ("ollama_chat/gemma4:26b", "gemma4_26b", "Gemma 4 26B"),
]
DEEPSEEK = "deepseek/deepseek-v4-flash"


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _measurement(scorecard: dict[str, Any], measurement_id: str) -> dict[str, Any]:
    return next(row for row in scorecard["measurements"] if row["measurement_id"] == measurement_id)


def _round4(value: float) -> float:
    return round(float(value), 4)


def _acc(correct: int, rows: int) -> float:
    return _round4(correct / rows)


def main() -> None:
    scorecard = _read(SCORECARD)
    test60 = _read(EXECT_TEST60)
    gan = _read(GAN_FLOORS)
    gan_llm_only = _read(GAN_LLM_ONLY_TEST450)
    deepseek = _read(DEEPSEEK_0731)
    ds_cells = deepseek["cells"]

    exect_dev = dict(
        _measurement(scorecard, "exectv2_six_model_dev140_clinical_headline_f1")["value"]
    )
    test60_by_model = {row["model"]: row for row in test60["conditions"]}
    gan_llm_only_by_model = {row["model"]: row for row in gan_llm_only["conditions"]}

    conditions: list[dict[str, Any]] = []
    for model, slug, label in MODELS:
        stage = test60_by_model[model]
        gan_test = gan["test450_aggregate"][slug]
        gan_dev = gan["dev750"][slug]
        gan_llm = gan_llm_only_by_model[model]

        if model == DEEPSEEK:
            exect_test_llm = _round4(ds_cells["exectv2_test60_llm_only"]["update_0731"]["value"])
            exect_test_final = _round4(
                ds_cells["exectv2_test60_llm_with_rules"]["update_0731"]["value"]
            )
            exect_dev_final = _round4(
                ds_cells["exectv2_dev140_llm_with_rules"]["update_0731"]["value"]
            )
            gan_test_purist = int(
                ds_cells["gan2026_test450_llm_with_rules"]["update_0731"]["purist_correct"]
            )
            gan_test_pragmatic = int(
                ds_cells["gan2026_test450_llm_with_rules"]["update_0731"]["pragmatic_correct"]
            )
            gan_test_rows = 450
            provider_revision = "DeepSeek-V4-Flash-0731"
        else:
            exect_test_llm = _round4(stage["raw_lane_score"]["f1"])
            exect_test_final = _round4(stage["clinical_headline"]["f1"])
            exect_dev_final = _round4(exect_dev[model])
            gan_test_purist = int(gan_test["after_purist"])
            gan_test_pragmatic = int(gan_test["after_pragmatic"])
            gan_test_rows = int(gan_test["rows"])
            provider_revision = None

        gan_dev_rows = int(gan_dev["rows"])
        gan_dev_purist = int(gan_dev["after_purist"])
        gan_llm_purist = int(gan_llm["purist_correct"])
        gan_llm_rows = int(gan_llm["rows"])

        conditions.append(
            {
                "model": model,
                "slug": slug,
                "label": label,
                "provider_revision": provider_revision,
                "exectv2": {
                    "dev140": {
                        "llm_with_rules_clinical_fact_f1": exect_dev_final,
                    },
                    "test60": {
                        "row_count": 59,
                        "row_policy": "aggregate_only",
                        "llm_clinical_fact_f1": exect_test_llm,
                        "llm_with_rules_clinical_fact_f1": exect_test_final,
                        "llm_with_rules_by_family": {
                            family: _round4(scores["f1"])
                            for family, scores in stage["clinical_headline_by_family"].items()
                        },
                    },
                },
                "gan2026": {
                    "dev750": {
                        "row_count": gan_dev_rows,
                        "row_policy": "development_review_permitted",
                        "llm_with_rules_purist_accuracy": _acc(gan_dev_purist, gan_dev_rows),
                    },
                    "test450": {
                        "row_count": gan_test_rows,
                        "row_policy": "aggregate_only",
                        "llm_purist_accuracy": _acc(gan_llm_purist, gan_llm_rows),
                        "llm_with_rules_purist_accuracy": _acc(gan_test_purist, gan_test_rows),
                        "llm_with_rules_pragmatic_accuracy": _acc(
                            gan_test_pragmatic, gan_test_rows
                        ),
                    },
                },
            }
        )

    panel = {
        "schema_version": "six_model.final_panel.v2",
        "generated_on": "2026-08-03",
        "identity": (
            "Final six-model results on the selected ExECT and Gan codebase for "
            "the comparison report"
        ),
        "primary_method": "llm_with_rules",
        "also_reports": ["llm"],
        "display_rule": "Report primary scores to two decimal places in prose and tables.",
        "models": [model for model, _, _ in MODELS],
        "claim_boundary": (
            "Aggregate-only locked holdout for test60/test450. Development splits "
            "permit row review. ExECT clinical fact F1 and Gan Purist are not "
            "interchangeable. Decision 0046 Sol method-row fills remain the paper "
            "ExECT method identity. Not clinical validation."
        ),
        "conditions": conditions,
        "provenance": {
            "note": (
                "Internal assembly sources only. Supervisor-facing prose cites this "
                "panel as the final results directory."
            ),
            "exectv2_test60_stage_panel": str(EXECT_TEST60.relative_to(ROOT)).replace("\\", "/"),
            "exectv2_dev140_scorecard_measurement": "exectv2_six_model_dev140_clinical_headline_f1",
            "gan2026_llm_with_rules_scores": str(GAN_FLOORS.relative_to(ROOT)).replace("\\", "/"),
            "gan2026_llm_only_test450": str(GAN_LLM_ONLY_TEST450.relative_to(ROOT)).replace(
                "\\", "/"
            ),
            "deepseek_v4_flash_0731": str(DEEPSEEK_0731.relative_to(ROOT)).replace("\\", "/"),
            "report": "docs/research/six_model_comparison_report_2026-07-18.md",
            "builder": "scripts/build_six_model_final_panel.py",
        },
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(panel, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_JSON.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
