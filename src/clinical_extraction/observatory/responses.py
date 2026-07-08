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


# ── Gold noise (read-only gold-quality inspection) ──
#
# Mirrors the gold-audit block but is read-only: the ledgers are produced by
# the offline canonical adjudicators, not by this surface. Payloads are kept
# permissive (``dict[str, Any]``) so the API does not couple to the full
# ``GoldCaseRow`` schema, which lives in the un-installed ``exectv2_ledger``
# script namespace under ``experiments/``.


class GoldNoiseLedgersResponse(BaseModel):
    families: list[dict[str, Any]]


class GoldNoiseRowResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    # A single normalized ``GoldNoiseItem``. Kept permissive (extra allowed)
    # because the shape is the unified adapter output, not a fixed enum.
    family: str
    letter_id: str
    row_id: str
    disagreement_type: str
    match_key: str
    mechanism: str
    verdict: str
    gold: dict[str, Any] | None = None
    pred: dict[str, Any] | None = None
    reason: str = ""
    run_id: str = ""
    source: str


class GoldNoiseGanAuditResponse(BaseModel):
    audit: dict[str, Any] | None
    taxonomy: str
    taxonomy_note: str


class GoldNoiseIssuesResponse(BaseModel):
    count: int
    issues: list[dict[str, Any]]


class GoldNoiseHypothesesResponse(BaseModel):
    count: int
    by_family: dict[str, list[dict[str, Any]]]
    entries: list[dict[str, Any]]


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


# ── SeizureFrequency inspection ──
#
# Read-only gold-vs-prediction inspection for the SF entity. Like the
# gold-noise block, inner payloads are permissive (``dict[str, Any]``) so the API
# does not couple to the scorer-internal key/attribute shapes, which live in the
# ``exectv2.scoring`` and ``exectv2.sf_inspection`` modules.


class SfInspectionResponse(BaseModel):
    generated_on: str
    split: str
    artifact: str
    n_letters: int
    n_with_errors: int
    scorecard: dict[str, Any]
    components: list[dict[str, Any]]
    letters: list[dict[str, Any]]
