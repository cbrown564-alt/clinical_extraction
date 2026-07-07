"""The final label as an explicit, ablatable graph query.

This is line 3.4 of the KG-grounded component-generation design note. It replaces
"the selector picks a string" for graph-sourced candidates with a single named
query, ``resolve_label(graph)``, that:

1. dual-validates the graph (only admitted nodes/edges participate);
2. resolves ``SUPERSEDES`` (drop the superseded statement);
3. resolves ``REFINES`` (the refiner replaces the vaguer base);
4. resolves ``CONTRADICTS`` (a current positive rate wins over a coexisting
   current seizure-free assertion - ADR ``0016`` / register C1 - flagging the
   seizure-free node ``contradicted_by_current_rate``; ``unknown`` is reserved for
   conflicts that cannot be attributed to a current rate);
5. delegates the final intra-kind rank to the tuned projection over the
   edge-resolved, ontology-admitted node set, and returns the surviving node's
   label plus the node ids, edges, and decision trace it used.

The query is one component with its own row-change accounting - not logic smeared
across prompt prose and nine selector versions. It is fed to the consensus+fresh
selector as a fourth ``graph-query`` candidate whose job is to mint a correct
component for the no-correct-component residual.

Per register C5 (deferred), the production path stays single-label: ``unknown``
is the only soft option and there is no ``outcome``/``allow_abstention`` surface.
"""

from __future__ import annotations

from collections.abc import Sequence

from pydantic import BaseModel, ConfigDict

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
    label_to_frequency_record,
)

from .edges import GraphEdge, GraphEdgeKind
from .graph import ClinicalFrequencyStateGraph, StateGraphNode
from .ontology import AdmissibleStateOntology
from .projection import GanGraphProjection, project_graph_to_gan
from .validation import GraphValidation, dual_validate_graph

_NO_REFERENCE_LABEL = "no seizure frequency reference"
_CONTRADICTED_BY_CURRENT_RATE = "contradicted_by_current_rate"


class GraphLabelResolution(BaseModel):
    model_config = ConfigDict(frozen=True)

    final_label: str
    final_kind: FrequencyLabelKind
    monthly_frequency: float
    selected_node_ids: tuple[str, ...]
    edges_used: tuple[GraphEdge, ...]
    used_edge_ids: tuple[str, ...] = ()
    admitted_node_ids: tuple[str, ...]
    rejected_node_ids: tuple[str, ...]
    superseded_node_ids: tuple[str, ...]
    refined_node_ids: tuple[str, ...]
    contradicted_node_ids: tuple[str, ...] = ()
    uncertainty_flags: tuple[str, ...] = ()
    decision_trace: tuple[str, ...] = ()
    rationale: str = ""
    resolver_id: str = "gan2026_state_graph_resolve_label_v1"


def _edge_id(edge: GraphEdge) -> str:
    return f"{edge.kind.value}:{edge.source_node_id}->{edge.target_node_id}"


def resolve_label(
    graph: ClinicalFrequencyStateGraph,
    *,
    ontology: AdmissibleStateOntology | None = None,
    validation: GraphValidation | None = None,
) -> GraphLabelResolution:
    """Resolve a graph to a single label by typed-edge resolution over the lattice."""

    ontology = ontology or AdmissibleStateOntology()
    validation = validation or dual_validate_graph(graph, ontology=ontology)

    admitted_ids = validation.admitted_node_ids
    admitted = [node for node in graph.nodes if node.node_id in admitted_ids]
    edges = validation.admitted_edges

    trace: list[str] = []
    rejected = sorted(validation.rejected_node_ids)
    trace.append(
        f"step0_admit: rejected {len(rejected)} node(s)"
        + (f": {', '.join(rejected)}" if rejected else "")
    )

    if not admitted:
        trace.append("no admitted nodes survived dual validation; defaulted to no-reference")
        return _resolution_from_label(
            _NO_REFERENCE_LABEL,
            selected_nodes=(),
            edges_used=edges,
            used_edge_ids=(),
            validation=validation,
            superseded_ids=(),
            refined_ids=(),
            decision_trace=tuple(trace),
            rationale="No admitted nodes survived dual validation; defaulted to no-reference.",
        )

    # Step 1 / Step 2: SUPERSEDES drops the older node; REFINES drops the vaguer.
    superseded_ids = {
        edge.target_node_id for edge in edges if edge.kind is GraphEdgeKind.SUPERSEDES
    }
    refined_ids = {edge.target_node_id for edge in edges if edge.kind is GraphEdgeKind.REFINES}
    used_edges: list[GraphEdge] = [
        edge
        for edge in edges
        if edge.kind in {GraphEdgeKind.SUPERSEDES, GraphEdgeKind.REFINES}
        and edge.target_node_id in admitted_ids
    ]
    if superseded_ids & admitted_ids:
        trace.append(f"step1_supersedes: dropped {sorted(superseded_ids & admitted_ids)}")
    if refined_ids & admitted_ids:
        trace.append(f"step2_refines: dropped {sorted(refined_ids & admitted_ids)}")

    dropped = superseded_ids | refined_ids
    surviving = [node for node in admitted if node.node_id not in dropped]
    if not surviving:
        # Everything was superseded/refined away by its own counterpart; fall back
        # to the full admitted set so resolution still has something to rank.
        surviving = admitted
        trace.append("all nodes dropped by counterparts; fell back to full admitted set")

    surviving_ids = {node.node_id for node in surviving}

    # Step 3: resolve CONTRADICTS. ADR 0016 (C1): a current positive rate wins over
    # a coexisting current seizure-free assertion. The derived CONTRADICTS edge is
    # rate-attributable by construction (its source is a positive FREQUENCY node),
    # so we flag the seizure-free node(s) and fall through to ranking, where the
    # projection ranks FREQUENCY > SEIZURE_FREE. unknown is reserved for conflicts
    # NOT attributable to a current rate (none are derived today).
    contradiction_edges = [
        edge
        for edge in edges
        if edge.kind is GraphEdgeKind.CONTRADICTS
        and edge.source_node_id in surviving_ids
        and edge.target_node_id in surviving_ids
    ]
    extra_flags: tuple[str, ...] = ()
    contradicted_ids: tuple[str, ...] = ()
    if contradiction_edges:
        contradicted_ids = tuple(sorted({e.target_node_id for e in contradiction_edges}))
        extra_flags = (_CONTRADICTED_BY_CURRENT_RATE,)
        used_edges.extend(contradiction_edges)
        trace.append(
            "step3_contradicts: current rate wins; flagged seizure-free node(s) "
            f"{list(contradicted_ids)} {_CONTRADICTED_BY_CURRENT_RATE}"
        )

    # Step 4: delegate the intra-kind rank to the tuned projection over the
    # edge-resolved, admitted node set, so resolve_label equals the baseline
    # projection on rows where no new mechanism fired (isolating the delta).
    projection = project_graph_to_gan(graph.model_copy(update={"nodes": tuple(surviving)}))
    trace.append(
        f"step4_rank: projection selected {list(projection.selected_node_ids)} "
        f"-> {projection.final_label}"
    )
    return _resolution_from_projection(
        projection,
        edges_used=edges,
        used_edge_ids=tuple(_edge_id(edge) for edge in used_edges),
        validation=validation,
        superseded_ids=tuple(sorted(superseded_ids)),
        refined_ids=tuple(sorted(refined_ids)),
        contradicted_ids=contradicted_ids,
        extra_flags=extra_flags,
        decision_trace=tuple(trace),
    )


def _edge_resolution_prefix(
    superseded_ids: tuple[str, ...],
    refined_ids: tuple[str, ...],
    contradicted_ids: tuple[str, ...],
) -> str:
    parts: list[str] = []
    if superseded_ids:
        parts.append(f"dropped {len(superseded_ids)} superseded node(s)")
    if refined_ids:
        parts.append(f"refined away {len(refined_ids)} vaguer node(s)")
    if contradicted_ids:
        parts.append(f"rate wins over {len(contradicted_ids)} seizure-free node(s)")
    return (" after " + ", ".join(parts)) if parts else ""


def _resolution_from_projection(
    projection: GanGraphProjection,
    *,
    edges_used: Sequence[GraphEdge],
    used_edge_ids: tuple[str, ...],
    validation: GraphValidation,
    superseded_ids: tuple[str, ...],
    refined_ids: tuple[str, ...],
    contradicted_ids: tuple[str, ...],
    extra_flags: tuple[str, ...],
    decision_trace: tuple[str, ...],
) -> GraphLabelResolution:
    prefix = _edge_resolution_prefix(superseded_ids, refined_ids, contradicted_ids)
    return GraphLabelResolution(
        final_label=projection.final_label,
        final_kind=projection.final_kind,
        monthly_frequency=projection.monthly_frequency,
        selected_node_ids=projection.selected_node_ids,
        edges_used=tuple(edges_used),
        used_edge_ids=used_edge_ids,
        admitted_node_ids=tuple(sorted(validation.admitted_node_ids)),
        rejected_node_ids=tuple(sorted(validation.rejected_node_ids)),
        superseded_node_ids=superseded_ids,
        refined_node_ids=refined_ids,
        contradicted_node_ids=contradicted_ids,
        uncertainty_flags=tuple(projection.uncertainty_flags) + extra_flags,
        decision_trace=decision_trace,
        rationale=f"{projection.rationale}{prefix}",
    )


def _resolution_from_label(
    label: str,
    *,
    selected_nodes: tuple[StateGraphNode, ...],
    edges_used: Sequence[GraphEdge],
    used_edge_ids: tuple[str, ...],
    validation: GraphValidation,
    superseded_ids: tuple[str, ...],
    refined_ids: tuple[str, ...],
    decision_trace: tuple[str, ...],
    contradicted_ids: tuple[str, ...] = (),
    uncertainty_flags: tuple[str, ...] = (),
    rationale: str,
) -> GraphLabelResolution:
    record = label_to_frequency_record(label)
    return GraphLabelResolution(
        final_label=record.normalized_label,
        final_kind=record.kind,
        monthly_frequency=record.monthly_frequency,
        selected_node_ids=tuple(node.node_id for node in selected_nodes),
        edges_used=tuple(edges_used),
        used_edge_ids=used_edge_ids,
        admitted_node_ids=tuple(sorted(validation.admitted_node_ids)),
        rejected_node_ids=tuple(sorted(validation.rejected_node_ids)),
        superseded_node_ids=superseded_ids,
        refined_node_ids=refined_ids,
        contradicted_node_ids=contradicted_ids,
        uncertainty_flags=uncertainty_flags,
        decision_trace=decision_trace,
        rationale=rationale,
    )
