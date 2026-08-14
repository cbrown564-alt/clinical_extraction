"""Drop an active-rate SF mention that is only a bare positive count."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.seizure_frequency import (
    _frequency_state,
)

COUNT_KEYS = (
    "NumberOfSeizures",
    "LowerNumberOfSeizures",
    "UpperNumberOfSeizures",
)
FRAME_KEYS = (
    "TimePeriod",
    "NumberOfTimePeriods",
    "LowerNumberOfTimePeriods",
    "UpperNumberOfTimePeriods",
    "PointInTime",
    "TimeSince_or_TimeOfEvent",
    "DayDate",
    "MonthDate",
    "YearDate",
    "FrequencyChange",
    "AgeLower",
    "AgeUpper",
    "AgeUnit",
)
IGNORE_KEYS = frozenset({"CUI", "CUIPhrase"})


def is_bare_count_active_rate(mention: Mapping[str, Any]) -> bool:
    if str(mention.get("entity") or "") != "SeizureFrequency":
        return False
    attrs = {
        str(key): str(value)
        for key, value in dict(mention.get("attributes") or {}).items()
        if key not in IGNORE_KEYS and value not in (None, "")
    }
    if _frequency_state(dict(mention.get("attributes") or {})) != "active-rate":
        return False
    if any(key in FRAME_KEYS for key in attrs):
        return False
    return any(key in COUNT_KEYS and attrs[key] != "0" for key in attrs)


def apply_bare_count_active_rate_drop(
    mentions: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    kept: list[dict[str, Any]] = []
    actions: list[dict[str, str]] = []
    for mention in mentions:
        if is_bare_count_active_rate(mention):
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
