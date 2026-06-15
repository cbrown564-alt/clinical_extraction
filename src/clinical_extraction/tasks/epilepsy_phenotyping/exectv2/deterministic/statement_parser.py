"""Structured narrative statements for SeizureFrequency extraction.

The primary pipeline binds attributes to anchors within one sentence. Some
letters use a two-sentence clinical shorthand instead: name the seizure type,
then give a rate or seizure-free duration with a pronoun ("these", "they",
"like this"). This module handles only those local carry-forward statements.
"""
from __future__ import annotations

import re

from ..contract.prediction import PredictedMention
from ..data import SEIZURE_FREQUENCY
from .frequency_section import _last_event_date_attrs, _rate_attrs
from .lexicon import assign_cui
from .normalizer import normalize_count, normalize_unit
from .rule_metadata import DEFAULT_ABLATION, ExtractionContext
from .rules.anchor import SEIZURE_TYPE_ANCHOR_RULE

_SENTENCE = re.compile(r"[^.!?\n]+(?:[.!?]|\n|$)")
_PRONOUN_CONTINUATION = re.compile(
    r"\b(?:they|these|this|it|seizure\s+like\s+this|one\s+like\s+this)\b",
    re.IGNORECASE,
)
_NO_EVENT_DURATION = re.compile(
    r"\b(?:(?:has|have|had)\s+not\s+had\s+(?:any\s+|a\s+|one\s+)?"
    r"(?:[a-z][a-z-]*\s+){0,4}?(?:seizures?|convulsions?|one|seizure\s+like\s+this)|"
    r"(?:hasn't|haven't|hadn't)\s+(?:had\s+)?(?:any\s+|a\s+|one\s+)?"
    r"(?:[a-z][a-z-]*\s+){0,4}?(?:seizures?|convulsions?|one|seizure\s+like\s+this)|"
    r"(?:they|these|this|it)\s+(?:have|has)?\s*not\s+happen(?:ed)?)"
    r"\s+(?:now\s+)?for\s+(?:around\s+|about\s+|at\s+least\s+|over\s+|more\s+than\s+)?"
    r"(?P<count>\d+|one|two|three|four|five|six|seven|eight|nine|ten|several|few)\s+"
    r"(?P<unit>day|week|month|year)s?\b",
    re.IGNORECASE,
)
_STOPPED_SINCE_DRUG = re.compile(
    r"\bseizures?\s+(?:have|has)\s+stopped\s+since\s+"
    r"(?:reaching|starting|commencing|increasing|changing)\b",
    re.IGNORECASE,
)
_NO_FURTHER_SINCE_DRUG = re.compile(
    r"\b(?:has|have)\s+had\s+no\s+further\s+seizures?\s+since\s+"
    r"(?:starting|commencing|reaching|increasing|changing)\b",
    re.IGNORECASE,
)
_COUNT_LAST_YEAR = re.compile(
    r"\b(?P<count>\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+"
    r"(?:[a-z][a-z-]*\s+){0,4}?seizures?\s+in\s+the\s+last\s+year\b",
    re.IGNORECASE,
)
_MANAGEMENT_TITRATION = re.compile(
    r"\b(?:mg|mgs|milligram|milligrammes|dose|dosing|increase\s+by|reduce\s+"
    r"by|start\s+lamotrigine|lamotrigine|levetiracetam|carbamazepine|"
    r"oxcarbazine|zonisamide|everolimus|phenobarbitone)\b",
    re.IGNORECASE,
)
_GENERIC_REFERENCE_ANCHORS = {"seizure", "seizures"}


def _with_cui(text: str, attrs: dict[str, str]) -> dict[str, str]:
    cui = assign_cui(text)
    if cui is None:
        return attrs
    return {**attrs, "CUI": cui, "CUIPhrase": text}


def _anchors(sentence: str) -> list[tuple[str, tuple[int, int]]]:
    ctx = ExtractionContext(text=sentence)
    return [
        (c.text, c.span)
        for c in SEIZURE_TYPE_ANCHOR_RULE.apply(ctx, DEFAULT_ABLATION)
        if c.evidence and c.evidence in sentence
    ]


def _mention(anchor_text: str, attrs: dict[str, str], evidence: str) -> PredictedMention:
    return PredictedMention(
        entity=SEIZURE_FREQUENCY,
        text=anchor_text,
        attributes=_with_cui(anchor_text, attrs),
        evidence=evidence.strip(),
        component_owner="deterministic_statement_parser",
    )


def _zero_duration_attrs(sentence: str) -> dict[str, str] | None:
    match = _NO_EVENT_DURATION.search(sentence)
    if not match:
        return None
    return {
        "NumberOfSeizures": "0",
        "NumberOfTimePeriods": normalize_count(match.group("count")),
        "TimePeriod": normalize_unit(match.group("unit")),
    }


def _drug_zero_attrs(sentence: str) -> dict[str, str] | None:
    if not (_STOPPED_SINCE_DRUG.search(sentence) or _NO_FURTHER_SINCE_DRUG.search(sentence)):
        return None
    return {
        "NumberOfSeizures": "0",
        "PointInTime": "DrugChange",
        "TimeSince_or_TimeOfEvent": "Since",
    }


def _last_year_count_attrs(sentence: str) -> dict[str, str] | None:
    match = _COUNT_LAST_YEAR.search(sentence)
    if not match:
        return None
    return {
        "NumberOfSeizures": normalize_count(match.group("count")),
        "PointInTime": "Last_Year",
        "TimeSince_or_TimeOfEvent": "During",
    }


def _statement_attrs(sentence: str) -> list[dict[str, str]]:
    attrs: list[dict[str, str]] = []
    zero_duration = _zero_duration_attrs(sentence)
    if zero_duration:
        attrs.append(zero_duration)
        return attrs

    rate = _rate_attrs(sentence)
    if rate and "FrequencyChange" not in rate and not _MANAGEMENT_TITRATION.search(sentence):
        attrs.append(rate)

    for candidate in (_last_event_date_attrs(sentence),):
        if candidate:
            attrs.append(candidate)

    for candidate in (_drug_zero_attrs(sentence), _last_year_count_attrs(sentence)):
        if candidate:
            attrs.append(candidate)
    return attrs


def statement_mentions(text: str) -> list[PredictedMention]:
    mentions: list[PredictedMention] = []
    previous_anchor: str | None = None

    for match in _SENTENCE.finditer(text):
        sentence = match.group(0).strip()
        if not sentence:
            continue

        anchors = _anchors(sentence)
        generic_reference = (
            bool(anchors)
            and bool(previous_anchor)
            and _PRONOUN_CONTINUATION.search(sentence)
            and all(anchor[0].lower() in _GENERIC_REFERENCE_ANCHORS for anchor in anchors)
        )
        if anchors:
            if generic_reference:
                anchors = []
            else:
                previous_anchor = max(anchors, key=lambda item: len(item[0]))[0]
                continue

        attrs_list = _statement_attrs(sentence)
        if not attrs_list:
            continue

        anchor_text: str | None = None
        if previous_anchor and _PRONOUN_CONTINUATION.search(sentence):
            anchor_text = previous_anchor

        if not anchor_text:
            continue
        for attrs in attrs_list:
            mentions.append(_mention(anchor_text, attrs, sentence))

    return mentions
