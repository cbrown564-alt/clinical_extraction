"""Gan later-stage select prompt.

Chooses the current burden from already labelled events.
No note text. No research metadata.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

GAN_LLM_SELECT = "gan_llm_select"
LLM_SELECT_AUTHORED_KEYS = (
    "task",
    "instructions",
    "selection_schema",
    "first_choice",
    "events",
)

_SELECT_EVENT_KEYS = (
    "event_id",
    "label",
    "kind",
    "temporality",
    "assertion_status",
    "applies_to",
    "time_window",
    "evidence",
)

TASK = "Choose which events describe the current seizure burden."

INSTRUCTIONS = [
    (
        "Each event already has a short seizure-frequency label and a "
        "supporting quote. Do not change a label that already matches "
        "one event."
    ),
    (
        "A first choice is given. Keep that first choice when it still "
        "names the highest current or recent burden."
    ),
    (
        "Change the first choice only in these four cases. Otherwise keep "
        "it."
    ),
    (
        "Usual spacing: the first choice is unknown, or a brief daily "
        "burst (for example 1 per day or multiple per day during short "
        "spells), and another event states the usual gap between seizures "
        "(for example every 2 weeks). Prefer that usual spacing."
    ),
    (
        "Usual rate versus a year total: the first choice is a count so "
        "far this year, and another event states the usual or typical "
        "rate (for example typically 1 per month). Prefer the usual rate, "
        "not the year total."
    ),
    (
        "Recent seizures after a quiet spell: the first choice is unknown "
        "or no seizure frequency reference, and the events give both a "
        "recent count and how long the person had been seizure-free. "
        "Write that count over that time (for example 2 per 6 month). "
        "Do this only when no event already has that label."
    ),
    (
        "Not epileptic seizures: the current events are attacks that are "
        "not epileptic seizures. Write no seizure frequency reference."
    ),
    (
        "Choose the highest current or recent burden across seizure types. "
        "If there is an overall current count plus a breakdown by type, "
        "choose the overall count."
    ),
    (
        "Do not choose seizure-free if other current seizure-like events "
        "remain active."
    ),
    (
        "Return selected event ids. Write a new short label only when no "
        "single event is the answer. That new label must use the same "
        "short forms as the event labels."
    ),
    "Do not add events. Do not write a new quote.",
    "Return exactly one JSON object with no markdown.",
]

SELECTION_SCHEMA = {
    "selected_event_ids": "ids of the events used for the answer",
    "label": (
        "new short seizure-frequency label, only when no single event "
        "is the answer; otherwise omit"
    ),
}


def _select_event_view(event: Mapping[str, Any]) -> dict[str, Any]:
    label = event.get("label")
    if label is None:
        label = event.get("designed_form_label")
    row: dict[str, Any] = {
        "event_id": str(event["event_id"]),
        "label": str(label) if label is not None else "",
        "kind": event.get("kind"),
        "temporality": event.get("temporality"),
        "assertion_status": event.get("assertion_status"),
        "applies_to": event.get("applies_to"),
        "time_window": event.get("time_window"),
        "evidence": str(event.get("evidence") or ""),
    }
    return {key: row[key] for key in _SELECT_EVENT_KEYS}


def build_llm_select_prompt_input(
    events: Sequence[Mapping[str, Any]],
    *,
    extract_selected_event_ids: Sequence[str],
    extract_label: str | None,
) -> str:
    """Build the later-stage select payload from labelled events."""

    payload = {
        "task": TASK,
        "instructions": list(INSTRUCTIONS),
        "selection_schema": dict(SELECTION_SCHEMA),
        "first_choice": {
            "selected_event_ids": [str(item) for item in extract_selected_event_ids],
            "label": extract_label,
        },
        "events": [_select_event_view(event) for event in events],
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)
