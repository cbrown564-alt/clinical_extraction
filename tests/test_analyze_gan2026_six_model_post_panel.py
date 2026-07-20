from scripts.analyze_gan2026_six_model_post_panel import (
    classify_first_failure,
    classify_subproblem,
    comparable_analysis,
)


def test_first_failure_separates_transport_schema_evidence_model_and_deterministic() -> None:
    assert (
        classify_first_failure(
            call_error="quota",
            parse_errors=[],
            evidence_valid=False,
            model_correct=False,
            final_correct=False,
        )
        == "model_transport"
    )
    assert (
        classify_first_failure(
            call_error=None,
            parse_errors=["invalid_json: bad"],
            evidence_valid=False,
            model_correct=False,
            final_correct=False,
        )
        == "format_or_schema"
    )
    assert (
        classify_first_failure(
            call_error=None,
            parse_errors=[],
            evidence_valid=False,
            model_correct=False,
            final_correct=False,
        )
        == "evidence_selection"
    )
    assert (
        classify_first_failure(
            call_error=None,
            parse_errors=[],
            evidence_valid=True,
            model_correct=True,
            final_correct=False,
        )
        == "deterministic_semantic"
    )
    assert (
        classify_first_failure(
            call_error=None,
            parse_errors=[],
            evidence_valid=True,
            model_correct=False,
            final_correct=False,
        )
        == "llm_clinical_selection"
    )


def test_subproblem_uses_clinical_signals_not_model_identity() -> None:
    assert classify_subproblem("cluster every month", "4 per month", []) == (
        "cluster_or_diary_aggregation"
    )
    assert classify_subproblem("no seizures since review", "seizure free", []) == (
        "seizure_free_boundary"
    )
    assert classify_subproblem("events two per week", "2 per week", []) == "rate_denominator"
    assert classify_subproblem("old events, now uncertain", "unknown", []) == (
        "uncertainty_boundary"
    )
    assert classify_subproblem("current focal events", "1 per month", ["historical"]) == (
        "temporal_selection"
    )


def test_comparable_analysis_ignores_only_generation_time() -> None:
    left = {"generated_at_utc": "first", "rows": [{"source_row_index": 1}]}
    right = {"generated_at_utc": "second", "rows": [{"source_row_index": 1}]}

    assert comparable_analysis(left) == comparable_analysis(right)
    assert comparable_analysis(left) != comparable_analysis({**right, "rows": []})
