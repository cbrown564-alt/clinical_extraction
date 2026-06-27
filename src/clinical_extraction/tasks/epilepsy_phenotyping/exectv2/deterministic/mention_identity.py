"""Mention span and identity helpers for deterministic ExECTv2 extraction."""
from __future__ import annotations

import re
from collections.abc import Iterable

from clinical_extraction.core.schemas import EvidenceSpan
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.evaluation import (
    preserves_distinct_occurrences,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase
def match_span(match: re.Match[str]) -> EvidenceSpan:
    """Return the exact source slice that triggered a mention."""

    return EvidenceSpan(text=match.group(0), start_char=match.start(), end_char=match.end())


def dedupe_mentions(mentions: Iterable[PredictedMention]) -> tuple[PredictedMention, ...]:
    """Collapse duplicate mentions using the entity-specific occurrence policy."""

    seen: set[tuple[str, str, tuple[tuple[str, str], ...], int | None]] = set()
    deduped: list[PredictedMention] = []
    for mention in mentions:
        key = _mention_identity_key(mention)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(mention)
    return tuple(deduped)


def _mention_identity_key(
    mention: PredictedMention,
) -> tuple[str, str, tuple[tuple[str, str], ...], int | None]:
    span = mention.evidence_span
    start_char = (
        span.start_char
        if span is not None and preserves_distinct_occurrences(mention.entity)
        else None
    )
    return (
        mention.entity,
        normalize_phrase(mention.text),
        tuple(sorted(dict(mention.attributes).items())),
        start_char,
    )
