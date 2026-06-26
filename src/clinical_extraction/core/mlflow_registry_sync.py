"""Dry-run registry-to-MLflow sync planning.

The run registry remains canonical. This module builds an aggregate-safe plan
for mirroring registry rows to MLflow without importing or calling MLflow.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass, replace
from datetime import date
from pathlib import Path
from typing import Literal

from clinical_extraction.core.mlflow_tracking import (
    MlflowRunPayload,
    mirror_payload_to_mlflow,
    normalized_metrics,
    normalized_params,
    normalized_tags,
    registry_entry_to_mlflow_payload,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry import (
    RunRegistryEntry,
    load_run_registry,
)

ArtifactAction = Literal["log_artifact", "pointer_only", "skip_invalid", "skip_missing"]

DEFAULT_REGISTRY_PATH = Path("experiments") / "registry.jsonl"
DEFAULT_RUN_INDEX_PATH = Path("experiments") / "RUN_INDEX.md"
ROW_ARTIFACT_SUFFIXES = frozenset((".jsonl", ".csv", ".tsv"))
RESTRICTED_DIRECT_SUFFIXES = frozenset((".md", ".txt"))
LARGE_ARTIFACT_BYTES = 5 * 1024 * 1024
SAME_CORE_DEV140_COMPARISON_ID = "exectv2_same_core_model_swap_dev140_20260625"
SAME_CORE_DEV140_RUN_IDS = (
    "exectv2_2call_no_sf_adjudicator_gpt41mini_dev140",
    "exectv2_2call_no_sf_adjudicator_deepseek_dev140",
    "exectv2_2call_no_sf_adjudicator_qwen36_dev140",
    "exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_dev140",
)
SAME_CORE_DEV140_PARENT_ARTIFACTS = (
    "docs/experiments/exectv2/reliability/exectv2_same_core_model_swap_dev140_2026-06-25.md",
    "experiments/exectv2_same_core_model_swap_dev140_20260625.json",
)


@dataclass(frozen=True)
class ArtifactSyncPlan:
    """One registry artifact and the dry-run action MLflow sync would take."""

    path: str
    action: ArtifactAction
    reason: str
    size_bytes: int | None = None


@dataclass(frozen=True)
class MlflowRunSyncPlan:
    """Dry-run MLflow payload summary for one registry row."""

    registry_run_id: str
    experiment_name: str
    run_name: str
    params: dict[str, str]
    metrics: dict[str, float]
    tags: dict[str, str]
    artifact_policy: str
    artifacts: tuple[ArtifactSyncPlan, ...]


@dataclass(frozen=True)
class RegistryMlflowSyncPlan:
    """Dry-run plan for a registry sync invocation."""

    registry_path: str
    run_index_path: str
    dry_run: bool
    selected_run_count: int
    runs: tuple[MlflowRunSyncPlan, ...]


@dataclass(frozen=True)
class MlflowComparisonSyncPlan:
    """Dry-run or execution plan for a parent/child MLflow comparison group."""

    comparison_id: str
    experiment_name: str
    parent_run_name: str
    parent_params: dict[str, str]
    parent_metrics: dict[str, float]
    parent_tags: dict[str, str]
    artifact_policy: str
    artifacts: tuple[ArtifactSyncPlan, ...]
    dry_run: bool
    selected_run_count: int
    child_runs: tuple[MlflowRunSyncPlan, ...]


@dataclass(frozen=True)
class MlflowSyncResult:
    """Result of an actual MLflow mirror invocation."""

    dry_run: bool
    parent_run_id: str | None
    mirrored_run_ids: dict[str, str | None]


def build_registry_mlflow_sync_plan(
    entries: Sequence[RunRegistryEntry],
    *,
    repo_root: Path,
    registry_path: Path = DEFAULT_REGISTRY_PATH,
    run_index_path: Path = DEFAULT_RUN_INDEX_PATH,
    since_date: str | None = None,
    run_ids: Iterable[str] = (),
    include_large_artifacts: bool = False,
) -> RegistryMlflowSyncPlan:
    """Build a dry-run MLflow sync plan from typed registry entries."""

    selected = filter_registry_entries(entries, since_date=since_date, run_ids=run_ids)
    runs = tuple(
        build_run_sync_plan(
            entry,
            repo_root=repo_root,
            include_large_artifacts=include_large_artifacts,
        )
        for entry in selected
    )
    return RegistryMlflowSyncPlan(
        registry_path=str(registry_path),
        run_index_path=str(run_index_path),
        dry_run=True,
        selected_run_count=len(runs),
        runs=runs,
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
) -> MlflowComparisonSyncPlan:
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
    artifact_policy = _artifact_policy(artifact_plan, include_large_artifacts)
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
            "artifact_policy": artifact_policy,
            "registry_canonical": True,
            "restricted_surface": False,
            "comparison_id": comparison_id,
        },
        artifact_paths=tuple(
            Path(artifact.path) for artifact in artifact_plan if artifact.action == "log_artifact"
        ),
    )

    return MlflowComparisonSyncPlan(
        comparison_id=comparison_id,
        experiment_name=parent_payload.experiment_name,
        parent_run_name=parent_payload.run_name,
        parent_params=normalized_params(parent_payload),
        parent_metrics=normalized_metrics(parent_payload),
        parent_tags=normalized_tags(parent_payload),
        artifact_policy=artifact_policy,
        artifacts=artifact_plan,
        dry_run=True,
        selected_run_count=len(child_runs),
        child_runs=child_runs,
    )


def sync_registry_plan_to_mlflow(
    plan: RegistryMlflowSyncPlan, *, repo_root: Path
) -> MlflowSyncResult:
    """Mirror a registry plan to MLflow as ungrouped runs."""

    mirrored: dict[str, str | None] = {}
    for run in plan.runs:
        payload = _run_sync_plan_to_payload(run)
        mirrored[run.registry_run_id] = mirror_payload_to_mlflow(payload, repo_root=repo_root)
    return MlflowSyncResult(dry_run=False, parent_run_id=None, mirrored_run_ids=mirrored)


def sync_comparison_plan_to_mlflow(
    plan: MlflowComparisonSyncPlan, *, repo_root: Path
) -> MlflowSyncResult:
    """Mirror a parent/child comparison plan to MLflow."""

    parent_payload = MlflowRunPayload(
        experiment_name=plan.experiment_name,
        run_name=plan.parent_run_name,
        params=plan.parent_params,
        metrics=plan.parent_metrics,
        tags=plan.parent_tags,
        artifact_paths=tuple(
            Path(artifact.path) for artifact in plan.artifacts if artifact.action == "log_artifact"
        ),
    )
    parent_run_id = mirror_payload_to_mlflow(parent_payload, repo_root=repo_root)
    mirrored: dict[str, str | None] = {}
    if parent_run_id is None:
        return MlflowSyncResult(dry_run=False, parent_run_id=None, mirrored_run_ids=mirrored)

    for child in plan.child_runs:
        payload = _run_sync_plan_to_payload(child, parent_run_id=parent_run_id)
        mirrored[child.registry_run_id] = mirror_payload_to_mlflow(payload, repo_root=repo_root)
    return MlflowSyncResult(
        dry_run=False,
        parent_run_id=parent_run_id,
        mirrored_run_ids=mirrored,
    )


def filter_registry_entries(
    entries: Sequence[RunRegistryEntry],
    *,
    since_date: str | None = None,
    run_ids: Iterable[str] = (),
) -> list[RunRegistryEntry]:
    """Return registry entries selected by run id and/or ISO date."""

    run_id_set = set(run_ids)
    threshold = _parse_since_date(since_date)
    selected: list[RunRegistryEntry] = []
    for entry in entries:
        if run_id_set and entry.run_id not in run_id_set:
            continue
        if threshold is not None and date.fromisoformat(entry.date) < threshold:
            continue
        selected.append(entry)
    return selected


def build_run_sync_plan(
    entry: RunRegistryEntry,
    *,
    repo_root: Path,
    include_large_artifacts: bool = False,
) -> MlflowRunSyncPlan:
    """Return the dry-run MLflow payload and artifact actions for one entry."""

    task = infer_task(entry)
    artifact_plan = tuple(
        classify_artifact(
            path,
            repo_root=repo_root,
            restricted_surface=_restricted_surface(entry),
            include_large_artifacts=include_large_artifacts,
        )
        for path in entry.artifact_paths
    )
    direct_artifacts = tuple(
        Path(item.path) for item in artifact_plan if item.action == "log_artifact"
    )
    artifact_policy = _artifact_policy(artifact_plan, include_large_artifacts)
    payload = registry_entry_to_mlflow_payload(
        entry,
        task=task,
        dataset=infer_dataset(entry),
        artifact_policy=artifact_policy,
    )
    payload = replace(payload, artifact_paths=direct_artifacts)

    return MlflowRunSyncPlan(
        registry_run_id=entry.run_id,
        experiment_name=payload.experiment_name,
        run_name=payload.run_name,
        params=normalized_params(payload),
        metrics=normalized_metrics(payload),
        tags=normalized_tags(payload),
        artifact_policy=artifact_policy,
        artifacts=artifact_plan,
    )


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


def render_sync_plan(plan: RegistryMlflowSyncPlan) -> str:
    """Render a compact human-facing dry-run report."""

    lines = [
        "# MLflow registry sync dry run",
        f"Registry: {plan.registry_path}",
        f"Run index: {plan.run_index_path}",
        f"Runs selected: {plan.selected_run_count}",
        "",
    ]
    for run in plan.runs:
        lines.append(f"- {run.registry_run_id}")
        lines.append(f"  experiment: {run.experiment_name}")
        lines.append(f"  run: {run.run_name}")
        lines.append(f"  artifact_policy: {run.artifact_policy}")
        if run.metrics:
            metric_keys = ", ".join(sorted(run.metrics))
            lines.append(f"  metrics: {metric_keys}")
        for artifact in run.artifacts:
            lines.append(f"  artifact {artifact.action}: {artifact.path} ({artifact.reason})")
    return "\n".join(lines).rstrip() + "\n"


def render_comparison_sync_plan(plan: MlflowComparisonSyncPlan) -> str:
    """Render a compact human-facing parent/child dry-run report."""

    lines = [
        "# MLflow comparison sync dry run",
        f"Comparison: {plan.comparison_id}",
        f"Experiment: {plan.experiment_name}",
        f"Parent run: {plan.parent_run_name}",
        f"Child runs selected: {plan.selected_run_count}",
        f"Parent artifact_policy: {plan.artifact_policy}",
        "",
    ]
    if plan.parent_metrics:
        metric_keys = ", ".join(sorted(plan.parent_metrics))
        lines.append(f"Parent metrics: {metric_keys}")
    for artifact in plan.artifacts:
        lines.append(f"Parent artifact {artifact.action}: {artifact.path} ({artifact.reason})")
    if plan.artifacts:
        lines.append("")
    for child in plan.child_runs:
        lines.append(f"- child {child.registry_run_id}")
        lines.append(f"  experiment: {child.experiment_name}")
        lines.append(f"  run: {child.run_name}")
        lines.append(f"  artifact_policy: {child.artifact_policy}")
        if child.metrics:
            metric_keys = ", ".join(sorted(child.metrics))
            lines.append(f"  metrics: {metric_keys}")
        for artifact in child.artifacts:
            lines.append(f"  artifact {artifact.action}: {artifact.path} ({artifact.reason})")
    return "\n".join(lines).rstrip() + "\n"


def render_sync_result(result: MlflowSyncResult) -> str:
    """Render the result of a real MLflow sync."""

    lines = ["# MLflow sync result", f"Dry run: {str(result.dry_run).lower()}"]
    if result.parent_run_id is not None:
        lines.append(f"Parent MLflow run id: {result.parent_run_id}")
    for registry_run_id, mlflow_run_id in result.mirrored_run_ids.items():
        lines.append(f"- {registry_run_id}: {mlflow_run_id or 'not mirrored'}")
    return "\n".join(lines).rstrip() + "\n"


def plan_to_json(plan: RegistryMlflowSyncPlan | MlflowComparisonSyncPlan) -> str:
    """Serialize a dry-run plan as deterministic JSON."""

    return json.dumps(asdict(plan), indent=2, sort_keys=True)


def result_to_json(result: MlflowSyncResult) -> str:
    """Serialize a sync result as deterministic JSON."""

    return json.dumps(asdict(result), indent=2, sort_keys=True)


def main(argv: Sequence[str] | None = None) -> None:
    """CLI entry point for dry-run registry-to-MLflow sync planning."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("--run-index", type=Path, default=DEFAULT_RUN_INDEX_PATH)
    parser.add_argument("--since-date", help="Only include registry rows on or after YYYY-MM-DD")
    parser.add_argument("--run-id", action="append", default=[], help="Registry run id to include")
    parser.add_argument(
        "--same-core-dev140-group",
        action="store_true",
        help="Mirror the ExECTv2 same-core dev140 model-swap comparison as a parent/child group",
    )
    parser.add_argument(
        "--include-large-artifacts",
        action="store_true",
        help="Plan direct artifact logging for large or row-level unrestricted artifacts",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Accepted for compatibility; this script is dry-run only",
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Actually mirror the planned registry rows to MLflow",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    parser.add_argument("--output-json", type=Path, help="Write the dry-run plan to JSON")
    args = parser.parse_args(argv)

    repo_root = _repo_root()
    registry_path = _resolve_under_repo(args.registry, repo_root=repo_root)
    run_index_path = _resolve_under_repo(args.run_index, repo_root=repo_root)
    entries = load_run_registry(registry_path)
    if args.same_core_dev140_group:
        plan = build_mlflow_comparison_sync_plan(
            entries,
            repo_root=repo_root,
            comparison_id=SAME_CORE_DEV140_COMPARISON_ID,
            child_run_ids=SAME_CORE_DEV140_RUN_IDS,
            parent_artifact_paths=SAME_CORE_DEV140_PARENT_ARTIFACTS,
            include_large_artifacts=args.include_large_artifacts,
        )
        plan = replace(plan, dry_run=not args.sync)
    else:
        plan = build_registry_mlflow_sync_plan(
            entries,
            repo_root=repo_root,
            registry_path=registry_path,
            run_index_path=run_index_path,
            since_date=args.since_date,
            run_ids=args.run_id,
            include_large_artifacts=args.include_large_artifacts,
        )
        plan = replace(plan, dry_run=not args.sync)
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(plan_to_json(plan) + "\n", encoding="utf-8")
    if args.sync:
        result = (
            sync_comparison_plan_to_mlflow(plan, repo_root=repo_root)
            if isinstance(plan, MlflowComparisonSyncPlan)
            else sync_registry_plan_to_mlflow(plan, repo_root=repo_root)
        )
        print(result_to_json(result) if args.json else render_sync_result(result), end="")
        return
    rendered_plan = (
        render_comparison_sync_plan(plan)
        if isinstance(plan, MlflowComparisonSyncPlan)
        else render_sync_plan(plan)
    )
    print(plan_to_json(plan) if args.json else rendered_plan, end="")


def _artifact_policy(
    artifacts: Sequence[ArtifactSyncPlan],
    include_large_artifacts: bool,
) -> str:
    if include_large_artifacts:
        return "full_artifacts"
    if any(artifact.action == "log_artifact" for artifact in artifacts):
        return "selected_artifacts"
    return "summary_only"


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
            run.metrics.get("parse_schema_failures", 0.0)
            + run.metrics.get("parse_failures", 0.0)
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


def _restricted_surface(entry: RunRegistryEntry) -> bool:
    split = entry.split.lower()
    return "full200" in split or "test" in split or "holdout" in split


def _parse_since_date(value: str | None) -> date | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("--since-date must use YYYY-MM-DD format") from exc


def _resolve_under_repo(path: Path, *, repo_root: Path) -> Path:
    return path if path.is_absolute() else repo_root / path


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("Could not locate repository root")


if __name__ == "__main__":
    main()
