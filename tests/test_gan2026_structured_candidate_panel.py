from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    structured_candidate_panel,
)


def test_direct_labeler_rows_become_structured_candidate_panel_rows() -> None:
    saved_rows = [
        {
            "source_row_index": 1,
            "split": "validation",
            "split_manifest": "gan2026_split_v1",
            "current_label": "unknown",
            "direct_label": "1 per month",
            "gold_label": "1 per month",
            "current_purist_correct": False,
            "direct_purist_correct": True,
            "evidence_valid": True,
            "parse_errors": [],
            "decision_record": {
                "answer_kind": "frequency",
                "evidence": "1 seizure per month",
            },
        },
        {
            "source_row_index": 2,
            "split": "validation",
            "split_manifest": "gan2026_split_v1",
            "current_label": "1 per month",
            "direct_label": "unknown",
            "gold_label": "1 per month",
            "current_purist_correct": True,
            "direct_purist_correct": False,
            "evidence_valid": False,
            "parse_errors": ["unparsable"],
            "decision_record": {
                "answer_kind": "unknown",
                "evidence": "no seizure count stated",
            },
        },
    ]
    note_text_by_source = {
        1: "Current frequency is 1 seizure per month.",
        2: "Current frequency is 1 seizure per month.",
    }

    rows = structured_candidate_panel.build_direct_labeler_panel_rows(
        saved_rows,
        note_text_by_source,
    )

    assert rows[0]["candidate_source"] == "llm_candidate"
    assert rows[0]["event_kind"] == "frequency_rate"
    assert rows[0]["panel_role"] == "hard"
    assert rows[0]["transition"] == "W_to_C"
    assert rows[0]["contract_issues"] == []
    assert rows[0]["note_text"] is None
    assert rows[1]["event_kind"] == "unknown_frequency"
    assert rows[1]["panel_role"] == "control"
    assert rows[1]["transition"] == "C_to_W"
    assert rows[1]["contract_issues"] == ["parse_not_ok", "evidence_not_exact"]


def test_direct_labeler_panel_summary_reports_gate_failure() -> None:
    rows = []
    for index in range(10):
        rows.append(
            {
                "source_row_index": index,
                "split": "validation",
                "split_manifest": "gan2026_split_v1",
                "current_label": "unknown",
                "direct_label": "1 per month",
                "gold_label": "1 per month",
                "current_purist_correct": False,
                "direct_purist_correct": True,
                "evidence_valid": True,
                "parse_errors": [],
                "decision_record": {
                    "answer_kind": "frequency",
                    "evidence": "1 seizure per month",
                },
            }
        )
    note_text_by_source = {
        index: "Current frequency is 1 seizure per month." for index in range(10)
    }
    panel_rows = structured_candidate_panel.build_direct_labeler_panel_rows(
        rows,
        note_text_by_source,
    )

    summary = structured_candidate_panel.summarize_panel_rows(panel_rows)

    assert summary["source_artifact_kind"] == "direct_labeler_full_validation750"
    assert summary["validation_gate"]["selected_prediction_bearing_rows"] == 10
    assert summary["validation_gate"]["w_to_c_rows"] == 10
    assert summary["validation_gate"]["frozen_test_audit_ready"] is False
    assert summary["validation_gate"]["gate_failures"] == [
        "coverage_below_150",
        "w_to_c_below_60",
    ]
