"""Drop an active-rate SF mention that is only a lifetime one-off count."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.seizure_frequency import (
    _frequency_state,
)

PERIOD_KEYS = (
    "TimePeriod",
    "NumberOfTimePeriods",
    "LowerNumberOfTimePeriods",
    "UpperNumberOfTimePeriods",
)
LIFETIME_CUE_RE = re.compile(
    r"\b(?:only ev(?:er|ery)|year of (?:his|her) diagnosis|when (?:he|she) was \d+)\b",
    re.IGNORECASE,
)


def is_lifetime_oneoff_active_rate(mention: Mapping[str, Any]) -> bool:
    if str(mention.get("entity") or "") != "SeizureFrequency":
        return False
    if _frequency_state(dict(mention.get("attributes") or {})) != "active-rate":
        return False
    attrs = {
        str(key): str(value)
        for key, value in dict(mention.get("attributes") or {}).items()
        if value not in (None, "")
    }
    if any(key in PERIOD_KEYS for key in attrs):
        return False
    return LIFETIME_CUE_RE.search(str(mention.get("evidence") or "")) is not None


def apply_lifetime_oneoff_active_rate_drop(
    mentions: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    kept: list[dict[str, Any]] = []
    actions: list[dict[str, str]] = []
    for mention in mentions:
        if is_lifetime_oneoff_active_rate(mention):
            actions.append(
                {
                    "action": "drop",
                    "text": str(mention.get("text") or ""),
                    "cui": str((mention.get("attributes") or {}).get("CUI") or ""),
                }
            )
            continue
        kept.append(dict(mention))
    return kept, actions
