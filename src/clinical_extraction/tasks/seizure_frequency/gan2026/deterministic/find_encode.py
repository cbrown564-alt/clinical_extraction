"""Same-fact encode for the Gan rules-only find ledger.

Find builders emit ``FindFact`` slots. This module is the only writer of
codebook phrasing. Protocol:
docs/research/gan2026/gan_rules_only_three_stage_phase_e2_protocol_2026-08-30.md
"""

from __future__ import annotations

from dataclasses import dataclass

from .candidates import CandidateKind
from .deterministic_frequency_tokens import (
    cluster_period_label,
    cluster_size_token,
    expanded_compact_unit,
    number_token,
    period_label,
    rate_label,
)

_ADJECTIVE_RATE_UNITS: dict[str, tuple[str, str | None]] = {
    "daily": ("day", None),
    "weekly": ("week", None),
    "monthly": ("month", None),
    "yearly": ("year", None),
    "bimonthly": ("month", "2"),
}

SEIZURE_FREE_FIND_TAG = "seizure_free"
NO_REFERENCE_FIND_TAG = "no seizure frequency reference"


@dataclass(frozen=True)
class FindFact:
    """Pre-codebook find payload for one matched span."""

    kind: CandidateKind
    count: str | None = None
    unit: str | None = None
    denominator: str | None = None
    cluster_count: str | None = None
    cluster_size: str | None = None
    sentinel: str | None = None
    custom_label: str | None = None


def find_tag(fact: FindFact) -> str:
    """Provisional find representation. Not codebook phrasing."""

    if fact.kind is CandidateKind.SEIZURE_FREE:
        return SEIZURE_FREE_FIND_TAG
    if fact.kind is CandidateKind.UNKNOWN_FREQUENCY:
        return fact.sentinel or "unknown"
    if fact.kind is CandidateKind.NO_REFERENCE:
        return fact.sentinel or NO_REFERENCE_FIND_TAG
    if fact.kind is CandidateKind.CLUSTER_FREQUENCY:
        if fact.cluster_count or fact.unit or fact.cluster_size:
            count = fact.cluster_count or "1"
            size = fact.cluster_size or "multiple"
            unit = fact.unit or "month"
            period = f"{fact.denominator} {unit}" if fact.denominator else unit
            return f"cluster:{count}/{period}:{size}"
        return fact.custom_label or "cluster"
    if fact.count and fact.unit:
        if fact.denominator:
            return f"{fact.count}/{fact.denominator} {fact.unit}"
        return f"{fact.count}/{fact.unit}"
    return fact.custom_label or fact.sentinel or ""


def encode_find_fact(fact: FindFact) -> str:
    """Write the codebook label for a find payload. Same-fact only."""

    if fact.kind is CandidateKind.SEIZURE_FREE:
        return fact.custom_label or "seizure free for multiple year"
    if fact.kind is CandidateKind.UNKNOWN_FREQUENCY:
        if fact.cluster_size:
            return f"unknown, {cluster_size_token(fact.cluster_size)} per cluster"
        return fact.sentinel or fact.custom_label or "unknown"
    if fact.kind is CandidateKind.NO_REFERENCE:
        return fact.sentinel or NO_REFERENCE_FIND_TAG
    if fact.kind is CandidateKind.CLUSTER_FREQUENCY:
        if fact.custom_label:
            return fact.custom_label
        return _cluster_codebook_label(fact)
    if fact.custom_label:
        return fact.custom_label
    if fact.count and fact.unit:
        unit, denominator = _encode_rate_unit(fact.unit, fact.denominator)
        return rate_label(fact.count, unit, denominator)
    return fact.sentinel or "unknown"


def _cluster_codebook_label(fact: FindFact) -> str:
    count = fact.cluster_count or "1"
    if count not in {"multiple", "unknown"}:
        count = number_token(count)
    unit = fact.unit or "month"
    try:
        unit = expanded_compact_unit(unit)
    except KeyError:
        pass
    if fact.denominator:
        period = period_label(unit, fact.denominator)
    else:
        period = cluster_period_label(unit)
    size = cluster_size_token(fact.cluster_size)
    return f"{count} cluster per {period}, {size} per cluster"


def _encode_rate_unit(unit: str, denominator: str | None) -> tuple[str, str | None]:
    lowered = unit.lower()
    if lowered in _ADJECTIVE_RATE_UNITS:
        mapped_unit, mapped_denominator = _ADJECTIVE_RATE_UNITS[lowered]
        return mapped_unit, denominator or mapped_denominator
    try:
        return expanded_compact_unit(lowered), denominator
    except KeyError:
        return unit, denominator
