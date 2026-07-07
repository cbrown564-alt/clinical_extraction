"""Gold audit worklist routes for the Observatory."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Query, Request

from clinical_extraction.observatory.gan2026.gold_audit_sampler import (
    enrich_rows_for_active_sampling,
)
from clinical_extraction.observatory.gan2026.gold_audit_store import (
    load_gold_audit_decisions,
    load_gold_audit_rows,
    rq10_class_counts,
    upsert_gold_audit_decision,
)
from clinical_extraction.observatory.models import GoldAuditDecision, ObservatorySettings
from clinical_extraction.observatory.responses import (
    GoldAuditDecideResponse,
    GoldAuditDecisionsResponse,
    GoldAuditNextResponse,
    GoldAuditRowsResponse,
)

router = APIRouter(tags=["gold-audit"])


def _settings(request: Request) -> ObservatorySettings:
    return request.app.state.observatory_settings


def _compute_next_row(
    rows: Sequence[Mapping[str, Any]], decisions: Sequence[Mapping[str, Any]]
) -> dict[str, Any] | None:
    enriched, _model_summary = enrich_rows_for_active_sampling(rows, decisions)
    candidates = [
        (float(row["active_learning_score"]), row) for row in enriched if not row["has_decision"]
    ]

    if not candidates:
        return None
    candidates.sort(key=lambda item: item[0], reverse=True)
    return dict(candidates[0][1])


@router.get("/gold-audit/rows", response_model=GoldAuditRowsResponse)
def gold_audit_rows(
    request: Request,
    split: str = Query(default="validation"),
) -> GoldAuditRowsResponse:
    settings = _settings(request)
    rows = load_gold_audit_rows(settings, split=split)
    decisions = load_gold_audit_decisions(settings)
    enriched, model_summary = enrich_rows_for_active_sampling(rows, decisions)
    for row in enriched:
        row["priority_score"] = row["active_learning_score"]
    return GoldAuditRowsResponse(
        split=split,
        total=len(rows),
        decided=sum(1 for row in enriched if row["has_decision"]),
        class_counts=rq10_class_counts(decisions),
        sampling_model=model_summary,
        rows=enriched,
    )


@router.get("/gold-audit/decisions", response_model=GoldAuditDecisionsResponse)
def gold_audit_decisions(
    request: Request,
    split: str | None = Query(default=None),
) -> GoldAuditDecisionsResponse:
    settings = _settings(request)
    all_decisions = load_gold_audit_decisions(settings)
    if split is not None:
        all_decisions = [decision for decision in all_decisions if decision.get("split") == split]
    validated = [GoldAuditDecision.model_validate(decision) for decision in all_decisions]
    return GoldAuditDecisionsResponse(decisions=validated, count=len(validated))


@router.post("/gold-audit/decide", response_model=GoldAuditDecideResponse)
def gold_audit_decide(decision: GoldAuditDecision, request: Request) -> GoldAuditDecideResponse:
    settings = _settings(request)
    payload = decision.model_dump(mode="json")
    if not payload.get("timestamp"):
        payload["timestamp"] = datetime.now(UTC).isoformat()
    saved = upsert_gold_audit_decision(settings, payload)
    return GoldAuditDecideResponse(status="saved", decision=saved)


@router.get("/gold-audit/next", response_model=GoldAuditNextResponse)
def gold_audit_next(
    request: Request,
    split: str = Query(default="validation"),
) -> GoldAuditNextResponse:
    settings = _settings(request)
    rows = load_gold_audit_rows(settings, split=split)
    decisions = load_gold_audit_decisions(settings)
    next_row = _compute_next_row(rows, decisions)
    if next_row is None:
        return GoldAuditNextResponse(
            split=split,
            row=None,
            message="All rows have been audited.",
        )
    return GoldAuditNextResponse(split=split, row=next_row)
