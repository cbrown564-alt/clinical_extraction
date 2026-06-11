"""Verify / route stage for the hybrid SeizureFrequency extractor.

A lightweight gate (satellite 04 §4). It checks two things and **routes** —
never silently fixes — the mentions it cannot resolve:

1. *Evidence presence/substring*: a mention whose ``evidence`` is not an exact
   substring of the letter is routed (it cannot be source-traced).
2. *Clinical plausibility*: a SeizureFrequency mention must carry frequency
   information. A bare nonzero count with no time frame ("4 seizures", no
   period/date/change) is not a frequency statement (guideline L255); an
   attribute-less mention has no frequency content at all. Both are routed.

Routed mentions are excluded from the scored set and recorded in a first-class
routed-row taxonomy (satellite 07) — they are a diagnostic, not a hidden drop.
No verifier-written labels: the stage only keeps or routes, it never edits a
mention's clinical fact.
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedMention,
)

# Attributes that carry genuine frequency content. A mention is frequency-bearing
# if it has at least one of these (or an explicit zero count — a valid
# seizure-free statement, guideline L53).
_FREQUENCY_ATTRS: frozenset[str] = frozenset({
    "NumberOfTimePeriods", "LowerNumberOfTimePeriods", "UpperNumberOfTimePeriods",
    "TimePeriod", "TimeSince_or_TimeOfEvent", "FrequencyChange", "PointInTime",
    "DayDate", "MonthDate", "YearDate", "AgeLower", "AgeUpper", "AgeUnit",
})
_COUNT_ATTRS: frozenset[str] = frozenset({
    "NumberOfSeizures", "LowerNumberOfSeizures", "UpperNumberOfSeizures",
})


@dataclass(frozen=True)
class RoutedMention:
    """A mention the verify stage could not resolve, with its routing reason."""

    mention: PredictedMention
    reason: str


def _is_frequency_bearing(attrs: dict[str, str]) -> bool:
    if any(k in attrs for k in _FREQUENCY_ATTRS):
        return True
    # A bare explicit-zero count is a valid seizure-free statement.
    if attrs.get("NumberOfSeizures") == "0":
        return True
    return False


def _route_reason(mention: PredictedMention, note_text: str) -> str | None:
    """Return the routing reason for ``mention``, or None if it passes."""
    if not mention.evidence:
        return "empty_evidence"
    if not evidence_is_substring(note_text, mention.evidence):
        return "evidence_not_substring"
    attrs = dict(mention.attributes)
    scored = {k: v for k, v in attrs.items() if k not in ("CUI", "CUIPhrase")}
    if not scored:
        return "no_frequency_attributes"
    if not _is_frequency_bearing(scored):
        # Has only count attrs and none is an explicit zero -> bare count.
        if set(scored) <= _COUNT_ATTRS:
            return "bare_nonzero_count"
        return "no_frequency_attributes"
    return None


def verify_and_route(
    mentions: Sequence[PredictedMention],
    *,
    note_text: str,
) -> tuple[list[PredictedMention], list[RoutedMention]]:
    """Partition mentions into (kept, routed).

    ``kept`` are evidence-traceable, clinically-plausible SeizureFrequency
    mentions ready to score. ``routed`` carry a reason from the taxonomy and are
    excluded from scoring (never silently kept, never silently fixed).
    """
    kept: list[PredictedMention] = []
    routed: list[RoutedMention] = []
    for mention in mentions:
        reason = _route_reason(mention, note_text)
        if reason is None:
            kept.append(mention)
        else:
            routed.append(RoutedMention(mention=mention, reason=reason))
    return kept, routed


def routed_taxonomy(routed: Sequence[RoutedMention]) -> dict[str, int]:
    """Count routed mentions by reason — the routed-row taxonomy diagnostic."""
    return dict(Counter(r.reason for r in routed))
