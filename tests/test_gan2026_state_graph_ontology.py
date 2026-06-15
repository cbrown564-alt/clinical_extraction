"""Tests for the KG-grounded component-generation promotion of the Gan 2026
clinical-frequency state graph (design note 2026-06-15).

Covers the four promoted lines: typed edges, the admissible-state ontology, dual
validation, and the ``resolve_label`` graph query - plus the Stage A
ontology-enriched oracle-uplift coverage.
"""

from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.state_graph import (
    AdmissibleStateOntology,
    EvidenceShape,
    EvidenceSpan,
    GraphEdgeKind,
    GraphNodeKind,
    StateGraphNode,
    atomic_claim_from_table_claim,
    atomic_claim_viability_summary,
    atomic_claims_from_structured_record,
    build_state_graph,
    build_state_graph_from_atomic_claims,
    classify_evidence_shape,
    derive_edges,
    dual_validate_graph,
    ontology_coverage_summary,
    resolve_label,
)


def _claim(label: str, evidence: str, *, kind: str, temporality: str = "current") -> dict:
    return {
        "kind": kind,
        "normalized_label": label,
        "evidence": evidence,
        "assertion_status": "asserted",
        "temporality": temporality,
    }


# --------------------------------------------------------------------------- #
# Typed edges (3.1)
# --------------------------------------------------------------------------- #


def test_supersedes_edge_links_current_over_historical() -> None:
    note = "Historically up to 5 per week. Now he reports 1 seizure per month."
    graph = build_state_graph_from_atomic_claims(
        note,
        [
            _claim("5 per week", "up to 5 per week", kind="frequency_rate", temporality="historical"),
            _claim("1 per month", "1 seizure per month", kind="frequency_rate"),
        ],
    )
    edges = derive_edges(graph)
    supersedes = [e for e in edges if e.kind is GraphEdgeKind.SUPERSEDES]
    assert len(supersedes) == 1
    # The current node is the source; the historical node is the target.
    assert supersedes[0].source_node_id == "llm-sg-002"
    assert supersedes[0].target_node_id == "llm-sg-001"


def test_contradicts_edge_links_positive_rate_and_seizure_free() -> None:
    note = "He reports 3 seizures per month. He also says he is seizure free."
    graph = build_state_graph_from_atomic_claims(
        note,
        [
            _claim("3 per month", "3 seizures per month", kind="frequency_rate"),
            _claim("seizure free", "seizure free", kind="seizure_free"),
        ],
    )
    contradicts = [e for e in derive_edges(graph) if e.kind is GraphEdgeKind.CONTRADICTS]
    assert len(contradicts) == 1


def test_refines_edge_links_cluster_burden_to_cadence() -> None:
    note = "Seizures occur in clusters about once per week, roughly 3 per cluster per week."
    graph = build_state_graph_from_atomic_claims(
        note,
        [
            _claim("1 cluster per week", "clusters about once per week", kind="cluster_frequency"),
            _claim("3 per cluster per week", "3 per cluster per week", kind="cluster_frequency"),
        ],
    )
    refines = [e for e in derive_edges(graph) if e.kind is GraphEdgeKind.REFINES]
    assert len(refines) == 1
    assert refines[0].rule_id == "state_graph.edge.refines.cluster_burden"


def test_no_spurious_edges_for_single_clean_rate() -> None:
    graph = build_state_graph("Patient reports about 2 seizures per week currently.")
    assert derive_edges(graph) == ()


# --------------------------------------------------------------------------- #
# Admissible-state ontology (3.2)
# --------------------------------------------------------------------------- #


def test_evidence_shape_classification() -> None:
    note = "Last seizure was 6 months ago."
    graph = build_state_graph_from_atomic_claims(
        note, [_claim("1 per 6 month", "Last seizure was 6 months ago", kind="frequency_rate")]
    )
    assert classify_evidence_shape(graph.nodes[0]) is EvidenceShape.LAST_EVENT_ONLY

    quantified = build_state_graph("about 2 seizures per week").nodes[0]
    assert classify_evidence_shape(quantified) is EvidenceShape.QUANTIFIED


def test_ontology_rejects_over_inference_out_of_unknown() -> None:
    ontology = AdmissibleStateOntology()
    graph = build_state_graph_from_atomic_claims(
        "Last seizure was 6 months ago.",
        [_claim("1 per 6 month", "Last seizure was 6 months ago", kind="frequency_rate")],
    )
    result = ontology.is_admissible_assignment(graph.nodes[0])
    assert result.admissible is False
    assert result.reason.startswith("over_inference_out_of_unknown")


def test_ontology_admits_unknown_from_last_event_evidence() -> None:
    ontology = AdmissibleStateOntology()
    graph = build_state_graph_from_atomic_claims(
        "Last seizure was 6 months ago.",
        [_claim("unknown", "Last seizure was 6 months ago", kind="unknown")],
    )
    assert ontology.is_admissible_assignment(graph.nodes[0]).admissible is True


def test_ontology_guard_is_graph_path_only_not_deterministic() -> None:
    # ADR 0017 (C2): the over-inference guard runs on the graph/LLM path only. A
    # curated deterministic node (sg- prefix) with open-ended-since evidence but a
    # seizure_free state is trusted; its uncurated (llm-) twin is still rejected.
    ontology = AdmissibleStateOntology()
    curated = StateGraphNode(
        node_id="sg-001",
        kind=GraphNodeKind.SEIZURE_FREE,
        normalized_label="seizure free for 6 month",
        semantic_kind=FrequencyLabelKind.SEIZURE_FREE,
        monthly_frequency=0.0,
        evidence=EvidenceSpan(
            text="Seizure-free since 27 March 2024", start_char=0, end_char=32
        ),
        rule_id="seizure_free.since_date",
    )
    assert ontology.is_admissible_assignment(curated).admissible is True

    uncurated = curated.model_copy(
        update={"node_id": "llm-sg-001", "rule_id": "llm.atomic_claim"}
    )
    rejected = ontology.is_admissible_assignment(uncurated)
    assert rejected.admissible is False
    assert rejected.reason.startswith("over_inference_out_of_unknown")


def test_vague_cluster_count_is_unknown_only_shape() -> None:
    # C4 (register): a vague *count of clusters* must not be rescued into a
    # quantified frequency by its trailing cadence denominator.
    node = StateGraphNode(
        node_id="llm-sg-001",
        kind=GraphNodeKind.CLUSTER_FREQUENCY,
        normalized_label="unknown",
        semantic_kind=FrequencyLabelKind.FREQUENCY,
        monthly_frequency=1.0,
        evidence=EvidenceSpan(
            text="several clusters per month", start_char=0, end_char=26
        ),
        rule_id="llm.atomic_claim",
    )
    assert classify_evidence_shape(node) is EvidenceShape.VAGUE_COUNT
    # ...and the graph-path guard therefore rejects an uncurated frequency mint.
    assert AdmissibleStateOntology().is_admissible_assignment(node).admissible is False


def test_ontology_blocks_cluster_cadence_change_under_refine() -> None:
    ontology = AdmissibleStateOntology()
    # Refiner cadence is weekly, base cadence monthly: refining must not move it.
    graph = build_state_graph_from_atomic_claims(
        "clusters monthly; separately 3 per cluster per week",
        [
            _claim("1 cluster per month", "clusters monthly", kind="cluster_frequency"),
            _claim("3 per cluster per week", "3 per cluster per week", kind="cluster_frequency"),
        ],
    )
    # No same-cadence refine edge should be derived at all.
    refines = [e for e in derive_edges(graph) if e.kind is GraphEdgeKind.REFINES]
    assert refines == []


# --------------------------------------------------------------------------- #
# Dual validation (3.3)
# --------------------------------------------------------------------------- #


def test_dual_validation_flags_but_retains_over_inference_node() -> None:
    graph = build_state_graph_from_atomic_claims(
        "Last seizure was 6 months ago.",
        [
            _claim("1 per 6 month", "Last seizure was 6 months ago", kind="frequency_rate"),
            _claim("unknown", "Last seizure was 6 months ago", kind="unknown"),
        ],
    )
    validation = dual_validate_graph(graph)
    assert validation.admitted_node_ids == frozenset({"llm-sg-002"})
    assert "llm-sg-001" in validation.rejected_node_ids
    # The rejected node is retained with provenance, not dropped from the graph.
    assert len(validation.node_validations) == 2


def test_dual_validation_rejects_node_without_located_span() -> None:
    graph = build_state_graph_from_atomic_claims(
        "no matching text here",
        [_claim("2 per week", "phantom evidence not in note", kind="frequency_rate")],
    )
    validation = dual_validate_graph(graph)
    [node_validation] = validation.node_validations
    assert node_validation.structural_valid is False
    assert node_validation.admitted is False


# --------------------------------------------------------------------------- #
# resolve_label graph query (3.4)
# --------------------------------------------------------------------------- #


def test_resolve_label_preserves_unknown_on_over_inference() -> None:
    graph = build_state_graph_from_atomic_claims(
        "Last seizure was 6 months ago.",
        [
            _claim("1 per 6 month", "Last seizure was 6 months ago", kind="frequency_rate"),
            _claim("unknown", "Last seizure was 6 months ago", kind="unknown"),
        ],
    )
    resolution = resolve_label(graph)
    assert resolution.final_kind is FrequencyLabelKind.UNKNOWN


def test_resolve_label_current_rate_wins_over_seizure_free() -> None:
    # ADR 0016 (C1): a current positive rate wins over a coexisting current
    # seizure-free assertion; the seizure-free node is flagged, not collapsed to
    # unknown.
    graph = build_state_graph_from_atomic_claims(
        "He reports 3 seizures per month. He also says he is seizure free.",
        [
            _claim("3 per month", "3 seizures per month", kind="frequency_rate"),
            _claim("seizure free", "seizure free", kind="seizure_free"),
        ],
    )
    resolution = resolve_label(graph)
    assert resolution.final_kind is FrequencyLabelKind.FREQUENCY
    assert resolution.final_label == "3 per month"
    assert "contradicted_by_current_rate" in resolution.uncertainty_flags
    # The seizure-free node (the CONTRADICTS target) is the one flagged.
    assert resolution.contradicted_node_ids == ("llm-sg-002",)


def test_resolve_label_drops_superseded_historical_rate() -> None:
    graph = build_state_graph_from_atomic_claims(
        "Historically up to 5 per week. Now he reports 1 seizure per month.",
        [
            _claim("5 per week", "up to 5 per week", kind="frequency_rate", temporality="historical"),
            _claim("1 per month", "1 seizure per month", kind="frequency_rate"),
        ],
    )
    resolution = resolve_label(graph)
    assert resolution.final_label == "1 per month"
    assert resolution.superseded_node_ids == ("llm-sg-001",)


def test_resolve_label_uses_cluster_burden_refinement() -> None:
    graph = build_state_graph_from_atomic_claims(
        "Seizures occur in clusters about once per week, roughly 3 per cluster per week.",
        [
            _claim("1 cluster per week", "clusters about once per week", kind="cluster_frequency"),
            _claim("3 per cluster per week", "3 per cluster per week", kind="cluster_frequency"),
        ],
    )
    resolution = resolve_label(graph)
    assert resolution.refined_node_ids == ("llm-sg-001",)
    assert resolution.selected_node_ids == ("llm-sg-002",)


def test_resolve_label_defaults_to_no_reference_when_nothing_admitted() -> None:
    graph = build_state_graph_from_atomic_claims(
        "no matching text here",
        [_claim("2 per week", "phantom evidence not in note", kind="frequency_rate")],
    )
    resolution = resolve_label(graph)
    assert resolution.final_kind is FrequencyLabelKind.NO_REFERENCE
    assert resolution.selected_node_ids == ()


# --------------------------------------------------------------------------- #
# Stage A - ontology-enriched oracle uplift, by band
# --------------------------------------------------------------------------- #


def _record(source_row_index: int, note_text: str, gold_label: str) -> GanFrequencyRecord:
    record = label_to_frequency_record(gold_label)
    return GanFrequencyRecord(
        source_row_index=source_row_index,
        note_text=note_text,
        gold_label=gold_label,
        gold_reference="",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label=record.normalized_label,
        gold_label_kind=record.kind,
        gold_yearly_bounds=record.yearly_bounds,
        gold_monthly_frequency=record.monthly_frequency,
    )


# --------------------------------------------------------------------------- #
# Stage B - atomic-claim graph viability gate (gold-free)
# --------------------------------------------------------------------------- #


def test_claim_table_normalizes_raw_frequency_into_gan_label() -> None:
    claim = {
        "claim_type": "frequency",
        "evidence": "17 per month",
        "raw_frequency": "17 per month",
        "assertion_status": "asserted",
        "temporality": "current",
        "semiology": "GTCS",
    }
    converted = atomic_claim_from_table_claim(claim)
    assert converted["normalized_label"] == "17 per month"
    assert converted["kind"] == "frequency"
    assert converted["applies_to"] == "GTCS"


def test_claim_table_leaves_label_unset_when_no_raw_frequency() -> None:
    claim = {"claim_type": "cluster_frequency", "evidence": "variable clustering"}
    assert atomic_claim_from_table_claim(claim)["normalized_label"] is None


def test_claim_table_normalization_exercises_the_over_inference_guard() -> None:
    # A last-event mention whose raw_frequency parses to a rate is the over-inference
    # the C2 guard must catch once the claim is given a quantifying label.
    record = {
        "claims": [
            {
                "claim_type": "last_event_only",
                "evidence": "including two episodes witnessed by a friend",
                "raw_frequency": "two episodes",
                "assertion_status": "asserted",
                "temporality": "recent",
            }
        ]
    }
    claims = atomic_claims_from_structured_record(record)
    graph = build_state_graph_from_atomic_claims(
        "He had a rough spell including two episodes witnessed by a friend.",
        claims,
    )
    node = graph.nodes[0]
    assert node.semantic_kind is FrequencyLabelKind.FREQUENCY
    assert node.kind is GraphNodeKind.LAST_EVENT_ONLY
    result = AdmissibleStateOntology().is_admissible_assignment(node)
    assert result.admissible is False
    assert result.reason.startswith("over_inference_out_of_unknown")


def test_atomic_claim_viability_summary_counts_admission_and_resolution() -> None:
    # A clean quantified node (admitted, localized) plus an over-inference mint
    # (rejected by the C2 guard) plus a structurally-broken node (phantom evidence).
    clean = build_state_graph_from_atomic_claims(
        "He reports about 2 seizures per week.",
        [_claim("2 per week", "about 2 seizures per week", kind="frequency_rate")],
    )
    over_inference = build_state_graph_from_atomic_claims(
        "Last seizure was 6 months ago.",
        [_claim("1 per 6 month", "Last seizure was 6 months ago", kind="frequency_rate")],
    )
    broken = build_state_graph_from_atomic_claims(
        "no matching text here",
        [_claim("2 per week", "phantom evidence not in note", kind="frequency_rate")],
    )

    summary = atomic_claim_viability_summary([clean, over_inference, broken])
    assert summary.row_count == 3
    admission = summary.node_admission
    assert admission.total_nodes == 3
    # The over-inference mint is the C2 guard's target; the phantom-evidence node
    # is a structural rejection. The two are reported apart.
    assert admission.over_inference_rejected == 1
    assert admission.structural_rejected == 1
    assert admission.admitted == 1
    assert admission.exact_evidence == 2

    resolve = summary.resolve
    assert resolve.rows_with_decision_trace == 3
    # Only the clean row is component-localized; the over-inference and broken rows
    # both default to no-reference because their only node is rejected.
    assert resolve.rows_with_localized_selection == 1
    assert resolve.rows_defaulted_no_admission == 2


def test_atomic_claim_viability_summary_guard_silent_on_unknown_only_nodes() -> None:
    # When the builder mints only unknown-state nodes (the v3 atomic-claim shape),
    # the over-inference guard has nothing to police and fires zero times, yet the
    # structural and interpretability sub-gates still pass.
    graph = build_state_graph_from_atomic_claims(
        "Last seizure was 6 months ago.",
        [_claim("unknown", "Last seizure was 6 months ago", kind="unknown")],
    )
    summary = atomic_claim_viability_summary([graph])
    assert summary.node_admission.over_inference_rejected == 0
    assert summary.node_admission.admitted == 1
    assert summary.resolve.rows_with_localized_selection == 1


def test_ontology_coverage_summary_reports_by_band() -> None:
    records = [
        _record(1, "Patient reports about 2 seizures per week currently.", "2 per week"),
        _record(2, "Routine review, no relevant seizure information.", "unknown"),
    ]
    summary = ontology_coverage_summary(records)
    assert summary.row_count == 2
    assert set(summary.by_band) == {"band_weekly", "band_unknown"}
    assert summary.by_band["band_weekly"].total == 1
    # resolve_label correctness is bounded above by representability.
    for band in summary.by_band.values():
        assert band.resolve_correct <= band.total
        assert band.admitted_representable <= band.total
