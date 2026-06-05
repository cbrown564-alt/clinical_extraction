from types import SimpleNamespace

from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    diary_log_full_validation_audit,
)


def test_diary_audit_selects_allowed_rule_and_scores_transition(monkeypatch) -> None:
    monkeypatch.setattr(
        diary_log_full_validation_audit.candidate_union,
        "_deterministic_candidates",
        lambda _note, _source: [
            {
                "normalized_label": "5 per 2 month",
                "evidence": "five dated seizures",
                "metadata": {"rule_id": "diary.date_list"},
            }
        ],
    )

    rows = diary_log_full_validation_audit.build_diary_log_audit_rows(
        [
            {
                "source_row_index": 1,
                "prediction_label": "unknown",
                "gold_label": "5 per 2 month",
                "final_purist_correct": False,
                "comparator_transition": "W_to_W",
            }
        ],
        [SimpleNamespace(source_row_index=1, note_text="note")],
    )

    assert rows[0]["candidate_action"] == "selected"
    assert rows[0]["selected_transition"] == "W_to_C"
    assert rows[0]["candidate_rule_id"] == "diary.date_list"


def test_diary_audit_rejects_unapproved_diary_rule(monkeypatch) -> None:
    monkeypatch.setattr(
        diary_log_full_validation_audit.candidate_union,
        "_deterministic_candidates",
        lambda _note, _source: [
            {
                "normalized_label": "4 per month",
                "evidence": "August x 4",
                "metadata": {"rule_id": "diary.increasing_monthly_count"},
            }
        ],
    )

    rows = diary_log_full_validation_audit.build_diary_log_audit_rows(
        [
            {
                "source_row_index": 1,
                "prediction_label": "5 per month",
                "gold_label": "5 per month",
                "final_purist_correct": True,
                "comparator_transition": "C_to_C",
            }
        ],
        [SimpleNamespace(source_row_index=1, note_text="note")],
    )

    assert rows[0]["candidate_action"] == "rejected_rule"
    assert rows[0]["selected_transition"] == ""


def test_diary_summary_freezes_only_clean_selected_rules() -> None:
    rows = [
        {
            "candidate_action": "selected",
            "candidate_rule_id": "diary.date_list",
            "selected_transition": "W_to_C",
        },
        {
            "candidate_action": "rejected_rule",
            "candidate_rule_id": "diary.increasing_monthly_count",
            "selected_transition": "",
        },
    ]

    summary = diary_log_full_validation_audit.summarize_diary_log_audit_rows(
        rows,
        [
            {"source_row_index": 1, "final_purist_correct": False},
            {"source_row_index": 2, "final_purist_correct": True},
        ],
    )

    assert summary["selected_candidate_rows"] == 1
    assert summary["rejected_candidate_rows"] == 1
    assert summary["selected_transition_counts"] == {"W_to_C": 1}
    assert summary["projected_correct_rows"] == 2
    assert summary["decision"] == "freeze_candidate_for_aggregate_audit"
