"""Pydantic models for clinical-findings pipeline I/O."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ClinicalFindingRecord(BaseModel):
    """One source-near seizure frequency finding emitted by the model."""

    model_config = ConfigDict(extra="ignore")

    text: str
    evidence: str
    clinical_kind: Literal[
        "frequency_rate",
        "seizure_free",
        "frequency_change",
        "dated_count",
        "last_event",
        "cluster_frequency",
        "other_frequency",
    ]
    frequency_statement_type: Literal[
        "header_count_since_anchor",
        "calendar_count",
        "calendar_occurrence_no_count",
        "recurrence_interval",
        "last_event_date",
        "background_rate",
        "seizure_free_duration",
        "current_control_no_duration",
        "current_zero_no_duration",
        "change_only",
        "other_frequency",
    ] = "other_frequency"
    source_role: Literal["compact_section", "narrative", "both"] = "narrative"
    count: str | None = None
    count_low: str | None = None
    count_high: str | None = None
    period_count: str | None = None
    period_low: str | None = None
    period_high: str | None = None
    period_unit: str | None = None
    time_relation: str | None = None
    point_in_time: str | None = None
    day: str | None = None
    month: str | None = None
    year: str | None = None
    age_low: str | None = None
    age_high: str | None = None
    age_unit: str | None = None
    frequency_change: str | None = None
    confidence: Literal["low", "medium", "high"] = "medium"
    rationale: str = ""


class FindingFamilyChecklist(BaseModel):
    """Model-owned note-level seizure-frequency family checklist."""

    model_config = ConfigDict(extra="ignore")

    has_compact_section: bool = False
    has_current_rate: bool = False
    has_dated_count: bool = False
    has_last_event: bool = False
    has_zero_status: bool = False
    has_frequency_change: bool = False
    has_cluster: bool = False
    has_non_target_episode: bool = False
    checklist_rationale: str = ""


class EventFrameRecord(BaseModel):
    """One model-owned clinical event frame used before ExECT projection."""

    model_config = ConfigDict(extra="ignore")

    event_id: str = ""
    evidence: str
    seizure_phrase: str
    target_status: Literal[
        "target_epileptic_seizure_frequency",
        "non_target_episode",
        "history_context_only",
        "diagnosis_without_frequency",
        "future_risk_or_driving",
        "uncertain_not_scored",
    ] = "target_epileptic_seizure_frequency"
    statement_family: str = "other_frequency"
    source_role: Literal["compact_section", "narrative", "both"] = "narrative"
    count: str | None = None
    count_low: str | None = None
    count_high: str | None = None
    period_count: str | None = None
    period_low: str | None = None
    period_high: str | None = None
    period_unit: str | None = None
    time_relation: str | None = None
    point_in_time: str | None = None
    day: str | None = None
    month: str | None = None
    year: str | None = None
    age_low: str | None = None
    age_high: str | None = None
    age_unit: str | None = None
    frequency_change: str | None = None
    finding_text: str | None = None
    include_as_finding: bool = True
    rationale: str = ""


class ClinicalFindingsRecord(BaseModel):
    """Full model output for one letter."""

    model_config = ConfigDict(extra="ignore")

    family_checklist: FindingFamilyChecklist = Field(default_factory=FindingFamilyChecklist)
    event_frames: list[EventFrameRecord] = Field(default_factory=list)
    findings: list[ClinicalFindingRecord] = Field(default_factory=list)


class VerificationDecisionRecord(BaseModel):
    """One model-owned decision about a raw finding."""

    model_config = ConfigDict(extra="ignore")

    raw_index: int
    action: Literal["keep", "remove", "revise"] = "keep"
    target_status: Literal[
        "target_epileptic_seizure_frequency",
        "non_target_episode",
        "history_context_only",
        "diagnosis_without_frequency",
        "future_risk_or_driving",
        "uncertain_not_scored",
    ] = "target_epileptic_seizure_frequency"
    text: str | None = None
    evidence: str | None = None
    clinical_kind: str | None = None
    frequency_statement_type: str | None = None
    source_role: str | None = None
    count: str | None = None
    count_low: str | None = None
    count_high: str | None = None
    period_count: str | None = None
    period_low: str | None = None
    period_high: str | None = None
    period_unit: str | None = None
    time_relation: str | None = None
    point_in_time: str | None = None
    day: str | None = None
    month: str | None = None
    year: str | None = None
    age_low: str | None = None
    age_high: str | None = None
    age_unit: str | None = None
    frequency_change: str | None = None
    rationale: str = ""


class VerificationDecisionList(BaseModel):
    """Model-owned final-selection decisions for one letter."""

    model_config = ConfigDict(extra="ignore")

    decisions: list[VerificationDecisionRecord] = Field(default_factory=list)
    findings_to_add: list[ClinicalFindingRecord] = Field(default_factory=list)
