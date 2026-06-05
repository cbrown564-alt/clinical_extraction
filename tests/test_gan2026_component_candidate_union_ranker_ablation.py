from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    candidate_union_ranker_ablation,
)


def test_diary_ranker_recovers_miss_without_gold_selection() -> None:
    rows = candidate_union_ranker_ablation.build_ranker_ablation_rows(
        [
            {
                "source_row_index": 1,
                "gold_label": "5 per 2 month",
                "comparison": {"comparator_correct": False},
                "comparator_selected_state_replay": {"label": "unknown"},
                "union_verified_candidates": [
                    {
                        "candidate_id": "det-1",
                        "candidate_kind": "frequency_rate",
                        "normalized_label": "5 per 2 month",
                        "evidence": "five dates in two months",
                        "provenance": ["deterministic"],
                        "metadata": {"rule_id": "diary.date_list"},
                    }
                ],
            }
        ]
    )

    diary_rows = [row for row in rows if row["ranker_name"] == "diary_log_only_v0"]
    assert len(diary_rows) == 1
    assert diary_rows[0]["selected_transition"] == "W_to_C"
    assert diary_rows[0]["selected_candidate_rule_id"] == "diary.date_list"


def test_comparator_absent_ranker_skips_when_comparator_label_is_in_union() -> None:
    rows = candidate_union_ranker_ablation.build_ranker_ablation_rows(
        [
            {
                "source_row_index": 1,
                "gold_label": "1 per week",
                "comparison": {"comparator_correct": True},
                "comparator_selected_state_replay": {"label": "1 per week"},
                "union_verified_candidates": [
                    {
                        "candidate_id": "det-1",
                        "candidate_kind": "frequency_rate",
                        "normalized_label": "1 per week",
                        "metadata": {"rule_id": "rate.direct_count_per_period"},
                    },
                    {
                        "candidate_id": "det-2",
                        "candidate_kind": "frequency_rate",
                        "normalized_label": "1 per month",
                        "metadata": {"rule_id": "rate.direct_count_per_period"},
                    },
                ],
            }
        ]
    )

    assert not [
        row
        for row in rows
        if row["ranker_name"] == "comparator_absent_quality_rank_v0"
    ]
    assert not [
        row
        for row in rows
        if row["ranker_name"] == "comparator_absent_structural_guard_rank_v0"
    ]


def test_structural_guard_suppresses_live_cluster_boundary_candidate() -> None:
    rows = candidate_union_ranker_ablation.build_ranker_ablation_rows(
        [
            {
                "source_row_index": 1,
                "gold_label": "multiple per month",
                "comparison": {"comparator_correct": True},
                "comparator_selected_state_replay": {"label": "multiple per month"},
                "union_verified_candidates": [
                    {
                        "candidate_id": "live-cluster-1",
                        "candidate_kind": "cluster_frequency",
                        "normalized_label": (
                            "multiple cluster per 4 week, multiple per cluster"
                        ),
                        "provenance": ["live_llm_boundary_proposal_v3"],
                        "metadata": {"rule_id": "cluster.live_boundary"},
                    }
                ],
            }
        ]
    )

    guarded_rows = [
        row
        for row in rows
        if row["ranker_name"] == "comparator_absent_structural_guard_rank_v0"
    ]
    broad_rows = [
        row
        for row in rows
        if row["ranker_name"] == "comparator_absent_quality_rank_v0"
    ]
    assert len(broad_rows) == 1
    assert guarded_rows == []


def test_structural_guard_suppresses_seizure_free_replacement() -> None:
    rows = candidate_union_ranker_ablation.build_ranker_ablation_rows(
        [
            {
                "source_row_index": 1,
                "gold_label": "unknown, 4 to 6 per cluster",
                "comparison": {"comparator_correct": True},
                "comparator_selected_state_replay": {
                    "label": "unknown, 4 to 6 per cluster"
                },
                "union_verified_candidates": [
                    {
                        "candidate_id": "sf-1",
                        "candidate_kind": "seizure_free",
                        "normalized_label": "seizure free for multiple year",
                        "provenance": ["deterministic"],
                        "metadata": {"rule_id": "seizure_free.current_control_phrase"},
                    }
                ],
            }
        ]
    )

    assert not [
        row
        for row in rows
        if row["ranker_name"] == "comparator_absent_structural_guard_rank_v0"
    ]


def test_structural_guard_preserves_cluster_shape_for_cluster_comparator() -> None:
    rows = candidate_union_ranker_ablation.build_ranker_ablation_rows(
        [
            {
                "source_row_index": 1,
                "gold_label": "1 cluster per 5 day, 2 to 4 per cluster",
                "comparison": {"comparator_correct": True},
                "comparator_selected_state_replay": {
                    "label": "1 cluster per 5 day, 2 to 4 per cluster"
                },
                "union_verified_candidates": [
                    {
                        "candidate_id": "rate-1",
                        "candidate_kind": "frequency_rate",
                        "normalized_label": "2 per 6 month",
                        "provenance": ["deterministic"],
                        "metadata": {"rule_id": "rate.there_have_been_count"},
                    },
                    {
                        "candidate_id": "cluster-1",
                        "candidate_kind": "cluster_frequency",
                        "normalized_label": "1 cluster per 6 month, 2 per cluster",
                        "provenance": ["deterministic"],
                        "metadata": {"rule_id": "cluster.vague_days_over_period"},
                    },
                ],
            }
        ]
    )

    guarded_rows = [
        row
        for row in rows
        if row["ranker_name"] == "comparator_absent_structural_guard_rank_v0"
    ]
    assert len(guarded_rows) == 1
    assert guarded_rows[0]["selected_candidate_id"] == "cluster-1"


def test_summary_reports_oracle_headroom_and_ranker_damage() -> None:
    rows = [
        {
            "ranker_name": "comparator_absent_quality_rank_v0",
            "selected_transition": "W_to_C",
            "selected_candidate_kind": "frequency_rate",
            "selected_candidate_rule_id": "diary.date_list",
        },
        {
            "ranker_name": "comparator_absent_quality_rank_v0",
            "selected_transition": "C_to_W",
            "selected_candidate_kind": "frequency_rate",
            "selected_candidate_rule_id": "rate.direct_count_per_period",
        },
    ]
    source_rows = [
        {
            "source_row_index": 1,
            "gold_label": "1 per month",
            "comparison": {"comparator_correct": False},
            "union_verified_candidates": [
                {"normalized_label": "1 per month", "candidate_kind": "frequency_rate"}
            ],
        },
        {
            "source_row_index": 2,
            "gold_label": "1 per week",
            "comparison": {"comparator_correct": True},
            "union_verified_candidates": [
                {"normalized_label": "1 per month", "candidate_kind": "frequency_rate"}
            ],
        },
    ]

    summary = candidate_union_ranker_ablation.summarize_ranker_ablation_rows(
        rows,
        source_rows,
    )

    ranker = summary["rankers"]["comparator_absent_quality_rank_v0"]
    assert summary["oracle_recoverable_miss_rows"] == 1
    assert ranker["selected_transition_counts"] == {"C_to_W": 1, "W_to_C": 1}
    assert ranker["decision"] == "reject"
