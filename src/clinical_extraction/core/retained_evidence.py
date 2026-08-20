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
_FREEZE_REQUIRED_FIELDS = {
    "freeze_id",
    "created_date",
    "status",
    "source_commit",
    "source_commit_scope",
    "python_version",
    "mutation_policy",
    "reference_cell_ids",
    "policy_files",
    "model_policy",
    "execution_policy",
}
_FREEZE_POLICY_ROLES = {
    "dependency",
    "model",
    "prompt",
    "quality",
    "repair",
    "scorer",
    "split",
    "split_runbook",
}
_TEXT_ARTIFACT_SUFFIXES = {
    ".json",
    ".jsonl",
    ".lock",
    ".md",
    ".py",
    ".txt",
    ".toml",
    ".yaml",
    ".yml",
}
_SEALED_RESULT_ROOTS = {"experiments"}
_SEALED_RESULT_SUFFIXES = {".json", ".jsonl"}
_SPLIT_MANIFEST_PARENT = "splits"
_SPLIT_MANIFEST_ROOT = "data"


def is_content_addressed_retained_path(
    path_text: str, *, retrieval: str | None = None
) -> bool:
    """Return whether always-on validation hashes this retained path.

    Content-addressed files are sealed result artifacts and split manifests.
    Living source, configs, prompts, docs, and CI files are path-presence only.
    """

    if retrieval == "git_lfs":
        return True
    relative = Path(path_text)
    suffix = relative.suffix.lower()
    parts = relative.parts
    if not parts or parts[0] == "..":
        return False
    if suffix == ".jsonl":
        return True
    if (
        suffix == ".json"
        and parts[0] == _SPLIT_MANIFEST_ROOT
        and _SPLIT_MANIFEST_PARENT in parts
    ):
        return True
    return parts[0] in _SEALED_RESULT_ROOTS and suffix in _SEALED_RESULT_SUFFIXES


def load_retained_evidence_manifest(path: Path) -> Mapping[str, Any]:
    """Load a retained-evidence manifest as a JSON object."""

    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise ValueError("retained-evidence manifest must be a JSON object")
    return value


def validate_retained_evidence_manifest(
    manifest: Mapping[str, Any], *, repo_root: Path, registry_path: Path
) -> None:
    """Validate reference-cell coverage, provenance fields, and sealed hashes."""

    if manifest.get("schema_version") != "retained-evidence-v3":
        raise ValueError("schema_version must be retained-evidence-v3")

    reference_cells = _records(manifest, "reference_cells")
    evidence_packages = _records(manifest, "evidence_packages")
    expected_cells = {(task, family) for task in _TASKS for family in _FAMILIES}
    actual_cells = {
        (record.get("task"), record.get("architecture_family")) for record in reference_cells
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

    _validate_architecture_freeze(
        manifest.get("architecture_freeze"),
        reference_cell_ids={_nonempty_text(record, "id") for record in reference_cells},
        repo_root=repo_root,
    )


def _validate_architecture_freeze(
    value: object, *, reference_cell_ids: set[str], repo_root: Path
) -> None:
    if not isinstance(value, Mapping):
        raise ValueError("architecture_freeze must be an object")
    missing = sorted(_FREEZE_REQUIRED_FIELDS - value.keys())
    if missing:
        raise ValueError(f"architecture_freeze is missing fields: {', '.join(missing)}")

    for field in (
        "freeze_id",
        "created_date",
        "status",
        "source_commit_scope",
        "python_version",
        "mutation_policy",
    ):
        _nonempty_text(value, field)
    if value.get("status") != "frozen_for_new_evidence":
        raise ValueError("architecture_freeze.status must be frozen_for_new_evidence")

    source_commit = _nonempty_text(value, "source_commit")
    if len(source_commit) != 40 or any(
        character not in "0123456789abcdef" for character in source_commit
    ):
        raise ValueError("architecture_freeze.source_commit must be a full Git commit id")

    frozen_ids = value.get("reference_cell_ids")
    if not isinstance(frozen_ids, Sequence) or isinstance(frozen_ids, (str, bytes)):
        raise ValueError("architecture_freeze.reference_cell_ids must be an array")
    if set(frozen_ids) != reference_cell_ids or len(frozen_ids) != len(reference_cell_ids):
        raise ValueError("architecture_freeze.reference_cell_ids must match reference_cells")

    policy_files = value.get("policy_files")
    if not isinstance(policy_files, Sequence) or isinstance(policy_files, (str, bytes)):
        raise ValueError("architecture_freeze.policy_files must be an array")
    roles: set[str] = set()
    paths: set[str] = set()
    for policy in policy_files:
        if not isinstance(policy, Mapping):
            raise ValueError("architecture_freeze policy file must be an object")
        role = _nonempty_text(policy, "role")
        roles.add(role)
        path_text = _nonempty_text(policy, "path")
        if path_text in paths:
            raise ValueError(f"duplicate frozen policy path: {path_text}")
        paths.add(path_text)
        path = _repo_file(repo_root, path_text, context="frozen policy")
        if not path.is_file():
            raise ValueError(f"frozen policy path is missing: {path_text}")
        if is_content_addressed_retained_path(path_text, retrieval="git_path"):
            digest = _nonempty_text(policy, "sha256")
            size = policy.get("bytes")
            if len(digest) != 64 or any(
                character not in "0123456789abcdef" for character in digest
            ):
                raise ValueError(f"invalid frozen policy sha256: {path_text}")
            if not isinstance(size, int) or isinstance(size, bool) or size < 0:
                raise ValueError(f"invalid frozen policy byte size: {path_text}")
            if _artifact_fingerprint(path) != (digest, size):
                raise ValueError(f"frozen policy hash or size drift: {path_text}")
    if roles != _FREEZE_POLICY_ROLES:
        raise ValueError("architecture_freeze.policy_files must cover every policy role")

    model_policy = value.get("model_policy")
    if not isinstance(model_policy, Mapping):
        raise ValueError("architecture_freeze.model_policy must be an object")
    runtime_ids = model_policy.get("retained_runtime_ids")
    if not isinstance(runtime_ids, Sequence) or isinstance(runtime_ids, (str, bytes)):
        raise ValueError("model_policy.retained_runtime_ids must be an array")
    if not runtime_ids or any(not isinstance(item, str) or not item for item in runtime_ids):
        raise ValueError("model_policy.retained_runtime_ids must contain exact identifiers")
    _nonempty_text(model_policy, "comparison_roster_status")
    _nonempty_text(model_policy, "new_runtime_rule")
    _nonempty_text(model_policy, "route_policy")

    execution_policy = value.get("execution_policy")
    if not isinstance(execution_policy, Mapping):
        raise ValueError("architecture_freeze.execution_policy must be an object")
    _nonempty_text(execution_policy, "model_calls")
    commands = execution_policy.get("required_commands")
    if not isinstance(commands, Sequence) or isinstance(commands, (str, bytes)):
        raise ValueError("execution_policy.required_commands must be an array")
    if not commands or any(not isinstance(item, str) or not item for item in commands):
        raise ValueError("execution_policy.required_commands must contain commands")


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
    required = _REQUIRED_RECORD_FIELDS | (_REQUIRED_REFERENCE_FIELDS if reference_cell else set())
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
        _validate_verification(record.get("verification"), record_id=record_id, repo_root=repo_root)


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
    for path_field in ("path",):
        if path_field not in required_inputs:
            continue
        path_text = _nonempty_text(inputs, path_field)
        path = _repo_file(repo_root, path_text, context="verification input")
        if not path.is_file():
            raise ValueError(
                f"verification input is missing in {record_id}: {path_text}"
            )
    expected = value.get("expected")
    if not isinstance(expected, Mapping) or not expected:
        raise ValueError(f"verification.expected in {record_id} must be a non-empty object")
    for metric, expected_value in expected.items():
        if not isinstance(metric, str) or not metric:
            raise ValueError(f"verification.expected in {record_id} has an invalid metric")
        if not isinstance(expected_value, (int, float)) or isinstance(expected_value, bool):
            raise ValueError(f"verification.expected.{metric} in {record_id} must be numeric")


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
    retrieval = artifact.get("retrieval")
    if retrieval not in {"git_path", "git_lfs"}:
        raise ValueError(f"artifact retrieval in {record_id} must be git_path or git_lfs")

    path = _repo_file(repo_root, path_text, context="artifact")
    if not path.is_file():
        raise ValueError(f"retained artifact is missing: {path_text}")

    content_addressed = is_content_addressed_retained_path(path_text, retrieval=retrieval)
    expected: tuple[str, int] | None = None
    if content_addressed:
        digest = _nonempty_text(artifact, "sha256")
        size = artifact.get("bytes")
        if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
            raise ValueError(f"invalid sha256 for {path_text}")
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            raise ValueError(f"invalid byte size for {path_text}")
        expected = (digest, size)
        if _artifact_fingerprint(path) != expected:
            raise ValueError(f"retained artifact hash or size drift: {path_text}")
    if retrieval == "git_lfs":
        lfs_oid = artifact.get("lfs_oid")
        if (
            not isinstance(lfs_oid, str)
            or not lfs_oid.startswith("sha256:")
            or len(lfs_oid) != 71
            or any(char not in "0123456789abcdef" for char in lfs_oid[7:])
        ):
            raise ValueError(f"invalid LFS object id: {path_text}")
    if expected is not None:
        prior = seen_artifacts.get(path_text)
        if prior is not None and prior != expected:
            raise ValueError(f"conflicting retained metadata for {path_text}")
        seen_artifacts[path_text] = expected


def _artifact_fingerprint(path: Path) -> tuple[str, int]:
    """Return a platform-stable fingerprint for retained artifact content."""

    content = path.read_bytes()
    if path.suffix.lower() in _TEXT_ARTIFACT_SUFFIXES:
        content = content.replace(b"\r\n", b"\n")
    return hashlib.sha256(content).hexdigest(), len(content)


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
