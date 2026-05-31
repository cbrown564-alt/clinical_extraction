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
    "extracted": "frequency",
    "extracted frequency": "frequency",
    "seizure frequency": "frequency",
    "seizure_frequency": "frequency",
    "patient report": "frequency",
    "patient self-report": "frequency",
    "current frequency": "frequency",
    "current seizure frequency": "frequency",
    "seizure-free": "seizure_free",
    "no reference": "no_reference",
    "no seizure frequency reference": "no_reference",
    "multiple": "unresolved_multiple",
}
