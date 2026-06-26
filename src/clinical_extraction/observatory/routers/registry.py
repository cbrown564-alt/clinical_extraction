"""Registry, artifact, and split routes for the Observatory."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request

from clinical_extraction.observatory.gan2026 import (
    build_pipeline_families,
    load_artifact_content,
    registry_entry,
    select_artifact_paths,
)
from clinical_extraction.observatory.helpers import relative_to_root, safe_repo_path
from clinical_extraction.tasks.seizure_frequency.gan2026.data import load_split_manifest
from clinical_extraction.core.registry import (
    load_run_registry,
)

router = APIRouter(tags=["registry"])


def _settings(request: Request):
    return request.app.state.observatory_settings


@router.get("/artifacts/{run_id}")
def get_artifact(
    run_id: str,
    request: Request,
    artifact_path: str | None = Query(default=None),
    limit: int | None = Query(default=None, ge=1),
) -> dict[str, Any]:
    settings = _settings(request)
    entry = registry_entry(settings, run_id)
    record = entry.to_json_record()
    selected_paths = select_artifact_paths(
        settings.repo_root,
        record["artifact_paths"],
        record.get("split"),
        artifact_path,
    )
    if not selected_paths:
        return {
            "run_id": run_id,
            "artifact_paths": [],
            "artifact_type": "none",
            "content": [],
            "note": "No JSONL artifacts available for this run",
        }
    all_content: list[Any] = []
    for selected_path in selected_paths:
        resolved = safe_repo_path(settings.repo_root, selected_path)
        if not resolved.exists():
            continue
        content = load_artifact_content(resolved, limit=limit)
        if isinstance(content, list):
            all_content.extend(content)
        else:
            all_content.append(content)
    if limit is not None:
        all_content = all_content[:limit]
    return {
        "run_id": run_id,
        "artifact_paths": selected_paths,
        "artifact_type": "jsonl",
        "content": all_content,
    }


@router.get("/registry")
def registry(request: Request) -> dict[str, Any]:
    settings = _settings(request)
    entries = [entry.to_json_record() for entry in load_run_registry(settings.registry_path)]
    return {
        "registry_path": relative_to_root(settings, settings.registry_path),
        "runs": entries,
    }


@router.get("/splits/{split_name}")
def split(split_name: str, request: Request) -> dict[str, Any]:
    settings = _settings(request)
    manifest = load_split_manifest(settings.split_manifest_path)
    splits = manifest.get("splits", {})
    if split_name not in splits:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown split {split_name!r}; expected one of {sorted(splits)}",
        )
    payload = dict(splits[split_name])
    payload["split_name"] = split_name
    payload["manifest_path"] = relative_to_root(settings, settings.split_manifest_path)
    payload["split_manifest"] = manifest.get("split_manifest", "gan2026_split_v1")
    return payload


@router.get("/pipeline-families")
def pipeline_families(request: Request) -> dict[str, Any]:
    settings = _settings(request)
    families = build_pipeline_families(settings)
    return {"families": families}
