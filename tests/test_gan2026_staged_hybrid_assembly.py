from clinical_extraction.tasks.seizure_frequency.gan2026.hybrid import (
    staged_hybrid_assembly,
)
from tests.test_gan2026_selected_state_union_replay import _boundary_row, _saved_row


def test_staged_hybrid_assembly_wires_promoted_no_call_components() -> None:
    outputs, metadata = (
        staged_hybrid_assembly.build_no_call_validation_development_replay(
            [_saved_row()],
            [_boundary_row()],
        )
    )

    assert sorted(outputs) == ["selected_state_union", "suspicious_state_routing"]
    assert metadata["policy_name"] == (
        "staged_hybrid_assembly_validation_development_v0"
    )
    assert metadata["metrics"]["selected_state_rows"] == 1
    assert metadata["metrics"]["suspicious_routing_rows"] == 1
    assert (
        metadata["component_outputs"]["selected_state_union"]["component_owner"]
        == "hybrid_selected_state_union"
    )
    assert (
        metadata["component_outputs"]["suspicious_state_routing"]["component_owner"]
        == "deterministic_suspicious_state_policy"
    )


def test_staged_hybrid_assembly_can_include_saved_verifier_replay() -> None:
    verifier_rows = [
        {
            "source_row_index": 101,
            "task_design": "binary_quote_highest_answer_selector",
            "call_status": "ok",
            "parsed_output": {"selected_answer": "1 per month"},
            "parse_errors": [],
            "design_action": "1 per month",
            "verifier_vs_routing": {
                "decision_changed": True,
                "delta": "W_to_C",
            },
        }
    ]

    outputs, metadata = (
        staged_hybrid_assembly.build_no_call_validation_development_replay(
            [_saved_row()],
            [_boundary_row()],
            verifier_rows=verifier_rows,
        )
    )

    assert sorted(outputs) == [
        "selected_state_union",
        "selective_verifier",
        "suspicious_state_routing",
    ]
    assert (
        metadata["component_outputs"]["selective_verifier"]["component_owner"]
        == "llm_selective_verifier"
    )
    assert metadata["metrics"]["selective_verifier_rows"] == 1
    assert metadata["metrics"]["selective_verifier_w_to_c_rows"] == 1
    assert metadata["metrics"]["assembly_rows"] == 2
    assert metadata["metrics"]["assembly_rows_with_selective_verifier"] == 1


def test_staged_hybrid_assembly_writes_report(tmp_path) -> None:
    verifier_rows = [
        {
            "source_row_index": 101,
            "task_design": "binary_quote_highest_answer_selector",
            "call_status": "ok",
            "parsed_output": {"selected_answer": "unknown"},
            "parse_errors": [],
            "design_action": "unknown",
            "verifier_vs_routing": {
                "decision_changed": True,
                "delta": "C_to_W",
            },
        }
    ]
    outputs, metadata = (
        staged_hybrid_assembly.build_no_call_validation_development_replay(
            [_saved_row()],
            [_boundary_row()],
            verifier_rows=verifier_rows,
        )
    )
    rows = staged_hybrid_assembly.build_assembly_rows(outputs)
    report_path = tmp_path / "assembly.md"
    json_path = tmp_path / "assembly.json"
    jsonl_path = tmp_path / "assembly.jsonl"

    staged_hybrid_assembly.write_summary_json(metadata, json_path)
    staged_hybrid_assembly.write_report(
        rows,
        metadata,
        report_path,
        jsonl_path=jsonl_path,
        json_path=json_path,
    )

    assert json_path.exists()
    report = report_path.read_text()
    assert "verifier impact is currently a slice readout" in report
    assert "101" in report


def test_validation750_assembly_adapts_full_validation_surfaces() -> None:
    reasoner_rows = [
        {
            "source_row_index": 101,
            "split": "validation",
            "split_manifest": "gan2026_split_v1",
            "reference": {"gold_label": "1 per month"},
            "component_status": {
                "selected_evidence_exactness": "ok",
                "source_id_trace": "ok",
            },
            "structured_adjudicator_record": {
                "final_label": "1 per month",
                "selected_evidence": "one seizure a month",
            },
            "structured_llm_candidate_record": {
                "selection": {"final_label": "frequency"}
            },
            "score_layers": {
                "hybrid_adjudicator_with_adapters": {
                    "final_label": "1 per month",
                    "purist_correct": True,
                }
            },
            "adjudicator_prompt_input_json": "historical prompt should stay out",
        }
    ]
    safety_rows = [
        {
            "source_row_index": 101,
            "gold_label": "1 per month",
            "baseline_label": "unknown",
            "selected_evidence_exact": True,
            "selected_source_ids_exist": True,
            "gate_variants": {
                "combined_selective_gate_v0": {
                    "final_label": "1 per month",
                    "changed": True,
                }
            },
        }
    ]
    router_rows = [
        {
            "source_row_index": 101,
            "split": "validation",
            "split_manifest": "gan2026_split_v1",
            "router_version": "gan2026_rq9_selective_action_router_v3",
            "selective_action": "predict",
            "final_label": "1 per month",
            "primary_reason": "plain_predictable_frequency",
            "source_candidate": {"final_label": "1 per month"},
        }
    ]

    outputs, metadata = staged_hybrid_assembly.build_validation750_no_call_replay(
        reasoner_rows,
        safety_rows,
        router_rows,
    )
    rows = staged_hybrid_assembly.build_validation750_assembly_rows(outputs)

    assert metadata["metrics"]["assembly_rows"] == 1
    assert metadata["metrics"]["router_predict_rows"] == 1
    assert rows[0]["gold_label"] == "1 per month"
    assert rows[0]["component_presence"] == {
        "hybrid_reasoner_replay": True,
        "selective_safety_floor_gate_v0": True,
        "rq9_selective_action_router_v3": True,
    }
    reasoner = rows[0]["hybrid_reasoner_replay"]
    assert reasoner["saved_prompt_payloads_omitted"] is True
    assert "adjudicator_prompt_input_json" not in reasoner


def test_validation750_assembly_writes_claim_bounded_report(tmp_path) -> None:
    outputs, metadata = staged_hybrid_assembly.build_validation750_no_call_replay(
        reasoner_rows=[],
        safety_floor_rows=[],
        router_rows=[],
    )
    rows = staged_hybrid_assembly.build_validation750_assembly_rows(outputs)
    report_path = tmp_path / "validation750.md"

    staged_hybrid_assembly.write_validation750_report(
        rows,
        metadata,
        report_path,
        jsonl_path=tmp_path / "validation750.jsonl",
        json_path=tmp_path / "validation750.json",
    )

    report = report_path.read_text()
    assert "makes no live model calls" in report
    assert "Prompt Payload Boundary" in report
    assert "promoted_binary_selective_verifier" in report


def test_decision_layer_report_records_prediction_boundary(tmp_path) -> None:
    decision_rows = [
        {
            "source_row_index": 101,
            "final_action": "predict",
            "prediction_bearing": True,
            "development_accounting": {
                "purist_correct": True,
                "pragmatic_correct": True,
            },
            "verifier_used": False,
        }
    ]
    from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
        staged_decision_policy,
    )

    summary = staged_decision_policy.summarize_decision_rows(decision_rows)
    metadata = {
        "claim_language": summary["claim_language"],
        "metrics": {
            "row_count": summary["row_count"],
            "prediction_bearing_rows": summary["prediction_bearing_rows"],
            "non_prediction_rows": summary["non_prediction_rows"],
            "selective_purist_accuracy": summary["selective_purist_accuracy"],
            "selective_pragmatic_accuracy": summary["selective_pragmatic_accuracy"],
            "verifier_rows_used": summary["verifier_rows_used"],
        },
        "action_counts": summary["action_counts"],
    }
    report_path = tmp_path / "decision.md"

    staged_hybrid_assembly.write_decision_layer_report(
        decision_rows,
        metadata,
        report_path,
        jsonl_path=tmp_path / "decision.jsonl",
        json_path=tmp_path / "decision.json",
    )

    report = report_path.read_text()
    assert "prediction-bearing decision layer" in report
    assert "verifier rows used | 0" in report
