from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    boundary_benchmark_contract,
    boundary_benchmark_seed_panel,
)


def test_boundary_contract_classifies_seed_panel_rows() -> None:
    rows = boundary_benchmark_seed_panel.build_seed_panel_rows()
    boundary_row = next(row for row in rows if row["pair_id"] == "last_event_only")

    result = boundary_benchmark_contract.build_contract_row(boundary_row)

    assert result["target_mechanism"] == "seizure_free_boundary_event_v0"
    assert result["boundary_state"] == "last_event_only"
    assert result["clinical_final_state"] == "last_event_only"
    assert result["gan_rendered_label"] == "unknown"
    assert result["contract_matched"] is True
    assert result["exact_evidence"] is True


def test_renderer_contract_keeps_clinical_state_and_gan_label_separate() -> None:
    rows = boundary_benchmark_seed_panel.build_seed_panel_rows()
    renderer_row = next(row for row in rows if row["pair_id"] == "unresolved_cluster_burden")

    result = boundary_benchmark_contract.build_contract_row(renderer_row)

    assert result["target_mechanism"] == "benchmark_convention_renderer_v0"
    assert result["clinical_final_state"] == "cluster_frequency_with_unresolved_burden"
    assert result["gan_rendered_label"] == "1 cluster per 4 to 5 week, multiple per cluster"
    assert result["format_only_change"] is True
    assert result["benchmark_format_rule_id"] == "gan_cluster_multiple_per_cluster"
    assert result["contract_matched"] is True


def test_boundary_contract_preserves_pair_consistency() -> None:
    panel_rows = boundary_benchmark_seed_panel.build_seed_panel_rows()
    result_rows = boundary_benchmark_contract.build_contract_rows(panel_rows)
    summary = boundary_benchmark_contract.summarize_contract_rows(result_rows)

    assert summary["decision"] == "boundary_renderer_contract_passed"
    assert summary["row_count"] == 12
    assert summary["contract_matched_rows"] == 12
    assert summary["exact_evidence_rows"] == 12
    assert summary["clinical_state_invariant_pairs"] == 6
    assert summary["final_label_policy_connected"] is False


def test_contract_flags_unmatched_expectations() -> None:
    row = dict(boundary_benchmark_seed_panel.build_seed_panel_rows()[0])
    row["expected_boundary_state"] = "last_event_only"

    result = boundary_benchmark_contract.build_contract_row(row)

    assert result["boundary_state"] == "asserted_seizure_free_interval"
    assert result["contract_matched"] is False
    assert "boundary_state_mismatch" in result["contract_issues"]
