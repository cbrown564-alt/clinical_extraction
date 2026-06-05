from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    fewshot_train_exemplar_candidate_experiment as fewshot,
)


def test_fewshot_contract_keeps_current_without_exact_evidence() -> None:
    assert (
        fewshot.contract_family_for(
            "1 per month",
            "1 cluster per month, multiple per cluster",
            evidence_valid=False,
        )
        == "keep_current"
    )


def test_fewshot_contract_allows_frozen_validation_clean_families() -> None:
    assert (
        fewshot.contract_family_for(
            "1 per month",
            "1 cluster per month, multiple per cluster",
            evidence_valid=True,
        )
        == "cluster_per_cluster_completion"
    )
    assert (
        fewshot.contract_family_for("1 per year", "1 per day", evidence_valid=True)
        == "daily_upgrade_from_non_daily"
    )
    assert (
        fewshot.contract_family_for("1 per day", "multiple per day", evidence_valid=True)
        == "multiple_daily_upgrade_from_single_daily"
    )
    assert (
        fewshot.contract_family_for("1 per 1 to 2 week", "9 per 4 week", evidence_valid=True)
        == "explicit_rate_replacement"
    )


def test_fewshot_test_row_summary_has_no_row_level_diagnostics() -> None:
    summary = fewshot._summarize_test_aggregate_rows(
        [
            {
                "combined_correct": False,
                "final_correct": True,
                "combined_changed_rows": False,
                "contract_family": "daily_upgrade_from_non_daily",
                "combined_family": "keep_current",
                "combined_transition": "W_to_W",
                "contract_transition": "W_to_C",
                "fewshot_call_ok": True,
                "fewshot_parse_ok": True,
                "fewshot_evidence_valid": True,
            }
        ]
    )

    assert summary == {
        "combined_correct_rows": 0,
        "final_correct_rows": 1,
        "combined_changed_rows": 0,
        "contract_selected_rows": 1,
        "fewshot_call_ok_rows": 1,
        "fewshot_parse_ok_rows": 1,
        "fewshot_exact_evidence_rows": 1,
        "combined_transition_counts": {"W_to_W": 1},
        "contract_transition_counts": {"W_to_C": 1},
        "combined_family_counts": {"keep_current": 1},
        "contract_family_counts": {"daily_upgrade_from_non_daily": 1},
    }
