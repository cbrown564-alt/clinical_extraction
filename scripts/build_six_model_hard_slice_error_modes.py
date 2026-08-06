#!/usr/bin/env python3
"""Error-mode drill-down inside six-model hard slices.

No new model calls. No locked-test row inspection. See
docs/research/six_model_hard_slice_error_modes_protocol_2026-08-06.md.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    headline_keys,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import load_records_for_split

REPO_ROOT = Path(__file__).resolve().parents[1]
DATE_STAMP = "20260806"
REPORT_DATE = "2026-08-06"
_MULTIPLE_WORD_RE = re.compile(r"\bmultiple\b", re.IGNORECASE)
_STATE_RE = re.compile(r"'(active-rate|seizure-free|unknown)'")

MODEL_SPECS = (
    ("gpt41mini", "GPT-4.1-mini"),
    ("gpt56luna", "GPT-5.6 Luna"),
    ("gpt56sol", "GPT-5.6 Sol"),
    ("deepseek_v4_flash", "DeepSeek V4 Flash"),
    ("qwen36_35b", "Qwen 3.6:35B"),
    ("gemma4_26b", "Gemma 4 26B"),
)

GAN_LLM_ONLY_DIR = REPO_ROOT / "experiments/gan2026_six_model_validation_20260718"
GAN_ATTR = REPO_ROOT / "experiments/gan2026_matched_v05_dev750_attribution_20260727.json"
GAN_FLOORS_PATCH = REPO_ROOT / (
    "experiments/gan2026_six_model_current_floors_replay_20260731/"
    "dev750_changed_rows.jsonl"
)
EXECT_JSONL = {
    "gpt41mini": REPO_ROOT
    / "experiments/exectv2_six_model_single_call_gpt41mini_dev140_20260715.jsonl",
    "gpt56luna": REPO_ROOT
    / "experiments/exectv2_six_model_single_call_gpt56luna_dev140_20260715.jsonl",
    "gpt56sol": REPO_ROOT
    / "experiments/exectv2_six_model_single_call_gpt56sol_dev140_20260715.jsonl",
    "deepseek_v4_flash": REPO_ROOT
    / "experiments/exectv2_deepseek_v4_flash_0731_update_dev140_20260731.jsonl",
    "qwen36_35b": REPO_ROOT
    / "experiments/exectv2_six_model_single_call_qwen36_35b_dev140_20260715.jsonl",
    "gemma4_26b": REPO_ROOT
    / "experiments/exectv2_six_model_single_call_gemma4_26b_dev140_20260715.jsonl",
}

EXEMPLAR_LIMIT = 6


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def _git_note() -> dict[str, Any]:
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            text=True,
        ).strip()
        dirty = bool(
            subprocess.check_output(
                ["git", "status", "--porcelain"],
                cwd=REPO_ROOT,
                text=True,
            ).strip()
        )
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty_tree": None}
    return {"commit": commit, "dirty_tree": dirty}


def _gan_shape_flags(label: str) -> dict[str, bool]:
    text = label.lower().strip()
    return {
        "is_range": " to " in text,
        "is_cluster": "cluster" in text,
        "is_multiple_word": bool(_MULTIPLE_WORD_RE.search(text)),
    }


def _gan_bucket(kind: str, flags: dict[str, bool]) -> str:
    if kind == "frequency" and flags["is_cluster"]:
        return "cluster_burden"
    if kind == "frequency" and flags["is_range"]:
        return "range_rate"
    if kind == "frequency" and flags["is_multiple_word"]:
        return "multiple_word_frequency"
    if kind == "frequency":
        return "ordinary_point_rate"
    if kind == "seizure_free":
        return "seizure_free"
    if kind == "unknown":
        return "unknown_sentinel"
    if kind == "no_reference":
        return "no_reference_sentinel"
    if kind == "unresolved_multiple":
        return "unresolved_multiple"
    return "other"


def _gan_gold_index() -> dict[int, dict[str, Any]]:
    out: dict[int, dict[str, Any]] = {}
    for record in load_records_for_split("validation"):
        kind = record.gold_label_kind.value
        flags = _gan_shape_flags(record.gold_label)
        out[int(record.source_row_index)] = {
            "a_priori_bucket": _gan_bucket(kind, flags),
            "gold_label": record.gold_label,
            "gold_label_kind": kind,
        }
    return out


def _llm_scored_label(row: dict[str, Any]) -> str:
    """Return the label scored by llm_only Purist comparison.

    Prefer decision_record.final_label (post format adapter). Model-boundary
    raw labels are retained separately for diagnostics.
    """

    decision = row.get("decision_record") or {}
    if decision.get("final_label"):
        return str(decision["final_label"])
    raw = (
        ((row.get("row_trace") or {}).get("model_prediction") or {}).get("record") or {}
    ).get("final_label")
    return str(raw or "")


def _llm_model_boundary_label(row: dict[str, Any]) -> str:
    raw = (
        ((row.get("row_trace") or {}).get("model_prediction") or {}).get("record") or {}
    ).get("final_label")
    return str(raw or "")


def _ordinary_error_mode(pred_label: str, comparison: dict[str, Any] | None) -> str:
    if comparison is None or not str(pred_label).strip():
        return "parse_or_call_failure"
    text = pred_label.lower().strip()
    if text == "unknown":
        return "over_abstain_unknown"
    if text == "no seizure frequency reference":
        return "over_abstain_no_reference"
    if text.startswith("seizure free"):
        return "false_seizure_free"
    if "cluster" in text:
        return "false_cluster_structure"
    if " to " in text:
        return "false_range"
    if _MULTIPLE_WORD_RE.search(text) and " per " in text:
        return "false_multiple_word"
    if " per " in text:
        return "wrong_point_rate_selection"
    return "other_malformed_or_unparsed"


def _cluster_error_mode(pred_label: str, comparison: dict[str, Any] | None) -> str:
    if comparison is None or not str(pred_label).strip():
        return "parse_or_call_failure"
    text = pred_label.lower().strip()
    if text == "unknown":
        return "collapse_to_unknown"
    if text == "no seizure frequency reference":
        return "collapse_to_no_reference"
    if text.startswith("seizure free"):
        return "false_seizure_free"
    if "cluster" in text:
        if "per cluster" in text:
            return "wrong_cluster_parameters"
        return "incomplete_cluster_grammar"
    if " per " in text or " to " in text:
        return "dropped_to_smooth_rate"
    return "other_malformed_or_unparsed"


def _load_gan_hybrid_rows() -> dict[str, dict[int, dict[str, Any]]]:
    attr = json.loads(GAN_ATTR.read_text(encoding="utf-8"))
    patch: dict[str, dict[int, dict[str, Any]]] = defaultdict(dict)
    for row in _read_jsonl(GAN_FLOORS_PATCH):
        patch[str(row["slug"])][int(row["source_row_index"])] = row
    out: dict[str, dict[int, dict[str, Any]]] = defaultdict(dict)
    for row in attr["rows"]:
        slug = str(row["model_slug"])
        index = int(row["source_row_index"])
        delta = patch[slug].get(index)
        if delta is not None:
            out[slug][index] = {
                "final_label": str(delta.get("after_label") or row["final_label"]),
                "purist_correct": bool(delta["after_purist"]),
                "model_boundary_label": str(row.get("model_boundary_label") or ""),
                "model_boundary_purist_correct": bool(row.get("model_boundary_purist_correct")),
                "selected_evidence_exact": bool(row.get("selected_evidence_exact")),
                "clinical_subproblem": row.get("clinical_subproblem"),
            }
        else:
            out[slug][index] = {
                "final_label": str(row["final_label"]),
                "purist_correct": bool(row["final_purist_correct"]),
                "model_boundary_label": str(row.get("model_boundary_label") or ""),
                "model_boundary_purist_correct": bool(row.get("model_boundary_purist_correct")),
                "selected_evidence_exact": bool(row.get("selected_evidence_exact")),
                "clinical_subproblem": row.get("clinical_subproblem"),
            }
    return out


def _count_modes(rows: list[dict[str, Any]]) -> dict[str, int]:
    counter: Counter[str] = Counter(str(row["error_mode"]) for row in rows)
    return dict(sorted(counter.items(), key=lambda item: (-item[1], item[0])))


def _consensus_ids(
    wrong_by_model: dict[str, set[Any]],
) -> list[Any]:
    if not wrong_by_model:
        return []
    shared = set.intersection(*wrong_by_model.values()) if wrong_by_model else set()
    return sorted(shared, key=lambda value: (str(type(value)), str(value)))


def _pick_exemplars(
    rows: list[dict[str, Any]],
    *,
    mode_key: str = "error_mode",
    limit: int = EXEMPLAR_LIMIT,
) -> list[dict[str, Any]]:
    by_mode: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_mode[str(row[mode_key])].append(row)
    picked: list[dict[str, Any]] = []
    ordered = sorted(by_mode.items(), key=lambda item: (-len(item[1]), item[0]))
    for _mode, mode_rows in ordered:
        for row in mode_rows[:2]:
            picked.append(row)
            if len(picked) >= limit:
                return picked
        if len(picked) >= limit:
            break
    return picked


def _state_token(key: str) -> str | None:
    match = _STATE_RE.search(key)
    return match.group(1) if match else None


def build_gan_ordinary_llm(
    gold_index: dict[int, dict[str, Any]],
    hybrid: dict[str, dict[int, dict[str, Any]]],
) -> dict[str, Any]:
    per_model: dict[str, Any] = {}
    wrong_by_model: dict[str, set[int]] = {}
    all_wrong_rows: list[dict[str, Any]] = []
    mode_by_row_model: dict[int, dict[str, str]] = defaultdict(dict)
    boundary_mode_rows: list[dict[str, Any]] = []

    for slug, display in MODEL_SPECS:
        rows = _read_jsonl(GAN_LLM_ONLY_DIR / f"{slug}--llm_only.jsonl")
        wrong_rows: list[dict[str, Any]] = []
        n_bucket = 0
        n_correct = 0
        pragmatic_near = 0
        hybrid_rescues = 0
        for row in rows:
            index = int(row["source_row_index"])
            meta = gold_index.get(index)
            if meta is None or meta["a_priori_bucket"] != "ordinary_point_rate":
                continue
            n_bucket += 1
            comparison = row.get("comparison")
            if comparison and comparison.get("purist_correct"):
                n_correct += 1
                continue
            pred_label = _llm_scored_label(row)
            boundary_label = _llm_model_boundary_label(row)
            mode = _ordinary_error_mode(
                pred_label, comparison if isinstance(comparison, dict) else None
            )
            boundary_mode = _ordinary_error_mode(
                boundary_label, comparison if isinstance(comparison, dict) else None
            )
            prag = bool(comparison and comparison.get("pragmatic_correct"))
            if prag:
                pragmatic_near += 1
            hybrid_row = hybrid[slug].get(index)
            rescued = bool(hybrid_row and hybrid_row["purist_correct"])
            if rescued:
                hybrid_rescues += 1
            payload = {
                "model_slug": slug,
                "source_row_index": index,
                "gold_label": meta["gold_label"],
                "predicted_label": pred_label,
                "model_boundary_label": boundary_label,
                "error_mode": mode,
                "model_boundary_error_mode": boundary_mode,
                "pragmatic_near_miss": prag,
                "hybrid_rescues": rescued,
                "gold_purist_category": (comparison or {}).get("gold_purist_category"),
                "predicted_purist_category": (comparison or {}).get(
                    "predicted_purist_category"
                ),
            }
            wrong_rows.append(payload)
            all_wrong_rows.append(payload)
            boundary_mode_rows.append(
                {"error_mode": boundary_mode, "source_row_index": index}
            )
            mode_by_row_model[index][slug] = mode
        wrong_by_model[slug] = {int(item["source_row_index"]) for item in wrong_rows}
        per_model[slug] = {
            "display_name": display,
            "n_bucket": n_bucket,
            "n_correct": n_correct,
            "n_wrong": len(wrong_rows),
            "accuracy": round(n_correct / n_bucket, 4) if n_bucket else None,
            "error_modes": _count_modes(wrong_rows),
            "model_boundary_error_modes": _count_modes(
                [{"error_mode": row["model_boundary_error_mode"]} for row in wrong_rows]
            ),
            "pragmatic_near_miss_among_wrong": pragmatic_near,
            "hybrid_rescue_among_wrong": hybrid_rescues,
            "hybrid_rescue_rate_among_wrong": (
                round(hybrid_rescues / len(wrong_rows), 4) if wrong_rows else None
            ),
        }

    consensus = _consensus_ids(wrong_by_model)
    consensus_modes: Counter[str] = Counter()
    for index in consensus:
        modes = list(mode_by_row_model[index].values())
        if modes and len(set(modes)) == 1:
            consensus_modes[modes[0]] += 1
        else:
            consensus_modes["mixed_mode_across_models"] += 1

    return {
        "slice": "ordinary_point_rate",
        "surface": "llm",
        "split": "dev750",
        "metric": "purist_accuracy",
        "n_gold": sum(
            1 for meta in gold_index.values() if meta["a_priori_bucket"] == "ordinary_point_rate"
        ),
        "models": per_model,
        "consensus_wrong_all_six": {
            "n": len(consensus),
            "source_row_indexes": consensus,
            "mode_agreement": dict(
                sorted(consensus_modes.items(), key=lambda item: (-item[1], item[0]))
            ),
        },
        "pooled_wrong_mode_counts": _count_modes(all_wrong_rows),
        "pooled_model_boundary_mode_counts": _count_modes(boundary_mode_rows),
        "exemplars": _pick_exemplars(
            [
                row
                for row in all_wrong_rows
                if int(row["source_row_index"]) in set(consensus)
            ]
            or all_wrong_rows
        ),
    }


def build_gan_cluster(
    gold_index: dict[int, dict[str, Any]],
    hybrid: dict[str, dict[int, dict[str, Any]]],
    *,
    surface: str,
) -> dict[str, Any]:
    per_model: dict[str, Any] = {}
    wrong_by_model: dict[str, set[int]] = {}
    all_wrong_rows: list[dict[str, Any]] = []
    mode_by_row_model: dict[int, dict[str, str]] = defaultdict(dict)
    boundary_mode_rows: list[dict[str, Any]] = []
    cluster_indexes = {
        index
        for index, meta in gold_index.items()
        if meta["a_priori_bucket"] == "cluster_burden"
    }

    for slug, display in MODEL_SPECS:
        wrong_rows: list[dict[str, Any]] = []
        n_correct = 0
        pragmatic_near = 0
        if surface == "llm":
            rows_by_index = {
                int(row["source_row_index"]): row
                for row in _read_jsonl(GAN_LLM_ONLY_DIR / f"{slug}--llm_only.jsonl")
            }
            for index in sorted(cluster_indexes):
                meta = gold_index[index]
                row = rows_by_index[index]
                comparison = row.get("comparison")
                if comparison and comparison.get("purist_correct"):
                    n_correct += 1
                    continue
                pred_label = _llm_scored_label(row)
                boundary_label = _llm_model_boundary_label(row)
                mode = _cluster_error_mode(
                    pred_label, comparison if isinstance(comparison, dict) else None
                )
                boundary_mode = _cluster_error_mode(
                    boundary_label, comparison if isinstance(comparison, dict) else None
                )
                prag = bool(comparison and comparison.get("pragmatic_correct"))
                if prag:
                    pragmatic_near += 1
                payload = {
                    "model_slug": slug,
                    "source_row_index": index,
                    "gold_label": meta["gold_label"],
                    "predicted_label": pred_label,
                    "model_boundary_label": boundary_label,
                    "error_mode": mode,
                    "model_boundary_error_mode": boundary_mode,
                    "pragmatic_near_miss": prag,
                }
                wrong_rows.append(payload)
                all_wrong_rows.append(payload)
                boundary_mode_rows.append(
                    {"error_mode": boundary_mode, "source_row_index": index}
                )
                mode_by_row_model[index][slug] = mode
        else:
            for index in sorted(cluster_indexes):
                meta = gold_index[index]
                hybrid_row = hybrid[slug][index]
                if hybrid_row["purist_correct"]:
                    n_correct += 1
                    continue
                pred_label = str(hybrid_row["final_label"])
                mode = _cluster_error_mode(pred_label, {"purist_correct": False})
                payload = {
                    "model_slug": slug,
                    "source_row_index": index,
                    "gold_label": meta["gold_label"],
                    "predicted_label": pred_label,
                    "error_mode": mode,
                    "model_boundary_label": hybrid_row["model_boundary_label"],
                    "model_boundary_purist_correct": hybrid_row[
                        "model_boundary_purist_correct"
                    ],
                    "selected_evidence_exact": hybrid_row["selected_evidence_exact"],
                    "clinical_subproblem": hybrid_row["clinical_subproblem"],
                }
                wrong_rows.append(payload)
                all_wrong_rows.append(payload)
                mode_by_row_model[index][slug] = mode

        wrong_by_model[slug] = {int(item["source_row_index"]) for item in wrong_rows}
        n_bucket = len(cluster_indexes)
        model_entry: dict[str, Any] = {
            "display_name": display,
            "n_bucket": n_bucket,
            "n_correct": n_correct,
            "n_wrong": len(wrong_rows),
            "accuracy": round(n_correct / n_bucket, 4) if n_bucket else None,
            "error_modes": _count_modes(wrong_rows),
            "pragmatic_near_miss_among_wrong": (
                pragmatic_near if surface == "llm" else None
            ),
        }
        if surface == "llm":
            model_entry["model_boundary_error_modes"] = _count_modes(
                [
                    {"error_mode": row["model_boundary_error_mode"]}
                    for row in wrong_rows
                ]
            )
        per_model[slug] = model_entry

    consensus = _consensus_ids(wrong_by_model)
    consensus_modes: Counter[str] = Counter()
    for index in consensus:
        modes = list(mode_by_row_model[index].values())
        if modes and len(set(modes)) == 1:
            consensus_modes[modes[0]] += 1
        else:
            consensus_modes["mixed_mode_across_models"] += 1

    exact_among_hybrid_wrong = None
    if surface == "llm_with_rules":
        exact_flags = [
            bool(row.get("selected_evidence_exact"))
            for row in all_wrong_rows
            if "selected_evidence_exact" in row
        ]
        exact_among_hybrid_wrong = {
            "n_wrong_rows_pooled": len(exact_flags),
            "exact_evidence": sum(exact_flags),
            "exact_evidence_rate": (
                round(sum(exact_flags) / len(exact_flags), 4) if exact_flags else None
            ),
        }

    result: dict[str, Any] = {
        "slice": "cluster_burden",
        "surface": surface,
        "split": "dev750",
        "metric": "purist_accuracy",
        "n_gold": len(cluster_indexes),
        "models": per_model,
        "consensus_wrong_all_six": {
            "n": len(consensus),
            "source_row_indexes": consensus,
            "mode_agreement": dict(
                sorted(consensus_modes.items(), key=lambda item: (-item[1], item[0]))
            ),
        },
        "pooled_wrong_mode_counts": _count_modes(all_wrong_rows),
        "exact_evidence_among_wrong": exact_among_hybrid_wrong,
        "exemplars": _pick_exemplars(
            [
                row
                for row in all_wrong_rows
                if int(row["source_row_index"]) in set(consensus)
            ]
            or all_wrong_rows
        ),
    }
    if surface == "llm":
        result["pooled_model_boundary_mode_counts"] = _count_modes(boundary_mode_rows)
    return result


def _exect_mode(gold_keys: list[str], pred_keys: list[str]) -> str:
    gold = Counter(gold_keys)
    pred = Counter(pred_keys)
    fp = sum(max(0, pred[key] - gold.get(key, 0)) for key in pred)
    fn = sum(max(0, gold[key] - pred.get(key, 0)) for key in gold)
    gold_n = sum(gold.values())
    pred_n = sum(pred.values())
    if fp == 0 and fn == 0:
        return "correct_empty" if gold_n == 0 else "correct_nonempty"
    if gold_n == 0 and pred_n > 0:
        return "empty_gold_spurious"
    if gold_n > 0 and pred_n == 0:
        return "missed_all_sf"
    if fp > 0 and fn == 0:
        return "extra_states_only"
    if fn > 0 and fp == 0:
        return "missed_states_only"
    return "substituted_or_mixed"


def build_exect_sf(*, surface: str) -> dict[str, Any]:
    field = "raw_lane_mentions" if surface == "llm" else "predicted_mentions"
    per_model: dict[str, Any] = {}
    imperfect_by_model: dict[str, set[str]] = {}
    all_imperfect: list[dict[str, Any]] = []
    missed_states: Counter[str] = Counter()
    extra_states: Counter[str] = Counter()
    mode_by_letter_model: dict[str, dict[str, str]] = defaultdict(dict)

    for slug, display in MODEL_SPECS:
        rows = _read_jsonl(EXECT_JSONL[slug])
        mode_counts: Counter[str] = Counter()
        imperfect_rows: list[dict[str, Any]] = []
        for row in rows:
            letter_id = str(row["letter_id"])
            gold_keys = headline_keys(row, "SeizureFrequency", field="gold_mentions")
            pred_keys = headline_keys(row, "SeizureFrequency", field=field)
            mode = _exect_mode(gold_keys, pred_keys)
            mode_counts[mode] += 1
            if mode.startswith("correct_"):
                continue
            gold_counter = Counter(gold_keys)
            pred_counter = Counter(pred_keys)
            for key, count in gold_counter.items():
                missing = count - pred_counter.get(key, 0)
                if missing > 0:
                    token = _state_token(key)
                    if token:
                        missed_states[token] += missing
            for key, count in pred_counter.items():
                extra = count - gold_counter.get(key, 0)
                if extra > 0:
                    token = _state_token(key)
                    if token:
                        extra_states[token] += extra
            payload = {
                "model_slug": slug,
                "letter_id": letter_id,
                "error_mode": mode,
                "gold_key_count": len(gold_keys),
                "pred_key_count": len(pred_keys),
                "gold_states": sorted(
                    {token for key in gold_keys if (token := _state_token(key))}
                ),
                "pred_states": sorted(
                    {token for key in pred_keys if (token := _state_token(key))}
                ),
            }
            imperfect_rows.append(payload)
            all_imperfect.append(payload)
            mode_by_letter_model[letter_id][slug] = mode
        imperfect_by_model[slug] = {str(item["letter_id"]) for item in imperfect_rows}
        n_letters = len(rows)
        n_correct = mode_counts.get("correct_empty", 0) + mode_counts.get(
            "correct_nonempty", 0
        )
        per_model[slug] = {
            "display_name": display,
            "prediction_field": field,
            "n_letters": n_letters,
            "n_correct_letters": n_correct,
            "n_imperfect_letters": n_letters - n_correct,
            "letter_exact_rate": round(n_correct / n_letters, 4) if n_letters else None,
            "modes": dict(sorted(mode_counts.items(), key=lambda item: (-item[1], item[0]))),
        }

    consensus = _consensus_ids(imperfect_by_model)
    consensus_modes: Counter[str] = Counter()
    for letter_id in consensus:
        modes = list(mode_by_letter_model[str(letter_id)].values())
        if modes and len(set(modes)) == 1:
            consensus_modes[modes[0]] += 1
        else:
            consensus_modes["mixed_mode_across_models"] += 1

    return {
        "slice": "SeizureFrequency",
        "surface": surface,
        "split": "dev140",
        "metric": "clinical_headline_unit_key_letter_exact",
        "scoring_note": (
            "Letter exactness uses clinical_headline_unit_keys multiset match for "
            "SeizureFrequency only. Aggregate family F1 remains the category-cut metric."
        ),
        "models": per_model,
        "consensus_imperfect_all_six": {
            "n": len(consensus),
            "letter_ids": consensus,
            "mode_agreement": dict(
                sorted(consensus_modes.items(), key=lambda item: (-item[1], item[0]))
            ),
        },
        "pooled_imperfect_mode_counts": _count_modes(all_imperfect),
        "pooled_missed_state_tokens": dict(
            sorted(missed_states.items(), key=lambda item: (-item[1], item[0]))
        ),
        "pooled_extra_state_tokens": dict(
            sorted(extra_states.items(), key=lambda item: (-item[1], item[0]))
        ),
        "exemplars": _pick_exemplars(
            [
                row
                for row in all_imperfect
                if str(row["letter_id"]) in set(consensus)
            ]
            or all_imperfect
        ),
    }


def build_artifact() -> dict[str, Any]:
    gold_index = _gan_gold_index()
    hybrid = _load_gan_hybrid_rows()
    return {
        "schema_version": "six_model.hard_slice_error_modes.v1",
        "date": REPORT_DATE,
        "protocol": "docs/research/six_model_hard_slice_error_modes_protocol_2026-08-06.md",
        "parent_category_cut": (
            "docs/research/six_model_category_cut_performance_2026-08-06.md"
        ),
        "call_mode": "saved_output_no_call",
        "git": _git_note(),
        "models": [
            {"slug": slug, "display_name": display} for slug, display in MODEL_SPECS
        ],
        "gan": {
            "ordinary_point_rate_llm": build_gan_ordinary_llm(gold_index, hybrid),
            "cluster_burden_llm": build_gan_cluster(
                gold_index, hybrid, surface="llm"
            ),
            "cluster_burden_llm_with_rules": build_gan_cluster(
                gold_index, hybrid, surface="llm_with_rules"
            ),
        },
        "exect": {
            "seizure_frequency_llm": build_exect_sf(surface="llm"),
            "seizure_frequency_llm_with_rules": build_exect_sf(
                surface="llm_with_rules"
            ),
        },
        "claim_boundary": (
            "Development hard-slice error modes from retained no-call artifacts. "
            "Not sealed holdout competence, not Decision 0046 method-fill rewrite."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / f"experiments/six_model_hard_slice_error_modes_{DATE_STAMP}.json",
    )
    args = parser.parse_args()
    artifact = build_artifact()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
