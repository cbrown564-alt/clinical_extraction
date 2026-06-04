from clinical_extraction.tasks.seizure_frequency.gan2026.components.source_trace import (
    build_selected_source_id_trace,
    projection_source_id_consistency,
    summarize_projection_source_id_consistency,
)


def test_selected_source_id_trace_accepts_exact_note_source() -> None:
    trace = build_selected_source_id_trace(
        {"selected_source_ids": ["note"]},
        exact_trace=True,
    )

    assert trace["source_id_status"] == "valid"
    assert trace["expected_source_ids"] == ["note"]
    assert trace["missing_expected_source_ids"] == []
    assert trace["unexpected_source_ids"] == []


def test_selected_source_id_trace_marks_non_exact_selection_invalid() -> None:
    trace = build_selected_source_id_trace({}, exact_trace=False)

    assert trace["source_id_status"] == "invalid"
    assert trace["expected_source_ids"] == []
    assert trace["trace_basis"] == "non_exact_or_missing_evidence"


def test_projection_consistency_requires_valid_source_and_exact_evidence() -> None:
    result = projection_source_id_consistency(
        {
            "source_id": "note",
            "source_id_status": "invalid",
            "exact_evidence": False,
            "evidence": "Current seizures occur monthly.",
        },
        {"scorable": True, "label": "1 per month"},
    )

    assert result["consistent"] is False
    assert result["failures"] == [
        "scorable_projection_without_valid_source_id",
        "scorable_projection_without_exact_evidence",
    ]


def test_projection_consistency_summary_counts_inconsistent_rows() -> None:
    summary = summarize_projection_source_id_consistency(
        [
            {
                "source_row_index": 1,
                "projection_source_id_consistency": {"consistent": True},
            },
            {
                "source_row_index": 2,
                "projection_source_id_consistency": {"consistent": False},
            },
        ]
    )

    assert summary["projection_source_id_consistent_rows"] == 1
    assert summary["projection_source_id_inconsistent_rows"] == 1
    assert summary["projection_source_id_inconsistent_source_row_indices"] == [2]

