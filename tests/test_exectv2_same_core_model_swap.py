from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    model_swap,
)
from scripts import run_exectv2_2call_model_swap as runner


def test_single_call_config_has_no_diagnosis_sidecar_path(tmp_path: Path) -> None:
    artifact = _write_jsonl(tmp_path / "rows.jsonl", [_row("EA1")])
    config_path = _write_config(
        tmp_path,
        candidate_id="single_call",
        model="openai/gpt-4.1-mini",
        model_label="GPT-4.1-mini",
        artifact=artifact,
        model_led=True,
        single_call_diagnosis=True,
    )
    config = model_swap.load_model_swap_config(config_path)

    assert runner._diagnosis_artifact_path(config) is None


def test_model_swap_config_parity_allows_only_model_adapter_differences(
    tmp_path: Path,
) -> None:
    shared_rows = _write_jsonl(tmp_path / "rows.jsonl", [_row("EA1"), _row("EA2")])
    gpt = _write_config(
        tmp_path,
        candidate_id="swap_gpt",
        model="openai/gpt-4.1-mini",
        model_label="GPT-4.1-mini",
        artifact=shared_rows,
    )
    qwen = _write_config(
        tmp_path,
        candidate_id="swap_qwen",
        model="ollama/qwen3.6:35b",
        model_label="Qwen 3.6 35B",
        artifact=tmp_path / "missing_qwen.jsonl",
        prompt_profile="qwen_compact",
    )

    configs = [model_swap.load_model_swap_config(path) for path in (gpt, qwen)]
    parity = model_swap.validate_same_core_configs(configs)

    assert parity["architecture_core_id"] == "same_core_test"
    assert parity["component_graph_identical"] is True
    assert parity["shared_signature"]["live_call_components"] == [
        "structured_key_family_event_ledger",
        "diagnosis_decomposer",
    ]
    assert parity["adapter_differences"] == {
        "swap_gpt": {
            "model": "openai/gpt-4.1-mini",
            "model_label": "GPT-4.1-mini",
            "prompt_profile": "full",
            "runtime": "openai_chat",
        },
        "swap_qwen": {
            "model": "ollama/qwen3.6:35b",
            "model_label": "Qwen 3.6 35B",
            "prompt_profile": "qwen_compact",
            "runtime": "openai_chat",
        },
    }


def test_model_led_sf_chain_stops_before_independent_extractor_union(
    monkeypatch,
    tmp_path: Path,
) -> None:
    structured = tmp_path / "candidate_structured.jsonl"
    output = tmp_path / "candidate_sf_unknown_suppression.jsonl"
    calls: list[tuple[str, Path]] = []

    monkeypatch.setattr(
        runner,
        "_write_sf_structured_direct_artifact",
        lambda **kwargs: calls.append(("direct", kwargs["output"])),
    )
    monkeypatch.setattr(
        runner.sf_projection,
        "read_rows",
        lambda path: calls.append(("projection_read", path)) or [],
    )
    monkeypatch.setattr(
        runner.sf_projection,
        "write_rows_and_report",
        lambda rows, **kwargs: calls.append(("projection_write", kwargs["jsonl_path"])),
    )
    monkeypatch.setattr(
        runner.sf_suppression,
        "read_rows",
        lambda path: calls.append(("suppression_read", path)) or [],
    )
    monkeypatch.setattr(
        runner.sf_suppression,
        "write_rows_and_report",
        lambda rows, **kwargs: calls.append(("suppression_write", kwargs["jsonl_path"])),
    )
    runner._run_model_led_sf_chain(
        structured_jsonl=structured,
        sf_output_jsonl=output,
        letters=[],
    )

    assert calls == [
        ("direct", tmp_path / "candidate_sf_structured_direct.jsonl"),
        ("projection_read", tmp_path / "candidate_sf_structured_direct.jsonl"),
        ("projection_write", tmp_path / "candidate_sf_state_projection_combined.jsonl"),
        ("suppression_read", tmp_path / "candidate_sf_state_projection_combined.jsonl"),
        ("suppression_write", output),
    ]


def test_retained_model_led_audit_configs_share_the_decision_0040_graph() -> None:
    paths = sorted(Path("configs/exectv2/model_led_audit").glob("*.json"))
    configs = [model_swap.load_model_swap_config(path) for path in paths]

    assert len(configs) == 3
    assert all(
        model_swap.validate_model_led_architecture(config)["status"] == "pass"
        for config in configs
    )
    assert model_swap.validate_same_core_configs(configs)["component_graph_identical"] is True


def test_model_swap_runner_rejects_resume_rows_outside_manifest_split(
    tmp_path: Path,
) -> None:
    artifact = _write_jsonl(tmp_path / "contaminated.jsonl", [_row("EA_TEST")])

    try:
        runner._validate_resume_artifact(
            artifact,
            expected_ids={"EA1", "EA2"},
            component="structured_key_family_event_ledger",
        )
    except ValueError as exc:
        assert "outside the frozen row set" in str(exc)
        assert "EA_TEST" in str(exc)
    else:
        raise AssertionError("contaminated resume artifact was accepted")


def _row(letter_id: str) -> dict[str, object]:
    mentions = [
        _mention(
            "Diagnosis",
            "focal epilepsy",
            "Diagnosis: focal epilepsy",
            {"DiagCategory": "Epilepsy", "Certainty": "5", "Negation": "Affirmed"},
        ),
        _mention(
            "SeizureFrequency",
            "focal seizures",
            "focal seizures twice a month",
            {
                "NumberOfSeizures": "2",
                "NumberOfTimePeriods": "1",
                "TimePeriod": "Month",
            },
        ),
        _mention(
            "Prescription",
            "lamotrigine",
            "lamotrigine 100 mg bd",
            {
                "DrugName": "lamotrigine",
                "DrugDose": "100",
                "DoseUnit": "mg",
                "Frequency": "2",
            },
        ),
        _mention(
            "Investigations",
            "MRI",
            "MRI was normal",
            {"MRI_Performed": "Yes", "MRI_Results": "Normal"},
        ),
    ]
    return {
        "letter_id": letter_id,
        "split": "toy",
        "pipeline_family": "toy_structured",
        "prompt_version": "toy_v1",
        "model": "none",
        "mode": "no-call",
        "call_error": None,
        "parse_errors": [],
        "gate_warnings": [],
        "n_mentions_raw": len(mentions),
        "n_mentions_scored": len(mentions),
        "n_evidence_invalid": 0,
        "predicted_mentions": mentions,
        "raw_output": json.dumps({"mentions": mentions}),
    }


def _mention(entity: str, text: str, evidence: str, attrs: dict[str, str]) -> dict[str, object]:
    return {
        "entity": entity,
        "text": text,
        "attributes": attrs,
        "evidence": evidence,
        "confidence": "high",
        "rationale": "",
    }


def _write_config(
    tmp_path: Path,
    *,
    candidate_id: str,
    model: str,
    model_label: str,
    artifact: Path,
    prompt_profile: str = "full",
    replayed_components: list[str] | None = None,
    split: str = "toy",
    row_count: int = 2,
    model_led: bool = False,
    single_call_diagnosis: bool = False,
) -> Path:
    payload = {
        "candidate_id": candidate_id,
        "model": model,
        "model_label": model_label,
        "architecture_core_id": "same_core_test",
        "calls_per_letter": 1 if single_call_diagnosis else 2,
        "runtime": "openai_chat",
        "prompt_profile": prompt_profile,
        "temperature": 0,
        "max_tokens": {
            "structured_key_family_event_ledger": 6000,
            "diagnosis_decomposer": 2600,
        },
        "live_call_components": (
            ["structured_key_family_event_ledger"]
            if single_call_diagnosis
            else [
                "structured_key_family_event_ledger",
                "diagnosis_decomposer",
            ]
        ),
        "architecture_contract": (
            "decision_0040_model_led" if model_led else "historical_same_core"
        ),
        "diagnosis_resolution_candidate": model_led,
        "replayed_components": replayed_components
        or (
            [
                "sf_structured_direct_adapter",
                "sf_state_projection",
                "sf_unknown_suppression",
                "prescription_dictionary_lens",
                "finding_assembly",
            ]
            if model_led
            else [
                "sf_structured_direct_adapter",
                "sf_state_projection",
                "sf_unknown_suppression",
                "sf_union_arbitration",
                "prescription_deterministic_repair",
                "finding_assembly",
            ]
        ),
        "claim_boundary": "toy model swap",
        "run_command": "python scripts/run_exectv2_2call_model_swap.py",
        "assembly": {
            "candidate_id": candidate_id,
            "pipeline_family": "toy_same_core_model_swap",
            "ownership": "toy_model_swap",
            "split": split,
            "row_count": row_count,
            "claim_boundary": "toy model swap",
            "baseline_producer": "structured_key_family_event_ledger",
            "promotion_decision": "same-core-model-swap-readout",
            "producers": {
                "structured_key_family_event_ledger": {
                    "kind": "saved_jsonl",
                    "artifact": str(artifact),
                    "ownership_label": "toy_structured",
                    "source_lane": "toy_structured",
                },
                "diagnosis_decomposer": {
                    "kind": "saved_jsonl",
                    "artifact": str(artifact),
                    "ownership_label": "toy_dx",
                    "source_lane": "toy_dx",
                },
                "sf_structured_union": {
                    "kind": "saved_jsonl",
                    "artifact": str(artifact),
                    "ownership_label": "toy_sf",
                    "source_lane": "toy_sf",
                },
                "sf_model_projection_suppression": {
                    "kind": "saved_jsonl",
                    "artifact": str(artifact),
                    "ownership_label": "toy_model_sf_projection_suppression",
                    "source_lane": "toy_model_sf_projection_suppression",
                },
                "prescription_deterministic_repair": {
                    "kind": "saved_jsonl",
                    "artifact": str(artifact),
                    "ownership_label": "toy_rx",
                    "source_lane": "toy_rx",
                },
            },
            "lenses": {
                "Diagnosis": {
                    "producer": (
                        "structured_key_family_event_ledger"
                        if single_call_diagnosis
                        else "diagnosis_decomposer"
                    ),
                    "lens": "diagnosis_hierarchy_negation_v01",
                    "source_lane": (
                        "toy_structured" if single_call_diagnosis else "toy_dx"
                    ),
                    "ownership_label": (
                        "toy_structured_dx" if single_call_diagnosis else "toy_dx"
                    ),
                },
                "SeizureFrequency": {
                    "producer": (
                        "sf_model_projection_suppression" if model_led else "sf_structured_union"
                    ),
                    "lens": "sf_state_projection_suppression_v01",
                    "source_lane": "toy_model_sf",
                    "ownership_label": "toy_model_sf",
                },
                "Prescription": {
                    "producer": (
                        "structured_key_family_event_ledger"
                        if model_led
                        else "prescription_deterministic_repair"
                    ),
                    "lens": (
                        "prescription_dictionary_v10" if model_led else "prescription_regimen_v01"
                    ),
                    "source_lane": "toy_model_rx" if model_led else "toy_rx",
                    "ownership_label": "toy_model_rx" if model_led else "toy_rx",
                },
                "Investigations": {
                    "producer": "structured_key_family_event_ledger",
                    "lens": "investigations_result_v01",
                    "source_lane": "toy_inv",
                    "ownership_label": "toy_inv",
                },
            },
            "views": [
                "raw_candidate",
                "post_lens",
                "clinical_headline",
                "fidelity_companion",
                "benchmark_cui",
            ],
        },
        "outputs": {
            "json": str(tmp_path / f"{candidate_id}.json"),
            "jsonl": str(tmp_path / f"{candidate_id}.jsonl"),
            "markdown": str(tmp_path / f"{candidate_id}.md"),
        },
    }
    path = tmp_path / f"{candidate_id}.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> Path:
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    return path
