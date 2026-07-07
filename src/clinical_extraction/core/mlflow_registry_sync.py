"""Dry-run registry-to-MLflow sync planning.

The run registry remains canonical. This module builds an aggregate-safe plan
for mirroring registry rows to MLflow without importing or calling MLflow.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from dataclasses import asdict, replace
from pathlib import Path

from clinical_extraction.core.mlflow_sync_artifacts import (
    artifact_policy,
    classify_artifact,
    classify_entry_artifacts,
    infer_dataset,
    infer_task,
)
from clinical_extraction.core.mlflow_sync_filters import (
    filter_registry_entries,
    resolve_backfill_filters,
)
from clinical_extraction.core.mlflow_sync_types import (
    BACKFILL_SCOPES,
    DEFAULT_REGISTRY_PATH,
    DEFAULT_RUN_INDEX_PATH,
    BackfillScopeName,
    MlflowParentSyncPlan,
    MlflowRunSyncPlan,
    MlflowSyncPlan,
    MlflowSyncResult,
)
from clinical_extraction.core.mlflow_tracking import (
    MlflowRunPayload,
    mirror_payload_to_mlflow,
    normalized_metrics,
    normalized_params,
    normalized_tags,
    registry_entry_to_mlflow_payload,
)
from clinical_extraction.core.registry import (
    RegistryRole,
    RunRegistryEntry,
)

__all__ = [
    "BACKFILL_SCOPES",
    "build_mlflow_comparison_sync_plan",
    "build_registry_mlflow_sync_plan",
    "build_run_sync_plan",
    "filter_registry_entries",
    "infer_dataset",
    "infer_task",
    "plan_to_json",
    "render_sync_plan",
    "render_sync_result",
    "resolve_backfill_filters",
    "result_to_json",
    "sync_plan_to_mlflow",
]


def build_registry_mlflow_sync_plan(
    entries: Sequence[RunRegistryEntry],
    *,
    repo_root: Path,
    registry_path: Path = DEFAULT_REGISTRY_PATH,
    run_index_path: Path = DEFAULT_RUN_INDEX_PATH,
    since_date: str | None = None,
    run_ids: Iterable[str] = (),
    registry_roles: Iterable[RegistryRole] = (),
    backfill_scope: BackfillScopeName | None = None,
    include_large_artifacts: bool = False,
) -> MlflowSyncPlan:
    """Build a dry-run MLflow sync plan from typed registry entries."""

    resolved_scope, resolved_since_date, resolved_roles = resolve_backfill_filters(
        backfill_scope=backfill_scope,
        since_date=since_date,
        registry_roles=registry_roles,
    )
    selected = filter_registry_entries(
        entries,
        since_date=resolved_since_date,
        run_ids=run_ids,
        registry_roles=resolved_roles,
    )
    runs = tuple(
        build_run_sync_plan(
            entry,
            repo_root=repo_root,
            include_large_artifacts=include_large_artifacts,
        )
        for entry in selected
    )
    return MlflowSyncPlan(
        dry_run=True,
        selected_run_count=len(runs),
        runs=runs,
        registry_path=str(registry_path),
        run_index_path=str(run_index_path),
        backfill_scope=resolved_scope.name if resolved_scope is not None else None,
        since_date=resolved_since_date,
        registry_roles=tuple(resolved_roles or ()),
    )


def build_mlflow_comparison_sync_plan(
    entries: Sequence[RunRegistryEntry],
    *,
    repo_root: Path,
    comparison_id: str,
    child_run_ids: Sequence[str],
    parent_artifact_paths: Sequence[str] = (),
    include_large_artifacts: bool = False,
    parent_run_name: str | None = None,
) -> MlflowSyncPlan:
    """Build a safe parent/child MLflow plan from canonical registry entries."""

    entries_by_id = {entry.run_id: entry for entry in entries}
    missing = [run_id for run_id in child_run_ids if run_id not in entries_by_id]
    if missing:
        raise ValueError(f"comparison child run id(s) not found: {', '.join(missing)}")

    child_runs = tuple(
        build_run_sync_plan(
            entries_by_id[run_id],
            repo_root=repo_root,
            include_large_artifacts=include_large_artifacts,
        )
        for run_id in child_run_ids
    )
    artifact_plan = tuple(
        classify_artifact(
            path,
            repo_root=repo_root,
            restricted_surface=False,
            include_large_artifacts=include_large_artifacts,
        )
        for path in parent_artifact_paths
    )
    policy = artifact_policy(artifact_plan, include_large_artifacts)
    parent_payload = MlflowRunPayload(
        experiment_name="clinical-extraction/exectv2",
        run_name=parent_run_name or comparison_id,
        params={
            "comparison_id": comparison_id,
            "task": "exectv2",
            "dataset": "ExECTv2 (2025)",
            "child_run_count": len(child_runs),
            "child_registry_run_ids": ",".join(child_run_ids),
            "primary_surface": "clinical_headline",
        },
        metrics=_comparison_parent_metrics(child_runs),
        tags={
            "same_core_comparison": True,
            "claim_boundary": "dev_only",
            "row_inspection_policy": "allowed",
            "raw_trace_policy": "disabled",
            "artifact_policy": policy,
            "registry_canonical": True,
            "restricted_surface": False,
            "comparison_id": comparison_id,
        },
        artifact_paths=tuple(
            Path(artifact.path) for artifact in artifact_plan if artifact.action == "log_artifact"
        ),
    )
    parent = MlflowParentSyncPlan(
        comparison_id=comparison_id,
        experiment_name=parent_payload.experiment_name,
        run_name=parent_payload.run_name,
        params=normalized_params(parent_payload),
        metrics=normalized_metrics(parent_payload),
        tags=normalized_tags(parent_payload),
        artifact_policy=policy,
        artifacts=artifact_plan,
    )
    return MlflowSyncPlan(
        dry_run=True,
        selected_run_count=len(child_runs),
        runs=child_runs,
        parent=parent,
    )


def build_run_sync_plan(
    entry: RunRegistryEntry,
    *,
    repo_root: Path,
    include_large_artifacts: bool = False,
) -> MlflowRunSyncPlan:
    """Return the dry-run MLflow payload and artifact actions for one entry."""

    artifact_plan = classify_entry_artifacts(
        entry,
        repo_root=repo_root,
        include_large_artifacts=include_large_artifacts,
    )
    direct_artifacts = tuple(
        Path(item.path) for item in artifact_plan if item.action == "log_artifact"
    )
    policy = artifact_policy(artifact_plan, include_large_artifacts)
    payload = registry_entry_to_mlflow_payload(
        entry,
        task=infer_task(entry),
        dataset=infer_dataset(entry),
        artifact_policy=policy,
    )
    payload = replace(payload, artifact_paths=direct_artifacts)

    return MlflowRunSyncPlan(
        registry_run_id=entry.run_id,
        experiment_name=payload.experiment_name,
        run_name=payload.run_name,
        params=normalized_params(payload),
        metrics=normalized_metrics(payload),
        tags=normalized_tags(payload),
        artifact_policy=policy,
        artifacts=artifact_plan,
    )


def sync_plan_to_mlflow(plan: MlflowSyncPlan, *, repo_root: Path) -> MlflowSyncResult:
    """Mirror a dry-run plan to MLflow."""

    if plan.parent is not None:
        return _sync_comparison_plan_to_mlflow(plan, repo_root=repo_root)
    mirrored: dict[str, str | None] = {}
    for run in plan.runs:
        payload = _run_sync_plan_to_payload(run)
        mirrored[run.registry_run_id] = mirror_payload_to_mlflow(payload, repo_root=repo_root)
    return MlflowSyncResult(dry_run=False, parent_run_id=None, mirrored_run_ids=mirrored)


def render_sync_plan(plan: MlflowSyncPlan) -> str:
    """Render a compact human-facing dry-run report."""

    if plan.parent is not None:
        return _render_comparison_sync_plan(plan)
    lines = [
        "# MLflow registry sync dry run",
        f"Registry: {plan.registry_path}",
        f"Run index: {plan.run_index_path}",
        f"Runs selected: {plan.selected_run_count}",
    ]
    if plan.backfill_scope is not None:
        lines.append(f"Backfill scope: {plan.backfill_scope}")
    if plan.since_date is not None:
        lines.append(f"Since date: {plan.since_date}")
    if plan.registry_roles:
        lines.append(f"Registry roles: {', '.join(plan.registry_roles)}")
    lines.append("")
    for run in plan.runs:
        lines.extend(_render_run_lines(run))
    return "\n".join(lines).rstrip() + "\n"


def render_sync_result(result: MlflowSyncResult) -> str:
    """Render the result of a real MLflow sync."""

    lines = ["# MLflow sync result", f"Dry run: {str(result.dry_run).lower()}"]
    if result.parent_run_id is not None:
        lines.append(f"Parent MLflow run id: {result.parent_run_id}")
    for registry_run_id, mlflow_run_id in result.mirrored_run_ids.items():
        lines.append(f"- {registry_run_id}: {mlflow_run_id or 'not mirrored'}")
    return "\n".join(lines).rstrip() + "\n"


def plan_to_json(plan: MlflowSyncPlan) -> str:
    """Serialize a dry-run plan as deterministic JSON."""

    return json.dumps(asdict(plan), indent=2, sort_keys=True)


def result_to_json(result: MlflowSyncResult) -> str:
    """Serialize a sync result as deterministic JSON."""

    return json.dumps(asdict(result), indent=2, sort_keys=True)


def _sync_comparison_plan_to_mlflow(plan: MlflowSyncPlan, *, repo_root: Path) -> MlflowSyncResult:
    parent = plan.parent
    if parent is None:
        raise ValueError("comparison sync requires plan.parent")

    parent_payload = MlflowRunPayload(
        experiment_name=parent.experiment_name,
        run_name=parent.run_name,
        params=parent.params,
        metrics=parent.metrics,
        tags=parent.tags,
        artifact_paths=tuple(
            Path(artifact.path)
            for artifact in parent.artifacts
            if artifact.action == "log_artifact"
        ),
    )
    parent_run_id = mirror_payload_to_mlflow(parent_payload, repo_root=repo_root)
    mirrored: dict[str, str | None] = {}
    if parent_run_id is None:
        return MlflowSyncResult(dry_run=False, parent_run_id=None, mirrored_run_ids=mirrored)

    for child in plan.runs:
        payload = _run_sync_plan_to_payload(child, parent_run_id=parent_run_id)
        mirrored[child.registry_run_id] = mirror_payload_to_mlflow(payload, repo_root=repo_root)
    return MlflowSyncResult(
        dry_run=False,
        parent_run_id=parent_run_id,
        mirrored_run_ids=mirrored,
    )


def _render_comparison_sync_plan(plan: MlflowSyncPlan) -> str:
    parent = plan.parent
    if parent is None:
        raise ValueError("comparison render requires plan.parent")

    lines = [
        "# MLflow comparison sync dry run",
        f"Comparison: {parent.comparison_id}",
        f"Experiment: {parent.experiment_name}",
        f"Parent run: {parent.run_name}",
        f"Child runs selected: {plan.selected_run_count}",
        f"Parent artifact_policy: {parent.artifact_policy}",
        "",
    ]
    if parent.metrics:
        metric_keys = ", ".join(sorted(parent.metrics))
        lines.append(f"Parent metrics: {metric_keys}")
    for artifact in parent.artifacts:
        lines.append(f"Parent artifact {artifact.action}: {artifact.path} ({artifact.reason})")
    if parent.artifacts:
        lines.append("")
    for child in plan.runs:
        lines.extend(_render_run_lines(child, child=True))
    return "\n".join(lines).rstrip() + "\n"


def _render_run_lines(run: MlflowRunSyncPlan, *, child: bool = False) -> list[str]:
    if child:
        lines = [f"- child {run.registry_run_id}"]
    else:
        lines = [f"- {run.registry_run_id}"]
    detail_prefix = "  "
    lines.extend(
        [
            f"{detail_prefix}experiment: {run.experiment_name}",
            f"{detail_prefix}run: {run.run_name}",
            f"{detail_prefix}artifact_policy: {run.artifact_policy}",
        ]
    )
    if run.metrics:
        metric_keys = ", ".join(sorted(run.metrics))
        lines.append(f"{detail_prefix}metrics: {metric_keys}")
    for artifact in run.artifacts:
        lines.append(
            f"{detail_prefix}artifact {artifact.action}: {artifact.path} ({artifact.reason})"
        )
    return lines


def _comparison_parent_metrics(child_runs: Sequence[MlflowRunSyncPlan]) -> dict[str, float]:
    clinical_f1 = [
        run.metrics["clinical_headline_f1"]
        for run in child_runs
        if "clinical_headline_f1" in run.metrics
    ]
    metrics: dict[str, float] = {
        "child_run_count": float(len(child_runs)),
        "call_failures_total": sum(run.metrics.get("call_failures", 0.0) for run in child_runs),
        "parse_schema_failures_total": sum(
            run.metrics.get("parse_schema_failures", 0.0) + run.metrics.get("parse_failures", 0.0)
            for run in child_runs
        ),
    }
    if clinical_f1:
        metrics["best_clinical_headline_f1"] = max(clinical_f1)
        metrics["worst_clinical_headline_f1"] = min(clinical_f1)
        metrics["clinical_headline_f1_spread"] = max(clinical_f1) - min(clinical_f1)
    return metrics


def _run_sync_plan_to_payload(
    run: MlflowRunSyncPlan, *, parent_run_id: str | None = None
) -> MlflowRunPayload:
    return MlflowRunPayload(
        experiment_name=run.experiment_name,
        run_name=run.run_name,
        params=run.params,
        metrics=run.metrics,
        tags=run.tags,
        artifact_paths=tuple(
            Path(artifact.path) for artifact in run.artifacts if artifact.action == "log_artifact"
        ),
        parent_run_id=parent_run_id,
    )
