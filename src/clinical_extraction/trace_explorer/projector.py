from __future__ import annotations

from collections import defaultdict
from typing import Any

from clinical_extraction.trace_explorer.contracts import (
    GraphEdge,
    GraphNode,
    LedgerRow,
    TraceEnvelope,
)


def derive_ledger(trace: TraceEnvelope) -> list[LedgerRow]:
    rows: list[LedgerRow] = []
    for stage in trace.stages:
        evidence_by_id = {item.evidence_id: item for item in stage.evidence}
        if stage.changes:
            for change_index, change in enumerate(stage.changes):
                selected = tuple(
                    evidence_by_id[evidence_id]
                    for evidence_id in change.evidence_ids
                    if evidence_id in evidence_by_id
                )
                rows.append(
                    LedgerRow(
                        ledger_id=f"{stage.stage_id}:{change.change_id}",
                        sequence=stage.sequence * 100 + change_index,
                        stage_id=stage.stage_id,
                        stage_name=stage.name,
                        category=stage.category,
                        owner=change.operation_owner,
                        input_ref=change.before_ref
                        or (stage.input_refs[0] if stage.input_refs else None),
                        operation=change.operation or change.reason,
                        output_ref=change.after_ref or stage.output_ref,
                        change_type=change.kind,
                        selected_evidence=selected,
                        status=stage.status,
                        diagnostics=stage.diagnostics,
                        before_value=change.before_value,
                        after_value=change.after_value,
                        provenance={
                            "clinical_meaning_changed": change.clinical_meaning_changed,
                            "deterministic_rule": change.deterministic_rule,
                            "rule_category": change.rule_category,
                            "reason": change.reason,
                        },
                    )
                )
        else:
            rows.append(
                LedgerRow(
                    ledger_id=f"{stage.stage_id}:operation",
                    sequence=stage.sequence * 100,
                    stage_id=stage.stage_id,
                    stage_name=stage.name,
                    category=stage.category,
                    owner=stage.owner,
                    input_ref=stage.input_refs[0] if stage.input_refs else None,
                    operation=stage.summary,
                    output_ref=stage.output_ref,
                    change_type=None,
                    selected_evidence=tuple(
                        item for item in stage.evidence if item.role.value == "selected"
                    ),
                    status=stage.status,
                    diagnostics=stage.diagnostics,
                    provenance={"semantic_role": stage.semantic_role},
                )
            )
    return rows


def derive_graph(trace: TraceEnvelope) -> tuple[list[GraphNode], list[GraphEdge]]:
    nodes = [
        GraphNode(
            stage_id=stage.stage_id,
            sequence=stage.sequence,
            name=stage.name,
            category=stage.category,
            owner=stage.owner,
            status=stage.status,
            input_summary=stage.input_refs,
            output_summary=stage.output_ref,
            evidence_count=len(stage.evidence),
        )
        for stage in trace.stages
    ]
    edges = [
        GraphEdge(source=stage.stage_id, target=successor)
        for stage in trace.stages
        for successor in stage.successor_stage_ids
    ]
    return nodes, edges


def align_traces(left: TraceEnvelope, right: TraceEnvelope) -> list[dict[str, Any]]:
    left_roles: dict[str, list[Any]] = defaultdict(list)
    right_roles: dict[str, list[Any]] = defaultdict(list)
    for stage in left.stages:
        left_roles[stage.semantic_role].append(stage)
    for stage in right.stages:
        right_roles[stage.semantic_role].append(stage)

    roles = list(dict.fromkeys([stage.semantic_role for stage in left.stages + right.stages]))
    aligned: list[dict[str, Any]] = []
    for role in roles:
        left_items = left_roles.get(role, [])
        right_items = right_roles.get(role, [])
        length = max(len(left_items), len(right_items))
        for index in range(length):
            aligned.append(
                {
                    "semantic_role": role,
                    "left": (
                        left_items[index].model_dump(mode="json")
                        if index < len(left_items)
                        else None
                    ),
                    "right": (
                        right_items[index].model_dump(mode="json")
                        if index < len(right_items)
                        else None
                    ),
                }
            )
    return aligned
