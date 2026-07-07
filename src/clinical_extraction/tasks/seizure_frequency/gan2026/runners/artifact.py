"""Unified pipeline artifact composition for Gan 2026 runners."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.pipeline.stages import (
    clinical_assessment_projection_render as projection_render,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.pipeline.stages import (
    clinical_assessment_projection_score as projection_score,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.pipeline.stages import (
    clinical_assessment_verification_decision as verification_decision,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.pipeline.stages import (
    clinical_assessment_verification_route as verification_route,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.config import (
    PipelineArchitecture,
    PipelineOutputArtifact,
)


def build_unified_pipeline_artifact(
    *,
    architecture: PipelineArchitecture,
    assessment_rows: Sequence[Mapping[str, object]],
    candidate_sets: Mapping[int, CandidateSet],
    gold_records: Mapping[int, GanFrequencyRecord],
    assessment_artifact_path: str = "in_memory",
    candidate_set_artifact_path: str = "in_memory",
    disabled_ablation_switches: set[str] | frozenset[str] | None = None,
    project_render_artifact_path: str | None = None,
    score_artifact_path: str | None = None,
    route_artifact_path: str | None = None,
) -> PipelineOutputArtifact:
    """Build unified pipeline artifacts using deterministic downstream stages."""
    projection_render_rows, projection_render_metadata = (
        projection_render.build_projection_render_artifact(
            assessment_rows,
            candidate_sets=candidate_sets,
            assessment_artifact_path=assessment_artifact_path,
            candidate_set_artifact_path=candidate_set_artifact_path,
            disabled_ablation_switches=disabled_ablation_switches,
        )
    )
    score_rows, score_metadata = projection_score.build_scoring_artifact(
        projection_render_rows,
        gold_records=gold_records,
        project_render_artifact_path=project_render_artifact_path or "in_memory",
    )
    route_rows, route_metadata = verification_route.build_verification_route_artifact(
        score_rows,
        score_artifact_path=score_artifact_path or "in_memory",
    )
    decision_rows, decision_metadata = verification_decision.build_verification_decision_artifact(
        route_rows,
        route_artifact_path=route_artifact_path or "in_memory",
    )

    projection_summary = dict(projection_render_metadata.get("summary") or {})
    score_summary = dict(score_metadata.get("summary") or {})
    route_summary = dict(route_metadata.get("summary") or {})
    decision_summary = dict(decision_metadata.get("summary") or {})

    metadata = {
        "artifact_kind": f"gan2026_{architecture}_pipeline",
        "pipeline_family": f"{architecture}_pipeline",
        "pipeline_version": f"gan2026_{architecture}_pipeline_v0",
        "claim_boundary": (
            "validation-development unified composition; no model calls, no "
            "locked-test inspection, and score context remains audit-only"
        ),
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
            "null_rendered_label_rows": int(projection_summary.get("null_rendered_label_rows", 0)),
            "scored_rows": int(score_summary.get("scored_rows", 0)),
            "purist_correct": int(score_summary.get("purist_correct", 0)),
            "routed_rows": int(route_summary.get("routed_rows", 0)),
            "decision_rows": int(decision_summary.get("decision_rows", 0)),
            "action_counts": dict(decision_summary.get("action_counts") or {}),
        },
    }

    return PipelineOutputArtifact(
        projection_render_rows=list(projection_render_rows),
        score_rows=list(score_rows),
        route_rows=list(route_rows),
        decision_rows=list(decision_rows),
        metadata=metadata,
    )
