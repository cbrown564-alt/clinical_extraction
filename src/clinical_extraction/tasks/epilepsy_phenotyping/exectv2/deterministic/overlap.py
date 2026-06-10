"""Overlap resolution for ExECTv2 anchors and attribute extractions.

Both ``AnchorCandidate`` and ``AttributeExtraction`` carry a ``span``
(character offsets), so resolution is a simple span-conflict pass — no text
re-search is needed.

Anchors: prefer longer (more specific) spans, e.g. "focal seizures with loss
of awareness" over the bare "seizures" inside it.

Attribute extractions: prefer the candidate with more attributes (more
specific match), e.g. a range rule over a bare count rule on the same span.

Key difference from Gan 2026: ExECTv2 is mention extraction — we want ALL
non-overlapping anchors/extractions, not just one dominant fact per letter.
So this stage only removes span-level conflicts, not all but the best.
"""
from __future__ import annotations

from .candidates import AnchorCandidate, AttributeExtraction


def _overlaps(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return a[0] < b[1] and b[0] < a[1]


def resolve_overlapping_anchors(anchors: list[AnchorCandidate]) -> list[AnchorCandidate]:
    """Keep the longest non-conflicting anchor span at each position."""
    ordered = sorted(
        anchors,
        key=lambda a: (-(a.span[1] - a.span[0]), a.span[0], a.rule_id),
    )
    accepted: list[AnchorCandidate] = []
    for a in ordered:
        if not any(_overlaps(a.span, b.span) for b in accepted):
            accepted.append(a)
    accepted.sort(key=lambda a: a.span[0])
    return accepted


def resolve_overlapping_attributes(
    extractions: list[AttributeExtraction],
) -> list[AttributeExtraction]:
    """Keep the most specific (most attributes) non-conflicting extraction per span."""
    ordered = sorted(
        extractions,
        key=lambda e: (-len(e.attributes), -(e.span[1] - e.span[0]), e.rule_id),
    )
    accepted: list[AttributeExtraction] = []
    for e in ordered:
        if not any(_overlaps(e.span, a.span) for a in accepted):
            accepted.append(e)
    accepted.sort(key=lambda e: e.span[0])
    return accepted
