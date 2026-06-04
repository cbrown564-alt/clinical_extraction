from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    rq9_last_event_boundary as last_event,
)


def _row(
    *,
    source_row_index: int,
    final_label: str = "seizure free for 4 month",
    purist_correct: bool = False,
    gold_kind: str = "unknown",
    reasons: list[str] | None = None,
) -> dict:
    return {
        "source_row_index": source_row_index,
        "selective_action": "human_review",
        "primary_reason": "last_event_boundary",
        "source_candidate": {
            "final_label": final_label,
            "purist_correct": purist_correct,
            "selected_evidence": "Last seizure on 25 December 2023. No subsequent events.",
        },
        "development_accounting": {
            "gold_label_kind": gold_kind,
            "human_simple_class": None,
            "codex_ambiguity_reasons": reasons
            or [
                "unknown_gold_boundary",
                "last_event_or_seizure_free_boundary",
                "calendar_or_diary_arithmetic",
            ],
        },
    }


def test_unknown_gold_last_event_seizure_free_candidate_stays_review() -> None:
    row = last_event.interpret_last_event_row(_row(source_row_index=11216))

    assert row["decision"] == "keep_human_review"
    assert row["failure_mode"] == "unknown_convention_blocks_seizure_free_projection"
    assert row["date_policy_ready"] is False


def test_frequency_last_event_boundary_is_selection_failure_not_date_policy() -> None:
    row = last_event.interpret_last_event_row(
        _row(
            source_row_index=14810,
            final_label="12 per month",
            gold_kind="frequency",
            reasons=["last_event_or_seizure_free_boundary"],
        )
    )

    assert row["decision"] == "keep_human_review"
    assert row["failure_mode"] == "recent_event_frequency_selection_boundary"
    assert row["date_policy_ready"] is False


def test_unknown_candidate_remains_review_due_to_unresolved_last_event_boundary() -> None:
    row = last_event.interpret_last_event_row(
        _row(source_row_index=11282, final_label="unknown", purist_correct=True)
    )

    assert row["decision"] == "keep_human_review"
    assert row["failure_mode"] == "unresolved_last_event_unknown_boundary"
    assert row["development_safe_if_predicted"] is True


def test_summary_rejects_v4_date_policy_when_no_rows_are_ready() -> None:
    rows, summary = last_event.interpret_last_event_rows(
        [
            _row(source_row_index=11216),
            _row(source_row_index=11282, final_label="unknown", purist_correct=True),
            _row(
                source_row_index=14810,
                final_label="12 per month",
                gold_kind="frequency",
                reasons=["last_event_or_seizure_free_boundary"],
            ),
        ]
    )

    assert len(rows) == 3
    assert summary["metrics"]["date_policy_ready_rows"] == 0
    assert summary["decision"] == "keep_last_event_as_human_review"
