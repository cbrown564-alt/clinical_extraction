"""Projection/render contracts for the Gan 2026 architecture reset."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = "gan2026_projection_render_v0"
PROJECTION_POLICY_ID = "gan2026_clinical_assessment_projection_v0"
RENDER_POLICY_ID = "gan2026_final_label_renderer_v0"

ProjectionKind = Literal[
    "frequency_rate",
    "cluster_frequency",
    "seizure_free",
    "unknown_frequency",
    "no_reference",
    "unresolved_multiple",
]


class ProjectionDecision(BaseModel):
    """Benchmark-policy projection from a normalized clinical assessment."""

    model_config = ConfigDict(extra="forbid")

    source_row_index: int
    component_owner: Literal["clinical_assessment_projection"]
    projection_policy_id: Literal["gan2026_clinical_assessment_projection_v0"] = (
        PROJECTION_POLICY_ID
    )
    projection_kind: ProjectionKind
    projection_basis: str
    projected_label_semantics: str
    source_assessment_kind: str
    source_aggregation_policy: str
    source_candidate_ids: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    projection_issues: list[str] = Field(default_factory=list)
    clinical_or_policy: Literal["benchmark_policy"] = "benchmark_policy"
    schema_version: Literal["gan2026_projection_render_v0"] = SCHEMA_VERSION


class FinalRenderedLabel(BaseModel):
    """Scorer-facing label rendering from a projection decision."""

    model_config = ConfigDict(extra="forbid")

    source_row_index: int
    component_owner: Literal["final_label_renderer"]
    render_policy_id: Literal["gan2026_final_label_renderer_v0"] = RENDER_POLICY_ID
    rendered_label: str | None
    render_basis: str
    render_issues: list[str] = Field(default_factory=list)
    scorer_facing: Literal[True] = True
    scoring_enabled: Literal[False] = False
    schema_version: Literal["gan2026_projection_render_v0"] = SCHEMA_VERSION
