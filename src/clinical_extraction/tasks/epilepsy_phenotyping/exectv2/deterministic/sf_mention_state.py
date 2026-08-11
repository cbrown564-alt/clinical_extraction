"""Shared SeizureFrequency mention-state classification for the SF replay lanes."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def mention_seizure_state(mention: Mapping[str, Any]) -> str:
    attrs = dict(mention.get("attributes") or {})
    values = [
        attrs.get("NumberOfSeizures"),
        attrs.get("LowerNumberOfSeizures"),
        attrs.get("UpperNumberOfSeizures"),
    ]
    if any(value == "0" for value in values if value is not None):
        return "seizure-free"
    if any(value for value in values):
        return "active-rate"
    return "unknown"
