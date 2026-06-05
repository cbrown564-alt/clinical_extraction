from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    benchmark_renderer_fixture,
    boundary_benchmark_contract,
    boundary_benchmark_seed_panel,
)


def test_benchmark_renderer_fixture_freezes_clinical_state() -> None:
    rows = benchmark_renderer_fixture.build_fixture_rows(_contract_rows())

    cluster_row = next(row for row in rows if row["pair_id"] == "unresolved_cluster_burden")

    assert cluster_row["component_owner"] == "benchmark_renderer"
    assert (
        cluster_row["input_clinical_state"]
        == "cluster_frequency_with_unresolved_burden"
    )
    assert (
        cluster_row["output_clinical_state"]
        == "cluster_frequency_with_unresolved_burden"
    )
    assert cluster_row["clinical_state_preserved"] is True
    assert (
        cluster_row["gan_rendered_label"]
        == "1 cluster per 4 to 5 week, multiple per cluster"
    )
    assert cluster_row["benchmark_format_rule_id"] == (
        "gan_cluster_multiple_per_cluster"
    )
    assert cluster_row["format_only_change"] is True
    assert cluster_row["final_label_policy_connected"] is False


def test_benchmark_renderer_fixture_exposes_sentinel_visibility() -> None:
    rows = benchmark_renderer_fixture.build_fixture_rows(_contract_rows())

    assert {row["scorer_sentinel_used"] for row in rows} == {False, True}
    assert {
        row["benchmark_format_rule_id"]
        for row in rows
        if row["scorer_sentinel_used"] is True
    } >= {
        "gan_cluster_multiple_per_cluster",
        "gan_unknown_sentinel",
        "gan_vague_multiple_frequency",
    }


def test_benchmark_renderer_fixture_summary_passes() -> None:
    rows = benchmark_renderer_fixture.build_fixture_rows(_contract_rows())

    summary = benchmark_renderer_fixture.summarize_fixture_rows(rows)

    assert summary["decision"] == "benchmark_renderer_fixture_v1_passed"
    assert summary["row_count"] == 16
    assert summary["clinical_state_preserved_rows"] == 16
    assert summary["format_only_rows"] == 16
    assert summary["renderer_rule_id_rows"] == 16
    assert summary["sentinel_visibility_rows"] == 16
    assert summary["scorer_sentinel_used_rows"] == 14
    assert summary["exact_evidence_rows"] == 16
    assert summary["contract_matched_rows"] == 16
    assert summary["final_label_policy_connected"] is False
    assert summary["benchmark_rule_counts"] == {
        "gan_cluster_multiple_per_cluster": 6,
        "gan_non_epileptic_seizure_free_projection": 2,
        "gan_unknown_sentinel": 4,
        "gan_vague_multiple_frequency": 4,
    }


def test_benchmark_renderer_fixture_fails_if_state_changes() -> None:
    rows = [dict(row) for row in benchmark_renderer_fixture.build_fixture_rows(_contract_rows())]
    rows[0]["output_clinical_state"] = "unknown_frequency"
    rows[0]["clinical_state_preserved"] = False

    summary = benchmark_renderer_fixture.summarize_fixture_rows(rows)

    assert summary["decision"] == "benchmark_renderer_fixture_v1_failed"
    assert summary["clinical_state_preserved_rows"] == 15


def _contract_rows() -> list[dict[str, object]]:
    return boundary_benchmark_contract.build_contract_rows(
        boundary_benchmark_seed_panel.build_seed_panel_rows()
    )
