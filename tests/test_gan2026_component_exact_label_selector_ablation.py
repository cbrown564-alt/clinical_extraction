from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    exact_label_selector_ablation,
)


def test_selector_uses_non_gold_features_then_scores_transition() -> None:
    rows = exact_label_selector_ablation.build_selector_ablation_rows(
        [
            {
                "source_row_index": 1,
                "comparator_transition": "W_to_W",
                "final_action": "predict",
                "prediction_label": "1 per day",
                "final_purist_correct": False,
            }
        ],
        [
            {
                "source_row_index": 1,
                "generator_name": "deterministic_candidates_all",
                "candidate_label": "1 per 6 week",
                "candidate_kind": "frequency_rate",
                "evidence_status": "exact",
                "source_id_valid": True,
                "denominator_or_window": {"count": "1", "unit": "week"},
                "metadata_missing_fields": ["temporality"],
                "gold_match_status": "exact_label",
                "gold_match_basis": "candidate_label",
                "candidate_id": "event_1",
            }
        ],
    )

    selected = [
        row
        for row in rows
        if row["selector_name"] == "deterministic_window_parseable_v0"
    ]
    assert len(selected) == 1
    assert selected[0]["selected_transition"] == "W_to_C"
    assert selected[0]["candidate_gold_match_status"] == "exact_label"


def test_selector_rejects_unparseable_frequency_candidate() -> None:
    rows = exact_label_selector_ablation.build_selector_ablation_rows(
        [
            {
                "source_row_index": 1,
                "prediction_label": "unknown",
                "final_purist_correct": False,
            }
        ],
        [
            {
                "source_row_index": 1,
                "generator_name": "deterministic_candidates_all",
                "candidate_label": "about weekly",
                "candidate_kind": "frequency_rate",
                "evidence_status": "exact",
                "source_id_valid": True,
                "denominator_or_window": {"unit": "week"},
                "gold_match_status": "semantic_state",
            }
        ],
    )

    assert rows == []


def test_summary_reports_c_to_w_damage_and_rejects_noisy_selector() -> None:
    rows = [
        {
            "selector_name": "llm_unknown_any_v0",
            "selected_transition": "C_to_W",
            "candidate_gold_match_status": "no_match",
            "candidate_generator": "llm_candidate_selector_raw",
        },
        {
            "selector_name": "llm_unknown_any_v0",
            "selected_transition": "W_to_C",
            "candidate_gold_match_status": "exact_label",
            "candidate_generator": "llm_candidate_selector_raw",
        },
    ]
    matrix_rows = [
        {"source_row_index": 1, "final_purist_correct": True},
        {"source_row_index": 2, "final_purist_correct": False},
    ]

    summary = exact_label_selector_ablation.summarize_selector_ablation_rows(
        rows,
        matrix_rows,
    )

    selector = summary["selectors"]["llm_unknown_any_v0"]
    assert selector["selected_rows"] == 2
    assert selector["selected_transition_counts"] == {"C_to_W": 1, "W_to_C": 1}
    assert selector["projected_correct_rows"] == 1
    assert selector["decision"] == "reject"


def test_nonprediction_unknown_selector_skips_existing_predictions() -> None:
    rows = exact_label_selector_ablation.build_selector_ablation_rows(
        [
            {
                "source_row_index": 1,
                "final_action": "predict",
                "prediction_label": "1 per week",
                "final_purist_correct": True,
            },
            {
                "source_row_index": 2,
                "final_action": "abstain",
                "prediction_label": "",
                "final_purist_correct": False,
            },
        ],
        [
            {
                "source_row_index": 1,
                "generator_name": "llm_candidate_selector_raw",
                "candidate_label": "unknown",
                "candidate_kind": "unknown_frequency",
                "evidence_status": "exact",
                "source_id_valid": True,
                "temporality": "current",
                "metadata_missing_fields": [],
                "gold_match_status": "no_match",
            },
            {
                "source_row_index": 2,
                "generator_name": "llm_candidate_selector_raw",
                "candidate_label": "unknown",
                "candidate_kind": "unknown_frequency",
                "evidence_status": "exact",
                "source_id_valid": True,
                "temporality": "current",
                "metadata_missing_fields": [],
                "gold_match_status": "exact_label",
            },
        ],
    )

    selected = [
        row
        for row in rows
        if row["selector_name"] == "nonprediction_llm_unknown_current_v0"
    ]
    assert [row["source_row_index"] for row in selected] == [2]
    assert selected[0]["selected_transition"] == "W_to_C"
