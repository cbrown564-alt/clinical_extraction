from __future__ import annotations

import re
from collections.abc import Sequence

from clinical_extraction.tasks.seizure_frequency.gan2026.candidates import (
    CandidateKind,
    RawCandidate,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.temporal import MONTH_NAME_PATTERN


def dedupe_candidates(candidates: Sequence[RawCandidate]) -> list[RawCandidate]:
    seen: set[tuple[CandidateKind, str | None, str]] = set()
    deduped: list[RawCandidate] = []
    for candidate in candidates:
        key = (candidate.kind, candidate.label, candidate.evidence)
        if key not in seen:
            seen.add(key)
            deduped.append(candidate)
    return deduped


def prune_contained_frequency_fragments(
    candidates: Sequence[RawCandidate], text: str
) -> list[RawCandidate]:
    has_current_frequency_candidate = any(
        candidate.kind in {CandidateKind.FREQUENCY_RATE, CandidateKind.CLUSTER_FREQUENCY}
        and not is_historical_candidate(candidate, text)
        for candidate in candidates
    )
    pruned: list[RawCandidate] = []
    for candidate in candidates:
        if candidate.kind is CandidateKind.FREQUENCY_RATE and any(
            _is_contained_monthly_list_fragment(candidate, other) for other in candidates
        ):
            continue
        if (
            has_current_frequency_candidate
            and candidate.kind in {CandidateKind.FREQUENCY_RATE, CandidateKind.CLUSTER_FREQUENCY}
            and is_historical_candidate(candidate, text)
        ):
            continue
        pruned.append(candidate)
    return pruned


def has_historical_lead_in(text: str, start: int) -> bool:
    preceding = text[max(0, start - 140) : start].lower()
    historical_markers = (
        "by way of comparison",
        "compared with earlier",
        "compared with the earlier",
        "earlier pattern",
        "prior to this",
        "prior to these",
        "prior to recent",
        "prior pattern",
        "historical description",
        "before improvement",
        "previously",
        "historically",
    )
    current_markers = (
        "over the past",
        "over the last",
        "current",
        "now",
        "however",
        "at present",
        "has reduced",
        "have reduced",
        "stabilised at",
        "stabilized at",
    )
    latest_historical = max((preceding.rfind(marker) for marker in historical_markers), default=-1)
    if latest_historical == -1:
        return False
    latest_current = max((preceding.rfind(marker) for marker in current_markers), default=-1)
    return latest_current < latest_historical


def is_historical_candidate(candidate: RawCandidate, text: str) -> bool:
    match = re.search(r"\s+".join(re.escape(part) for part in candidate.evidence.split()), text)
    if match is None:
        return False
    return has_historical_lead_in(text, match.start())


def _is_contained_monthly_list_fragment(candidate: RawCandidate, other: RawCandidate) -> bool:
    if other is candidate or other.kind is not CandidateKind.FREQUENCY_RATE:
        return False
    candidate_evidence = candidate.evidence.lower()
    other_evidence = other.evidence.lower()
    if candidate_evidence == other_evidence or candidate_evidence not in other_evidence:
        return False
    if len(other_evidence) < len(candidate_evidence) + 20:
        return False
    month_mentions = re.findall(rf"\b(?:{MONTH_NAME_PATTERN})\b", other.evidence, re.IGNORECASE)
    if len(month_mentions) < 2:
        return False
    return any(
        marker in other_evidence
        for marker in (
            "this month",
            "as of this month",
            "has recorded",
            "cluster of",
            "run of",
        )
    )
