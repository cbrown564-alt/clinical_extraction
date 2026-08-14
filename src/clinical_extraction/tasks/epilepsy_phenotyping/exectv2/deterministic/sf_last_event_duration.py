"""Last-event duration parse and leftover active-rate conversion."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import (
    normalize_phrase,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.lexicon import (
    assign_cui,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.seizure_frequency import (
    _frequency_state,
)

_WORD_NUMBER: dict[str, str] = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
}


def last_event_duration(evidence: str) -> tuple[str, str] | None:
    """Return ``(number, TimePeriod)`` for an explicit last-event ago span."""

    lower = evidence.lower()
    if not re.search(r"\b(last|single|about|ago)\b", lower):
        return None
    match = re.search(
        r"\b(?P<num>\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+"
        r"(?P<unit>weeks?|months?|years?)\s+ago\b",
        lower,
    )
    if not match:
        return None
    return (_number_token(match.group("num")), _unit_token(match.group("unit")))


def _number_token(token: str) -> str:
    return _WORD_NUMBER.get(token.lower(), token)


def _unit_token(token: str) -> str:
    lower = token.lower()
    if lower.startswith("week"):
        return "Week"
    if lower.startswith("month"):
        return "Month"
    return "Year"


def is_pending_last_event_duration(mention: Mapping[str, Any]) -> bool:
    if str(mention.get("entity") or "") != "SeizureFrequency":
        return False
    if _frequency_state(dict(mention.get("attributes") or {})) != "active-rate":
        return False
    return last_event_duration(str(mention.get("evidence") or "")) is not None


def _rewrite_last_event(mention: Mapping[str, Any]) -> dict[str, Any]:
    evidence = str(mention.get("evidence") or "")
    duration = last_event_duration(evidence)
    if duration is None:
        return dict(mention)
    number, unit = duration
    out = dict(mention)
    text = "seizure" if "seizure" in normalize_phrase(evidence).split() else "seizures"
    attrs = {
        "NumberOfSeizures": "0",
        "NumberOfTimePeriods": number,
        "TimePeriod": unit,
    }
    cui = assign_cui(text)
    if cui:
        attrs["CUI"] = cui
        attrs["CUIPhrase"] = text
    out["text"] = text
    out["attributes"] = attrs
    return out


def apply_last_event_duration_complete(
    mentions: Sequence[Mapping[str, Any]],
    *,
    require_single_or_last: bool = False,
    require_count_one: bool = False,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    kept: list[dict[str, Any]] = []
    actions: list[dict[str, str]] = []
    for mention in mentions:
        if not is_pending_last_event_duration(mention):
            kept.append(dict(mention))
            continue
        evidence = str(mention.get("evidence") or "").lower()
        attrs = dict(mention.get("attributes") or {})
        if require_single_or_last and not (
            "single" in evidence.split() or "last" in evidence.split()
        ):
            kept.append(dict(mention))
            continue
        if require_count_one and str(attrs.get("NumberOfSeizures") or "") != "1":
            kept.append(dict(mention))
            continue
        rewritten = _rewrite_last_event(mention)
        actions.append(
            {
                "action": "repair",
                "text": str(mention.get("text") or ""),
                "cui": str(attrs.get("CUI") or ""),
                "after_state": _frequency_state(dict(rewritten.get("attributes") or {})),
            }
        )
        kept.append(rewritten)
    return kept, actions


def apply_single_last_event(
    mentions: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    return apply_last_event_duration_complete(
        mentions,
        require_single_or_last=True,
        require_count_one=True,
    )
