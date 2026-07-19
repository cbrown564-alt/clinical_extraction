from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel, ConfigDict

from clinical_extraction.trace_explorer.api.dependencies import TraceIndexDependency
from clinical_extraction.trace_explorer.api.errors import aggregate_only, not_found
from clinical_extraction.trace_explorer.api.routes_catalog import _decode_cursor, _encode_cursor
from clinical_extraction.trace_explorer.contracts import StageCategory, TraceEnvelope
from clinical_extraction.trace_explorer.index import TraceIndex
from clinical_extraction.trace_explorer.policy import RowPolicy
from clinical_extraction.trace_explorer.projector import align_traces, derive_graph, derive_ledger

router = APIRouter(prefix="/api/v1", tags=["traces"])


def _inspectable_run(index: TraceIndex, run_id: str) -> dict[str, Any]:
    run = index.get_run(run_id)
    if run is None:
        raise not_found()
    policy = RowPolicy(run["row_policy"])
    if policy is RowPolicy.AGGREGATE_ONLY:
        raise aggregate_only()
    if not policy.permits_records:
        raise not_found()
    return run


@router.get("/runs/{run_id}/records")
def records(
    run_id: str,
    index: TraceIndexDependency,
    cursor: str | None = None,
    limit: int = Query(default=100, ge=1, le=100),
) -> dict[str, object]:
    _inspectable_run(index, run_id)
    after = _decode_cursor(cursor)
    items = index.list_records(run_id, after=after, limit=limit + 1)
    page = items[:limit]
    next_cursor = _encode_cursor(page[-1]["source_id"]) if len(items) > limit and page else None
    return {"schema_version": "trace.v1", "items": page, "next_cursor": next_cursor}


def _trace(index: TraceIndex, run_id: str, source_id: str):
    _inspectable_run(index, run_id)
    trace = index.get_trace(run_id=run_id, source_id=source_id)
    if trace is None:
        raise not_found()
    return trace


@router.get("/runs/{run_id}/records/{source_id}/trace")
def trace_detail(
    run_id: str,
    source_id: str,
    index: TraceIndexDependency,
) -> TraceEnvelope:
    return _trace(index, run_id, source_id)


@router.get("/runs/{run_id}/records/{source_id}/stages/{stage_id}")
def stage_detail(
    run_id: str,
    source_id: str,
    stage_id: str,
    index: TraceIndexDependency,
) -> dict[str, object]:
    trace = _trace(index, run_id, source_id)
    stage = next((item for item in trace.stages if item.stage_id == stage_id), None)
    if stage is None:
        raise not_found()
    return {
        "schema_version": "trace.v1",
        "trace_id": trace.trace_id,
        "stage": stage.model_dump(mode="json"),
    }


@router.get("/runs/{run_id}/records/{source_id}/ledger")
def ledger(
    run_id: str,
    source_id: str,
    index: TraceIndexDependency,
    category: StageCategory | None = None,
    owner: str | None = None,
    status: str | None = None,
    change_type: str | None = None,
    evidence_grade: str | None = None,
    entity: str | None = None,
    text: str | None = None,
) -> dict[str, object]:
    trace = _trace(index, run_id, source_id)
    rows = derive_ledger(trace)
    if category is not None:
        rows = [row for row in rows if row.category is category]
    if owner:
        rows = [row for row in rows if row.owner.component_id == owner]
    if status:
        rows = [row for row in rows if row.status.value == status]
    if change_type:
        rows = [row for row in rows if row.change_type and row.change_type.value == change_type]
    if evidence_grade:
        rows = [
            row
            for row in rows
            if any(item.grade.value == evidence_grade for item in row.selected_evidence)
        ]
    if entity:
        finding_ids = {
            finding.finding_id for finding in trace.findings if finding.entity == entity
        }
        rows = [
            row
            for row in rows
            if any(finding_ids.intersection(item.finding_ids) for item in row.selected_evidence)
        ]
    if text:
        needle = text.casefold()
        rows = [
            row
            for row in rows
            if needle in row.operation.casefold()
            or needle in row.stage_name.casefold()
            or needle in row.owner.display_name.casefold()
        ]
    return {
        "schema_version": "trace.v1",
        "trace_id": trace.trace_id,
        "items": [row.model_dump(mode="json") for row in rows],
    }


@router.get("/runs/{run_id}/records/{source_id}/graph")
def graph(
    run_id: str,
    source_id: str,
    index: TraceIndexDependency,
) -> dict[str, object]:
    trace = _trace(index, run_id, source_id)
    nodes, edges = derive_graph(trace)
    return {
        "schema_version": "trace.v1",
        "trace_id": trace.trace_id,
        "nodes": [node.model_dump(mode="json") for node in nodes],
        "edges": [edge.model_dump(mode="json") for edge in edges],
    }


class ComparisonRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    left_trace_id: str
    right_trace_id: str
    stage_id: str | None = None


@router.post("/comparisons/resolve")
def resolve_comparison(
    request: ComparisonRequest,
    index: TraceIndexDependency,
) -> dict[str, object]:
    left = index.get_trace_by_id(request.left_trace_id)
    right = index.get_trace_by_id(request.right_trace_id)
    if left is None or right is None:
        raise not_found()
    if not left.run.row_policy.permits_records or not right.run.row_policy.permits_records:
        raise aggregate_only()
    same_record = (
        left.run.dataset == right.run.dataset and left.source.source_id == right.source.source_id
    )
    task_explanation = (
        left.source.source_id == right.source.source_id == "SYN-014"
        and {left.run.task, right.run.task} == {"exectv2", "gan2026"}
    )
    if not same_record and not task_explanation:
        raise not_found()
    return {
        "schema_version": "trace.v1",
        "mode": "task_explanation" if task_explanation else "same_record",
        "source_id": left.source.source_id,
        "selected_stage_id": request.stage_id,
        "left": {
            "trace_id": left.trace_id,
            "run": left.run.model_dump(mode="json"),
            "findings": [item.model_dump(mode="json") for item in left.findings],
            "score_views": [item.model_dump(mode="json") for item in left.score_views],
        },
        "right": {
            "trace_id": right.trace_id,
            "run": right.run.model_dump(mode="json"),
            "findings": [item.model_dump(mode="json") for item in right.findings],
            "score_views": [item.model_dump(mode="json") for item in right.score_views],
        },
        "stages": align_traces(left, right),
    }


@router.get("/review-sets")
def review_sets() -> dict[str, object]:
    return {
        "schema_version": "trace.v1",
        "items": [],
        "readiness": "not_indexed",
        "message": (
            "Semantic-support review is unavailable until a frozen response schema "
            "and adjudication rule are indexed."
        ),
    }
