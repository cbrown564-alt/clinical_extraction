"""Typed relations between clinical-frequency state-graph nodes.

This is line 3.1 of the KG-grounded component-generation design note: promote the
flat ``competing_hypothesis_node_ids`` bag into a minimal, closed set of typed
edges so the recency and refinement decisions the prompt prose and consensus+fresh
selector currently arbitrate become *edge resolutions over typed nodes*, each
carrying the provenance of both endpoints.

Three edge kinds, no more:

- ``SUPERSEDES`` - a current statement overrides an older one for the same target.
- ``REFINES`` - a more specific statement refines a vaguer one (cluster burden
  refines cluster cadence; an explicit count+window refines a vague mention).
- ``CONTRADICTS`` - a positive current rate conflicts with a current
  seizure-free assertion.

Edges are *derived* from a built graph rather than stored on the (frozen) graph
model, so existing serialized artifacts are unchanged.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)

from .graph import ClinicalFrequencyStateGraph, GraphNodeKind, StateGraphNode

# Temporality tokens we treat as "older than current". The deterministic builder
# leaves nodes at the default ``current``; the atomic-claim builder may set these.
HISTORICAL_TEMPORALITY: frozenset[str] = frozenset(
    {"historical", "past", "previous", "prior", "former", "remote"}
)
CURRENT_TEMPORALITY: frozenset[str] = frozenset({"current", "present", "recent"})

_PER_CLUSTER_COUNT_RE = re.compile(r"(\d+(?:\s*to\s*\d+)?)\s*per\s+cluster", re.IGNORECASE)
_CADENCE_PERIOD_RE = re.compile(r"\bper\s+(day|week|month|year)s?\b", re.IGNORECASE)


class GraphEdgeKind(StrEnum):
    SUPERSEDES = "supersedes"
    REFINES = "refines"
    CONTRADICTS = "contradicts"


class GraphEdge(BaseModel):
    """A typed, provenance-bearing relation between two state-graph nodes.

    ``source_node_id`` is the node doing the acting (the later/refining/positive
    statement); ``target_node_id`` is the node being acted upon (the
    earlier/vaguer/contradicted statement).
    """

    model_config = ConfigDict(frozen=True)

    kind: GraphEdgeKind
    source_node_id: str
    target_node_id: str
    rule_id: str
    rationale: str


def derive_edges(graph: ClinicalFrequencyStateGraph) -> tuple[GraphEdge, ...]:
    """Derive the closed set of typed edges for a built state graph."""

    nodes = graph.nodes
    edges: list[GraphEdge] = []
    edges.extend(_supersedes_edges(nodes))
    edges.extend(_refines_edges(nodes))
    edges.extend(_contradicts_edges(nodes))
    # Stable, deterministic ordering so downstream serialization is reproducible.
    return tuple(
        sorted(edges, key=lambda edge: (edge.kind.value, edge.source_node_id, edge.target_node_id))
    )


def cadence_period(node: StateGraphNode) -> str | None:
    """Return the trailing ``per <period>`` cadence token of a node, if any.

    For cluster labels this is the *clusters-per-period* cadence, which the
    ontology treats as immutable under ``REFINES``. The normalized label drops the
    ``per cluster`` axis, so we read the label first and fall back to the evidence.
    """

    for text in (node.normalized_label or "", node.evidence.text):
        matches = _CADENCE_PERIOD_RE.findall(text)
        if matches:
            return matches[-1].lower()
    return None


def per_cluster_count_text(node: StateGraphNode) -> str | None:
    """Return the events-per-cluster token of a cluster node, if present.

    The scoring grammar normalizes the ``per cluster`` axis out of the label, so
    this reads the evidence span as well as the label.
    """

    for text in (node.normalized_label or "", node.evidence.text):
        match = _PER_CLUSTER_COUNT_RE.search(text)
        if match:
            return match.group(1).strip().lower()
    return None


def evidence_overlaps(left: StateGraphNode, right: StateGraphNode) -> bool:
    """Whether two nodes' evidence spans plausibly describe the same statement."""

    ls, le = left.evidence.start_char, left.evidence.end_char
    rs, re_ = right.evidence.start_char, right.evidence.end_char
    if None not in (ls, le, rs, re_):
        return ls < re_ and rs < le  # type: ignore[operator]
    left_text = left.evidence.text.lower().strip()
    right_text = right.evidence.text.lower().strip()
    if not left_text or not right_text:
        return False
    return left_text in right_text or right_text in left_text


def _supersedes_edges(nodes: Sequence[StateGraphNode]) -> list[GraphEdge]:
    edges: list[GraphEdge] = []
    for current in nodes:
        if not _is_current_assertion(current):
            continue
        for older in nodes:
            if older.node_id == current.node_id:
                continue
            if older.temporality not in HISTORICAL_TEMPORALITY:
                continue
            if not _same_target(current, older):
                continue
            if not _state_bearing(current) or not _state_bearing(older):
                continue
            edges.append(
                GraphEdge(
                    kind=GraphEdgeKind.SUPERSEDES,
                    source_node_id=current.node_id,
                    target_node_id=older.node_id,
                    rule_id="state_graph.edge.supersedes.current_over_historical",
                    rationale=(
                        f"Current node {current.node_id} supersedes historical node "
                        f"{older.node_id} for the same target."
                    ),
                )
            )
    return edges


def _refines_edges(nodes: Sequence[StateGraphNode]) -> list[GraphEdge]:
    edges: list[GraphEdge] = []
    for refiner in nodes:
        for base in nodes:
            if refiner.node_id == base.node_id:
                continue
            rule = _refines_rule(refiner, base)
            if rule is None:
                continue
            edges.append(
                GraphEdge(
                    kind=GraphEdgeKind.REFINES,
                    source_node_id=refiner.node_id,
                    target_node_id=base.node_id,
                    rule_id=rule,
                    rationale=(
                        f"Node {refiner.node_id} refines vaguer node {base.node_id}."
                    ),
                )
            )
    return edges


def _contradicts_edges(nodes: Sequence[StateGraphNode]) -> list[GraphEdge]:
    edges: list[GraphEdge] = []
    positives = [
        node
        for node in nodes
        if _is_current_assertion(node)
        and node.semantic_kind is FrequencyLabelKind.FREQUENCY
        and node.monthly_frequency > 0
    ]
    seizure_free = [
        node
        for node in nodes
        if _is_current_assertion(node)
        and node.semantic_kind is FrequencyLabelKind.SEIZURE_FREE
    ]
    for positive in positives:
        for free in seizure_free:
            if not _same_target(positive, free):
                continue
            edges.append(
                GraphEdge(
                    kind=GraphEdgeKind.CONTRADICTS,
                    source_node_id=positive.node_id,
                    target_node_id=free.node_id,
                    rule_id="state_graph.edge.contradicts.positive_rate_vs_seizure_free",
                    rationale=(
                        f"Positive current rate {positive.node_id} contradicts current "
                        f"seizure-free assertion {free.node_id}."
                    ),
                )
            )
    return edges


def _refines_rule(refiner: StateGraphNode, base: StateGraphNode) -> str | None:
    # Cluster burden refines cluster cadence: refiner adds a per-cluster count to a
    # cadence-only node. The two clauses usually sit apart in the note, so we link
    # them by a shared cadence period rather than by span overlap.
    if (
        refiner.kind is GraphNodeKind.CLUSTER_FREQUENCY
        and base.kind is GraphNodeKind.CLUSTER_FREQUENCY
        and per_cluster_count_text(refiner) is not None
        and per_cluster_count_text(base) is None
        and _shares_cluster_context(refiner, base)
    ):
        return "state_graph.edge.refines.cluster_burden"
    # Explicit count+window refines a vague mention (unknown/unresolved-multiple).
    if (
        refiner.semantic_kind is FrequencyLabelKind.FREQUENCY
        and refiner.monthly_frequency > 0
        and base.semantic_kind
        in {FrequencyLabelKind.UNKNOWN, FrequencyLabelKind.UNRESOLVED_MULTIPLE}
        and evidence_overlaps(refiner, base)
    ):
        return "state_graph.edge.refines.count_window_over_vague"
    return None


def _shares_cluster_context(refiner: StateGraphNode, base: StateGraphNode) -> bool:
    if evidence_overlaps(refiner, base):
        return True
    refiner_period = cadence_period(refiner)
    base_period = cadence_period(base)
    return refiner_period is not None and refiner_period == base_period


def _is_current_assertion(node: StateGraphNode) -> bool:
    return node.assertion_status == "asserted" and node.temporality not in HISTORICAL_TEMPORALITY


def _state_bearing(node: StateGraphNode) -> bool:
    return node.semantic_kind in {
        FrequencyLabelKind.FREQUENCY,
        FrequencyLabelKind.SEIZURE_FREE,
        FrequencyLabelKind.UNRESOLVED_MULTIPLE,
    }


def _same_target(left: StateGraphNode, right: StateGraphNode) -> bool:
    return _normalized_applies_to(left) == _normalized_applies_to(right)


def _normalized_applies_to(node: StateGraphNode) -> str | None:
    if node.applies_to is None:
        return None
    text = node.applies_to.strip().lower()
    return text or None
