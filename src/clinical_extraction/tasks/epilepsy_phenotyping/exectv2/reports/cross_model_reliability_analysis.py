"""No-call reliability analysis for the ExECTv2 cross-model scorecard.

This module upgrades the 2026-06-22 reliability scorecard with computed dev140
trust evidence. It deliberately keeps two surfaces separate:

* the rich-schema holistic finding assemblies used by the original scorecard;
* the newer LLM-only de-duplicated clinical-fact Phase 6 runs.

No model calls are made here, and no full-200 or holdout rows are loaded.
"""

from __future__ import annotations

import itertools
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from clinical_extraction.core.scoring import PRF1, multiset_prf1
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.target_indicator_report import (
    TARGET_INDICATORS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability import (
    ReliabilityRun,
    load_active_llm_only_runs,
    load_rich_schema_runs,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    benchmark_config_for,
    clinical_headline_unit_keys,
    score_concept_identity,
    score_frequency_state,
    score_investigations_components,
    score_overall,
    score_prescription_components,
)

FAMILIES: tuple[str, ...] = tuple(TARGET_INDICATORS)

RICH_SCHEMA_RUNS: tuple[ReliabilityRun, ...] = load_rich_schema_runs()
ACTIVE_LLM_ONLY_RUNS: tuple[ReliabilityRun, ...] = load_active_llm_only_runs()

_FAMILY_BASE_RISK = {
    "Diagnosis": 0.22,
    "SeizureFrequency": 0.25,
    "Prescription": 0.16,
    "Investigations": 0.14,
}
_CALIBRATION_FEATURES: tuple[str, ...] = (
    "family:Diagnosis",
    "family:SeizureFrequency",
    "family:Prescription",
    "family:Investigations",
    "evidence_invalid",
    "low_confidence",
    "source_final_delta",
    "active_rate",
    "plan_language",
    "result_state",
    "deterministic_action_count",
    "prediction_count",
)
_PLAN_LANGUAGE = re.compile(
    r"\b(?:plan|planned|future|increase|reduce|switch|commence|start|"
    r"consider|option|suggest|if\s+.*then)\b",
    re.IGNORECASE,
)


def _find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parents[6]


REPO_ROOT = _find_repo_root()


def build_cross_model_reliability_analysis(
    *,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    """Build the computed reliability package for the scorecard payload."""

    from . import robustness_panels

    rich_rows = {
        run.candidate: _load_jsonl(repo_root / run.rows_path)
        for run in RICH_SCHEMA_RUNS
    }
    rich_summaries = {
        run.candidate: _load_json(repo_root / run.summary_path)
        for run in RICH_SCHEMA_RUNS
        if run.summary_path is not None
    }
    active_rows = {
        run.candidate: _load_jsonl(repo_root / run.rows_path)
        for run in ACTIVE_LLM_ONLY_RUNS
    }

    cells = list(_iter_reliability_cells(rich_rows))
    return {
        "analysis_kind": "exectv2_cross_model_reliability_no_call_dev140",
        "claim_boundary": (
            "Computed from saved dev140 artifacts only; no full-200 or holdout "
            "row-level inspection."
        ),
        "latest_run_check": _latest_run_check(),
        "family_error_table": _family_error_table(rich_summaries),
        "family_parity": _family_parity(rich_summaries),
        "cross_model_agreement": _cross_model_agreement(rich_rows),
        "calibration_proxy": _calibration_proxy(cells),
        "review_routing": _review_routing(cells),
        "robustness_panel_preflight": robustness_panels.build_robustness_panel_payload(
            include_case_text=False
        ),
        "active_llm_only_readout": [
            _active_llm_only_readout(run, active_rows[run.candidate])
            for run in ACTIVE_LLM_ONLY_RUNS
        ],
        "same_prompt_consistency": _same_prompt_consistency(active_rows),
        "deterministic_replay_stability": _deterministic_replay_stability(rich_rows),
        "holdout_guardrail": {
            "full_200_or_holdout_rows_loaded": False,
            "blocked_surfaces": ["full-200", "holdout", "test"],
            "policy": (
                "Latest active rows are dev140 only. Any full-200 or holdout "
                "analysis still requires a frozen protocol and explicit authorization."
            ),
        },
        "coverage_update": _coverage_update(),
    }


def _load_json(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _run_ref(run: ReliabilityRun) -> dict[str, str]:
    out = {
        "candidate": run.candidate,
        "model_label": run.model_label,
        "rows_path": run.rows_path.as_posix(),
        "role": run.role,
        "claim_boundary": run.claim_boundary,
    }
    if run.summary_path is not None:
        out["summary_path"] = run.summary_path.as_posix()
    return out


def _latest_run_check() -> dict[str, Any]:
    rich_deepseek = _run_ref(
        next(run for run in RICH_SCHEMA_RUNS if "deepseek" in run.candidate)
    )
    rich_qwen = _run_ref(next(run for run in RICH_SCHEMA_RUNS if "qwen" in run.candidate))
    active_deepseek = _run_ref(
        next(run for run in ACTIVE_LLM_ONLY_RUNS if "deepseek" in run.candidate)
    )
    active_qwen = _run_ref(next(run for run in ACTIVE_LLM_ONLY_RUNS if "qwen" in run.candidate))
    return {
        "surfaces": [
            {
                "surface_id": "rich_schema_reliability",
                "surface_label": "Rich-schema holistic finding assembly reliability scorecard",
                "latest_deepseek": rich_deepseek,
                "latest_qwen": rich_qwen,
                "replacement_policy": "same-surface comparators retained",
                "rationale": (
                    "These are the final dev140 non-GPT diagnostics for the "
                    "2026-06-22 scorecard surface."
                ),
            },
            {
                "surface_id": "active_llm_only",
                "surface_label": "Active de-duplicated clinical-fact LLM-only workstream",
                "latest_deepseek": active_deepseek,
                "latest_qwen": active_qwen,
                "replacement_policy": "reported separately; different claim surface",
                "rationale": (
                    "Phase 6 uses model-emitted de-duplicated clinical facts, "
                    "not rich-schema holistic assembly, so it should not replace "
                    "the archived scorecard comparators."
                ),
            },
        ]
    }


def _family_error_table(summaries: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for run in RICH_SCHEMA_RUNS:
        summary = summaries[run.candidate]
        candidate = summary["target_report"]["candidates"][0]
        errors = candidate.get("error_analysis", {}).get("per_indicator", {})
        for family in FAMILIES:
            score = candidate["headline_scores"][family]
            family_errors = errors.get(family, {})
            pred_count = int(score.get("pred_count", int(score["tp"]) + int(score["fp"])))
            gold_count = int(score.get("gold_count", int(score["tp"]) + int(score["fn"])))
            evidence_failure = int(family_errors.get("evidence_failure", 0))
            fp = int(score["fp"])
            fn = int(score["fn"])
            rows.append(
                {
                    "candidate": run.candidate,
                    "model_label": run.model_label,
                    "family": family,
                    "f1": round(float(score["f1"]), 4),
                    "precision": round(float(score["precision"]), 4),
                    "recall": round(float(score["recall"]), 4),
                    "tp": int(score["tp"]),
                    "fp": fp,
                    "fn": fn,
                    "pred_count": pred_count,
                    "gold_count": gold_count,
                    "over_emission_rate": _round_rate(fp, pred_count),
                    "miss_rate": _round_rate(fn, gold_count),
                    "candidate_miss": int(family_errors.get("candidate_miss", 0)),
                    "wrong_detail_selection": int(
                        family_errors.get("wrong_detail_selection", 0)
                    ),
                    "projection_gap": int(family_errors.get("projection_gap", 0)),
                    "evidence_failure": evidence_failure,
                    "evidence_valid_error_count": max(0, fp + fn - evidence_failure),
                }
            )
    return rows


def _family_parity(summaries: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for run in RICH_SCHEMA_RUNS:
        candidate = summaries[run.candidate]["target_report"]["candidates"][0]
        family_scores = {
            family: float(candidate["headline_scores"][family]["f1"])
            for family in FAMILIES
        }
        worst_family, worst_f1 = min(family_scores.items(), key=lambda item: item[1])
        best_family, best_f1 = max(family_scores.items(), key=lambda item: item[1])
        rows.append(
            {
                "candidate": run.candidate,
                "model_label": run.model_label,
                "worst_family": worst_family,
                "worst_family_f1": round(worst_f1, 4),
                "best_family": best_family,
                "best_family_f1": round(best_f1, 4),
                "family_f1_spread": round(best_f1 - worst_f1, 4),
                "families_below_0_90": [
                    family
                    for family, f1 in family_scores.items()
                    if f1 < 0.9
                ],
            }
        )
    return rows


def _cross_model_agreement(rich_rows: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    by_candidate = {
        candidate: {str(row["letter_id"]): row for row in rows}
        for candidate, rows in rich_rows.items()
    }
    pair_rows: list[dict[str, Any]] = []
    family_accumulator: dict[str, list[float]] = defaultdict(list)
    all_jaccards: list[float] = []
    exact_cells = total_cells = 0
    for left, right in itertools.combinations(by_candidate, 2):
        common_ids = sorted(by_candidate[left].keys() & by_candidate[right].keys())
        for family in FAMILIES:
            family_exact = 0
            family_jaccards: list[float] = []
            for letter_id in common_ids:
                left_keys = set(_headline_keys(by_candidate[left][letter_id], family))
                right_keys = set(_headline_keys(by_candidate[right][letter_id], family))
                jaccard = _jaccard(left_keys, right_keys)
                family_jaccards.append(jaccard)
                all_jaccards.append(jaccard)
                family_accumulator[family].append(jaccard)
                if left_keys == right_keys:
                    family_exact += 1
                    exact_cells += 1
                total_cells += 1
            pair_rows.append(
                {
                    "left_candidate": left,
                    "right_candidate": right,
                    "family": family,
                    "cells": len(common_ids),
                    "exact_cell_agreement_rate": _round_rate(family_exact, len(common_ids)),
                    "mean_jaccard": round(
                        sum(family_jaccards) / len(family_jaccards), 4
                    )
                    if family_jaccards
                    else 0.0,
                }
            )
    return {
        "overall": {
            "pair_count": len(list(itertools.combinations(by_candidate, 2))),
            "cell_count": total_cells,
            "exact_cell_agreement_rate": _round_rate(exact_cells, total_cells),
            "mean_pairwise_jaccard": round(sum(all_jaccards) / len(all_jaccards), 4)
            if all_jaccards
            else 0.0,
        },
        "by_family": [
            {
                "family": family,
                "mean_pairwise_jaccard": round(sum(values) / len(values), 4)
                if values
                else 0.0,
            }
            for family, values in sorted(family_accumulator.items())
        ],
        "pairwise": pair_rows,
    }


def _iter_reliability_cells(
    rich_rows: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    cells: list[dict[str, Any]] = []
    for run in RICH_SCHEMA_RUNS:
        for row in rich_rows[run.candidate]:
            for family in FAMILIES:
                score = _row_family_score(row, family)
                if score.pred_count == 0 and score.gold_count == 0:
                    continue
                features = _risk_features(row, family)
                risk_score = _risk_score(family, features)
                cells.append(
                    {
                        "candidate": run.candidate,
                        "model_label": run.model_label,
                        "letter_id": row["letter_id"],
                        "family": family,
                        "f1": score.f1,
                        "correct": score.fp == 0 and score.fn == 0,
                        "risk_score": risk_score,
                        "confidence_proxy": round(1.0 - risk_score, 4),
                        "features": features,
                    }
                )
    return cells


def _calibration_proxy(cells: list[dict[str, Any]]) -> dict[str, Any]:
    scored = _cross_validated_calibration_scores(cells, fold_count=5)
    pairs = [
        (float(row["calibrated_confidence"]), bool(row["correct"]))
        for row in scored
    ]
    baseline_pairs = [
        (float(row["training_fold_base_rate"]), bool(row["correct"]))
        for row in scored
    ]
    heuristic = _heuristic_calibration_baseline(cells)
    bins = _reliability_bins(scored, bin_count=5)
    per_family = [
        _calibration_summary_for_family(
            str(family),
            [row for row in scored if str(row["family"]) == family],
            baseline_pairs=[
                (float(row["training_fold_base_rate"]), bool(row["correct"]))
                for row in scored
                if str(row["family"]) == family
            ],
        )
        for family in FAMILIES
    ]
    ece = _expected_calibration_error(pairs, bins)
    brier = _brier_score(pairs)
    baseline_brier = _brier_score(baseline_pairs)
    return {
        "definition": (
            "Frozen no-call scoring rule trained by grouped cross-validation over "
            "dev140 rich-schema candidate-family cells. Features are family and "
            "predeclared provenance/evidence ambiguity flags; no full-200 or "
            "holdout rows are loaded."
        ),
        "model_type": "grouped_cross_validated_logistic_scoring_rule",
        "validation_status": (
            "dev140 cross-validated development evidence only; not a full-200 or "
            "holdout calibration claim."
        ),
        "feature_set": list(_CALIBRATION_FEATURES),
        "cell_count": len(scored),
        "fold_count": len({row["fold"] for row in scored}),
        "bin_count": len(bins),
        "expected_calibration_error": round(ece, 4),
        "brier_score": round(brier, 4),
        "constant_base_rate_brier_score": round(baseline_brier, 4),
        "brier_improvement_vs_base_rate": round(baseline_brier - brier, 4),
        "overall_accuracy": round(
            sum(1 for row in scored if row["correct"]) / len(scored), 4
        )
        if scored
        else 0.0,
        "mean_calibrated_confidence": round(
            sum(float(row["calibrated_confidence"]) for row in scored) / len(scored),
            4,
        )
        if scored
        else 0.0,
        "max_adjacent_bin_reversal": _max_adjacent_bin_reversal(bins),
        "leakage_audit": _calibration_leakage_audit(scored),
        "heuristic_baseline": heuristic,
        "bins": bins,
        "per_family": per_family,
    }


def _heuristic_calibration_baseline(cells: list[dict[str, Any]]) -> dict[str, Any]:
    bins: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for cell in cells:
        bins[_confidence_bin(float(cell["confidence_proxy"]))].append(cell)

    rows = []
    total = len(cells)
    ece = 0.0
    for label in ("very_high", "high", "medium", "low"):
        bucket = bins.get(label, [])
        if not bucket:
            continue
        avg_confidence = sum(float(c["confidence_proxy"]) for c in bucket) / len(bucket)
        accuracy = sum(1 for c in bucket if c["correct"]) / len(bucket)
        ece += (len(bucket) / total) * abs(avg_confidence - accuracy)
        rows.append(
            {
                "bin": label,
                "cells": len(bucket),
                "avg_confidence_proxy": round(avg_confidence, 4),
                "accuracy": round(accuracy, 4),
                "mean_cell_f1": round(sum(float(c["f1"]) for c in bucket) / len(bucket), 4),
            }
        )
    return {
        "definition": (
            "External no-call confidence proxy from family, evidence validity, "
            "source-to-final changes, confidence labels, and deterministic action burden."
        ),
        "cell_count": total,
        "bin_count": len(rows),
        "expected_calibration_error": round(ece, 4),
        "brier_score": round(
            _brier_score(
                [
                    (float(cell["confidence_proxy"]), bool(cell["correct"]))
                    for cell in cells
                ]
            ),
            4,
        ),
        "bins": rows,
    }


def _cross_validated_calibration_scores(
    cells: list[dict[str, Any]],
    *,
    fold_count: int,
) -> list[dict[str, Any]]:
    if not cells:
        return []
    folds = _group_folds(cells, fold_count=fold_count)
    scored: list[dict[str, Any]] = []
    for fold_index, test_letters in enumerate(folds):
        train = [cell for cell in cells if str(cell["letter_id"]) not in test_letters]
        test = [cell for cell in cells if str(cell["letter_id"]) in test_letters]
        weights = _fit_logistic_scoring_rule(train)
        train_base_rate = (
            sum(1 for cell in train if bool(cell["correct"])) / len(train)
            if train
            else 0.5
        )
        for cell in test:
            probability = _predict_logistic_probability(weights, cell)
            scored.append(
                {
                    "candidate": cell["candidate"],
                    "model_label": cell["model_label"],
                    "letter_id": cell["letter_id"],
                    "family": cell["family"],
                    "fold": fold_index,
                    "correct": bool(cell["correct"]),
                    "f1": cell["f1"],
                    "calibrated_confidence": round(probability, 6),
                    "training_fold_base_rate": round(train_base_rate, 6),
                }
            )
    return scored


def _group_folds(
    cells: list[dict[str, Any]],
    *,
    fold_count: int,
) -> list[set[str]]:
    letter_ids = sorted({str(cell["letter_id"]) for cell in cells})
    folds = [set() for _ in range(fold_count)]
    for index, letter_id in enumerate(letter_ids):
        folds[index % fold_count].add(letter_id)
    return folds


def _fit_logistic_scoring_rule(cells: list[dict[str, Any]]) -> list[float]:
    weights = [0.0 for _ in range(len(_CALIBRATION_FEATURES) + 1)]
    if not cells:
        return weights
    learning_rate = 0.18
    l2 = 0.015
    epochs = 700
    for _ in range(epochs):
        gradients = [0.0 for _ in weights]
        for cell in cells:
            features = _calibration_vector(cell)
            probability = _sigmoid(
                sum(
                    weight * value
                    for weight, value in zip(weights, features, strict=True)
                )
            )
            target = 1.0 if cell["correct"] else 0.0
            error = probability - target
            for index, value in enumerate(features):
                gradients[index] += error * value
        n = float(len(cells))
        for index in range(len(weights)):
            penalty = 0.0 if index == 0 else l2 * weights[index]
            weights[index] -= learning_rate * ((gradients[index] / n) + penalty)
    return weights


def _predict_logistic_probability(weights: list[float], cell: dict[str, Any]) -> float:
    raw = sum(
        weight * value
        for weight, value in zip(weights, _calibration_vector(cell), strict=True)
    )
    return min(max(_sigmoid(raw), 0.001), 0.999)


def _calibration_vector(cell: dict[str, Any]) -> list[float]:
    features = cell["features"]
    family = str(cell["family"])
    return [
        1.0,
        1.0 if family == "Diagnosis" else 0.0,
        1.0 if family == "SeizureFrequency" else 0.0,
        1.0 if family == "Prescription" else 0.0,
        1.0 if family == "Investigations" else 0.0,
        1.0 if bool(features["evidence_invalid"]) else 0.0,
        1.0 if bool(features["low_confidence"]) else 0.0,
        1.0 if bool(features["source_final_delta"]) else 0.0,
        1.0 if bool(features["active_rate"]) else 0.0,
        1.0 if bool(features["plan_language"]) else 0.0,
        1.0 if bool(features["result_state"]) else 0.0,
        min(float(features["deterministic_action_count"]), 5.0) / 5.0,
        min(float(features["prediction_count"]), 8.0) / 8.0,
    ]


def _sigmoid(value: float) -> float:
    if value >= 0:
        z = math.exp(-value)
        return 1.0 / (1.0 + z)
    z = math.exp(value)
    return z / (1.0 + z)


def _reliability_bins(
    scored: list[dict[str, Any]],
    *,
    bin_count: int,
) -> list[dict[str, Any]]:
    if not scored:
        return []
    ordered = sorted(scored, key=lambda row: float(row["calibrated_confidence"]))
    rows = []
    total = len(ordered)
    for index in range(bin_count):
        start = (index * total) // bin_count
        end = ((index + 1) * total) // bin_count
        bucket = ordered[start:end]
        if not bucket:
            continue
        avg_confidence = sum(float(row["calibrated_confidence"]) for row in bucket) / len(bucket)
        accuracy = sum(1 for row in bucket if row["correct"]) / len(bucket)
        rows.append(
            {
                "bin": f"q{index + 1}",
                "confidence_range": [
                    round(float(bucket[0]["calibrated_confidence"]), 4),
                    round(float(bucket[-1]["calibrated_confidence"]), 4),
                ],
                "cells": len(bucket),
                "avg_confidence_proxy": round(avg_confidence, 4),
                "avg_calibrated_confidence": round(avg_confidence, 4),
                "accuracy": round(accuracy, 4),
                "calibration_gap": round(accuracy - avg_confidence, 4),
                "ece_contribution": round(
                    (len(bucket) / total) * abs(accuracy - avg_confidence),
                    4,
                ),
                "mean_cell_f1": round(
                    sum(float(row["f1"]) for row in bucket) / len(bucket), 4
                ),
            }
        )
    return rows


def _calibration_summary_for_family(
    family: str,
    rows: list[dict[str, Any]],
    *,
    baseline_pairs: list[tuple[float, bool]],
) -> dict[str, Any]:
    pairs = [
        (float(row["calibrated_confidence"]), bool(row["correct"]))
        for row in rows
    ]
    bins = _reliability_bins(rows, bin_count=min(4, len(rows))) if rows else []
    return {
        "family": family,
        "cells": len(rows),
        "accuracy": round(sum(1 for row in rows if row["correct"]) / len(rows), 4)
        if rows
        else 0.0,
        "mean_calibrated_confidence": round(
            sum(float(row["calibrated_confidence"]) for row in rows) / len(rows), 4
        )
        if rows
        else 0.0,
        "expected_calibration_error": round(_expected_calibration_error(pairs, bins), 4),
        "brier_score": round(_brier_score(pairs), 4),
        "constant_base_rate_brier_score": round(_brier_score(baseline_pairs), 4),
        "bin_count": len(bins),
    }


def _expected_calibration_error(
    pairs: list[tuple[float, bool]],
    bins: list[dict[str, Any]],
) -> float:
    total = len(pairs)
    if not total:
        return 0.0
    return sum(float(row["ece_contribution"]) for row in bins)


def _brier_score(pairs: list[tuple[float, bool]]) -> float:
    if not pairs:
        return 0.0
    return sum(
        (float(score) - (1.0 if outcome else 0.0)) ** 2
        for score, outcome in pairs
    ) / len(pairs)


def _max_adjacent_bin_reversal(bins: list[dict[str, Any]]) -> float:
    reversals = [
        max(0.0, float(left["accuracy"]) - float(right["accuracy"]))
        for left, right in zip(bins, bins[1:], strict=False)
    ]
    return round(max(reversals), 4) if reversals else 0.0


def _calibration_leakage_audit(scored: list[dict[str, Any]]) -> dict[str, Any]:
    fold_letters: dict[int, set[str]] = defaultdict(set)
    for row in scored:
        fold_letters[int(row["fold"])].add(str(row["letter_id"]))
    shared = False
    folds = sorted(fold_letters)
    for left, right in itertools.combinations(folds, 2):
        if fold_letters[left] & fold_letters[right]:
            shared = True
            break
    return {
        "surface": "dev140 rich-schema holistic assembly reliability scorecard",
        "group_key": "letter_id",
        "fold_count": len(folds),
        "unique_groups": len(set().union(*fold_letters.values())) if fold_letters else 0,
        "shared_letter_between_train_and_test": shared,
        "forbidden_validation_rows_loaded": False,
        "forbidden_row_level_outputs_emitted": False,
        "candidate_identity_used_as_feature": False,
        "gold_or_failure_residual_used_as_feature": False,
    }


def _review_routing(cells: list[dict[str, Any]]) -> dict[str, Any]:
    reviewed = caught = false_alarm = missed = total_errors = 0
    by_family: dict[str, Counter[str]] = defaultdict(Counter)
    trigger_counts: Counter[str] = Counter()
    for cell in cells:
        triggers = _review_triggers(cell)
        is_error = not bool(cell["correct"])
        if is_error:
            total_errors += 1
        if triggers:
            reviewed += 1
            trigger_counts.update(triggers)
            by_family[str(cell["family"])]["reviewed_cells"] += 1
            if is_error:
                caught += 1
                by_family[str(cell["family"])]["caught_error_cells"] += 1
            else:
                false_alarm += 1
                by_family[str(cell["family"])]["false_alarm_cells"] += 1
        elif is_error:
            missed += 1
            by_family[str(cell["family"])]["missed_error_cells"] += 1
        by_family[str(cell["family"])]["eligible_cells"] += 1
        if is_error:
            by_family[str(cell["family"])]["total_error_cells"] += 1

    return {
        "definition": (
            "Predeclared dev-only review triggers over evidence-invalid cells, "
            "high proxy risk, source-to-final changes, and family-specific ambiguity cues."
        ),
        "eligible_cells": len(cells),
        "reviewed_cells": reviewed,
        "review_burden": _round_rate(reviewed, len(cells)),
        "total_error_cells": total_errors,
        "caught_error_cells": caught,
        "catch_rate": _round_rate(caught, total_errors),
        "false_alarm_cells": false_alarm,
        "missed_error_cells": missed,
        "operating_points": _review_operating_points(cells),
        "trigger_counts": dict(sorted(trigger_counts.items())),
        "by_family": [
            {
                "family": family,
                **dict(counts),
                "review_burden": _round_rate(
                    int(counts["reviewed_cells"]), int(counts["eligible_cells"])
                ),
                "catch_rate": _round_rate(
                    int(counts["caught_error_cells"]), int(counts["total_error_cells"])
                ),
            }
            for family, counts in sorted(by_family.items())
        ],
    }


def _review_operating_points(cells: list[dict[str, Any]]) -> list[dict[str, Any]]:
    points = [
        _operating_point_summary(
            cells,
            point_id="high_recall_predeclared",
            label="High-recall predeclared trigger net",
            rules=[
                "any current review trigger",
                "risk >= 0.35",
                "evidence invalid",
                "family-specific ambiguity cue",
            ],
            validation_status="dev replay only; not a promoted policy",
            review_fn=lambda cell: bool(_review_triggers(cell)),
        ),
        _operating_point_summary(
            cells,
            point_id="risk_ge_030",
            label="Risk proxy >= 0.30",
            rules=["risk >= 0.30"],
            validation_status="dev replay threshold scan",
            review_fn=lambda cell: float(cell["risk_score"]) >= 0.30,
        ),
        _operating_point_summary(
            cells,
            point_id="balanced_dev_candidate",
            label="Balanced dev candidate",
            rules=[
                "risk >= 0.35",
                "source-to-final delta",
                "low confidence",
                "investigation result-state cue",
            ],
            validation_status="dev-tuned candidate; needs frozen validation",
            review_fn=lambda cell: (
                float(cell["risk_score"]) >= 0.35
                or bool(cell["features"]["source_final_delta"])
                or bool(cell["features"]["low_confidence"])
                or bool(cell["features"]["result_state"])
            ),
        ),
        _operating_point_summary(
            cells,
            point_id="transition_focus",
            label="Transition-focused candidate",
            rules=[
                "source-to-final delta",
                "SF active-rate cue",
                "Prescription plan language",
                "Investigation result-state cue",
            ],
            validation_status="dev-tuned candidate; needs frozen validation",
            review_fn=lambda cell: (
                bool(cell["features"]["source_final_delta"])
                or (
                    cell["family"] == "SeizureFrequency"
                    and bool(cell["features"]["active_rate"])
                )
                or (
                    cell["family"] == "Prescription"
                    and bool(cell["features"]["plan_language"])
                )
                or bool(cell["features"]["result_state"])
            ),
        ),
    ]
    high_recall = points[0]
    for point in points:
        point["review_burden_delta_vs_high_recall"] = round(
            float(point["review_burden"]) - float(high_recall["review_burden"]),
            4,
        )
        point["catch_rate_delta_vs_high_recall"] = round(
            float(point["catch_rate"]) - float(high_recall["catch_rate"]),
            4,
        )
    return points


def _operating_point_summary(
    cells: list[dict[str, Any]],
    *,
    point_id: str,
    label: str,
    rules: list[str],
    validation_status: str,
    review_fn: Any,
) -> dict[str, Any]:
    reviewed_cells = [cell for cell in cells if review_fn(cell)]
    total_errors = sum(1 for cell in cells if not cell["correct"])
    caught = sum(1 for cell in reviewed_cells if not cell["correct"])
    false_alarm = sum(1 for cell in reviewed_cells if cell["correct"])
    missed = total_errors - caught
    return {
        "id": point_id,
        "label": label,
        "rules": rules,
        "validation_status": validation_status,
        "eligible_cells": len(cells),
        "reviewed_cells": len(reviewed_cells),
        "review_burden": _round_rate(len(reviewed_cells), len(cells)),
        "total_error_cells": total_errors,
        "caught_error_cells": caught,
        "catch_rate": _round_rate(caught, total_errors),
        "false_alarm_cells": false_alarm,
        "false_alarm_rate": _round_rate(false_alarm, len(reviewed_cells)),
        "missed_error_cells": missed,
    }


def _active_llm_only_readout(
    run: ReliabilityRun,
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    gold_letters, pred_letters = _letters_for_rows(rows)
    family_scores = _clinical_headline_scores(gold_letters, pred_letters)
    overall = _aggregate_scores(family_scores.values())
    invalid = sum(int(row.get("n_evidence_invalid") or 0) for row in rows)
    raw_mentions = sum(int(row.get("n_mentions_raw") or 0) for row in rows)
    strict = score_overall(gold_letters, pred_letters, FAMILIES, benchmark_config_for)
    return {
        "candidate": run.candidate,
        "model_label": run.model_label,
        "rows_path": run.rows_path.as_posix(),
        "rows": len(rows),
        "surface": "active_llm_only_decision_table_sf_inv_clinical_headline",
        "clinical_headline_f1": round(float(overall["f1"]), 4),
        "precision": round(float(overall["precision"]), 4),
        "recall": round(float(overall["recall"]), 4),
        "strict_benchmark_f1": round(strict.per_item.f1, 4),
        "evidence_validity": _round_rate(raw_mentions - invalid, raw_mentions),
        "call_failures": sum(1 for row in rows if _row_has_call_error(row)),
        "parse_errors": sum(_row_parse_error_count(row) for row in rows),
        "family_f1": {
            family: round(float(score["f1"]), 4)
            for family, score in family_scores.items()
        },
        "claim_boundary": run.claim_boundary,
    }


def _same_prompt_consistency(
    active_rows: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    groups: dict[
        tuple[str, str, str, str, str],
        list[tuple[ReliabilityRun, list[dict[str, Any]]]],
    ] = defaultdict(list)
    for run in ACTIVE_LLM_ONLY_RUNS:
        rows = active_rows[run.candidate]
        prompt_version, prompt_profile, temperature = _prompt_metadata(rows)
        groups[
            (
                run.surface_id,
                run.model_label,
                prompt_version,
                prompt_profile,
                temperature,
            )
        ].append((run, rows))

    return {
        "evidence_type": "same_prompt_cross_seed_resampling",
        "analysis_kind": "exectv2_same_prompt_consistency_no_call_dev140",
        "deterministic_replay_included": False,
        "claim_boundary": (
            "Panels use saved live dev140 LLM artifacts only. Agreement metrics "
            "are populated only when at least two artifacts share surface, model, "
            "prompt version/profile, and temperature."
        ),
        "minimum_repeats_for_agreement": 2,
        "panels": [
            _same_prompt_panel(key, artifacts)
            for key, artifacts in sorted(groups.items(), key=lambda item: item[0])
        ],
    }


def _same_prompt_panel(
    key: tuple[str, str, str, str, str],
    artifacts: list[tuple[ReliabilityRun, list[dict[str, Any]]]],
) -> dict[str, Any]:
    surface_id, model_label, prompt_version, prompt_profile, temperature = key
    health = _live_artifact_health([rows for _, rows in artifacts])
    agreement = _family_cell_agreement([rows for _, rows in artifacts])
    repeat_count = len(artifacts)
    status = (
        "computed_saved_live_repeats"
        if repeat_count >= 2
        else "blocked_needs_at_least_two_saved_live_repeats"
    )
    return {
        "surface_id": surface_id,
        "surface_label": "Active de-duplicated clinical-fact LLM-only workstream",
        "model_label": model_label,
        "prompt_version": prompt_version,
        "prompt_profile": prompt_profile,
        "temperature": temperature,
        "repeat_count": repeat_count,
        "seed_or_repeat_count": repeat_count,
        "seed_labels": [_seed_label(run, rows) for run, rows in artifacts],
        "status": status,
        "artifact_rows": [
            {
                **_run_ref(run),
                "rows": len(rows),
                "mode": _row_mode(rows),
                "seed": _seed_label(run, rows),
            }
            for run, rows in artifacts
        ],
        **health,
        "within_model_pairwise_clinical_headline_jaccard": agreement[
            "mean_pairwise_jaccard"
        ],
        "family_cell_agreement": {
            "pairwise_comparisons": agreement["pairwise_comparisons"],
            "cell_count": agreement["cell_count"],
            "exact_family_cell_agreement_rate": agreement[
                "exact_family_cell_agreement_rate"
            ],
        },
        "per_family_disagreement_rates": agreement["per_family_disagreement_rates"],
    }


def _live_artifact_health(
    artifacts: list[list[dict[str, Any]]],
) -> dict[str, Any]:
    rows = [row for artifact in artifacts for row in artifact]
    raw_mentions = sum(int(row.get("n_mentions_raw") or 0) for row in rows)
    evidence_invalid_mentions = sum(int(row.get("n_evidence_invalid") or 0) for row in rows)
    schema_failures = sum(_row_parse_error_count(row) for row in rows)
    schema_invalid_rows = sum(1 for row in rows if _row_parse_error_count(row) > 0)
    call_failures = sum(1 for row in rows if _row_has_call_error(row))
    return {
        "rows": len(rows),
        "call_failures": call_failures,
        "schema_failures": schema_failures,
        "schema_invalid_rows": schema_invalid_rows,
        "schema_validity_rate": _round_rate(len(rows) - schema_invalid_rows, len(rows)),
        "evidence_invalid_mentions": evidence_invalid_mentions,
        "raw_mentions": raw_mentions,
        "evidence_validity_rate": _round_rate(
            raw_mentions - evidence_invalid_mentions, raw_mentions
        ),
    }


def _family_cell_agreement(
    artifacts: list[list[dict[str, Any]]],
) -> dict[str, Any]:
    family_counts: dict[str, Counter[str]] = defaultdict(Counter)
    jaccards: list[float] = []
    total_cells = exact_cells = pairwise_comparisons = 0

    for left_rows, right_rows in itertools.combinations(artifacts, 2):
        pairwise_comparisons += 1
        left_by_id = {str(row["letter_id"]): row for row in left_rows}
        right_by_id = {str(row["letter_id"]): row for row in right_rows}
        common_ids = sorted(left_by_id.keys() & right_by_id.keys())
        for family in FAMILIES:
            for letter_id in common_ids:
                left_keys = set(_headline_keys(left_by_id[letter_id], family))
                right_keys = set(_headline_keys(right_by_id[letter_id], family))
                total_cells += 1
                family_counts[family]["cells"] += 1
                jaccards.append(_jaccard(left_keys, right_keys))
                if left_keys == right_keys:
                    exact_cells += 1
                    family_counts[family]["exact"] += 1

    if pairwise_comparisons == 0:
        return {
            "pairwise_comparisons": 0,
            "cell_count": 0,
            "mean_pairwise_jaccard": None,
            "exact_family_cell_agreement_rate": None,
            "per_family_disagreement_rates": [
                {
                    "family": family,
                    "cell_count": 0,
                    "disagreement_rate": None,
                }
                for family in FAMILIES
            ],
        }

    return {
        "pairwise_comparisons": pairwise_comparisons,
        "cell_count": total_cells,
        "mean_pairwise_jaccard": round(sum(jaccards) / len(jaccards), 4)
        if jaccards
        else None,
        "exact_family_cell_agreement_rate": _round_rate(exact_cells, total_cells),
        "per_family_disagreement_rates": [
            {
                "family": family,
                "cell_count": int(family_counts[family]["cells"]),
                "disagreement_rate": round(
                    1.0
                    - _round_rate(
                        int(family_counts[family]["exact"]),
                        int(family_counts[family]["cells"]),
                    ),
                    4,
                )
                if family_counts[family]["cells"]
                else None,
            }
            for family in FAMILIES
        ],
    }


def _deterministic_replay_stability(
    rich_rows: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    rows = [row for artifact in rich_rows.values() for row in artifact]
    return {
        "evidence_type": "deterministic_replay_stability",
        "same_prompt_consistency_included": False,
        "analysis_kind": "exectv2_saved_artifact_replay_stability_dev140",
        "artifact_count": len(rich_rows),
        "rows": len(rows),
        "replayable_from_saved_jsonl": True,
        "call_failures": sum(1 for row in rows if _row_has_call_error(row)),
        "schema_failures": sum(_row_parse_error_count(row) for row in rows),
        "claim_boundary": (
            "Deterministic replay confirms saved-artifact reproducibility only; "
            "it is not within-model live resampling evidence."
        ),
    }


def _coverage_update() -> list[dict[str, Any]]:
    return [
        {
            "id": "factuality_and_over_inference",
            "coverage": 4,
            "evidence_added": "Per-family FP/FN over-emission and miss-rate table.",
        },
        {
            "id": "calibration",
            "coverage": 4,
            "evidence_added": (
                "Grouped dev140 calibration rule plus aggregate full-200 validation "
                "audit with ECE, Brier, reliability bins, and per-family calibration."
            ),
        },
        {
            "id": "abstention_review_routing",
            "coverage": 4,
            "evidence_added": "Predeclared trigger set with burden/benefit table.",
        },
        {
            "id": "robustness",
            "coverage": 4,
            "evidence_added": "Latest DeepSeek/Qwen transfer rows reported by surface.",
        },
        {
            "id": "consistency",
            "coverage": 4,
            "evidence_added": (
                "Cross-model dev140 agreement plus explicit same-prompt live "
                "resampling panel contract; saved cross-seed repeats are not yet present."
            ),
        },
        {
            "id": "family_parity",
            "coverage": 5,
            "evidence_added": "Residual subtype and parity metrics across all selected models.",
        },
    ]


def _ann(mention: dict[str, Any]) -> ExectAnnotation:
    return ExectAnnotation(
        entity=str(mention.get("entity", "")),
        text=str(mention.get("text", "")),
        attributes={
            str(key): str(value)
            for key, value in (mention.get("attributes") or {}).items()
            if value is not None
        },
    )


def _letters_for_rows(
    rows: list[dict[str, Any]],
) -> tuple[list[ExectLetter], list[ExectLetter]]:
    gold_letters = []
    pred_letters = []
    for row in rows:
        gold_letters.append(
            ExectLetter(
                letter_id=str(row["letter_id"]),
                note_text="",
                annotations=tuple(_ann(mention) for mention in row.get("gold_mentions", [])),
            )
        )
        pred_letters.append(
            ExectLetter(
                letter_id=str(row["letter_id"]),
                note_text="",
                annotations=tuple(
                    _ann(mention) for mention in row.get("predicted_mentions", [])
                ),
            )
        )
    return gold_letters, pred_letters


def _clinical_headline_scores(
    gold_letters: list[ExectLetter],
    pred_letters: list[ExectLetter],
) -> dict[str, dict[str, Any]]:
    return {
        "Diagnosis": _score_dict(
            score_concept_identity(gold_letters, pred_letters, "Diagnosis").concept_only
        ),
        "SeizureFrequency": _score_dict(
            score_frequency_state(gold_letters, pred_letters).clinical_headline
        ),
        "Prescription": _score_dict(
            score_prescription_components(gold_letters, pred_letters).clinical_headline
        ),
        "Investigations": _score_dict(
            score_investigations_components(gold_letters, pred_letters).clinical_headline
        ),
    }


def _score_dict(score: Any) -> dict[str, Any]:
    pred_count = int(getattr(score, "pred_count", score.tp + score.fp))
    gold_count = int(getattr(score, "gold_count", score.tp + score.fn))
    return {
        "tp": score.tp,
        "precision_tp": int(getattr(score, "precision_tp", score.tp)),
        "recall_tp": int(getattr(score, "recall_tp", score.tp)),
        "fp": score.fp,
        "fn": score.fn,
        "pred_count": pred_count,
        "gold_count": gold_count,
        "precision": score.precision,
        "recall": score.recall,
        "f1": score.f1,
    }


def _aggregate_scores(scores: Any) -> dict[str, Any]:
    precision_tp = recall_tp = pred_count = gold_count = 0
    for score in scores:
        precision_tp += int(score.get("precision_tp", score.get("tp", 0)))
        recall_tp += int(score.get("recall_tp", score.get("tp", 0)))
        pred_default = int(score.get("tp", 0)) + int(score.get("fp", 0))
        gold_default = int(score.get("tp", 0)) + int(score.get("fn", 0))
        pred_count += int(score.get("pred_count", pred_default))
        gold_count += int(score.get("gold_count", gold_default))
    precision = precision_tp / pred_count if pred_count else 0.0
    recall = recall_tp / gold_count if gold_count else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "tp": recall_tp,
        "precision_tp": precision_tp,
        "recall_tp": recall_tp,
        "fp": max(0, pred_count - precision_tp),
        "fn": max(0, gold_count - recall_tp),
        "pred_count": pred_count,
        "gold_count": gold_count,
    }


def _headline_keys(
    row: dict[str, Any],
    family: str,
    *,
    field: str = "predicted_mentions",
) -> list[str]:
    mentions = [
        _ann(mention)
        for mention in row.get(field, [])
        if str(mention.get("entity", "")) == family
    ]
    return [repr(key) for key in clinical_headline_unit_keys(family, mentions)]


def _surface_headline_keys(
    row: dict[str, Any],
    family: str,
    surface: str,
) -> list[str]:
    mentions = [
        _ann(mention)
        for mention in (row.get("prediction_surfaces", {}).get(surface) or [])
        if str(mention.get("entity", "")) == family
    ]
    return [repr(key) for key in clinical_headline_unit_keys(family, mentions)]


def _row_family_score(row: dict[str, Any], family: str) -> PRF1:
    return multiset_prf1(
        _headline_keys(row, family, field="gold_mentions"),
        _headline_keys(row, family),
    )


def _risk_features(row: dict[str, Any], family: str) -> dict[str, Any]:
    mentions = [
        mention
        for mention in row.get("predicted_mentions", [])
        if str(mention.get("entity", "")) == family
    ]
    evidence_invalid = any(not bool(mention.get("evidence_valid", True)) for mention in mentions)
    low_confidence = any(
        str(mention.get("confidence", "high")).lower() not in {"", "high"}
        for mention in mentions
    )
    deterministic_actions = _deterministic_action_count(mentions)
    source_final_delta = (
        _surface_headline_keys(row, family, "source_scored")
        != _surface_headline_keys(row, family, "final")
        if row.get("prediction_surfaces")
        else False
    )
    active_rate = any(
        mention.get("attributes", {}).get("NumberOfSeizures")
        or mention.get("attributes", {}).get("LowerNumberOfSeizures")
        or mention.get("attributes", {}).get("UpperNumberOfSeizures")
        for mention in mentions
    )
    plan_language = any(
        _PLAN_LANGUAGE.search(str(mention.get("evidence", "")))
        or _PLAN_LANGUAGE.search(str(mention.get("text", "")))
        for mention in mentions
    )
    result_state = any(
        key.endswith("_Results") or key.endswith("_Performed")
        for mention in mentions
        for key in (mention.get("attributes") or {})
    )
    return {
        "evidence_invalid": evidence_invalid,
        "low_confidence": low_confidence,
        "deterministic_action_count": deterministic_actions,
        "source_final_delta": source_final_delta,
        "active_rate": active_rate,
        "plan_language": plan_language,
        "result_state": result_state,
        "prediction_count": len(mentions),
    }


def _risk_score(family: str, features: dict[str, Any]) -> float:
    score = _FAMILY_BASE_RISK.get(family, 0.18)
    if features["evidence_invalid"]:
        score += 0.25
    if features["source_final_delta"]:
        score += 0.12
    if int(features["deterministic_action_count"]) > 0:
        score += 0.10
    if features["low_confidence"]:
        score += 0.08
    if family == "SeizureFrequency" and features["active_rate"]:
        score += 0.08
    if family == "Prescription" and features["plan_language"]:
        score += 0.08
    if family == "Investigations" and features["result_state"]:
        score += 0.04
    return round(min(score, 0.95), 4)


def _review_triggers(cell: dict[str, Any]) -> list[str]:
    family = str(cell["family"])
    features = cell["features"]
    triggers = []
    if float(cell["risk_score"]) >= 0.35:
        triggers.append("high_proxy_risk")
    if features["evidence_invalid"]:
        triggers.append("evidence_invalid")
    if family == "Diagnosis" and int(features["deterministic_action_count"]) > 0:
        triggers.append("diagnosis_convention_or_assertion_repair")
    if family == "SeizureFrequency" and (
        features["source_final_delta"] or features["active_rate"]
    ):
        triggers.append("sf_state_or_rate_fidelity")
    if family == "Prescription" and (
        features["plan_language"] or int(features["deterministic_action_count"]) > 0
    ):
        triggers.append("prescription_current_vs_plan")
    if family == "Investigations" and (
        features["result_state"] and int(features["deterministic_action_count"]) > 0
    ):
        triggers.append("investigations_result_state")
    return sorted(set(triggers))


def _deterministic_action_count(mentions: list[dict[str, Any]]) -> int:
    count = 0
    for mention in mentions:
        for event in mention.get("provenance") or []:
            action = str(event.get("action", "")).lower()
            owner = str(event.get("owner", "")).lower()
            if (
                "repair" in action
                or "suppress" in action
                or "added" in action
                or "recovery" in action
                or "deterministic" in owner
            ):
                count += 1
    return count


def _confidence_bin(confidence: float) -> str:
    if confidence >= 0.78:
        return "very_high"
    if confidence >= 0.65:
        return "high"
    if confidence >= 0.5:
        return "medium"
    return "low"


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left and not right:
        return 1.0
    union = left | right
    return len(left & right) / len(union) if union else 1.0


def _round_rate(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0


def _row_has_call_error(row: dict[str, Any]) -> bool:
    if (
        row.get("call_error")
        or row.get("generation_call_error")
        or row.get("selection_call_error")
    ):
        return True
    family_errors = row.get("dedup_fact_call_errors_by_family") or {}
    return any(family_errors.values())


def _row_parse_error_count(row: dict[str, Any]) -> int:
    fields = (
        "parse_errors",
        "generation_parse_errors",
        "inventory_parse_errors",
        "selection_parse_errors",
        "adapter_parse_errors",
    )
    return sum(len(row.get(field) or []) for field in fields)


def _prompt_metadata(rows: list[dict[str, Any]]) -> tuple[str, str, str]:
    if not rows:
        return "unknown", "unknown", "unknown"
    first = rows[0]
    return (
        str(first.get("prompt_version") or "unknown"),
        str(first.get("prompt_profile") or "unknown"),
        str(first.get("temperature") or first.get("sampling_temperature") or "not_recorded"),
    )


def _row_mode(rows: list[dict[str, Any]]) -> str:
    modes = {str(row.get("mode") or "unknown") for row in rows}
    if len(modes) == 1:
        return next(iter(modes))
    return "mixed"


def _seed_label(run: ReliabilityRun, rows: list[dict[str, Any]]) -> str:
    seeds = {
        str(row.get("seed") or row.get("sampling_seed") or row.get("repeat_id") or "")
        for row in rows
    }
    seeds.discard("")
    if len(seeds) == 1:
        return next(iter(seeds))
    if len(seeds) > 1:
        return "mixed"
    return run.candidate
