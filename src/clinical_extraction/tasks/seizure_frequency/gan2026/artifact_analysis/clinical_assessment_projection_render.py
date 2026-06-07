"""Project and render saved ClinicalAssessment mechanics artifacts."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
    candidate_source_phrase,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.clinical_assessment import (
    ClinicalAssessment,
    NormalizedBurden,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.projection_render import (
    PROJECTION_POLICY_ID,
    RENDER_POLICY_ID,
    SCHEMA_VERSION,
    FinalRenderedLabel,
    ProjectionDecision,
    ProjectionOwner,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm_candidate_set_clinical_assessment_probe as assessment_probe,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm_candidate_set_selector_schema_probe as selector_probe,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.selected_evidence import (
    selected_evidence_derivation,
)

DEFAULT_ASSESSMENT_JSONL_PATH = Path(
    "experiments/"
    "gan2026_candidate_set_clinical_assessment_probe_live_validation250_"
    "gpt41mini_v3nested_v2.jsonl"
)
DEFAULT_CANDIDATE_SET_JSONL_PATH = Path(
    "experiments/gan2026_validation250_candidate_set_v3_nested_dedupe.jsonl"
)
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_clinical_assessment_projection_render_validation250_v0.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_clinical_assessment_projection_render_validation250_v0.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_clinical_assessment_projection_render_validation250_v0.md"
)


@dataclass(frozen=True)
class ProjectionOutcome:
    label: str | None
    basis: str
    owner: ProjectionOwner
    rule_id: str
    issues: list[str]


def build_projection_render_artifact(
    assessment_rows: Sequence[Mapping[str, Any]],
    *,
    candidate_sets: Mapping[int, CandidateSet],
    assessment_artifact_path: str = str(DEFAULT_ASSESSMENT_JSONL_PATH),
    candidate_set_artifact_path: str = str(DEFAULT_CANDIDATE_SET_JSONL_PATH),
    disabled_ablation_switches: set[str] | frozenset[str] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = [
        build_projection_render_row(
            row,
            candidate_sets=candidate_sets,
            disabled_ablation_switches=disabled_ablation_switches,
        )
        for row in assessment_rows
    ]
    return rows, summarize_rows(
        rows,
        assessment_artifact_path=assessment_artifact_path,
        candidate_set_artifact_path=candidate_set_artifact_path,
        disabled_ablation_switches=disabled_ablation_switches,
    )


def build_projection_render_row(
    assessment_row: Mapping[str, Any],
    *,
    candidate_sets: Mapping[int, CandidateSet],
    disabled_ablation_switches: set[str] | frozenset[str] | None = None,
) -> dict[str, Any]:
    source_row_index = int(assessment_row["source_row_index"])
    candidate_set = candidate_sets.get(source_row_index)
    disabled_switches = frozenset(disabled_ablation_switches or ())
    parse_errors = list(assessment_row.get("parse_errors") or [])
    row_issues: list[str] = []
    clinical_assessment: ClinicalAssessment | None = None

    if candidate_set is None:
        row_issues.append("candidate_set_missing")
    else:
        clinical_assessment, assembly_issues = _reassemble_assessment(
            assessment_row,
            candidate_set=candidate_set,
            disabled_ablation_switches=disabled_switches,
        )
        row_issues.extend(assembly_issues)

    projection_decision: ProjectionDecision | None = None
    final_rendered_label: FinalRenderedLabel | None = None
    if clinical_assessment is not None:
        projection_decision, final_rendered_label = project_and_render(
            clinical_assessment,
            candidate_set=candidate_set,
            disabled_ablation_switches=disabled_switches,
        )

    ytd_instrumentation = None
    if projection_decision is not None:
        cleaned_issues = []
        for issue in projection_decision.projection_issues:
            if issue.startswith("ytd_instrumentation:"):
                parts = issue[len("ytd_instrumentation:"):].split(";")
                ytd_instrumentation = {}
                for part in parts:
                    if "=" in part:
                        k, v = part.split("=", 1)
                        ytd_instrumentation[k] = int(v) if v.isdigit() else v
            else:
                cleaned_issues.append(issue)
        projection_decision = projection_decision.model_copy(update={"projection_issues": cleaned_issues})

    return {
        "artifact_kind": "gan2026_clinical_assessment_projection_render_row",
        "source_row_index": source_row_index,
        "split": assessment_row.get("split", "validation"),
        "split_manifest": assessment_row.get("split_manifest", "gan2026_split_v1"),
        "schema_version": SCHEMA_VERSION,
        "projection_policy_id": PROJECTION_POLICY_ID,
        "render_policy_id": RENDER_POLICY_ID,
        "disabled_ablation_switches": sorted(disabled_switches),
        "scoring_enabled": False,
        "claim_boundary": (
            "mechanics artifact from saved ClinicalAssessment and CandidateSet rows; "
            "no model calls, scoring, or benchmark-comparable claim"
        ),
        "source_artifacts": {
            "assessment_prompt_version": assessment_row.get("prompt_version"),
            "assessment_schema_version": assessment_row.get("schema_version"),
        },
        "input_parse_errors": parse_errors,
        "row_issues": row_issues,
        "clinical_assessment": (
            clinical_assessment.model_dump() if clinical_assessment is not None else None
        ),
        "projection_decision": (
            projection_decision.model_dump() if projection_decision is not None else None
        ),
        "final_rendered_label": (
            final_rendered_label.model_dump() if final_rendered_label is not None else None
        ),
        "ytd_instrumentation": ytd_instrumentation,
    }


def project_and_render(
    assessment: ClinicalAssessment,
    *,
    candidate_set: CandidateSet,
    disabled_ablation_switches: set[str] | frozenset[str] | None = None,
) -> tuple[ProjectionDecision, FinalRenderedLabel]:
    source_ids = _source_ids_for_assessment(assessment, candidate_set)
    selected_evidence_status = _selected_evidence_status_for_assessment(
        assessment,
        candidate_set,
    )
    outcome = _project_label_semantics(
        assessment,
        candidate_set=candidate_set,
        disabled_ablation_switches=disabled_ablation_switches,
    )
    projection = ProjectionDecision(
        source_row_index=assessment.source_row_index,
        component_owner=outcome.owner,
        projection_owner=outcome.owner,
        projection_rule_id=outcome.rule_id,
        projection_kind=assessment.assessment_kind,
        projection_basis=outcome.basis,
        projected_label_semantics=outcome.label or "",
        source_assessment_kind=assessment.assessment_kind,
        source_aggregation_policy=assessment.aggregation_policy,
        source_normalized_phrase=assessment.normalized_burden.source_normalized_phrase,
        source_candidate_ids=list(assessment.primary_candidate_ids),
        source_ids=source_ids,
        selected_evidence_status=selected_evidence_status,
        projection_issues=[*assessment.normalization_issues, *outcome.issues],
    )
    rendered_label, render_basis, render_issues = _render_label(projection)
    rendered = FinalRenderedLabel(
        source_row_index=assessment.source_row_index,
        component_owner=projection.projection_owner,
        projection_owner=projection.projection_owner,
        projection_rule_id=projection.projection_rule_id,
        rendered_label=rendered_label,
        render_basis=render_basis,
        render_issues=render_issues,
    )
    return projection, rendered


def summarize_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    assessment_artifact_path: str = str(DEFAULT_ASSESSMENT_JSONL_PATH),
    candidate_set_artifact_path: str = str(DEFAULT_CANDIDATE_SET_JSONL_PATH),
    disabled_ablation_switches: set[str] | frozenset[str] | None = None,
) -> dict[str, Any]:
    projected = [row for row in rows if row.get("projection_decision")]
    rendered = [
        row
        for row in rows
        if (row.get("final_rendered_label") or {}).get("rendered_label") is not None
    ]
    null_rendered = [
        row
        for row in rows
        if row.get("final_rendered_label")
        and (row.get("final_rendered_label") or {}).get("rendered_label") is None
    ]
    projection_kind_counts = Counter(
        str((row.get("projection_decision") or {}).get("projection_kind"))
        for row in projected
    )
    render_basis_counts = Counter(
        str((row.get("final_rendered_label") or {}).get("render_basis"))
        for row in rows
        if row.get("final_rendered_label")
    )
    projection_owner_counts = Counter(
        str((row.get("projection_decision") or {}).get("projection_owner"))
        for row in projected
    )
    projection_rule_counts = Counter(
        str((row.get("projection_decision") or {}).get("projection_rule_id"))
        for row in projected
    )
    issue_counts = Counter(
        issue
        for row in rows
        for issue in [
            *list(row.get("row_issues") or []),
            *list((row.get("projection_decision") or {}).get("projection_issues") or []),
            *list((row.get("final_rendered_label") or {}).get("render_issues") or []),
        ]
    )
    surface_label = f"validation{len(rows)}"
    disabled_switches = sorted(disabled_ablation_switches or [])
    return {
        "artifact_kind": "gan2026_clinical_assessment_projection_render",
        "schema_version": SCHEMA_VERSION,
        "assessment_artifact_path": assessment_artifact_path,
        "candidate_set_artifact_path": candidate_set_artifact_path,
        "disabled_ablation_switches": disabled_switches,
        "row_count": len(rows),
        "claim_boundary": (
            f"Projection/render mechanics only over saved {surface_label} artifacts. "
            "This artifact renders labels when deterministic v0 policy can do so, "
            "but scoring is disabled and no benchmark-comparable claim is made."
        ),
        "summary": {
            "projection_rows": len(projected),
            "rendered_label_rows": len(rendered),
            "null_rendered_label_rows": len(null_rendered),
            "row_issue_rows": sum(bool(row.get("row_issues")) for row in rows),
            "projection_kind_counts": dict(sorted(projection_kind_counts.items())),
            "projection_owner_counts": dict(sorted(projection_owner_counts.items())),
            "projection_rule_counts": dict(sorted(projection_rule_counts.items())),
            "render_basis_counts": dict(sorted(render_basis_counts.items())),
            "issue_counts": dict(sorted(issue_counts.items())),
            "null_rendered_source_row_indices": [
                int(row["source_row_index"]) for row in null_rendered
            ][:25],
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
        "# Gan 2026 ClinicalAssessment Projection/Render Mechanics",
        "",
        str(metadata["claim_boundary"]),
        "",
        "## Artifacts",
        "",
        f"- Projection/render JSONL: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        f"- Assessment source: `{metadata['assessment_artifact_path']}`",
        f"- CandidateSet source: `{metadata['candidate_set_artifact_path']}`",
        f"- Disabled ablation switches: `{metadata.get('disabled_ablation_switches') or []}`",
        "",
        "## Summary",
        "",
        f"- Rows: {metadata['row_count']}",
        f"- Projection rows: {summary['projection_rows']}",
        f"- Rendered-label rows: {summary['rendered_label_rows']}",
        f"- Null rendered-label rows: {summary['null_rendered_label_rows']}",
        f"- Row issue rows: {summary['row_issue_rows']}",
        "",
        "## Projection Kinds",
        "",
    ]
    for kind, count in summary["projection_kind_counts"].items():
        lines.append(f"- `{kind}`: {count}")
    lines.extend(["", "## Projection Owners", ""])
    for owner, count in summary["projection_owner_counts"].items():
        lines.append(f"- `{owner}`: {count}")
    lines.extend(["", "## Projection Rules", ""])
    for rule_id, count in summary["projection_rule_counts"].items():
        lines.append(f"- `{rule_id}`: {count}")
    lines.extend(["", "## Render Bases", ""])
    for basis, count in summary["render_basis_counts"].items():
        lines.append(f"- `{basis}`: {count}")
    lines.extend(["", "## Issues", ""])
    if not summary["issue_counts"]:
        lines.append("- None.")
    for issue, count in summary["issue_counts"].items():
        lines.append(f"- `{issue}`: {count}")
    lines.extend(["", "## Null Rendered Labels", ""])
    if not summary["null_rendered_source_row_indices"]:
        lines.append("- None.")
    else:
        lines.append(
            "- First rows: "
            + ", ".join(str(i) for i in summary["null_rendered_source_row_indices"])
        )
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _reassemble_assessment(
    row: Mapping[str, Any],
    *,
    candidate_set: CandidateSet,
    disabled_ablation_switches: frozenset[str] = frozenset(),
) -> tuple[ClinicalAssessment | None, list[str]]:
    draft_payload = row.get("assessment_draft")
    if not isinstance(draft_payload, Mapping):
        return None, ["assessment_draft_missing"]
    try:
        draft = assessment_probe.AssessmentDraft.model_validate(draft_payload)
    except ValidationError as exc:
        return None, [f"assessment_draft_invalid:{error['msg']}" for error in exc.errors()]
    return assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
        disabled_ablation_switches=disabled_ablation_switches,
    )


def _is_ytd_phrase(phrase: str) -> bool:
    lower = phrase.strip().lower()
    return bool(
        re.search(
            r"\b(?:ytd|year[- ]to[- ]date|so far this year|this year so far|since the beginning of the year|since (?:january|jan))\b",
            lower
        )
    )


def _project_label_semantics(
    assessment: ClinicalAssessment,
    *,
    candidate_set: CandidateSet,
    disabled_ablation_switches: set[str] | frozenset[str] | None = None,
) -> ProjectionOutcome:
    disabled_switches = frozenset(disabled_ablation_switches or ())
    burden = assessment.normalized_burden
    if assessment.assessment_kind == "frequency_rate":
        dominant_vague_label = _dominant_vague_current_burden_label(
            assessment,
            candidate_set,
        )
        if dominant_vague_label is not None:
            return ProjectionOutcome(
                dominant_vague_label,
                "dominant_vague_current_burden",
                "rate_projection_policy",
                "dominant_vague_current_burden_v0",
                [],
            )

        # Check G1: Date-Anchored Temporal Arithmetic (YTD Calibration)
        by_id = {candidate.candidate_id: candidate for candidate in candidate_set.candidates}
        primary_candidates = [by_id[cid] for cid in assessment.primary_candidate_ids if cid in by_id]
        
        ytd_candidate = None
        for candidate in primary_candidates:
            phrase = " ".join(
                part
                for part in [
                    candidate_source_phrase(candidate),
                    candidate.evidence_span.text,
                ]
                if part
            )
            if _is_ytd_phrase(phrase):
                ytd_candidate = candidate
                break

        is_ytd = ytd_candidate is not None or _is_ytd_phrase(burden.source_normalized_phrase)
        if is_ytd:
            ref_date_ctx = candidate_set.row_context.reference_date
            if ref_date_ctx is not None:
                if "project_date_anchored_ytd_denominator" in disabled_switches:
                    return ProjectionOutcome(
                        None,
                        "frequency_rate",
                        "rate_projection_policy",
                        "frequency_rate_values_v0",
                        ["frequency_rate_values_incomplete", "ablation_switch_disabled:project_date_anchored_ytd_denominator"],
                    )
                try:
                    ref_date = date.fromisoformat(ref_date_ctx.date)
                    elapsed_months = ref_date.month
                    ytd_burden = burden.model_copy(
                        update={
                            "period_low": float(elapsed_months),
                            "period_high": float(elapsed_months),
                            "period_unit": "month"
                        }
                    )
                    label = _rate_label(ytd_burden)
                    if label is not None:
                        source_phrase = ytd_candidate.evidence_span.text if ytd_candidate else burden.source_normalized_phrase
                        candidate_id = ytd_candidate.candidate_id if ytd_candidate else (assessment.primary_candidate_ids[0] if assessment.primary_candidate_ids else "unknown")
                        instrumentation_str = (
                            f"ytd_instrumentation:"
                            f"ytd_anchor_start={ref_date.year}-01-01;"
                            f"ytd_reference_date={ref_date_ctx.date};"
                            f"elapsed_months={elapsed_months};"
                            f"source_phrase={source_phrase};"
                            f"candidate_id={candidate_id}"
                        )
                        return ProjectionOutcome(
                            label,
                            "date_anchored_ytd_denominator",
                            "rate_projection_policy",
                            "date_anchored_ytd_denominator_v0",
                            [instrumentation_str],
                        )
                except Exception:
                    pass

        label = _rate_label(burden)
        if label is None:
            return ProjectionOutcome(
                None,
                "frequency_rate",
                "rate_projection_policy",
                "frequency_rate_values_v0",
                ["frequency_rate_values_incomplete"],
            )
        return ProjectionOutcome(
            label,
            "frequency_rate",
            "rate_projection_policy",
            "frequency_rate_values_v0",
            [],
        )
    if assessment.assessment_kind == "cluster_frequency":
        return _cluster_label(
            assessment,
            candidate_set=candidate_set,
            disabled_ablation_switches=disabled_switches,
        )
    if assessment.assessment_kind == "seizure_free":
        label = _seizure_free_label(burden)
        if label is None:
            return ProjectionOutcome(
                None,
                "seizure_free_duration",
                "boundary_projection_policy",
                "seizure_free_duration_required_v0",
                ["seizure_free_duration_required"],
            )
        if _has_seizure_free_proxy_evidence_overreach(assessment, candidate_set):
            return ProjectionOutcome(
                None,
                "seizure_free_proxy_evidence",
                "boundary_projection_policy",
                "seizure_free_proxy_evidence_block_v0",
                ["seizure_free_proxy_evidence_overreach"],
            )
        return ProjectionOutcome(
            label,
            "seizure_free_duration",
            "boundary_projection_policy",
            "seizure_free_duration_projection_v0",
            [],
        )
    if assessment.assessment_kind == "unknown_frequency":
        return ProjectionOutcome(
            "unknown",
            "unknown_frequency_internal_state",
            "benchmark_renderer",
            "unknown_frequency_sentinel_render_v0",
            [],
        )
    if assessment.assessment_kind == "no_reference":
        return ProjectionOutcome(
            "no seizure frequency reference",
            "no_reference_internal_state",
            "benchmark_renderer",
            "no_reference_sentinel_render_v0",
            [],
        )
    return ProjectionOutcome(
        None,
        "unresolved_multiple",
        "benchmark_renderer",
        "unresolved_multiple_no_render_v0",
        ["unresolved_multiple_not_renderable"],
    )


def _render_label(projection: ProjectionDecision) -> tuple[str | None, str, list[str]]:
    if projection.projected_label_semantics:
        return projection.projected_label_semantics, projection.projection_basis, []
    return None, projection.projection_basis, ["projection_semantics_missing"]


def _rate_label(burden: NormalizedBurden) -> str | None:
    if (
        burden.period_low is None
        or burden.period_high is None
        or burden.period_unit is None
    ):
        return None
    if burden.count_low is None or burden.count_high is None:
        if burden.vague_count is None:
            return None
        return f"{burden.vague_count} per {_format_period(burden)}"
    return f"{_format_range(burden.count_low, burden.count_high)} per {_format_period(burden)}"


def _cluster_label(
    assessment: ClinicalAssessment,
    *,
    candidate_set: CandidateSet,
    disabled_ablation_switches: frozenset[str] = frozenset(),
) -> ProjectionOutcome:
    burden = assessment.normalized_burden
    medication_cadence = _has_primary_medication_cadence(assessment, candidate_set)
    if (
        not medication_cadence
        and not _has_normalized_cluster_cadence(burden)
        and _has_unknown_cadence_multiple_cluster_burden(
            assessment,
            candidate_set,
        )
    ):
        return ProjectionOutcome(
            "unknown, multiple per cluster",
            "unknown_cadence_cluster_burden",
            "cluster_projection_policy",
            "unknown_cadence_multiple_per_cluster_v0",
            ["cluster_cadence_unknown_with_per_cluster_burden"],
        )
    cyclic_window = _has_primary_cyclic_vulnerability_window(assessment, candidate_set)
    if (
        burden.cluster_count_low is None
        or burden.cluster_count_high is None
        or burden.cluster_period_low is None
        or burden.cluster_period_high is None
        or burden.cluster_period_unit is None
    ):
        issues = ["cluster_cadence_values_incomplete"]
        if medication_cadence:
            issues.append("medication_cadence_ambiguity")
        if cyclic_window:
            issues.append("cyclic_window_without_event_count")
        return ProjectionOutcome(
            None,
            "cluster_frequency",
            "cluster_projection_policy",
            "cluster_cadence_values_required_v0",
            issues,
        )
    cadence = (
        f"{_format_range(burden.cluster_count_low, burden.cluster_count_high)} "
        f"cluster per {_format_cluster_period(burden)}"
    )
    if burden.events_per_cluster_low is None or burden.events_per_cluster_high is None:
        if medication_cadence:
            return ProjectionOutcome(
                None,
                "cluster_frequency",
                "cluster_projection_policy",
                "cluster_cadence_as_event_rate_when_size_absent_v0",
                ["medication_cadence_ambiguity"],
            )
        if "project_cluster_cadence_default_multiple_per_cluster" not in disabled_ablation_switches:
            default_cluster_label = f"{cadence}, multiple per cluster"
            return ProjectionOutcome(
                default_cluster_label,
                "cluster_cadence_without_size",
                "cluster_projection_policy",
                "cluster_cadence_default_multiple_per_cluster_v0",
                [],
            )
        simple_rate = (
            f"{_format_range(burden.cluster_count_low, burden.cluster_count_high)} "
            f"per {_format_cluster_period(burden)}"
        )
        return ProjectionOutcome(
            simple_rate,
            "cluster_cadence_without_size",
            "cluster_projection_policy",
            "cluster_cadence_as_event_rate_when_size_absent_v0",
            [],
        )
    label = (
        f"{cadence}, "
        f"{_format_range(burden.events_per_cluster_low, burden.events_per_cluster_high)} "
        "per cluster"
    )
    return ProjectionOutcome(
        label,
        "cluster_cadence_with_events_per_cluster",
        "cluster_projection_policy",
        "cluster_cadence_with_events_per_cluster_v0",
        [],
    )


def _seizure_free_label(burden: NormalizedBurden) -> str | None:
    if (
        burden.seizure_free_duration_low is None
        or burden.seizure_free_duration_high is None
        or burden.seizure_free_duration_unit is None
    ):
        return None
    duration = _format_range(
        burden.seizure_free_duration_low,
        burden.seizure_free_duration_high,
    )
    return f"seizure free for {duration} {burden.seizure_free_duration_unit}"


def _format_period(burden: NormalizedBurden) -> str:
    assert burden.period_low is not None
    assert burden.period_high is not None
    assert burden.period_unit is not None
    if burden.period_low == burden.period_high == 1:
        return burden.period_unit
    return f"{_format_range(burden.period_low, burden.period_high)} {burden.period_unit}"


def _format_cluster_period(burden: NormalizedBurden) -> str:
    assert burden.cluster_period_low is not None
    assert burden.cluster_period_high is not None
    assert burden.cluster_period_unit is not None
    if burden.cluster_period_low == burden.cluster_period_high == 1:
        return burden.cluster_period_unit
    return (
        f"{_format_range(burden.cluster_period_low, burden.cluster_period_high)} "
        f"{burden.cluster_period_unit}"
    )


def _format_range(low: float, high: float) -> str:
    left = _format_number(low)
    right = _format_number(high)
    if left == right:
        return left
    return f"{left} to {right}"


def _format_number(value: float) -> str:
    return str(int(value)) if float(value).is_integer() else str(value)


def _source_ids_for_assessment(
    assessment: ClinicalAssessment,
    candidate_set: CandidateSet,
) -> list[str]:
    by_id = {candidate.candidate_id: candidate for candidate in candidate_set.candidates}
    source_ids: list[str] = []
    for candidate_id in assessment.primary_candidate_ids:
        candidate = by_id.get(candidate_id)
        if candidate is None:
            continue
        source_ids.extend(candidate.source_ids)
    return sorted(set(source_ids))


def _selected_evidence_status_for_assessment(
    assessment: ClinicalAssessment,
    candidate_set: CandidateSet,
) -> dict[str, Any]:
    by_id = {candidate.candidate_id: candidate for candidate in candidate_set.candidates}
    primary_candidates = [
        candidate
        for candidate_id in assessment.primary_candidate_ids
        for candidate in [by_id.get(candidate_id)]
        if candidate is not None
    ]
    expected_source_ids = sorted(
        set(
            source_id
            for candidate in primary_candidates
            if _candidate_has_exact_trace_evidence(candidate)
            for source_id in candidate.source_ids
        )
    )
    selected_source_ids = _source_ids_for_assessment(assessment, candidate_set)
    if not primary_candidates:
        exact_trace: bool | None = None
        trace_basis = "no_primary_candidate"
    else:
        exact_trace = all(
            _candidate_has_exact_trace_evidence(candidate) for candidate in primary_candidates
        )
        trace_basis = (
            "primary_candidate_exact_evidence"
            if exact_trace
            else "primary_candidate_evidence_missing"
        )
    missing_expected_source_ids = [
        source_id for source_id in expected_source_ids if source_id not in selected_source_ids
    ]
    unexpected_source_ids = [
        source_id for source_id in selected_source_ids if source_id not in expected_source_ids
    ]
    if exact_trace is False:
        source_id_status = "invalid"
    elif exact_trace is None:
        source_id_status = "not_applicable"
    elif not selected_source_ids:
        source_id_status = "not_instrumented"
    elif any("unresolved" in source_id for source_id in selected_source_ids):
        source_id_status = "invalid"
    elif missing_expected_source_ids:
        source_id_status = "invalid"
    else:
        source_id_status = "valid"
    return {
        "exact_trace": exact_trace,
        "source_id_status": source_id_status,
        "source_id_trace": {
            "selected_source_ids": selected_source_ids,
            "expected_source_ids": expected_source_ids,
            "missing_expected_source_ids": missing_expected_source_ids,
            "unexpected_source_ids": unexpected_source_ids,
            "trace_basis": trace_basis,
        },
    }


def _exact_trace_phrases(candidate: Any) -> list[str]:
    phrases = [
        candidate_source_phrase(candidate) or "",
        candidate.evidence_span.text,
    ]
    cleaned = [phrase.strip() for phrase in phrases if phrase and phrase.strip()]
    seen: set[str] = set()
    deduped: list[str] = []
    for phrase in cleaned:
        if phrase in seen:
            continue
        seen.add(phrase)
        deduped.append(phrase)
    return deduped


def _candidate_has_exact_trace_evidence(candidate: Any) -> bool:
    return bool(_exact_trace_phrases(candidate))


def _has_primary_medication_cadence(
    assessment: ClinicalAssessment,
    candidate_set: CandidateSet,
) -> bool:
    by_id = {candidate.candidate_id: candidate for candidate in candidate_set.candidates}
    return any(
        _is_medication_cadence_text(
            " ".join(
                part
                for part in [
                    _candidate_source_phrase(candidate),
                    candidate.evidence_span.text,
                ]
                if part
            )
        )
        for candidate_id in assessment.primary_candidate_ids
        for candidate in [by_id.get(candidate_id)]
        if candidate is not None
    )


def _has_seizure_free_proxy_evidence_overreach(
    assessment: ClinicalAssessment,
    candidate_set: CandidateSet,
) -> bool:
    by_id = {candidate.candidate_id: candidate for candidate in candidate_set.candidates}
    primary_candidates = [
        candidate
        for candidate_id in assessment.primary_candidate_ids
        for candidate in [by_id.get(candidate_id)]
        if candidate is not None
    ]
    if not primary_candidates:
        return False
    texts = [
        _canonicalize_derivation_text(
            " ".join(
                part
                for part in [
                    _candidate_source_phrase(candidate),
                    candidate.evidence_span.text,
                ]
                if part
            )
        )
        for candidate in primary_candidates
    ]
    explicit = any(_is_explicit_seizure_free_text(text) for text in texts)
    proxy_or_conditional = any(
        _is_seizure_free_proxy_or_conditional_text(text) for text in texts
    )
    unresolved = any(
        any("unresolved" in source_id for source_id in candidate.source_ids)
        for candidate in primary_candidates
    )
    return (proxy_or_conditional or unresolved) and not explicit


def _is_explicit_seizure_free_text(text: str) -> bool:
    lower = text.lower()
    return any(
        marker in lower
        for marker in (
            "no seizures",
            "no seizure",
            "no events",
            "no further events",
            "seizure-free",
            "seizure free",
            "free of seizures",
        )
    )


def _is_seizure_free_proxy_or_conditional_text(text: str) -> bool:
    lower = text.lower()
    return any(
        marker in lower
        for marker in (
            "rescue medication",
            "rescue med",
            "required",
            "injur",
            "admission",
            "attendances",
            "if breakthrough events recur",
            "breakthrough events recur",
            "if this occurs",
            "better over",
        )
    )


def _dominant_vague_current_burden_label(
    assessment: ClinicalAssessment,
    candidate_set: CandidateSet,
) -> str | None:
    if assessment.aggregation_policy != "additive_same_window":
        return None
    by_id = {candidate.candidate_id: candidate for candidate in candidate_set.candidates}
    derived: list[tuple[str, float, Any]] = []
    for candidate_id in assessment.primary_candidate_ids:
        candidate = by_id.get(candidate_id)
        if candidate is None:
            continue
        if candidate.temporality not in {"current", "recent"}:
            continue
        text = " ".join(
            part
            for part in [
                _candidate_source_phrase(candidate),
                candidate.evidence_span.text,
            ]
            if part
        )
        text = _canonicalize_derivation_text(text)
        if not text or _is_medication_cadence_text(text):
            continue
        label = selected_evidence_derivation.prediction_label_from_selected_evidence(
            text
        )
        if label in {None, "unknown", "no seizure frequency reference"}:
            continue
        try:
            record = label_to_frequency_record(label)
        except ValueError:
            continue
        derived.append((label, float(record.monthly_frequency), candidate))
    vague = [
        item
        for item in derived
        if item[0].startswith("multiple per ")
        and _is_dominant_vague_frequency_text(
            " ".join(
                part
                for part in [
                    _candidate_source_phrase(item[2]),
                    item[2].evidence_span.text,
                ]
                if part
            )
        )
    ]
    if not vague or len(derived) < 2:
        return None
    dominant_label, dominant_frequency, _ = max(vague, key=lambda item: item[1])
    context_frequencies = [
        frequency for label, frequency, _ in derived if label != dominant_label
    ]
    if not context_frequencies:
        return None
    if all(frequency < dominant_frequency for frequency in context_frequencies):
        return dominant_label
    return None


def _is_dominant_vague_frequency_text(text: str) -> bool:
    lower = text.lower()
    return any(
        marker in lower
        for marker in (
            "most weekdays",
            "most days",
            "multiple days",
            "several days",
            "many days",
        )
    )


def _canonicalize_derivation_text(text: str) -> str:
    return text.replace("\u2013", "-").replace("\u2014", "-").replace("\u2212", "-")


def _has_primary_cyclic_vulnerability_window(
    assessment: ClinicalAssessment,
    candidate_set: CandidateSet,
) -> bool:
    by_id = {candidate.candidate_id: candidate for candidate in candidate_set.candidates}
    return any(
        _is_cyclic_vulnerability_window_text(
            " ".join(
                part
                for part in [
                    _candidate_source_phrase(candidate),
                    candidate.evidence_span.text,
                ]
                if part
            )
        )
        and not _has_vague_multiple_burden(
            candidate.cluster_details.events_per_cluster
            if candidate.cluster_details is not None
            else None
        )
        for candidate_id in assessment.primary_candidate_ids
        for candidate in [by_id.get(candidate_id)]
        if candidate is not None and candidate.candidate_kind == "cluster_frequency"
    )


def _has_normalized_cluster_cadence(burden: NormalizedBurden) -> bool:
    return (
        burden.cluster_count_low is not None
        and burden.cluster_count_high is not None
        and burden.cluster_period_low is not None
        and burden.cluster_period_high is not None
        and burden.cluster_period_unit is not None
    )


def _has_unknown_cadence_multiple_cluster_burden(
    assessment: ClinicalAssessment,
    candidate_set: CandidateSet,
) -> bool:
    by_id = {candidate.candidate_id: candidate for candidate in candidate_set.candidates}
    if _has_competing_renderable_frequency_candidate(assessment, candidate_set):
        return False
    for candidate_id in assessment.primary_candidate_ids:
        candidate = by_id.get(candidate_id)
        if candidate is None or candidate.candidate_kind != "cluster_frequency":
            continue
        if candidate.event_type not in {"seizure", "seizure_like_event"}:
            continue
        if candidate.cluster_details is None:
            continue
        if _has_cluster_recurrence_cadence(candidate):
            continue
        if _has_vague_multiple_burden(candidate.cluster_details.events_per_cluster):
            return True
    return False


def _has_competing_renderable_frequency_candidate(
    assessment: ClinicalAssessment,
    candidate_set: CandidateSet,
) -> bool:
    primary_ids = set(assessment.primary_candidate_ids)
    for candidate in candidate_set.candidates:
        if candidate.candidate_id in primary_ids:
            continue
        if candidate.candidate_kind != "frequency_rate" or candidate.frequency is None:
            continue
        text = " ".join(
            part
            for part in [candidate.frequency.source_phrase, candidate.evidence_span.text]
            if part
        )
        if _is_medication_cadence_text(text):
            continue
        if _looks_renderable_frequency_text(text):
            return True
    return False


def _has_cluster_recurrence_cadence(candidate: Any) -> bool:
    assert candidate.cluster_details is not None
    text = " ".join(
        part
        for part in [
            candidate.cluster_details.cluster_frequency,
            candidate.cluster_details.cluster_period,
        ]
        if part
    ).lower()
    if not text:
        return False
    if any(marker in text for marker in ("unknown", "unclear", "not specified")):
        return False
    if any(
        marker in text
        for marker in (
            "single day",
            "one day",
            "24-hour",
            "24 hour",
            "within that day",
        )
    ):
        return False
    return any(
        marker in text
        for marker in (
            "per ",
            "every ",
            "daily",
            "weekly",
            "monthly",
            "yearly",
            "annually",
            "day",
            "week",
            "month",
            "year",
        )
    )


def _has_vague_multiple_burden(text: str | None) -> bool:
    if not text:
        return False
    lower = text.lower()
    return any(
        marker in lower
        for marker in (
            "multiple",
            "several",
            "many",
            "few",
            "repeated",
            "cluster of events",
            "episodes",
            "events",
        )
    )


def _looks_renderable_frequency_text(text: str) -> bool:
    lower = text.lower()
    return any(
        marker in lower
        for marker in (
            "per day",
            "per week",
            "per month",
            "per year",
            "daily",
            "weekly",
            "monthly",
            "yearly",
        )
    )


def _candidate_source_phrase(candidate: Any) -> str:
    if candidate.frequency is not None:
        return candidate.frequency.source_phrase or ""
    if candidate.cluster_details is not None:
        return " ".join(
            part
            for part in [
                candidate.cluster_details.cluster_frequency,
                candidate.cluster_details.events_per_cluster,
                candidate.cluster_details.cluster_count,
                candidate.cluster_details.cluster_period,
            ]
            if part
        )
    if candidate.seizure_free is not None:
        return candidate.seizure_free.source_phrase or ""
    if candidate.last_event_only is not None:
        return candidate.last_event_only.source_phrase or ""
    if candidate.unknown_frequency is not None:
        return candidate.unknown_frequency.source_phrase or ""
    if candidate.no_reference is not None:
        return candidate.no_reference.source_phrase or ""
    return ""


def _is_medication_cadence_text(text: str) -> bool:
    lower = text.lower()
    return any(
        marker in lower
        for marker in (
            "as needed",
            "as-needed",
            "clobazam",
            "rescue medication",
            "patient-led use",
            "treated with",
        )
    )


def _is_cyclic_vulnerability_window_text(text: str) -> bool:
    lower = text.lower()
    return any(
        marker in lower
        for marker in (
            "perimenstrual",
            "peri-menstrual",
            "catamenial",
            "menstrual",
            "menstruation",
            "period",
        )
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assessment-jsonl", type=Path, default=DEFAULT_ASSESSMENT_JSONL_PATH)
    parser.add_argument(
        "--candidate-set-jsonl",
        type=Path,
        default=DEFAULT_CANDIDATE_SET_JSONL_PATH,
    )
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument(
        "--disable-ablation-switch",
        action="append",
        default=[],
        help="Named reset-stage ablation switch to disable for this replay.",
    )
    args = parser.parse_args(argv)

    candidate_sets = selector_probe.load_candidate_sets(args.candidate_set_jsonl)
    rows, metadata = build_projection_render_artifact(
        load_jsonl_rows(args.assessment_jsonl),
        candidate_sets=candidate_sets,
        assessment_artifact_path=str(args.assessment_jsonl),
        candidate_set_artifact_path=str(args.candidate_set_jsonl),
        disabled_ablation_switches=set(args.disable_ablation_switch),
    )
    write_jsonl_rows(rows, args.jsonl_path)
    write_summary_json(metadata, args.json_path)
    write_report(metadata, args.report_path, jsonl_path=args.jsonl_path, json_path=args.json_path)
    print(json.dumps(metadata["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
