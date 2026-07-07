"""Summary tables for the cross-model reliability scorecard."""

from __future__ import annotations

import itertools
from collections import defaultdict
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.constants import (
    ACTIVE_LLM_ONLY_RUNS,
    FAMILIES,
    RICH_SCHEMA_RUNS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.io import run_ref
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.scoring import (
    headline_keys,
    round_rate,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.scoring import (
    jaccard as pairwise_jaccard,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.types import (
    ReliabilityRun,
)


def latest_run_check() -> dict[str, Any]:
    # Emit one RunRef per non-control run in each surface. The catalog
    # (catalog.yaml) is the single source of run identity and model_label;
    # the frontend renders a column per distinct model_label, so adding a
    # new model to the catalog automatically appears here without code
    # changes. Control runs (performance/simplicity controls) are excluded
    # because they are not "latest model" diagnostics.
    return {
        "surfaces": [
            {
                "surface_id": "rich_schema_reliability",
                "surface_label": "Rich-schema holistic finding assembly reliability scorecard",
                "latest_runs": [run_ref(run) for run in RICH_SCHEMA_RUNS if not _is_control(run)],
                "replacement_policy": "same-surface comparators retained",
                "rationale": (
                    "These are the final dev140 non-GPT diagnostics for the "
                    "2026-06-22 scorecard surface."
                ),
            },
            {
                "surface_id": "active_llm_only",
                "surface_label": "Active de-duplicated clinical-fact LLM-only workstream",
                "latest_runs": [run_ref(run) for run in ACTIVE_LLM_ONLY_RUNS if not _is_control(run)],
                "replacement_policy": "reported separately; different claim surface",
                "rationale": (
                    "Phase 6 uses model-emitted de-duplicated clinical facts, "
                    "not rich-schema holistic assembly, so it should not replace "
                    "the archived scorecard comparators."
                ),
            },
        ]
    }


def _is_control(run: ReliabilityRun) -> bool:
    """A control run (performance/simplicity control) is not a latest-model diagnostic."""

    return "control" in run.role.lower()


def family_error_table(summaries: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
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
                    "over_emission_rate": round_rate(fp, pred_count),
                    "miss_rate": round_rate(fn, gold_count),
                    "candidate_miss": int(family_errors.get("candidate_miss", 0)),
                    "wrong_detail_selection": int(family_errors.get("wrong_detail_selection", 0)),
                    "projection_gap": int(family_errors.get("projection_gap", 0)),
                    "evidence_failure": evidence_failure,
                    "evidence_valid_error_count": max(0, fp + fn - evidence_failure),
                }
            )
    return rows


def family_parity(summaries: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for run in RICH_SCHEMA_RUNS:
        candidate = summaries[run.candidate]["target_report"]["candidates"][0]
        family_scores = {
            family: float(candidate["headline_scores"][family]["f1"]) for family in FAMILIES
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
                "families_below_0_90": [family for family, f1 in family_scores.items() if f1 < 0.9],
            }
        )
    return rows


def cross_model_agreement(rich_rows: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
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
                left_keys = set(headline_keys(by_candidate[left][letter_id], family))
                right_keys = set(headline_keys(by_candidate[right][letter_id], family))
                score = pairwise_jaccard(left_keys, right_keys)
                family_jaccards.append(score)
                all_jaccards.append(score)
                family_accumulator[family].append(score)
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
                    "exact_cell_agreement_rate": round_rate(family_exact, len(common_ids)),
                    "mean_jaccard": round(sum(family_jaccards) / len(family_jaccards), 4)
                    if family_jaccards
                    else 0.0,
                }
            )
    return {
        "overall": {
            "pair_count": len(list(itertools.combinations(by_candidate, 2))),
            "cell_count": total_cells,
            "exact_cell_agreement_rate": round_rate(exact_cells, total_cells),
            "mean_pairwise_jaccard": round(sum(all_jaccards) / len(all_jaccards), 4)
            if all_jaccards
            else 0.0,
        },
        "by_family": [
            {
                "family": family,
                "mean_pairwise_jaccard": round(sum(values) / len(values), 4) if values else 0.0,
            }
            for family, values in sorted(family_accumulator.items())
        ],
        "pairwise": pair_rows,
    }


def coverage_update() -> list[dict[str, Any]]:
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
