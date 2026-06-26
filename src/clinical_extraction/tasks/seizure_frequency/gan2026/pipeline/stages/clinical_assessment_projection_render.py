"""Project and render saved ClinicalAssessment mechanics artifacts."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.assessment_draft import (
    AssessmentDraft,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.clinical_assessment import (
    ClinicalAssessment,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.projection_render import (
    PROJECTION_POLICY_ID,
    RENDER_POLICY_ID,
    SCHEMA_VERSION,
    FinalRenderedLabel,
    ProjectionDecision,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.clinical_assessment_assembly import (
    assemble_clinical_assessment,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.pipeline.stages import (
    evidence_gating,
    label_render,
    projection_semantics,
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
        "ytd_instrumentation": (
            projection_decision.model_dump().get("ytd_instrumentation")
            if projection_decision is not None
            else None
        ),
    }


def project_and_render(
    assessment: ClinicalAssessment,
    *,
    candidate_set: CandidateSet,
    disabled_ablation_switches: set[str] | frozenset[str] | None = None,
) -> tuple[ProjectionDecision, FinalRenderedLabel]:
    source_ids = evidence_gating.source_ids_for_assessment(assessment, candidate_set)
    selected_evidence_status = evidence_gating.selected_evidence_status_for_assessment(
        assessment,
        candidate_set,
    )
    outcome = projection_semantics.project_label_semantics(
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
        ytd_instrumentation=outcome.ytd_instrumentation,
    )
    rendered_label, render_basis, render_issues = label_render.render_label(projection)
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
        draft = AssessmentDraft.model_validate(draft_payload)
    except ValidationError as exc:
        return None, [f"assessment_draft_invalid:{error['msg']}" for error in exc.errors()]
    return assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
        component_owner="llm_candidate_set_clinical_assessment",
        disabled_ablation_switches=disabled_ablation_switches,
    )


def main() -> int:
    """Deprecated: use experiments.projection_render_cli.main instead."""
    from clinical_extraction.tasks.seizure_frequency.gan2026.experiments import (
        projection_render_cli,
    )

    return projection_render_cli.main()


if __name__ == "__main__":
    raise SystemExit(main())
