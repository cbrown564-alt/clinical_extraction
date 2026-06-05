from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    boundary_benchmark_seed_panel,
)


def test_boundary_benchmark_seed_panel_has_both_mechanisms() -> None:
    rows = boundary_benchmark_seed_panel.build_seed_panel_rows()
    summary = boundary_benchmark_seed_panel.summarize_seed_panel_rows(rows)

    assert summary["decision"] == "ready_for_boundary_renderer_contract_tests"
    assert summary["boundary_rows"] == 6
    assert summary["renderer_rows"] == 6
    assert summary["exact_evidence_rows"] == summary["row_count"]


def test_boundary_pairs_preserve_expected_clinical_state() -> None:
    rows = boundary_benchmark_seed_panel.build_seed_panel_rows()
    pairs = {}
    for row in rows:
        pairs.setdefault(row["pair_id"], set()).add(row["expected_clinical_final_state"])

    assert all(len(states) == 1 for states in pairs.values())
    assert pairs["last_event_only"] == {"last_event_only"}
    assert pairs["residual_active_semiology"] == {"active_residual_seizure_frequency"}


def test_renderer_rows_are_format_transparent() -> None:
    rows = boundary_benchmark_seed_panel.build_seed_panel_rows()
    renderer_rows = [
        row
        for row in rows
        if row["target_mechanism"] == "benchmark_convention_renderer_v0"
    ]

    assert renderer_rows
    assert all(row["expected_format_only_change"] is True for row in renderer_rows)
    assert all(
        row["expected_benchmark_format_rule_id"] != "none_boundary_state_only"
        for row in renderer_rows
    )
    assert {row["expected_gan_rendered_label"] for row in renderer_rows} >= {
        "1 cluster per 4 to 5 week, multiple per cluster",
        "multiple per month",
        "unknown",
    }


def test_panel_does_not_promote_final_label_policy() -> None:
    rows = boundary_benchmark_seed_panel.build_seed_panel_rows()

    assert {
        row["promotion_scope"] for row in rows
    } == {"panel_seed_only_no_final_label_promotion"}
