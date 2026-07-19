from __future__ import annotations

import base64

from fastapi import APIRouter, Query

from clinical_extraction.trace_explorer.api.dependencies import TraceIndexDependency
from clinical_extraction.trace_explorer.api.errors import TraceExplorerError, not_found
from clinical_extraction.trace_explorer.policy import RowPolicy

router = APIRouter(prefix="/api/v1", tags=["catalog"])


def _encode_cursor(value: str) -> str:
    return base64.urlsafe_b64encode(value.encode("utf-8")).decode("ascii").rstrip("=")


def _decode_cursor(value: str | None) -> str | None:
    if value is None:
        return None
    try:
        padding = "=" * (-len(value) % 4)
        return base64.urlsafe_b64decode(value + padding).decode("utf-8")
    except (ValueError, UnicodeDecodeError) as exc:
        raise TraceExplorerError(
            status_code=400,
            code="invalid_cursor",
            message="The pagination cursor is invalid.",
        ) from exc


@router.get("/health")
def health(index: TraceIndexDependency) -> dict[str, object]:
    return {
        "schema_version": "trace.v1",
        "process_ready": True,
        "index_ready": index.ready,
    }


@router.get("/catalog")
def catalog(index: TraceIndexDependency) -> dict[str, object]:
    runs = index.list_runs()
    policy_counts = {policy.value: 0 for policy in RowPolicy}
    for run in runs:
        policy_counts[run["row_policy"]] += 1
    manifest = index.manifest()
    return {
        "schema_version": "trace.v1",
        "index_build_id": manifest.build_id,
        "tasks": sorted({run["task"] for run in runs}),
        "filters": {
            "task": sorted({run["task"] for run in runs}),
            "method": sorted({run["method"] for run in runs}),
            "split": sorted({run["split"] for run in runs}),
            "model": sorted({run["model"] for run in runs if run.get("model")}),
            "run_state": sorted({run["run_state"] for run in runs}),
            "inspectability": ["inspectable", "aggregate_only"],
        },
        "policy_counts": policy_counts,
        "review_sets": {"count": 0, "status": "not_indexed"},
    }


@router.get("/runs")
def runs(
    index: TraceIndexDependency,
    task: str | None = None,
    method: str | None = None,
    split: str | None = None,
    model: str | None = None,
    run_state: str | None = None,
    inspectable: bool | None = None,
    cursor: str | None = None,
    limit: int = Query(default=100, ge=1, le=100),
) -> dict[str, object]:
    after = _decode_cursor(cursor)
    items = index.list_runs(
        task=task,
        method=method,
        split=split,
        model=model,
        run_state=run_state,
        inspectable=inspectable,
    )
    if after is not None:
        items = [item for item in items if item["run_id"] > after]
    page = items[:limit]
    next_cursor = _encode_cursor(page[-1]["run_id"]) if len(items) > limit and page else None
    return {"schema_version": "trace.v1", "items": page, "next_cursor": next_cursor}


@router.get("/runs/{run_id}")
def run_detail(
    run_id: str,
    index: TraceIndexDependency,
) -> dict[str, object]:
    run = index.get_run(run_id)
    if run is None:
        raise not_found()
    return {"schema_version": "trace.v1", **run}


@router.get("/runs/{run_id}/aggregates")
def run_aggregates(
    run_id: str,
    index: TraceIndexDependency,
) -> dict[str, object]:
    run = index.get_run(run_id)
    if run is None:
        raise not_found()
    if run["row_policy"] == RowPolicy.DENIED:
        raise not_found()
    return {
        "schema_version": "trace.v1",
        "run_id": run["run_id"],
        "score_views": run.get("score_views", []),
        "diagnostics": run.get("integrity", {}),
    }
