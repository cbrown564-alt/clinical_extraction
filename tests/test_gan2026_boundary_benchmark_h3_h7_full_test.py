from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    boundary_benchmark_h3_h7_full_test,
)


def test_full_test_summary_rejects_undercovered_h3_and_supports_h7() -> None:
    synthetic_rows = [
        _synthetic_row("pair_a", "stable", "old_a"),
        _synthetic_row("pair_a", "stable", "old_b"),
    ]
    validation_contract_rows = [
        _validation_contract_row(1),
        _validation_contract_row(2),
    ]
    validation_candidate_rows = [
        _validation_candidate_row(1, transition="W_to_C"),
        _validation_candidate_row(2, transition="C_to_C"),
    ]

    summary = boundary_benchmark_h3_h7_full_test.summarize_full_test(
        synthetic_rows=synthetic_rows,
        validation_contract_rows=validation_contract_rows,
        validation_candidate_rows=validation_candidate_rows,
    )

    assert summary["h3_status"] == "tested_rejected_for_current_typed_layer"
    assert summary["h7_status"] == "tested_supported_for_deterministic_template_brittleness"
    assert (
        summary["h8_status"]
        == "tested_partial_validation_support_for_benchmark_convention_subset"
    )
    assert summary["deterministic_flip_pairs"] == 1
    assert summary["typed_pair_consistent_pairs"] == 1
    assert summary["validation_candidate_present_rows"] == 2
    assert summary["validation_transition_counts"] == {"C_to_C": 1, "W_to_C": 1}
    assert summary["h8_validation_rows"] == 1
    assert summary["h8_transition_counts"] == {"C_to_C": 1}
    assert summary["h8_benchmark_rule_counts"] == {"gan_vague_multiple_frequency": 1}
    assert summary["h8_clinical_rendering_separated_rows"] == 1
    assert summary["locked_test_row_level_artifacts_used"] == 0
    assert summary["holdout_authorized"] is False


def test_full_test_summary_flags_absent_template_flips() -> None:
    synthetic_rows = [
        _synthetic_row("pair_a", "stable", "old_a"),
        _synthetic_row("pair_a", "stable", "old_a"),
    ]

    summary = boundary_benchmark_h3_h7_full_test.summarize_full_test(
        synthetic_rows=synthetic_rows,
        validation_contract_rows=[_validation_contract_row(1)],
        validation_candidate_rows=[_validation_candidate_row(1, transition="C_to_C")],
    )

    assert summary["h7_status"] == "tested_not_supported_on_current_pair_panel"
    assert summary["h7_gate_failures"] == ["no_deterministic_template_flips_observed"]


def _synthetic_row(pair_id: str, typed_label: str, deterministic_label: str) -> dict[str, object]:
    return {
        "pair_id": pair_id,
        "typed_label": typed_label,
        "deterministic_label": deterministic_label,
        "typed_correct": True,
        "deterministic_correct": False,
        "target_mechanism": "seizure_free_boundary_event_v0",
    }


def _validation_contract_row(source_row_index: int) -> dict[str, object]:
    return {
        "source_row_index": source_row_index,
        "contract_matched": True,
        "exact_evidence": True,
        "contract_issues": [],
    }


def _validation_candidate_row(source_row_index: int, *, transition: str) -> dict[str, object]:
    is_benchmark_row = source_row_index == 2
    return {
        "source_row_index": source_row_index,
        "selected_for_ablation": True,
        "transition": transition,
        "candidate_exposure": (
            "typed_clinical_state_present"
            if is_benchmark_row
            else "typed_boundary_event_present"
        ),
        "target_mechanism": (
            "benchmark_convention_renderer_v0"
            if is_benchmark_row
            else "seizure_free_boundary_event_v0"
        ),
        "slice_id": "vague_multiple_frequency" if is_benchmark_row else "last_event_only",
        "event_kind": "frequency_rate" if is_benchmark_row else "last_event_only",
        "event_target": "seizure",
        "temporality": "current" if is_benchmark_row else "historical",
        "assertion_status": "asserted" if is_benchmark_row else "uncertain",
        "benchmark_policy_id": "gan2026_boundary_projection_policy_v0",
        "benchmark_format_rule_id": (
            "gan_vague_multiple_frequency"
            if is_benchmark_row
            else "none_boundary_state_only"
        ),
        "component_owner": (
            "benchmark_renderer" if is_benchmark_row else "typed_boundary_classifier"
        ),
        "clinical_final_state": (
            "vague_multiple_current_events"
            if is_benchmark_row
            else "last_event_only"
        ),
        "proposed_label": "multiple per month" if is_benchmark_row else "unknown",
        "exact_evidence": True,
        "source_note_text_present": False,
    }
