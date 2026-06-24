from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from clinical_extraction.observatory.api import create_app
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    component_ablation_replay,
)


def _by_run(payload: dict[str, object]) -> dict[str, dict[str, object]]:
    return {
        str(architecture["run_id"]): architecture
        for architecture in payload["architectures"]  # type: ignore[index]
    }


def test_component_ablation_replay_builds_layer_ladders_for_all_architectures() -> None:
    payload = component_ablation_replay.build_component_ablation_payload()

    assert payload["artifact_kind"] == "exectv2_component_ablation_set"
    assert payload["row_inspection_policy"] == "aggregate_only"
    assert payload["allow_model_calls"] is False
    assert len(payload["architectures"]) == 4
    assert len(payload["layers"]) == 6
    assert len(payload["ablations"]) == 24

    layer_ids = [layer["layer_id"] for layer in payload["layers"]]
    # The redundant always-zero "final assembly" stage is gone entirely.
    assert "final_assembly" not in layer_ids
    # The two structurally-inert producer guards are kept but tagged for the
    # frontend to hide (not deleted from the aggregate provenance).
    inert = {layer["layer_id"] for layer in payload["layers"] if layer.get("inert")}
    assert inert == {"source_scored", "evidence_valid"}

    architectures = _by_run(payload)
    v08 = architectures["exectv2_holistic_finding_assembly_v08_dev140"]
    v09 = architectures["exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140"]
    deepseek = architectures["exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140"]
    qwen = architectures[
        "exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140"
    ]

    assert v08["final_score"]["overall"]["f1"] == 0.9155  # type: ignore[index]
    assert v09["final_score"]["overall"]["f1"] == 0.9061  # type: ignore[index]
    assert deepseek["final_score"]["overall"]["f1"] == 0.9174  # type: ignore[index]
    assert qwen["final_score"]["overall"]["f1"] == 0.9001  # type: ignore[index]


def test_component_ablation_replay_exposes_meaningful_layer_deltas() -> None:
    payload = component_ablation_replay.build_component_ablation_payload()
    architectures = _by_run(payload)

    v08_impacts = {
        str(impact["layer_id"]): impact
        for impact in architectures["exectv2_holistic_finding_assembly_v08_dev140"][
            "layer_impacts"
        ]
    }
    qwen_impacts = {
        str(impact["layer_id"]): impact
        for impact in architectures[
            "exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140"
        ]["layer_impacts"]
    }

    assert v08_impacts["dictionary_normalized"]["overall_delta_from_previous"] == 0.0389
    assert v08_impacts["residual_semantic_added"]["family_deltas"]["Diagnosis"] == 0.0476
    assert v08_impacts["headline_projection"]["family_deltas"]["SeizureFrequency"] == 0.1239

    assert qwen_impacts["dictionary_normalized"]["overall_delta_from_previous"] == 0.112
    assert qwen_impacts["residual_semantic_added"]["overall_delta_from_previous"] == 0.1041
    assert qwen_impacts["headline_projection"]["family_deltas"]["SeizureFrequency"] == 0.1942


def test_component_ablation_replay_outputs_contract_artifacts(tmp_path: Path) -> None:
    json_path = tmp_path / "ablation.json"
    jsonl_path = tmp_path / "ablation.jsonl"
    md_path = tmp_path / "ablation.md"
    config_dir = tmp_path / "configs"

    paths = component_ablation_replay.write_component_ablation_artifacts(
        json_path=json_path,
        jsonl_path=jsonl_path,
        md_path=md_path,
        config_dir=config_dir,
        frontend_path=None,
    )

    assert paths == {
        "json": json_path,
        "jsonl": jsonl_path,
        "markdown": md_path,
        "configs": config_dir,
    }
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    lines = [
        json.loads(line)
        for line in jsonl_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(lines) == len(payload["architectures"]) == 4
    assert all(
        line["artifact_kind"] == "exectv2_component_architecture_ladder"
        for line in lines
    )
    assert "No model calls" in md_path.read_text(encoding="utf-8")
    assert len(list(config_dir.glob("*.yaml"))) == 24


def test_committed_component_ablation_artifact_matches_builder_contract() -> None:
    static_path = (
        component_ablation_replay.REPO_ROOT
        / "frontend/public/mock-data/exectv2/component-ablation.json"
    )
    if not static_path.exists():
        return

    static_payload = json.loads(static_path.read_text(encoding="utf-8"))
    built_payload = component_ablation_replay.build_component_ablation_payload()

    assert static_payload["architectures"] == built_payload["architectures"]
    assert static_payload["ablations"] == built_payload["ablations"]


def test_observatory_serves_exectv2_component_ablation_payload() -> None:
    client = TestClient(create_app(repo_root=component_ablation_replay.REPO_ROOT))

    response = client.get("/exectv2/component-ablation")

    assert response.status_code == 200
    payload = response.json()
    assert payload["artifact_kind"] == "exectv2_component_ablation_set"
    assert len(payload["architectures"]) == 4
    assert len(payload["ablations"]) == 24
