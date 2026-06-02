from __future__ import annotations

from collections.abc import Sequence

from pydantic import BaseModel, ConfigDict

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
    label_to_frequency_record,
)

from .graph import ClinicalFrequencyStateGraph, StateGraphNode


class ProjectionPolicy(BaseModel):
    model_config = ConfigDict(frozen=True)

    force_single_label: bool = True
    allow_competing_frequency_uncertainty: bool = True


class GanGraphProjection(BaseModel):
    model_config = ConfigDict(frozen=True)

    final_label: str
    final_kind: FrequencyLabelKind
    monthly_frequency: float
    selected_node_ids: tuple[str, ...]
    rationale: str
    evidence: str
    uncertainty_flags: tuple[str, ...] = ()
    projection_policy: str = "gan2026_state_graph_projection_v0"


def project_graph_to_gan(
    graph: ClinicalFrequencyStateGraph,
    *,
    policy: ProjectionPolicy | None = None,
) -> GanGraphProjection:
    policy = policy or ProjectionPolicy()
    selected_nodes = _select_projection_nodes(graph.nodes, policy)

    if not selected_nodes:
        return _projection_from_label(
            "no seizure frequency reference",
            selected_nodes=(),
            rationale="Projected no-reference because the graph has no usable frequency nodes.",
            evidence="",
        )

    if _should_emit_competing_uncertainty(selected_nodes, policy):
        rationale = (
            "Preserved uncertainty because competing current frequency hypotheses remain."
        )
        return _projection_from_label(
            "unknown",
            selected_nodes=selected_nodes,
            rationale=rationale,
            evidence=" | ".join(node.evidence.text for node in selected_nodes),
            uncertainty_flags=("competing_frequency_hypotheses",),
        )

    selected = max(selected_nodes, key=lambda node: _projection_priority(node))
    return _projection_from_label(
        selected.normalized_label or "unknown",
        selected_nodes=(selected,),
        rationale=_projection_rationale(selected),
        evidence=selected.evidence.text,
    )


def _select_projection_nodes(
    nodes: Sequence[StateGraphNode],
    policy: ProjectionPolicy,
) -> tuple[StateGraphNode, ...]:
    current_frequency_nodes = tuple(
        node
        for node in nodes
        if node.semantic_kind is FrequencyLabelKind.FREQUENCY
        and node.assertion_status == "asserted"
        and node.temporality == "current"
    )
    if current_frequency_nodes:
        if policy.allow_competing_frequency_uncertainty and not policy.force_single_label:
            return current_frequency_nodes
        return current_frequency_nodes

    for kind in (
        FrequencyLabelKind.SEIZURE_FREE,
        FrequencyLabelKind.UNKNOWN,
        FrequencyLabelKind.NO_REFERENCE,
        FrequencyLabelKind.UNRESOLVED_MULTIPLE,
    ):
        selected = tuple(node for node in nodes if node.semantic_kind is kind)
        if selected:
            return selected
    return ()


def _should_emit_competing_uncertainty(
    nodes: Sequence[StateGraphNode],
    policy: ProjectionPolicy,
) -> bool:
    if policy.force_single_label or len(nodes) <= 1:
        return False
    labels = {node.normalized_label for node in nodes}
    return len(labels) > 1


def _projection_from_label(
    label: str,
    *,
    selected_nodes: Sequence[StateGraphNode],
    rationale: str,
    evidence: str,
    uncertainty_flags: tuple[str, ...] = (),
) -> GanGraphProjection:
    record = label_to_frequency_record(label)
    return GanGraphProjection(
        final_label=record.normalized_label,
        final_kind=record.kind,
        monthly_frequency=record.monthly_frequency,
        selected_node_ids=tuple(node.node_id for node in selected_nodes),
        rationale=rationale,
        evidence=evidence,
        uncertainty_flags=uncertainty_flags,
    )


def _projection_priority(node: StateGraphNode) -> tuple[int, float]:
    if node.semantic_kind is FrequencyLabelKind.FREQUENCY:
        return 4, node.monthly_frequency
    if node.semantic_kind is FrequencyLabelKind.SEIZURE_FREE:
        return 3, node.monthly_frequency
    if node.semantic_kind is FrequencyLabelKind.UNKNOWN:
        return 2, node.monthly_frequency
    if node.semantic_kind is FrequencyLabelKind.UNRESOLVED_MULTIPLE:
        return 1, node.monthly_frequency
    return 0, node.monthly_frequency


def _projection_rationale(node: StateGraphNode) -> str:
    if node.semantic_kind is FrequencyLabelKind.FREQUENCY:
        return "Projected the graph by selecting the highest current frequency node."
    if node.semantic_kind is FrequencyLabelKind.SEIZURE_FREE:
        return "Projected the graph from an explicit seizure-free state node."
    if node.semantic_kind is FrequencyLabelKind.UNKNOWN:
        return "Projected the graph from an unquantified seizure-frequency state node."
    if node.semantic_kind is FrequencyLabelKind.NO_REFERENCE:
        return "Projected the graph from a no-reference state node."
    return "Projected the graph from an unresolved multiple-frequency state node."
