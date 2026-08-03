"""Materialize the clean six-model final panel used by the comparison report.

Assembles aggregate-only ExECT and Gan scores for LLM only and LLM with rules
into one directory. Supervisor-facing docs cite this panel as the final results
on the selected codebase; provenance pointers stay inside the JSON.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from clinical_extraction.core.evidence import evidence_is_substring

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
GAN_VALIDATION_COMPARISON = (
    ROOT / "experiments/gan2026_six_model_validation_comparison_20260718.json"
)
DEEPSEEK_0731 = ROOT / "experiments/deepseek_v4_flash_0731_matched_comparison_20260803.json"

EXECT_DEV140_LLM_ONLY_SOURCES: dict[str, Path] = {
    "openai/gpt-4.1-mini": ROOT
    / "experiments/exectv2_six_model_single_call_gpt41mini_dev140_20260715.json",
    "openai/gpt-5.6-luna": ROOT
    / "experiments/exectv2_six_model_single_call_gpt56luna_dev140_20260715.json",
    "openai/gpt-5.6-sol": ROOT
    / "experiments/exectv2_six_model_single_call_gpt56sol_dev140_20260715.json",
    "ollama_chat/qwen3.6:35b": ROOT
    / "experiments/exectv2_six_model_single_call_qwen36_35b_dev140_20260715.json",
    "ollama_chat/gemma4:26b": ROOT
    / "experiments/exectv2_six_model_single_call_gemma4_26b_dev140_20260715.json",
}

EXECT_DEV140_STRUCTURED_JSONL: dict[str, Path] = {
    "openai/gpt-4.1-mini": ROOT
    / "experiments/exectv2_six_model_single_call_gpt41mini_dev140_20260715_structured.jsonl",
    "openai/gpt-5.6-luna": ROOT
    / "experiments/exectv2_six_model_single_call_gpt56luna_dev140_20260715_structured.jsonl",
    "openai/gpt-5.6-sol": ROOT
    / "experiments/exectv2_six_model_single_call_gpt56sol_dev140_20260715_structured.jsonl",
    "deepseek/deepseek-v4-flash": ROOT
    / "experiments/exectv2_deepseek_v4_flash_0731_update_dev140_20260731_structured.jsonl",
    "ollama_chat/qwen3.6:35b": ROOT
    / "experiments/exectv2_six_model_single_call_qwen36_35b_dev140_20260715_structured.jsonl",
    "ollama_chat/gemma4:26b": ROOT
    / "experiments/exectv2_six_model_single_call_gemma4_26b_dev140_20260715_structured.jsonl",
}

EXECT_DEV140_ASSEMBLY_JSON: dict[str, Path] = {
    "openai/gpt-4.1-mini": ROOT
    / "experiments/exectv2_six_model_single_call_gpt41mini_dev140_20260715.json",
    "openai/gpt-5.6-luna": ROOT
    / "experiments/exectv2_six_model_single_call_gpt56luna_dev140_20260715.json",
    "openai/gpt-5.6-sol": ROOT
    / "experiments/exectv2_six_model_single_call_gpt56sol_dev140_20260715.json",
    "deepseek/deepseek-v4-flash": ROOT
    / "experiments/exectv2_deepseek_v4_flash_0731_update_dev140_20260731.json",
    "ollama_chat/qwen3.6:35b": ROOT
    / "experiments/exectv2_six_model_single_call_qwen36_35b_dev140_20260715.json",
    "ollama_chat/gemma4:26b": ROOT
    / "experiments/exectv2_six_model_single_call_gemma4_26b_dev140_20260715.json",
}

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


def _raw_lane_f1(path: Path) -> float:
    payload = _read(path)
    stack: list[Any] = [payload]
    while stack:
        obj = stack.pop()
        if isinstance(obj, dict):
            raw = obj.get("raw_lane_score")
            if isinstance(raw, dict):
                overall = raw.get("overall")
                if isinstance(overall, dict) and "f1" in overall:
                    return _round4(overall["f1"])
                if "f1" in raw:
                    return _round4(raw["f1"])
            stack.extend(obj.values())
        elif isinstance(obj, list):
            stack.extend(obj)
    raise KeyError(f"raw_lane_score F1 not found in {path}")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _letter_text(row: Mapping[str, Any]) -> str:
    payload = row.get("prompt_input_json")
    if isinstance(payload, str):
        payload = json.loads(payload)
    if not isinstance(payload, dict):
        raise KeyError("prompt_input_json missing letter_text")
    return str(payload["letter_text"])


def _mentions_from_structured_events(row: Mapping[str, Any]) -> list[dict[str, str]]:
    mentions: list[dict[str, str]] = []
    for event in row.get("structured_events") or []:
        if not isinstance(event, dict):
            continue
        evidence = str(event.get("evidence") or "")
        for mention in event.get("mentions") or []:
            if not isinstance(mention, dict):
                continue
            mentions.append(
                {
                    "entity": str(mention.get("entity") or ""),
                    "text": str(mention.get("text") or ""),
                    "evidence": evidence,
                }
            )
    return mentions


def _classify_evidence_warnings(warnings: Any) -> tuple[int, int, dict[str, int]]:
    repaired = 0
    hard_drop = 0
    detail = {
        "repaired_from_mention_text": 0,
        "repaired_exact_copy": 0,
        "dropped_not_substring": 0,
        "dropped_empty": 0,
    }
    for warning in warnings or []:
        text = str(warning)
        body = text
        if ": " in text:
            maybe = text.split(": ", 1)[1]
            if maybe.startswith(("repaired_", "dropped_")):
                body = maybe
        if body.startswith("repaired_evidence_from_mention_text"):
            repaired += 1
            detail["repaired_from_mention_text"] += 1
        elif body.startswith("repaired_evidence_exact_copy"):
            repaired += 1
            detail["repaired_exact_copy"] += 1
        elif body.startswith("dropped_evidence_not_substring"):
            hard_drop += 1
            detail["dropped_not_substring"] += 1
        elif body.startswith("dropped_empty_evidence"):
            hard_drop += 1
            detail["dropped_empty"] += 1
    return repaired, hard_drop, detail


def _pre_gate_evidence(model: str) -> dict[str, Any]:
    """Producer-stage quote validity before evidence repair/drop gates."""

    structured_path = EXECT_DEV140_STRUCTURED_JSONL[model]
    assembly_path = EXECT_DEV140_ASSEMBLY_JSON[model]
    rows = _read_jsonl(structured_path)
    exact = 0
    total = 0
    repaired = 0
    hard_drop = 0
    detail_totals = {
        "repaired_from_mention_text": 0,
        "repaired_exact_copy": 0,
        "dropped_not_substring": 0,
        "dropped_empty": 0,
    }
    for row in rows:
        note = _letter_text(row)
        for mention in _mentions_from_structured_events(row):
            total += 1
            if evidence_is_substring(note, mention["evidence"]):
                exact += 1
        row_repaired, row_hard, detail = _classify_evidence_warnings(row.get("gate_warnings"))
        repaired += row_repaired
        hard_drop += row_hard
        for key, value in detail.items():
            detail_totals[key] += value

    assembly = _read(assembly_path)
    lane_diagnostics = assembly.get("lane_diagnostics") or {}
    post_exact = sum(
        int(lane.get("exact_evidence_mentions") or 0) for lane in lane_diagnostics.values()
    )
    post_scored = sum(int(lane.get("scored_mentions") or 0) for lane in lane_diagnostics.values())
    if total <= 0:
        raise ValueError(f"no pre-gate mentions in {structured_path}")
    if post_scored <= 0:
        raise ValueError(f"no post-rules scored mentions in {assembly_path}")

    return {
        "pre_gate_mention_count": total,
        "pre_gate_exact_evidence_count": exact,
        "pre_gate_exact_evidence_rate": _round4(exact / total),
        "evidence_repaired_count": repaired,
        "evidence_hard_dropped_count": hard_drop,
        "evidence_warning_detail": detail_totals,
        "post_rules_exact_evidence_mentions": post_exact,
        "post_rules_scored_mentions": post_scored,
        "post_rules_exact_evidence_rate": _round4(post_exact / post_scored),
        "source_structured_jsonl": str(structured_path.relative_to(ROOT)).replace("\\", "/"),
        "source_assembly_json": str(assembly_path.relative_to(ROOT)).replace("\\", "/"),
        "metric_note": (
            "Pre-gate rate uses structured_events mention evidence versus letter_text "
            "before repaired_evidence_* / dropped_evidence_* gates. "
            "Post-rules rate is lane_diagnostics on final predicted_mentions "
            "(filter outcome; expect ~1.0)."
        ),
    }


def main() -> None:
    scorecard = _read(SCORECARD)
    test60 = _read(EXECT_TEST60)
    gan = _read(GAN_FLOORS)
    gan_llm_only = _read(GAN_LLM_ONLY_TEST450)
    gan_validation = _read(GAN_VALIDATION_COMPARISON)
    deepseek = _read(DEEPSEEK_0731)
    ds_cells = deepseek["cells"]

    exect_dev = dict(
        _measurement(scorecard, "exectv2_six_model_dev140_clinical_headline_f1")["value"]
    )
    test60_by_model = {row["model"]: row for row in test60["conditions"]}
    gan_llm_only_by_model = {row["model"]: row for row in gan_llm_only["conditions"]}
    gan_llm_only_dev = {
        row["model"]: row
        for row in gan_validation["conditions"]
        if row["method"] == "llm_only"
    }

    conditions: list[dict[str, Any]] = []
    for model, slug, label in MODELS:
        stage = test60_by_model[model]
        gan_test = gan["test450_aggregate"][slug]
        gan_dev = gan["dev750"][slug]
        gan_llm = gan_llm_only_by_model[model]
        gan_llm_dev = gan_llm_only_dev[model]

        if model == DEEPSEEK:
            exect_test_llm = _round4(ds_cells["exectv2_test60_llm_only"]["update_0731"]["value"])
            exect_test_final = _round4(
                ds_cells["exectv2_test60_llm_with_rules"]["update_0731"]["value"]
            )
            exect_dev_llm = _round4(ds_cells["exectv2_dev140_llm_only"]["update_0731"]["value"])
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
            gan_llm_only_dev_note = (
                "dev750 llm_only is pre-0731 six-model validation cell; "
                "test450 llm_only is 0731. Gap is provisional until matched "
                "0731 validation750 completes."
            )
        else:
            exect_test_llm = _round4(stage["raw_lane_score"]["f1"])
            exect_test_final = _round4(stage["clinical_headline"]["f1"])
            exect_dev_llm = _raw_lane_f1(EXECT_DEV140_LLM_ONLY_SOURCES[model])
            exect_dev_final = _round4(exect_dev[model])
            gan_test_purist = int(gan_test["after_purist"])
            gan_test_pragmatic = int(gan_test["after_pragmatic"])
            gan_test_rows = int(gan_test["rows"])
            provider_revision = None
            gan_llm_only_dev_note = None

        gan_dev_rows = int(gan_dev["rows"])
        gan_dev_purist = int(gan_dev["after_purist"])
        gan_llm_purist = int(gan_llm["purist_correct"])
        gan_llm_rows = int(gan_llm["rows"])
        gan_llm_dev_rows = int(gan_llm_dev["row_count"])
        gan_llm_dev_purist = int(gan_llm_dev["purist_correct"])

        gan_dev750: dict[str, Any] = {
            "row_count": gan_dev_rows,
            "row_policy": "development_review_permitted",
            "llm_purist_accuracy": _acc(gan_llm_dev_purist, gan_llm_dev_rows),
            "llm_with_rules_purist_accuracy": _acc(gan_dev_purist, gan_dev_rows),
        }
        if gan_llm_only_dev_note is not None:
            gan_dev750["llm_only_revision_note"] = gan_llm_only_dev_note

        evidence = _pre_gate_evidence(model)
        conditions.append(
            {
                "model": model,
                "slug": slug,
                "label": label,
                "provider_revision": provider_revision,
                "exectv2": {
                    "dev140": {
                        "llm_clinical_fact_f1": exect_dev_llm,
                        "llm_with_rules_clinical_fact_f1": exect_dev_final,
                        "pre_gate_exact_evidence_rate": evidence[
                            "pre_gate_exact_evidence_rate"
                        ],
                        "pre_gate_mention_count": evidence["pre_gate_mention_count"],
                        "pre_gate_exact_evidence_count": evidence[
                            "pre_gate_exact_evidence_count"
                        ],
                        "evidence_repaired_count": evidence["evidence_repaired_count"],
                        "evidence_hard_dropped_count": evidence[
                            "evidence_hard_dropped_count"
                        ],
                        "evidence_warning_detail": evidence["evidence_warning_detail"],
                        "post_rules_exact_evidence_rate": evidence[
                            "post_rules_exact_evidence_rate"
                        ],
                        "post_rules_scored_mentions": evidence[
                            "post_rules_scored_mentions"
                        ],
                        "evidence_metric_note": evidence["metric_note"],
                        "evidence_source_structured_jsonl": evidence[
                            "source_structured_jsonl"
                        ],
                        "evidence_source_assembly_json": evidence[
                            "source_assembly_json"
                        ],
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
                    "dev750": gan_dev750,
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
        "schema_version": "six_model.final_panel.v4",
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
            "ExECT method identity. Gan llm_only uses matched v0.8 prompt on "
            "dev750 and test450; do not mix historical llm_with_rules v0.7 "
            "validation with current-floors v0.5 test450. DeepSeek gan llm_only "
            "dev750 remains pre-0731 while test450 is 0731. ExECT "
            "post_rules_exact_evidence_rate is a filter outcome after "
            "evidence repair/drop; use pre_gate_exact_evidence_rate for model "
            "quote divergence. Not clinical validation."
        ),
        "conditions": conditions,
        "provenance": {
            "note": (
                "Internal assembly sources only. Supervisor-facing prose cites this "
                "panel as the final results directory."
            ),
            "exectv2_test60_stage_panel": str(EXECT_TEST60.relative_to(ROOT)).replace("\\", "/"),
            "exectv2_dev140_scorecard_measurement": "exectv2_six_model_dev140_clinical_headline_f1",
            "exectv2_dev140_llm_only_sources": {
                model: str(path.relative_to(ROOT)).replace("\\", "/")
                for model, path in EXECT_DEV140_LLM_ONLY_SOURCES.items()
            },
            "exectv2_dev140_llm_only_deepseek_0731": (
                "experiments/deepseek_v4_flash_0731_matched_comparison_20260803.json"
                "#cells.exectv2_dev140_llm_only"
            ),
            "exectv2_dev140_pre_gate_evidence_structured_jsonl": {
                model: str(path.relative_to(ROOT)).replace("\\", "/")
                for model, path in EXECT_DEV140_STRUCTURED_JSONL.items()
            },
            "gan2026_llm_with_rules_scores": str(GAN_FLOORS.relative_to(ROOT)).replace("\\", "/"),
            "gan2026_llm_only_test450": str(GAN_LLM_ONLY_TEST450.relative_to(ROOT)).replace(
                "\\", "/"
            ),
            "gan2026_llm_only_dev750": str(GAN_VALIDATION_COMPARISON.relative_to(ROOT)).replace(
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
