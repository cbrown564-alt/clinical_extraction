"""Artifact classification and task inference for MLflow registry sync."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from clinical_extraction.core.claim_policy import restricted_surface_for_registry_entry
from clinical_extraction.core.mlflow_sync_types import (
    LARGE_ARTIFACT_BYTES,
    RESTRICTED_DIRECT_SUFFIXES,
    ROW_ARTIFACT_SUFFIXES,
    ArtifactSyncPlan,
)
from clinical_extraction.core.registry import RunRegistryEntry


def classify_artifact(
    artifact_path: str,
    *,
    repo_root: Path,
    restricted_surface: bool,
    include_large_artifacts: bool,
) -> ArtifactSyncPlan:
    """Classify one artifact path without reading artifact contents."""

    root = repo_root.resolve()
    path = Path(artifact_path)
    if path.is_absolute() or ".." in path.parts:
        return ArtifactSyncPlan(
            path=artifact_path,
            action="skip_invalid",
            reason="artifact path must be repo-relative",
        )
    resolved = (root / path).resolve()
    if root not in (resolved, *resolved.parents):
        return ArtifactSyncPlan(
            path=artifact_path,
            action="skip_invalid",
            reason="artifact path resolves outside the repository",
        )
    if not resolved.exists() or not resolved.is_file():
        return ArtifactSyncPlan(
            path=artifact_path,
            action="skip_missing",
            reason="artifact file is missing",
        )

    size = resolved.stat().st_size
    suffix = resolved.suffix.lower()
    if restricted_surface and suffix not in RESTRICTED_DIRECT_SUFFIXES:
        return ArtifactSyncPlan(
            path=artifact_path,
            action="pointer_only",
            reason="restricted surface; direct artifact copy limited to aggregate text reports",
            size_bytes=size,
        )
    if suffix in ROW_ARTIFACT_SUFFIXES and not include_large_artifacts:
        return ArtifactSyncPlan(
            path=artifact_path,
            action="pointer_only",
            reason=(
                "row-level artifact; pointer only unless large artifacts are explicitly included"
            ),
            size_bytes=size,
        )
    if size > LARGE_ARTIFACT_BYTES and not include_large_artifacts:
        return ArtifactSyncPlan(
            path=artifact_path,
            action="pointer_only",
            reason="large artifact; pointer only unless large artifacts are explicitly included",
            size_bytes=size,
        )
    return ArtifactSyncPlan(
        path=artifact_path,
        action="log_artifact",
        reason="safe selected artifact",
        size_bytes=size,
    )


def artifact_policy(
    artifacts: Sequence[ArtifactSyncPlan],
    include_large_artifacts: bool,
) -> str:
    if include_large_artifacts:
        return "full_artifacts"
    if any(artifact.action == "log_artifact" for artifact in artifacts):
        return "selected_artifacts"
    return "summary_only"


def infer_task(entry: RunRegistryEntry) -> str:
    """Infer the stable task label used for MLflow experiment names."""

    text = f"{entry.run_id} {entry.pipeline_family}".lower()
    if "exectv2" in text:
        return "exectv2"
    if "gan2026" in text or "gan_2026" in text:
        return "gan2026"
    return "reliability"


def infer_dataset(entry: RunRegistryEntry) -> str | None:
    """Infer the broad dataset family for registry-derived MLflow params."""

    task = infer_task(entry)
    if task == "exectv2":
        return "ExECTv2 (2025)"
    if task == "gan2026":
        return "Gan (2026)"
    return None


def classify_entry_artifacts(
    entry: RunRegistryEntry,
    *,
    repo_root: Path,
    include_large_artifacts: bool,
) -> tuple[ArtifactSyncPlan, ...]:
    return tuple(
        classify_artifact(
            path,
            repo_root=repo_root,
            restricted_surface=restricted_surface_for_registry_entry(entry),
            include_large_artifacts=include_large_artifacts,
        )
        for path in entry.artifact_paths
    )
