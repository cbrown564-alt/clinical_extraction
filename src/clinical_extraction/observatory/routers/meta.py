"""Health and repository metadata routes for the Observatory."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Request

from clinical_extraction.observatory.git import git_metadata

router = APIRouter(tags=["meta"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/meta")
def meta(request: Request) -> dict[str, object]:
    settings = request.app.state.observatory_settings
    return {
        "git": git_metadata(settings.repo_root),
        "observatory_version": "0.1.0",
        "timestamp": datetime.now(UTC).isoformat(),
    }
