"""Compatibility API for the Next.js clinical explorer."""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, Query
from pydantic import BaseModel, ConfigDict, Field

from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rule_metadata import (
    AblationConfig,
    Portability,
    RuleGroup,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.config import (
    PipelineConfiguration,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.deterministic_canonical import (
    run_item,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.naming import active_pipeline_name
from clinical_extraction.trace_explorer.api.dependencies import (
    FrontendDataDependency,
    ReviewStoreDependency,
    TraceIndexDependency,
)
from clinical_extraction.trace_explorer.api.errors import (
    TraceExplorerError,
    aggregate_only,
    not_found,
)

router = APIRouter(tags=["frontend-compatibility"])

DatasetId = Literal["gan2026", "exectv2"]


class AblationPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled_groups: list[str] | None = None
    enabled_portability: list[str] | None = None
    disabled_rule_ids: list[str] = Field(default_factory=list)


class RunNoteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    note_text: str = Field(min_length=1, max_length=2_000_000)
    pipeline: str = "rules"
    source_row_index: int = 0
    gold_label: str | None = None
    gold_reference: str | None = None
    ablation_config: AblationPayload = Field(default_factory=AblationPayload)


class SemanticSupportReviewDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    review_item_id: str = Field(min_length=1, max_length=1000)
    reviewer_id: str = Field(min_length=1, max_length=120)
    clinical_support: Literal["supported", "unsupported", "unclear"]
    review_notes: str | None = Field(default=None, max_length=10_000)


_SEMANTIC_SUPPORT_ALLOWED_VALUES = {
    "clinical_support": ["supported", "unsupported", "unclear"],
}


class GoldAuditDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset: DatasetId = "gan2026"
    audit_id: str | None = None
    source_row_index: int | None = None
    split: str
    simple_class: str | None = None
    rq10_class: str | None = None
    notes: str | None = None
    corrected_gold_label: str | None = None
    benchmark_convention_flag: bool | None = None
    all_system_fail: bool | None = None
    exact_evidence_but_scorer_wrong: bool | None = None
    clinically_defensible_alternative: bool | None = None
    likely_gold_defect: bool | None = None
    assertion_status: str | None = None
    attribute_entailment: str | None = None
    fact_boundaries: str | None = None
    clinical_interpretation: str | None = None
    reviewer_rationale: str | None = None
    review_confidence: str | None = None
    timestamp: str | None = None
    auditor: str | None = None


@router.get("/health")
def health(index: TraceIndexDependency) -> dict[str, object]:
    return {"status": "ok", "index_ready": index.ready}


@router.get("/registry")
def registry(data: FrontendDataDependency) -> dict[str, Any]:
    return data.named("registry")


@router.get("/pipeline-families")
def pipeline_families(data: FrontendDataDependency) -> dict[str, Any]:
    return data.named("pipeline_families")


@router.get("/datasets/{dataset}/letters")
def dataset_letters(dataset: DatasetId, data: FrontendDataDependency) -> dict[str, Any]:
    return data.letters(dataset)


@router.get("/datasets/{dataset}/letters/{letter_id}")
def dataset_letter(
    dataset: DatasetId,
    letter_id: str,
    data: FrontendDataDependency,
) -> dict[str, Any]:
    if data.is_locked_letter(dataset, letter_id):
        raise aggregate_only()
    payload = data.letter(dataset, letter_id)
    if payload is None:
        raise not_found()
    return payload


@router.get("/datasets/{dataset}/runs")
def dataset_runs(dataset: DatasetId, data: FrontendDataDependency) -> dict[str, Any]:
    return data.runs(dataset)


@router.get("/datasets/{dataset}/runs/{run_id}")
def dataset_run(
    dataset: DatasetId,
    run_id: str,
    data: FrontendDataDependency,
) -> dict[str, Any]:
    payload = data.run(dataset, run_id)
    if payload is None:
        raise not_found()
    return payload


@router.get("/records/{split}")
def records(split: str, data: FrontendDataDependency) -> dict[str, Any]:
    _check_record_split(split)
    payload = data.records(split)
    if payload is None:
        raise not_found()
    return payload


@router.get("/records/{split}/{source_row_index}")
def record(split: str, source_row_index: int, data: FrontendDataDependency) -> dict[str, Any]:
    _check_record_split(split)
    if data.is_locked_letter("gan2026", str(source_row_index)):
        raise aggregate_only()
    payload = data.record(split, source_row_index)
    if payload is None:
        raise not_found()
    return payload


@router.get("/artifacts/{run_id}")
def artifact(
    run_id: str,
    data: FrontendDataDependency,
    artifact_path: str | None = None,
    limit: int | None = Query(default=None, ge=1, le=1000),
    letter_id: str | None = Query(default=None),
) -> dict[str, Any]:
    del artifact_path
    if letter_id is not None and data.is_locked_letter_id(letter_id):
        raise aggregate_only()
    payload = data.artifact(run_id, limit=limit, letter_id=letter_id)
    if payload is None:
        raise not_found()
    return payload


@router.post("/run/note")
def run_note(request: RunNoteRequest) -> dict[str, Any]:
    try:
        canonical_pipeline = active_pipeline_name(request.pipeline)
    except ValueError:
        raise TraceExplorerError(
            status_code=400,
            code="model_calls_disabled",
            message="Model-backed execution is disabled; inspect an indexed saved replay instead.",
        ) from None
    if canonical_pipeline != "rules":
        raise TraceExplorerError(
            status_code=400,
            code="model_calls_disabled",
            message="Model-backed execution is disabled; inspect an indexed saved replay instead.",
        ) from None
    result = run_item(_gan_record(request), _pipeline_configuration(request.ablation_config))
    return {
        "pipeline": canonical_pipeline,
        "source_row_index": request.source_row_index,
        "gold_label": request.gold_label or "unknown",
        "result": result.model_dump(mode="json"),
    }


@router.get("/exectv2/runs")
def exectv2_runs(data: FrontendDataDependency) -> dict[str, Any]:
    return data.exectv2_catalog()


@router.get("/exectv2/runs/{run_id}")
def exectv2_run(run_id: str, data: FrontendDataDependency) -> dict[str, Any]:
    payload = data.exectv2_run(run_id)
    if payload is None:
        raise not_found()
    return payload


@router.get("/semantic-support-review/packets")
def semantic_support_review_packets(
    data: FrontendDataDependency,
    reviews: ReviewStoreDependency,
    reviewer_id: str | None = Query(default=None, min_length=1, max_length=120),
) -> dict[str, Any]:
    payload = data.semantic_support_review_packets()
    decisions = (
        reviews.list(_semantic_support_review_kind(reviewer_id)) if reviewer_id else []
    )
    decided_ids = {str(item["review_item_id"]) for item in decisions}
    packets = payload["packets"]
    for packet in packets:
        packet["has_decision"] = str(packet["review_item_id"]) in decided_ids
    return {
        **payload,
        "protocol_version": "exectv2-semantic-support-review-v2",
        "blinded": True,
        "reviewer_id": reviewer_id,
        "total": len(packets),
        "decided": len(decided_ids),
        "allowed_values": _SEMANTIC_SUPPORT_ALLOWED_VALUES,
    }


@router.get("/semantic-support-review/decisions")
def semantic_support_review_decisions(
    reviews: ReviewStoreDependency,
    reviewer_id: str = Query(min_length=1, max_length=120),
) -> dict[str, Any]:
    decisions = reviews.list(_semantic_support_review_kind(reviewer_id))
    return {
        "reviewer_id": reviewer_id,
        "decisions": decisions,
        "count": len(decisions),
        "blinded": True,
    }


@router.post("/semantic-support-review/decide")
def semantic_support_review_decide(
    decision: SemanticSupportReviewDecision,
    data: FrontendDataDependency,
    reviews: ReviewStoreDependency,
) -> dict[str, Any]:
    if decision.review_item_id not in data.semantic_support_review_ids():
        raise not_found()
    saved = reviews.save_revisioned(
        _semantic_support_review_kind(decision.reviewer_id),
        decision.review_item_id,
        decision.model_dump(mode="json", exclude_none=True),
    )
    return {"status": "saved", "decision": saved}


@router.get("/semantic-support-review/export")
def semantic_support_review_export(
    data: FrontendDataDependency,
    reviews: ReviewStoreDependency,
    reviewer_id: str = Query(min_length=1, max_length=120),
) -> dict[str, Any]:
    review_kind = _semantic_support_review_kind(reviewer_id)
    decisions = reviews.list(review_kind)
    revisions = reviews.revisions(review_kind)
    source = data.semantic_support_review_packets()
    return {
        "schema_version": "exectv2-semantic-support-review-export-v2",
        "protocol_version": "exectv2-semantic-support-review-v2",
        "reviewer_id": reviewer_id,
        "claim_boundary": source["claim_boundary"],
        "completion": {"decided": len(decisions), "total": len(source["packets"])},
        "decisions": decisions,
        "revisions": revisions,
    }


@router.get("/gold-audit/rows")
def gold_audit_rows(
    data: FrontendDataDependency,
    reviews: ReviewStoreDependency,
    split: str = "dev750",
    dataset: DatasetId = "gan2026",
) -> dict[str, Any]:
    del split
    payload = data.gold_audit_rows(dataset)
    decisions = _gold_decisions(data, reviews, dataset)
    decided_ids = {_gold_decision_identity(item) for item in decisions}
    rows = payload.get("rows")
    if isinstance(rows, list):
        for row in rows:
            if isinstance(row, dict):
                row["has_decision"] = bool(row.get("has_decision")) or _gold_row_identity(
                    row
                ) in decided_ids
        payload["decided"] = sum(bool(row.get("has_decision")) for row in rows)
    return payload


@router.get("/gold-audit/decisions")
def gold_audit_decisions(
    data: FrontendDataDependency,
    reviews: ReviewStoreDependency,
    split: str | None = None,
    dataset: DatasetId = "gan2026",
) -> dict[str, Any]:
    del split
    decisions = _gold_decisions(data, reviews, dataset)
    return {"dataset": dataset, "decisions": decisions, "count": len(decisions)}


@router.post("/gold-audit/decide")
def gold_audit_decide(
    decision: GoldAuditDecision,
    data: FrontendDataDependency,
    reviews: ReviewStoreDependency,
) -> dict[str, Any]:
    if decision.split in {"test", "test450", "test60"}:
        raise aggregate_only()
    payload = decision.model_dump(mode="json", exclude_none=True)
    identity = _gold_decision_identity(payload)
    if identity not in data.gold_audit_ids(decision.dataset):
        raise not_found()
    saved = reviews.save(f"gold:{decision.dataset}", identity, payload)
    return {"status": "saved", "decision": saved}


def _check_record_split(split: str) -> None:
    if split in {"test", "test450", "test60", "holdout", "full200", "full-200"}:
        raise aggregate_only()
    if split not in {"validation", "validation750", "dev750"}:
        raise not_found()


def _pipeline_configuration(payload: AblationPayload) -> PipelineConfiguration:
    enabled_groups = (
        frozenset(RuleGroup(value) for value in payload.enabled_groups)
        if payload.enabled_groups is not None
        else frozenset(RuleGroup)
    )
    enabled_portability = (
        frozenset(Portability(value) for value in payload.enabled_portability)
        if payload.enabled_portability is not None
        else frozenset(Portability)
    )
    return PipelineConfiguration(
        architecture="rules",
        ablation_config=AblationConfig(
            enabled_groups=enabled_groups,
            enabled_portability=enabled_portability,
            disabled_rule_ids=frozenset(payload.disabled_rule_ids),
        ),
    )


def _gan_record(request: RunNoteRequest) -> GanRecord:
    return GanRecord(
        source_row_index=request.source_row_index,
        note_text=request.note_text,
        gold_label=request.gold_label or "unknown",
        gold_reference=request.gold_reference or "",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
    )


def _merge_decisions(
    seed: list[dict[str, Any]],
    local: list[dict[str, Any]],
    identity,
) -> list[dict[str, Any]]:
    merged = {identity(item): item for item in seed}
    merged.update({identity(item): item for item in local})
    return list(merged.values())


def _semantic_support_review_kind(reviewer_id: str) -> str:
    return f"semantic-support:{reviewer_id.strip()}"


def _gold_decisions(
    data: FrontendDataDependency,
    reviews: ReviewStoreDependency,
    dataset: DatasetId,
) -> list[dict[str, Any]]:
    seed = data.gold_audit_decisions(dataset).get("decisions")
    return _merge_decisions(
        seed if isinstance(seed, list) else [],
        reviews.list(f"gold:{dataset}"),
        _gold_decision_identity,
    )


def _gold_decision_identity(decision: dict[str, Any]) -> str:
    return str(decision.get("audit_id") or decision.get("source_row_index") or "missing")


def _gold_row_identity(row: dict[str, Any]) -> str:
    return str(row.get("audit_id") or row.get("source_row_index") or "missing")
