from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    model_swap,
)
from scripts import run_exectv2_2call_model_swap as runner


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


def test_model_swap_readiness_marks_missing_model_rows_pending(tmp_path: Path) -> None:
    shared_rows = _write_jsonl(tmp_path / "rows.jsonl", [_row("EA1"), _row("EA2")])
    gpt_path = _write_config(
        tmp_path,
        candidate_id="swap_gpt",
        model="openai/gpt-4.1-mini",
        model_label="GPT-4.1-mini",
        artifact=shared_rows,
    )
    deepseek_path = _write_config(
        tmp_path,
        candidate_id="swap_deepseek",
        model="deepseek/deepseek-chat",
        model_label="DeepSeek chat",
        artifact=tmp_path / "missing_deepseek.jsonl",
    )

    paths = model_swap.write_model_swap_artifacts(
        config_paths=[gpt_path, deepseek_path],
        generated_on="2026-06-25",
        json_path=tmp_path / "summary.json",
        jsonl_path=tmp_path / "summary.jsonl",
        markdown_path=tmp_path / "summary.md",
        gold_loader=lambda _split: _letters(),
    )

    payload = json.loads(paths["json"].read_text(encoding="utf-8"))
    rows = _read_jsonl(paths["jsonl"])
    by_candidate = {row["candidate_id"]: row for row in payload["model_rows"]}

    assert payload["overall_status"] == "pending_same_core_model_runs"
    assert payload["readiness_gates"]["architecture_parity"]["status"] == "pass"
    assert payload["readiness_gates"]["operational_stability"]["status"] == "pending"
    assert by_candidate["swap_gpt"]["status"] == "complete"
    assert by_candidate["swap_gpt"]["metrics"]["overall"]["f1"] == 0.75
    assert by_candidate["swap_deepseek"]["status"] == "pending_source_artifacts"
    assert "missing_deepseek.jsonl" in by_candidate["swap_deepseek"]["missing_artifacts"][0]
    assert rows == [
        {
            "candidate_id": "swap_gpt",
            "model_label": "GPT-4.1-mini",
            "status": "complete",
            "overall_clinical_headline_f1": 0.75,
            "call_failures": 0,
            "parse_schema_failures": 0,
            "minimum_exact_evidence_rate": 1.0,
        },
        {
            "candidate_id": "swap_deepseek",
            "model_label": "DeepSeek chat",
            "status": "pending_source_artifacts",
            "overall_clinical_headline_f1": None,
            "call_failures": None,
            "parse_schema_failures": None,
            "minimum_exact_evidence_rate": None,
        },
    ]


def test_model_swap_readiness_marks_completed_operational_failures(tmp_path: Path) -> None:
    shared_rows = _write_jsonl(tmp_path / "rows.jsonl", [_row("EA1"), _row("EA2")])
    gpt_path = _write_config(
        tmp_path,
        candidate_id="swap_gpt",
        model="openai/gpt-4.1-mini",
        model_label="GPT-4.1-mini",
        artifact=shared_rows,
    )
    qwen_path = _write_config(
        tmp_path,
        candidate_id="swap_qwen",
        model="ollama_chat/qwen3.6:35b",
        model_label="Qwen 3.6 35B",
        artifact=shared_rows,
        prompt_profile="qwen_compact",
    )
    configs = [model_swap.load_model_swap_config(path) for path in (gpt_path, qwen_path)]
    parity = model_swap.validate_same_core_configs(configs)
    rows = [
        _complete_model_row("swap_gpt", "GPT-4.1-mini", call_failures=0, parse_failures=0),
        _complete_model_row("swap_qwen", "Qwen 3.6 35B", call_failures=1, parse_failures=2),
    ]

    payload = model_swap.build_model_swap_payload(
        configs=configs,
        model_rows=rows,
        parity=parity,
        generated_on="2026-06-25",
    )

    assert payload["overall_status"] == "blocked_architecture_or_operational_gate"
    assert payload["readiness_gates"]["family_parity"]["status"] == "pass"
    assert payload["readiness_gates"]["operational_stability"]["status"] == "fail"
    assert "operational stability is not promoted" in payload["claim_boundary"]
    assert payload["next_actions"] == [
        "Record the completed dev140 same-core comparison with an "
        "operational-stability caveat.",
        "Review Qwen call/parse failures before any full-200 "
        "aggregate-only predeclaration.",
    ]


def test_model_swap_parity_fails_when_component_graph_changes(tmp_path: Path) -> None:
    rows = _write_jsonl(tmp_path / "rows.jsonl", [_row("EA1"), _row("EA2")])
    gpt = _write_config(
        tmp_path,
        candidate_id="swap_gpt",
        model="openai/gpt-4.1-mini",
        model_label="GPT-4.1-mini",
        artifact=rows,
    )
    changed = _write_config(
        tmp_path,
        candidate_id="swap_changed",
        model="deepseek/deepseek-chat",
        model_label="DeepSeek chat",
        artifact=rows,
        replayed_components=["finding_assembly"],
    )

    configs = [model_swap.load_model_swap_config(path) for path in (gpt, changed)]
    parity = model_swap.validate_same_core_configs(configs)

    assert parity["component_graph_identical"] is False
    assert parity["mismatched_candidates"] == ["swap_changed"]


def test_model_swap_runner_passes_api_base_to_live_components(
    monkeypatch, tmp_path: Path
) -> None:
    captured: dict[str, str | None] = {}

    def fake_structured_run_split(*args, **kwargs):
        captured["structured_api_base"] = kwargs["api_base"]
        return [], {"summary": {}}

    def fake_dx_run_split(*args, **kwargs):
        captured["diagnosis_api_base"] = kwargs["api_base"]
        captured["diagnosis_prompt_profile"] = kwargs["prompt_profile"]
        return [], {"summary": {}}

    monkeypatch.setattr(runner.structured, "run_split", fake_structured_run_split)
    monkeypatch.setattr(runner.dx_decomposer, "run_split", fake_dx_run_split)
    monkeypatch.setattr(runner, "write_jsonl", lambda *args, **kwargs: None)
    monkeypatch.setattr(runner.structured, "write_report", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        runner.dx_decomposer, "write_report", lambda *args, **kwargs: None
    )
    config = SimpleNamespace(
        model="ollama_chat/qwen3.6:35b",
        temperature=0,
        max_tokens={
            "structured_key_family_event_ledger": 10000,
            "diagnosis_decomposer": 3200,
        },
        prompt_profile="qwen_compact",
        assembly=SimpleNamespace(split="dev140"),
    )
    args = SimpleNamespace(
        no_dspy_cache=True,
        api_base="http://127.0.0.1:11435",
        progress_every=1,
        resume=True,
    )

    structured_rows = runner._run_structured(
        config, [], tmp_path / "structured.jsonl", args
    )
    runner._run_diagnosis(config, [], structured_rows, tmp_path / "dx.jsonl", args)

    assert captured == {
        "structured_api_base": "http://127.0.0.1:11435",
        "diagnosis_api_base": "http://127.0.0.1:11435",
        "diagnosis_prompt_profile": "qwen_compact",
    }


def _letters() -> list[ExectLetter]:
    note = (
        "Diagnosis: focal epilepsy. Current medication: lamotrigine 100 mg bd. "
        "MRI was normal. She has focal seizures twice a month."
    )
    annotations = (
        ExectAnnotation(
            entity="Diagnosis",
            text="focal epilepsy",
            attributes={
                "DiagCategory": "Epilepsy",
                "Certainty": "5",
                "Negation": "Affirmed",
            },
        ),
        ExectAnnotation(
            entity="SeizureFrequency",
            text="focal seizures",
            attributes={
                "NumberOfSeizures": "2",
                "NumberOfTimePeriods": "1",
                "TimePeriod": "Month",
            },
        ),
        ExectAnnotation(
            entity="Prescription",
            text="lamotrigine",
            attributes={
                "DrugName": "lamotrigine",
                "DrugDose": "100",
                "DoseUnit": "mg",
                "Frequency": "2",
            },
        ),
        ExectAnnotation(
            entity="Investigations",
            text="MRI",
            attributes={"MRI_Performed": "Yes", "MRI_Results": "Normal"},
        ),
    )
    return [
        ExectLetter(letter_id="EA1", note_text=note, annotations=annotations),
        ExectLetter(letter_id="EA2", note_text=note, annotations=annotations),
    ]


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
) -> Path:
    payload = {
        "candidate_id": candidate_id,
        "model": model,
        "model_label": model_label,
        "architecture_core_id": "same_core_test",
        "calls_per_letter": 2,
        "runtime": "openai_chat",
        "prompt_profile": prompt_profile,
        "temperature": 0,
        "max_tokens": {
            "structured_key_family_event_ledger": 6000,
            "diagnosis_decomposer": 2600,
        },
        "live_call_components": [
            "structured_key_family_event_ledger",
            "diagnosis_decomposer",
        ],
        "replayed_components": replayed_components
        or [
            "sf_structured_direct_adapter",
            "sf_state_projection",
            "sf_unknown_suppression",
            "sf_union_arbitration",
            "prescription_deterministic_repair",
            "finding_assembly",
        ],
        "claim_boundary": "toy model swap",
        "run_command": "python scripts/run_exectv2_2call_model_swap.py",
        "assembly": {
            "candidate_id": candidate_id,
            "pipeline_family": "toy_same_core_model_swap",
            "ownership": "toy_model_swap",
            "split": "toy",
            "row_count": 2,
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
                "prescription_deterministic_repair": {
                    "kind": "saved_jsonl",
                    "artifact": str(artifact),
                    "ownership_label": "toy_rx",
                    "source_lane": "toy_rx",
                },
            },
            "lenses": {
                "Diagnosis": {
                    "producer": "diagnosis_decomposer",
                    "lens": "diagnosis_hierarchy_negation_v01",
                    "source_lane": "toy_dx",
                    "ownership_label": "toy_dx",
                },
                "SeizureFrequency": {
                    "producer": "sf_structured_union",
                    "lens": "sf_state_direct_v01",
                    "source_lane": "toy_sf",
                    "ownership_label": "toy_sf",
                },
                "Prescription": {
                    "producer": "prescription_deterministic_repair",
                    "lens": "prescription_regimen_v01",
                    "source_lane": "toy_rx",
                    "ownership_label": "toy_rx",
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
                "evidence_valid",
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


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _complete_model_row(
    candidate_id: str,
    model_label: str,
    *,
    call_failures: int,
    parse_failures: int,
) -> dict[str, object]:
    return {
        "candidate_id": candidate_id,
        "model": model_label,
        "model_label": model_label,
        "status": "complete",
        "metrics": {"overall": {"f1": 0.8}, "by_indicator": {}},
        "diagnostics": {
            "call_failures": call_failures,
            "parse_schema_failures": parse_failures,
            "minimum_exact_evidence_rate": 1.0,
        },
        "paths": {"config": f"{candidate_id}.json"},
    }
