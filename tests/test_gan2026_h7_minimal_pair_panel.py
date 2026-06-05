from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    boundary_benchmark_seed_panel,
    boundary_event_contract,
    h7_minimal_pair_panel,
)


def test_h7_minimal_pair_rows_preserve_typed_state_across_axis() -> None:
    contract_rows = boundary_event_contract.build_contract_rows(
        boundary_benchmark_seed_panel.build_seed_panel_rows()
    )

    rows = h7_minimal_pair_panel.build_minimal_pair_rows(contract_rows)

    pair_rows = [
        row for row in rows if row["pair_id"] == "residual_active_semiology"
    ]
    assert {row["perturbation_axis"] for row in pair_rows} == {"order_semiology"}
    assert {row["selected_frequency_state"] for row in pair_rows} == {
        "active_residual_seizure_frequency"
    }
    assert {row["clinical_event"]["event_state"] for row in pair_rows} == {
        "active_residual_seizure_frequency"
    }
    assert {row["gan_rendered_label"] for row in pair_rows} == {"2 per week"}
    assert {row["final_label_policy_connected"] for row in pair_rows} == {False}


def test_h7_minimal_pair_summary_passes_all_seed_pairs() -> None:
    rows = h7_minimal_pair_panel.build_minimal_pair_rows(
        boundary_event_contract.build_contract_rows(
            boundary_benchmark_seed_panel.build_seed_panel_rows()
        )
    )

    summary = h7_minimal_pair_panel.summarize_minimal_pair_rows(rows)

    assert summary["decision"] == "h7_minimal_pair_panel_v1_passed"
    assert summary["row_count"] == 36
    assert summary["pair_count"] == 18
    assert summary["complete_pairs"] == 18
    assert summary["clinical_state_invariant_pairs"] == 18
    assert summary["exact_evidence_rows"] == 36
    assert summary["final_label_policy_connected"] is False
    assert summary["inconsistent_pair_ids"] == []
    assert summary["perturbation_axis_pair_counts"]["order"] == 3
    assert summary["perturbation_axis_pair_counts"]["order_semiology"] == 2
    assert summary["perturbation_axis_pair_counts"]["wording"] == 5


def test_h7_minimal_pair_summary_fails_inconsistent_pair() -> None:
    rows = h7_minimal_pair_panel.build_minimal_pair_rows(
        boundary_event_contract.build_contract_rows(
            boundary_benchmark_seed_panel.build_seed_panel_rows()
        )
    )
    broken_rows = [dict(row) for row in rows]
    for row in broken_rows:
        if row["pair_id"] == "last_event_only":
            row["selected_frequency_state"] = "seizure_free_interval"
            break

    summary = h7_minimal_pair_panel.summarize_minimal_pair_rows(broken_rows)

    assert summary["decision"] == "h7_minimal_pair_panel_v1_failed"
    assert summary["inconsistent_pair_ids"] == ["last_event_only"]
