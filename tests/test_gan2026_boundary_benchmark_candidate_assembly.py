from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    boundary_benchmark_candidate_assembly,
)


def test_candidate_assembly_layers_typed_fields_over_current_candidate() -> None:
    rows = boundary_benchmark_candidate_assembly.build_candidate_rows(
        [
            _contract_row(
                source_row_index=1,
                mechanism="seizure_free_boundary_event_v0",
                evidence="Last seizure on 25 December 2023",
                gan_label="unknown",
                gold_label="unknown",
            )
        ],
        [_assembled_row(1, candidate_label="1 per month", gold_label="unknown")],
    )

    row = rows[0]

    assert row["architecture_decision"] == "typed_candidate_contract_layer"
    assert row["component_owner"] == "typed_boundary_classifier"
    assert row["current_label"] == "1 per month"
    assert row["proposed_label"] == "unknown"
    assert row["transition"] == "W_to_C"
    assert row["selected_for_ablation"] is True
    assert row["exact_evidence"] is True
    assert row["source_note_text"] is None
    assert row["final_label_policy_connected"] is False


def test_candidate_assembly_keeps_renderer_projection_ownership() -> None:
    rows = boundary_benchmark_candidate_assembly.build_candidate_rows(
        [
            _contract_row(
                source_row_index=2,
                mechanism="benchmark_convention_renderer_v0",
                evidence="multiple focal seizures per week",
                gan_label="multiple per week",
                gold_label="multiple per week",
                component_owner="benchmark_renderer",
                benchmark_rule="gan_vague_multiple_frequency",
                candidate_exposure="typed_clinical_state_present",
            )
        ],
        [_assembled_row(2, candidate_label="1 per month", gold_label="multiple per week")],
    )

    row = rows[0]

    assert row["component_owner"] == "benchmark_renderer"
    assert row["component_ownership_basis"] == "benchmark_convention_renderer_v0"
    assert row["benchmark_format_rule_id"] == "gan_vague_multiple_frequency"
    assert row["candidate_exposure"] == "typed_clinical_state_present"
    assert row["transition"] == "W_to_C"


def test_candidate_assembly_summary_blocks_undercovered_validation_panel() -> None:
    rows = boundary_benchmark_candidate_assembly.build_candidate_rows(
        [
            _contract_row(
                source_row_index=1,
                mechanism="seizure_free_boundary_event_v0",
                evidence="Last seizure on 25 December 2023",
                gan_label="unknown",
                gold_label="unknown",
            ),
            _contract_row(
                source_row_index=2,
                mechanism="benchmark_convention_renderer_v0",
                evidence="multiple focal seizures per week",
                gan_label="multiple per week",
                gold_label="multiple per week",
                component_owner="benchmark_renderer",
                benchmark_rule="gan_vague_multiple_frequency",
                candidate_exposure="typed_clinical_state_present",
            ),
        ],
        [
            _assembled_row(1, candidate_label="1 per month", gold_label="unknown"),
            _assembled_row(2, candidate_label="1 per month", gold_label="multiple per week"),
        ],
    )

    summary = boundary_benchmark_candidate_assembly.summarize_candidate_rows(rows)

    assert summary["decision"] == "candidate_contract_layer_diagnostic_only"
    assert summary["candidate_rows"] == 2
    assert summary["selected_prediction_bearing_rows"] == 2
    assert summary["w_to_c_rows"] == 2
    assert summary["c_to_w_rows"] == 0
    assert summary["parse_ok_exact_evidence_rate"] == 1.0
    assert summary["frozen_test_audit_ready"] is False
    assert summary["gate_failures"] == ["coverage_below_150", "w_to_c_below_25"]
    assert summary["holdout_authorized"] is False


def _contract_row(
    *,
    source_row_index: int,
    mechanism: str,
    evidence: str,
    gan_label: str,
    gold_label: str,
    component_owner: str = "typed_boundary_classifier",
    benchmark_rule: str = "none_boundary_state_only",
    candidate_exposure: str = "typed_boundary_event_present",
) -> dict[str, object]:
    return {
        "artifact_kind": "gan2026_boundary_benchmark_validation_contract_row",
        "source_row_index": source_row_index,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "slice_id": "fixture_slice",
        "panel_role": "hard",
        "target_family": "seizure_free_duration",
        "target_mechanism": mechanism,
        "component_owner": component_owner,
        "candidate_exposure": candidate_exposure,
        "boundary_state": "last_event_only",
        "clinical_final_state": "last_event_only",
        "gan_rendered_label": gan_label,
        "benchmark_policy_id": "gan2026_boundary_projection_policy_v0",
        "benchmark_format_rule_id": benchmark_rule,
        "evidence": evidence,
        "exact_evidence": True,
        "contract_matched": True,
        "contract_issues": [],
        "gold_label": gold_label,
        "source_note_text": None,
        "source_note_text_present": False,
        "final_label_policy_connected": False,
    }


def _assembled_row(
    source_row_index: int,
    *,
    candidate_label: str,
    gold_label: str,
) -> dict[str, object]:
    return {
        "source_row_index": source_row_index,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "candidate_label": candidate_label,
        "candidate_action": "predict",
        "candidate_purist_correct": False,
        "gold_label": gold_label,
        "component_owner": "deterministic_adapter",
    }
