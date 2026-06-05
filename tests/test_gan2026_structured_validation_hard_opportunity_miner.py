from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    structured_validation_hard_opportunity_miner,
)


def test_hard_opportunity_miner_selects_residual_misses_and_controls() -> None:
    rows = structured_validation_hard_opportunity_miner.build_opportunity_rows(
        [
            _assembled_row(1, "seizure free for multiple year", "unknown", False),
            _assembled_row(2, "1 per month", "1 cluster per month, multiple per cluster", False),
            _assembled_row(3, "unknown", "unknown", True),
            _assembled_row(4, "1 per month", "1 per month", True),
        ],
        {
            1: _record(1, "unknown", "trigger-only seizures"),
            2: _record(2, "1 cluster per month, multiple per cluster", "monthly clusters"),
            3: _record(3, "unknown", "frequency unclear"),
            4: _record(4, "1 per month", "one seizure per month"),
        },
    )

    hard_rows = [row for row in rows if row["panel_role"] == "hard"]
    control_rows = [row for row in rows if row["panel_role"] == "control"]

    assert len(hard_rows) == 2
    assert len(control_rows) == 2
    assert {row["projection_owner"] for row in hard_rows} == {
        "boundary_projection_policy",
        "cluster_projection_policy",
    }
    assert all(row["transition"] == "W_to_C" for row in hard_rows)
    assert all(row["transition"] == "not_selected" for row in control_rows)
    assert all(row["source_note_text"] is None for row in rows)


def test_hard_opportunity_summary_reports_w_to_c_ceiling() -> None:
    rows = [
        _opportunity_row(1, "hard", "W_to_C"),
        _opportunity_row(2, "hard", "W_to_C"),
        _opportunity_row(3, "control", "not_selected"),
        _opportunity_row(4, "control", "not_selected"),
        _opportunity_row(5, "no_regression", "not_selected", no_regression=True),
    ]

    summary = structured_validation_hard_opportunity_miner.summarize_opportunity_rows(rows)

    assert summary["hard_rows"] == 2
    assert summary["control_rows"] == 2
    assert summary["no_regression_case_rows"] == 1
    assert summary["selected_prediction_bearing_rows"] == 2
    assert summary["w_to_c_rows"] == 2
    assert summary["w_to_c_gate_reachable_on_current_surface"] is False
    assert summary["gate_failures"] == ["coverage_below_150", "w_to_c_below_25"]


def _assembled_row(
    source_row_index: int,
    candidate_label: str,
    gold_label: str,
    candidate_purist_correct: bool,
) -> dict[str, object]:
    return {
        "source_row_index": source_row_index,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "candidate_label": candidate_label,
        "candidate_action": "predict",
        "candidate_purist_correct": candidate_purist_correct,
        "gold_label": gold_label,
    }


def _record(source_row_index: int, gold_label: str, gold_reference: str) -> dict[str, object]:
    return {
        "source_row_index": source_row_index,
        "gold_label": gold_label,
        "gold_reference": gold_reference,
        "note_text": f"Clinical note. {gold_reference}.",
    }


def _opportunity_row(
    source_row_index: int,
    panel_role: str,
    transition: str,
    *,
    no_regression: bool = False,
) -> dict[str, object]:
    return {
        "source_row_index": source_row_index,
        "panel_role": panel_role,
        "projection_owner": "boundary_projection_policy",
        "prediction_bearing": panel_role == "hard",
        "transition": transition,
        "parse_ok": True,
        "exact_evidence": True,
        "contract_issues": [],
        "projection_ownership_explicit": True,
        "source_note_text_present": False,
        "no_regression_case": no_regression,
    }
