"""CLI for registry-to-MLflow sync planning and execution."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path

from clinical_extraction.core.mlflow_registry_sync import (
    build_mlflow_comparison_sync_plan,
    build_registry_mlflow_sync_plan,
    plan_to_json,
    render_sync_plan,
    render_sync_result,
    result_to_json,
    sync_plan_to_mlflow,
)
from clinical_extraction.core.mlflow_sync_types import (
    BACKFILL_SCOPES,
    DEFAULT_REGISTRY_PATH,
    DEFAULT_RUN_INDEX_PATH,
    BackfillScopeName,
    MlflowSyncPlan,
)
from clinical_extraction.core.paths import discover_repo_root, resolve_under_root
from clinical_extraction.core.registry import (
    REGISTRY_ROLES,
    RegistryRole,
    RunRegistryEntry,
    load_run_registry,
)


def main(argv: Sequence[str] | None = None) -> None:
    """CLI entry point for dry-run registry-to-MLflow sync planning."""

    parser = argparse.ArgumentParser(
        description="Dry-run registry-to-MLflow sync planning and optional mirror."
    )
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("--run-index", type=Path, default=DEFAULT_RUN_INDEX_PATH)
    parser.add_argument("--since-date", help="Only include registry rows on or after YYYY-MM-DD")
    parser.add_argument("--run-id", action="append", default=[], help="Registry run id to include")
    parser.add_argument(
        "--backfill-scope",
        choices=tuple(BACKFILL_SCOPES),
        help="Operator-facing backfill preset; see docs/decisions/0036-mlflow-registry-backfill-scope.md",
    )
    parser.add_argument(
        "--registry-role",
        action="append",
        default=[],
        choices=sorted(REGISTRY_ROLES),
        help="Override scope role filter; entry must match at least one listed role",
    )
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

    repo_root = discover_repo_root()
    registry_path = resolve_under_root(args.registry, repo_root=repo_root)
    run_index_path = resolve_under_root(args.run_index, repo_root=repo_root)
    entries = load_run_registry(registry_path)
    plan = build_cli_plan(
        entries,
        repo_root=repo_root,
        registry_path=registry_path,
        run_index_path=run_index_path,
        since_date=args.since_date,
        run_ids=args.run_id,
        registry_roles=args.registry_role,
        backfill_scope=args.backfill_scope,
        include_large_artifacts=args.include_large_artifacts,
        same_core_dev140_group=args.same_core_dev140_group,
        sync=args.sync,
    )
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(plan_to_json(plan) + "\n", encoding="utf-8")
    if args.sync:
        result = sync_plan_to_mlflow(plan, repo_root=repo_root)
        print(result_to_json(result) if args.json else render_sync_result(result), end="")
        return
    print(plan_to_json(plan) if args.json else render_sync_plan(plan), end="")


def build_cli_plan(
    entries: Sequence[RunRegistryEntry],
    *,
    repo_root: Path,
    registry_path: Path,
    run_index_path: Path,
    since_date: str | None,
    run_ids: Sequence[str],
    registry_roles: Sequence[RegistryRole],
    backfill_scope: BackfillScopeName | None,
    include_large_artifacts: bool,
    same_core_dev140_group: bool,
    sync: bool,
) -> MlflowSyncPlan:
    if same_core_dev140_group or backfill_scope == "same_core_dev140":
        from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.mlflow_comparison_groups import (
            SAME_CORE_DEV140_MLFLOW_GROUP,
        )

        group = SAME_CORE_DEV140_MLFLOW_GROUP
        plan = build_mlflow_comparison_sync_plan(
            entries,
            repo_root=repo_root,
            comparison_id=group.comparison_id,
            child_run_ids=group.child_run_ids,
            parent_artifact_paths=group.parent_artifact_paths,
            include_large_artifacts=include_large_artifacts,
        )
    else:
        plan = build_registry_mlflow_sync_plan(
            entries,
            repo_root=repo_root,
            registry_path=registry_path,
            run_index_path=run_index_path,
            since_date=since_date,
            run_ids=run_ids,
            registry_roles=registry_roles,
            backfill_scope=backfill_scope,
            include_large_artifacts=include_large_artifacts,
        )
    return replace(plan, dry_run=not sync)
