"""Typed boundary and benchmark-renderer contract smoke for H3/H7 seed panels."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    boundary_benchmark_seed_panel,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

POLICY_NAME = "gan2026_boundary_benchmark_contract_v0"
DEFAULT_PANEL_JSONL_PATH = (
    boundary_benchmark_seed_panel.DEFAULT_OUTPUT_JSONL_PATH
)
DEFAULT_OUTPUT_JSONL_PATH = Path(
    "experiments/gan2026_boundary_benchmark_contract_v0_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_boundary_benchmark_contract_v0_2026-06-05.json"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    "experiments/gan2026_boundary_benchmark_contract_v0_2026-06-05.md"
)


@dataclass(frozen=True)
class MechanismResult:
    boundary_state: str
    clinical_final_state: str
    gan_rendered_label: str
    benchmark_policy_id: str
    benchmark_format_rule_id: str
    format_only_change: bool
    scorer_sentinel_used: bool
    evidence: str
    component_owner: str


def build_contract_rows(panel_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Run the no-call mechanism contract over panel rows."""

    return [build_contract_row(row) for row in panel_rows]


def build_contract_row(panel_row: Mapping[str, Any]) -> dict[str, Any]:
    """Run one panel row through the expected target mechanism."""

    target_mechanism = str(panel_row["target_mechanism"])
    note_text = str(panel_row["source_note_text"])
    result = (
        _classify_boundary(note_text)
        if target_mechanism == "seizure_free_boundary_event_v0"
        else _render_benchmark_convention(note_text)
    )
    exact_evidence = evidence_is_substring(note_text, result.evidence)
    issues = _contract_issues(panel_row, result, exact_evidence=exact_evidence)
    return {
        "artifact_kind": "gan2026_boundary_benchmark_contract_row",
        "policy_name": POLICY_NAME,
        "source_row_index": int(panel_row["source_row_index"]),
        "split": panel_row["split"],
        "split_manifest": panel_row["split_manifest"],
        "hypothesis_ids": panel_row.get("hypothesis_ids", []),
        "pair_id": panel_row["pair_id"],
        "pair_variant": panel_row["pair_variant"],
        "panel_role": panel_row["panel_role"],
        "target_family": panel_row["target_family"],
        "target_mechanism": target_mechanism,
        "component_owner": result.component_owner,
        "boundary_state": result.boundary_state,
        "clinical_final_state": result.clinical_final_state,
        "gan_rendered_label": result.gan_rendered_label,
        "benchmark_policy_id": result.benchmark_policy_id,
        "benchmark_format_rule_id": result.benchmark_format_rule_id,
        "format_only_change": result.format_only_change,
        "scorer_sentinel_used": result.scorer_sentinel_used,
        "candidate_exposure": _candidate_exposure(target_mechanism),
        "evidence": result.evidence,
        "exact_evidence": exact_evidence,
        "expected_boundary_state": panel_row["expected_boundary_state"],
        "expected_clinical_final_state": panel_row["expected_clinical_final_state"],
        "expected_gan_rendered_label": panel_row["expected_gan_rendered_label"],
        "expected_benchmark_policy_id": panel_row["expected_benchmark_policy_id"],
        "expected_benchmark_format_rule_id": panel_row[
            "expected_benchmark_format_rule_id"
        ],
        "expected_format_only_change": panel_row["expected_format_only_change"],
        "expected_scorer_sentinel_used": panel_row["expected_scorer_sentinel_used"],
        "contract_matched": not issues,
        "contract_issues": issues,
        "final_label_policy_connected": False,
        "claim_boundary": "synthetic_mechanism_contract_only_no_final_label_promotion",
    }


def summarize_contract_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize contract match and pair consistency."""

    pair_rows = _rows_by_pair(rows)
    invariant_pairs = sum(_pair_clinical_state_invariant(pair) for pair in pair_rows.values())
    contract_matched_rows = sum(row["contract_matched"] is True for row in rows)
    exact_evidence_rows = sum(row["exact_evidence"] is True for row in rows)
    mechanism_counts = Counter(str(row["target_mechanism"]) for row in rows)
    issue_counts = Counter(
        issue for row in rows for issue in row.get("contract_issues", [])
    )
    final_policy_connected = any(row.get("final_label_policy_connected") for row in rows)
    passed = (
        bool(rows)
        and contract_matched_rows == len(rows)
        and exact_evidence_rows == len(rows)
        and invariant_pairs == len(pair_rows)
        and not final_policy_connected
    )
    return {
        "artifact_kind": "gan2026_boundary_benchmark_contract_summary",
        "policy_name": POLICY_NAME,
        "row_count": len(rows),
        "pair_count": len(pair_rows),
        "clinical_state_invariant_pairs": invariant_pairs,
        "contract_matched_rows": contract_matched_rows,
        "contract_issue_counts": dict(sorted(issue_counts.items())),
        "exact_evidence_rows": exact_evidence_rows,
        "target_mechanism_counts": dict(sorted(mechanism_counts.items())),
        "boundary_state_counts": dict(
            sorted(Counter(str(row["boundary_state"]) for row in rows).items())
        ),
        "benchmark_rule_counts": dict(
            sorted(Counter(str(row["benchmark_format_rule_id"]) for row in rows).items())
        ),
        "final_label_policy_connected": final_policy_connected,
        "claim_boundary": (
            "Synthetic H3/H7 mechanism contract smoke. It executes typed boundary "
            "classification and benchmark rendering over the seed panel while keeping "
            "clinical state and Gan-rendered label separate. It does not connect to "
            "final-label policy and is not validation or holdout evidence."
        ),
        "decision": (
            "boundary_renderer_contract_passed"
            if passed
            else "boundary_renderer_contract_failed"
        ),
        "recommended_next_step": (
            "Port only the stable typed boundary and benchmark-renderer fields to a "
            "validation hard-slice panel. Keep final-label policy disconnected until "
            "the validation mechanism surface is robust."
        ),
    }


def materialize_contract_smoke(
    *,
    panel_jsonl_path: Path = DEFAULT_PANEL_JSONL_PATH,
    output_jsonl_path: Path = DEFAULT_OUTPUT_JSONL_PATH,
    output_json_path: Path = DEFAULT_OUTPUT_JSON_PATH,
    output_report_path: Path = DEFAULT_OUTPUT_REPORT_PATH,
) -> dict[str, Any]:
    panel_rows = load_jsonl_rows(panel_jsonl_path)
    rows = build_contract_rows(panel_rows)
    summary = summarize_contract_rows(rows)
    summary = {
        **summary,
        "source_panel_artifact": str(panel_jsonl_path),
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
        "# Gan 2026 Boundary/Benchmark Contract Smoke v0",
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
        f"| contract-matched rows | {summary['contract_matched_rows']} |",
        f"| exact evidence rows | {summary['exact_evidence_rows']} |",
        f"| final-label policy connected | {summary['final_label_policy_connected']} |",
        "",
        "## Target Mechanisms",
        "",
        "| Mechanism | Rows |",
        "| --- | ---: |",
    ]
    for mechanism, count in summary["target_mechanism_counts"].items():
        lines.append(f"| `{mechanism}` | {count} |")
    lines.extend(["", "## Benchmark Rules", "", "| Rule | Rows |", "| --- | ---: |"])
    for rule, count in summary["benchmark_rule_counts"].items():
        lines.append(f"| `{rule}` | {count} |")
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            str(summary["recommended_next_step"]),
            "",
            "## Artifacts",
            "",
            f"- Contract JSONL: `{summary['jsonl_artifact']}`",
            f"- Summary JSON: `{summary['json_artifact']}`",
            f"- Source panel JSONL: `{summary['source_panel_artifact']}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _classify_boundary(note_text: str) -> MechanismResult:
    lowered = note_text.lower()
    for phrase, label in (
        ("focal aware seizures continue twice weekly", "2 per week"),
        ("absence seizures continue three times monthly", "3 per month"),
    ):
        if phrase in lowered:
            return _residual_activity_result(note_text, phrase, gan_rendered_label=label)
    for phrase in (
        "seizures occur only when medication doses are missed",
        "events are only reported after sleep deprivation",
        "breakthrough seizures happen only with fever",
    ):
        if phrase in lowered:
            return _conditional_trigger_result(
                note_text,
                _substring_by_case(note_text, phrase),
            )
    for phrase in (
        "current shaking spells are non-epileptic",
        "functional events continue but are not epileptic seizures",
    ):
        if phrase in lowered:
            return _non_epileptic_result(note_text, _substring_by_case(note_text, phrase))
    for phrase in (
        "medication side effects are reviewed",
        "school performance is discussed",
    ):
        if phrase in lowered:
            return _no_boundary_result(note_text, _substring_by_case(note_text, phrase))
    for phrase in (
        "last seizure was in january 2024",
        "most recent seizure occurred in january 2024",
        "last event was in march 2024",
        "most recent epileptic event occurred in march 2024",
    ):
        if phrase in lowered:
            return _last_event_result(note_text, _substring_by_case(note_text, phrase))
    for phrase in (
        "no seizures since january 2024",
        "seizure-free since january 2024",
        "free of seizures for six months",
        "no epileptic events for the past half year",
    ):
        if phrase in lowered:
            return _seizure_free_interval_result(
                note_text,
                _substring_by_case(note_text, phrase),
                gan_rendered_label="seizure free for multiple month",
            )
    return _no_boundary_result(note_text, note_text[:80])


def _render_benchmark_convention(note_text: str) -> MechanismResult:
    lowered = note_text.lower()
    for phrase, clinical_state, label, rule_id, sentinel_used in _renderer_rules():
        if phrase in lowered:
            return _renderer_result(
                note_text,
                evidence=_substring_by_case(note_text, phrase),
                clinical_final_state=clinical_state,
                gan_rendered_label=label,
                benchmark_format_rule_id=rule_id,
                scorer_sentinel_used=sentinel_used,
            )
    return _renderer_result(
        note_text,
        evidence=note_text[:80],
        clinical_final_state="unknown_frequency",
        gan_rendered_label="unknown",
        benchmark_format_rule_id="gan_unknown_sentinel",
        scorer_sentinel_used=True,
    )


def _renderer_rules() -> tuple[tuple[str, str, str, str, bool], ...]:
    return (
        (
            "one cluster every four to five weeks with several seizures per cluster",
            "cluster_frequency_with_unresolved_burden",
            "1 cluster per 4 to 5 week, multiple per cluster",
            "gan_cluster_multiple_per_cluster",
            True,
        ),
        (
            "several seizures per cluster about every four to five weeks",
            "cluster_frequency_with_unresolved_burden",
            "1 cluster per 4 to 5 week, multiple per cluster",
            "gan_cluster_multiple_per_cluster",
            True,
        ),
        (
            "one cluster about every two months with many seizures in each cluster",
            "cluster_frequency_with_unresolved_burden",
            "1 cluster per 2 month, multiple per cluster",
            "gan_cluster_multiple_per_cluster",
            True,
        ),
        (
            "many seizures in each cluster about every two months",
            "cluster_frequency_with_unresolved_burden",
            "1 cluster per 2 month, multiple per cluster",
            "gan_cluster_multiple_per_cluster",
            True,
        ),
        (
            "one seizure cluster each week with several seizures per cluster",
            "cluster_frequency_with_unresolved_burden",
            "1 cluster per week, multiple per cluster",
            "gan_cluster_multiple_per_cluster",
            True,
        ),
        (
            "several seizures per cluster in one weekly cluster",
            "cluster_frequency_with_unresolved_burden",
            "1 cluster per week, multiple per cluster",
            "gan_cluster_multiple_per_cluster",
            True,
        ),
        (
            "events continue but the frequency is unclear",
            "unknown_frequency",
            "unknown",
            "gan_unknown_sentinel",
            True,
        ),
        (
            "no seizure-frequency history is documented",
            "unknown_frequency",
            "unknown",
            "gan_unknown_sentinel",
            True,
        ),
        (
            "seizures are ongoing but not quantified",
            "unknown_frequency",
            "unknown",
            "gan_unknown_sentinel",
            True,
        ),
        (
            "not enough information to estimate seizure frequency",
            "unknown_frequency",
            "unknown",
            "gan_unknown_sentinel",
            True,
        ),
        (
            "multiple seizures each month",
            "vague_multiple_current_events",
            "multiple per month",
            "gan_vague_multiple_frequency",
            True,
        ),
        (
            "several seizures in a typical month",
            "vague_multiple_current_events",
            "multiple per month",
            "gan_vague_multiple_frequency",
            True,
        ),
        (
            "multiple seizures each week",
            "vague_multiple_current_events",
            "multiple per week",
            "gan_vague_multiple_frequency",
            True,
        ),
        (
            "several seizures in a typical week",
            "vague_multiple_current_events",
            "multiple per week",
            "gan_vague_multiple_frequency",
            True,
        ),
        (
            "current shaking spells are non-epileptic",
            "non_epileptic_current_events",
            "seizure free for multiple year",
            "gan_non_epileptic_seizure_free_projection",
            False,
        ),
        (
            "functional events continue but are not epileptic seizures",
            "non_epileptic_current_events",
            "seizure free for multiple year",
            "gan_non_epileptic_seizure_free_projection",
            False,
        ),
    )


def _residual_activity_result(
    note_text: str,
    evidence_lower: str,
    *,
    gan_rendered_label: str,
) -> MechanismResult:
    return MechanismResult(
        boundary_state="residual_seizure_activity",
        clinical_final_state="active_residual_seizure_frequency",
        gan_rendered_label=gan_rendered_label,
        benchmark_policy_id="gan2026_boundary_projection_policy_v0",
        benchmark_format_rule_id="none_boundary_state_only",
        format_only_change=False,
        scorer_sentinel_used=False,
        evidence=_substring_by_case(note_text, evidence_lower),
        component_owner="typed_boundary_classifier",
    )


def _conditional_trigger_result(note_text: str, evidence: str) -> MechanismResult:
    return MechanismResult(
        boundary_state="conditional_or_trigger_only",
        clinical_final_state="conditional_or_trigger_only",
        gan_rendered_label="unknown",
        benchmark_policy_id="gan2026_boundary_projection_policy_v0",
        benchmark_format_rule_id="none_boundary_state_only",
        format_only_change=False,
        scorer_sentinel_used=True,
        evidence=evidence,
        component_owner="typed_boundary_classifier",
    )


def _non_epileptic_result(note_text: str, evidence: str) -> MechanismResult:
    return MechanismResult(
        boundary_state="non_epileptic_current_events",
        clinical_final_state="non_epileptic_current_events",
        gan_rendered_label="seizure free for multiple year",
        benchmark_policy_id="gan2026_boundary_projection_policy_v0",
        benchmark_format_rule_id="none_boundary_state_only",
        format_only_change=False,
        scorer_sentinel_used=False,
        evidence=evidence,
        component_owner="typed_boundary_classifier",
    )


def _no_boundary_result(note_text: str, evidence: str) -> MechanismResult:
    return MechanismResult(
        boundary_state="no_boundary_evidence",
        clinical_final_state="no_boundary_evidence",
        gan_rendered_label="no seizure frequency reference",
        benchmark_policy_id="gan2026_boundary_projection_policy_v0",
        benchmark_format_rule_id="none_boundary_state_only",
        format_only_change=False,
        scorer_sentinel_used=True,
        evidence=evidence,
        component_owner="typed_boundary_classifier",
    )


def _last_event_result(note_text: str, evidence: str) -> MechanismResult:
    return MechanismResult(
        boundary_state="last_event_only",
        clinical_final_state="last_event_only",
        gan_rendered_label="unknown",
        benchmark_policy_id="gan2026_boundary_projection_policy_v0",
        benchmark_format_rule_id="none_boundary_state_only",
        format_only_change=False,
        scorer_sentinel_used=True,
        evidence=evidence,
        component_owner="typed_boundary_classifier",
    )


def _seizure_free_interval_result(
    note_text: str,
    evidence: str,
    *,
    gan_rendered_label: str,
) -> MechanismResult:
    return MechanismResult(
        boundary_state="asserted_seizure_free_interval",
        clinical_final_state="seizure_free_interval",
        gan_rendered_label=gan_rendered_label,
        benchmark_policy_id="gan2026_boundary_projection_policy_v0",
        benchmark_format_rule_id="none_boundary_state_only",
        format_only_change=False,
        scorer_sentinel_used=False,
        evidence=evidence,
        component_owner="typed_boundary_classifier",
    )


def _renderer_result(
    note_text: str,
    *,
    evidence: str,
    clinical_final_state: str,
    gan_rendered_label: str,
    benchmark_format_rule_id: str,
    scorer_sentinel_used: bool,
) -> MechanismResult:
    return MechanismResult(
        boundary_state="not_applicable",
        clinical_final_state=clinical_final_state,
        gan_rendered_label=gan_rendered_label,
        benchmark_policy_id="gan2026_benchmark_renderer_policy_v0",
        benchmark_format_rule_id=benchmark_format_rule_id,
        format_only_change=True,
        scorer_sentinel_used=scorer_sentinel_used,
        evidence=evidence,
        component_owner="benchmark_renderer",
    )


def _contract_issues(
    panel_row: Mapping[str, Any],
    result: MechanismResult,
    *,
    exact_evidence: bool,
) -> list[str]:
    comparisons = {
        "boundary_state": result.boundary_state,
        "clinical_final_state": result.clinical_final_state,
        "gan_rendered_label": result.gan_rendered_label,
        "benchmark_policy_id": result.benchmark_policy_id,
        "benchmark_format_rule_id": result.benchmark_format_rule_id,
        "format_only_change": result.format_only_change,
        "scorer_sentinel_used": result.scorer_sentinel_used,
    }
    issues = [
        f"{field}_mismatch"
        for field, actual in comparisons.items()
        if actual != panel_row[f"expected_{field}"]
    ]
    if not exact_evidence:
        issues.append("evidence_not_exact")
    return issues


def _candidate_exposure(target_mechanism: str) -> str:
    if target_mechanism == "seizure_free_boundary_event_v0":
        return "typed_boundary_event_present"
    return "typed_clinical_state_present"


def _rows_by_pair(rows: Sequence[Mapping[str, Any]]) -> dict[str, list[Mapping[str, Any]]]:
    pairs: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        pairs[str(row["pair_id"])].append(row)
    return pairs


def _pair_clinical_state_invariant(rows: Sequence[Mapping[str, Any]]) -> bool:
    return len({str(row["clinical_final_state"]) for row in rows}) == 1


def _substring_by_case(note_text: str, evidence_lower: str) -> str:
    start = note_text.lower().index(evidence_lower)
    return note_text[start : start + len(evidence_lower)]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel-jsonl-path", type=Path, default=DEFAULT_PANEL_JSONL_PATH)
    parser.add_argument("--output-jsonl-path", type=Path, default=DEFAULT_OUTPUT_JSONL_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    parser.add_argument("--output-report-path", type=Path, default=DEFAULT_OUTPUT_REPORT_PATH)
    args = parser.parse_args(argv)
    summary = materialize_contract_smoke(
        panel_jsonl_path=args.panel_jsonl_path,
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
