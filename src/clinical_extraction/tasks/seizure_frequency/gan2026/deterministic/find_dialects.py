"""Project atomic FindFact slots onto LLM extract dialects.

Protocol:
docs/research/gan2026/gan_rules_find_llm_dialects_protocol_2026-08-31.md

``gan_llm_extract`` is the codebook writer. That is the Purist-commensurate
find dialect. ``gan_llm_extract_raw`` keeps found tokens as a source-near
phrase. Atomic ``find_tag`` is diagnostic only.
"""

from __future__ import annotations

from typing import Literal

from .candidates import CandidateKind
from .find_encode import (
    NO_REFERENCE_FIND_TAG,
    FindFact,
    encode_find_fact,
    find_tag,
)

FIND_DIALECT_ATOMIC = "atomic"
FIND_DIALECT_GAN_LLM_EXTRACT = "gan_llm_extract"
FIND_DIALECT_GAN_LLM_EXTRACT_RAW = "gan_llm_extract_raw"
FindDialect = Literal[
    "atomic",
    "gan_llm_extract",
    "gan_llm_extract_raw",
]

_ADJECTIVE_RATE_UNITS = frozenset(
    {"daily", "weekly", "monthly", "yearly", "bimonthly"}
)


def render_find_fact(fact: FindFact, dialect: FindDialect) -> str:
    """Render one find payload in a named comparison dialect."""

    if dialect == FIND_DIALECT_ATOMIC:
        return find_tag(fact)
    if dialect == FIND_DIALECT_GAN_LLM_EXTRACT:
        return encode_find_fact(fact)
    if dialect == FIND_DIALECT_GAN_LLM_EXTRACT_RAW:
        return _source_near_label(fact)
    raise ValueError(f"unknown find dialect: {dialect}")


def project_find_event(
    fact: FindFact,
    dialect: FindDialect,
    *,
    evidence: str | None = None,
    event_id: str = "e1",
) -> dict[str, str | None]:
    """Slim event+selection fields matching the LLM extract schemas."""

    source_near = _source_near_label(fact)
    codebook = encode_find_fact(fact)
    raw_value = evidence or source_near
    if dialect == FIND_DIALECT_GAN_LLM_EXTRACT:
        final_label = codebook
    elif dialect == FIND_DIALECT_GAN_LLM_EXTRACT_RAW:
        final_label = source_near
    elif dialect == FIND_DIALECT_ATOMIC:
        final_label = find_tag(fact)
    else:
        raise ValueError(f"unknown find dialect: {dialect}")
    return {
        "event_id": event_id,
        "kind": str(fact.kind),
        "raw_value": raw_value,
        "final_label": final_label,
        "evidence": evidence,
    }


def _source_near_label(fact: FindFact) -> str:
    if fact.kind is CandidateKind.SEIZURE_FREE:
        return fact.custom_label or "seizure free"
    if fact.kind is CandidateKind.UNKNOWN_FREQUENCY:
        if fact.cluster_size:
            return f"unknown, {fact.cluster_size} per cluster"
        return fact.sentinel or fact.custom_label or "unknown"
    if fact.kind is CandidateKind.NO_REFERENCE:
        return fact.sentinel or NO_REFERENCE_FIND_TAG
    if fact.kind is CandidateKind.CLUSTER_FREQUENCY:
        if fact.cluster_count or fact.unit or fact.cluster_size:
            count = fact.cluster_count or "1"
            size = fact.cluster_size or "multiple"
            unit = fact.unit or "month"
            period = f"{fact.denominator} {unit}" if fact.denominator else unit
            return f"{count} cluster per {period}, {size} per cluster"
        return fact.custom_label or "cluster"
    if fact.count and fact.unit:
        unit = fact.unit
        if (
            unit.lower() in _ADJECTIVE_RATE_UNITS
            and fact.count.lower() in {"1", "one", "a", "an"}
            and not fact.denominator
        ):
            return unit.lower()
        if fact.denominator:
            return f"{fact.count} per {fact.denominator} {unit}"
        return f"{fact.count} per {unit}"
    return fact.custom_label or fact.sentinel or ""
