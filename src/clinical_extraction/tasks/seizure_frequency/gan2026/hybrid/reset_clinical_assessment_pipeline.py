"""Composable reset-stage ClinicalAssessment pipeline runner.

This module intentionally adds no new clinical logic. It wires the existing
reset-stage artifact builders into one replayable pipeline bundle:

CandidateSet + ClinicalAssessment -> Project/Render -> Score Audit -> Route -> V0 Decision
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    clinical_assessment_projection_render as projection_render,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    clinical_assessment_projection_score as projection_score,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    clinical_assessment_verification_decision as verification_decision,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    clinical_assessment_verification_route as verification_route,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm_candidate_set_selector_schema_probe as selector_probe,
)

PIPELINE_FAMILY = "reset_clinical_assessment_pipeline"
PIPELINE_VERSION = "gan2026_reset_clinical_assessment_pipeline_v0"
DEFAULT_OUTPUT_PREFIX = Path(
    "experiments/gan2026_reset_clinical_assessment_pipeline_validation250_v0"
)
CLAIM_BOUNDARY = (
    "validation-development reset-stage composition only; no model calls, no "
    "locked-test inspection, no benchmark-comparable promotion claim, and score "
    "context remains audit-only"
)


@dataclass(frozen=True)
class ResetClinicalAssessmentPipelineArtifact:
    """Rows and metadata produced by the composable reset-stage replay."""

    projection_render_rows: list[dict[str, Any]]
    score_rows: list[dict[str, Any]]
    route_rows: list[dict[str, Any]]
    decision_rows: list[dict[str, Any]]
    metadata: dict[str, Any]


@dataclass(frozen=True)
class ResetClinicalAssessmentPipelinePaths:
    """Output paths for the bundled replay artifacts."""

    pipeline_json: Path
    pipeline_report: Path
    projection_render_jsonl: Path
    projection_render_json: Path
    projection_render_report: Path
    score_jsonl: Path
    score_json: Path
    score_report: Path
    route_jsonl: Path
    route_json: Path
    route_report: Path
    decision_jsonl: Path
    decision_json: Path
    decision_report: Path


def build_reset_clinical_assessment_pipeline_artifact(
    *,
    assessment_rows: Sequence[Mapping[str, Any]],
    candidate_sets: Mapping[int, CandidateSet],
    gold_records: Mapping[int, GanFrequencyRecord],
    assessment_artifact_path: str,
    candidate_set_artifact_path: str,
    disabled_ablation_switches: set[str] | frozenset[str] | None = None,
    project_render_artifact_path: str | None = None,
    score_artifact_path: str | None = None,
    route_artifact_path: str | None = None,
) -> ResetClinicalAssessmentPipelineArtifact:
    """Run saved ClinicalAssessment rows through all reset deterministic stages."""
    from clinical_extraction.tasks.seizure_frequency.gan2026.runner import (
        build_unified_pipeline_artifact,
    )

    unified = build_unified_pipeline_artifact(
        architecture="hybrid",
        assessment_rows=assessment_rows,
        candidate_sets=candidate_sets,
        gold_records=gold_records,
        assessment_artifact_path=assessment_artifact_path,
        candidate_set_artifact_path=candidate_set_artifact_path,
        disabled_ablation_switches=disabled_ablation_switches,
        project_render_artifact_path=project_render_artifact_path,
        score_artifact_path=score_artifact_path,
        route_artifact_path=route_artifact_path,
    )
    metadata = summarize_pipeline_artifact(
        assessment_rows=assessment_rows,
        projection_render_metadata=unified.metadata["stage_metadata"]["projection_render"],
        score_metadata=unified.metadata["stage_metadata"]["score"],
        route_metadata=unified.metadata["stage_metadata"]["route"],
        decision_metadata=unified.metadata["stage_metadata"]["verification_decision"],
        assessment_artifact_path=assessment_artifact_path,
        candidate_set_artifact_path=candidate_set_artifact_path,
        disabled_ablation_switches=disabled_ablation_switches,
    )
    return ResetClinicalAssessmentPipelineArtifact(
        projection_render_rows=unified.projection_render_rows,
        score_rows=unified.score_rows,
        route_rows=unified.route_rows,
        decision_rows=unified.decision_rows,
        metadata=metadata,
    )


def summarize_pipeline_artifact(
    *,
    assessment_rows: Sequence[Mapping[str, Any]],
    projection_render_metadata: Mapping[str, Any],
    score_metadata: Mapping[str, Any],
    route_metadata: Mapping[str, Any],
    decision_metadata: Mapping[str, Any],
    assessment_artifact_path: str,
    candidate_set_artifact_path: str,
    disabled_ablation_switches: set[str] | frozenset[str] | None = None,
) -> dict[str, Any]:
    """Build a compact cross-stage summary for the composed replay."""

    projection_summary = dict(projection_render_metadata.get("summary") or {})
    score_summary = dict(score_metadata.get("summary") or {})
    route_summary = dict(route_metadata.get("summary") or {})
    decision_summary = dict(decision_metadata.get("summary") or {})
    return {
        "artifact_kind": "gan2026_reset_clinical_assessment_pipeline",
        "pipeline_family": PIPELINE_FAMILY,
        "pipeline_version": PIPELINE_VERSION,
        "claim_boundary": CLAIM_BOUNDARY,
        "source_artifacts": {
            "assessment_artifact_path": assessment_artifact_path,
            "candidate_set_artifact_path": candidate_set_artifact_path,
        },
        "disabled_ablation_switches": sorted(disabled_ablation_switches or []),
        "stage_metadata": {
            "projection_render": dict(projection_render_metadata),
            "score": dict(score_metadata),
            "route": dict(route_metadata),
            "verification_decision": dict(decision_metadata),
        },
        "summary": {
            "input_assessment_rows": len(assessment_rows),
            "projection_rows": int(projection_summary.get("projection_rows", 0)),
            "rendered_label_rows": int(projection_summary.get("rendered_label_rows", 0)),
            "null_rendered_label_rows": int(
                projection_summary.get("null_rendered_label_rows", 0)
            ),
            "scored_rows": int(score_summary.get("scored_rows", 0)),
            "purist_correct": int(score_summary.get("purist_correct", 0)),
            "routed_rows": int(route_summary.get("routed_rows", 0)),
            "decision_rows": int(decision_summary.get("decision_rows", 0)),
            "action_counts": dict(decision_summary.get("action_counts") or {}),
        },
    }


def stage_output_paths_from_prefix(prefix: str | Path) -> ResetClinicalAssessmentPipelinePaths:
    """Derive all stage output paths from one artifact prefix."""

    base = Path(prefix)
    return ResetClinicalAssessmentPipelinePaths(
        pipeline_json=base.with_suffix(".json"),
        pipeline_report=base.with_suffix(".md"),
        projection_render_jsonl=base.with_suffix(".projection_render.jsonl"),
        projection_render_json=base.with_suffix(".projection_render.json"),
        projection_render_report=base.with_suffix(".projection_render.md"),
        score_jsonl=base.with_suffix(".score.jsonl"),
        score_json=base.with_suffix(".score.json"),
        score_report=base.with_suffix(".score.md"),
        route_jsonl=base.with_suffix(".route.jsonl"),
        route_json=base.with_suffix(".route.json"),
        route_report=base.with_suffix(".route.md"),
        decision_jsonl=base.with_suffix(".verification_decision.jsonl"),
        decision_json=base.with_suffix(".verification_decision.json"),
        decision_report=base.with_suffix(".verification_decision.md"),
    )


def write_pipeline_artifact(
    artifact: ResetClinicalAssessmentPipelineArtifact,
    paths: ResetClinicalAssessmentPipelinePaths,
) -> None:
    """Write the composed pipeline bundle and each underlying stage artifact."""

    write_jsonl_rows(artifact.projection_render_rows, paths.projection_render_jsonl)
    projection_render.write_summary_json(
        artifact.metadata["stage_metadata"]["projection_render"],
        paths.projection_render_json,
    )
    projection_render.write_report(
        artifact.metadata["stage_metadata"]["projection_render"],
        paths.projection_render_report,
        jsonl_path=paths.projection_render_jsonl,
        json_path=paths.projection_render_json,
    )

    write_jsonl_rows(artifact.score_rows, paths.score_jsonl)
    projection_score.write_summary_json(
        artifact.metadata["stage_metadata"]["score"],
        paths.score_json,
    )
    projection_score.write_report(
        artifact.metadata["stage_metadata"]["score"],
        paths.score_report,
        jsonl_path=paths.score_jsonl,
        json_path=paths.score_json,
    )

    write_jsonl_rows(artifact.route_rows, paths.route_jsonl)
    verification_route.write_summary_json(
        artifact.metadata["stage_metadata"]["route"],
        paths.route_json,
    )
    verification_route.write_report(
        artifact.metadata["stage_metadata"]["route"],
        artifact.route_rows,
        paths.route_report,
        jsonl_path=paths.route_jsonl,
        json_path=paths.route_json,
    )

    write_jsonl_rows(artifact.decision_rows, paths.decision_jsonl)
    verification_decision.write_summary_json(
        artifact.metadata["stage_metadata"]["verification_decision"],
        paths.decision_json,
    )
    verification_decision.write_report(
        artifact.metadata["stage_metadata"]["verification_decision"],
        artifact.decision_rows,
        paths.decision_report,
        jsonl_path=paths.decision_jsonl,
        json_path=paths.decision_json,
    )

    write_summary_json(artifact.metadata, paths.pipeline_json)
    write_pipeline_report(artifact.metadata, paths.pipeline_report, paths=paths)


def write_summary_json(metadata: Mapping[str, Any], path: Path) -> None:
    """Write composed pipeline metadata as JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_pipeline_report(
    metadata: Mapping[str, Any],
    path: Path,
    *,
    paths: ResetClinicalAssessmentPipelinePaths,
) -> None:
    """Write a compact Markdown report for the composed reset-stage replay."""

    summary = metadata.get("summary") or {}
    action_counts = summary.get("action_counts") or {}
    lines = [
        "# Gan 2026 Reset ClinicalAssessment Pipeline",
        "",
        str(metadata["claim_boundary"]),
        "",
        "## Artifacts",
        "",
        f"- Summary JSON: `{paths.pipeline_json}`",
        f"- Projection/render JSONL: `{paths.projection_render_jsonl}`",
        f"- Score JSONL: `{paths.score_jsonl}`",
        f"- Route JSONL: `{paths.route_jsonl}`",
        f"- VerificationDecision JSONL: `{paths.decision_jsonl}`",
        "",
        "## Summary",
        "",
        f"- Input assessment rows: {summary.get('input_assessment_rows', 0)}",
        f"- Projection rows: {summary.get('projection_rows', 0)}",
        f"- Rendered-label rows: {summary.get('rendered_label_rows', 0)}",
        f"- Null rendered-label rows: {summary.get('null_rendered_label_rows', 0)}",
        f"- Scored rows: {summary.get('scored_rows', 0)}",
        f"- Purist-correct scored rows: {summary.get('purist_correct', 0)}",
        f"- Routed rows: {summary.get('routed_rows', 0)}",
        f"- VerificationDecision rows: {summary.get('decision_rows', 0)}",
        "",
        "## Verification Actions",
        "",
    ]
    if not action_counts:
        lines.append("- None.")
    for action, count in sorted(action_counts.items()):
        lines.append(f"- `{action}`: {count}")
    lines.extend(
        [
            "",
            "## Source Artifacts",
            "",
            (
                "- Assessment artifact: "
                f"`{metadata['source_artifacts']['assessment_artifact_path']}`"
            ),
            (
                "- CandidateSet artifact: "
                f"`{metadata['source_artifacts']['candidate_set_artifact_path']}`"
            ),
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def load_gold_records(split: str) -> dict[int, GanFrequencyRecord]:
    """Load Gan records keyed by source row index for audit-only scoring."""

    return {record.source_row_index: record for record in load_records_for_split(split)}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--assessment-jsonl",
        type=Path,
        default=projection_render.DEFAULT_ASSESSMENT_JSONL_PATH,
        help="Saved ClinicalAssessment probe JSONL to replay.",
    )
    parser.add_argument(
        "--candidate-set-jsonl",
        type=Path,
        default=projection_render.DEFAULT_CANDIDATE_SET_JSONL_PATH,
        help="CandidateSet JSONL used by the saved assessment rows.",
    )
    parser.add_argument(
        "--split",
        choices=("train", "validation", "test"),
        default="validation",
        help="Split used only to load gold records for audit scoring.",
    )
    parser.add_argument(
        "--output-prefix",
        type=Path,
        default=DEFAULT_OUTPUT_PREFIX,
        help="Prefix used to write the bundled stage artifacts.",
    )
    parser.add_argument(
        "--disable-ablation-switch",
        action="append",
        default=[],
        help="Named reset-stage ablation switch to disable during projection/render replay.",
    )
    args = parser.parse_args(argv)

    paths = stage_output_paths_from_prefix(args.output_prefix)
    candidate_sets = selector_probe.load_candidate_sets(args.candidate_set_jsonl)
    artifact = build_reset_clinical_assessment_pipeline_artifact(
        assessment_rows=load_jsonl_rows(args.assessment_jsonl),
        candidate_sets=candidate_sets,
        gold_records=load_gold_records(args.split),
        assessment_artifact_path=str(args.assessment_jsonl),
        candidate_set_artifact_path=str(args.candidate_set_jsonl),
        disabled_ablation_switches=set(args.disable_ablation_switch),
        project_render_artifact_path=str(paths.projection_render_jsonl),
        score_artifact_path=str(paths.score_jsonl),
        route_artifact_path=str(paths.route_jsonl),
    )
    write_pipeline_artifact(artifact, paths)
    print(json.dumps(artifact.metadata["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
