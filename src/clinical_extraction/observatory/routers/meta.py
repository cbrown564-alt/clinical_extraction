"""Health and repository metadata routes for the Observatory."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Request

from clinical_extraction.observatory.git import git_metadata
from clinical_extraction.observatory.responses import HealthResponse, MetaResponse

router = APIRouter(tags=["meta"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/meta", response_model=MetaResponse)
def meta(request: Request) -> MetaResponse:
    settings = request.app.state.observatory_settings
    return MetaResponse(
        git=git_metadata(settings.repo_root),
        observatory_version="0.1.0",
        timestamp=datetime.now(UTC).isoformat(),
    )
