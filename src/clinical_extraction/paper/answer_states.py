"""Ordered answer hops and the graph derived from them."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal

from clinical_extraction.paper.rungs import (
    CELL_ORDER,
    RungId,
    cell_id_from_legacy_rung,
    normalize_effect_class,
)

EffectClass = Literal["extract", "encode", "select", "validation", "projection"]
HopOwner = Literal["rules", "model", "replay"]


def make_hop(
    *,
    stage_id: str,
    owner: HopOwner,
    effect_class: EffectClass | str,
    before: str | None,
    after: str | None,
    evidence: str | None = None,
    evidence_exact: bool | None = None,
    operands: Sequence[str] | None = None,
    vetoed: str | None = None,
    cell_id: RungId | str,
    cell_order: int | None = None,
    rung: int | None = None,
) -> dict[str, Any]:
    """Build one recorded answer version.

    New emission uses ``cell_id`` and ``cell_order``. Legacy ``rung`` ints
    are accepted as a read/write alias for older callers and sealed hops.
    """

    resolved = _resolve_cell(cell_id=cell_id, cell_order=cell_order, rung=rung)
    return {
        "stage_id": stage_id,
        "owner": owner,
        "effect_class": normalize_effect_class(effect_class),
        "before": before,
        "after": after,
        "evidence": evidence,
        "evidence_exact": evidence_exact,
        "operands": list(operands or ()),
        "vetoed": vetoed,
        "cell_id": resolved,
        "cell_order": CELL_ORDER[resolved],
        "changed": before != after,
    }


def normalize_hop(hop: Mapping[str, Any]) -> dict[str, Any]:
    """Accept sealed hops that used ``rung`` / old effect-class strings."""

    payload = dict(hop)
    cell = cell_id_from_legacy_rung(
        payload.get("cell_id") or payload.get("rung")
    )
    if cell is not None:
        payload["cell_id"] = cell
        payload["cell_order"] = CELL_ORDER[cell]
    if "effect_class" in payload:
        payload["effect_class"] = normalize_effect_class(str(payload["effect_class"]))
    return payload


def graph_from_hops(
    hops: Sequence[Mapping[str, Any]],
    unused_candidates: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    """Derive a state graph. The hop log remains the stored object."""

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    seen: set[str] = set()
    last_id: str | None = None
    for index, hop in enumerate(hops):
        hop = normalize_hop(hop)
        label = hop.get("after")
        if label is None:
            continue
        node_id = f"answer:{index}:{label}"
        if label not in seen or hop.get("changed"):
            nodes.append(
                {
                    "id": node_id,
                    "kind": "answer",
                    "label": label,
                    "stage_id": hop["stage_id"],
                    "cell_id": hop.get("cell_id"),
                    "cell_order": hop.get("cell_order"),
                }
            )
            seen.add(str(label))
        if last_id is not None and hop.get("changed"):
            edges.append(
                {
                    "from": last_id,
                    "to": node_id,
                    "stage_id": hop["stage_id"],
                    "effect_class": hop["effect_class"],
                    "owner": hop["owner"],
                }
            )
        if hop.get("changed") or last_id is None:
            last_id = node_id
    for candidate in unused_candidates:
        nodes.append(
            {
                "id": str(candidate["id"]),
                "kind": "unused_candidate",
                "label": candidate.get("label"),
                "candidate_kind": candidate.get("kind"),
            }
        )
    return {"nodes": nodes, "edges": edges}


def unused_model_events(
    events: Sequence[Mapping[str, Any]],
    selected_event_ids: Sequence[str],
) -> list[dict[str, Any]]:
    """Events the model extracted but did not select."""

    selected = set(selected_event_ids)
    unused: list[dict[str, Any]] = []
    for event in events:
        event_id = str(event.get("event_id") or "")
        if not event_id or event_id in selected:
            continue
        unused.append(
            {
                "id": event_id,
                "label": event.get("raw_value") or event.get("kind"),
                "kind": event.get("kind"),
            }
        )
    return unused


def _resolve_cell(
    *,
    cell_id: RungId | str | None,
    cell_order: int | None,
    rung: int | None,
) -> RungId:
    if cell_id is not None:
        resolved = cell_id_from_legacy_rung(cell_id)
        if resolved is not None:
            return resolved
    if cell_order is not None:
        resolved = cell_id_from_legacy_rung(cell_order)
        if resolved is not None:
            return resolved
    if rung is not None:
        resolved = cell_id_from_legacy_rung(rung)
        if resolved is not None:
            return resolved
    raise ValueError("hop requires cell_id (or legacy rung / cell_order)")
