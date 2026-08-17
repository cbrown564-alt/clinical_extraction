from __future__ import annotations

import hashlib
from copy import deepcopy
from pathlib import Path

import pytest

from clinical_extraction.core.retained_evidence import (
    _validate_architecture_freeze,
    _validate_artifact,
    is_content_addressed_retained_path,
    load_retained_evidence_manifest,
    validate_retained_evidence_manifest,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "experiments" / "retained_evidence_manifest.json"
REGISTRY = ROOT / "experiments" / "registry.jsonl"

pytestmark = pytest.mark.local_corpus


def test_committed_retained_evidence_manifest_is_valid() -> None:
    validate_retained_evidence_manifest(
        load_retained_evidence_manifest(MANIFEST),
        repo_root=ROOT,
        registry_path=REGISTRY,
    )


def test_content_addressed_paths_are_sealed_results_and_splits() -> None:
    assert is_content_addressed_retained_path(
        "experiments/example_rows.jsonl", retrieval="git_path"
    )
    assert is_content_addressed_retained_path(
        "experiments/example_report.json", retrieval="git_path"
    )
    assert is_content_addressed_retained_path(
        "data/ExECTv2 (2025)/splits/exectv2_split_v1.json", retrieval="git_path"
    )
    assert is_content_addressed_retained_path(
        "experiments/large_rows.jsonl", retrieval="git_lfs"
    )
    assert not is_content_addressed_retained_path(
        "configs/exectv2/finding_assembly/example.yaml", retrieval="git_path"
    )
    assert not is_content_addressed_retained_path(
        "src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/scoring/match.py",
        retrieval="git_path",
    )
    assert not is_content_addressed_retained_path(
        ".github/workflows/ci.yml", retrieval="git_path"
    )
    assert not is_content_addressed_retained_path(
        "docs/canon/10_paper_provenance.md", retrieval="git_path"
    )
    assert not is_content_addressed_retained_path(
        "pyproject.toml", retrieval="git_path"
    )


def test_retained_evidence_manifest_detects_hash_drift(tmp_path: Path) -> None:
    artifact = tmp_path / "experiments" / "artifact.jsonl"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("{}\n", encoding="utf-8")
    manifest = deepcopy(load_retained_evidence_manifest(MANIFEST))
    first = manifest["reference_cells"][0]
    first["artifacts"] = [
        {
            "path": "experiments/artifact.jsonl",
            "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
            "bytes": artifact.stat().st_size + 1,
            "retrieval": "git_path",
        }
    ]

    with pytest.raises(ValueError, match="hash or size drift"):
        validate_retained_evidence_manifest(
            manifest,
            repo_root=tmp_path,
            registry_path=REGISTRY,
        )


def test_living_artifact_hash_drift_is_ignored(tmp_path: Path) -> None:
    path = tmp_path / "configs" / "live.yaml"
    path.parent.mkdir(parents=True)
    path.write_text("views:\n  - post_lens\n", encoding="utf-8")
    _validate_artifact(
        {
            "path": "configs/live.yaml",
            "sha256": "0" * 64,
            "bytes": 1,
            "retrieval": "git_path",
        },
        record_id="example",
        repo_root=tmp_path,
        seen_artifacts={},
    )


def test_living_artifact_without_hash_is_presence_only(tmp_path: Path) -> None:
    path = tmp_path / "docs" / "note.md"
    path.parent.mkdir(parents=True)
    path.write_text("note\n", encoding="utf-8")
    _validate_artifact(
        {"path": "docs/note.md", "retrieval": "git_path"},
        record_id="example",
        repo_root=tmp_path,
        seen_artifacts={},
    )


def test_missing_living_artifact_still_fails(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="retained artifact is missing"):
        _validate_artifact(
            {"path": "configs/missing.yaml", "retrieval": "git_path"},
            record_id="example",
            repo_root=tmp_path,
            seen_artifacts={},
        )


def test_living_freeze_policy_hash_drift_is_ignored(tmp_path: Path) -> None:
    manifest = load_retained_evidence_manifest(MANIFEST)
    freeze = deepcopy(manifest["architecture_freeze"])
    policy_root = tmp_path
    for policy in freeze["policy_files"]:
        path = policy_root / policy["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("changed\n", encoding="utf-8")
        if is_content_addressed_retained_path(policy["path"], retrieval="git_path"):
            policy["sha256"] = hashlib.sha256(b"changed\n").hexdigest()
            policy["bytes"] = len("changed\n")
        else:
            policy["sha256"] = "0" * 64
            policy["bytes"] = 1
    _validate_architecture_freeze(
        freeze,
        reference_cell_ids=set(freeze["reference_cell_ids"]),
        repo_root=policy_root,
    )


def test_architecture_freeze_covers_every_reference_cell_and_policy_role() -> None:
    manifest = load_retained_evidence_manifest(MANIFEST)
    freeze = manifest["architecture_freeze"]

    assert set(freeze["reference_cell_ids"]) == {
        record["id"] for record in manifest["reference_cells"]
    }
    assert {policy["role"] for policy in freeze["policy_files"]} == {
        "dependency",
        "model",
        "prompt",
        "quality",
        "repair",
        "scorer",
        "split",
        "split_runbook",
    }
    assert freeze["freeze_id"] == "retained_comparison_architecture_20260816"
    assert (
        freeze["model_policy"]["comparison_roster_status"]
        == "six_of_six_current_stack_retained"
    )


def test_hybrid_reference_uses_current_stack_primary_fills() -> None:
    manifest = load_retained_evidence_manifest(MANIFEST)
    reference = next(
        record
        for record in manifest["reference_cells"]
        if record["id"] == "exectv2_hybrid_reference"
    )
    artifact_paths = {artifact["path"] for artifact in reference["artifacts"]}
    assert reference["verification"]["replay"] == "current_stack_primary"
    assert "experiments/current_stack/latest/fills.json" in artifact_paths
    assert "experiments/current_stack/SOURCES.json" in artifact_paths
    assert not any(
        path.startswith("experiments/") and ("v08" in path or "2call_no_sf" in path)
        for path in artifact_paths
    )


def test_retained_manifest_selects_both_six_model_panels() -> None:
    manifest = load_retained_evidence_manifest(MANIFEST)
    packages = {record["id"]: record for record in manifest["evidence_packages"]}
    assert packages["exectv2_fixed_six_model_panel_subject"]["result_summary"][
        "local_conditions_retained_at_equal_status"
    ] is True
    assert packages["gan2026_matched_six_model_panel_subject"]["result_summary"][
        "local_conditions_retained_at_equal_status"
    ] is True


def test_retained_evidence_manifest_requires_complete_two_by_three_matrix() -> None:
    manifest = deepcopy(load_retained_evidence_manifest(MANIFEST))
    manifest["reference_cells"] = manifest["reference_cells"][:-1]

    with pytest.raises(ValueError, match="exactly one record"):
        validate_retained_evidence_manifest(
            manifest,
            repo_root=ROOT,
            registry_path=REGISTRY,
        )
