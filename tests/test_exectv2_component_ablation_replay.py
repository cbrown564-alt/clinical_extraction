from __future__ import annotations

import json
from pathlib import Path

import pytest
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
        for impact in architectures["exectv2_holistic_finding_assembly_v08_dev140"]["layer_impacts"]
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


def test_component_off_replay_configs_cover_named_dev140_component_removals() -> None:
    payload = component_ablation_replay.build_component_ablation_payload()

    configs = component_ablation_replay.build_component_off_replay_configs(payload)

    assert len(configs) == 16
    assert {config["component_id"] for config in configs} == {
        "evidence_validation",
        "standard_dictionary",
        "residual_semantic_lens",
        "headline_projection",
    }
    assert {config["row_inspection_policy"] for config in configs} == {"aggregate_only"}
    assert {config["allow_model_calls"] for config in configs} == {False}

    first = next(
        config
        for config in configs
        if config["baseline_run_id"] == "exectv2_holistic_finding_assembly_v08_dev140"
        and config["component_id"] == "standard_dictionary"
    )
    assert first["artifact_kind"] == "exectv2_component_off_replay_config"
    assert first["prediction_bearing_status"] == "conditional"
    assert first["split"] == "dev140"
    assert first["scorer_view"] == "clinical_headline"
    assert first["baseline_surface"] == "dictionary_normalized"
    assert first["component_off_surface"] == "evidence_valid"
    assert first["baseline_aggregate_score"]["overall"]["f1"] == 0.8697
    assert first["component_off_aggregate_score"]["overall"]["f1"] == 0.8308
    assert first["overall_delta"] == -0.0389
    assert first["overall_component_contribution_delta"] == 0.0389
    assert first["family_component_contribution_deltas"]["Diagnosis"] == 0.1042
    assert "schema_validity" in first["validity_rates"]
    assert "evidence_validity" in first["validity_rates"]

    component_ablation_replay.validate_component_off_replay_configs(configs)
    malformed = dict(first)
    malformed.pop("component_id")
    with pytest.raises(ValueError, match="component_id"):
        component_ablation_replay.validate_component_off_replay_configs([malformed])


def test_component_off_readout_payload_reports_named_dev140_ablations() -> None:
    payload = component_ablation_replay.build_component_off_readout_payload()

    assert payload["artifact_kind"] == "exectv2_component_off_readout_set"
    assert payload["split"] == "dev140"
    assert payload["scorer_view"] == "clinical_headline"
    assert payload["row_inspection_policy"] == "aggregate_only"
    assert payload["allow_model_calls"] is False
    assert len(payload["ablations"]) == 16
    assert len(payload["component_summaries"]) == 4
    assert payload["claim_boundary"] == (
        "dev140 replay-only one-component-off aggregate component-impact readout; "
        "separate from reliability scorecard"
    )

    evidence = next(
        summary
        for summary in payload["component_summaries"]
        if summary["component_id"] == "evidence_validation"
    )
    assert "structurally inert" in evidence["claim_use"]
    assert all(row["overall_component_contribution_delta"] == 0.0 for row in evidence["rows"])

    dictionary = next(
        summary
        for summary in payload["component_summaries"]
        if summary["component_id"] == "standard_dictionary"
    )
    assert "Dictionary normalization" in dictionary["claim_use"]


def test_full200_component_off_readout_uses_frozen_component_set() -> None:
    payload = component_ablation_replay.build_full200_component_off_readout_payload(
        code_hash="test-hash",
        worktree_state="clean",
    )

    assert payload["artifact_kind"] == "exectv2_component_off_full200_readout_set"
    assert payload["split"] == "full200"
    assert payload["row_count"] == 200
    assert payload["code_hash"] == "test-hash"
    assert payload["worktree_state"] == "clean"
    assert payload["row_inspection_boundary"] == (
        "aggregate_only_no_full200_or_holdout_row_level_inspection"
    )
    assert {row["status"] for row in payload["preflight"]} == {"pass"}
    assert len(payload["ablations"]) == 9
    assert {row["component_id"] for row in payload["ablations"]} == {
        "standard_dictionary",
        "residual_semantic_lens",
        "headline_projection",
    }
    assert "evidence_validation" not in {row["component_id"] for row in payload["ablations"]}

    deepseek_projection = next(
        row
        for row in payload["ablations"]
        if row["baseline_run_id"] == "exectv2_2call_no_sf_adjudicator_deepseek_full200"
        and row["component_id"] == "headline_projection"
    )
    assert deepseek_projection["baseline_aggregate_score"]["overall"]["f1"] == 0.8566
    assert deepseek_projection["operational_counts"]["parse_failures"] == 1
    assert deepseek_projection["validity_rates"]["schema_validity"] == 0.9988


def test_full200_component_off_readout_outputs_contract_artifacts(
    tmp_path: Path,
) -> None:
    json_path = tmp_path / "full200_component_off.json"
    jsonl_path = tmp_path / "full200_component_off.jsonl"
    md_path = tmp_path / "full200_component_off.md"

    paths = component_ablation_replay.write_full200_component_off_readout_artifacts(
        json_path=json_path,
        jsonl_path=jsonl_path,
        md_path=md_path,
        generated_on="2026-06-26",
        code_hash="test-hash",
        worktree_state="clean",
    )

    assert paths == {
        "component_off_json": json_path,
        "component_off_jsonl": jsonl_path,
        "component_off_markdown": md_path,
    }
    readout = json.loads(json_path.read_text(encoding="utf-8"))
    lines = [
        json.loads(line)
        for line in jsonl_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    markdown = md_path.read_text(encoding="utf-8")

    assert readout["predeclaration_path"].endswith(
        "exectv2_component_off_full200_predeclaration_2026-06-26.md"
    )
    assert len(lines) == 9
    assert "Aggregate Component-Off Table" in markdown
    assert "Component Impact evidence only" in markdown
    assert "Reliability Scorecard" in markdown
    assert "evidence_validation" not in markdown


def test_component_off_readout_outputs_contract_artifacts(tmp_path: Path) -> None:
    payload = component_ablation_replay.build_component_ablation_payload()
    json_path = tmp_path / "component_off.json"
    jsonl_path = tmp_path / "component_off.jsonl"
    md_path = tmp_path / "component_off.md"

    paths = component_ablation_replay.write_component_off_readout_artifacts(
        payload,
        json_path=json_path,
        jsonl_path=jsonl_path,
        md_path=md_path,
        ladder_json=tmp_path / "ladder.json",
    )

    assert paths == {
        "component_off_json": json_path,
        "component_off_jsonl": jsonl_path,
        "component_off_markdown": md_path,
    }
    lines = [
        json.loads(line)
        for line in jsonl_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(lines) == 16
    assert all(line["artifact_kind"] == "exectv2_component_off_replay_config" for line in lines)
    markdown = md_path.read_text(encoding="utf-8")
    assert "Aggregate Component-Off Table" in markdown
    assert "reliability scorecard" in markdown
    assert "evidence_validation" in markdown


def test_component_ablation_replay_outputs_contract_artifacts(tmp_path: Path) -> None:
    json_path = tmp_path / "ablation.json"
    jsonl_path = tmp_path / "ablation.jsonl"
    md_path = tmp_path / "ablation.md"
    config_dir = tmp_path / "configs"
    component_off_json = tmp_path / "component_off.json"
    component_off_jsonl = tmp_path / "component_off.jsonl"
    component_off_md = tmp_path / "component_off.md"

    paths = component_ablation_replay.write_component_ablation_artifacts(
        json_path=json_path,
        jsonl_path=jsonl_path,
        md_path=md_path,
        config_dir=config_dir,
        frontend_path=None,
        component_off_json_path=component_off_json,
        component_off_jsonl_path=component_off_jsonl,
        component_off_md_path=component_off_md,
    )

    assert paths == {
        "json": json_path,
        "jsonl": jsonl_path,
        "markdown": md_path,
        "configs": config_dir,
        "component_off_json": component_off_json,
        "component_off_jsonl": component_off_jsonl,
        "component_off_markdown": component_off_md,
    }
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    lines = [
        json.loads(line)
        for line in jsonl_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(lines) == len(payload["architectures"]) == 4
    assert all(line["artifact_kind"] == "exectv2_component_architecture_ladder" for line in lines)
    markdown = md_path.read_text(encoding="utf-8")
    assert "No model calls" in markdown
    assert "Final assembly" not in markdown
    assert "Residual semantic" in markdown
    assert len(list(config_dir.glob("*__layer_*.yaml"))) == 24
    assert len(list(config_dir.glob("*__component_off_*.yaml"))) == 16


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
