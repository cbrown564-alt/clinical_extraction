"""Validation for the small, paper-facing retained-evidence manifest."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.core.registry import load_run_registry

_TASKS = {"exectv2", "gan2026"}
_FAMILIES = {"rules_only", "llm_only", "hybrid"}
_STORY_IDS = {f"S{index}" for index in range(1, 10)}
_CLOSURE_FIELDS = {
    "entrypoints",
    "implementation",
    "scoring",
    "data_contract",
    "configurations",
    "tests",
}
_REPLAY_INPUT_FIELDS = {
    "exectv2_deterministic": {"split"},
    "exectv2_saved_predictions": {"path", "split"},
    "exectv2_finding_assembly": {"path"},
    "gan_saved_comparisons": {"path"},
}
_REQUIRED_RECORD_FIELDS = {
    "id",
    "task",
    "architecture_family",
    "dataset",
    "split_manifest",
    "split",
    "row_count",
    "row_inspection_policy",
    "scorer",
    "model",
    "model_role",
    "prompt_program_version",
    "cache_replay_mode",
    "repair_policy",
    "claim_boundary",
    "story_ids",
    "artifacts",
}
_REQUIRED_REFERENCE_FIELDS = {"closure", "verification"}


def load_retained_evidence_manifest(path: Path) -> Mapping[str, Any]:
    """Load a retained-evidence manifest as a JSON object."""

    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise ValueError("retained-evidence manifest must be a JSON object")
    return value


def validate_retained_evidence_manifest(
    manifest: Mapping[str, Any], *, repo_root: Path, registry_path: Path
) -> None:
    """Validate reference-cell coverage, provenance fields, paths, and hashes."""

    if manifest.get("schema_version") != "retained-evidence-v2":
        raise ValueError("schema_version must be retained-evidence-v2")

    reference_cells = _records(manifest, "reference_cells")
    evidence_packages = _records(manifest, "evidence_packages")
    expected_cells = {(task, family) for task in _TASKS for family in _FAMILIES}
    actual_cells = {
        (record.get("task"), record.get("architecture_family"))
        for record in reference_cells
    }
    if len(reference_cells) != len(expected_cells) or actual_cells != expected_cells:
        raise ValueError(
            "reference_cells must contain exactly one record for each "
            "task × architecture family cell"
        )

    registry = {entry.run_id: entry for entry in load_run_registry(registry_path)}
    seen_ids: set[str] = set()
    seen_artifacts: dict[str, tuple[str, int]] = {}
    for record in reference_cells:
        _validate_record(
            record,
            repo_root=repo_root,
            registry=registry,
            seen_ids=seen_ids,
            seen_artifacts=seen_artifacts,
            reference_cell=True,
        )
    for record in evidence_packages:
        _validate_record(
            record,
            repo_root=repo_root,
            registry=registry,
            seen_ids=seen_ids,
            seen_artifacts=seen_artifacts,
            reference_cell=False,
        )


def _records(manifest: Mapping[str, Any], field: str) -> tuple[Mapping[str, Any], ...]:
    value = manifest.get(field)
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError(f"{field} must be an array")
    records: list[Mapping[str, Any]] = []
    for index, record in enumerate(value):
        if not isinstance(record, Mapping):
            raise ValueError(f"{field}[{index}] must be an object")
        records.append(record)
    return tuple(records)


def _validate_record(
    record: Mapping[str, Any],
    *,
    repo_root: Path,
    registry: Mapping[str, Any],
    seen_ids: set[str],
    seen_artifacts: dict[str, tuple[str, int]],
    reference_cell: bool,
) -> None:
    required = _REQUIRED_RECORD_FIELDS | (
        _REQUIRED_REFERENCE_FIELDS if reference_cell else set()
    )
    missing = sorted(required - record.keys())
    if missing:
        raise ValueError(f"evidence record is missing fields: {', '.join(missing)}")

    record_id = _nonempty_text(record, "id")
    if record_id in seen_ids:
        raise ValueError(f"duplicate evidence record id: {record_id}")
    seen_ids.add(record_id)

    task = _nonempty_text(record, "task")
    if task not in _TASKS and task != "cross_task":
        raise ValueError(f"unsupported task in {record_id}: {task}")
    family = _nonempty_text(record, "architecture_family")
    if family not in _FAMILIES and family != "cross_family":
        raise ValueError(f"unsupported architecture_family in {record_id}: {family}")

    row_count = record.get("row_count")
    if not isinstance(row_count, int) or isinstance(row_count, bool) or row_count < 0:
        raise ValueError(f"row_count in {record_id} must be a non-negative integer")

    story_ids = record.get("story_ids")
    if not isinstance(story_ids, Sequence) or isinstance(story_ids, (str, bytes)):
        raise ValueError(f"story_ids in {record_id} must be an array")
    invalid_story_ids = sorted(set(story_ids) - _STORY_IDS)
    if invalid_story_ids or not story_ids:
        raise ValueError(f"invalid or empty story_ids in {record_id}: {invalid_story_ids}")

    run_id = record.get("run_id")
    if run_id is not None:
        if not isinstance(run_id, str) or not run_id:
            raise ValueError(f"run_id in {record_id} must be non-empty text")
        entry = registry.get(run_id)
        if entry is None:
            raise ValueError(f"run_id in {record_id} is absent from registry: {run_id}")
        if entry.split != record.get("split") or entry.row_count != row_count:
            raise ValueError(f"split or row_count drift for {record_id} versus {run_id}")
        if entry.model != record.get("model"):
            raise ValueError(f"model drift for {record_id} versus {run_id}")

    for field in _REQUIRED_RECORD_FIELDS - {"row_count", "story_ids", "artifacts"}:
        _nonempty_text(record, field)

    artifacts = record.get("artifacts")
    if not isinstance(artifacts, Sequence) or isinstance(artifacts, (str, bytes)):
        raise ValueError(f"artifacts in {record_id} must be an array")
    if not artifacts:
        raise ValueError(f"artifacts in {record_id} must not be empty")
    for artifact in artifacts:
        _validate_artifact(
            artifact,
            record_id=record_id,
            repo_root=repo_root,
            seen_artifacts=seen_artifacts,
        )
    if reference_cell:
        _validate_closure(record.get("closure"), record_id=record_id, repo_root=repo_root)
        _validate_verification(
            record.get("verification"), record_id=record_id, repo_root=repo_root
        )


def _validate_closure(value: object, *, record_id: str, repo_root: Path) -> None:
    if not isinstance(value, Mapping):
        raise ValueError(f"closure in {record_id} must be an object")
    missing = sorted(_CLOSURE_FIELDS - value.keys())
    if missing:
        raise ValueError(f"closure in {record_id} is missing fields: {', '.join(missing)}")
    for field in sorted(_CLOSURE_FIELDS):
        paths = value.get(field)
        if not isinstance(paths, Sequence) or isinstance(paths, (str, bytes)) or not paths:
            raise ValueError(f"closure.{field} in {record_id} must be a non-empty array")
        for path_text in paths:
            if not isinstance(path_text, str) or not path_text.strip():
                raise ValueError(f"closure.{field} in {record_id} contains an invalid path")
            path = _repo_file(repo_root, path_text, context="closure")
            if not path.is_file():
                raise ValueError(f"closure path is missing in {record_id}: {path_text}")


def _validate_verification(value: object, *, record_id: str, repo_root: Path) -> None:
    if not isinstance(value, Mapping):
        raise ValueError(f"verification in {record_id} must be an object")
    replay = _nonempty_text(value, "replay")
    required_inputs = _REPLAY_INPUT_FIELDS.get(replay)
    if required_inputs is None:
        raise ValueError(f"unsupported replay in {record_id}: {replay}")
    inputs = value.get("inputs")
    if not isinstance(inputs, Mapping):
        raise ValueError(f"verification.inputs in {record_id} must be an object")
    missing = sorted(required_inputs - inputs.keys())
    if missing:
        raise ValueError(
            f"verification.inputs in {record_id} is missing fields: {', '.join(missing)}"
        )
    if "split" in required_inputs:
        _nonempty_text(inputs, "split")
    if "path" in required_inputs:
        path_text = _nonempty_text(inputs, "path")
        path = _repo_file(repo_root, path_text, context="verification input")
        if not path.is_file():
            raise ValueError(f"verification input is missing in {record_id}: {path_text}")
    expected = value.get("expected")
    if not isinstance(expected, Mapping) or not expected:
        raise ValueError(f"verification.expected in {record_id} must be a non-empty object")
    for metric, expected_value in expected.items():
        if not isinstance(metric, str) or not metric:
            raise ValueError(f"verification.expected in {record_id} has an invalid metric")
        if not isinstance(expected_value, (int, float)) or isinstance(expected_value, bool):
            raise ValueError(
                f"verification.expected.{metric} in {record_id} must be numeric"
            )


def _validate_artifact(
    artifact: object,
    *,
    record_id: str,
    repo_root: Path,
    seen_artifacts: dict[str, tuple[str, int]],
) -> None:
    if not isinstance(artifact, Mapping):
        raise ValueError(f"artifact in {record_id} must be an object")
    path_text = _nonempty_text(artifact, "path")
    digest = _nonempty_text(artifact, "sha256")
    size = artifact.get("bytes")
    retrieval = artifact.get("retrieval")
    if retrieval != "git_path":
        raise ValueError(f"artifact retrieval in {record_id} must be git_path")
    if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
        raise ValueError(f"invalid sha256 for {path_text}")
    if not isinstance(size, int) or isinstance(size, bool) or size < 0:
        raise ValueError(f"invalid byte size for {path_text}")

    path = _repo_file(repo_root, path_text, context="artifact")
    if not path.is_file():
        raise ValueError(f"retained artifact is missing: {path_text}")

    actual = (hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_size)
    expected = (digest, size)
    if actual != expected:
        raise ValueError(f"retained artifact hash or size drift: {path_text}")
    prior = seen_artifacts.get(path_text)
    if prior is not None and prior != expected:
        raise ValueError(f"conflicting retained metadata for {path_text}")
    seen_artifacts[path_text] = expected


def _nonempty_text(record: Mapping[str, Any], field: str) -> str:
    value = record.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-empty text")
    return value


def _repo_file(repo_root: Path, path_text: str, *, context: str) -> Path:
    relative = Path(path_text)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"{context} path must be repository-relative: {path_text}")
    root = repo_root.resolve()
    path = (root / relative).resolve()
    if root not in (path, *path.parents):
        raise ValueError(f"{context} path escapes repository: {path_text}")
    return path
