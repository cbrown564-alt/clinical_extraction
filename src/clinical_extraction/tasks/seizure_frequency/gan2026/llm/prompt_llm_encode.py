"""Gan later-stage encode prompt.

Rewrites every extract event into a short seizure-frequency label.
No note text. No research metadata.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_label_forms import (
    label_forms_payload,
)

GAN_LLM_ENCODE = "gan_llm_encode"
LLM_ENCODE_AUTHORED_KEYS = (
    "task",
    "instructions",
    "label_forms",
    "label_schema",
    "events",
)

TASK = "Write one short seizure-frequency label for each event."

INSTRUCTIONS = [
    "Each event has an event_id, a stated value, and a supporting quote.",
    "Leave event_id unchanged. Return one label for every event, same event_id.",
    "Every label must match one of the label forms.",
    (
        "Use the stated value. The quote is only to read that value. "
        "Do not invent a rate from unused words in the quote."
    ),
    "Do not reuse the stated value as the label unless it already matches a form.",
    "Do not add, drop, or merge events.",
    "Return one JSON object with a labels list: one event_id and label per event.",
]

LABEL_SCHEMA = {
    "event_id": "copy the given event_id",
    "label": "short seizure-frequency label",
}


def _encode_event_view(event: Mapping[str, Any]) -> dict[str, str | None]:
    raw_value = event.get("raw_value")
    return {
        "event_id": str(event["event_id"]),
        "stated_value": None if raw_value is None else str(raw_value),
        "evidence": str(event.get("evidence") or ""),
    }


def build_llm_encode_prompt_input(events: Sequence[Mapping[str, Any]]) -> str:
    """Build the later-stage encode payload from extract events."""

    payload = {
        "task": TASK,
        "instructions": list(INSTRUCTIONS),
        "label_forms": label_forms_payload(),
        "label_schema": dict(LABEL_SCHEMA),
        "events": [_encode_event_view(event) for event in events],
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)
