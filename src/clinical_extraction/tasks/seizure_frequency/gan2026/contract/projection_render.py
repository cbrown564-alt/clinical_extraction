"""Projection/render contracts for the Gan 2026 architecture reset."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = "gan2026_projection_render_v1"
PROJECTION_POLICY_ID = "gan2026_clinical_assessment_projection_owner_split_v1"
RENDER_POLICY_ID = "gan2026_projection_owner_aware_label_render_v1"
SCORING_SCHEMA_VERSION = "gan2026_rendered_label_scoring_v0"
SCORING_POLICY_ID = "gan2026_rendered_label_scoring_policy_v0"

ProjectionKind = Literal[
    "frequency_rate",
    "cluster_frequency",
    "seizure_free",
    "unknown_frequency",
    "no_reference",
    "unresolved_multiple",
]

ProjectionOwner = Literal[
    "rate_projection_policy",
    "cluster_projection_policy",
    "boundary_projection_policy",
    "benchmark_renderer",
]


class ProjectionDecision(BaseModel):
    """Benchmark-policy projection from a normalized clinical assessment."""

    model_config = ConfigDict(extra="forbid")

    source_row_index: int
    component_owner: ProjectionOwner
    projection_policy_id: str = PROJECTION_POLICY_ID
    projection_owner: ProjectionOwner
    projection_rule_id: str
    projection_kind: ProjectionKind
    projection_basis: str
    projected_label_semantics: str
    source_assessment_kind: str
    source_aggregation_policy: str
    source_candidate_ids: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    projection_issues: list[str] = Field(default_factory=list)
    clinical_or_policy: Literal["benchmark_policy"] = "benchmark_policy"
    schema_version: Literal["gan2026_projection_render_v1"] = SCHEMA_VERSION


class FinalRenderedLabel(BaseModel):
    """Scorer-facing label rendering from a projection decision."""

    model_config = ConfigDict(extra="forbid")

    source_row_index: int
    component_owner: ProjectionOwner
    render_policy_id: str = RENDER_POLICY_ID
    projection_owner: ProjectionOwner
    projection_rule_id: str
    rendered_label: str | None
    render_basis: str
    render_issues: list[str] = Field(default_factory=list)
    scorer_facing: Literal[True] = True
    scoring_enabled: Literal[False] = False
    schema_version: Literal["gan2026_projection_render_v1"] = SCHEMA_VERSION


ScoreStatus = Literal[
    "scored",
    "not_scored_null_rendered_label",
    "not_scored_unparseable_rendered_label",
    "not_scored_missing_gold_record",
]


class RenderedLabelScore(BaseModel):
    """Score-policy result for a scorer-facing rendered label."""

    model_config = ConfigDict(extra="forbid")

    source_row_index: int
    component_owner: Literal["rendered_label_scorer"]
    scoring_policy_id: Literal["gan2026_rendered_label_scoring_policy_v0"] = (
        SCORING_POLICY_ID
    )
    score_status: ScoreStatus
    rendered_label: str | None
    gold_label: str | None
    predicted_normalized_label: str | None = None
    gold_normalized_label: str | None = None
    predicted_monthly_frequency: float | None = None
    gold_monthly_frequency: float | None = None
    predicted_purist_category: str | None = None
    gold_purist_category: str | None = None
    predicted_pragmatic_category: str | None = None
    gold_pragmatic_category: str | None = None
    exact_normalized_label_match: bool | None = None
    purist_correct: bool | None = None
    pragmatic_correct: bool | None = None
    score_issues: list[str] = Field(default_factory=list)
    clinical_or_policy: Literal["score_policy"] = "score_policy"
    schema_version: Literal["gan2026_rendered_label_scoring_v0"] = SCORING_SCHEMA_VERSION
