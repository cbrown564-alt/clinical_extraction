"""Merged clinical assessment contract for Gan 2026 candidate sets."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

SCHEMA_VERSION = "gan2026_clinical_assessment_v0"

AssessmentKind = Literal[
    "frequency_rate",
    "cluster_frequency",
    "seizure_free",
    "unknown_frequency",
    "no_reference",
    "unresolved_multiple",
]

AggregationPolicy = Literal[
    "single_fact",
    "additive_same_window",
    "primary_with_context",
    "cluster_axis",
    "seizure_free_state",
    "unknown_due_to_ambiguity",
    "unknown_due_to_absence",
    "no_reference_boundary",
]


class NormalizedBurden(BaseModel):
    """Source-backed clinical burden, before task-specific projection/rendering."""

    model_config = ConfigDict(extra="forbid")

    count_low: float | None = None
    count_high: float | None = None
    vague_count: Literal["multiple", "rare", "occasional", "frequent"] | None = None
    period_low: float | None = None
    period_high: float | None = None
    period_unit: Literal["day", "week", "month", "year"] | None = None
    seizure_free_duration_low: float | None = None
    seizure_free_duration_high: float | None = None
    seizure_free_duration_unit: Literal["day", "week", "month", "year"] | None = None
    cluster_count_low: float | None = None
    cluster_count_high: float | None = None
    cluster_period_low: float | None = None
    cluster_period_high: float | None = None
    cluster_period_unit: Literal["day", "week", "month", "year"] | None = None
    events_per_cluster_low: float | None = None
    events_per_cluster_high: float | None = None
    source_normalized_phrase: str = ""


class DateReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: str
    date_precision: Literal["day", "month"]
    source: str
    source_phrase: str = ""
    source_candidate_ids: list[str] = Field(default_factory=list)


class ComputedDuration(BaseModel):
    model_config = ConfigDict(extra="forbid")

    low: float
    high: float
    unit: Literal["month"]


class AntecedentReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_phrase: str
    anchor_date: DateReference
    link_type: Literal["local_since_then_antecedent"]
    source_candidate_ids: list[str] = Field(default_factory=list)


class SeizureFreeInstrumentation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    state_kind: Literal["since_date", "unresolved_anchor"]
    source_phrase: str
    anchor_date: DateReference | None = None
    antecedent: AntecedentReference | None = None
    reference_date: DateReference | None = None
    computed_duration: ComputedDuration | None = None
    source_candidate_ids: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    instrumentation_issues: list[str] = Field(default_factory=list)


class ClinicalAssessment(BaseModel):
    """LLM-owned clinical synthesis before deterministic project/render stages."""

    model_config = ConfigDict(extra="forbid")

    source_row_index: int
    component_owner: str
    assessment_kind: AssessmentKind
    primary_candidate_ids: list[str] = Field(default_factory=list)
    supporting_candidate_ids: list[str] = Field(default_factory=list)
    rejected_candidate_ids: list[str] = Field(default_factory=list)
    aggregation_policy: AggregationPolicy
    normalized_burden: NormalizedBurden
    seizure_free_instrumentation: SeizureFreeInstrumentation | None = None
    normalization_policy_id: str = "gan2026_clinical_assessment_normalization_v0"
    normalization_issues: list[str] = Field(default_factory=list)
    assessment_summary: str = ""
    uncertainty_flags: list[str] = Field(default_factory=list)
    schema_version: Literal["gan2026_clinical_assessment_v0"] = SCHEMA_VERSION

    @model_validator(mode="after")
    def validate_candidate_id_roles(self) -> ClinicalAssessment:
        role_lists = [
            self.primary_candidate_ids,
            self.supporting_candidate_ids,
            self.rejected_candidate_ids,
        ]
        for candidate_ids in role_lists:
            if len(candidate_ids) != len(set(candidate_ids)):
                raise ValueError("candidate ids must be unique within each role")
        primary = set(self.primary_candidate_ids)
        supporting = set(self.supporting_candidate_ids)
        rejected = set(self.rejected_candidate_ids)
        if primary & supporting:
            raise ValueError("primary_candidate_ids and supporting_candidate_ids overlap")
        if primary & rejected:
            raise ValueError("primary_candidate_ids and rejected_candidate_ids overlap")
        if supporting & rejected:
            raise ValueError("supporting_candidate_ids and rejected_candidate_ids overlap")
        if self.assessment_kind in {
            "frequency_rate",
            "cluster_frequency",
            "seizure_free",
        } and not self.primary_candidate_ids:
            raise ValueError(f"{self.assessment_kind} requires primary_candidate_ids")
        return self


def referenced_candidate_ids(assessment: ClinicalAssessment) -> set[str]:
    """Return every candidate id named by a clinical assessment."""

    return {
        *assessment.primary_candidate_ids,
        *assessment.supporting_candidate_ids,
        *assessment.rejected_candidate_ids,
    }
