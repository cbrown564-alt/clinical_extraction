from __future__ import annotations

import hashlib
from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from clinical_extraction.core.retained_evidence import (
    load_retained_evidence_manifest,
    validate_retained_evidence_manifest,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "experiments" / "retained_evidence_manifest.json"
REGISTRY = ROOT / "experiments" / "registry.jsonl"


def test_committed_retained_evidence_manifest_is_valid() -> None:
    validate_retained_evidence_manifest(
        load_retained_evidence_manifest(MANIFEST),
        repo_root=ROOT,
        registry_path=REGISTRY,
    )


def test_retained_evidence_manifest_detects_hash_drift(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.json"
    artifact.write_text("{}\n", encoding="utf-8")
    manifest = deepcopy(load_retained_evidence_manifest(MANIFEST))
    first = manifest["reference_cells"][0]
    first["artifacts"] = [
        {
            "path": "artifact.json",
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
    assert (
        freeze["model_policy"]["comparison_roster_status"]
        == "six_of_six_dev140_and_holdout_retained"
    )


def test_hybrid_reference_manifest_keeps_all_finding_assembly_inputs() -> None:
    manifest = load_retained_evidence_manifest(MANIFEST)
    reference = next(
        record
        for record in manifest["reference_cells"]
        if record["id"] == "exectv2_hybrid_reference"
    )
    artifact_paths = {artifact["path"] for artifact in reference["artifacts"]}
    config_path = ROOT / reference["verification"]["inputs"]["path"]
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    replay_inputs = {producer["artifact"] for producer in config["producers"].values()}

    assert replay_inputs <= artifact_paths


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
