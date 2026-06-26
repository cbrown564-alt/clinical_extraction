"""Shared MLflow registry sync plan types and backfill scope presets."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from clinical_extraction.core.registry import RegistryRole

ArtifactAction = Literal["log_artifact", "pointer_only", "skip_invalid", "skip_missing"]

DEFAULT_REGISTRY_PATH = Path("experiments") / "registry.jsonl"
DEFAULT_RUN_INDEX_PATH = Path("experiments") / "RUN_INDEX.md"
ROW_ARTIFACT_SUFFIXES = frozenset((".jsonl", ".csv", ".tsv"))
RESTRICTED_DIRECT_SUFFIXES = frozenset((".md", ".txt"))
LARGE_ARTIFACT_BYTES = 5 * 1024 * 1024

BackfillScopeName = Literal[
    "same_core_dev140",
    "paper_facing",
    "reliability_slice",
    "all_since_2026_06_24",
    "full_registry",
]


@dataclass(frozen=True)
class BackfillScope:
    """Operator-facing MLflow backfill selection."""

    name: BackfillScopeName
    since_date: str | None
    registry_roles: frozenset[RegistryRole] | None
    description: str


BACKFILL_SCOPES: dict[BackfillScopeName, BackfillScope] = {
    "same_core_dev140": BackfillScope(
        name="same_core_dev140",
        since_date=None,
        registry_roles=None,
        description="ExECTv2 same-core dev140 parent/child comparison group only.",
    ),
    "paper_facing": BackfillScope(
        name="paper_facing",
        since_date="2026-06-24",
        registry_roles=frozenset(
            (
                "architecture_comparator",
                "reliability_scorecard",
                "component_ladder",
                "holdout_anchor",
            )
        ),
        description=(
            "Paper-facing reliability, architecture, component, and holdout-anchor "
            "rows since 2026-06-24."
        ),
    ),
    "reliability_slice": BackfillScope(
        name="reliability_slice",
        since_date="2026-06-24",
        registry_roles=frozenset(("architecture_comparator", "reliability_scorecard")),
        description="Reliability scorecards and architecture comparators since 2026-06-24.",
    ),
    "all_since_2026_06_24": BackfillScope(
        name="all_since_2026_06_24",
        since_date="2026-06-24",
        registry_roles=None,
        description="All registry rows on or after 2026-06-24.",
    ),
    "full_registry": BackfillScope(
        name="full_registry",
        since_date=None,
        registry_roles=None,
        description="Entire experiments/registry.jsonl. Explicit opt-in only.",
    ),
}


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
class MlflowParentSyncPlan:
    """Optional parent run for a grouped MLflow comparison sync."""

    comparison_id: str
    experiment_name: str
    run_name: str
    params: dict[str, str]
    metrics: dict[str, float]
    tags: dict[str, str]
    artifact_policy: str
    artifacts: tuple[ArtifactSyncPlan, ...]


@dataclass(frozen=True)
class MlflowSyncPlan:
    """Dry-run or execution plan for registry-to-MLflow sync."""

    dry_run: bool
    selected_run_count: int
    runs: tuple[MlflowRunSyncPlan, ...]
    parent: MlflowParentSyncPlan | None = None
    registry_path: str | None = None
    run_index_path: str | None = None
    backfill_scope: str | None = None
    since_date: str | None = None
    registry_roles: tuple[str, ...] = ()


@dataclass(frozen=True)
class MlflowSyncResult:
    """Result of an actual MLflow mirror invocation."""

    dry_run: bool
    parent_run_id: str | None
    mirrored_run_ids: dict[str, str | None]
