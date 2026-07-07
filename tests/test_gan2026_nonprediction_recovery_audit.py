from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    nonprediction_recovery_audit,
)


def test_recovery_audit_selects_untagged_nonprediction_lane() -> None:
    rows = nonprediction_recovery_audit.build_recovery_audit_rows(
        [
            _component_row(
                1,
                hidden_families="",
                transition="C_to_abstain",
                baseline_label="unknown",
                baseline_correct=True,
            ),
            _component_row(
                2,
                hidden_families="seizure_free_duration|unknown_boundary",
                transition="W_to_abstain",
                baseline_label="seizure free for 6 month",
                baseline_correct=False,
            ),
        ],
        [{"source_row_index": 1}],
    )
    summary = nonprediction_recovery_audit.summarize_recovery_audit_rows(rows)

    assert rows[0]["release_lanes"] == [
        "untagged_nonprediction",
        "sentinel_untagged_nonprediction",
        "trigger_untagged_nonprediction",
    ]
    assert rows[0]["surface_membership"] == "h2_h4_component_stress_panel"
    assert rows[1]["release_lanes"] == []
    assert summary["selected_candidate_lane"]["variant"] == "untagged_nonprediction"
    assert summary["selected_candidate_lane"]["release_rows"] == 1
    assert summary["selected_candidate_lane"]["would_release_wrong_baseline"] == 0
    assert summary["decision"] == "candidate_lane_passes_validation_no_regression_audit"


def test_recovery_audit_keeps_broad_release_visible_as_unsafe() -> None:
    rows = nonprediction_recovery_audit.build_recovery_audit_rows(
        [
            _component_row(
                1,
                hidden_families="",
                transition="C_to_abstain",
                baseline_label="unknown",
                baseline_correct=True,
            ),
            _component_row(
                2,
                hidden_families="current_vs_historical",
                transition="W_to_review",
                baseline_label="seizure free for multiple year",
                baseline_correct=False,
                router_reason="last_event_boundary",
                final_action="human_review",
            ),
        ],
    )

    summary = nonprediction_recovery_audit.summarize_recovery_audit_rows(rows)

    broad = next(
        item for item in summary["variant_summaries"] if item["variant"] == "all_nonpredictions"
    )
    assert broad["release_rows"] == 2
    assert broad["would_release_wrong_baseline"] == 1
    assert summary["locked_test_row_level_artifacts_used"] == 0
    assert "correctness is development accounting only" in summary["claim_boundary"]


def _component_row(
    source_row_index: int,
    *,
    hidden_families: str,
    transition: str,
    baseline_label: str,
    baseline_correct: bool,
    router_reason: str = "trigger_conditioned_frequency",
    final_action: str = "abstain",
) -> dict[str, object]:
    return {
        "candidate_version": "hybrid_multi_component_staged_assembly_v0",
        "source_row_index": str(source_row_index),
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "gold_label": "unknown",
        "final_action": final_action,
        "prediction_bearing": "False",
        "prediction_label": "",
        "deterministic_comparator_label": baseline_label,
        "deterministic_comparator_purist_correct": str(baseline_correct),
        "final_purist_correct": "",
        "comparator_transition": transition,
        "hidden_families": hidden_families,
        "router_reason": router_reason,
    }
