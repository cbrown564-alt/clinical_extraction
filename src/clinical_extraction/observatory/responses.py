"""Pydantic response models for high-traffic Observatory routes."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from clinical_extraction.observatory.models import GoldAuditDecision, PipelineFamily

# ── Meta ──


class HealthResponse(BaseModel):
    status: Literal["ok"]


class MetaResponse(BaseModel):
    git: dict[str, Any]
    observatory_version: str
    timestamp: str


# ── Registry & artifacts ──


class RegistryResponse(BaseModel):
    registry_path: str
    runs: list[dict[str, Any]]


class ArtifactResponse(BaseModel):
    run_id: str
    artifact_paths: list[str]
    artifact_type: str
    content: list[Any]
    note: str | None = None


class SplitResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    split_name: str
    manifest_path: str
    split_manifest: str


class PipelineFamiliesResponse(BaseModel):
    families: list[dict[str, Any]]


# ── Gold audit ──


class GoldAuditRowsResponse(BaseModel):
    split: str
    total: int
    decided: int
    class_counts: dict[str, int]
    sampling_model: dict[str, Any]
    rows: list[dict[str, Any]]


class GoldAuditDecisionsResponse(BaseModel):
    decisions: list[GoldAuditDecision]
    count: int


class GoldAuditDecideResponse(BaseModel):
    status: Literal["saved"]
    decision: GoldAuditDecision


class GoldAuditNextResponse(BaseModel):
    split: str
    row: dict[str, Any] | None = None
    message: str | None = None


# ── Gan execution & catalog ──


class RunNoteResponse(BaseModel):
    pipeline: PipelineFamily
    source_row_index: int
    gold_label: str
    result: dict[str, Any]


class RunAblationSummary(BaseModel):
    total: int
    purist: dict[str, Any]
    pragmatic: dict[str, Any]


class RunAblationResponse(BaseModel):
    split: str
    pipeline: PipelineFamily
    row_count: int
    ablation_config: dict[str, Any]
    summary: RunAblationSummary
    rows: list[dict[str, Any]]


class RulesResponse(BaseModel):
    groups: list[str]
    portability: list[str]
    rules: list[dict[str, Any]]


class PromptsResponse(BaseModel):
    prompts: list[dict[str, Any]]


class RecordPreview(BaseModel):
    source_row_index: int
    gold_label: str
    gold_reference: str
    row_ok: bool
    note_preview: str


class RecordsListResponse(BaseModel):
    split: str
    count: int
    records: list[RecordPreview]


class RecordDetailResponse(BaseModel):
    split: str
    source_row_index: int
    gold_label: str
    gold_reference: str
    row_ok: bool
    note_text: str
    labels_match_all_categories: bool
    quotes_ok_all_categories: bool


class TagErrorResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    error_type: str
    severity: int
    severity_level: str


class HardSliceDefinitionsResponse(BaseModel):
    slices: list[dict[str, Any]]


class HardSliceMembershipRow(BaseModel):
    source_row_index: Any = None
    hidden_families: list[str]


class HardSliceMembershipResponse(BaseModel):
    rows: list[HardSliceMembershipRow]
