from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    validation_component_stress_panel,
)


def test_component_stress_panel_selects_hard_rows_and_matched_controls() -> None:
    rows = [
        _final_row(
            1,
            owner="deterministic_adapter",
            subproblem="adapter_rendering",
            family="current_vs_historical",
            transition="W_to_W",
            purist_correct=False,
        ),
        _final_row(
            2,
            owner="deterministic_adapter",
            subproblem="adapter_rendering",
            family="current_vs_historical",
            transition="C_to_C",
            purist_correct=True,
            baseline_purist_correct=True,
        ),
        _final_row(
            3,
            owner="deterministic_adapter",
            subproblem="adapter_rendering",
            family="none",
            transition="C_to_C",
            purist_correct=True,
            baseline_purist_correct=True,
        ),
    ]

    panel_rows = validation_component_stress_panel.build_component_stress_panel_rows(rows)
    summary = validation_component_stress_panel.summarize_component_stress_panel_rows(panel_rows)

    assert summary["decision"] == "ready_for_component_stress_ablation"
    assert summary["hard_rows"] == 1
    assert summary["control_rows"] == 1
    assert summary["locked_test_row_level_artifacts_used"] == 0
    control = next(row for row in panel_rows if row["panel_role"] == "control")
    assert control["source_row_index"] == 2
    assert control["match_quality"] == "owner_subproblem_family"
    assert control["hypothesis_ids"] == ["H2", "H4", "H6"]
    assert control["source_note_text"] is None


def test_component_stress_panel_uses_untagged_owner_subproblem_controls() -> None:
    rows = [
        _final_row(
            1,
            owner="safety_floor",
            subproblem="final_policy",
            family="unknown_boundary",
            transition="W_to_review",
            purist_correct=None,
        ),
        _final_row(
            2,
            owner="safety_floor",
            subproblem="final_policy",
            family="none",
            transition="C_to_C",
            purist_correct=True,
            baseline_purist_correct=True,
        ),
    ]

    panel_rows = validation_component_stress_panel.build_component_stress_panel_rows(rows)

    hard = next(row for row in panel_rows if row["panel_role"] == "hard")
    control = next(row for row in panel_rows if row["panel_role"] == "control")
    assert hard["stress_target"] == "action_policy_nonprediction"
    assert hard["expected_panel_use"] == (
        "candidate_must_choose_predict_or_preserve_review_with_reason"
    )
    assert control["match_quality"] == "owner_subproblem_untagged"


def test_component_stress_panel_refuses_locked_test_rows() -> None:
    rows = [
        {
            **_final_row(
                1,
                owner="deterministic_adapter",
                subproblem="adapter_rendering",
                family="current_vs_historical",
                transition="W_to_W",
                purist_correct=False,
            ),
            "split": "test",
            "distribution": "locked_test450",
        }
    ]

    panel_rows = validation_component_stress_panel.build_component_stress_panel_rows(rows)
    summary = validation_component_stress_panel.summarize_component_stress_panel_rows(panel_rows)

    assert panel_rows == []
    assert summary["locked_test_row_level_artifacts_used"] == 0
    assert summary["decision"] == "panel_contract_failed"


def _final_row(
    source_row_index: int,
    *,
    owner: str,
    subproblem: str,
    family: str,
    transition: str,
    purist_correct: bool | None,
    baseline_purist_correct: bool = False,
) -> dict[str, object]:
    return {
        "score_layer": "final_policy",
        "source_row_index": source_row_index,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "distribution": "validation750",
        "component_owner": owner,
        "clinical_subproblem": subproblem,
        "hidden_families": [] if family == "none" else [family],
        "baseline_to_layer_transition": transition,
        "purist_correct": purist_correct,
        "baseline_purist_correct": baseline_purist_correct,
        "final_purist_correct": purist_correct,
        "evidence_exact": True,
        "source_ids_valid": True,
        "parse_valid": True,
        "schema_valid": True,
        "gold_label": "1 per month",
        "baseline_label": "unknown",
        "final_label": "unknown",
        "first_failure_owner": "",
        "first_failure_reason": "",
    }
