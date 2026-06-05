from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    boundary_renderer_component_ablation,
)


def test_boundary_renderer_ablation_separates_benchmark_only_effects() -> None:
    rows = boundary_renderer_component_ablation.build_ablation_rows(
        [
            _panel_row(
                source_row_index=1,
                mechanism="benchmark_convention_renderer_v0",
                gan_label="multiple per week",
                gold_label="multiple per week",
                component_owner="benchmark_renderer",
                benchmark_rule="gan_vague_multiple_frequency",
                selected_state="vague_multiple_current_events",
            )
        ],
        [_current_row(1, candidate_label="1 per month", h6_member=False)],
    )

    row = rows[0]

    assert row["effect_class"] == "benchmark_only_rendering"
    assert row["component_owner"] == "benchmark_renderer"
    assert row["benchmark_format_rule_id"] == "gan_vague_multiple_frequency"
    assert row["transition"] == "W_to_C"
    assert row["source_note_text"] is None
    assert row["final_label_policy_connected"] is False


def test_boundary_renderer_ablation_flags_non_convention_regression() -> None:
    rows = boundary_renderer_component_ablation.build_ablation_rows(
        [
            _panel_row(
                source_row_index=2,
                mechanism="seizure_free_boundary_event_v0",
                gan_label="unknown",
                gold_label="seizure free for 16 month",
                component_owner="typed_boundary_classifier",
                benchmark_rule="none_boundary_state_only",
                selected_state="last_event_only",
                slice_id="last_event_only",
            )
        ],
        [
            _current_row(
                2,
                candidate_label="seizure free for 16 month",
                h6_member=True,
            )
        ],
    )

    summary = boundary_renderer_component_ablation.summarize_ablation_rows(
        rows,
        [_current_row(2, candidate_label="seizure free for 16 month", h6_member=True)],
    )

    assert rows[0]["effect_class"] == "clinical_boundary_projection"
    assert rows[0]["transition"] == "C_to_W"
    assert summary["decision"] == (
        "boundary_renderer_component_ablation_v1_rejected_revise_only"
    )
    assert "c_to_w_outside_benchmark_convention" in summary["gate_failures"]
    assert "h6_control_regression" in summary["gate_failures"]
    assert summary["non_convention_c_to_w_source_row_indices"] == [2]
    assert summary["h6_control_regression_source_row_indices"] == [2]


def test_boundary_renderer_ablation_summary_reports_low_exposure() -> None:
    rows = boundary_renderer_component_ablation.build_ablation_rows(
        [
            _panel_row(
                source_row_index=1,
                mechanism="benchmark_convention_renderer_v0",
                gan_label="multiple per week",
                gold_label="multiple per week",
                component_owner="benchmark_renderer",
                benchmark_rule="gan_vague_multiple_frequency",
                selected_state="vague_multiple_current_events",
            ),
            _panel_row(
                source_row_index=2,
                mechanism="seizure_free_boundary_event_v0",
                gan_label="unknown",
                gold_label="seizure free for 16 month",
                component_owner="typed_boundary_classifier",
                benchmark_rule="none_boundary_state_only",
                selected_state="last_event_only",
                slice_id="last_event_only",
            ),
        ],
        [
            _current_row(1, candidate_label="1 per month", h6_member=False),
            _current_row(
                2,
                candidate_label="seizure free for 16 month",
                h6_member=True,
            ),
        ],
    )

    summary = boundary_renderer_component_ablation.summarize_ablation_rows(
        rows,
        [
            _current_row(1, candidate_label="1 per month", h6_member=False),
            _current_row(
                2,
                candidate_label="seizure free for 16 month",
                h6_member=True,
            ),
        ],
    )

    assert summary["selected_prediction_bearing_rows"] == 2
    assert summary["w_to_c_rows"] == 1
    assert summary["c_to_w_rows"] == 1
    assert summary["benchmark_only_transition_counts"] == {"W_to_C": 1}
    assert summary["clinical_boundary_transition_counts"] == {"C_to_W": 1}
    assert "coverage_below_150" in summary["gate_failures"]
    assert "w_to_c_below_25" in summary["gate_failures"]
    assert summary["frozen_test_audit_ready"] is False


def _panel_row(
    *,
    source_row_index: int,
    mechanism: str,
    gan_label: str,
    gold_label: str,
    component_owner: str,
    benchmark_rule: str,
    selected_state: str,
    slice_id: str = "fixture_slice",
) -> dict[str, object]:
    return {
        "artifact_kind": "gan2026_boundary_event_validation_panel_v1_row",
        "policy_name": "gan2026_boundary_event_validation_panel_v1",
        "source_row_index": source_row_index,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "slice_id": slice_id,
        "panel_role": "hard",
        "target_family": "benchmark_format_convention",
        "target_mechanism": mechanism,
        "clinical_event": {
            "event_target": "seizure",
            "event_kind": selected_state,
            "event_state": selected_state,
            "component_owner": component_owner,
        },
        "boundary_state": "not_applicable",
        "selected_frequency_state": selected_state,
        "projection_policy": {
            "projection_policy_id": "gan2026_benchmark_renderer_policy_v1",
            "projection_owner": component_owner,
            "projection_stage": "benchmark_format_rendering",
            "benchmark_format_rule_id": benchmark_rule,
        },
        "gan_rendered_label": gan_label,
        "evidence": "exact evidence",
        "exact_evidence": True,
        "gold_label": gold_label,
        "source_note_text": None,
        "source_note_text_present": False,
        "final_label_policy_connected": False,
    }


def _current_row(
    source_row_index: int,
    *,
    candidate_label: str,
    h6_member: bool,
) -> dict[str, object]:
    return {
        "source_row_index": source_row_index,
        "candidate_action": "predict",
        "candidate_label": candidate_label,
        "candidate_purist_correct": True,
        "component_owner": "deterministic_adapter",
        "h6_member": h6_member,
        "h6_panel_role": "control" if h6_member else "",
    }
