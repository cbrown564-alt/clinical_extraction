from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    validation_component_stress_ablation,
)


def test_component_stress_ablation_counts_transitions_and_nonpredictions() -> None:
    panel_rows = [
        _panel_row(
            1,
            panel_role="hard",
            baseline_correct=False,
            final_correct=True,
            baseline_label="unknown",
            final_label="1 per month",
            transition="W_to_C",
        ),
        _panel_row(
            2,
            panel_role="hard",
            baseline_correct=True,
            final_correct=None,
            baseline_label="2 per week",
            final_label=None,
            transition="C_to_abstain",
        ),
    ]

    rows = validation_component_stress_ablation.build_component_stress_ablation_rows(
        panel_rows
    )
    summary = validation_component_stress_ablation.summarize_component_stress_ablation_rows(
        rows
    )

    final_comparison = next(
        item
        for item in summary["comparisons"]
        if item["candidate"] == "staged_final_policy"
    )
    assert final_comparison["wrong_to_correct"] == 1
    assert final_comparison["correct_to_wrong"] == 0
    assert final_comparison["correct_to_nonprediction"] == 1
    assert final_comparison["wrong_to_nonprediction"] == 0
    assert summary["conditions"]["staged_prediction_bearing_only"]["rows"] == 1
    assert summary["conditions"]["staged_final_policy"]["nonprediction_rows"] == 1


def test_component_stress_ablation_preserves_h6_controls() -> None:
    panel_rows = [
        _panel_row(
            1,
            panel_role="control",
            baseline_correct=True,
            final_correct=True,
            baseline_label="1 per week",
            final_label="1 per week",
            transition="C_to_C",
        )
    ]

    rows = validation_component_stress_ablation.build_component_stress_ablation_rows(
        panel_rows
    )
    summary = validation_component_stress_ablation.summarize_component_stress_ablation_rows(
        rows
    )

    assert summary["h6_control_summary"] == {
        "control_rows": 1,
        "preserved_correct_rows": 1,
        "regression_rows": 0,
        "nonprediction_regression_rows": 0,
    }
    assert summary["locked_test_row_level_artifacts_used"] == 0
    assert summary["decision"] == (
        "diagnostic_ablation_passed_h6_controls_but_nonprediction_pressure_remains"
    )


def test_component_stress_ablation_rows_keep_validation_claim_boundary() -> None:
    rows = validation_component_stress_ablation.build_component_stress_ablation_rows(
        [
            {
                **_panel_row(
                    1,
                    panel_role="control",
                    baseline_correct=True,
                    final_correct=True,
                    baseline_label="1 per week",
                    final_label="1 per week",
                    transition="C_to_C",
                ),
                "split": "test",
                "distribution": "locked_test450",
            }
        ]
    )

    assert {row["claim_boundary"] for row in rows} == {
        "validation_development_only_no_holdout_row_level_use"
    }
    assert all(row["split_manifest"] == "gan2026_split_v1" for row in rows)


def _panel_row(
    source_row_index: int,
    *,
    panel_role: str,
    baseline_correct: bool,
    final_correct: bool | None,
    baseline_label: str,
    final_label: str | None,
    transition: str,
) -> dict[str, object]:
    return {
        "source_row_index": source_row_index,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "distribution": "validation750",
        "panel_role": panel_role,
        "component_owner": "deterministic_adapter",
        "clinical_subproblem": "adapter_rendering",
        "primary_hidden_family": "current_vs_historical",
        "hidden_families": ["current_vs_historical"],
        "baseline_transition": transition,
        "gold_label": "1 per month",
        "baseline_label": baseline_label,
        "final_label": final_label,
        "baseline_purist_correct": baseline_correct,
        "final_purist_correct": final_correct,
        "purist_correct": final_correct,
        "evidence_exact": final_label is not None,
        "source_ids_valid": final_label is not None,
        "parse_valid": True,
        "schema_valid": True,
    }
