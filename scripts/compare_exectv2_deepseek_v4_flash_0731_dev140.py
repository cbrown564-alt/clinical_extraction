"""Compare DeepSeek V4-Flash-0731 ExECTv2 dev140 re-run to the 2026-07-15 cell.

Development-row analysis only. Reads retained comparator and new update artifacts;
writes a machine-readable diff JSON and prints a short aggregate/row summary.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    score_concept_identity,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    aggregate_scores,
    clinical_headline_scores,
    headline_keys,
    letters_for_rows,
    row_family_score,
    score_dict,
)

ROOT = Path(__file__).resolve().parents[1]
# Ruleset-matched baseline: frozen 2026-07-15 model structured outputs replayed
# through the current deterministic SF/assembly stack (no new model calls).
BASELINE_JSON = ROOT / (
    "experiments/exectv2_deepseek_v4_flash_20260715_model_current_rules_dev140_20260731.json"
)
BASELINE_JSONL = ROOT / (
    "experiments/exectv2_deepseek_v4_flash_20260715_model_current_rules_dev140_20260731.jsonl"
)
UPDATE_JSON = ROOT / (
    "experiments/exectv2_deepseek_v4_flash_0731_update_dev140_20260731.json"
)
UPDATE_JSONL = ROOT / (
    "experiments/exectv2_deepseek_v4_flash_0731_update_dev140_20260731.jsonl"
)
OUT_JSON = ROOT / (
    "experiments/exectv2_deepseek_v4_flash_0731_update_dev140_20260731_vs_20260715_current_rules.json"
)

ENTITIES = ("Diagnosis", "SeizureFrequency", "Prescription", "Investigations")


def _load_jsonl(path: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            rows[str(row["letter_id"])] = row
    return rows


def _headline_block(report: dict[str, Any]) -> dict[str, Any]:
    return report["score_ladder"]["headline_target"]


def _f1_map(block: dict[str, Any]) -> dict[str, float]:
    out = {"overall": float(block["overall"]["f1"])}
    for entity, payload in (block.get("by_indicator") or {}).items():
        out[entity] = float(payload["f1"])
    return out


def _direction(base_f1: float, upd_f1: float) -> str:
    if abs(upd_f1 - base_f1) < 1e-12:
        return "unchanged"
    if upd_f1 > base_f1:
        return "rescue"
    return "regression"


def _panel_scores(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    gold, pred = letters_for_rows(rows)
    scores = clinical_headline_scores(gold, pred)
    # Assembly clinical_headline Diagnosis uses concept_negation, not concept_only.
    scores["Diagnosis"] = score_dict(
        score_concept_identity(gold, pred, "Diagnosis").concept_negation
    )
    scores["overall"] = aggregate_scores([scores[entity] for entity in ENTITIES])
    return scores


def compare() -> dict[str, Any]:
    baseline_report = json.loads(BASELINE_JSON.read_text(encoding="utf-8"))
    update_report = json.loads(UPDATE_JSON.read_text(encoding="utf-8"))
    baseline_rows = _load_jsonl(BASELINE_JSONL)
    update_rows = _load_jsonl(UPDATE_JSONL)

    shared = sorted(set(baseline_rows) & set(update_rows))
    missing_in_update = sorted(set(baseline_rows) - set(update_rows))
    extra_in_update = sorted(set(update_rows) - set(baseline_rows))

    aggregate = {
        "baseline_clinical_headline": _f1_map(_headline_block(baseline_report)),
        "update_clinical_headline": _f1_map(_headline_block(update_report)),
        "delta_clinical_headline": {},
    }
    for key, base_f1 in aggregate["baseline_clinical_headline"].items():
        upd = aggregate["update_clinical_headline"].get(key)
        if upd is None:
            continue
        aggregate["delta_clinical_headline"][key] = round(upd - base_f1, 4)

    baseline_panel = _panel_scores([baseline_rows[lid] for lid in shared])
    update_panel = _panel_scores([update_rows[lid] for lid in shared])

    changed_letters: list[dict[str, Any]] = []
    direction_counts: Counter[str] = Counter()
    family_change_counts: Counter[str] = Counter()
    family_direction: dict[str, Counter[str]] = defaultdict(Counter)

    for letter_id in shared:
        base = baseline_rows[letter_id]
        upd = update_rows[letter_id]
        letter_entry: dict[str, Any] = {
            "letter_id": letter_id,
            "entities": {},
            "any_prediction_change": False,
            "any_correctness_change": False,
        }
        for entity in ENTITIES:
            base_keys = sorted(headline_keys(base, entity))
            upd_keys = sorted(headline_keys(upd, entity))
            base_score = row_family_score(base, entity)
            upd_score = row_family_score(upd, entity)
            prediction_changed = base_keys != upd_keys
            correctness = _direction(float(base_score.f1), float(upd_score.f1))
            entity_entry = {
                "prediction_changed": prediction_changed,
                "baseline_f1": round(float(base_score.f1), 4),
                "update_f1": round(float(upd_score.f1), 4),
                "delta_f1": round(float(upd_score.f1) - float(base_score.f1), 4),
                "correctness_direction": correctness,
                "baseline_tp_fp_fn": [base_score.tp, base_score.fp, base_score.fn],
                "update_tp_fp_fn": [upd_score.tp, upd_score.fp, upd_score.fn],
                "baseline_keys": base_keys,
                "update_keys": upd_keys,
            }
            letter_entry["entities"][entity] = entity_entry
            if prediction_changed:
                letter_entry["any_prediction_change"] = True
                family_change_counts[entity] += 1
            if correctness != "unchanged":
                letter_entry["any_correctness_change"] = True
                family_direction[entity][correctness] += 1
        if letter_entry["any_prediction_change"] or letter_entry["any_correctness_change"]:
            if letter_entry["any_correctness_change"]:
                rescues = sum(
                    1
                    for e in letter_entry["entities"].values()
                    if e["correctness_direction"] == "rescue"
                )
                regs = sum(
                    1
                    for e in letter_entry["entities"].values()
                    if e["correctness_direction"] == "regression"
                )
                if rescues and regs:
                    direction = "mixed"
                elif rescues:
                    direction = "rescue"
                elif regs:
                    direction = "regression"
                else:
                    direction = "prediction_only"
            else:
                direction = "prediction_only"
            letter_entry["letter_direction"] = direction
            direction_counts[direction] += 1
            changed_letters.append(letter_entry)

    examples: dict[str, list[dict[str, Any]]] = {"rescue": [], "regression": []}
    for direction in ("rescue", "regression"):
        ranked: list[tuple[float, dict[str, Any]]] = []
        for letter in changed_letters:
            for entity, payload in letter["entities"].items():
                if payload["correctness_direction"] != direction:
                    continue
                ranked.append(
                    (
                        abs(payload["delta_f1"]),
                        {
                            "letter_id": letter["letter_id"],
                            "entity": entity,
                            "baseline_f1": payload["baseline_f1"],
                            "update_f1": payload["update_f1"],
                            "delta_f1": payload["delta_f1"],
                            "baseline_keys": payload["baseline_keys"][:8],
                            "update_keys": payload["update_keys"][:8],
                        },
                    )
                )
        ranked.sort(key=lambda item: (-item[0], item[1]["letter_id"], item[1]["entity"]))
        examples[direction] = [item[1] for item in ranked[:12]]

    payload = {
        "study": "exectv2_deepseek_v4_flash_0731_update_dev140",
        "date": "2026-07-31",
        "split": "dev140",
        "row_inspection_policy": "dev140_permitted",
        "baseline_kind": "20260715_model_current_rules_no_call_replay",
        "baseline_artifact": str(BASELINE_JSON.relative_to(ROOT).as_posix()),
        "update_artifact": str(UPDATE_JSON.relative_to(ROOT).as_posix()),
        "claim_boundary": (
            "Development provider-update comparison on ExECTv2 dev140 with both "
            "sides assembled under the current deterministic ruleset; baseline "
            "uses frozen 2026-07-15 DeepSeek structured outputs (no new calls). "
            "Not holdout, published benchmark, or clinical validation."
        ),
        "row_coverage": {
            "shared_letters": len(shared),
            "missing_in_update": missing_in_update,
            "extra_in_update": extra_in_update,
        },
        "aggregate": aggregate,
        "jsonl_rescored_clinical_headline": {
            "baseline": {
                entity: {
                    "f1": round(float(score["f1"]), 4),
                    "tp": score["tp"],
                    "fp": score["fp"],
                    "fn": score["fn"],
                }
                for entity, score in baseline_panel.items()
            },
            "update": {
                entity: {
                    "f1": round(float(score["f1"]), 4),
                    "tp": score["tp"],
                    "fp": score["fp"],
                    "fn": score["fn"],
                }
                for entity, score in update_panel.items()
            },
            "delta_f1": {
                entity: round(
                    float(update_panel[entity]["f1"]) - float(baseline_panel[entity]["f1"]),
                    4,
                )
                for entity in baseline_panel
            },
        },
        "lane_diagnostics": {
            "baseline": baseline_report.get("lane_diagnostics"),
            "update": update_report.get("lane_diagnostics"),
        },
        "changed_letter_summary": {
            "n_letters_with_prediction_or_correctness_change": len(changed_letters),
            "direction_counts": dict(direction_counts),
            "family_prediction_change_counts": dict(family_change_counts),
            "family_correctness_direction_counts": {
                entity: dict(counts) for entity, counts in family_direction.items()
            },
        },
        "changed_letters": changed_letters,
        "examples": examples,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def _print_summary(payload: dict[str, Any]) -> None:
    agg = payload["aggregate"]
    print("Aggregate clinical_headline F1 (report score_ladder)")
    keys = ["overall", *ENTITIES]
    for key in keys:
        if key not in agg["baseline_clinical_headline"]:
            continue
        print(
            f"  {key}: "
            f"{agg['baseline_clinical_headline'][key]:.4f} -> "
            f"{agg['update_clinical_headline'][key]:.4f} "
            f"(delta {agg['delta_clinical_headline'][key]:+.4f})"
        )
    print("JSONL rescored delta:", payload["jsonl_rescored_clinical_headline"]["delta_f1"])
    summary = payload["changed_letter_summary"]
    print(
        "Changed letters:",
        summary["n_letters_with_prediction_or_correctness_change"],
        summary["direction_counts"],
    )
    print("Family prediction changes:", summary["family_prediction_change_counts"])
    print("Family correctness:", summary["family_correctness_direction_counts"])
    print("Wrote", OUT_JSON.as_posix())


if __name__ == "__main__":
    _print_summary(compare())
