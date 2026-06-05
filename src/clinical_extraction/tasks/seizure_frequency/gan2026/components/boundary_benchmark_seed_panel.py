"""H3/H7 seed panel for seizure-free boundary and benchmark convention mechanisms."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)

PANEL_NAME = "gan2026_boundary_benchmark_seed_panel_v0"
POLICY_NAME = PANEL_NAME
SYNTHETIC_SOURCE_INDEX_BASE = 930_000
DEFAULT_OUTPUT_JSONL_PATH = Path(
    "experiments/gan2026_boundary_benchmark_seed_panel_v0_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_boundary_benchmark_seed_panel_v0_2026-06-05.json"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    "experiments/gan2026_boundary_benchmark_seed_panel_v0_2026-06-05.md"
)


def build_seed_panel_rows() -> list[dict[str, Any]]:
    """Build deterministic synthetic H3/H7 seed rows."""

    rows = []
    for offset, spec in enumerate(_case_specs()):
        rows.append(
            {
                "artifact_kind": "gan2026_boundary_benchmark_seed_panel_row",
                "policy_name": POLICY_NAME,
                "source_row_index": SYNTHETIC_SOURCE_INDEX_BASE + offset,
                "split": "synthetic_hard_control",
                "split_manifest": PANEL_NAME,
                "hypothesis_ids": spec["hypothesis_ids"],
                "pair_id": spec["pair_id"],
                "pair_variant": spec["pair_variant"],
                "panel_role": spec["panel_role"],
                "target_family": spec["target_family"],
                "target_mechanism": spec["target_mechanism"],
                "expected_component": spec["expected_component"],
                "expected_candidate_exposure": spec["expected_candidate_exposure"],
                "expected_boundary_state": spec["expected_boundary_state"],
                "expected_clinical_final_state": spec["expected_clinical_final_state"],
                "expected_gan_rendered_label": spec["expected_gan_rendered_label"],
                "expected_benchmark_policy_id": spec["expected_benchmark_policy_id"],
                "expected_benchmark_format_rule_id": spec[
                    "expected_benchmark_format_rule_id"
                ],
                "expected_format_only_change": spec["expected_format_only_change"],
                "expected_scorer_sentinel_used": spec["expected_scorer_sentinel_used"],
                "expected_evidence_substring": spec["expected_evidence_substring"],
                "source_note_text": spec["source_note_text"],
                "promotion_scope": "panel_seed_only_no_final_label_promotion",
                "claim_boundary": "synthetic_development_only_no_holdout_use",
            }
        )
    return rows


def summarize_seed_panel_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize panel contract and pair-level invariance."""

    exact_evidence_rows = sum(
        str(row["expected_evidence_substring"]) in str(row["source_note_text"])
        for row in rows
    )
    pair_rows = _rows_by_pair(rows)
    invariant_pairs = sum(_pair_clinical_state_invariant(pair) for pair in pair_rows.values())
    renderer_rows = [
        row for row in rows if row["target_mechanism"] == "benchmark_convention_renderer_v0"
    ]
    boundary_rows = [
        row for row in rows if row["target_mechanism"] == "seizure_free_boundary_event_v0"
    ]
    return {
        "artifact_kind": "gan2026_boundary_benchmark_seed_panel_summary",
        "policy_name": POLICY_NAME,
        "row_count": len(rows),
        "pair_count": len(pair_rows),
        "clinical_state_invariant_pairs": invariant_pairs,
        "exact_evidence_rows": exact_evidence_rows,
        "boundary_rows": len(boundary_rows),
        "renderer_rows": len(renderer_rows),
        "hard_rows": sum(row["panel_role"] == "hard" for row in rows),
        "control_rows": sum(row["panel_role"] == "control" for row in rows),
        "target_family_counts": dict(
            sorted(Counter(str(row["target_family"]) for row in rows).items())
        ),
        "target_mechanism_counts": dict(
            sorted(Counter(str(row["target_mechanism"]) for row in rows).items())
        ),
        "boundary_state_counts": dict(
            sorted(Counter(str(row["expected_boundary_state"]) for row in rows).items())
        ),
        "benchmark_rule_counts": dict(
            sorted(
                Counter(
                    str(row["expected_benchmark_format_rule_id"]) for row in renderer_rows
                ).items()
            )
        ),
        "claim_boundary": (
            "Synthetic H3/H7 mechanism seed panel. It tests typed candidate exposure, "
            "seizure-free boundary state, benchmark-renderer transparency, and "
            "minimal-pair consistency. It is not validation750, not holdout, and not "
            "final-label promotion evidence."
        ),
        "decision": (
            "ready_for_boundary_renderer_contract_tests"
            if rows
            and exact_evidence_rows == len(rows)
            and invariant_pairs == len(pair_rows)
            and boundary_rows
            and renderer_rows
            else "panel_contract_failed"
        ),
        "recommended_next_step": (
            "Port only the stable typed boundary and benchmark-renderer fields to a "
            "validation hard-slice panel. Keep final-label policy disconnected until "
            "the validation mechanism surface is robust."
        ),
    }


def materialize_seed_panel(
    *,
    output_jsonl_path: Path = DEFAULT_OUTPUT_JSONL_PATH,
    output_json_path: Path = DEFAULT_OUTPUT_JSON_PATH,
    output_report_path: Path = DEFAULT_OUTPUT_REPORT_PATH,
) -> dict[str, Any]:
    rows = build_seed_panel_rows()
    summary = summarize_seed_panel_rows(rows)
    summary = {
        **summary,
        "jsonl_artifact": str(output_jsonl_path),
        "json_artifact": str(output_json_path),
        "report_artifact": str(output_report_path),
    }
    write_jsonl_rows(rows, output_jsonl_path)
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(summary, output_report_path)
    return summary


def write_report(summary: Mapping[str, Any], path: Path) -> None:
    lines = [
        "# Gan 2026 Boundary/Benchmark Seed Panel v0",
        "",
        str(summary["claim_boundary"]),
        "",
        "## Decision",
        "",
        str(summary["decision"]),
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| rows | {summary['row_count']} |",
        f"| pairs | {summary['pair_count']} |",
        f"| clinical-state invariant pairs | {summary['clinical_state_invariant_pairs']} |",
        f"| exact evidence rows | {summary['exact_evidence_rows']} |",
        f"| boundary rows | {summary['boundary_rows']} |",
        f"| renderer rows | {summary['renderer_rows']} |",
        f"| hard rows | {summary['hard_rows']} |",
        f"| control rows | {summary['control_rows']} |",
        "",
        "## Target Families",
        "",
        "| Family | Rows |",
        "| --- | ---: |",
    ]
    for family, count in summary["target_family_counts"].items():
        lines.append(f"| `{family}` | {count} |")
    lines.extend(
        [
            "",
            "## Target Mechanisms",
            "",
            "| Mechanism | Rows |",
            "| --- | ---: |",
        ]
    )
    for mechanism, count in summary["target_mechanism_counts"].items():
        lines.append(f"| `{mechanism}` | {count} |")
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            str(summary["recommended_next_step"]),
            "",
            "## Artifacts",
            "",
            f"- Panel JSONL: `{summary['jsonl_artifact']}`",
            f"- Summary JSON: `{summary['json_artifact']}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _rows_by_pair(rows: Sequence[Mapping[str, Any]]) -> dict[str, list[Mapping[str, Any]]]:
    pairs: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        pairs[str(row["pair_id"])].append(row)
    return pairs


def _pair_clinical_state_invariant(rows: Sequence[Mapping[str, Any]]) -> bool:
    return len({str(row["expected_clinical_final_state"]) for row in rows}) == 1


def _case_specs() -> list[dict[str, Any]]:
    seed_cases = [
        _boundary_case(
            pair_id="sf_asserted_interval",
            pair_variant="no_seizures_since",
            panel_role="hard",
            target_family="seizure_free_duration",
            boundary_state="asserted_seizure_free_interval",
            clinical_state="seizure_free_interval",
            gan_label="seizure free for multiple month",
            evidence="no seizures since January 2024",
            note=(
                "Interval history: no seizures since January 2024. Medication "
                "adherence is stable and no rescue treatment was needed."
            ),
        ),
        _boundary_case(
            pair_id="sf_asserted_interval",
            pair_variant="seizure_free_wording",
            panel_role="hard",
            target_family="seizure_free_duration",
            boundary_state="asserted_seizure_free_interval",
            clinical_state="seizure_free_interval",
            gan_label="seizure free for multiple month",
            evidence="seizure-free since January 2024",
            note=(
                "Interval history: seizure-free since January 2024. Medication "
                "adherence is stable and no rescue treatment was needed."
            ),
        ),
        _boundary_case(
            pair_id="last_event_only",
            pair_variant="last_seizure_statement",
            panel_role="hard",
            target_family="seizure_free_duration",
            boundary_state="last_event_only",
            clinical_state="last_event_only",
            gan_label="unknown",
            evidence="last seizure was in January 2024",
            note=(
                "Interval history: last seizure was in January 2024. The letter "
                "does not state whether events stopped after that date."
            ),
        ),
        _boundary_case(
            pair_id="last_event_only",
            pair_variant="most_recent_event_statement",
            panel_role="hard",
            target_family="seizure_free_duration",
            boundary_state="last_event_only",
            clinical_state="last_event_only",
            gan_label="unknown",
            evidence="most recent seizure occurred in January 2024",
            note=(
                "Interval history: most recent seizure occurred in January 2024. "
                "The letter does not state whether events stopped after that date."
            ),
        ),
        _boundary_case(
            pair_id="residual_active_semiology",
            pair_variant="seizure_free_generalized_first",
            panel_role="hard",
            target_family="seizure_free_duration",
            boundary_state="residual_seizure_activity",
            clinical_state="active_residual_seizure_frequency",
            gan_label="2 per week",
            evidence="focal aware seizures continue twice weekly",
            note=(
                "No generalized convulsions for two years. However, focal aware "
                "seizures continue twice weekly and remain the active seizure type."
            ),
        ),
        _boundary_case(
            pair_id="residual_active_semiology",
            pair_variant="active_focal_first",
            panel_role="control",
            target_family="seizure_free_duration",
            boundary_state="residual_seizure_activity",
            clinical_state="active_residual_seizure_frequency",
            gan_label="2 per week",
            evidence="Focal aware seizures continue twice weekly",
            note=(
                "Focal aware seizures continue twice weekly and remain the active "
                "seizure type. There have been no generalized convulsions for two years."
            ),
        ),
        _renderer_case(
            pair_id="unresolved_cluster_burden",
            pair_variant="cadence_then_burden",
            panel_role="hard",
            target_family="benchmark_format_convention",
            clinical_state="cluster_frequency_with_unresolved_burden",
            gan_label="1 cluster per 4 to 5 week, multiple per cluster",
            rule_id="gan_cluster_multiple_per_cluster",
            scorer_sentinel_used=True,
            evidence="one cluster every four to five weeks with several seizures per cluster",
            note=(
                "Diary summary: one cluster every four to five weeks with several "
                "seizures per cluster. Exact within-cluster count is not recorded."
            ),
        ),
        _renderer_case(
            pair_id="unresolved_cluster_burden",
            pair_variant="burden_then_cadence",
            panel_role="hard",
            target_family="benchmark_format_convention",
            clinical_state="cluster_frequency_with_unresolved_burden",
            gan_label="1 cluster per 4 to 5 week, multiple per cluster",
            rule_id="gan_cluster_multiple_per_cluster",
            scorer_sentinel_used=True,
            evidence="several seizures per cluster about every four to five weeks",
            note=(
                "Diary summary: several seizures per cluster about every four to "
                "five weeks. Exact within-cluster count is not recorded."
            ),
        ),
        _renderer_case(
            pair_id="unknown_no_reference_sentinel",
            pair_variant="unknown_frequency_evidence",
            panel_role="hard",
            target_family="benchmark_format_convention",
            clinical_state="unknown_frequency",
            gan_label="unknown",
            rule_id="gan_unknown_sentinel",
            scorer_sentinel_used=True,
            evidence="events continue but the frequency is unclear",
            note=(
                "Interval history: events continue but the frequency is unclear. "
                "There is seizure-frequency evidence, but no usable denominator."
            ),
        ),
        _renderer_case(
            pair_id="unknown_no_reference_sentinel",
            pair_variant="no_reference_evidence",
            panel_role="control",
            target_family="benchmark_format_convention",
            clinical_state="unknown_frequency",
            gan_label="unknown",
            rule_id="gan_unknown_sentinel",
            scorer_sentinel_used=True,
            evidence="no seizure-frequency history is documented",
            note=(
                "Interval history: no seizure-frequency history is documented. "
                "The note focuses on medication side effects."
            ),
        ),
        _renderer_case(
            pair_id="vague_multiple_frequency",
            pair_variant="multiple_current_events",
            panel_role="hard",
            target_family="benchmark_format_convention",
            clinical_state="vague_multiple_current_events",
            gan_label="multiple per month",
            rule_id="gan_vague_multiple_frequency",
            scorer_sentinel_used=True,
            evidence="multiple seizures each month",
            note=(
                "Interval history: multiple seizures each month, but the family "
                "cannot give a reliable numeric count."
            ),
        ),
        _renderer_case(
            pair_id="vague_multiple_frequency",
            pair_variant="several_current_events",
            panel_role="hard",
            target_family="benchmark_format_convention",
            clinical_state="vague_multiple_current_events",
            gan_label="multiple per month",
            rule_id="gan_vague_multiple_frequency",
            scorer_sentinel_used=True,
            evidence="several seizures in a typical month",
            note=(
                "Interval history: several seizures in a typical month, but the "
                "family cannot give a reliable numeric count."
            ),
        ),
    ]
    return seed_cases + _generated_case_specs()


def _generated_case_specs() -> list[dict[str, Any]]:
    return [
        _boundary_case(
            pair_id="sf_asserted_interval_generated",
            pair_variant="free_for_six_months",
            panel_role="hard",
            target_family="seizure_free_duration",
            boundary_state="asserted_seizure_free_interval",
            clinical_state="seizure_free_interval",
            gan_label="seizure free for multiple month",
            evidence="free of seizures for six months",
            note=(
                "Follow-up note: free of seizures for six months. There are no "
                "current spells reported by the family."
            ),
        ),
        _boundary_case(
            pair_id="sf_asserted_interval_generated",
            pair_variant="no_events_for_half_year",
            panel_role="hard",
            target_family="seizure_free_duration",
            boundary_state="asserted_seizure_free_interval",
            clinical_state="seizure_free_interval",
            gan_label="seizure free for multiple month",
            evidence="no epileptic events for the past half year",
            note=(
                "Follow-up note: no epileptic events for the past half year. "
                "Medication has not changed."
            ),
        ),
        _boundary_case(
            pair_id="last_event_only_generated",
            pair_variant="last_event_in_march",
            panel_role="hard",
            target_family="seizure_free_duration",
            boundary_state="last_event_only",
            clinical_state="last_event_only",
            gan_label="unknown",
            evidence="last event was in March 2024",
            note=(
                "Interval history: last event was in March 2024. The note does not "
                "say whether events stopped after March."
            ),
        ),
        _boundary_case(
            pair_id="last_event_only_generated",
            pair_variant="most_recent_event_in_march",
            panel_role="hard",
            target_family="seizure_free_duration",
            boundary_state="last_event_only",
            clinical_state="last_event_only",
            gan_label="unknown",
            evidence="most recent epileptic event occurred in March 2024",
            note=(
                "Interval history: most recent epileptic event occurred in March 2024. "
                "The note does not say whether events stopped after March."
            ),
        ),
        _boundary_case(
            pair_id="conditional_trigger_only",
            pair_variant="missed_medication_trigger",
            panel_role="hard",
            target_family="seizure_free_duration",
            boundary_state="conditional_or_trigger_only",
            clinical_state="conditional_or_trigger_only",
            gan_label="unknown",
            evidence="seizures occur only when medication doses are missed",
            note=(
                "History: seizures occur only when medication doses are missed. "
                "No baseline unprovoked frequency is documented."
            ),
        ),
        _boundary_case(
            pair_id="conditional_trigger_only",
            pair_variant="sleep_deprivation_trigger",
            panel_role="control",
            target_family="seizure_free_duration",
            boundary_state="conditional_or_trigger_only",
            clinical_state="conditional_or_trigger_only",
            gan_label="unknown",
            evidence="events are only reported after sleep deprivation",
            note=(
                "History: events are only reported after sleep deprivation. "
                "No baseline unprovoked frequency is documented."
            ),
        ),
        _boundary_case(
            pair_id="non_epileptic_current_events",
            pair_variant="current_nonepileptic_spells",
            panel_role="hard",
            target_family="seizure_free_duration",
            boundary_state="non_epileptic_current_events",
            clinical_state="non_epileptic_current_events",
            gan_label="seizure free for multiple year",
            evidence="current shaking spells are non-epileptic",
            note=(
                "Assessment: current shaking spells are non-epileptic. No epileptic "
                "seizures have occurred for two years."
            ),
        ),
        _boundary_case(
            pair_id="non_epileptic_current_events",
            pair_variant="functional_events_current",
            panel_role="control",
            target_family="seizure_free_duration",
            boundary_state="non_epileptic_current_events",
            clinical_state="non_epileptic_current_events",
            gan_label="seizure free for multiple year",
            evidence="functional events continue but are not epileptic seizures",
            note=(
                "Assessment: functional events continue but are not epileptic seizures. "
                "No epileptic seizures have occurred for two years."
            ),
        ),
        _boundary_case(
            pair_id="residual_active_semiology_generated",
            pair_variant="absence_active_after_convulsion_free",
            panel_role="hard",
            target_family="seizure_free_duration",
            boundary_state="residual_seizure_activity",
            clinical_state="active_residual_seizure_frequency",
            gan_label="3 per month",
            evidence="absence seizures continue three times monthly",
            note=(
                "No convulsions for one year. However, absence seizures continue "
                "three times monthly and remain the active seizure type."
            ),
        ),
        _boundary_case(
            pair_id="residual_active_semiology_generated",
            pair_variant="active_absence_first",
            panel_role="control",
            target_family="seizure_free_duration",
            boundary_state="residual_seizure_activity",
            clinical_state="active_residual_seizure_frequency",
            gan_label="3 per month",
            evidence="Absence seizures continue three times monthly",
            note=(
                "Absence seizures continue three times monthly and remain the active "
                "seizure type. There have been no convulsions for one year."
            ),
        ),
        _boundary_case(
            pair_id="no_boundary_evidence",
            pair_variant="medication_only",
            panel_role="control",
            target_family="seizure_free_duration",
            boundary_state="no_boundary_evidence",
            clinical_state="no_boundary_evidence",
            gan_label="no seizure frequency reference",
            evidence="medication side effects are reviewed",
            note=(
                "Clinic note: medication side effects are reviewed. No seizure "
                "frequency or seizure-free interval is documented."
            ),
        ),
        _boundary_case(
            pair_id="no_boundary_evidence",
            pair_variant="school_update_only",
            panel_role="control",
            target_family="seizure_free_duration",
            boundary_state="no_boundary_evidence",
            clinical_state="no_boundary_evidence",
            gan_label="no seizure frequency reference",
            evidence="school performance is discussed",
            note=(
                "Clinic note: school performance is discussed. No seizure frequency "
                "or seizure-free interval is documented."
            ),
        ),
        _boundary_case(
            pair_id="conditional_trigger_ordering",
            pair_variant="trigger_before_free_text",
            panel_role="hard",
            target_family="seizure_free_duration",
            boundary_state="conditional_or_trigger_only",
            clinical_state="conditional_or_trigger_only",
            gan_label="unknown",
            evidence="breakthrough seizures happen only with fever",
            note=(
                "Family reports breakthrough seizures happen only with fever. "
                "Between illnesses he is described as seizure-free."
            ),
        ),
        _boundary_case(
            pair_id="conditional_trigger_ordering",
            pair_variant="free_text_before_trigger",
            panel_role="control",
            target_family="seizure_free_duration",
            boundary_state="conditional_or_trigger_only",
            clinical_state="conditional_or_trigger_only",
            gan_label="unknown",
            evidence="breakthrough seizures happen only with fever",
            note=(
                "Between illnesses he is described as seizure-free. Family reports "
                "breakthrough seizures happen only with fever."
            ),
        ),
        _renderer_case(
            pair_id="cluster_generated_interval",
            pair_variant="two_month_cluster",
            panel_role="hard",
            target_family="benchmark_format_convention",
            clinical_state="cluster_frequency_with_unresolved_burden",
            gan_label="1 cluster per 2 month, multiple per cluster",
            rule_id="gan_cluster_multiple_per_cluster",
            scorer_sentinel_used=True,
            evidence="one cluster about every two months with many seizures in each cluster",
            note=(
                "Diary summary: one cluster about every two months with many seizures "
                "in each cluster. Exact within-cluster count is not recorded."
            ),
        ),
        _renderer_case(
            pair_id="cluster_generated_interval",
            pair_variant="burden_first_two_month_cluster",
            panel_role="control",
            target_family="benchmark_format_convention",
            clinical_state="cluster_frequency_with_unresolved_burden",
            gan_label="1 cluster per 2 month, multiple per cluster",
            rule_id="gan_cluster_multiple_per_cluster",
            scorer_sentinel_used=True,
            evidence="many seizures in each cluster about every two months",
            note=(
                "Diary summary: many seizures in each cluster about every two months. "
                "Exact within-cluster count is not recorded."
            ),
        ),
        _renderer_case(
            pair_id="vague_multiple_generated_week",
            pair_variant="multiple_weekly",
            panel_role="hard",
            target_family="benchmark_format_convention",
            clinical_state="vague_multiple_current_events",
            gan_label="multiple per week",
            rule_id="gan_vague_multiple_frequency",
            scorer_sentinel_used=True,
            evidence="multiple seizures each week",
            note=(
                "Interval history: multiple seizures each week, but no reliable "
                "numeric count is available."
            ),
        ),
        _renderer_case(
            pair_id="vague_multiple_generated_week",
            pair_variant="several_weekly",
            panel_role="hard",
            target_family="benchmark_format_convention",
            clinical_state="vague_multiple_current_events",
            gan_label="multiple per week",
            rule_id="gan_vague_multiple_frequency",
            scorer_sentinel_used=True,
            evidence="several seizures in a typical week",
            note=(
                "Interval history: several seizures in a typical week, but no "
                "reliable numeric count is available."
            ),
        ),
        _renderer_case(
            pair_id="unknown_generated_sentinel",
            pair_variant="frequency_not_quantified",
            panel_role="hard",
            target_family="benchmark_format_convention",
            clinical_state="unknown_frequency",
            gan_label="unknown",
            rule_id="gan_unknown_sentinel",
            scorer_sentinel_used=True,
            evidence="seizures are ongoing but not quantified",
            note=(
                "Interval history: seizures are ongoing but not quantified. "
                "The note gives no denominator."
            ),
        ),
        _renderer_case(
            pair_id="unknown_generated_sentinel",
            pair_variant="not_enough_information",
            panel_role="control",
            target_family="benchmark_format_convention",
            clinical_state="unknown_frequency",
            gan_label="unknown",
            rule_id="gan_unknown_sentinel",
            scorer_sentinel_used=True,
            evidence="not enough information to estimate seizure frequency",
            note=(
                "Interval history: not enough information to estimate seizure "
                "frequency. The note gives no denominator."
            ),
        ),
        _renderer_case(
            pair_id="non_epileptic_renderer_projection",
            pair_variant="nonepileptic_current_spells",
            panel_role="hard",
            target_family="benchmark_format_convention",
            clinical_state="non_epileptic_current_events",
            gan_label="seizure free for multiple year",
            rule_id="gan_non_epileptic_seizure_free_projection",
            scorer_sentinel_used=False,
            evidence="current shaking spells are non-epileptic",
            note=(
                "Assessment: current shaking spells are non-epileptic. No epileptic "
                "seizures have occurred for two years."
            ),
        ),
        _renderer_case(
            pair_id="non_epileptic_renderer_projection",
            pair_variant="functional_current_events",
            panel_role="control",
            target_family="benchmark_format_convention",
            clinical_state="non_epileptic_current_events",
            gan_label="seizure free for multiple year",
            rule_id="gan_non_epileptic_seizure_free_projection",
            scorer_sentinel_used=False,
            evidence="functional events continue but are not epileptic seizures",
            note=(
                "Assessment: functional events continue but are not epileptic seizures. "
                "No epileptic seizures have occurred for two years."
            ),
        ),
        _renderer_case(
            pair_id="cluster_generated_week",
            pair_variant="weekly_cluster",
            panel_role="hard",
            target_family="benchmark_format_convention",
            clinical_state="cluster_frequency_with_unresolved_burden",
            gan_label="1 cluster per week, multiple per cluster",
            rule_id="gan_cluster_multiple_per_cluster",
            scorer_sentinel_used=True,
            evidence="one seizure cluster each week with several seizures per cluster",
            note=(
                "Diary summary: one seizure cluster each week with several seizures "
                "per cluster. Exact within-cluster count is not recorded."
            ),
        ),
        _renderer_case(
            pair_id="cluster_generated_week",
            pair_variant="cluster_burden_weekly",
            panel_role="control",
            target_family="benchmark_format_convention",
            clinical_state="cluster_frequency_with_unresolved_burden",
            gan_label="1 cluster per week, multiple per cluster",
            rule_id="gan_cluster_multiple_per_cluster",
            scorer_sentinel_used=True,
            evidence="several seizures per cluster in one weekly cluster",
            note=(
                "Diary summary: several seizures per cluster in one weekly cluster. "
                "Exact within-cluster count is not recorded."
            ),
        ),
    ]


def _boundary_case(
    *,
    pair_id: str,
    pair_variant: str,
    panel_role: str,
    target_family: str,
    boundary_state: str,
    clinical_state: str,
    gan_label: str,
    evidence: str,
    note: str,
) -> dict[str, Any]:
    return {
        "hypothesis_ids": ["H3", "H7"],
        "pair_id": pair_id,
        "pair_variant": pair_variant,
        "panel_role": panel_role,
        "target_family": target_family,
        "target_mechanism": "seizure_free_boundary_event_v0",
        "expected_component": "typed_boundary_classifier",
        "expected_candidate_exposure": "typed_boundary_event_present",
        "expected_boundary_state": boundary_state,
        "expected_clinical_final_state": clinical_state,
        "expected_gan_rendered_label": gan_label,
        "expected_benchmark_policy_id": "gan2026_boundary_projection_policy_v0",
        "expected_benchmark_format_rule_id": "none_boundary_state_only",
        "expected_format_only_change": False,
        "expected_scorer_sentinel_used": gan_label
        in {"unknown", "no seizure frequency reference"},
        "expected_evidence_substring": evidence,
        "source_note_text": note,
    }


def _renderer_case(
    *,
    pair_id: str,
    pair_variant: str,
    panel_role: str,
    target_family: str,
    clinical_state: str,
    gan_label: str,
    rule_id: str,
    scorer_sentinel_used: bool,
    evidence: str,
    note: str,
) -> dict[str, Any]:
    return {
        "hypothesis_ids": ["H3", "H7", "H8"],
        "pair_id": pair_id,
        "pair_variant": pair_variant,
        "panel_role": panel_role,
        "target_family": target_family,
        "target_mechanism": "benchmark_convention_renderer_v0",
        "expected_component": "benchmark_renderer",
        "expected_candidate_exposure": "typed_clinical_state_present",
        "expected_boundary_state": "not_applicable",
        "expected_clinical_final_state": clinical_state,
        "expected_gan_rendered_label": gan_label,
        "expected_benchmark_policy_id": "gan2026_benchmark_renderer_policy_v0",
        "expected_benchmark_format_rule_id": rule_id,
        "expected_format_only_change": True,
        "expected_scorer_sentinel_used": scorer_sentinel_used,
        "expected_evidence_substring": evidence,
        "source_note_text": note,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-jsonl-path", type=Path, default=DEFAULT_OUTPUT_JSONL_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    parser.add_argument("--output-report-path", type=Path, default=DEFAULT_OUTPUT_REPORT_PATH)
    args = parser.parse_args(argv)
    summary = materialize_seed_panel(
        output_jsonl_path=args.output_jsonl_path,
        output_json_path=args.output_json_path,
        output_report_path=args.output_report_path,
    )
    print(
        json.dumps(
            {"decision": summary["decision"], "row_count": summary["row_count"]},
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
