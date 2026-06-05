from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    assembly_failure_recoverability,
)


def test_recoverability_identifies_actionable_candidate_for_w_failure() -> None:
    rows = assembly_failure_recoverability.build_recoverability_rows(
        [
            {
                "source_row_index": 1,
                "comparator_transition": "W_to_W",
                "final_action": "predict",
                "prediction_label": "unknown",
                "gold_label": "1 per month",
            },
            {
                "source_row_index": 2,
                "comparator_transition": "C_to_C",
                "final_action": "predict",
            },
        ],
        [
            {
                "source_row_index": 1,
                "generator_name": "state_graph_nodes",
                "candidate_label": "1 per month",
                "candidate_kind": "frequency_rate",
                "gold_match_status": "exact_label",
                "evidence_status": "exact",
                "source_id_valid": True,
            }
        ],
    )

    assert len(rows) == 1
    assert rows[0]["recoverability_class"] == "actionable_candidate"
    assert rows[0]["best_generator"] == "state_graph_nodes"
    assert rows[0]["best_recall_status"] == "exact_label"


def test_recoverability_keeps_semantic_state_separate() -> None:
    rows = assembly_failure_recoverability.build_recoverability_rows(
        [{"source_row_index": 1, "comparator_transition": "W_to_review"}],
        [
            {
                "source_row_index": 1,
                "generator_name": "llm_candidate_selector_raw",
                "candidate_label": "frequency",
                "candidate_kind": "frequency_rate",
                "gold_match_status": "semantic_state",
                "evidence_status": "exact",
                "source_id_valid": True,
            }
        ],
    )
    summary = assembly_failure_recoverability.summarize_recoverability_rows(rows)

    assert rows[0]["recoverability_class"] == "semantic_state_only"
    assert summary["actionable_candidate_rows"] == 0
    assert "build new candidate-generation" in summary["recommended_next_step"]


def test_recoverability_summary_recommends_top_actionable_generator() -> None:
    rows = [
        {
            "source_row_index": 1,
            "failure_transition": "W_to_W",
            "recoverability_class": "actionable_candidate",
            "best_generator": "state_graph_nodes",
        },
        {
            "source_row_index": 2,
            "failure_transition": "W_to_abstain",
            "recoverability_class": "no_recalled_candidate",
            "best_generator": "",
        },
    ]

    summary = assembly_failure_recoverability.summarize_recoverability_rows(
        rows,
        base_correct_rows=10,
        total_rows=20,
    )

    assert summary["row_count"] == 2
    assert summary["by_failure_transition"] == {"W_to_W": 1, "W_to_abstain": 1}
    assert summary["by_recoverability_class"] == {
        "actionable_candidate": 1,
        "no_recalled_candidate": 1,
    }
    assert summary["exact_label_actionable_rows"] == 0
    assert summary["purist_category_actionable_rows"] == 0
    assert summary["oracle_actionable_upper_bound_correct_rows"] == 11
    assert summary["oracle_actionable_upper_bound_score"] == 0.55
    assert "state_graph_nodes" in summary["recommended_next_step"]
