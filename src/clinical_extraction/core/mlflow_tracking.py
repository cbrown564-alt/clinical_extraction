"""Optional MLflow mirroring helpers for experiment observability.

The run registry and human-readable reports remain the source of truth. This
module only mirrors safe metadata and selected artifacts when MLflow is present.
"""

from __future__ import annotations

import importlib
import importlib.util
import logging
import math
import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)

MLFLOW_DISABLED_ENV = "CLINICAL_EXTRACTION_MLFLOW_DISABLED"
MLFLOW_STRICT_ENV = "CLINICAL_EXTRACTION_MLFLOW_STRICT"
MLFLOW_TRACKING_URI_ENV = "MLFLOW_TRACKING_URI"
MLFLOW_ALLOW_FILE_STORE_ENV = "MLFLOW_ALLOW_FILE_STORE"
MLFLOW_PARENT_RUN_TAG = "mlflow.parentRunId"

ParamValue = str | int | float | bool | None
MetricValue = int | float
TagValue = str | bool | None


@dataclass(frozen=True)
class MlflowRunPayload:
    """Safe metadata package for one optional MLflow run."""

    experiment_name: str
    run_name: str
    params: Mapping[str, ParamValue] = field(default_factory=dict)
    metrics: Mapping[str, MetricValue] = field(default_factory=dict)
    tags: Mapping[str, TagValue] = field(default_factory=dict)
    artifact_paths: tuple[Path, ...] = ()
    artifact_pointer_paths: tuple[Path, ...] = ()
    parent_run_id: str | None = None


def mlflow_available() -> bool:
    """Return whether MLflow can be imported without importing it eagerly."""

    return importlib.util.find_spec("mlflow") is not None


def configure_mlflow_from_env(repo_root: Path) -> None:
    """Configure MLflow tracking URI from environment or a repo-local default."""

    if _disabled():
        LOGGER.info("MLflow mirroring disabled by %s=1", MLFLOW_DISABLED_ENV)
        return
    if not mlflow_available():
        LOGGER.info("MLflow is not installed; optional mirroring is skipped")
        return

    mlflow = _load_mlflow()
    tracking_uri = os.getenv(MLFLOW_TRACKING_URI_ENV)
    if not tracking_uri:
        tracking_uri = f"file:{(repo_root.resolve() / 'mlruns').as_posix()}"
        os.environ.setdefault(MLFLOW_ALLOW_FILE_STORE_ENV, "true")
    mlflow.set_tracking_uri(tracking_uri)


def mirror_payload_to_mlflow(
    payload: MlflowRunPayload, *, repo_root: Path | None = None
) -> str | None:
    """Mirror one payload to MLflow and return the MLflow run id when created.

    MLflow is optional. Missing MLflow, disabled mirroring, or non-strict logging
    failures return ``None`` after logging a concise message. Set
    ``CLINICAL_EXTRACTION_MLFLOW_STRICT=1`` to make logging failures fatal.
    """

    if _disabled():
        LOGGER.info("MLflow mirroring disabled by %s=1", MLFLOW_DISABLED_ENV)
        return None
    if not mlflow_available():
        LOGGER.info("MLflow is not installed; optional mirroring is skipped")
        return None

    root = (repo_root or Path.cwd()).resolve()
    try:
        configure_mlflow_from_env(root)
        mlflow = _load_mlflow()
        mlflow.set_experiment(payload.experiment_name)
        tags = normalized_tags(payload)
        if payload.parent_run_id:
            tags[MLFLOW_PARENT_RUN_TAG] = payload.parent_run_id

        with mlflow.start_run(run_name=payload.run_name, tags=tags) as active_run:
            params = normalized_params(payload)
            metrics = normalized_metrics(payload)
            if params:
                mlflow.log_params(params)
            if metrics:
                mlflow.log_metrics(metrics)
            for artifact_path in safe_artifact_paths(payload, repo_root=root):
                mlflow.log_artifact(str(artifact_path))
            return str(active_run.info.run_id)
    except Exception:
        if _strict():
            raise
        LOGGER.warning(
            "Optional MLflow mirroring failed; core artifact is unchanged",
            exc_info=True,
        )
        return None


def registry_entry_to_mlflow_payload(
    entry: Any,
    *,
    task: str,
    dataset: str | None = None,
    experiment_name: str | None = None,
    claim_boundary: str | None = None,
    row_inspection_policy: str | None = None,
    raw_trace_policy: str = "disabled",
    artifact_policy: str = "selected_artifacts",
) -> MlflowRunPayload:
    """Convert a registry-like entry into an MLflow payload.

    The function intentionally accepts a registry-like object instead of making
    core depend on a task package. The expected shape is ``RunRegistryEntry``.
    """

    split = str(entry.split)
    pipeline_family = str(entry.pipeline_family)
    architecture_family = getattr(entry, "architecture_family", None)
    comparison_role = getattr(entry, "comparison_role", None)
    decision = str(entry.decision)
    primary_metrics = getattr(entry, "primary_metrics", {})
    repair_mode = getattr(entry, "repair_mode", None)
    evidence_validity = getattr(entry, "evidence_validity", None)

    params: dict[str, ParamValue] = {
        "registry_run_id": str(entry.run_id),
        "task": task,
        "dataset": dataset,
        "split": split,
        "row_count": entry.row_count,
        "pipeline_family": pipeline_family,
        "model": str(entry.model),
        "model_role": str(entry.model_role),
        "mode": str(entry.mode),
        "replay_status": str(entry.replay_status),
        "repair_mode": repair_mode,
    }
    metrics = {
        name: value
        for name, value in dict(primary_metrics).items()
        if _is_metric_value(value)
    }
    tags: dict[str, TagValue] = {
        "claim_status": _claim_status_from_decision(decision, comparison_role),
        "claim_boundary": claim_boundary or _claim_boundary_for_split(split),
        "row_inspection_policy": row_inspection_policy or _row_inspection_policy_for_split(split),
        "raw_trace_policy": raw_trace_policy,
        "artifact_policy": artifact_policy,
        "component_ownership": _component_ownership(pipeline_family, architecture_family),
        "registry_canonical": True,
        "restricted_surface": _restricted_surface(split),
        "operational_candidate": comparison_role != "diagnostic",
    }
    if evidence_validity:
        tags["evidence_validity"] = str(evidence_validity)

    experiment = experiment_name or f"clinical-extraction/{task}"
    artifact_paths = tuple(Path(path) for path in entry.artifact_paths)
    return MlflowRunPayload(
        experiment_name=experiment,
        run_name=str(entry.run_id),
        params=params,
        metrics=metrics,
        tags=tags,
        artifact_paths=artifact_paths,
    )


def normalized_params(payload: MlflowRunPayload) -> dict[str, str]:
    """Return MLflow-safe params, dropping unset values."""

    return {
        str(key): _stringify(value)
        for key, value in payload.params.items()
        if value is not None
    }


def normalized_metrics(payload: MlflowRunPayload) -> dict[str, float]:
    """Return finite numeric metrics, excluding booleans and non-finite values."""

    metrics: dict[str, float] = {}
    for key, value in payload.metrics.items():
        if isinstance(value, bool):
            continue
        numeric = float(value)
        if math.isfinite(numeric):
            metrics[str(key)] = numeric
    return metrics


def normalized_tags(payload: MlflowRunPayload) -> dict[str, str]:
    """Return MLflow-safe tags, dropping unset values."""

    return {
        str(key): _stringify(value)
        for key, value in payload.tags.items()
        if value is not None
    }


def safe_artifact_paths(payload: MlflowRunPayload, *, repo_root: Path) -> tuple[Path, ...]:
    """Return existing artifact paths that resolve under ``repo_root``."""

    root = repo_root.resolve()
    safe_paths: list[Path] = []
    for artifact_path in (*payload.artifact_paths, *payload.artifact_pointer_paths):
        candidate = artifact_path if artifact_path.is_absolute() else root / artifact_path
        resolved = candidate.resolve()
        if root not in (resolved, *resolved.parents):
            LOGGER.warning("Skipping MLflow artifact outside repo root: %s", artifact_path)
            continue
        if not resolved.exists() or not resolved.is_file():
            LOGGER.warning("Skipping missing MLflow artifact: %s", artifact_path)
            continue
        safe_paths.append(resolved)
    return tuple(safe_paths)


def _load_mlflow() -> Any:
    return importlib.import_module("mlflow")


def _disabled() -> bool:
    return os.getenv(MLFLOW_DISABLED_ENV) == "1"


def _strict() -> bool:
    return os.getenv(MLFLOW_STRICT_ENV) == "1"


def _stringify(value: str | int | float | bool) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _is_metric_value(value: Any) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool) and math.isfinite(value)


def _claim_status_from_decision(decision: str, comparison_role: Any) -> str:
    if comparison_role == "diagnostic":
        return "diagnostic"
    if decision in {"promote", "promote_to_phase3_report"} or decision.startswith(
        "promote_"
    ):
        return "promote"
    if decision == "reject":
        return "reject"
    if decision == "revise":
        return "revise"
    if decision == "reliability_scorecard":
        return "reliability_scorecard"
    if decision in {"historical", "superseded"}:
        return "historical"
    return "diagnostic"


def _claim_boundary_for_split(split: str) -> str:
    lower = split.lower()
    if "full200" in lower:
        return "full200_aggregate_only"
    if "test" in lower or "holdout" in lower:
        return "locked_holdout_aggregate"
    if "validation" in lower:
        return "validation_development"
    if "dev" in lower:
        return "dev_only"
    return "analysis_only"


def _row_inspection_policy_for_split(split: str) -> str:
    lower = split.lower()
    if "full200" in lower or "test" in lower or "holdout" in lower:
        return "aggregate_only"
    if "dev" in lower or "validation" in lower:
        return "allowed"
    return "not_applicable"


def _restricted_surface(split: str) -> bool:
    lower = split.lower()
    return "full200" in lower or "test" in lower or "holdout" in lower


def _component_ownership(pipeline_family: str, architecture_family: Any) -> str:
    if architecture_family in {"rules_only", "hybrid", "llm_only"}:
        return str(architecture_family)
    if pipeline_family.startswith("rules_only"):
        return "rules_only"
    if pipeline_family.startswith("hybrid"):
        return "hybrid"
    if pipeline_family.startswith("llm_only"):
        return "llm_only"
    return "analysis_only"
