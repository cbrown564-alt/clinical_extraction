"""Ordered answer hops and the graph derived from them."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal

EffectClass = Literal["schema", "format", "semantic", "validation", "projection"]
HopOwner = Literal["rules", "model", "replay"]


def make_hop(
    *,
    stage_id: str,
    owner: HopOwner,
    effect_class: EffectClass,
    before: str | None,
    after: str | None,
    evidence: str | None = None,
    evidence_exact: bool | None = None,
    operands: Sequence[str] | None = None,
    vetoed: str | None = None,
    rung: int,
) -> dict[str, Any]:
    """Build one recorded answer version."""

    return {
        "stage_id": stage_id,
        "owner": owner,
        "effect_class": effect_class,
        "before": before,
        "after": after,
        "evidence": evidence,
        "evidence_exact": evidence_exact,
        "operands": list(operands or ()),
        "vetoed": vetoed,
        "rung": rung,
        "changed": before != after,
    }


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
                    "rung": hop["rung"],
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
