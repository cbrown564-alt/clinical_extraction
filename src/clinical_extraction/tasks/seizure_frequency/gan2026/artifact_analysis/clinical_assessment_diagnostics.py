"""Diagnostics for CandidateSet ClinicalAssessment probe artifacts."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.clinical_assessment import (
    ClinicalAssessment,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

DEFAULT_ASSESSMENT_JSONL_PATH = Path(
    "experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation25_gpt41mini_v0.jsonl"
)
DEFAULT_MINIMAL_SELECTOR_JSONL_PATH = Path(
    "experiments/gan2026_validation250_selected_candidate_decision_v2_v2_high_recall.jsonl"
)
DEFAULT_RICH_SELECTOR_JSONL_PATH = Path(
    "experiments/gan2026_validation250_selected_fact_v0_v2_high_recall.jsonl"
)
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation25_v0_diagnostics.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation25_v0_diagnostics.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation25_v0_diagnostics.md"
)
MAX_EXAMPLES_PER_SECTION = 12


def build_clinical_assessment_diagnostics(
    assessment_rows: Sequence[Mapping[str, Any]],
    *,
    minimal_selector_rows: Sequence[Mapping[str, Any]] = (),
    rich_selector_rows: Sequence[Mapping[str, Any]] = (),
    source_artifact: str = str(DEFAULT_ASSESSMENT_JSONL_PATH),
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    minimal_by_index = _rows_by_source_index(minimal_selector_rows)
    rich_by_index = _rows_by_source_index(rich_selector_rows)
    diagnostics = [
        _diagnostic_row(
            row,
            minimal_selector_row=minimal_by_index.get(int(row["source_row_index"])),
            rich_selector_row=rich_by_index.get(int(row["source_row_index"])),
        )
        for row in assessment_rows
    ]
    return diagnostics, summarize_diagnostics(diagnostics, source_artifact=source_artifact)


def summarize_diagnostics(
    diagnostics: Sequence[Mapping[str, Any]],
    *,
    source_artifact: str = str(DEFAULT_ASSESSMENT_JSONL_PATH),
) -> dict[str, Any]:
    assessment_kind_counts = Counter(
        str(row["assessment_kind"]) for row in diagnostics if row["assessment_status"] == "present"
    )
    aggregation_policy_counts = Counter(
        str(row["aggregation_policy"])
        for row in diagnostics
        if row["assessment_status"] == "present"
    )
    primary_count_counts = Counter(
        str(row["primary_candidate_count"])
        for row in diagnostics
        if row["assessment_status"] == "present"
    )
    flag_counts = Counter(flag for row in diagnostics for flag in row["diagnostic_flags"])
    comparison_counts = Counter(
        str(row["minimal_selector_primary_relation"])
        for row in diagnostics
        if row["minimal_selector_primary_relation"] != "not_available"
    )
    rich_comparison_counts = Counter(
        str(row["rich_selector_primary_relation"])
        for row in diagnostics
        if row["rich_selector_primary_relation"] != "not_available"
    )
    rows_with_flags = [row for row in diagnostics if row["diagnostic_flags"]]
    return {
        "artifact_name": (
            "gan2026_candidate_set_clinical_assessment_probe_live_validation25_v0_diagnostics"
        ),
        "source_artifact": source_artifact,
        "row_count": len(diagnostics),
        "claim_boundary": (
            f"{len(diagnostics)}-row clinical-assessment diagnostics only. This "
            "inspects role usage, context separation, and comparisons to selector "
            "artifacts; it does not score, project, or render answers."
        ),
        "summary": {
            "clinical_assessment_rows": sum(
                row["assessment_status"] == "present" for row in diagnostics
            ),
            "missing_assessment_rows": sum(
                row["assessment_status"] == "missing" for row in diagnostics
            ),
            "invalid_reference_rows": sum(
                bool(row["unknown_candidate_ids"]) for row in diagnostics
            ),
            "role_overlap_rows": sum(
                bool(row["role_overlap_candidate_ids"]) for row in diagnostics
            ),
            "rows_with_diagnostic_flags": len(rows_with_flags),
            "assessment_kind_counts": dict(sorted(assessment_kind_counts.items())),
            "aggregation_policy_counts": dict(sorted(aggregation_policy_counts.items())),
            "primary_candidate_count_distribution": dict(sorted(primary_count_counts.items())),
            "diagnostic_flag_counts": dict(sorted(flag_counts.items())),
            "minimal_selector_primary_relation_counts": dict(sorted(comparison_counts.items())),
            "rich_selector_primary_relation_counts": dict(sorted(rich_comparison_counts.items())),
            "flagged_source_row_indices": [int(row["source_row_index"]) for row in rows_with_flags],
        },
        "inspection_examples": {
            "flagged_rows": _examples(rows_with_flags),
            "multi_primary_rows": _examples(
                [row for row in diagnostics if row["primary_candidate_count"] > 1]
            ),
            "context_leak_rows": _examples(
                [
                    row
                    for row in diagnostics
                    if any("context_leak" in flag for flag in row["diagnostic_flags"])
                ]
            ),
            "minimal_selector_differences": _examples(
                [
                    row
                    for row in diagnostics
                    if row["minimal_selector_primary_relation"] not in {"same", "not_available"}
                ]
            ),
            "rich_selector_differences": _examples(
                [
                    row
                    for row in diagnostics
                    if row["rich_selector_primary_relation"] not in {"same", "not_available"}
                ]
            ),
        },
    }


def write_summary_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_report(
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path = DEFAULT_JSONL_PATH,
    json_path: Path = DEFAULT_JSON_PATH,
) -> None:
    summary = metadata["summary"]
    lines = [
        "# Gan 2026 Clinical Assessment Diagnostics",
        "",
        str(metadata["claim_boundary"]),
        "",
        "## Artifacts",
        "",
        f"- Diagnostic JSONL: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        f"- Assessment source: `{metadata['source_artifact']}`",
        "",
        "## Summary",
        "",
        f"- Rows: {metadata['row_count']}",
        f"- Clinical assessment rows: {summary['clinical_assessment_rows']}",
        f"- Missing assessment rows: {summary['missing_assessment_rows']}",
        f"- Invalid reference rows: {summary['invalid_reference_rows']}",
        f"- Role overlap rows: {summary['role_overlap_rows']}",
        f"- Rows with diagnostic flags: {summary['rows_with_diagnostic_flags']}",
        "",
        "## Assessment Kinds",
        "",
    ]
    for kind, count in summary["assessment_kind_counts"].items():
        lines.append(f"- `{kind}`: {count}")
    lines.extend(["", "## Aggregation Policies", ""])
    for policy, count in summary["aggregation_policy_counts"].items():
        lines.append(f"- `{policy}`: {count}")
    lines.extend(["", "## Primary Candidate Counts", ""])
    for count_value, count in summary["primary_candidate_count_distribution"].items():
        lines.append(f"- `{count_value}`: {count}")
    lines.extend(["", "## Diagnostic Flags", ""])
    if not summary["diagnostic_flag_counts"]:
        lines.append("- None.")
    for flag, count in summary["diagnostic_flag_counts"].items():
        lines.append(f"- `{flag}`: {count}")
    lines.extend(["", "## Selector Comparisons", ""])
    lines.append("### Minimal Selector V2")
    for relation, count in summary["minimal_selector_primary_relation_counts"].items():
        lines.append(f"- `{relation}`: {count}")
    lines.extend(["", "### Rich Selector V0", ""])
    for relation, count in summary["rich_selector_primary_relation_counts"].items():
        lines.append(f"- `{relation}`: {count}")
    lines.extend(["", "## Inspection Examples", ""])
    for title, examples in metadata["inspection_examples"].items():
        lines.extend([f"### {title.replace('_', ' ').title()}", ""])
        if not examples:
            lines.append("- None.")
        for row in examples:
            lines.append(
                "- "
                f"{row['source_row_index']}: kind `{row['assessment_kind']}`, "
                f"policy `{row['aggregation_policy']}`, primary "
                f"{row['primary_candidate_ids']}, supporting "
                f"{row['supporting_candidate_ids']}, rejected "
                f"{row['rejected_candidate_ids']}, flags "
                f"{row['diagnostic_flags']}, minimal selector "
                f"`{row['minimal_selector_primary_relation']}`, rich selector "
                f"`{row['rich_selector_primary_relation']}`. "
                f"Summary: {row['assessment_summary']}"
            )
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _diagnostic_row(
    row: Mapping[str, Any],
    *,
    minimal_selector_row: Mapping[str, Any] | None,
    rich_selector_row: Mapping[str, Any] | None,
) -> dict[str, Any]:
    candidates = _candidate_payloads_from_row(row)
    candidate_by_id = {str(candidate.get("candidate_id")): candidate for candidate in candidates}
    assessment = _assessment_from_row(row)
    if assessment is None:
        return _missing_diagnostic_row(row, candidates)

    primary_ids = list(assessment.primary_candidate_ids)
    supporting_ids = list(assessment.supporting_candidate_ids)
    rejected_ids = list(assessment.rejected_candidate_ids)
    unknown_ids = [
        candidate_id
        for candidate_id in [*primary_ids, *supporting_ids, *rejected_ids]
        if candidate_id not in candidate_by_id
    ]
    role_overlap_ids = _role_overlap_ids(primary_ids, supporting_ids, rejected_ids)
    primary_candidates = [candidate_by_id[cid] for cid in primary_ids if cid in candidate_by_id]
    supporting_candidates = [
        candidate_by_id[cid] for cid in supporting_ids if cid in candidate_by_id
    ]
    rejected_candidates = [candidate_by_id[cid] for cid in rejected_ids if cid in candidate_by_id]
    normalized_burden = assessment.normalized_burden.model_dump()
    diagnostic_flags = _diagnostic_flags(
        assessment=assessment,
        primary_candidates=primary_candidates,
        supporting_candidates=supporting_candidates,
        rejected_candidates=rejected_candidates,
        normalized_burden=normalized_burden,
    )
    minimal_selected_ids = _minimal_selector_selected_ids(minimal_selector_row)
    rich_selected_ids = _rich_selector_selected_ids(rich_selector_row)
    return {
        "source_row_index": int(row["source_row_index"]),
        "split": row.get("split", "validation"),
        "assessment_status": "present",
        "candidate_count": len(candidates),
        "assessment_kind": assessment.assessment_kind,
        "aggregation_policy": assessment.aggregation_policy,
        "primary_candidate_ids": primary_ids,
        "supporting_candidate_ids": supporting_ids,
        "rejected_candidate_ids": rejected_ids,
        "unknown_candidate_ids": unknown_ids,
        "role_overlap_candidate_ids": role_overlap_ids,
        "primary_candidate_count": len(primary_ids),
        "supporting_candidate_count": len(supporting_ids),
        "rejected_candidate_count": len(rejected_ids),
        "primary_candidate_kinds": _candidate_values(primary_candidates, "candidate_kind"),
        "supporting_candidate_kinds": _candidate_values(supporting_candidates, "candidate_kind"),
        "rejected_candidate_kinds": _candidate_values(rejected_candidates, "candidate_kind"),
        "primary_temporalities": _candidate_values(primary_candidates, "temporality"),
        "supporting_temporalities": _candidate_values(supporting_candidates, "temporality"),
        "rejected_temporalities": _candidate_values(rejected_candidates, "temporality"),
        "primary_evidence_texts": [_candidate_evidence_text(c) for c in primary_candidates],
        "supporting_evidence_texts": [_candidate_evidence_text(c) for c in supporting_candidates],
        "rejected_evidence_texts": [_candidate_evidence_text(c) for c in rejected_candidates],
        "normalized_burden": normalized_burden,
        "assessment_summary": assessment.assessment_summary,
        "uncertainty_flags": list(assessment.uncertainty_flags),
        "diagnostic_flags": diagnostic_flags,
        "minimal_selector_selected_candidate_ids": minimal_selected_ids,
        "minimal_selector_selection_mode": _minimal_selector_mode(minimal_selector_row),
        "minimal_selector_primary_relation": _set_relation(primary_ids, minimal_selected_ids),
        "rich_selector_selected_candidate_ids": rich_selected_ids,
        "rich_selector_clinical_fact_kind": _rich_selector_kind(rich_selector_row),
        "rich_selector_primary_relation": _set_relation(primary_ids, rich_selected_ids),
        "parse_errors": list(row.get("parse_errors") or []),
        "call_error": row.get("call_error"),
    }


def _missing_diagnostic_row(
    row: Mapping[str, Any],
    candidates: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    return {
        "source_row_index": int(row["source_row_index"]),
        "split": row.get("split", "validation"),
        "assessment_status": "missing",
        "candidate_count": len(candidates),
        "assessment_kind": "missing",
        "aggregation_policy": "missing",
        "primary_candidate_ids": [],
        "supporting_candidate_ids": [],
        "rejected_candidate_ids": [],
        "unknown_candidate_ids": [],
        "role_overlap_candidate_ids": [],
        "primary_candidate_count": 0,
        "supporting_candidate_count": 0,
        "rejected_candidate_count": 0,
        "primary_candidate_kinds": [],
        "supporting_candidate_kinds": [],
        "rejected_candidate_kinds": [],
        "primary_temporalities": [],
        "supporting_temporalities": [],
        "rejected_temporalities": [],
        "primary_evidence_texts": [],
        "supporting_evidence_texts": [],
        "rejected_evidence_texts": [],
        "normalized_burden": {},
        "assessment_summary": "",
        "uncertainty_flags": [],
        "diagnostic_flags": ["assessment_missing"],
        "minimal_selector_selected_candidate_ids": [],
        "minimal_selector_selection_mode": "not_available",
        "minimal_selector_primary_relation": "not_available",
        "rich_selector_selected_candidate_ids": [],
        "rich_selector_clinical_fact_kind": "not_available",
        "rich_selector_primary_relation": "not_available",
        "parse_errors": list(row.get("parse_errors") or []),
        "call_error": row.get("call_error"),
    }


def _diagnostic_flags(
    *,
    assessment: ClinicalAssessment,
    primary_candidates: Sequence[Mapping[str, Any]],
    supporting_candidates: Sequence[Mapping[str, Any]],
    rejected_candidates: Sequence[Mapping[str, Any]],
    normalized_burden: Mapping[str, Any],
) -> list[str]:
    flags: list[str] = []
    primary_kinds = {str(candidate.get("candidate_kind")) for candidate in primary_candidates}
    if len(assessment.primary_candidate_ids) > 1 and assessment.aggregation_policy in {
        "single_fact",
        "primary_with_context",
    }:
        flags.append("multi_primary_nonadditive_policy")
    if assessment.aggregation_policy == "single_fact" and len(assessment.primary_candidate_ids) > 1:
        flags.append("single_fact_multiple_primary_candidates")
    if _has_actionable_historical_primary(
        assessment=assessment,
        primary_candidates=primary_candidates,
        supporting_candidates=supporting_candidates,
        rejected_candidates=rejected_candidates,
    ):
        flags.append("historical_primary_candidate")
    if assessment.assessment_kind == "frequency_rate" and _has_cluster_burden(normalized_burden):
        flags.append("cluster_context_leak_in_frequency_burden")
    if assessment.assessment_kind == "frequency_rate" and _has_seizure_free_burden(
        normalized_burden
    ):
        flags.append("seizure_free_context_leak_in_frequency_burden")
    if assessment.assessment_kind == "cluster_frequency" and _has_seizure_free_burden(
        normalized_burden
    ):
        flags.append("seizure_free_context_leak_in_cluster_burden")
    source_phrase = str(normalized_burden.get("source_normalized_phrase") or "").lower()
    if any(token in source_phrase for token in ("previous", "histor", "prior", "formerly")):
        flags.append("historical_context_phrase_in_burden")
    if assessment.aggregation_policy == "primary_with_context" and not supporting_candidates:
        flags.append("primary_with_context_without_supporting_candidates")
    if (
        assessment.aggregation_policy == "additive_same_window"
        and len(assessment.primary_candidate_ids) < 2
    ):
        flags.append("aggregation_policy_without_multiple_primary_candidates")
    if (
        assessment.aggregation_policy == "cluster_axis"
        and len(assessment.primary_candidate_ids) < 2
        and not _cluster_axis_single_primary_allowed(normalized_burden)
    ):
        flags.append("aggregation_policy_without_multiple_primary_candidates")
    if assessment.aggregation_policy == "additive_same_window" and primary_kinds != {
        "frequency_rate"
    }:
        flags.append("additive_policy_non_frequency_primary")
    if assessment.aggregation_policy == "cluster_axis" and "cluster_frequency" not in primary_kinds:
        flags.append("cluster_axis_without_cluster_primary")
    if rejected_candidates and not assessment.rejected_candidate_ids:
        flags.append("unreachable")
    return flags


def _candidate_payloads_from_row(row: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    typed_input = row.get("typed_input")
    if not isinstance(typed_input, Mapping):
        return []
    candidate_set_payload = typed_input.get("candidate_set")
    if not isinstance(candidate_set_payload, Mapping):
        return []
    candidates = candidate_set_payload.get("candidates")
    if not isinstance(candidates, list):
        return []
    return [candidate for candidate in candidates if isinstance(candidate, Mapping)]


def _candidate_evidence_text(candidate: Mapping[str, Any]) -> str:
    evidence = candidate.get("evidence_text")
    if isinstance(evidence, str):
        return evidence
    evidence_span = candidate.get("evidence_span")
    if isinstance(evidence_span, Mapping) and isinstance(evidence_span.get("text"), str):
        return str(evidence_span["text"])
    return ""


def _assessment_from_row(row: Mapping[str, Any]) -> ClinicalAssessment | None:
    assessment_payload = row.get("clinical_assessment")
    if not isinstance(assessment_payload, Mapping):
        return None
    return ClinicalAssessment.model_validate(assessment_payload)


def _candidate_values(
    candidates: Sequence[Mapping[str, Any]],
    key: str,
) -> list[str]:
    return [str(candidate.get(key)) for candidate in candidates]


def _has_cluster_burden(normalized_burden: Mapping[str, Any]) -> bool:
    return any(
        normalized_burden.get(key) is not None
        for key in (
            "cluster_count_low",
            "cluster_count_high",
            "cluster_period_low",
            "cluster_period_high",
            "cluster_period_unit",
            "events_per_cluster_low",
            "events_per_cluster_high",
        )
    )


def _cluster_axis_single_primary_allowed(normalized_burden: Mapping[str, Any]) -> bool:
    has_cluster_cadence = any(
        normalized_burden.get(key) is not None
        for key in (
            "count_low",
            "count_high",
            "period_low",
            "period_high",
            "period_unit",
            "cluster_count_low",
            "cluster_count_high",
        )
    )
    has_cluster_size_or_duration = any(
        normalized_burden.get(key) is not None
        for key in (
            "cluster_period_low",
            "cluster_period_high",
            "cluster_period_unit",
            "events_per_cluster_low",
            "events_per_cluster_high",
        )
    )
    return has_cluster_cadence and has_cluster_size_or_duration


def _has_seizure_free_burden(normalized_burden: Mapping[str, Any]) -> bool:
    return any(
        normalized_burden.get(key) is not None
        for key in (
            "seizure_free_duration_low",
            "seizure_free_duration_high",
            "seizure_free_duration_unit",
        )
    )


def _has_actionable_historical_primary(
    *,
    assessment: ClinicalAssessment,
    primary_candidates: Sequence[Mapping[str, Any]],
    supporting_candidates: Sequence[Mapping[str, Any]],
    rejected_candidates: Sequence[Mapping[str, Any]],
) -> bool:
    if "historical" not in _candidate_values(primary_candidates, "temporality"):
        return False
    competing_candidates = [*supporting_candidates, *rejected_candidates]
    has_current_or_recent_alternative = any(
        str(candidate.get("temporality")) in {"current", "recent"}
        for candidate in competing_candidates
    )
    if has_current_or_recent_alternative:
        return True
    if assessment.assessment_kind == "seizure_free":
        return False
    return True


def _role_overlap_ids(
    primary_ids: Sequence[str],
    supporting_ids: Sequence[str],
    rejected_ids: Sequence[str],
) -> list[str]:
    counts = Counter([*primary_ids, *supporting_ids, *rejected_ids])
    return sorted(candidate_id for candidate_id, count in counts.items() if count > 1)


def _rows_by_source_index(
    rows: Sequence[Mapping[str, Any]],
) -> dict[int, Mapping[str, Any]]:
    return {int(row["source_row_index"]): row for row in rows}


def _minimal_selector_selected_ids(row: Mapping[str, Any] | None) -> list[str]:
    if not isinstance(row, Mapping):
        return []
    decision = row.get("selected_candidate_decision")
    if not isinstance(decision, Mapping):
        return []
    return [str(candidate_id) for candidate_id in decision.get("selected_candidate_ids") or []]


def _minimal_selector_mode(row: Mapping[str, Any] | None) -> str:
    if not isinstance(row, Mapping):
        return "not_available"
    decision = row.get("selected_candidate_decision")
    if not isinstance(decision, Mapping):
        return "not_available"
    return str(decision.get("selection_mode"))


def _rich_selector_selected_ids(row: Mapping[str, Any] | None) -> list[str]:
    if not isinstance(row, Mapping):
        return []
    selection = row.get("selected_clinical_fact")
    if not isinstance(selection, Mapping):
        return []
    return [str(candidate_id) for candidate_id in selection.get("selected_candidate_ids") or []]


def _rich_selector_kind(row: Mapping[str, Any] | None) -> str:
    if not isinstance(row, Mapping):
        return "not_available"
    selection = row.get("selected_clinical_fact")
    if not isinstance(selection, Mapping):
        return "not_available"
    return str(selection.get("clinical_fact_kind"))


def _set_relation(left_ids: Sequence[str], right_ids: Sequence[str]) -> str:
    if not right_ids:
        return "not_available"
    left = set(left_ids)
    right = set(right_ids)
    if left == right:
        return "same"
    if left < right:
        return "assessment_primary_subset"
    if left > right:
        return "assessment_primary_superset"
    if left & right:
        return "overlap"
    return "different"


def _examples(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "source_row_index": int(row["source_row_index"]),
            "assessment_kind": row["assessment_kind"],
            "aggregation_policy": row["aggregation_policy"],
            "primary_candidate_ids": list(row["primary_candidate_ids"]),
            "supporting_candidate_ids": list(row["supporting_candidate_ids"]),
            "rejected_candidate_ids": list(row["rejected_candidate_ids"]),
            "diagnostic_flags": list(row["diagnostic_flags"]),
            "minimal_selector_primary_relation": row["minimal_selector_primary_relation"],
            "rich_selector_primary_relation": row["rich_selector_primary_relation"],
            "assessment_summary": row["assessment_summary"],
        }
        for row in rows[:MAX_EXAMPLES_PER_SECTION]
    ]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assessment-jsonl", type=Path, default=DEFAULT_ASSESSMENT_JSONL_PATH)
    parser.add_argument(
        "--minimal-selector-jsonl",
        type=Path,
        default=DEFAULT_MINIMAL_SELECTOR_JSONL_PATH,
    )
    parser.add_argument(
        "--rich-selector-jsonl",
        type=Path,
        default=DEFAULT_RICH_SELECTOR_JSONL_PATH,
    )
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    minimal_rows = (
        load_jsonl_rows(args.minimal_selector_jsonl) if args.minimal_selector_jsonl.exists() else []
    )
    rich_rows = (
        load_jsonl_rows(args.rich_selector_jsonl) if args.rich_selector_jsonl.exists() else []
    )
    rows, metadata = build_clinical_assessment_diagnostics(
        load_jsonl_rows(args.assessment_jsonl),
        minimal_selector_rows=minimal_rows,
        rich_selector_rows=rich_rows,
        source_artifact=str(args.assessment_jsonl),
    )
    write_jsonl_rows(rows, args.jsonl_path)
    write_summary_json(metadata, args.json_path)
    write_report(metadata, args.report_path, jsonl_path=args.jsonl_path, json_path=args.json_path)
    print(json.dumps(metadata["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
