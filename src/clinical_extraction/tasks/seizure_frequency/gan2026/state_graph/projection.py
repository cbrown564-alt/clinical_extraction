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
    policy_priority = _acd_projection_priority(node)
    if policy_priority is not None:
        return policy_priority, node.monthly_frequency
    if node.semantic_kind is FrequencyLabelKind.FREQUENCY:
        return 4, node.monthly_frequency
    if node.semantic_kind is FrequencyLabelKind.SEIZURE_FREE:
        return 3, node.monthly_frequency
    if node.semantic_kind is FrequencyLabelKind.UNKNOWN:
        return 2, node.monthly_frequency
    if node.semantic_kind is FrequencyLabelKind.UNRESOLVED_MULTIPLE:
        return 1, node.monthly_frequency
    return 0, node.monthly_frequency


def _acd_projection_priority(node: StateGraphNode) -> int | None:
    if node.rule_id == "projection_policy.acd_008.explicit_summary_rate":
        return 8
    if node.rule_id == "projection_policy.acd_009.previous_month_active_rate":
        return 8
    if node.rule_id == "rate.yesterday_or_today_count" and _is_major_recent_relapse(node):
        return 9
    return None


def _projection_rationale(node: StateGraphNode) -> str:
    acd_rationale = _acd_projection_rationale(node)
    if acd_rationale is not None:
        return acd_rationale
    if node.semantic_kind is FrequencyLabelKind.FREQUENCY:
        return "Projected the graph by selecting the highest current frequency node."
    if node.semantic_kind is FrequencyLabelKind.SEIZURE_FREE:
        return "Projected the graph from an explicit seizure-free state node."
    if node.semantic_kind is FrequencyLabelKind.UNKNOWN:
        return "Projected the graph from an unquantified seizure-frequency state node."
    if node.semantic_kind is FrequencyLabelKind.NO_REFERENCE:
        return "Projected the graph from a no-reference state node."
    return "Projected the graph from an unresolved multiple-frequency state node."


def _acd_projection_rationale(node: StateGraphNode) -> str | None:
    if node.rule_id == "projection_policy.acd_003.vague_count_without_denominator":
        return "Projected unknown because a vague count adjective lacks a calendar denominator."
    if node.rule_id == "projection_policy.acd_004.conditional_only_trigger":
        return "Projected unknown because a conditional-only trigger does not quantify cadence."
    if node.rule_id == "projection_policy.acd_005.relative_only_trend":
        return "Projected unknown because a relative-only trend lacks an absolute current rate."
    if node.rule_id == "projection_policy.acd_008.explicit_summary_rate":
        return "Projected the explicit current summary rate over a derived long-period average."
    if node.rule_id == "projection_policy.acd_009.previous_month_active_rate":
        return "Projected the previous-month active rate over a current-month-to-date zero count."
    if node.rule_id == "diary.date_list":
        return "Projected the graph from a diary date listing."
    if node.rule_id == "seizure_free.no_definite_events":
        return "Projected seizure freedom because recent events were triaged as non-epileptic."
    if node.rule_id == "rate.yesterday_or_today_count" and _is_major_recent_relapse(node):
        return "Projected the recent major-semiology relapse over lower-severity interictal rates."
    if (
        node.semantic_kind is FrequencyLabelKind.UNRESOLVED_MULTIPLE
        and node.normalized_label
        and node.normalized_label.startswith("multiple per ")
        and _has_vague_count_with_denominator(node)
    ):
        return "Projected the graph from a projection-compatible vague count with denominator."
    return None


def _is_major_recent_relapse(node: StateGraphNode) -> bool:
    evidence = node.evidence.text.lower()
    return (
        ("yesterday" in evidence or "today" in evidence)
        and any(term in evidence for term in ("tonic-clonic", "convulsive", "generalised"))
    )


def _has_vague_count_with_denominator(node: StateGraphNode) -> bool:
    evidence = node.evidence.text.lower()
    return any(
        token in evidence
        for token in ("several", "frequent", "many", "handful", "a few", "few")
    ) and any(
        denominator in evidence
        for denominator in ("last week", "per week", "weekly", "last month", "per month", "monthly")
    )
