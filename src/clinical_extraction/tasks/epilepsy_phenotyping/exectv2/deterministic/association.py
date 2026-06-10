"""Associate attribute extractions with their nearest anchor phrase.

Each ``AttributeExtraction`` (a frequency / seizure-free / change expression)
is assigned to whichever ``AnchorCandidate`` (seizure-type / event phrase) is
closest to it in the letter text. Anchors that end up with no associated
attribute extraction are dropped — in the gold annotation scheme every
SeizureFrequency mention carries frequency-related attributes, so a bare
seizure-type mention with no nearby frequency information is not a
SeizureFrequency mention (it is more likely a Diagnosis mention).
"""
from __future__ import annotations

import re
from collections import defaultdict

from .candidates import AnchorCandidate, AttributeExtraction

_SENTENCE_BREAK = re.compile(r"[.!?\n]+")

# An attribute extraction binds to an anchor only when they plausibly belong to
# the same frequency statement: the same sentence, within this many characters.
# Without this bound, a rate expression on a non-seizure noun ("migraine
# episodes once a month", "4 to 5 episodes a month") glued onto a seizure-type
# anchor elsewhere in the letter — the single largest cross-context FP source.
_MAX_ASSOCIATION_GAP = 80


def _gap(a: tuple[int, int], b: tuple[int, int]) -> int:
    """Character distance between two spans (0 if they overlap or touch)."""
    if a[1] <= b[0]:
        return b[0] - a[1]
    if b[1] <= a[0]:
        return a[0] - b[1]
    return 0


def _sentence_breaks(text: str) -> list[int]:
    """Character offsets of sentence-ending punctuation in ``text``."""
    return [m.start() for m in _SENTENCE_BREAK.finditer(text)]


def _sentence_index(pos: int, breaks: list[int]) -> int:
    """How many sentence breaks occur strictly before ``pos``."""
    count = 0
    for b in breaks:
        if b < pos:
            count += 1
        else:
            break
    return count


def associate_attributes_to_anchors(
    anchors: list[AnchorCandidate],
    attributes: list[AttributeExtraction],
    text: str = "",
) -> list[tuple[AnchorCandidate, dict[str, str]]]:
    """Pair each anchor with the merged attributes of its nearest extractions.

    An attribute extraction binds to the nearest anchor that (a) shares its
    sentence and (b) is within ``_MAX_ASSOCIATION_GAP`` characters. An extraction
    with no anchor satisfying both is dropped rather than forced onto a distant
    anchor — a frequency expression on a non-seizure noun must not borrow a
    seizure anchor from elsewhere in the letter. Returns one
    ``(anchor, merged_attributes)`` pair per anchor that gathered at least one
    extraction, in document order.
    """
    if not anchors:
        return []

    breaks = _sentence_breaks(text)
    anchor_sentences = [_sentence_index(a.span[0], breaks) for a in anchors]

    groups: dict[int, list[AttributeExtraction]] = defaultdict(list)
    for attr in attributes:
        attr_sentence = _sentence_index(attr.span[0], breaks)
        same_sentence = [i for i, s in enumerate(anchor_sentences) if s == attr_sentence]
        if not same_sentence:
            continue
        nearest_idx = min(
            same_sentence,
            key=lambda i: (_gap(anchors[i].span, attr.span), abs(anchors[i].span[0] - attr.span[0])),
        )
        if _gap(anchors[nearest_idx].span, attr.span) > _MAX_ASSOCIATION_GAP:
            continue
        groups[nearest_idx].append(attr)

    results: list[tuple[AnchorCandidate, dict[str, str]]] = []
    for i, anchor in enumerate(anchors):
        attrs = groups.get(i)
        if not attrs:
            continue
        # Per-statement emission (D8): splitting a co-located numeric statement
        # from a FrequencyChange into two mentions was implemented and measured
        # net-negative on dev (per-item F1 0.272→0.264, per-letter 0.482→0.471) —
        # the ~11-mention upside is outweighed by split-induced false positives
        # (lone change mentions that gold had merged, or whose direction is
        # wrong). Kept as a single merged statement; see the SF error-analysis
        # artifact for the measurement.
        merged: dict[str, str] = {}
        for attr in attrs:
            for key, value in attr.attributes.items():
                merged.setdefault(key, value)
        results.append((anchor, merged))
    return results
