"""Shared schema repair for Gan 2026 prediction records."""

from __future__ import annotations

import ast
import json
from typing import Any


def parse_json_payload_with_schema_repair(raw_payload: str) -> tuple[Any, list[str]]:
    """Parse model JSON, allowing explicit non-semantic JSON dialect repair.

    Some local models emit Python literal syntax for otherwise valid structured
    objects, for example single-quoted keys and `None`. Treating that as a
    schema repair keeps the clinical payload unchanged while making its impact
    visible in run artifacts.
    """

    try:
        return json.loads(raw_payload), []
    except json.JSONDecodeError as json_error:
        try:
            return ast.literal_eval(raw_payload), ["json_dialect_repaired: python_literal"]
        except (SyntaxError, ValueError):
            raise json_error from None


def repair_decision_payload(payload: Any) -> Any:
    """Repair common model schema aliases without changing clinical content."""

    if not isinstance(payload, dict):
        return payload

    repaired = dict(payload)
    _repair_string_alias(repaired, "kind", _EVENT_KIND_ALIASES)
    _repair_string_alias(repaired, "final_kind", _ANSWER_KIND_ALIASES)
    _repair_string_alias(repaired, "assertion_status", _ASSERTION_ALIASES)
    _repair_string_alias(repaired, "uncertainty", _UNCERTAINTY_ALIASES)
    _repair_string_alias(repaired, "certainty", _CERTAINTY_ALIASES)
    _repair_string_alias(repaired, "temporality", _TEMPORALITY_ALIASES)
    _repair_string_alias(repaired, "answer_kind", _ANSWER_KIND_ALIASES)
    _repair_numeric_confidence(repaired)

    normalized_rate = repaired.get("normalized_rate")
    if normalized_rate is not None and not isinstance(normalized_rate, str):
        repaired["normalized_rate"] = str(normalized_rate)
    return repaired


def repair_structured_extraction_payload(payload: Any) -> Any:
    """Repair schema aliases in a structured extraction payload.

    This intentionally repairs only output-shape aliases such as enum names and
    numeric confidence. It does not repair Gan benchmark labels; that remains in
    normalize.py so deterministic and LLM pipelines share the same label policy.
    """

    if not isinstance(payload, dict):
        return payload

    repaired = dict(payload)
    events = repaired.get("events")
    if isinstance(events, list):
        repaired["events"] = [repair_decision_payload(event) for event in events]
    selection = repaired.get("selection")
    if isinstance(selection, dict):
        repaired_selection = repair_decision_payload(selection)
        repaired_selection.setdefault("confidence", "medium")
        repaired["selection"] = repaired_selection
    return repaired


def _repair_string_alias(payload: dict[str, Any], key: str, aliases: dict[str, str]) -> None:
    value = payload.get(key)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if key == "temporality" and normalized.startswith("since "):
            payload[key] = "recent"
        else:
            payload[key] = aliases.get(normalized, value)


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
    "negative": "negated",
    "unknown": "unclear",
}

_UNCERTAINTY_ALIASES = {
    "none": "low",
    "certain": "low",
    "clear": "low",
    "unclear": "high",
    "uncertain": "high",
}

_CERTAINTY_ALIASES = {
    "clear": "certain",
    "low": "certain",
    "medium": "approximate",
    "high": "uncertain",
    "unclear": "unknown",
}

_TEMPORALITY_ALIASES = {
    "active": "current",
    "current/recent": "recent",
    "current to recent": "recent",
    "ongoing": "current",
    "past": "historical",
    "remote": "historical",
}

_EVENT_KIND_ALIASES = {
    "current frequency": "frequency_rate",
    "direct frequency": "frequency_rate",
    "frequency": "frequency_rate",
    "frequency statement": "frequency_rate",
    "historical": "last_event_only",
    "historical event": "last_event_only",
    "rate": "frequency_rate",
    "cluster": "cluster_frequency",
    "clusters": "cluster_frequency",
    "cluster rate": "cluster_frequency",
    "seizure-free": "seizure_free",
    "seizure free": "seizure_free",
    "last event": "last_event_only",
    "last seizure": "last_event_only",
    "unknown": "unknown_frequency",
    "unknown frequency": "unknown_frequency",
    "no reference": "no_reference",
    "no seizure frequency reference": "no_reference",
}

_ANSWER_KIND_ALIASES = {
    "count": "frequency",
    "count and cluster": "frequency",
    "cluster": "frequency",
    "cluster frequency": "frequency",
    "cluster_frequency": "frequency",
    "cluster rate": "frequency",
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
    "last event": "frequency",
    "last-event-only": "frequency",
    "last_event_only": "frequency",
    "last seizure": "frequency",
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
