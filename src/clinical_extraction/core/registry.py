"""Run-registry records for experiment artifact indexing."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, cast

RunDecision = Literal[
    "promote",
    "promote_to_phase3_report",
    "promote_hybrid_structured_events_direction",
    "revise",
    "reject",
    "inform_phase3",
    "phase3_complete_gpt41mini",
    "inform_phase4",
    "phase4_complete",
    "inform_phase7",
    "reliability_scorecard",
    "inform_architecture_loop",
    "clinical_recovery_reporting",
    "superseded",
    "historical",
    "calibration_measure_val_to_test_gap",
]

ReplayStatus = Literal[
    "live",
    "native_run_split",
    "cache_first",
    "schema_replay",
    "saved_output_replay",
    "assessment_stage_only",
    "analysis_only",
]

ComparisonRole = Literal["control", "diagnostic"]
ArchitectureFamily = Literal["rules_only", "hybrid", "llm_only"]
RegistryRole = Literal[
    "architecture_comparator",
    "model_family_variant",
    "holdout_anchor",
    "component_ladder",
    "reliability_scorecard",
    "negative_attribution",
    "historical_lineage",
]

MetricValue = int | float | str | None | list[int | float | str | None]

RUN_DECISIONS: frozenset[RunDecision] = frozenset(
    (
        "promote",
        "promote_to_phase3_report",
        "promote_hybrid_structured_events_direction",
        "revise",
        "reject",
        "inform_phase3",
        "phase3_complete_gpt41mini",
        "inform_phase4",
        "phase4_complete",
        "inform_phase7",
        "reliability_scorecard",
        "inform_architecture_loop",
        "clinical_recovery_reporting",
        "superseded",
        "historical",
        "calibration_measure_val_to_test_gap",
    )
)
REPLAY_STATUSES: frozenset[ReplayStatus] = frozenset(
    (
        "live",
        "native_run_split",
        "cache_first",
        "schema_replay",
        "saved_output_replay",
        "assessment_stage_only",
        "analysis_only",
    )
)
REGISTRY_ROLES: frozenset[RegistryRole] = frozenset(
    (
        "architecture_comparator",
        "model_family_variant",
        "holdout_anchor",
        "component_ladder",
        "reliability_scorecard",
        "negative_attribution",
        "historical_lineage",
    )
)


@dataclass(frozen=True)
class RunRegistryEntry:
    """Durable index row for a run or analysis artifact family."""

    run_id: str
    artifact_paths: tuple[str, ...]
    date: str
    pipeline_family: str
    split: str
    row_count: int
    model: str
    model_role: str
    mode: str
    replay_status: ReplayStatus
    decision: RunDecision
    primary_metrics: Mapping[str, MetricValue] = field(default_factory=dict)
    repair_mode: str | None = None
    cache_reuse_source: str | None = None
    evidence_validity: str | None = None
    supersedes: tuple[str, ...] = ()
    superseded_by: str | None = None
    claim_language_notes: str = ""
    surface_as_architecture: bool = False
    display_label: str | None = None
    architecture_family: ArchitectureFamily | None = None
    comparison_role: ComparisonRole | None = None
    registry_roles: tuple[RegistryRole, ...] = ()

    def to_json_record(self) -> dict[str, Any]:
        """Return a deterministic JSON-compatible registry record."""

        self.validate()
        record: dict[str, Any] = {
            "run_id": self.run_id,
            "artifact_paths": list(self.artifact_paths),
            "date": self.date,
            "pipeline_family": self.pipeline_family,
            "split": self.split,
            "row_count": self.row_count,
            "model": self.model,
            "model_role": self.model_role,
            "mode": self.mode,
            "replay_status": self.replay_status,
            "repair_mode": self.repair_mode,
            "cache_reuse_source": self.cache_reuse_source,
            "primary_metrics": dict(self.primary_metrics),
            "evidence_validity": self.evidence_validity,
            "decision": self.decision,
            "supersedes": list(self.supersedes),
            "superseded_by": self.superseded_by,
            "claim_language_notes": self.claim_language_notes,
            "surface_as_architecture": self.surface_as_architecture,
            "display_label": self.display_label,
            "architecture_family": self.architecture_family,
            "comparison_role": self.comparison_role,
        }
        if self.registry_roles:
            record["registry_roles"] = list(self.registry_roles)
        return record

    def validate(self) -> None:
        """Validate fields that protect experiment traceability."""

        required_text = {
            "run_id": self.run_id,
            "date": self.date,
            "pipeline_family": self.pipeline_family,
            "split": self.split,
            "model": self.model,
            "model_role": self.model_role,
            "mode": self.mode,
        }
        missing = [name for name, value in required_text.items() if not value.strip()]
        if missing:
            raise ValueError(f"registry entry missing required field(s): {', '.join(missing)}")
        if not self.artifact_paths:
            raise ValueError("registry entry must reference at least one artifact path")
        if self.row_count < 0:
            raise ValueError("registry entry row_count must be non-negative")
        if self.decision == "superseded" and not self.superseded_by:
            raise ValueError("superseded registry entries must name superseded_by")


def registry_entry_from_json_record(record: Mapping[str, Any]) -> RunRegistryEntry:
    """Parse one JSON registry record into a typed entry."""

    artifact_paths = _string_tuple(record.get("artifact_paths"), field_name="artifact_paths")
    supersedes = _string_tuple(record.get("supersedes", ()), field_name="supersedes")
    entry = RunRegistryEntry(
        run_id=_required_str(record, "run_id"),
        artifact_paths=artifact_paths,
        date=_required_str(record, "date"),
        pipeline_family=_required_str(record, "pipeline_family"),
        split=_required_str(record, "split"),
        row_count=_required_int(record, "row_count"),
        model=_required_str(record, "model"),
        model_role=_required_str(record, "model_role"),
        mode=_required_str(record, "mode"),
        replay_status=_replay_status(record),
        repair_mode=_optional_str(record.get("repair_mode")),
        cache_reuse_source=_optional_str(record.get("cache_reuse_source")),
        primary_metrics=_metrics(record.get("primary_metrics", {})),
        evidence_validity=_optional_str(record.get("evidence_validity")),
        decision=_run_decision(record),
        supersedes=supersedes,
        superseded_by=_optional_str(record.get("superseded_by")),
        claim_language_notes=_optional_str(record.get("claim_language_notes")) or "",
        surface_as_architecture=_optional_bool(record.get("surface_as_architecture")),
        display_label=_optional_str(record.get("display_label")),
        architecture_family=_optional_architecture_family(record.get("architecture_family")),
        comparison_role=_optional_comparison_role(record.get("comparison_role")),
        registry_roles=_registry_roles(record.get("registry_roles")),
    )
    entry.validate()
    return entry


def load_run_registry(path: Path) -> list[RunRegistryEntry]:
    """Load newline-delimited run-registry entries."""

    if not path.exists():
        return []
    entries: list[RunRegistryEntry] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
            entries.append(registry_entry_from_json_record(record))
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ValueError(f"invalid registry record at {path}:{line_number}: {exc}") from exc
    return entries


def write_run_registry(entries: Sequence[RunRegistryEntry], path: Path) -> None:
    """Write newline-delimited run-registry entries sorted by run id."""

    run_ids = [entry.run_id for entry in entries]
    duplicates = sorted({run_id for run_id in run_ids if run_ids.count(run_id) > 1})
    if duplicates:
        raise ValueError(f"duplicate run_id(s): {', '.join(duplicates)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = sorted(entries, key=lambda entry: entry.run_id)
    lines = [
        json.dumps(entry.to_json_record(), ensure_ascii=False, sort_keys=True) for entry in ordered
    ]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def validate_run_registry_artifacts(
    entries: Sequence[RunRegistryEntry], *, repo_root: Path
) -> None:
    """Check that every registry artifact path exists under the repository root."""

    missing: list[str] = []
    invalid: list[str] = []
    root = repo_root.resolve()
    for entry in entries:
        for artifact_path in entry.artifact_paths:
            path = Path(artifact_path)
            if path.is_absolute() or ".." in path.parts:
                invalid.append(f"{entry.run_id}: {artifact_path}")
                continue
            resolved = (root / path).resolve()
            if root not in (resolved, *resolved.parents):
                invalid.append(f"{entry.run_id}: {artifact_path}")
                continue
            if not resolved.exists():
                missing.append(f"{entry.run_id}: {artifact_path}")
    if invalid:
        raise ValueError(f"invalid artifact path(s): {', '.join(invalid)}")
    if missing:
        raise ValueError(f"missing artifact path(s): {', '.join(missing)}")


def _required_str(record: Mapping[str, Any], field_name: str) -> str:
    value = record.get(field_name)
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    return value


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("optional text fields must be strings or null")
    return value


def _optional_bool(value: Any) -> bool:
    if value is None:
        return False
    if not isinstance(value, bool):
        raise ValueError("surface_as_architecture must be a boolean")
    return value


def _optional_architecture_family(value: Any) -> ArchitectureFamily | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("architecture_family must be a string or null")
    allowed: frozenset[str] = frozenset(("rules_only", "hybrid", "llm_only"))
    if value not in allowed:
        raise ValueError(f"architecture_family must be one of: {', '.join(sorted(allowed))}")
    return cast(ArchitectureFamily, value)


def _optional_comparison_role(value: Any) -> ComparisonRole | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("comparison_role must be a string or null")
    allowed: frozenset[str] = frozenset(("control", "diagnostic"))
    if value not in allowed:
        raise ValueError(f"comparison_role must be one of: {', '.join(sorted(allowed))}")
    return cast(ComparisonRole, value)


def _registry_roles(value: Any) -> tuple[RegistryRole, ...]:
    if value is None:
        return ()
    if not isinstance(value, list | tuple):
        raise ValueError("registry_roles must be a list of controlled role strings")
    if not all(isinstance(item, str) and item in REGISTRY_ROLES for item in value):
        allowed = ", ".join(sorted(REGISTRY_ROLES))
        raise ValueError(f"registry_roles must contain only: {allowed}")
    return tuple(cast(RegistryRole, item) for item in value)


def _required_int(record: Mapping[str, Any], field_name: str) -> int:
    value = record.get(field_name)
    if not isinstance(value, int):
        raise ValueError(f"{field_name} must be an integer")
    return value


def _run_decision(record: Mapping[str, Any]) -> RunDecision:
    value = _required_str(record, "decision")
    if value not in RUN_DECISIONS:
        raise ValueError(f"decision must be one of: {', '.join(sorted(RUN_DECISIONS))}")
    return cast(RunDecision, value)


def _replay_status(record: Mapping[str, Any]) -> ReplayStatus:
    value = _required_str(record, "replay_status")
    if value not in REPLAY_STATUSES:
        raise ValueError(f"replay_status must be one of: {', '.join(sorted(REPLAY_STATUSES))}")
    return cast(ReplayStatus, value)


def _string_tuple(value: Any, *, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, list | tuple):
        raise ValueError(f"{field_name} must be a list of strings")
    if not all(isinstance(item, str) for item in value):
        raise ValueError(f"{field_name} must contain only strings")
    return tuple(value)


def _metrics(value: Any) -> Mapping[str, MetricValue]:
    if not isinstance(value, Mapping):
        raise ValueError("primary_metrics must be an object")
    parsed: dict[str, MetricValue] = {}
    for key, metric in value.items():
        if not isinstance(key, str):
            raise ValueError("primary_metrics keys must be strings")
        if not _is_metric_value(metric):
            raise ValueError(
                "primary_metrics values must be strings, numbers, null, "
                "or flat lists of those values"
            )
        parsed[key] = metric
    return parsed


def _is_metric_value(value: Any) -> bool:
    if value is None or isinstance(value, int | float | str):
        return True
    if isinstance(value, list):
        return all(item is None or isinstance(item, int | float | str) for item in value)
    return False
