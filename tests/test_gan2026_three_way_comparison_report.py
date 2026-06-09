from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    three_way_comparison_report as report,
)


def test_rendered_split_uses_unknown_final_label_for_deterministic_architectures() -> None:
    rows = [
        {"source_row_index": 1, "final_label": "1 per day"},
        {"source_row_index": 2, "final_label": "unknown"},
    ]

    rendered, null_rows = report._rendered_split("deterministic", rows)

    assert [row["source_row_index"] for row in rendered] == [1]
    assert [row["source_row_index"] for row in null_rows] == [2]


def test_rendered_split_treats_llm_only_direct_labeler_as_never_null() -> None:
    rows = [
        {"source_row_index": 1, "decision_record": {"final_label": "1 per day"}},
        {"source_row_index": 2, "decision_record": {"final_label": "seizure_freq_unknown"}},
    ]

    rendered, null_rows = report._rendered_split("llm_only_direct_labeler", rows)

    assert len(rendered) == 2
    assert null_rows == []


def test_rendered_split_uses_predicted_purist_category_for_structured_events() -> None:
    rows = [
        {"source_row_index": 1, "comparison": {"predicted_purist_category": "seizure_freq_1_per_mon"}},
        {"source_row_index": 2, "comparison": {"predicted_purist_category": None}},
    ]

    rendered, null_rows = report._rendered_split("hybrid_structured_events", rows)

    assert [row["source_row_index"] for row in rendered] == [1]
    assert [row["source_row_index"] for row in null_rows] == [2]


def test_evidence_trace_metric_distinguishes_canonical_pipeline_from_others() -> None:
    rows = [
        {"evidence_valid": True, "evidence_text_contained": False},
        {"evidence_valid": False, "evidence_text_contained": True},
    ]

    direct_name, direct_valid, direct_total = report._evidence_trace_metric(
        "llm_only_direct_labeler", rows
    )
    canonical_name, canonical_valid, canonical_total = report._evidence_trace_metric(
        "llm_only_canonical_pipeline", rows
    )

    assert (direct_name, direct_valid, direct_total) == ("evidence_valid", 1, 2)
    assert (canonical_name, canonical_valid, canonical_total) == ("evidence_text_contained", 1, 2)


def test_single_shot_summary_row_computes_rates_over_rendered_rows_only() -> None:
    rows = [
        {
            "source_row_index": 1,
            "final_label": "1 per day",
            "comparison": {"purist_correct": True, "pragmatic_correct": True},
            "evidence_valid": True,
        },
        {
            "source_row_index": 2,
            "final_label": "1 per week",
            "comparison": {"purist_correct": False, "pragmatic_correct": True},
            "evidence_valid": False,
        },
        {
            "source_row_index": 3,
            "final_label": "unknown",
            "comparison": {"purist_correct": False, "pragmatic_correct": False},
            "evidence_valid": False,
        },
    ]

    summary_row = report._single_shot_summary_row("deterministic", rows)

    assert summary_row["examples"] == 3
    assert summary_row["rendered_rows"] == 2
    assert summary_row["null_rows"] == 1
    assert summary_row["routed_rows"] is None
    assert summary_row["purist_correct_of_rendered"] == 1
    assert summary_row["purist_correct_rate_of_rendered"] == 0.5
    assert summary_row["pragmatic_correct_of_rendered"] == 2
    assert summary_row["pragmatic_correct_rate_of_rendered"] == 1.0
    assert summary_row["evidence_trace_valid_rows"] == 1
    assert summary_row["evidence_trace_valid_rate"] == 1 / 3
    assert summary_row["final_label_distribution"] == {
        "1 per day": 1,
        "1 per week": 1,
        "unknown": 1,
    }


def test_hybrid_final_label_distribution_merges_route_passthrough_and_decisions() -> None:
    route_rows = [
        {"source_row_index": 1, "final_rendered_label": {"rendered_label": "1 per day"}},
        {"source_row_index": 2, "final_rendered_label": {"rendered_label": "1 per week"}},
        {"source_row_index": 3, "final_rendered_label": {"rendered_label": "unknown"}},
    ]
    decision_rows = [
        {
            "source_row_index": 2,
            "verification_decision": {"final_rendered_label": "1 per week"},
        },
        {
            "source_row_index": 3,
            "verification_decision": {"final_rendered_label": None},
        },
    ]

    counts = report._hybrid_final_label_distribution(route_rows, decision_rows)

    assert counts == {"1 per day": 1, "1 per week": 1, "None": 1}


def test_hybrid_candidate_sets_skips_rows_without_an_embedded_candidate_set() -> None:
    rows = [
        {
            "source_row_index": 7,
            "candidate_set": {
                "source_row_index": 7,
                "component_owner": "test",
                "source_artifacts": ["test_artifact"],
                "row_context": {},
                "candidates": [],
                "schema_version": "gan2026_candidate_set_source_near_v0",
            },
        },
        {"source_row_index": 8, "candidate_set": None},
    ]

    candidate_sets = report._hybrid_candidate_sets(rows)

    assert set(candidate_sets) == {7}
    assert candidate_sets[7].source_row_index == 7
