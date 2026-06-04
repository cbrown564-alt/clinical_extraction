from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    rq9_abstention_pressure as pressure,
)


def _row(
    *,
    source_row_index: int,
    action: str = "abstain",
    reason: str = "trigger_conditioned_frequency",
    final_label: str = "2 per month",
    purist_correct: bool = True,
    human_class: str | None = None,
) -> dict:
    return {
        "source_row_index": source_row_index,
        "selective_action": action,
        "primary_reason": reason,
        "source_candidate": {
            "final_label": final_label,
            "purist_correct": purist_correct,
            "selected_evidence": "twice a month, often around the luteal phase",
        },
        "development_accounting": {
            "gold_label_kind": "frequency",
            "human_simple_class": human_class,
            "codex_ambiguity_reasons": ["conditional_or_trigger_bound"],
        },
    }


def test_trigger_abstention_with_non_sentinel_correct_label_is_dev_safe_candidate() -> None:
    row = pressure.interpret_abstention_row(_row(source_row_index=704))

    assert row["pressure_class"] == "candidate_prediction_bearing"
    assert row["development_safe_if_predicted"] is True
    assert row["policy_interpretation"] == "rate_with_trigger_context"


def test_trigger_abstention_with_unknown_label_remains_policy_supported_abstention() -> None:
    row = pressure.interpret_abstention_row(
        _row(source_row_index=3371, final_label="unknown")
    )

    assert row["pressure_class"] == "policy_supported_nonprediction"
    assert row["development_safe_if_predicted"] is False
    assert row["policy_interpretation"] == "trigger_only_or_unquantified"


def test_last_event_boundary_needs_frozen_date_policy_not_direct_prediction() -> None:
    row = pressure.interpret_abstention_row(
        _row(
            source_row_index=11282,
            action="human_review",
            reason="last_event_boundary",
            final_label="unknown",
            purist_correct=True,
        )
    )

    assert row["pressure_class"] == "needs_frozen_policy_before_prediction"
    assert row["development_safe_if_predicted"] is False
    assert row["policy_interpretation"] == "last_event_needs_date_policy"


def test_summary_counts_candidate_and_gold_blind_risk_separately() -> None:
    _, summary = pressure.interpret_abstention_rows(
        [
            _row(source_row_index=1),
            _row(source_row_index=2, final_label="3 per week", purist_correct=False),
            _row(source_row_index=3, final_label="unknown", purist_correct=True),
        ]
    )

    assert summary["metrics"]["candidate_prediction_bearing_rows"] == 2
    assert summary["metrics"]["development_safe_candidate_rows"] == 1
    assert summary["metrics"]["development_unsafe_candidate_rows"] == 1
    assert summary["metrics"]["policy_supported_nonprediction_rows"] == 1
