from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    month_bucket_duration_selection_ablation,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.state_graph import (
    ClinicalFrequencyStateGraph,
    EvidenceSpan,
    GraphNodeKind,
    StateGraphNode,
)


def test_month_bucket_ablation_reports_target_gains_and_regression_cost() -> None:
    target_graph = ClinicalFrequencyStateGraph(
        source_row_index=1,
        nodes=(
            _node("sg-001", "seizure free for multiple year", GraphNodeKind.SEIZURE_FREE),
            _node(
                "duration-sg-002",
                "seizure free for multiple month",
                GraphNodeKind.SEIZURE_FREE,
            ),
        ),
    )
    already_correct_graph = ClinicalFrequencyStateGraph(
        source_row_index=2,
        nodes=(
            _node("sg-001", "2 per month", GraphNodeKind.FREQUENCY_RATE),
            _node("sg-002", "seizure free for multiple month", GraphNodeKind.SEIZURE_FREE),
        ),
    )

    rows, metadata = (
        month_bucket_duration_selection_ablation.run_month_bucket_duration_selection_ablation(
            [
                {
                    "source_row_index": 1,
                    "gold_normalized_label": "seizure free for multiple month",
                    "gold_label_kind": "seizure_free",
                    "gold_monthly_frequency": 0.0,
                    "replayed_graph": target_graph.model_dump(mode="json"),
                    "baseline_projection": {"final_label": "seizure free for multiple year"},
                    "projection_exact_duration_match": False,
                }
            ],
            [
                {
                    "source_row_index": 2,
                    "gold_normalized_label": "2 per month",
                    "gold_label_kind": "frequency",
                    "gold_monthly_frequency": 2.0,
                    "graph": already_correct_graph.model_dump(mode="json"),
                    "projection": {"final_label": "2 per month"},
                    "projection_exact_label_match": True,
                    "validation_hard_slice_memberships": [
                        "cluster_or_diary",
                        "temporal_conflict",
                    ],
                }
            ],
            split="validation_hard_slices",
            split_manifest="gan2026_split_v1",
        )
    )

    assert metadata["summary"]["target"]["exact_duration_corrections"] == 1
    assert metadata["summary"]["regression"]["already_correct_regressions"] == 1
    assert metadata["summary"]["all_rows"]["changed_labels"] == 2
    assert metadata["summary"]["regression_family_tags"] == {
        "cluster_or_diary": {"rows": 1, "changed_labels": 1},
        "temporal_conflict": {"rows": 1, "changed_labels": 1},
    }
    assert rows[0]["month_bucket_projection"]["final_label"] == (
        "seizure free for multiple month"
    )
    assert rows[1]["regression_tags"] == [
        "already_projection_correct",
        "cluster_or_diary",
        "frequency_with_seizure_free_node",
        "temporal_conflict",
    ]


def test_month_bucket_ablation_falls_back_without_seizure_free_nodes() -> None:
    graph = ClinicalFrequencyStateGraph(
        source_row_index=3,
        nodes=(_node("sg-001", "unknown", GraphNodeKind.UNKNOWN_FREQUENCY),),
    )

    rows, metadata = (
        month_bucket_duration_selection_ablation.run_month_bucket_duration_selection_ablation(
            [],
            [
                {
                    "source_row_index": 3,
                    "gold_normalized_label": "unknown",
                    "gold_label_kind": "unknown",
                    "gold_monthly_frequency": 1000.0,
                    "graph": graph.model_dump(mode="json"),
                    "projection": {"final_label": "unknown"},
                    "projection_exact_label_match": True,
                }
            ],
            split="validation_hard_slices",
            split_manifest="gan2026_split_v1",
        )
    )

    assert rows[0]["month_bucket_projection"]["final_label"] == "unknown"
    assert rows[0]["label_changed"] is False
    assert metadata["summary"]["regression"]["already_correct_regressions"] == 0


def test_gated_month_bucket_blocks_frequency_override_but_keeps_duration_gain() -> None:
    target_graph = ClinicalFrequencyStateGraph(
        source_row_index=4,
        nodes=(
            _node("sg-001", "seizure free for multiple year", GraphNodeKind.SEIZURE_FREE),
            _node(
                "duration-sg-002",
                "seizure free for multiple month",
                GraphNodeKind.SEIZURE_FREE,
            ),
        ),
    )
    frequency_graph = ClinicalFrequencyStateGraph(
        source_row_index=5,
        nodes=(
            _node("sg-001", "2 per month", GraphNodeKind.FREQUENCY_RATE),
            _node("sg-002", "seizure free for multiple month", GraphNodeKind.SEIZURE_FREE),
        ),
    )

    rows, metadata = (
        month_bucket_duration_selection_ablation.run_month_bucket_duration_selection_ablation(
            [
                {
                    "source_row_index": 4,
                    "gold_normalized_label": "seizure free for multiple month",
                    "gold_label_kind": "seizure_free",
                    "gold_monthly_frequency": 0.0,
                    "replayed_graph": target_graph.model_dump(mode="json"),
                    "baseline_projection": {"final_label": "seizure free for multiple year"},
                }
            ],
            [
                {
                    "source_row_index": 5,
                    "gold_normalized_label": "2 per month",
                    "gold_label_kind": "frequency",
                    "gold_monthly_frequency": 2.0,
                    "graph": frequency_graph.model_dump(mode="json"),
                    "projection": {"final_label": "2 per month"},
                    "projection_exact_label_match": True,
                }
            ],
            split="validation_hard_slices",
            split_manifest="gan2026_split_v1",
            policy_variant="gated_v1",
        )
    )

    assert rows[0]["month_bucket_projection"]["final_label"] == (
        "seizure free for multiple month"
    )
    assert rows[1]["month_bucket_projection"]["final_label"] == "2 per month"
    assert rows[1]["label_changed"] is False
    assert metadata["summary"]["target"]["exact_duration_corrections"] == 1
    assert metadata["summary"]["regression"]["already_correct_regressions"] == 0


def test_gated_month_bucket_preserves_already_correct_numeric_month_surface() -> None:
    graph = ClinicalFrequencyStateGraph(
        source_row_index=6,
        nodes=(
            _node("sg-001", "seizure free for 7 month", GraphNodeKind.SEIZURE_FREE),
        ),
    )

    rows, metadata = (
        month_bucket_duration_selection_ablation.run_month_bucket_duration_selection_ablation(
            [],
            [
                {
                    "source_row_index": 6,
                    "gold_normalized_label": "seizure free for 7 month",
                    "gold_label_kind": "seizure_free",
                    "gold_monthly_frequency": 0.0,
                    "graph": graph.model_dump(mode="json"),
                    "projection": {"final_label": "seizure free for 7 month"},
                    "projection_exact_label_match": True,
                }
            ],
            split="validation_hard_slices",
            split_manifest="gan2026_split_v1",
            policy_variant="gated_v1",
        )
    )

    assert rows[0]["month_bucket_projection"]["final_label"] == "seizure free for 7 month"
    assert rows[0]["label_changed"] is False
    assert metadata["summary"]["regression"]["already_correct_regressions"] == 0


def test_graph_gated_month_bucket_requires_duration_normalizer_node() -> None:
    target_graph = ClinicalFrequencyStateGraph(
        source_row_index=7,
        nodes=(
            _node("sg-001", "seizure free for multiple year", GraphNodeKind.SEIZURE_FREE),
            _node(
                "duration-sg-002",
                "seizure free for multiple month",
                GraphNodeKind.SEIZURE_FREE,
                rule_id=(
                    "seizure_free_duration_node_normalization_v0."
                    "since_without_date_boundary"
                ),
                certainty="medium",
            ),
        ),
    )
    regression_graph = ClinicalFrequencyStateGraph(
        source_row_index=8,
        nodes=(
            _node("sg-001", "seizure free for multiple year", GraphNodeKind.SEIZURE_FREE),
            _node(
                "sg-002",
                "seizure free for 6 month",
                GraphNodeKind.SEIZURE_FREE,
                rule_id="seizure_free.since_date",
            ),
        ),
    )

    rows, metadata = (
        month_bucket_duration_selection_ablation.run_month_bucket_duration_selection_ablation(
            [
                {
                    "source_row_index": 7,
                    "gold_normalized_label": "seizure free for multiple month",
                    "gold_label_kind": "seizure_free",
                    "gold_monthly_frequency": 0.0,
                    "replayed_graph": target_graph.model_dump(mode="json"),
                    "baseline_projection": {"final_label": "seizure free for multiple year"},
                }
            ],
            [
                {
                    "source_row_index": 8,
                    "gold_normalized_label": "seizure free for 6 month",
                    "gold_label_kind": "seizure_free",
                    "gold_monthly_frequency": 0.0,
                    "graph": regression_graph.model_dump(mode="json"),
                    "projection": {"final_label": "seizure free for multiple year"},
                    "projection_exact_label_match": False,
                }
            ],
            split="validation_hard_slices",
            split_manifest="gan2026_split_v1",
            policy_variant="graph_gated_v2",
        )
    )

    assert rows[0]["month_bucket_projection"]["final_label"] == (
        "seizure free for multiple month"
    )
    assert rows[0]["graph_gate"]["blocked"] is False
    assert rows[1]["month_bucket_projection"]["final_label"] == (
        "seizure free for multiple year"
    )
    assert rows[1]["graph_gate"] == {
        "blocked": True,
        "flags": ["selected_rule_not_duration_normalization_v0"],
        "selected_node_ids": ["sg-002"],
    }
    assert metadata["summary"]["graph_gate"] == {
        "blocked_rows": 1,
        "selected_rule_not_duration_normalization_v0": {"rows": 1},
    }


def test_graph_gated_month_bucket_records_boundary_state_risk() -> None:
    graph = ClinicalFrequencyStateGraph(
        source_row_index=9,
        nodes=(
            _node("sg-001", "seizure free for multiple year", GraphNodeKind.SEIZURE_FREE),
            _node(
                "duration-sg-002",
                "seizure free for 6 month",
                GraphNodeKind.SEIZURE_FREE,
                rule_id="seizure_free_duration_node_normalization_v0.dated_since_interval",
                certainty="medium",
            ),
            _node("sg-003", "unknown", GraphNodeKind.UNKNOWN_FREQUENCY),
        ),
    )

    rows, _metadata = (
        month_bucket_duration_selection_ablation.run_month_bucket_duration_selection_ablation(
            [],
            [
                {
                    "source_row_index": 9,
                    "gold_normalized_label": "unknown",
                    "gold_label_kind": "unknown",
                    "gold_monthly_frequency": 1000.0,
                    "graph": graph.model_dump(mode="json"),
                    "projection": {"final_label": "seizure free for multiple year"},
                    "projection_exact_label_match": False,
                }
            ],
            split="validation_hard_slices",
            split_manifest="gan2026_split_v1",
            policy_variant="graph_gated_v2",
        )
    )

    assert rows[0]["month_bucket_projection"]["final_label"] == (
        "seizure free for multiple year"
    )
    assert rows[0]["graph_gate"]["flags"] == ["active_boundary_state_node"]


def _node(
    node_id: str,
    label: str,
    kind: GraphNodeKind,
    *,
    rule_id: str = "unknown",
    certainty: str = "certain",
) -> StateGraphNode:
    parsed = label_to_frequency_record(label)
    return StateGraphNode(
        node_id=node_id,
        kind=kind,
        normalized_label=parsed.normalized_label,
        semantic_kind=parsed.kind,
        monthly_frequency=parsed.monthly_frequency,
        evidence=EvidenceSpan(text=label, start_char=0, end_char=len(label)),
        certainty=certainty,
        rule_id=rule_id,
    )
