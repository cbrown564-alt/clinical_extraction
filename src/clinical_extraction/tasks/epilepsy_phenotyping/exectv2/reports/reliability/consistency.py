"""Consistency and active-surface readouts for reliability analysis."""

from __future__ import annotations

import itertools
from collections import Counter, defaultdict
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.constants import (
    FAMILIES,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.io import run_ref
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.scoring import (
    aggregate_scores,
    clinical_headline_scores,
    headline_keys,
    jaccard,
    letters_for_rows,
    prompt_metadata,
    round_rate,
    row_has_call_error,
    row_mode,
    row_parse_error_count,
    seed_label,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.types import (
    ReliabilityRun,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    benchmark_config_for,
    score_overall,
)


def _active_llm_only_runs() -> tuple[ReliabilityRun, ...]:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
        cross_model_reliability_analysis as reliability_module,
    )

    return reliability_module.ACTIVE_LLM_ONLY_RUNS


def active_llm_only_readout(
    run: ReliabilityRun,
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    gold_letters, pred_letters = letters_for_rows(rows)
    family_scores = clinical_headline_scores(gold_letters, pred_letters)
    overall = aggregate_scores(family_scores.values())
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
        "evidence_validity": round_rate(raw_mentions - invalid, raw_mentions),
        "call_failures": sum(1 for row in rows if row_has_call_error(row)),
        "parse_errors": sum(row_parse_error_count(row) for row in rows),
        "family_f1": {
            family: round(float(score["f1"]), 4) for family, score in family_scores.items()
        },
        "claim_boundary": run.claim_boundary,
    }


def same_prompt_consistency(
    active_rows: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    groups: dict[
        tuple[str, str, str, str, str],
        list[tuple[ReliabilityRun, list[dict[str, Any]]]],
    ] = defaultdict(list)
    for run in _active_llm_only_runs():
        rows = active_rows[run.candidate]
        prompt_version, prompt_profile, temperature = prompt_metadata(rows)
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
            same_prompt_panel(key, artifacts)
            for key, artifacts in sorted(groups.items(), key=lambda item: item[0])
        ],
    }


def same_prompt_panel(
    key: tuple[str, str, str, str, str],
    artifacts: list[tuple[ReliabilityRun, list[dict[str, Any]]]],
) -> dict[str, Any]:
    surface_id, model_label, prompt_version, prompt_profile, temperature = key
    health = live_artifact_health([rows for _, rows in artifacts])
    agreement = family_cell_agreement([rows for _, rows in artifacts])
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
        "seed_labels": [seed_label(run, rows) for run, rows in artifacts],
        "status": status,
        "artifact_rows": [
            {
                **run_ref(run),
                "rows": len(rows),
                "mode": row_mode(rows),
                "seed": seed_label(run, rows),
            }
            for run, rows in artifacts
        ],
        **health,
        "within_model_pairwise_clinical_headline_jaccard": agreement["mean_pairwise_jaccard"],
        "family_cell_agreement": {
            "pairwise_comparisons": agreement["pairwise_comparisons"],
            "cell_count": agreement["cell_count"],
            "exact_family_cell_agreement_rate": agreement["exact_family_cell_agreement_rate"],
        },
        "per_family_disagreement_rates": agreement["per_family_disagreement_rates"],
    }


def live_artifact_health(
    artifacts: list[list[dict[str, Any]]],
) -> dict[str, Any]:
    rows = [row for artifact in artifacts for row in artifact]
    raw_mentions = sum(int(row.get("n_mentions_raw") or 0) for row in rows)
    evidence_invalid_mentions = sum(int(row.get("n_evidence_invalid") or 0) for row in rows)
    schema_failures = sum(row_parse_error_count(row) for row in rows)
    schema_invalid_rows = sum(1 for row in rows if row_parse_error_count(row) > 0)
    call_failures = sum(1 for row in rows if row_has_call_error(row))
    return {
        "rows": len(rows),
        "call_failures": call_failures,
        "schema_failures": schema_failures,
        "schema_invalid_rows": schema_invalid_rows,
        "schema_validity_rate": round_rate(len(rows) - schema_invalid_rows, len(rows)),
        "evidence_invalid_mentions": evidence_invalid_mentions,
        "raw_mentions": raw_mentions,
        "evidence_validity_rate": round_rate(
            raw_mentions - evidence_invalid_mentions, raw_mentions
        ),
    }


def family_cell_agreement(
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
                left_keys = set(headline_keys(left_by_id[letter_id], family))
                right_keys = set(headline_keys(right_by_id[letter_id], family))
                total_cells += 1
                family_counts[family]["cells"] += 1
                jaccards.append(jaccard(left_keys, right_keys))
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
        "mean_pairwise_jaccard": round(sum(jaccards) / len(jaccards), 4) if jaccards else None,
        "exact_family_cell_agreement_rate": round_rate(exact_cells, total_cells),
        "per_family_disagreement_rates": [
            {
                "family": family,
                "cell_count": int(family_counts[family]["cells"]),
                "disagreement_rate": round(
                    1.0
                    - round_rate(
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


def deterministic_replay_stability(
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
        "call_failures": sum(1 for row in rows if row_has_call_error(row)),
        "schema_failures": sum(row_parse_error_count(row) for row in rows),
        "claim_boundary": (
            "Deterministic replay confirms saved-artifact reproducibility only; "
            "it is not within-model live resampling evidence."
        ),
    }
