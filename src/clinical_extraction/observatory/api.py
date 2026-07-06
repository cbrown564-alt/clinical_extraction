"""Thin FastAPI wrapper for the clinical-extraction Observatory.

Shared cross-task backend the frontend consumes: Gan 2026 (registry, records,
rules, live pipeline/ablation execution) and ExECTv2 (the live ``/exectv2/runs``
frontend dataset). Lives at the package top level rather than under the gan2026
task because it now serves both datasets.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI

from clinical_extraction.observatory.helpers import discover_repo_root, resolve_under_root
from clinical_extraction.observatory.models import ObservatorySettings
from clinical_extraction.observatory.routers import (
    exectv2,
    gan2026,
    gold_audit,
    gold_noise,
    meta,
    registry,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    DEFAULT_DATA_PATH,
    DEFAULT_SPLIT_MANIFEST_PATH,
)


def create_app(
    *,
    repo_root: Path | None = None,
    data_path: Path | None = None,
    split_manifest_path: Path | None = None,
    registry_path: Path | None = None,
    experiments_dir: Path | None = None,
) -> FastAPI:
    """Create the Observatory FastAPI app."""

    root = (repo_root or discover_repo_root()).resolve()
    settings = ObservatorySettings(
        repo_root=root,
        data_path=resolve_under_root(root, data_path or DEFAULT_DATA_PATH),
        split_manifest_path=resolve_under_root(
            root,
            split_manifest_path or DEFAULT_SPLIT_MANIFEST_PATH,
        ),
        registry_path=resolve_under_root(
            root,
            registry_path or Path("experiments/registry.jsonl"),
        ),
        experiments_dir=resolve_under_root(root, experiments_dir or Path("experiments")),
    )

    app = FastAPI(
        title="Clinical Extraction Observatory API",
        version="0.1.0",
        summary=(
            "Thin backend over the clinical-extraction pipelines, artifacts, "
            "and frontend datasets (Gan 2026 and ExECTv2)."
        ),
    )
    app.state.observatory_settings = settings

    app.include_router(meta.router)
    app.include_router(exectv2.router)
    app.include_router(gan2026.router)
    app.include_router(registry.router)
    app.include_router(gold_audit.router)
    app.include_router(gold_noise.router)

    return app


app = create_app()
