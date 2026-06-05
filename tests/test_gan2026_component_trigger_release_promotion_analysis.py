from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    trigger_release_promotion_analysis,
)


def test_trigger_release_promotion_analysis_promotes_with_category_caveat() -> None:
    summary = trigger_release_promotion_analysis.build_promotion_analysis(
        [
            {
                "source_row_index": 5977,
                "release_decision": "release_as_prediction",
                "prediction_label": "multiple per 6 week",
                "selected_evidence": "several episodes over the past six weeks",
                "selected_source_ids": ["det:event_1"],
            }
        ],
        [
            {
                "source_row_index": 5977,
                "selected_evidence_exact": True,
                "development_accounting": {"purist_correct": True},
            }
        ],
        [
            {
                "source_row_index": 5977,
                "gold_label": "unknown",
                "final_action": "abstain",
                "deterministic_comparator_purist_correct": False,
                "comparator_transition": "W_to_abstain",
            }
        ],
    )

    assert summary["decision"] == "promote_with_category_caveat"
    assert summary["w_to_c_rows"] == 1
    assert summary["c_to_w_rows"] == 0
    assert summary["category_correct_not_exact_label_rows"] == 1
    assert summary["issues"] == []
    assert summary["rows"][0]["caveat"] == "category_correct_not_exact_label"


def test_trigger_release_promotion_analysis_rejects_gate_mismatch() -> None:
    summary = trigger_release_promotion_analysis.build_promotion_analysis(
        [
            {
                "source_row_index": 5977,
                "release_decision": "release_as_prediction",
                "prediction_label": "multiple per 6 week",
                "selected_evidence": "several episodes over the past six weeks",
                "selected_source_ids": ["det:event_1"],
            }
        ],
        [
            {
                "source_row_index": 5977,
                "selected_evidence_exact": True,
                "development_accounting": {"purist_correct": True},
            }
        ],
        [
            {
                "source_row_index": 5977,
                "gold_label": "unknown",
                "final_action": "abstain",
                "deterministic_comparator_purist_correct": True,
                "comparator_transition": "C_to_abstain",
            }
        ],
    )

    assert summary["decision"] == "reject"
    assert summary["w_to_c_rows"] == 0
    assert summary["c_to_w_rows"] == 0
    assert summary["issues"] == [
        "promotion_gate_expected_all_releases_w_to_c_and_zero_c_to_w"
    ]


def test_trigger_release_promotion_analysis_rejects_missing_evidence() -> None:
    summary = trigger_release_promotion_analysis.build_promotion_analysis(
        [
            {
                "source_row_index": 1,
                "release_decision": "release_as_prediction",
                "prediction_label": "1 per month",
                "selected_evidence": "",
                "selected_source_ids": [],
            }
        ],
        [
            {
                "source_row_index": 1,
                "selected_evidence_exact": False,
                "development_accounting": {"purist_correct": True},
            }
        ],
        [
            {
                "source_row_index": 1,
                "gold_label": "1 per month",
                "final_action": "abstain",
                "deterministic_comparator_purist_correct": False,
            }
        ],
    )

    assert summary["decision"] == "reject"
    assert summary["issues"] == [
        "missing_selected_evidence:1",
        "missing_selected_source_ids:1",
        "selected_evidence_not_exact:1",
    ]
