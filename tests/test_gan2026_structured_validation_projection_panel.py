from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    structured_validation_projection_panel,
)


def test_validation_projection_panel_maps_seed_rows_to_owner_schema() -> None:
    rows = structured_validation_projection_panel.build_validation_projection_rows(
        [
            _seed_row(
                source_row_index=1,
                seed_family="yearly_to_daily",
                panel_role="hard",
                expected_action="emit_candidate",
                current_label="4 per year",
                gold_label="1 per day",
                expected_candidate_label="1 per day",
            )
        ],
        [],
    )

    row = rows[0]

    assert row["representation_version"] == "structured_event_projection_v0"
    assert row["panel_source"] == "structured_seed_validation_panel_v0"
    assert row["clinical_event_owner"] == "typed_event_extractor"
    assert row["projection_owner"] == "rate_projection_policy"
    assert row["projection_ownership_explicit"] is True
    assert row["selected_for_ablation"] is True
    assert row["transition"] == "W_to_C"
    assert row["source_note_text_present"] is False


def test_validation_projection_panel_preserves_suppress_controls() -> None:
    rows = structured_validation_projection_panel.build_validation_projection_rows(
        [
            _seed_row(
                source_row_index=2,
                seed_family="cluster_completion",
                panel_role="control",
                expected_action="suppress_candidate",
                current_label="1 per month",
                gold_label="1 per month",
                expected_candidate_label=None,
                unsafe_candidate_label="1 cluster per month, multiple per cluster",
            )
        ],
        [],
    )

    row = rows[0]

    assert row["projection_owner"] == "cluster_projection_policy"
    assert row["generator_action"] == "suppress_candidate"
    assert row["selected_for_ablation"] is False
    assert row["prediction_bearing"] is False
    assert row["transition"] == "not_selected"


def test_validation_projection_panel_carries_no_regression_rows() -> None:
    rows = structured_validation_projection_panel.build_validation_projection_rows(
        [],
        [_projection_audit_row()],
    )

    row = rows[0]

    assert row["panel_source"] == "structured_event_projection_audit_v0"
    assert row["panel_role"] == "no_regression"
    assert row["projection_owner"] == "boundary_projection_policy"
    assert row["no_regression_case"] is True
    assert row["transition"] == "C_to_W"
    assert row["selected_for_ablation"] is True


def test_validation_projection_panel_summary_blocks_undercovered_validation() -> None:
    rows = structured_validation_projection_panel.build_validation_projection_rows(
        [
            _seed_row(
                source_row_index=1,
                seed_family="yearly_to_daily",
                panel_role="hard",
                expected_action="emit_candidate",
                current_label="4 per year",
                gold_label="1 per day",
                expected_candidate_label="1 per day",
            ),
            _seed_row(
                source_row_index=2,
                seed_family="yearly_to_daily",
                panel_role="control",
                expected_action="suppress_candidate",
                current_label="4 per year",
                gold_label="4 per year",
                expected_candidate_label=None,
                unsafe_candidate_label="1 per day",
            ),
        ],
        [_projection_audit_row()],
    )

    summary = structured_validation_projection_panel.summarize_validation_projection_rows(
        rows
    )

    assert summary["row_count"] == 3
    assert summary["hard_rows"] == 1
    assert summary["control_rows"] == 1
    assert summary["no_regression_case_rows"] == 1
    assert summary["selected_prediction_bearing_rows"] == 2
    assert summary["w_to_c_rows"] == 1
    assert summary["c_to_w_rows"] == 1
    assert summary["projection_ownership_explicit_rows"] == 3
    assert summary["frozen_test_audit_ready"] is False
    assert summary["gate_failures"] == [
        "coverage_below_150",
        "w_to_c_below_25",
        "c_to_w_above_5_percent",
    ]


def _seed_row(
    *,
    source_row_index: int,
    seed_family: str,
    panel_role: str,
    expected_action: str,
    current_label: str,
    gold_label: str,
    expected_candidate_label: str | None,
    unsafe_candidate_label: str | None = None,
) -> dict[str, object]:
    return {
        "artifact_kind": "gan2026_structured_seed_validation_panel_row",
        "source_row_index": source_row_index,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "panel_role": panel_role,
        "seed_family": seed_family,
        "expected_generator_action": expected_action,
        "current_label": current_label,
        "gold_label": gold_label,
        "expected_candidate_label": expected_candidate_label,
        "unsafe_candidate_label": unsafe_candidate_label,
        "expected_evidence_substring": "bounded validation evidence",
        "source_note_text": None,
        "claim_boundary": "validation_development_only_no_holdout_use",
    }


def _projection_audit_row() -> dict[str, object]:
    return {
        "artifact_kind": "gan2026_structured_event_projection_audit_row",
        "source_row_index": 3,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "slice_id": "last_event_only",
        "panel_role": "hard",
        "target_family": "seizure_free_duration",
        "target_mechanism": "seizure_free_boundary_event_v0",
        "clinical_event_owner": "typed_boundary_classifier",
        "clinical_event_kind": "last_event_only",
        "clinical_event_target": "seizure",
        "temporality": "historical",
        "assertion_status": "uncertain",
        "projection_owner": "boundary_projection_policy",
        "projection_ownership_basis": "seizure_free_boundary_event_v0",
        "projection_stage": "clinical_event_to_benchmark_label",
        "projection_policy_id": "gan2026_boundary_projection_policy_v0",
        "benchmark_format_rule_id": "none_boundary_state_only",
        "clinical_final_state": "last_event_only",
        "boundary_state": "last_event_only",
        "current_label": "seizure free for 16 month",
        "projection_input_label": "seizure free for 16 month",
        "gan_rendered_label": "unknown",
        "proposed_label": "unknown",
        "gold_label": "seizure free for 16 month",
        "transition": "C_to_W",
        "no_regression_case": True,
        "selected_for_ablation": True,
        "prediction_bearing": True,
        "parse_ok": True,
        "exact_evidence": True,
        "evidence": "Last seizure on 03-Sep-2017",
        "source_note_text": None,
        "source_note_text_present": False,
        "contract_matched": True,
        "contract_issues": [],
        "projection_ownership_explicit": True,
        "final_label_policy_connected": False,
        "claim_boundary": "validation_development_only_no_holdout_use",
    }
