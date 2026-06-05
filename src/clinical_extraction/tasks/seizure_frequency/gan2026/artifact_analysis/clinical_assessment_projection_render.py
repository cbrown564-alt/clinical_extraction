"""Project and render saved ClinicalAssessment mechanics artifacts."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.clinical_assessment import (
    ClinicalAssessment,
    NormalizedBurden,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.projection_render import (
    PROJECTION_POLICY_ID,
    RENDER_POLICY_ID,
    SCHEMA_VERSION,
    FinalRenderedLabel,
    ProjectionDecision,
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


def build_projection_render_artifact(
    assessment_rows: Sequence[Mapping[str, Any]],
    *,
    candidate_sets: Mapping[int, CandidateSet],
    assessment_artifact_path: str = str(DEFAULT_ASSESSMENT_JSONL_PATH),
    candidate_set_artifact_path: str = str(DEFAULT_CANDIDATE_SET_JSONL_PATH),
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = [
        build_projection_render_row(row, candidate_sets=candidate_sets)
        for row in assessment_rows
    ]
    return rows, summarize_rows(
        rows,
        assessment_artifact_path=assessment_artifact_path,
        candidate_set_artifact_path=candidate_set_artifact_path,
    )


def build_projection_render_row(
    assessment_row: Mapping[str, Any],
    *,
    candidate_sets: Mapping[int, CandidateSet],
) -> dict[str, Any]:
    source_row_index = int(assessment_row["source_row_index"])
    candidate_set = candidate_sets.get(source_row_index)
    parse_errors = list(assessment_row.get("parse_errors") or [])
    row_issues: list[str] = []
    clinical_assessment: ClinicalAssessment | None = None

    if candidate_set is None:
        row_issues.append("candidate_set_missing")
    else:
        clinical_assessment, assembly_issues = _reassemble_assessment(
            assessment_row,
            candidate_set=candidate_set,
        )
        row_issues.extend(assembly_issues)

    projection_decision: ProjectionDecision | None = None
    final_rendered_label: FinalRenderedLabel | None = None
    if clinical_assessment is not None:
        projection_decision, final_rendered_label = project_and_render(
            clinical_assessment,
            candidate_set=candidate_set,
        )

    return {
        "artifact_kind": "gan2026_clinical_assessment_projection_render_row",
        "source_row_index": source_row_index,
        "split": assessment_row.get("split", "validation"),
        "split_manifest": assessment_row.get("split_manifest", "gan2026_split_v1"),
        "schema_version": SCHEMA_VERSION,
        "projection_policy_id": PROJECTION_POLICY_ID,
        "render_policy_id": RENDER_POLICY_ID,
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
    }


def project_and_render(
    assessment: ClinicalAssessment,
    *,
    candidate_set: CandidateSet,
) -> tuple[ProjectionDecision, FinalRenderedLabel]:
    source_ids = _source_ids_for_assessment(assessment, candidate_set)
    projection_label, projection_basis, projection_issues = _project_label_semantics(assessment)
    projection = ProjectionDecision(
        source_row_index=assessment.source_row_index,
        component_owner="clinical_assessment_projection",
        projection_kind=assessment.assessment_kind,
        projection_basis=projection_basis,
        projected_label_semantics=projection_label or "",
        source_assessment_kind=assessment.assessment_kind,
        source_aggregation_policy=assessment.aggregation_policy,
        source_candidate_ids=list(assessment.primary_candidate_ids),
        source_ids=source_ids,
        projection_issues=[*assessment.normalization_issues, *projection_issues],
    )
    rendered_label, render_basis, render_issues = _render_label(projection)
    rendered = FinalRenderedLabel(
        source_row_index=assessment.source_row_index,
        component_owner="final_label_renderer",
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
    issue_counts = Counter(
        issue
        for row in rows
        for issue in [
            *list(row.get("row_issues") or []),
            *list((row.get("projection_decision") or {}).get("projection_issues") or []),
            *list((row.get("final_rendered_label") or {}).get("render_issues") or []),
        ]
    )
    return {
        "artifact_kind": "gan2026_clinical_assessment_projection_render",
        "schema_version": SCHEMA_VERSION,
        "assessment_artifact_path": assessment_artifact_path,
        "candidate_set_artifact_path": candidate_set_artifact_path,
        "row_count": len(rows),
        "claim_boundary": (
            "Projection/render mechanics only over saved validation250 artifacts. "
            "This artifact renders labels when deterministic v0 policy can do so, "
            "but scoring is disabled and no benchmark-comparable claim is made."
        ),
        "summary": {
            "projection_rows": len(projected),
            "rendered_label_rows": len(rendered),
            "null_rendered_label_rows": len(null_rendered),
            "row_issue_rows": sum(bool(row.get("row_issues")) for row in rows),
            "projection_kind_counts": dict(sorted(projection_kind_counts.items())),
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
) -> tuple[ClinicalAssessment | None, list[str]]:
    draft_payload = row.get("assessment_draft")
    if not isinstance(draft_payload, Mapping):
        return None, ["assessment_draft_missing"]
    try:
        draft = assessment_probe.AssessmentDraft.model_validate(draft_payload)
    except ValidationError as exc:
        return None, [f"assessment_draft_invalid:{error['msg']}" for error in exc.errors()]
    return assessment_probe.assemble_clinical_assessment(draft, candidate_set=candidate_set)


def _project_label_semantics(
    assessment: ClinicalAssessment,
) -> tuple[str | None, str, list[str]]:
    burden = assessment.normalized_burden
    if assessment.assessment_kind == "frequency_rate":
        label = _rate_label(burden)
        if label is None:
            return None, "frequency_rate", ["frequency_rate_operands_incomplete"]
        return label, "frequency_rate", []
    if assessment.assessment_kind == "cluster_frequency":
        return _cluster_label(burden)
    if assessment.assessment_kind == "seizure_free":
        label = _seizure_free_label(burden)
        if label is None:
            return None, "seizure_free_duration", ["seizure_free_duration_required"]
        return label, "seizure_free_duration", []
    if assessment.assessment_kind == "unknown_frequency":
        return "unknown", "unknown_frequency_internal_state", []
    if assessment.assessment_kind == "no_reference":
        return "no seizure frequency reference", "no_reference_internal_state", []
    return None, "unresolved_multiple", ["unresolved_multiple_not_renderable"]


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


def _cluster_label(burden: NormalizedBurden) -> tuple[str | None, str, list[str]]:
    if (
        burden.cluster_count_low is None
        or burden.cluster_count_high is None
        or burden.cluster_period_low is None
        or burden.cluster_period_high is None
        or burden.cluster_period_unit is None
    ):
        return None, "cluster_frequency", ["cluster_cadence_operands_incomplete"]
    cadence = (
        f"{_format_range(burden.cluster_count_low, burden.cluster_count_high)} "
        f"cluster per {_format_cluster_period(burden)}"
    )
    if burden.events_per_cluster_low is None or burden.events_per_cluster_high is None:
        simple_rate = (
            f"{_format_range(burden.cluster_count_low, burden.cluster_count_high)} "
            f"per {_format_cluster_period(burden)}"
        )
        return simple_rate, "cluster_cadence_without_size", []
    label = (
        f"{cadence}, "
        f"{_format_range(burden.events_per_cluster_low, burden.events_per_cluster_high)} "
        "per cluster"
    )
    return label, "cluster_cadence_with_events_per_cluster", []


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
    args = parser.parse_args(argv)

    candidate_sets = selector_probe.load_candidate_sets(args.candidate_set_jsonl)
    rows, metadata = build_projection_render_artifact(
        load_jsonl_rows(args.assessment_jsonl),
        candidate_sets=candidate_sets,
        assessment_artifact_path=str(args.assessment_jsonl),
        candidate_set_artifact_path=str(args.candidate_set_jsonl),
    )
    write_jsonl_rows(rows, args.jsonl_path)
    write_summary_json(metadata, args.json_path)
    write_report(metadata, args.report_path, jsonl_path=args.jsonl_path, json_path=args.json_path)
    print(json.dumps(metadata["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
