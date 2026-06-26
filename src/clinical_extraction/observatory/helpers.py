"""Path and settings utilities shared by Observatory routers."""

from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException

from clinical_extraction.core.paths import (
    discover_repo_root_or_cwd,
    resolve_under_root,
)
from clinical_extraction.observatory.models import EXECUTABLE_PIPELINES, ObservatorySettings

__all__ = [
    "discover_repo_root",
    "relative_to_root",
    "require_supported_pipeline",
    "resolve_under_root",
    "safe_repo_path",
]


def discover_repo_root() -> Path:
    return discover_repo_root_or_cwd(require_src=True)


def safe_repo_path(repo_root: Path, relative_path: str) -> Path:
    path = Path(relative_path)
    if path.is_absolute() or ".." in path.parts:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid repository-relative path: {relative_path}",
        )
    resolved = (repo_root / path).resolve()
    if repo_root not in (resolved, *resolved.parents):
        raise HTTPException(status_code=400, detail=f"Path escapes repository: {relative_path}")
    return resolved


def relative_to_root(settings: ObservatorySettings, path: Path) -> str:
    try:
        return str(path.relative_to(settings.repo_root))
    except ValueError:
        return str(path)


def require_supported_pipeline(pipeline: str) -> None:
    if pipeline not in EXECUTABLE_PIPELINES:
        raise HTTPException(
            status_code=400,
            detail=f"Pipeline {pipeline!r} is not yet executable via the Observatory API. "
            f"Supported: {sorted(EXECUTABLE_PIPELINES)}.",
        )
