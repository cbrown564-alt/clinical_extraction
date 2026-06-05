from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    nonprediction_release_candidate,
)


def test_release_candidate_releases_only_untagged_nonpredictions() -> None:
    rows = nonprediction_release_candidate.build_release_candidate_rows(
        [
            _component_row(
                1,
                final_action="abstain",
                hidden_families="",
                transition="C_to_abstain",
                baseline_label="unknown",
                baseline_correct=True,
            ),
            _component_row(
                2,
                final_action="abstain",
                hidden_families="seizure_free_duration",
                transition="W_to_abstain",
                baseline_label="seizure free for 6 month",
                baseline_correct=False,
            ),
        ],
        [{"source_row_index": 1}],
    )

    assert rows[0]["release_applied"] is True
    assert rows[0]["candidate_action"] == "predict"
    assert rows[0]["candidate_label"] == "unknown"
    assert rows[0]["candidate_purist_correct"] is True
    assert rows[0]["surface_membership"] == "h2_h4_component_stress_panel"
    assert rows[1]["release_applied"] is False
    assert rows[1]["candidate_action"] == "abstain"
    assert rows[1]["candidate_label"] is None


def test_release_candidate_summary_passes_no_regression_gate() -> None:
    rows = nonprediction_release_candidate.build_release_candidate_rows(
        [
            _component_row(
                1,
                final_action="abstain",
                hidden_families="",
                transition="C_to_abstain",
                baseline_label="unknown",
                baseline_correct=True,
            ),
            _component_row(
                2,
                final_action="predict",
                hidden_families="",
                transition="C_to_C",
                baseline_label="1 per week",
                baseline_correct=True,
                prediction_label="1 per week",
                final_correct=True,
            ),
        ],
        [{"source_row_index": 1}, {"source_row_index": 2}],
    )

    summary = nonprediction_release_candidate.summarize_release_candidate_rows(rows)

    assert summary["release_rows"] == 1
    assert summary["release_wrong_rows"] == 0
    assert summary["h6_control_rows"] == 1
    assert summary["h6_control_regression_rows"] == 0
    assert summary["decision"] == "candidate_patch_passes_validation_no_regression_gate"
    assert summary["locked_test_row_level_artifacts_used"] == 0


def _component_row(
    source_row_index: int,
    *,
    final_action: str,
    hidden_families: str,
    transition: str,
    baseline_label: str,
    baseline_correct: bool,
    prediction_label: str = "",
    final_correct: bool | None = None,
) -> dict[str, object]:
    return {
        "candidate_version": "hybrid_multi_component_staged_assembly_v0",
        "source_row_index": str(source_row_index),
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "gold_label": "unknown",
        "final_action": final_action,
        "prediction_bearing": str(final_action == "predict"),
        "prediction_label": prediction_label,
        "deterministic_comparator_label": baseline_label,
        "deterministic_comparator_purist_correct": str(baseline_correct),
        "final_purist_correct": "" if final_correct is None else str(final_correct),
        "comparator_transition": transition,
        "hidden_families": hidden_families,
        "router_reason": "trigger_conditioned_frequency",
    }
