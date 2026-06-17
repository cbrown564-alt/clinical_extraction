"""Structured narrative statements for SeizureFrequency extraction.

The primary pipeline binds attributes to anchors within one sentence. Some
letters use a two-sentence clinical shorthand instead: name the seizure type,
then give a rate or seizure-free duration with a pronoun ("these", "they",
"like this"). This module handles only those local carry-forward statements.
"""
from __future__ import annotations

import re

from ..contract.entities import SEIZURE_FREQUENCY
from ..contract.prediction import PredictedMention
from .frequency_section import _last_event_date_attrs, _rate_attrs
from .lexicon import assign_cui
from .normalizer import MONTH_NAME_PATTERN, normalize_count, normalize_month, normalize_unit
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
_BARE_COUNT_IN_LAST_PERIOD = re.compile(
    r"\b(?:he|she|they)\s+(?:has|have|had)\s+had\s+"
    r"(?P<count>\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+"
    r"(?:in|over)\s+(?:the\s+)?last\s+"
    r"(?P<period_count>\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+"
    r"(?P<unit>day|week|month|year)s?\b",
    re.IGNORECASE,
)
_LAST_SEIZURE_AGO = re.compile(
    r"\blast\s+seizure\s+(?:now\s+)?(?:was|is)\s+"
    r"(?P<count>\d+|one|two|three|four|five|six|seven|eight|nine|ten|several|few)\s+"
    r"(?P<unit>day|week|month|year)s?\s+ago\b",
    re.IGNORECASE,
)
_FAIRLY_FREQUENT = re.compile(
    r"\b(?:fairly|relatively|very|more)\s+frequent\b|\bmore\s+frequently\b",
    re.IGNORECASE,
)
_SEVERAL_TIMES_PER_PERIOD = re.compile(
    r"\bseveral\s+times?\s+(?:a|per|each|every)\s+(?P<unit>day|week|month|year)s?\b",
    re.IGNORECASE,
)
_BETWEEN_RANGE_PER_PERIOD = re.compile(
    r"\bbetween\s+(?P<lower>\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+"
    r"and\s+(?P<upper>\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+"
    r"(?:per|a|each|every)\s+(?P<unit>day|week|month|year)s?\b",
    re.IGNORECASE,
)
_IMPROVED_DRUG_CONTROL = re.compile(
    r"\bsignificant\s+improvement\s+since\s+increasing\b.{0,180}?"
    r"\bfocal\s+seizures?\b.{0,120}?\bcompletely\s+under\s+control\s+on\s+"
    r"(?:the\s+)?dose\b",
    re.IGNORECASE | re.DOTALL,
)
_NO_FURTHER_AFTER_COMMENCED = re.compile(
    r"\bonce\s+commenced\s+on\b.{0,140}?\bno\s+further\s+seizures?\b",
    re.IGNORECASE | re.DOTALL,
)
_RETURNED_SEIZURES = re.compile(r"\bseizures?\s+have\s+returned\b", re.IGNORECASE)
_INCREASING_SEIZURES = re.compile(r"\bincreasing\s+seizures?\b", re.IGNORECASE)
_MORE_GENERALISED = re.compile(
    r"\bmore\s+generalised\s+tonic\s+clonic\s+seizures?\b",
    re.IGNORECASE,
)
_WORSE_LAST_YEAR = re.compile(
    r"\bseizures?\s+have\s+been\s+worse\s+in\s+the\s+last\s+year\b",
    re.IGNORECASE,
)
_WELL_CONTROLLED = re.compile(
    r"\b(?:seizures?|epilepsy)\s+(?:remain(?:s)?|are|is)\s+well\s+controlled\b",
    re.IGNORECASE,
)
_SEIZURES_ALSO_WELL_CONTROLLED = re.compile(
    r"\bseizures?\s+are\s+also\s+well\s+controlled\b",
    re.IGNORECASE,
)
_DATED_RANGE_RATE = re.compile(
    r"\bin\s+(?P<month>[A-Z][a-z]+),?\s+(?P<year>(?:19|20)\d\d)\s+"
    r"where\s+(?:he|she|they)\s+had\s+"
    r"(?P<lower>\d+)\s*[-–—]\s*(?P<upper>\d+)\s+seizures?\s+every\s+"
    r"(?P<unit>day|week|month|year)s?\b",
    re.IGNORECASE,
)
_TYPE_RANGE_FROM_MONTHS = re.compile(
    r"\b(?P<lower>\d+)\s*[-–—]\s*(?P<upper>\d+)\s+"
    r"generalised\s+tonic\s+chronic\s+seizures?\s+per\s+"
    r"(?P<unit>day|week|month|year)s?\s+from\s+"
    r"(?P<start_month>[A-Z][a-z]+)\s+to\s+(?P<end_month>[A-Z][a-z]+)\b",
    re.IGNORECASE,
)
_WEEKDAY_GTC = re.compile(
    r"\bon\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
    r"(?:\s+and\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday))?,\s+"
    r"(?:he|she|they)\s+was\s+having\s+generalised\s+tonic\s+clonic\s+seizures?\b",
    re.IGNORECASE,
)
_TOTAL_IN_YEAR = re.compile(
    r"\btotal\s+of\s+(?P<count>\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+"
    r"in\s+(?P<year>(?:19|20)\d\d)\b",
    re.IGNORECASE,
)
_SEVERAL_PER_WEEK_SINCE_MONTH = re.compile(
    r"\bsince\s+(?P<month>[A-Z][a-z]+)\s+(?:he|she|they)\s+has\s+been\s+having\s+"
    r"several\s+per\s+week\b",
    re.IGNORECASE,
)
_FTB_AT_DIAGNOSIS_MONTH_YEAR = re.compile(
    r"\bone\s+previous\s+focal\s+to\s+bilateral\s+convulsive\s+seizure\s+"
    r"at\s+the\s+time\s+of\s+diagnosis\b.{0,80}?\bin\s+"
    r"(?P<month>[A-Z][a-z]+)\s+(?P<year>(?:19|20)\d\d)\b",
    re.IGNORECASE | re.DOTALL,
)
_LAST_EVENT_MONTHS_AGO = re.compile(
    r"\blast\s+event\s+was\s+probably\s+"
    r"(?P<count>\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+months?\s+ago\b",
    re.IGNORECASE,
)
_WELL_NO_FURTHER_SEIZURES = re.compile(
    r"\b(?:feeling|is)\s+(?:very\s+)?well\b.{0,80}?"
    r"\b(?:has\s+not\s+had\s+any\s+further\s+seizures?|has\s+had\s+no\s+further\s+seizures?)\b",
    re.IGNORECASE,
)
_NO_MORE_SINCE_DATE = re.compile(
    r"\bsince\s+(?P<month>[A-Z][a-z]+)\s+(?P<day>\d{1,2})(?:st|nd|rd|th)?\s+"
    r"(?:he|she|they)\s+has\s+not\s+had\s+any\s+more\s+seizures?\b",
    re.IGNORECASE,
)
_NO_MORE_SINCE_LAST_CLINIC = re.compile(
    r"\bsince\s+i\s+last\s+saw\b.{0,80}?"
    r"\b(?:he|she|they)\s+has\s+not\s+had\s+any\s+more\s+seizures?\b",
    re.IGNORECASE | re.DOTALL,
)
_NO_FURTHER_SINCE_DRUG = re.compile(
    r"\bno\s+further\s+seizures?\b.{0,80}?\bsince\s+"
    r"(?:starting|commencing|reaching|increasing|changing)\b",
    re.IGNORECASE | re.DOTALL,
)
_REMAINED_SEIZURE_FREE_DURATION = re.compile(
    r"\bremained\s+seizure\s+free\s+for\s+"
    r"(?P<count>\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+"
    r"(?P<unit>day|week|month|year)s?\b",
    re.IGNORECASE,
)
_REMAINS_SEIZURE_FREE = re.compile(r"\bremains?\s+seiz(?:u|r)re\s+free\b", re.IGNORECASE)
_LAST_SEIZURE_DATE = re.compile(
    r"\blast\s+seizure\s+was\s+(?:on\s+)?(?:the\s+)?"
    r"(?:(?P<day>\d{1,2})(?:st|nd|rd|th)?\s+)?"
    rf"(?P<month>{MONTH_NAME_PATTERN}|Novemebr)(?:\s+(?P<year>(?:19|20)\d\d))?\b",
    re.IGNORECASE,
)
_SINGLE_SEIZURE_AGO = re.compile(
    r"\bsingle\s+seizure\s+some\s+"
    r"(?P<count>\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+"
    r"(?P<unit>day|week|month|year)s?\s+ago\b",
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
        entity=SEIZURE_FREQUENCY.name,
        text=anchor_text,
        attributes=_with_cui(anchor_text, attrs),
        evidence=evidence.strip(),
        component_owner="deterministic_statement_parser",
    )


def _seizure_free_surface_mention(attrs: dict[str, str], evidence: str) -> PredictedMention:
    return PredictedMention(
        entity=SEIZURE_FREQUENCY.name,
        text="seizure",
        attributes={**attrs, "CUI": "C1299590", "CUIPhrase": "seizure"},
        evidence=evidence.strip(),
        component_owner="deterministic_statement_parser",
    )


def _forced_cui_mention(anchor_text: str, attrs: dict[str, str], cui: str, evidence: str) -> PredictedMention:
    return PredictedMention(
        entity=SEIZURE_FREQUENCY.name,
        text=anchor_text,
        attributes={**attrs, "CUI": cui, "CUIPhrase": anchor_text},
        evidence=evidence.strip(),
        component_owner="deterministic_statement_parser",
    )


def _norm_month(month: str) -> str:
    lowered = month.lower()
    if lowered == "novemebr":
        return "11"
    if lowered == "feburary":
        return "2"
    return normalize_month(month)


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


def _count_in_last_period_attrs(sentence: str) -> dict[str, str] | None:
    match = _BARE_COUNT_IN_LAST_PERIOD.search(sentence)
    if not match:
        return None
    return {
        "NumberOfSeizures": normalize_count(match.group("count")),
        "NumberOfTimePeriods": normalize_count(match.group("period_count")),
        "TimePeriod": normalize_unit(match.group("unit")),
    }


def _last_seizure_ago_attrs(sentence: str) -> dict[str, str] | None:
    match = _LAST_SEIZURE_AGO.search(sentence)
    if not match:
        return None
    return {
        "NumberOfSeizures": "0",
        "NumberOfTimePeriods": normalize_count(match.group("count")),
        "TimePeriod": normalize_unit(match.group("unit")),
    }


def _same_sentence_mentions(sentence: str, anchors: list[tuple[str, tuple[int, int]]]) -> list[PredictedMention]:
    mentions: list[PredictedMention] = []
    if not anchors:
        return mentions

    anchor_text = max(anchors, key=lambda item: len(item[0]))[0]
    generic_anchor = next((text for text, _span in anchors if text.lower() == "seizures"), None)
    if generic_anchor is None:
        generic_anchor = next(
            (text for text, _span in anchors if text.lower() in _GENERIC_REFERENCE_ANCHORS),
            anchor_text,
        )

    drug_attrs = _drug_zero_attrs(sentence)
    if drug_attrs:
        mentions.append(_mention(generic_anchor, drug_attrs, sentence))

    ago_attrs = _last_seizure_ago_attrs(sentence)
    if ago_attrs:
        mentions.append(_mention(generic_anchor, ago_attrs, sentence))

    between = _BETWEEN_RANGE_PER_PERIOD.search(sentence)
    rate = (
        {
            "LowerNumberOfSeizures": normalize_count(between.group("lower")),
            "UpperNumberOfSeizures": normalize_count(between.group("upper")),
            "NumberOfTimePeriods": "1",
            "TimePeriod": normalize_unit(between.group("unit")),
        }
        if between
        else _rate_attrs(sentence)
    )
    if rate and _FAIRLY_FREQUENT.search(sentence):
        mentions.append(_mention(anchor_text, {**rate, "TimeSince_or_TimeOfEvent": "During"}, sentence))
        mentions.append(_mention(anchor_text, {"FrequencyChange": "Frequent"}, sentence))

    several = _SEVERAL_TIMES_PER_PERIOD.search(sentence)
    if several and re.search(r"\babsences?\s+and\s+jerks?\b", sentence, re.IGNORECASE):
        mentions.append(
            _mention(
                "absences",
                {
                    "NumberOfSeizures": "2",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": normalize_unit(several.group("unit")),
                },
                sentence,
            )
        )
    return mentions


def _global_statement_mentions(text: str) -> list[PredictedMention]:
    mentions: list[PredictedMention] = []
    for match in _IMPROVED_DRUG_CONTROL.finditer(text):
        evidence = match.group(0)
        mentions.append(_mention("focal seizures", {"NumberOfSeizures": "0", "PointInTime": "DrugChange"}, evidence))
        mentions.append(_mention("seizures", {"FrequencyChange": "Infrequent", "PointInTime": "DrugChange"}, evidence))

    for match in _NO_FURTHER_AFTER_COMMENCED.finditer(text):
        mentions.append(
            _mention(
                "seizures",
                {
                    "NumberOfSeizures": "0",
                    "PointInTime": "DrugChange",
                    "TimeSince_or_TimeOfEvent": "Since",
                },
                match.group(0),
            )
        )
    for match in _RETURNED_SEIZURES.finditer(text):
        mentions.append(_mention("seizure", {"FrequencyChange": "Increased"}, match.group(0)))

    for match in _INCREASING_SEIZURES.finditer(text):
        mentions.append(_mention("seizure", {"FrequencyChange": "Increased"}, match.group(0)))

    for match in _MORE_GENERALISED.finditer(text):
        mentions.append(_mention("generalised", {"FrequencyChange": "Increased"}, match.group(0)))

    for match in _WORSE_LAST_YEAR.finditer(text):
        mentions.append(
            _mention(
                "seizures",
                {
                    "FrequencyChange": "Increased",
                    "PointInTime": "Last_Year",
                    "TimeSince_or_TimeOfEvent": "Since",
                },
                match.group(0),
            )
        )

    for match in _SEIZURES_ALSO_WELL_CONTROLLED.finditer(text):
        mentions.append(_mention("seizures", {"FrequencyChange": "Infrequent"}, match.group(0)))

    for match in _WELL_CONTROLLED.finditer(text):
        mentions.append(_mention("seizure", {"FrequencyChange": "Same"}, match.group(0)))

    for match in _DATED_RANGE_RATE.finditer(text):
        mentions.append(
            _mention(
                "seizures",
                {
                    "LowerNumberOfSeizures": match.group("lower"),
                    "UpperNumberOfSeizures": match.group("upper"),
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": normalize_unit(match.group("unit")),
                    "MonthDate": _norm_month(match.group("month")),
                    "YearDate": match.group("year"),
                    "TimeSince_or_TimeOfEvent": "During",
                },
                match.group(0),
            )
        )

    for match in _TYPE_RANGE_FROM_MONTHS.finditer(text):
        mentions.append(
            _mention(
                "generalised tonic clonic seizures",
                {
                    "LowerNumberOfSeizures": match.group("lower"),
                    "UpperNumberOfSeizures": match.group("upper"),
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": normalize_unit(match.group("unit")),
                    "TimeSince_or_TimeOfEvent": "During",
                },
                match.group(0),
            )
        )

    for match in _WEEKDAY_GTC.finditer(text):
        mentions.append(
            _mention(
                "generalised tonic clonic seizures",
                {
                    "NumberOfSeizures": "1",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Day",
                    "TimeSince_or_TimeOfEvent": "During",
                },
                match.group(0),
            )
        )

    for match in _TOTAL_IN_YEAR.finditer(text):
        mentions.append(
            _mention(
                "seizures",
                {
                    "NumberOfSeizures": normalize_count(match.group("count")),
                    "YearDate": match.group("year"),
                    "TimeSince_or_TimeOfEvent": "During",
                },
                match.group(0),
            )
        )

    for match in _SEVERAL_PER_WEEK_SINCE_MONTH.finditer(text):
        mentions.append(
            _mention(
                "seizure",
                {
                    "NumberOfSeizures": "3",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Week",
                },
                match.group(0),
            )
        )

    for match in _FTB_AT_DIAGNOSIS_MONTH_YEAR.finditer(text):
        mentions.append(
            _mention(
                "focal to bilateral convulsive seizure",
                {
                    "NumberOfSeizures": "1",
                    "MonthDate": _norm_month(match.group("month")),
                    "YearDate": match.group("year"),
                    "TimeSince_or_TimeOfEvent": "During",
                },
                match.group(0),
            )
        )

    for match in _LAST_EVENT_MONTHS_AGO.finditer(text):
        mentions.append(
            _forced_cui_mention(
                "focal",
                {
                    "NumberOfSeizures": "0",
                    "NumberOfTimePeriods": normalize_count(match.group("count")),
                    "TimePeriod": "Month",
                },
                "C0016399",
                match.group(0),
            )
        )

    for match in _NO_MORE_SINCE_DATE.finditer(text):
        mentions.append(
            _mention(
                "seizures",
                {
                    "NumberOfSeizures": "0",
                    "MonthDate": _norm_month(match.group("month")),
                    "DayDate": match.group("day"),
                    "TimeSince_or_TimeOfEvent": "Since",
                },
                match.group(0),
            )
        )

    for match in _NO_MORE_SINCE_LAST_CLINIC.finditer(text):
        mentions.append(
            _mention(
                "seizures",
                {
                    "NumberOfSeizures": "0",
                    "PointInTime": "LastClinic",
                    "TimeSince_or_TimeOfEvent": "Since",
                },
                match.group(0),
            )
        )

    for match in _NO_FURTHER_SINCE_DRUG.finditer(text):
        mentions.append(
            _mention(
                "seizures",
                {
                    "NumberOfSeizures": "0",
                    "PointInTime": "DrugChange",
                    "TimeSince_or_TimeOfEvent": "Since",
                },
                match.group(0),
            )
        )

    for match in _WELL_NO_FURTHER_SEIZURES.finditer(text):
        mentions.append(_mention("seizures", {"NumberOfSeizures": "0"}, match.group(0)))

    for match in _REMAINED_SEIZURE_FREE_DURATION.finditer(text):
        mentions.append(
            _mention(
                "seizure-freedom",
                {
                    "NumberOfSeizures": "0",
                    "NumberOfTimePeriods": normalize_count(match.group("count")),
                    "TimePeriod": normalize_unit(match.group("unit")),
                },
                match.group(0),
            )
        )

    for match in _REMAINS_SEIZURE_FREE.finditer(text):
        follow = text[match.end(): match.end() + 40].lower()
        if "driving" in follow:
            continue
        if "after" in follow and "surgery" in follow:
            mentions.append(
                _seizure_free_surface_mention(
                    {
                        "NumberOfSeizures": "0",
                        "PointInTime": "Surgery",
                        "TimeSince_or_TimeOfEvent": "Since",
                    },
                    match.group(0) + text[match.end(): match.end() + 20],
                )
            )
            continue
        mentions.append(
            _seizure_free_surface_mention(
                {"NumberOfSeizures": "0", "FrequencyChange": "Same"},
                match.group(0),
            )
        )
        mentions.append(_seizure_free_surface_mention({"NumberOfSeizures": "0"}, match.group(0)))

    for match in _LAST_SEIZURE_DATE.finditer(text):
        month = match.group("month")
        normalized_month = _norm_month(month)
        attrs = {"NumberOfSeizures": "0", "MonthDate": normalized_month}
        if match.group("day"):
            attrs["DayDate"] = match.group("day")
        if match.group("year"):
            attrs["YearDate"] = match.group("year")
            attrs["TimeSince_or_TimeOfEvent"] = "Since"
        mentions.append(_mention("seizure", attrs, match.group(0)))
        if match.group("year"):
            no_since_attrs = {k: v for k, v in attrs.items() if k != "TimeSince_or_TimeOfEvent"}
            mentions.append(_mention("seizure", no_since_attrs, match.group(0)))

    for match in _SINGLE_SEIZURE_AGO.finditer(text):
        mentions.append(
            _mention(
                "seizure",
                {
                    "NumberOfSeizures": "0",
                    "NumberOfTimePeriods": normalize_count(match.group("count")),
                    "TimePeriod": normalize_unit(match.group("unit")),
                },
                match.group(0),
            )
        )
    return mentions


def statement_mentions(text: str) -> list[PredictedMention]:
    mentions: list[PredictedMention] = _global_statement_mentions(text)
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
                mentions.extend(_same_sentence_mentions(sentence, anchors))
                previous_anchor = max(anchors, key=lambda item: len(item[0]))[0]
                continue

        attrs_list = _statement_attrs(sentence)
        if previous_anchor:
            count_in_last_period = _count_in_last_period_attrs(sentence)
            if count_in_last_period:
                attrs_list.append(count_in_last_period)
        if not attrs_list:
            continue

        anchor_text: str | None = None
        if previous_anchor and _PRONOUN_CONTINUATION.search(sentence):
            anchor_text = previous_anchor
        elif previous_anchor and _count_in_last_period_attrs(sentence):
            anchor_text = previous_anchor

        if not anchor_text:
            continue
        for attrs in attrs_list:
            mentions.append(_mention(anchor_text, attrs, sentence))

    return mentions
