"""Gan later-stage encode prompt.

Rewrites every extract event into a short seizure-frequency label.
No note text. No research metadata.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

GAN_LLM_ENCODE = "gan_llm_encode"
LLM_ENCODE_AUTHORED_KEYS = (
    "task",
    "instructions",
    "label_schema",
    "events",
)

TASK = "Write one short seizure-frequency label for each event."

INSTRUCTIONS = [
    "Each event has an event_id, a stated value, and a supporting quote.",
    "Leave event_id unchanged. Return one label for every event, same event_id.",
    (
        "Write the label in this short form: a count and time unit "
        "(1 per day), a range (2 to 3 per month), a cluster pair "
        "(1 cluster per 4 month, 5 per cluster), a seizure-free duration "
        "(seizure free for 6 month), unknown, or no seizure frequency "
        "reference."
    ),
    (
        "Use digits, not word numbers. Flatten an upper or lower bound: "
        "at most four per day, or ≤ four per day, becomes 4 per day."
    ),
    (
        "Use the stated value. The quote is only to read that value. "
        "Do not invent a rate from unused words in the quote."
    ),
    (
        "If the stated value is not one of those shapes, write unknown "
        "when seizures are discussed, or no seizure frequency reference "
        "when there is no usable frequency evidence. Do not reuse the "
        "stated value as the label."
    ),
    "Do not add, drop, or merge events.",
    "Return exactly one JSON object with no markdown.",
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
        "label_schema": dict(LABEL_SCHEMA),
        "events": [_encode_event_view(event) for event in events],
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)
