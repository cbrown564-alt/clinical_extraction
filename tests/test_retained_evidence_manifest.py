from __future__ import annotations

import hashlib
from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from clinical_extraction.core.retained_evidence import (
    _artifact_fingerprint,
    load_retained_evidence_manifest,
    validate_retained_evidence_manifest,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    run_all9_on_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    deterministic_all9_scorecard,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "experiments" / "retained_evidence_manifest.json"
REGISTRY = ROOT / "experiments" / "registry.jsonl"


def test_retained_text_artifact_fingerprint_is_line_ending_stable(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.jsonl"
    artifact.write_bytes(b'{"id": 1}\r\n{"id": 2}\r\n')
    canonical = b'{"id": 1}\n{"id": 2}\n'

    assert _artifact_fingerprint(artifact) == (
        hashlib.sha256(canonical).hexdigest(),
        len(canonical),
    )


def test_committed_retained_evidence_manifest_is_valid() -> None:
    validate_retained_evidence_manifest(
        load_retained_evidence_manifest(MANIFEST),
        repo_root=ROOT,
        registry_path=REGISTRY,
    )


def test_model_transfer_package_keeps_permitted_dev_replay_inputs() -> None:
    manifest = load_retained_evidence_manifest(MANIFEST)
    package = next(
        record
        for record in manifest["evidence_packages"]
        if record["id"] == "exectv2_model_transfer_subject"
    )
    artifact_paths = {artifact["path"] for artifact in package["artifacts"]}

    expected = {
        "scripts/run_exectv2_2call_model_swap.py",
        "configs/exectv2/model_swap/exectv2_2call_no_sf_adjudicator_gpt41mini_dev140.json",
        "configs/exectv2/model_swap/exectv2_2call_no_sf_adjudicator_deepseek_dev140.json",
        "configs/exectv2/model_swap/exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_dev140.json",
        "experiments/exectv2_2call_no_sf_adjudicator_gpt41mini_dev140_20260625.json",
        "experiments/exectv2_2call_no_sf_adjudicator_gpt41mini_dev140_20260625.jsonl",
        "experiments/exectv2_2call_no_sf_adjudicator_deepseek_dev140_20260625.json",
        "experiments/exectv2_2call_no_sf_adjudicator_deepseek_dev140_20260625.jsonl",
        "experiments/exectv2_2call_no_sf_adjudicator_qwen36_dev140_20260625.json",
        "experiments/exectv2_2call_no_sf_adjudicator_qwen36_dev140_20260625.jsonl",
        "experiments/exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_dev140_20260625.json",
        "experiments/exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_dev140_20260625.jsonl",
    }
    assert expected <= artifact_paths


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
    replay_inputs = {
        producer["artifact"] for producer in config["producers"].values()
    }

    assert replay_inputs <= artifact_paths


def test_retained_evidence_manifest_requires_complete_two_by_three_matrix(
    tmp_path: Path,
) -> None:
    manifest = deepcopy(load_retained_evidence_manifest(MANIFEST))
    manifest["reference_cells"] = manifest["reference_cells"][:-1]

    with pytest.raises(ValueError, match="exactly one record"):
        validate_retained_evidence_manifest(
            manifest,
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


def test_retained_evidence_manifest_accepts_content_addressed_git_lfs_artifact(
) -> None:
    manifest = deepcopy(load_retained_evidence_manifest(MANIFEST))
    artifact = manifest["reference_cells"][0]["artifacts"][0]
    artifact["retrieval"] = "git_lfs"
    artifact["lfs_oid"] = f"sha256:{'0' * 64}"

    validate_retained_evidence_manifest(
        manifest,
        repo_root=ROOT,
        registry_path=REGISTRY,
    )


def test_git_lfs_artifact_requires_valid_content_oid() -> None:
    manifest = deepcopy(load_retained_evidence_manifest(MANIFEST))
    artifact = manifest["reference_cells"][0]["artifacts"][0]
    artifact["retrieval"] = "git_lfs"
    artifact["lfs_oid"] = "sha256:not-a-digest"

    with pytest.raises(ValueError, match="invalid LFS object id"):
        validate_retained_evidence_manifest(
            manifest,
            repo_root=ROOT,
            registry_path=REGISTRY,
        )


def test_retained_reference_cell_requires_source_closure() -> None:
    manifest = deepcopy(load_retained_evidence_manifest(MANIFEST))
    del manifest["reference_cells"][0]["closure"]

    with pytest.raises(ValueError, match="missing fields: closure"):
        validate_retained_evidence_manifest(
            manifest,
            repo_root=ROOT,
            registry_path=REGISTRY,
        )


def test_retained_reference_cell_requires_replay_verification() -> None:
    manifest = deepcopy(load_retained_evidence_manifest(MANIFEST))
    del manifest["reference_cells"][0]["verification"]

    with pytest.raises(ValueError, match="missing fields: verification"):
        validate_retained_evidence_manifest(
            manifest,
            repo_root=ROOT,
            registry_path=REGISTRY,
        )


def test_retained_reference_cell_rejects_missing_closure_path() -> None:
    manifest = deepcopy(load_retained_evidence_manifest(MANIFEST))
    manifest["reference_cells"][0]["closure"]["entrypoints"] = [
        "src/clinical_extraction/does_not_exist.py"
    ]

    with pytest.raises(ValueError, match="closure path is missing"):
        validate_retained_evidence_manifest(
            manifest,
            repo_root=ROOT,
            registry_path=REGISTRY,
        )


def test_deterministic_all9_registry_entry_is_the_rules_reference() -> None:
    letter = ExectLetter("RULES-REFERENCE", "Diagnosis: focal epilepsy.")
    scorecard = deterministic_all9_scorecard.build_scorecard(
        [letter],
        run_all9_on_letters([letter]),
    )
    scorecard.update({"split": "dev", "generated_on": "2026-07-14"})

    entry = deterministic_all9_scorecard._registry_entry(
        scorecard,
        json_path=Path("experiments/example.json"),
        md_path=Path("docs/experiments/example.md"),
    )

    assert entry.architecture_family == "rules_only"
    assert entry.comparison_role == "control"
    assert entry.registry_roles == ("architecture_comparator",)
