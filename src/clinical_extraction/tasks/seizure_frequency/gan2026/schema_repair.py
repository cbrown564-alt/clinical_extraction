"""Shared schema repair for Gan 2026 prediction records."""

from __future__ import annotations

from typing import Any


def repair_decision_payload(payload: Any) -> Any:
    """Repair common model schema aliases without changing clinical content."""

    if not isinstance(payload, dict):
        return payload

    repaired = dict(payload)
    _repair_string_alias(repaired, "assertion_status", _ASSERTION_ALIASES)
    _repair_string_alias(repaired, "uncertainty", _UNCERTAINTY_ALIASES)
    _repair_string_alias(repaired, "answer_kind", _ANSWER_KIND_ALIASES)
    _repair_numeric_confidence(repaired)

    normalized_rate = repaired.get("normalized_rate")
    if normalized_rate is not None and not isinstance(normalized_rate, str):
        repaired["normalized_rate"] = str(normalized_rate)
    return repaired


def _repair_string_alias(payload: dict[str, Any], key: str, aliases: dict[str, str]) -> None:
    value = payload.get(key)
    if isinstance(value, str):
        payload[key] = aliases.get(value.strip().lower(), value)


def _repair_numeric_confidence(payload: dict[str, Any]) -> None:
    confidence = payload.get("confidence")
    if not isinstance(confidence, int | float):
        return
    if confidence >= 0.8:
        payload["confidence"] = "high"
    elif confidence >= 0.45:
        payload["confidence"] = "medium"
    else:
        payload["confidence"] = "low"


_ASSERTION_ALIASES = {
    "present": "asserted",
    "positive": "asserted",
    "current": "asserted",
    "certain": "asserted",
}

_UNCERTAINTY_ALIASES = {
    "none": "low",
    "certain": "low",
    "clear": "low",
    "unclear": "high",
}

_ANSWER_KIND_ALIASES = {
    "count": "frequency",
    "count and cluster": "frequency",
    "count and time interval": "frequency",
    "count and time window": "frequency",
    "count and window": "frequency",
    "count over interval": "frequency",
    "count over time window": "frequency",
    "count per time": "frequency",
    "count per time window": "frequency",
    "count per year": "frequency",
    "count-based": "frequency",
    "count-conditioned frequency": "frequency",
    "current frequency": "frequency",
    "current seizure frequency": "frequency",
    "direct": "frequency",
    "direct report": "frequency",
    "direct statement": "frequency",
    "direct_extraction": "frequency",
    "electrographic seizure frequency": "frequency",
    "extracted": "frequency",
    "extracted frequency": "frequency",
    "frequency change": "frequency",
    "multiple": "unresolved_multiple",
    "no reference": "no_reference",
    "no seizure frequency reference": "no_reference",
    "seizure frequency": "frequency",
    "seizure_frequency": "frequency",
    "patient report": "frequency",
    "patient report and peer observation": "frequency",
    "patient self-report": "frequency",
    "patient-reported count": "frequency",
    "seizure-free": "seizure_free",
}
