from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.state_graph import (
    GraphNodeKind,
    ProjectionPolicy,
    build_state_graph,
    build_state_graph_from_atomic_claims,
    graph_invariance_signature,
    oracle_coverage_summary,
    project_graph_to_gan,
)


def test_state_graph_harvester_builds_source_near_nodes_with_exact_evidence() -> None:
    graph = build_state_graph(
        "Clinic Date: 10 January 2024. "
        "Current frequency: two focal seizures per week. "
        "No tonic-clonic seizures for one year.",
        source_row_index=7,
    )

    frequency_nodes = [
        node for node in graph.nodes if node.kind is GraphNodeKind.FREQUENCY_RATE
    ]
    seizure_free_nodes = [
        node for node in graph.nodes if node.kind is GraphNodeKind.SEIZURE_FREE
    ]

    assert graph.source_row_index == 7
    assert len(frequency_nodes) == 1
    assert frequency_nodes[0].normalized_label == "2 per week"
    assert frequency_nodes[0].evidence_text == "two focal seizures per week"
    assert frequency_nodes[0].evidence_start is not None
    assert frequency_nodes[0].evidence_end is not None
    assert len(seizure_free_nodes) == 1
    assert seizure_free_nodes[0].semantic_kind is FrequencyLabelKind.SEIZURE_FREE


def test_projection_solver_prefers_highest_current_frequency_over_partial_seizure_free() -> None:
    graph = build_state_graph(
        "She has no tonic-clonic seizures for one year, "
        "but still has three focal impaired-awareness seizures per month.",
    )

    projection = project_graph_to_gan(graph)

    assert projection.final_label == "3 per month"
    assert projection.final_kind is FrequencyLabelKind.FREQUENCY
    assert projection.selected_node_ids == ("sg-001",)
    assert projection.rationale == (
        "Projected the graph by selecting the highest current frequency node."
    )


def test_projection_solver_can_emit_uncertain_when_competing_hypotheses_remain() -> None:
    graph = build_state_graph(
        "One section says two seizures per month. "
        "A later diary summary says four seizures per month.",
    )

    projection = project_graph_to_gan(
        graph,
        policy=ProjectionPolicy(force_single_label=False),
    )

    assert projection.final_label == "unknown"
    assert projection.final_kind is FrequencyLabelKind.UNKNOWN
    assert projection.uncertainty_flags == ("competing_frequency_hypotheses",)
    assert projection.selected_node_ids == ("sg-001", "sg-002")


def test_counterfactual_invariance_signature_ignores_surface_order_and_writing() -> None:
    original = build_state_graph(
        "Current frequency: two seizures per week. "
        "They occur in clusters of three events each.",
    )
    paraphrase = build_state_graph(
        "The diary describes clusters of three events each. "
        "The current seizure rate is two seizures per week.",
    )

    assert graph_invariance_signature(original) == graph_invariance_signature(paraphrase)


def test_oracle_coverage_summary_reports_gold_representability() -> None:
    records = [
        _frequency_record(
            source_row_index=1,
            note_text="Current frequency: two seizures per week.",
            gold_label="2 per week",
        ),
        _frequency_record(
            source_row_index=2,
            note_text="Seizures are discussed but frequency remains unclear.",
            gold_label="1 per day",
        ),
        _frequency_record(
            source_row_index=3,
            note_text="Medication changed. No seizure frequency reference.",
            gold_label="no seizure frequency reference",
        ),
    ]

    summary = oracle_coverage_summary(records)

    assert summary.row_count == 3
    assert summary.representable_count == 2
    assert summary.representable_rate == 0.6667
    assert summary.by_gold_kind[FrequencyLabelKind.FREQUENCY.value]["representable"] == 1
    assert summary.by_gold_kind[FrequencyLabelKind.NO_REFERENCE.value]["representable"] == 1
    assert summary.missing_source_row_indices == (2,)


def test_llm_atomic_claim_graph_builder_requires_exact_evidence_for_certainty() -> None:
    graph = build_state_graph_from_atomic_claims(
        "Current frequency: two focal seizures per week.",
        [
            {
                "kind": "frequency_rate",
                "evidence": "two focal seizures per week",
                "normalized_label": "2 per week",
                "assertion_status": "asserted",
                "temporality": "current",
            },
            {
                "kind": "frequency_rate",
                "evidence": "paraphrased two weekly seizures",
                "normalized_label": "2 per week",
                "assertion_status": "asserted",
                "temporality": "current",
            },
        ],
    )

    assert graph.nodes[0].certainty == "certain"
    assert graph.nodes[0].evidence_start is not None
    assert graph.nodes[1].certainty == "unknown"
    assert graph.nodes[1].graph_errors == ("atomic_claim_evidence_not_exact",)


def _frequency_record(
    *,
    source_row_index: int,
    note_text: str,
    gold_label: str,
) -> GanFrequencyRecord:
    from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
        label_to_frequency_record,
    )

    parsed = label_to_frequency_record(gold_label)
    return GanFrequencyRecord(
        source_row_index=source_row_index,
        note_text=note_text,
        gold_label=gold_label,
        gold_reference="",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label=parsed.normalized_label,
        gold_label_kind=parsed.kind,
        gold_yearly_bounds=parsed.yearly_bounds,
        gold_monthly_frequency=parsed.monthly_frequency,
    )
