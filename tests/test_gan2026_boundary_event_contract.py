from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    boundary_benchmark_seed_panel,
    boundary_event_contract,
)


def test_boundary_event_contract_exposes_richer_typed_event_fields() -> None:
    panel_row = next(
        row
        for row in boundary_benchmark_seed_panel.build_seed_panel_rows()
        if row["pair_id"] == "conditional_trigger_only"
    )

    result = boundary_event_contract.build_contract_row(panel_row)

    assert result["policy_name"] == "gan2026_boundary_event_contract_v1"
    assert result["clinical_event"] == {
        "event_target": "seizure",
        "event_kind": "conditional_or_trigger_only",
        "event_state": "conditional_or_trigger_only",
        "component_owner": "typed_boundary_classifier",
    }
    assert result["boundary_state"] == "conditional_or_trigger_only"
    assert result["selected_frequency_state"] == "conditional_or_trigger_only"
    assert result["projection_policy"] == {
        "projection_policy_id": "gan2026_boundary_projection_policy_v1",
        "projection_owner": "boundary_projection_policy",
        "projection_stage": "clinical_event_to_benchmark_label",
        "benchmark_format_rule_id": "none_boundary_state_only",
    }
    assert result["gan_rendered_label"] == "unknown"
    assert result["final_label_policy_connected"] is False
    assert result["contract_matched"] is True


def test_boundary_event_contract_keeps_renderer_clinical_state_separate() -> None:
    panel_row = next(
        row
        for row in boundary_benchmark_seed_panel.build_seed_panel_rows()
        if row["pair_id"] == "unresolved_cluster_burden"
    )

    result = boundary_event_contract.build_contract_row(panel_row)

    assert result["clinical_event"]["event_kind"] == "benchmark_format_convention"
    assert (
        result["selected_frequency_state"]
        == "cluster_frequency_with_unresolved_burden"
    )
    assert result["projection_policy"]["projection_owner"] == "benchmark_renderer"
    assert (
        result["projection_policy"]["projection_policy_id"]
        == "gan2026_benchmark_renderer_policy_v1"
    )
    assert (
        result["gan_rendered_label"]
        == "1 cluster per 4 to 5 week, multiple per cluster"
    )
    assert result["contract_matched"] is True


def test_boundary_event_contract_summary_passes_without_final_policy() -> None:
    rows = boundary_event_contract.build_contract_rows(
        boundary_benchmark_seed_panel.build_seed_panel_rows()
    )
    summary = boundary_event_contract.summarize_contract_rows(rows)

    assert summary["decision"] == "boundary_event_contract_v1_passed"
    assert summary["row_count"] == 36
    assert summary["contract_matched_rows"] == 36
    assert summary["exact_evidence_rows"] == 36
    assert summary["clinical_state_invariant_pairs"] == 18
    assert summary["final_label_policy_connected"] is False
    assert summary["typed_event_complete_rows"] == 36
    assert summary["projection_policy_complete_rows"] == 36
