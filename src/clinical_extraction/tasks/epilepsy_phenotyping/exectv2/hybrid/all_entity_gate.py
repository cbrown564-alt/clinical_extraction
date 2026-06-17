"""Generalized verify / route gate for the all-entity ExECTv2 hybrid.

A faithfulness + plausibility gate that **routes** — never silently edits — the
candidate mentions it cannot resolve. It generalizes the SeizureFrequency
``verify_route`` stage to every entity (satellite 09, Phase C):

1. *Evidence presence/substring* (all entities): a mention whose ``evidence`` is
   not an exact substring of the letter cannot be source-traced and is routed.
2. *SeizureFrequency plausibility*: a SF mention must carry frequency content
   (count+period, date, change, or an explicit zero) — a bare seizure type or a
   bare nonzero count is not a frequency statement (guideline L255).
3. *Within-letter duplicate collapse* (all entities): exact duplicate candidates
   — same entity, normalized phrase, and scored attributes — are deterministic
   over-emission and the duplicate copies are routed. This trims literal repeats
   without choosing which clinical fact is real.

The gate owns ontology-neutral routing and projection only. It never introduces
a clinical fact, never rewrites a phrase, and never prunes a well-formed mention
on semantic grounds — that is the LLM's job (the candidate already came from the
LLM). Routed mentions are surfaced in a first-class taxonomy, never hidden.
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Hashable, Sequence
from dataclasses import dataclass

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    canonicalize_attribute_value,
    normalize_phrase,
)

_CUI_KEYS: frozenset[str] = frozenset({"CUI", "CUIPhrase"})

# Frequency-bearing attributes (mirrors hybrid.verify_route for SF parity).
_SF_FREQUENCY_ATTRS: frozenset[str] = frozenset({
    "NumberOfTimePeriods", "LowerNumberOfTimePeriods", "UpperNumberOfTimePeriods",
    "TimePeriod", "TimeSince_or_TimeOfEvent", "FrequencyChange", "PointInTime",
    "DayDate", "MonthDate", "YearDate", "AgeLower", "AgeUpper", "AgeUnit",
})
_SF_COUNT_ATTRS: frozenset[str] = frozenset({
    "NumberOfSeizures", "LowerNumberOfSeizures", "UpperNumberOfSeizures",
})


@dataclass(frozen=True)
class RoutedMention:
    """A candidate the gate could not keep, with its routing reason."""

    mention: PredictedMention
    reason: str


def _scored_attrs(mention: PredictedMention) -> dict[str, str]:
    return {k: v for k, v in mention.attributes.items() if k not in _CUI_KEYS}


def _sf_is_frequency_bearing(attrs: dict[str, str]) -> bool:
    if any(k in attrs for k in _SF_FREQUENCY_ATTRS):
        return True
    return attrs.get("NumberOfSeizures") == "0"


def _duplicate_key(mention: PredictedMention) -> Hashable:
    scored = tuple(
        sorted(
            (k, canonicalize_attribute_value(k, v))
            for k, v in _scored_attrs(mention).items()
        )
    )
    return (mention.entity, normalize_phrase(mention.text), scored)


def _route_reason(mention: PredictedMention, note_text: str) -> str | None:
    """Faithfulness + SF-plausibility reason for ``mention``, or None to keep."""
    if not mention.evidence:
        return "empty_evidence"
    if not evidence_is_substring(note_text, mention.evidence):
        return "evidence_not_substring"
    if mention.entity == SEIZURE_FREQUENCY.name:
        scored = _scored_attrs(mention)
        if not scored:
            return "no_frequency_attributes"
        if not _sf_is_frequency_bearing(scored):
            if set(scored) <= _SF_COUNT_ATTRS:
                return "bare_nonzero_count"
            return "no_frequency_attributes"
    return None


def gate_mentions(
    mentions: Sequence[PredictedMention],
    *,
    note_text: str,
) -> tuple[list[PredictedMention], list[RoutedMention]]:
    """Partition combined candidates into (kept, routed).

    Order is preserved for kept mentions. Duplicates are collapsed to their first
    occurrence; later copies are routed with reason ``duplicate_mention``.
    """
    kept: list[PredictedMention] = []
    routed: list[RoutedMention] = []
    seen: set[Hashable] = set()
    for mention in mentions:
        reason = _route_reason(mention, note_text)
        if reason is not None:
            routed.append(RoutedMention(mention=mention, reason=reason))
            continue
        key = _duplicate_key(mention)
        if key in seen:
            routed.append(RoutedMention(mention=mention, reason="duplicate_mention"))
            continue
        seen.add(key)
        kept.append(mention)
    return kept, routed


def routed_taxonomy(routed: Sequence[RoutedMention]) -> dict[str, int]:
    """Count routed mentions by reason — the routed-row taxonomy diagnostic."""
    return dict(Counter(r.reason for r in routed))


def routed_taxonomy_by_entity(routed: Sequence[RoutedMention]) -> dict[str, dict[str, int]]:
    """Routed counts grouped by entity then reason (over-emission attribution)."""
    by_entity: dict[str, Counter[str]] = {}
    for r in routed:
        by_entity.setdefault(r.mention.entity, Counter())[r.reason] += 1
    return {entity: dict(counter) for entity, counter in by_entity.items()}
