"""Shared schema repair for Gan 2026 prediction records."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from clinical_extraction.core.json_schema_repair import (
    parse_json_payload_with_schema_repair,
)

__all__ = [
    "parse_json_payload_with_schema_repair",
    "repair_decision_payload",
    "repair_selected_answer_payload",
    "repair_structured_extraction_payload",
]


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
    _repair_string_alias(repaired, "confidence", _CONFIDENCE_ALIASES)
    _repair_numeric_confidence(repaired)

    normalized_rate = repaired.get("normalized_rate")
    if normalized_rate is not None and not isinstance(normalized_rate, str):
        repaired["normalized_rate"] = str(normalized_rate)
    return repaired


def repair_structured_extraction_payload(payload: Any) -> Any:
    """Repair schema aliases in a structured extraction payload.

    This repairs output-shape aliases such as enum names and numeric
    confidence, and fills an omitted required event ``kind`` from sibling
    events or the already-written selection. It does not repair Gan
    benchmark labels; that remains in normalize.py so deterministic and
    LLM pipelines share the same label policy.
    """

    if not isinstance(payload, dict):
        return payload

    repaired = dict(payload)
    events = repaired.get("events")
    if isinstance(events, list):
        repaired_events: list[Any] = []
        has_any_event_id = any(
            isinstance(event, dict) and (event.get("event_id") or event.get("pevent_id"))
            for event in events
        )
        used_event_ids = {
            str(event.get("event_id"))
            for event in events
            if isinstance(event, dict) and event.get("event_id")
        }
        for index, event in enumerate(events):
            repaired_event = repair_decision_payload(event)
            if isinstance(repaired_event, dict):
                _move_key_alias(repaired_event, "pevent_id", "event_id")
                _move_key_alias(repaired_event, "temporlagity", "temporality")
                if has_any_event_id and not repaired_event.get("event_id"):
                    repaired_event["event_id"] = _next_event_id(index, used_event_ids)
                if repaired_event.get("event_id"):
                    used_event_ids.add(str(repaired_event["event_id"]))
                if repaired_event.get("kind") == "no_reference" and repaired_event.get(
                    "evidence"
                ) is None:
                    repaired_event["evidence"] = ""
            repaired_events.append(repaired_event)
        repaired["events"] = repaired_events
    selection = repaired.get("selection")
    if isinstance(selection, dict):
        repaired_selection = repair_decision_payload(selection)
        _move_key_alias(repaired_selection, "rationality", "rationale")
        repaired_selection.setdefault("confidence", "medium")
        repaired["selection"] = repaired_selection
    _fill_omitted_event_kinds(repaired)
    return repaired


def repair_selected_answer_payload(
    payload: Any,
    *,
    event_validator: Callable[[Any], Any] | None = None,
) -> tuple[Any, list[str], list[str]]:
    """Apply selected-answer-preserving structural repair.

    Mapping-to-list conversion and an empty evidence string for an explicit
    ``no_reference`` selection preserve model values. Invalid events may be
    quarantined only when a caller supplies the canonical event validator and
    the event is not selected. Selected events are never removed.
    """

    if not isinstance(payload, dict):
        return payload, [], []

    repaired = dict(payload)
    notes: list[str] = []
    quarantined: list[str] = []
    events = repaired.get("events")
    if isinstance(events, dict) and all(isinstance(event, dict) for event in events.values()):
        repaired["events"] = list(events.values())
        events = repaired["events"]
        notes.append("container_shape_repaired: events_mapping_to_list")

    selection = repaired.get("selection")
    if isinstance(selection, dict):
        repaired_selection = dict(selection)
        if (
            repaired_selection.get("final_kind") == "no_reference"
            and repaired_selection.get("evidence") is None
        ):
            repaired_selection["evidence"] = ""
            notes.append("container_shape_repaired: no_reference_null_evidence")
        repaired["selection"] = repaired_selection
        selection = repaired_selection
    elif selection is not None:
        # A non-mapping selection (a bare string or list) carries no usable
        # selected ids. Treat it as absent for id extraction, leaving the
        # payload itself untouched for downstream consumers.
        notes.append("container_shape_repaired: selection_not_mapping")
        selection = None

    if not isinstance(events, list) or event_validator is None:
        return repaired, notes, quarantined

    raw_selected_ids = (selection or {}).get("selected_event_ids", [])
    if not isinstance(raw_selected_ids, (list, tuple, set)):
        # A bare string here would otherwise iterate character by character.
        notes.append("container_shape_repaired: selected_event_ids_not_sequence")
        raw_selected_ids = []
    selected_ids = {str(value) for value in raw_selected_ids if value is not None}
    retained: list[Any] = []
    for event in events:
        event_id = str(event.get("event_id", "")) if isinstance(event, dict) else ""
        try:
            event_validator(event)
        except (TypeError, ValueError):
            if event_id and event_id not in selected_ids:
                quarantined.append(event_id)
                notes.append(f"unselected_event_quarantined: {event_id}")
                continue
        retained.append(event)
    repaired["events"] = retained
    return repaired, notes, quarantined


_VALID_EVENT_KINDS = frozenset(
    {
        "frequency_rate",
        "cluster_frequency",
        "seizure_free",
        "last_event_only",
        "unknown_frequency",
        "no_reference",
    }
)
_FINAL_KIND_TO_EVENT_KIND = {
    "seizure_free": "seizure_free",
    "unknown": "unknown_frequency",
    "no_reference": "no_reference",
}


def _event_kind_omitted(event: dict[str, Any]) -> bool:
    kind = event.get("kind")
    return kind is None or (isinstance(kind, str) and not kind.strip())


def _same_written_value(left: Any, right: Any) -> bool:
    if not isinstance(left, str) or not isinstance(right, str):
        return False
    left_text = left.strip()
    right_text = right.strip()
    return bool(left_text) and left_text == right_text


def _omitted_event_kind_from_siblings(
    event: dict[str, Any],
    events: list[dict[str, Any]],
) -> str | None:
    raw_value = event.get("raw_value")
    evidence = event.get("evidence")
    sibling_kinds: set[str] = set()
    for other in events:
        if other is event or _event_kind_omitted(other):
            continue
        other_kind = other.get("kind")
        if other_kind not in _VALID_EVENT_KINDS:
            continue
        has_raw = isinstance(raw_value, str) and bool(raw_value.strip())
        matched = (
            _same_written_value(raw_value, other.get("raw_value"))
            if has_raw
            else _same_written_value(evidence, other.get("evidence"))
        )
        if matched:
            sibling_kinds.add(str(other_kind))
    if len(sibling_kinds) == 1:
        return sibling_kinds.pop()
    return None


def _omitted_event_kind_from_selection(
    event: dict[str, Any],
    final_kind: str | None,
) -> str | None:
    if final_kind is None:
        return None
    mapped = _FINAL_KIND_TO_EVENT_KIND.get(final_kind)
    if mapped is not None:
        return mapped
    if final_kind != "frequency":
        return None
    written = event.get("raw_value")
    if not isinstance(written, str) or not written.strip():
        written = event.get("evidence")
    if not isinstance(written, str) or not written.strip():
        return None
    if "cluster" in written.lower():
        return "cluster_frequency"
    return "frequency_rate"


def _fill_omitted_event_kinds(payload: dict[str, Any]) -> None:
    events = payload.get("events")
    if not isinstance(events, list):
        return
    dict_events = [event for event in events if isinstance(event, dict)]
    selection = payload.get("selection")
    final_kind = None
    if isinstance(selection, dict) and isinstance(selection.get("final_kind"), str):
        final_kind = selection["final_kind"]
    for event in dict_events:
        if not _event_kind_omitted(event):
            continue
        filled = _omitted_event_kind_from_siblings(event, dict_events)
        if filled is None:
            filled = _omitted_event_kind_from_selection(event, final_kind)
        if filled is not None:
            event["kind"] = filled


def _move_key_alias(payload: dict[str, Any], alias: str, canonical: str) -> None:
    if canonical not in payload and alias in payload:
        payload[canonical] = payload[alias]
    payload.pop(alias, None)


def _next_event_id(index: int, used: set[str]) -> str:
    candidate_number = index + 1
    while f"e{candidate_number}" in used:
        candidate_number += 1
    return f"e{candidate_number}"


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
    if isinstance(confidence, str):
        try:
            confidence = float(confidence)
        except ValueError:
            return
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

_CONFIDENCE_ALIASES = {
    "very high": "high",
    "high confidence": "high",
    "confident": "high",
    "moderate": "medium",
    "moderate confidence": "medium",
    "uncertain": "low",
}

_TEMPORALITY_ALIASES = {
    "active": "current",
    "current/recent": "recent",
    "current to recent": "recent",
    "historical/current": "current",
    "hypothetical": "future",
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
    "count-and-window": "frequency",
    "count-based": "frequency",
    "count-conditioned frequency": "frequency",
    "current frequency": "frequency",
    "current seizure frequency": "frequency",
    "direct": "frequency",
    "direct frequency statement": "frequency",
    "direct patient report": "frequency",
    "direct report": "frequency",
    "direct statement": "frequency",
    "direct_extraction": "frequency",
    "direct_normalized": "frequency",
    "direct_report": "frequency",
    "electrographic seizure frequency": "frequency",
    "explicit frequency": "frequency",
    "explicit frequency statement": "frequency",
    "explicit_frequency": "frequency",
    "explicit_frequency_normalized": "frequency",
    "explicit_frequency_phrase": "frequency",
    "extracted": "frequency",
    "extracted frequency": "frequency",
    "frequency_count": "frequency",
    "frequency change": "frequency",
    "frequency pattern with trigger": "frequency",
    "frequency described but not quantifiable": "unknown",
    "imprecise frequency": "unknown",
    "last event": "frequency",
    "last-event-only": "frequency",
    "last_event_only": "frequency",
    "last seizure": "frequency",
    "multiple": "unresolved_multiple",
    "nonnumeric": "unknown",
    "no reference": "no_reference",
    "no seizure frequency reference": "no_reference",
    "normalized_frequency_unknown": "unknown",
    "seizure frequency": "frequency",
    "seizure_frequency": "frequency",
    "patient report": "frequency",
    "patient report and peer observation": "frequency",
    "patient and observer report": "frequency",
    "patient and witness report": "frequency",
    "patient/caregiver reported": "frequency",
    "patient self-report": "frequency",
    "patient-reported count": "frequency",
    "provoked-only": "unknown",
    "quoted normalized": "frequency",
    "seizure-free": "seizure_free",
    "seizure-free duration": "seizure_free",
    "duration_seizure_free": "seizure_free",
    "temporal numeric extraction": "frequency",
    "verbatim": "frequency",
    "verbatim and paraphrased extraction": "frequency",
    "verbatim/complex": "unresolved_multiple",
    "verbatim_count_and_window": "frequency",
}
