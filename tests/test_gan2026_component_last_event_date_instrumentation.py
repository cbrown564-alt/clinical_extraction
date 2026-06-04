from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    last_event_date_instrumentation,
)


def test_last_event_date_instrumentation_classifies_explicit_dates() -> None:
    pressure_rows = [
        {"source_row_index": 11216, "review_lane": "date_policy_needed"},
        {"source_row_index": 11272, "review_lane": "date_policy_needed"},
        {"source_row_index": 11259, "review_lane": "date_policy_needed"},
        {"source_row_index": 101, "review_lane": "trigger_release_candidate"},
    ]
    residual_rows = [
        {
            "source_row_index": 11216,
            "blocked_candidate_label": "seizure free for 4 month",
            "blocked_candidate_evidence": "Last seizure on 25 December 2023.",
            "blocked_candidate_source_ids": ["det:last_event"],
        },
        {
            "source_row_index": 11272,
            "blocked_candidate_label": "seizure free for multiple year",
            "blocked_candidate_evidence": (
                "last seizure on 20/Dec. There have been no seizures since then"
            ),
            "blocked_candidate_source_ids": ["det:last_event"],
        },
        {
            "source_row_index": 11259,
            "blocked_candidate_label": "seizure free for multiple year",
            "blocked_candidate_evidence": "no clearly documented events since",
            "blocked_candidate_source_ids": ["det:last_event"],
        },
    ]

    rows = last_event_date_instrumentation.build_last_event_date_rows(
        pressure_rows,
        residual_rows,
    )

    assert [row["source_row_index"] for row in rows] == [11216, 11272, 11259]
    assert [row["date_signal_class"] for row in rows] == [
        "full_date_detected",
        "partial_date_missing_year",
        "no_explicit_date_in_selected_evidence",
    ]
    assert rows[0]["explicit_date_spans"] == ["25 December 2023"]
    assert rows[1]["partial_date_spans"] == ["20/Dec"]
    assert rows[2]["explicit_date_spans"] == []
    assert rows[2]["partial_date_spans"] == []
    assert all(row["automatic_release_ready"] is False for row in rows)


def test_last_event_date_instrumentation_extracts_reference_date_from_source_record() -> None:
    pressure_rows = [{"source_row_index": 11216, "review_lane": "date_policy_needed"}]
    residual_rows = [
        {
            "source_row_index": 11216,
            "blocked_candidate_label": "seizure free for 4 month",
            "blocked_candidate_evidence": "Last seizure on 25 December 2023.",
            "blocked_candidate_source_ids": ["det:last_event"],
        }
    ]
    source_records = [
        {
            "source_row_index": 11216,
            "note_text": "From: Dr Example Sent: 27 April 2024 10:15 To: team",
        }
    ]

    rows = last_event_date_instrumentation.build_last_event_date_rows(
        pressure_rows,
        residual_rows,
        source_records=source_records,
    )

    assert rows[0]["reference_date_spans"] == ["27 April 2024"]
    assert rows[0]["reference_date_source"] == "sent_header"
    assert rows[0]["note_or_reference_date_available"] is True
    assert rows[0]["automatic_release_ready"] is False
    assert rows[0]["release_blocker"] == "release_policy_not_implemented"


def test_last_event_date_instrumentation_summarizes_release_blocker() -> None:
    rows = [
        {
            "source_row_index": 11216,
            "date_signal_class": "full_date_detected",
            "note_or_reference_date_available": True,
            "automatic_release_ready": False,
        },
        {
            "source_row_index": 11272,
            "date_signal_class": "partial_date_missing_year",
            "note_or_reference_date_available": True,
            "automatic_release_ready": False,
        },
        {
            "source_row_index": 11259,
            "date_signal_class": "no_explicit_date_in_selected_evidence",
            "note_or_reference_date_available": False,
            "automatic_release_ready": False,
        },
    ]

    summary = last_event_date_instrumentation.summarize_last_event_date_rows(rows)

    assert summary["row_count"] == 3
    assert summary["date_signal_class_counts"] == {
        "full_date_detected": 1,
        "no_explicit_date_in_selected_evidence": 1,
        "partial_date_missing_year": 1,
    }
    assert summary["automatic_release_ready_rows"] == 0
    assert summary["reference_date_available_rows"] == 2
    assert "duration derivation" in summary["recommended_next_step"]
    assert "does not change prediction-bearing behavior" in summary["claim_language"]
