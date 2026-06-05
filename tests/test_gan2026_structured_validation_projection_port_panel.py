from __future__ import annotations

from collections import Counter

from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    structured_validation_projection_port_panel,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)


def test_validation_projection_port_panel_keeps_only_exact_evidence_rows() -> None:
    miner_rows = load_jsonl_rows(
        structured_validation_projection_port_panel.DEFAULT_MINER_JSONL_PATH
    )

    rows = structured_validation_projection_port_panel.build_validation_projection_port_rows(
        miner_rows
    )

    assert len(rows) == 47
    assert all(row["exact_evidence"] is True for row in rows)
    assert all(row["contract_issues"] == [] for row in rows)
    assert all(row["projection_ownership_explicit"] is True for row in rows)
    assert all(row["source_note_text"] is None for row in rows)
    assert all(row["source_note_text_present"] is False for row in rows)


def test_validation_projection_port_panel_balances_controls_by_target_family() -> None:
    miner_rows = load_jsonl_rows(
        structured_validation_projection_port_panel.DEFAULT_MINER_JSONL_PATH
    )

    rows = structured_validation_projection_port_panel.build_validation_projection_port_rows(
        miner_rows
    )

    hard_counts = Counter(
        row["target_family"] for row in rows if row["panel_role"] == "hard"
    )
    control_counts = Counter(
        row["target_family"] for row in rows if row["panel_role"] == "control"
    )

    assert hard_counts == control_counts
    assert hard_counts == {
        "cluster_frequency": 2,
        "daily_frequency": 7,
        "other_frequency": 5,
        "seizure_free": 2,
        "unknown_frequency": 6,
        "weekly_frequency": 1,
    }


def test_validation_projection_port_panel_summary_is_clean_but_under_gate() -> None:
    miner_rows = load_jsonl_rows(
        structured_validation_projection_port_panel.DEFAULT_MINER_JSONL_PATH
    )
    rows = structured_validation_projection_port_panel.build_validation_projection_port_rows(
        miner_rows
    )

    summary = (
        structured_validation_projection_port_panel
        .summarize_validation_projection_port_rows(rows)
    )

    assert summary["row_count"] == 47
    assert summary["hard_rows"] == 23
    assert summary["control_rows"] == 23
    assert summary["no_regression_case_rows"] == 1
    assert summary["selected_prediction_bearing_rows"] == 23
    assert summary["w_to_c_rows"] == 23
    assert summary["c_to_w_rows"] == 0
    assert summary["parse_ok_exact_evidence_rate"] == 1.0
    assert summary["frozen_test_audit_ready"] is False
    assert summary["gate_failures"] == ["coverage_below_150", "w_to_c_below_60"]
    assert (
        summary["decision"]
        == "validation_projection_port_panel_ready_for_extractor_smoke_undercoverage"
    )
