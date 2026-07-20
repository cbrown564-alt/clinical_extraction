"""Lenient model-facing assessment draft contract for Gan 2026."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.clinical_assessment import (
    AggregationPolicy,
    AssessmentKind,
    NormalizedBurden,
)


class AssessmentDraftBurden(BaseModel):
    """Lenient model-facing burden draft.

    The final ClinicalAssessment still uses the strict NormalizedBurden contract.
    This draft only preserves the source-near phrase; deterministic assembly owns
    parsed values.
    """

    model_config = ConfigDict(extra="ignore")

    count_low: float | None = None
    count_high: float | None = None
    vague_count: str | None = None
    period_low: float | None = None
    period_high: float | None = None
    period_unit: str | None = None
    seizure_free_duration_low: float | None = None
    seizure_free_duration_high: float | None = None
    seizure_free_duration_unit: str | None = None
    cluster_count_low: float | None = None
    cluster_count_high: float | None = None
    cluster_period_low: float | None = None
    cluster_period_high: float | None = None
    cluster_period_unit: str | None = None
    events_per_cluster_low: float | None = None
    events_per_cluster_high: float | None = None
    source_normalized_phrase: str = ""

    @field_validator(
        "period_unit",
        "seizure_free_duration_unit",
        "cluster_period_unit",
        mode="before",
    )
    @classmethod
    def _normalise_unit(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        normalized = value.strip().lower().replace("_", " ")
        singular = {
            "days": "day",
            "weeks": "week",
            "months": "month",
            "years": "year",
        }.get(normalized, normalized)
        return singular if singular in {"day", "week", "month", "year"} else None


class AssessmentDraft(BaseModel):
    """Model-owned clinical assessment fields."""

    model_config = ConfigDict(extra="ignore")

    assessment_kind: AssessmentKind
    primary_candidate_ids: list[str]
    supporting_candidate_ids: list[str] = Field(default_factory=list)
    rejected_candidate_ids: list[str] = Field(default_factory=list)
    aggregation_policy: AggregationPolicy | None = None
    normalized_burden: AssessmentDraftBurden
    assessment_summary: str = ""
    uncertainty_flags: list[str] = Field(default_factory=list)

    @field_validator("normalized_burden", mode="before")
    @classmethod
    def _accept_final_burden_model(cls, value: object) -> object:
        if isinstance(value, NormalizedBurden):
            return value.model_dump()
        return value


__all__ = [
    "AssessmentDraft",
    "AssessmentDraftBurden",
]
