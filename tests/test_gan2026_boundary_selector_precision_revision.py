from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    boundary_selector_precision_revision,
)


def test_selector_revision_suppresses_last_event_seizure_free_override() -> None:
    rows = boundary_selector_precision_revision.build_revision_rows(
        [
            _ablation_row(
                source_row_index=2965,
                slice_id="last_event_only",
                current_label="seizure free for 16 month",
                proposed_label="unknown",
                transition="C_to_W",
                h6_member=True,
            )
        ]
    )

    row = rows[0]

    assert row["selected_for_ablation"] is False
    assert row["prediction_bearing"] is False
    assert row["transition"] == "not_selected"
    assert row["selector_reason"] == "last_event_current_seizure_free_protected"
    assert row["final_label_policy_connected"] is False


def test_selector_revision_suppresses_unknown_no_reference_churn() -> None:
    rows = boundary_selector_precision_revision.build_revision_rows(
        [
            _ablation_row(
                source_row_index=7455,
                slice_id="unknown_sentinel",
                current_label="no seizure frequency reference",
                proposed_label="unknown",
                transition="C_to_C",
            )
        ]
    )

    assert rows[0]["selected_for_ablation"] is False
    assert rows[0]["selector_reason"] == "unknown_no_reference_sentinel_churn"


def test_selector_revision_summary_fixes_precision_but_keeps_low_coverage_gate() -> None:
    rows = boundary_selector_precision_revision.build_revision_rows(
        [
            _ablation_row(
                source_row_index=2965,
                slice_id="last_event_only",
                current_label="seizure free for 16 month",
                proposed_label="unknown",
                transition="C_to_W",
                h6_member=True,
            ),
            _ablation_row(
                source_row_index=11216,
                slice_id="last_event_only",
                current_label="",
                proposed_label="unknown",
                transition="W_to_C",
            ),
        ]
    )

    summary = boundary_selector_precision_revision.summarize_revision_rows(rows)

    assert summary["decision"] == (
        "boundary_selector_precision_revision_v1_precision_fixed_low_coverage"
    )
    assert summary["selected_prediction_bearing_rows"] == 1
    assert summary["suppressed_rows"] == 1
    assert summary["w_to_c_rows"] == 1
    assert summary["c_to_w_rows"] == 0
    assert summary["h6_control_regression_rows"] == 0
    assert summary["non_convention_c_to_w_rows"] == 0
    assert summary["gate_failures"] == ["coverage_below_150", "w_to_c_below_25"]
    assert summary["frozen_test_audit_ready"] is False


def _ablation_row(
    *,
    source_row_index: int,
    slice_id: str,
    current_label: str,
    proposed_label: str,
    transition: str,
    h6_member: bool = False,
) -> dict[str, object]:
    return {
        "artifact_kind": "gan2026_boundary_renderer_component_ablation_v1_row",
        "policy_name": "gan2026_boundary_renderer_component_ablation_v1",
        "source_row_index": source_row_index,
        "slice_id": slice_id,
        "effect_class": "clinical_boundary_projection",
        "current_label": current_label,
        "proposed_label": proposed_label,
        "transition": transition,
        "selected_for_ablation": True,
        "prediction_bearing": True,
        "h6_member": h6_member,
        "final_label_policy_connected": False,
    }
