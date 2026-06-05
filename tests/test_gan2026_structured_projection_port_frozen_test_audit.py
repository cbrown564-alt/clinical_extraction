from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    structured_projection_port_frozen_test_audit,
)


def test_structured_projection_port_prefers_llm_cluster_candidate() -> None:
    row = _test_row(
        base_label="1 per month",
        gold_purist_category="seizure_freq_1ormore_daily",
        base_correct=True,
        llm_candidates=[
            {
                "normalized_label": "1 cluster per month, 4 per cluster",
                "assertion_status": "asserted",
                "temporality": "current",
            }
        ],
        deterministic_candidates=[
            {"normalized_label": "1 per day"},
        ],
    )

    result = structured_projection_port_frozen_test_audit._run_aggregate_row(row)

    assert result["selected_family"] == "cluster_frequency"
    assert result["selected_source"] == "llm_candidate"
    assert result["transition"] == "C_to_W"


def test_structured_projection_port_uses_daily_candidate_when_base_is_not_daily() -> None:
    row = _test_row(
        base_label="4 per year",
        gold_purist_category="seizure_freq_1ormore_daily",
        base_correct=False,
        llm_candidates=[],
        deterministic_candidates=[
            {"normalized_label": "1 per day"},
        ],
    )

    result = structured_projection_port_frozen_test_audit._run_aggregate_row(row)

    assert result["selected_family"] == "daily_frequency"
    assert result["selected_source"] == "deterministic_candidate"
    assert result["transition"] == "W_to_C"


def test_structured_projection_port_summary_counts_transitions() -> None:
    rows = [
        _test_row(
            base_label="4 per year",
            gold_purist_category="seizure_freq_1ormore_daily",
            base_correct=False,
            llm_candidates=[],
            deterministic_candidates=[{"normalized_label": "1 per day"}],
        ),
        _test_row(
            base_label="1 per day",
            gold_purist_category="seizure_freq_1ormore_daily",
            base_correct=True,
            llm_candidates=[],
            deterministic_candidates=[],
        ),
    ]

    metadata = structured_projection_port_frozen_test_audit.run_test_aggregate_audit(
        rows
    )

    assert metadata["metrics"]["test_rows"] == 2
    assert metadata["metrics"]["base_correct_rows"] == 1
    assert metadata["metrics"]["final_correct_rows"] == 2
    assert metadata["transition_counts"] == {"C_to_C": 1, "W_to_C": 1}
    assert metadata["selected_family_counts"] == {
        "daily_frequency": 1,
        "keep_current": 1,
    }
    assert metadata["decision"] == "promoted_audit_positive"


def _test_row(
    *,
    base_label: str,
    gold_purist_category: str,
    base_correct: bool,
    llm_candidates: list[dict[str, object]],
    deterministic_candidates: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "score_layers": {
            "hybrid_adjudicator_raw": {
                "final_label": base_label,
                "gold_purist_category": gold_purist_category,
                "predicted_purist_category": "seizure_freq_1_per_yr",
                "purist_correct": base_correct,
            }
        },
        "structured_llm_candidate_record": {"candidates": llm_candidates},
        "component_inputs": {
            "deterministic_candidates": deterministic_candidates,
        },
    }
