"""Structured parser for ExECTv2 seizure-frequency header blocks.

The generic anchor/attribute association pipeline is intentionally conservative:
one anchor span gathers nearby attributes and emits one mention. Frequency
header mini-tables sometimes need a different shape, e.g. one seizure type with
two dated events on the same line. This module handles only explicitly labeled
``Seizure type and frequency`` blocks and emits benchmark-format extra mentions
for those structured list cases.
"""
from __future__ import annotations

import re

from ..contract.entities import SEIZURE_FREQUENCY
from ..contract.prediction import PredictedMention
from .lexicon import assign_cui
from .normalizer import MONTH_NAME_PATTERN, normalize_count, normalize_month, normalize_unit
from .rule_metadata import DEFAULT_ABLATION, ExtractionContext
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.adapters.extraction import (
    SEIZURE_TYPE_ANCHOR_RULE,
)

_SECTION_HEADER = re.compile(r"\bseizure\s+type\s+and\s+frequency\s*:\s*", re.IGNORECASE)
_STOP_HEADER = re.compile(
    r"^(?:current|previous|other|anti[- ]?epileptic|antiepileptic|medication|"
    r"investigations?|mri|eeg|dear\b|i\s+(?:reviewed|spoke|saw)\b)",
    re.IGNORECASE,
)
_DATE_LIST = re.compile(
    rf"\b(?P<month>{MONTH_NAME_PATTERN})\s+(?P<year>(?:19|20)\d\d)\b",
    re.IGNORECASE,
)
_COUNT = r"\d+|one|two|three|four|five|six|seven|eight|nine|ten|once|twice"
_UNIT = r"day|week|month|year|days|weeks|months|years"
_RANGE_RATE = re.compile(
    rf"\b(?P<lower>{_COUNT})\s*(?:[-–—]|to|or)\s*(?P<upper>{_COUNT})\s+"
    rf"(?:times?\s+)?(?:per|a|each|every)\s+(?P<unit>{_UNIT})\b",
    re.IGNORECASE,
)
_COUNT_RATE = re.compile(
    rf"\b(?P<count>{_COUNT})\s+(?:per|a|each|every)\s+(?P<unit>{_UNIT})\b",
    re.IGNORECASE,
)
_ADVERB_RATE = re.compile(r"\b(?P<adv>daily|weekly|monthly|fortnightly|yearly|annually)\b", re.IGNORECASE)
_EVERY_N_RATE = re.compile(
    rf"\bevery\s+(?P<period_count>{_COUNT})\s+(?P<unit>{_UNIT})\b",
    re.IGNORECASE,
)
_EVERY_PERIOD_RATE = re.compile(rf"\bevery\s+(?P<unit>{_UNIT})\b", re.IGNORECASE)
_COUNT_SINCE_LAST_CLINIC = re.compile(
    rf"\b(?P<count>{_COUNT})\s+since\s+(?:the\s+)?(?:previous|last)\s+(?:appointment|clinic|review|visit)\b",
    re.IGNORECASE,
)
_OCCASIONAL = re.compile(r"\boccasional(?:ly)?\b", re.IGNORECASE)
_LAST_EVENT_AGO = re.compile(
    rf"\blast\s+(?:event|one|seizure)\s+(?:was\s+|being\s+|occurred\s+)?"
    rf"(?:around\s+|about\s+|more\s+than\s+)?(?P<count>{_COUNT})\s+(?P<unit>{_UNIT})\s+ago\b",
    re.IGNORECASE,
)
_LAST_EVENT_DATE = re.compile(
    rf"\blast\s+(?:event|one|seizure)\s+(?:was\s+|being\s+|occurred\s+)?"
    rf"(?:around\s+|about\s+|in\s+|on\s+|at\s+)?"
    rf"(?:(?P<day>\d{{1,2}})(?:st|nd|rd|th)?\s+)?"
    rf"(?:(?P<christmas>christmas)(?:\s+(?P<christmas_qualifier>day|time))?|"
    rf"(?P<month>{MONTH_NAME_PATTERN}))?\s*(?P<year>(?:19|20)\d\d)?\b",
    re.IGNORECASE,
)
_ADVERB_MAP = {
    "daily": ("1", "1", "Day"),
    "weekly": ("1", "1", "Week"),
    "monthly": ("1", "1", "Month"),
    "fortnightly": ("1", "2", "Week"),
    "yearly": ("1", "1", "Year"),
    "annually": ("1", "1", "Year"),
}


def _with_cui(text: str, attrs: dict[str, str]) -> dict[str, str]:
    cui = assign_cui(text)
    if cui is None:
        return attrs
    return {**attrs, "CUI": cui, "CUIPhrase": text}


def _first_anchor(line: str) -> tuple[str, tuple[int, int]] | None:
    ctx = ExtractionContext(text=line)
    anchors = [
        c for c in SEIZURE_TYPE_ANCHOR_RULE.apply(ctx, DEFAULT_ABLATION)
        if c.evidence and c.evidence in line
    ]
    if not anchors:
        return None
    anchor = min(anchors, key=lambda c: c.span[0])
    return anchor.text, anchor.span


def _mention(anchor_text: str, attrs: dict[str, str], evidence: str) -> PredictedMention:
    return PredictedMention(
        entity=SEIZURE_FREQUENCY.name,
        text=anchor_text,
        attributes=_with_cui(anchor_text, attrs),
        evidence=evidence,
        component_owner="deterministic_frequency_section",
    )


def _frequency_section_lines(text: str) -> list[tuple[str, int]]:
    """Return non-empty content lines from all labeled frequency sections."""
    lines = text.splitlines(keepends=True)
    out: list[tuple[str, int]] = []
    in_section = False
    offset = 0
    for raw in lines:
        line_start = offset
        offset += len(raw)
        line = raw.rstrip("\r\n")
        stripped = line.strip(" \t\u00a0")

        header = _SECTION_HEADER.search(line)
        if header:
            in_section = True
            remainder = line[header.end():].strip(" \t\u00a0")
            if remainder:
                out.append((remainder, line_start + header.end()))
            continue

        if not in_section:
            continue
        if not stripped:
            break
        if _STOP_HEADER.match(stripped):
            break
        out.append((stripped, line_start + line.find(stripped)))
    return out


def _last_event_date_attrs(line: str) -> dict[str, str] | None:
    match = _LAST_EVENT_AGO.search(line)
    if match:
        return {
            "NumberOfSeizures": "0",
            "NumberOfTimePeriods": normalize_count(match.group("count")),
            "TimePeriod": normalize_unit(match.group("unit")),
        }

    match = _LAST_EVENT_DATE.search(line)
    if not match:
        return None
    month = match.groupdict().get("month")
    day = match.groupdict().get("day")
    year = match.groupdict().get("year")
    christmas = match.groupdict().get("christmas")
    christmas_qualifier = match.groupdict().get("christmas_qualifier")
    if christmas:
        month = "December"
        if christmas_qualifier and christmas_qualifier.lower() == "day":
            day = "25"
    if not (month or year):
        return None
    attrs = {"NumberOfSeizures": "0", "TimeSince_or_TimeOfEvent": "Since"}
    if day:
        attrs["DayDate"] = day
    if month:
        attrs["MonthDate"] = normalize_month(month)
    if year:
        attrs["YearDate"] = year
    return attrs


def _rate_attrs(line: str) -> dict[str, str] | None:
    match = _RANGE_RATE.search(line)
    if match:
        return {
            "LowerNumberOfSeizures": normalize_count(match.group("lower")),
            "UpperNumberOfSeizures": normalize_count(match.group("upper")),
            "NumberOfTimePeriods": "1",
            "TimePeriod": normalize_unit(match.group("unit")),
        }

    match = _COUNT_SINCE_LAST_CLINIC.search(line)
    if match:
        return {
            "NumberOfSeizures": normalize_count(match.group("count")),
            "PointInTime": "LastClinic",
            "TimeSince_or_TimeOfEvent": "Since",
        }

    match = _COUNT_RATE.search(line)
    if match:
        return {
            "NumberOfSeizures": normalize_count(match.group("count")),
            "NumberOfTimePeriods": "1",
            "TimePeriod": normalize_unit(match.group("unit")),
        }

    match = _EVERY_N_RATE.search(line)
    if match:
        return {
            "NumberOfSeizures": "1",
            "NumberOfTimePeriods": normalize_count(match.group("period_count")),
            "TimePeriod": normalize_unit(match.group("unit")),
        }

    match = _EVERY_PERIOD_RATE.search(line)
    if match:
        return {
            "NumberOfSeizures": "1",
            "NumberOfTimePeriods": "1",
            "TimePeriod": normalize_unit(match.group("unit")),
        }

    match = _ADVERB_RATE.search(line)
    if match:
        count, period_count, unit = _ADVERB_MAP[match.group("adv").lower()]
        return {
            "NumberOfSeizures": count,
            "NumberOfTimePeriods": period_count,
            "TimePeriod": unit,
        }

    if _OCCASIONAL.search(line):
        return {"FrequencyChange": "Infrequent"}
    return None


def frequency_section_mentions(text: str) -> list[PredictedMention]:
    """Emit extra mentions from structured frequency-section date lists.

    Currently handles a seizure-type anchor followed by more than one bare
    month/year on the same header line:
    ``Focal to bilateral convulsive seizures August 2014 and September 2015``.
    The generic pipeline already captures the first date; this stage supplies
    the additional dated mentions, and exact de-duplication in the pipeline
    prevents double emission.
    """
    mentions: list[PredictedMention] = []
    for line, line_start in _frequency_section_lines(text):
        anchor_info = _first_anchor(line)
        if anchor_info is None:
            continue
        anchor_text, anchor_span = anchor_info
        evidence = line.strip()
        rate_attrs = _rate_attrs(line)
        if rate_attrs:
            mentions.append(_mention(anchor_text, rate_attrs, evidence))

        last_event_attrs = _last_event_date_attrs(line[anchor_span[1]:])
        if last_event_attrs:
            mentions.append(_mention(anchor_text, last_event_attrs, evidence))

        date_matches = list(_DATE_LIST.finditer(line[anchor_span[1]:]))
        if len(date_matches) < 2:
            continue
        for match in date_matches:
            attrs = {
                "NumberOfSeizures": "1",
                "MonthDate": normalize_month(match.group("month")),
                "YearDate": match.group("year"),
                "TimeSince_or_TimeOfEvent": "During",
            }
            mentions.append(_mention(anchor_text, attrs, evidence))
    return mentions
