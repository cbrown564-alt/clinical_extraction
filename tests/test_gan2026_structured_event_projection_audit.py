from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    structured_event_projection_audit,
)


def test_projection_audit_makes_projection_ownership_explicit() -> None:
    rows = structured_event_projection_audit.build_projection_rows(
        [
            _candidate_row(
                source_row_index=1,
                component_owner="benchmark_renderer",
                mechanism="benchmark_convention_renderer_v0",
                current_label="1 per month",
                proposed_label="multiple per week",
                gold_label="multiple per week",
                transition="W_to_C",
                benchmark_rule="gan_vague_multiple_frequency",
            )
        ]
    )

    row = rows[0]

    assert row["representation_version"] == "structured_event_projection_v0"
    assert row["clinical_event_owner"] == "typed_event_extractor"
    assert row["projection_owner"] == "benchmark_renderer"
    assert row["projection_ownership_basis"] == "benchmark_convention_renderer_v0"
    assert row["projection_policy_id"] == "gan2026_boundary_projection_policy_v0"
    assert row["benchmark_format_rule_id"] == "gan_vague_multiple_frequency"
    assert row["projection_ownership_explicit"] is True
    assert row["source_note_text"] is None
    assert row["transition"] == "W_to_C"


def test_projection_audit_carries_regression_case_as_no_regression_control() -> None:
    rows = structured_event_projection_audit.build_projection_rows(
        [
            _candidate_row(
                source_row_index=2,
                current_label="unknown",
                proposed_label="seizure free for 1 year",
                gold_label="unknown",
                transition="C_to_W",
            )
        ]
    )

    row = rows[0]

    assert row["transition"] == "C_to_W"
    assert row["no_regression_case"] is True
    assert row["projection_owner"] == "boundary_projection_policy"
    assert row["clinical_event_owner"] == "typed_boundary_classifier"


def test_projection_audit_summary_blocks_undercoverage_but_accepts_schema() -> None:
    rows = structured_event_projection_audit.build_projection_rows(
        [
            _candidate_row(
                source_row_index=1,
                current_label="unknown",
                proposed_label="1 per day",
                gold_label="1 per day",
                transition="W_to_C",
            ),
            _candidate_row(
                source_row_index=2,
                current_label="unknown",
                proposed_label="seizure free for 1 year",
                gold_label="unknown",
                transition="C_to_W",
            ),
        ]
    )

    summary = structured_event_projection_audit.summarize_projection_rows(rows)

    assert summary["representation_decision"] == "rich_structured_event_projection_layer"
    assert summary["selected_prediction_bearing_rows"] == 2
    assert summary["w_to_c_rows"] == 1
    assert summary["c_to_w_rows"] == 1
    assert summary["projection_ownership_explicit_rows"] == 2
    assert summary["no_regression_case_rows"] == 1
    assert summary["schema_ready"] is True
    assert summary["frozen_test_audit_ready"] is False
    assert summary["gate_failures"] == [
        "coverage_below_150",
        "w_to_c_below_60",
        "c_to_w_above_5_percent",
    ]


def _candidate_row(
    *,
    source_row_index: int,
    current_label: str,
    proposed_label: str,
    gold_label: str,
    transition: str,
    component_owner: str = "typed_boundary_classifier",
    mechanism: str = "seizure_free_boundary_event_v0",
    benchmark_rule: str = "none_boundary_state_only",
) -> dict[str, object]:
    return {
        "artifact_kind": "gan2026_boundary_benchmark_candidate_assembly_row",
        "source_row_index": source_row_index,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "slice_id": "fixture_slice",
        "panel_role": "hard",
        "target_family": "fixture_family",
        "target_mechanism": mechanism,
        "component_owner": component_owner,
        "component_ownership_basis": mechanism,
        "candidate_source": "typed_candidate_contract",
        "candidate_exposure": "typed_boundary_event_present",
        "event_kind": "seizure_free",
        "event_target": "seizure",
        "temporality": "current",
        "assertion_status": "asserted",
        "benchmark_policy_id": "gan2026_boundary_projection_policy_v0",
        "benchmark_format_rule_id": benchmark_rule,
        "boundary_state": "asserted_seizure_free_interval",
        "clinical_final_state": "asserted_seizure_free_interval",
        "current_label": current_label,
        "proposed_label": proposed_label,
        "gold_label": gold_label,
        "transition": transition,
        "selected_for_ablation": True,
        "prediction_bearing": True,
        "parse_ok": True,
        "exact_evidence": True,
        "evidence": "seizure free since last year",
        "source_note_text": None,
        "source_note_text_present": False,
        "contract_matched": True,
        "contract_issues": [],
        "final_label_policy_connected": False,
        "claim_boundary": "validation_development_only_no_holdout_use",
    }
