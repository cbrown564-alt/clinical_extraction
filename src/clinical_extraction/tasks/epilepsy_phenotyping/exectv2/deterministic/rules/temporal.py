"""Temporal-anchoring rules for ExECTv2 SeizureFrequency.

These extract the date / point-in-time / "since vs during" attributes that
41% of gold SF mentions carry (PointInTime, MonthDate, YearDate, DayDate,
TimeSince_or_TimeOfEvent), plus the "last seizure was <date> ⇒ 0 Since"
zero-count generator. They emit AttributeExtractions that associate onto the
nearest seizure anchor; the count is supplied by an explicit count rule, the
seizure-free rules, or the implied-count default.

Guideline basis (v9):
- L231 / Ex3 (L237): TimeSince is used ONLY with a date or point in time, never
  with a bare "N years ago" period — so the period-ago rule emits NO TimeSince.
- Ex1 (L233): "in May" with a positive count ⇒ During.
- Ex6 / L247: "last seizure in <date>" ⇒ Since (no events since that date), even
  though the surface preposition is "in".
- Ex4 (L239): "since starting <drug>" ⇒ PointInTime=DrugChange, Since.
- Ex5 (L243): "since last being seen" ⇒ PointInTime=LastClinic, Since.
- Appendix (L1003-L1011): MonthDate 1-12 numeric, YearDate 4-digit, DayDate
  1-31, PointInTime closed vocab.
"""
from __future__ import annotations

import re

from clinical_extraction.tasks.shared.epilepsy.terms import NUMBER_WORD_PATTERN

from ..candidates import AttributeExtraction, AttributeKind
from ..normalizer import (
    MONTH_NAME_PATTERN,
    clean_span,
    normalize_count,
    normalize_month,
    normalize_unit,
)
from ..rule_metadata import (
    ExtractionContext,
    Portability,
    RuleExample,
    RuleGroup,
    RuleSpec,
)

# ---------------------------------------------------------------------------
# Shared fragments
# ---------------------------------------------------------------------------

_YEAR = r"(?:19|20)\d\d"
_PREP = r"since|after|in|on|during"
# "since the beginning of July", "in early March" — descriptive filler between
# the preposition and the month name; gold keeps only the month.
_DATE_FILLER = r"(?:the\s+)?(?:beginning|start|early|end|middle|mid|late)\s+(?:of\s+)?"
_SF_NOUN = r"seizures?|absences?|jerks?"
# "last [<descriptor words>] seizure" — up to 3 descriptor words before the noun.
_LAST_SEIZURE = rf"last\s+(?:[a-z][a-z\-]*\s+){{0,3}}?(?:{_SF_NOUN})"


def _time_since(prep: str) -> str:
    return "Since" if prep.strip().lower() == "since" else "During"


# A date / point-in-time only contributes SeizureFrequency attributes when it
# sits in a seizure context — otherwise "diagnosed in 2010" or "born in May"
# would attach a spurious date to a nearby seizure anchor. Guideline L255 warns
# against annotating dates/events without a frequency statement.
_SF_CONTEXT = re.compile(r"seizures?|absences?|jerks?|seizure[\s-]?free|fits?", re.IGNORECASE)


def _outside_seizure_context(match: re.Match[str], context: ExtractionContext) -> bool:
    lo = max(0, match.start() - 45)
    hi = min(len(context.text), match.end() + 25)
    return not _SF_CONTEXT.search(context.text[lo:hi])


def _extraction(
    match: re.Match[str],
    attributes: dict[str, str],
    rule_id: str,
) -> AttributeExtraction:
    return AttributeExtraction(
        evidence=clean_span(match.group(0)),
        span=(match.start(), match.end()),
        attributes=attributes,
        kind=AttributeKind.TEMPORAL,
        rule_id=rule_id,
        rule_group=RuleGroup.TEMPORAL_ANCHOR,
        portability=Portability.CLINICAL_EPILEPSY,
    )


# ---------------------------------------------------------------------------
# Point in time: "since <trigger>"  → PointInTime + TimeSince=Since
# ---------------------------------------------------------------------------

_PIT_TRIGGER = (
    r"last\s+clinic|last\s+(?:seen|review(?:ed)?|appointment|visit)|being\s+seen|"
    r"start(?:ing|ed)?|commenc(?:ing|ed)|introduc\w+|"
    r"stop(?:ping|ped)?|discontinu\w+|withdraw\w+|"
    r"dose\s+(?:increase|change|adjustment)|(?:drug|medication)\s+change|"
    r"chang(?:ing|ed)\s+(?:the\s+)?(?:dose|drug|medication)|"
    r"surgery|operation|resection|"
    r"last\s+month|last\s+week|last\s+year|this\s+year|"
    r"birthday|last\s+christmas|easter|discharge\w*"
)


def _pit_value(trigger: str) -> str | None:
    t = trigger.lower()
    if any(w in t for w in ("clinic", "seen", "review", "appointment", "visit")):
        return "LastClinic"
    if (
        t.startswith(("start", "commenc", "introduc", "chang", "stop", "discontinu", "withdraw"))
        or "dose" in t
        or "drug change" in t
        or "medication" in t
    ):
        return "DrugChange"
    if any(w in t for w in ("surgery", "operation", "resection")):
        return "Surgery"
    if "last month" in t:
        return "Last_Month"
    if "last week" in t:
        return "Last_Week"
    if "last year" in t:
        return "Last_Year"
    if "this year" in t:
        return "This_Year"
    if "birthday" in t:
        return "Birthday"
    if "christmas" in t:
        return "LastChristmas"
    if "easter" in t:
        return "Easter"
    if "discharge" in t:
        return "DischargeDate"
    return None


def _build_pit_since(match: re.Match[str], _ctx: ExtractionContext) -> AttributeExtraction | None:
    value = _pit_value(match.group("trig"))
    if value is None:
        return None
    return _extraction(
        match,
        {"PointInTime": value, "TimeSince_or_TimeOfEvent": "Since"},
        rule_id="temporal.point_in_time_since",
    )


PIT_SINCE_RULE = RuleSpec(
    rule_id="temporal.point_in_time_since",
    group=RuleGroup.TEMPORAL_ANCHOR,
    portability=Portability.CLINICAL_EPILEPSY,
    description="'since <point-in-time>' → PointInTime + TimeSince=Since.",
    pattern=re.compile(
        rf"\b(?:since|after)\s+(?:[a-z][a-z'\-]*\s+){{0,4}}?(?P<trig>{_PIT_TRIGGER})\b",
        re.IGNORECASE,
    ),
    build=_build_pit_since,
    exclude=(_outside_seizure_context,),
    examples=(
        RuleExample(
            text="She had two seizures since last being seen.",
            expected_attributes={"PointInTime": "LastClinic", "TimeSince_or_TimeOfEvent": "Since"},
        ),
        RuleExample(
            text="Since starting lamotrigine his seizure frequency has improved.",
            expected_attributes={"PointInTime": "DrugChange", "TimeSince_or_TimeOfEvent": "Since"},
        ),
        RuleExample(
            text="He has had no seizures since his surgery.",
            expected_attributes={"PointInTime": "Surgery", "TimeSince_or_TimeOfEvent": "Since"},
        ),
    ),
    provenance="Guideline v9 Ex4/Ex5 (L239/L243); List 4 points in time.",
)


# ---------------------------------------------------------------------------
# Dates: "<prep> [<day>] <month> [<year>]" / "<prep> <year>"
# TimeSince from preposition: since→Since, in/on/during→During.
# ---------------------------------------------------------------------------

def _build_date_dmy(match: re.Match[str], _ctx: ExtractionContext) -> AttributeExtraction:
    return _extraction(
        match,
        {
            "DayDate": match.group("day"),
            "MonthDate": normalize_month(match.group("month")),
            "YearDate": match.group("year"),
            "TimeSince_or_TimeOfEvent": _time_since(match.group("prep")),
        },
        rule_id="temporal.date_day_month_year",
    )


DATE_DMY_RULE = RuleSpec(
    rule_id="temporal.date_day_month_year",
    group=RuleGroup.TEMPORAL_ANCHOR,
    portability=Portability.CLINICAL_EPILEPSY,
    description="<prep> <day> <month> <year> → DayDate/MonthDate/YearDate + TimeSince.",
    pattern=re.compile(
        rf"\b(?P<prep>{_PREP})\s+(?P<day>\d{{1,2}})(?:st|nd|rd|th)?\s+"
        rf"(?P<month>{MONTH_NAME_PATTERN})\s+(?P<year>{_YEAR})\b",
        re.IGNORECASE,
    ),
    build=_build_date_dmy,
    exclude=(_outside_seizure_context,),
    examples=(
        RuleExample(
            text="Her last event was on 15 March 2018.",
            expected_attributes={
                "DayDate": "15", "MonthDate": "3", "YearDate": "2018",
                "TimeSince_or_TimeOfEvent": "During",
            },
        ),
    ),
    provenance="Guideline Appendix date features (L1003-L1007).",
)


def _build_date_my(match: re.Match[str], _ctx: ExtractionContext) -> AttributeExtraction:
    return _extraction(
        match,
        {
            "MonthDate": normalize_month(match.group("month")),
            "YearDate": match.group("year"),
            "TimeSince_or_TimeOfEvent": _time_since(match.group("prep")),
        },
        rule_id="temporal.date_month_year",
    )


DATE_MY_RULE = RuleSpec(
    rule_id="temporal.date_month_year",
    group=RuleGroup.TEMPORAL_ANCHOR,
    portability=Portability.CLINICAL_EPILEPSY,
    description="<prep> <month> <year> → MonthDate/YearDate + TimeSince.",
    pattern=re.compile(
        rf"\b(?P<prep>{_PREP})\s+(?:{_DATE_FILLER})?(?P<month>{MONTH_NAME_PATTERN})\s+(?P<year>{_YEAR})\b",
        re.IGNORECASE,
    ),
    build=_build_date_my,
    exclude=(_outside_seizure_context,),
    examples=(
        RuleExample(
            text="He had 3 seizures in March 2014.",
            expected_attributes={
                "MonthDate": "3", "YearDate": "2014",
                "TimeSince_or_TimeOfEvent": "During",
            },
        ),
    ),
    provenance="Guideline Appendix date features.",
)


def _build_date_month(match: re.Match[str], _ctx: ExtractionContext) -> AttributeExtraction:
    return _extraction(
        match,
        {
            "MonthDate": normalize_month(match.group("month")),
            "TimeSince_or_TimeOfEvent": _time_since(match.group("prep")),
        },
        rule_id="temporal.date_month",
    )


DATE_MONTH_RULE = RuleSpec(
    rule_id="temporal.date_month",
    group=RuleGroup.TEMPORAL_ANCHOR,
    portability=Portability.CLINICAL_EPILEPSY,
    description="<prep> <month> (no year) → MonthDate + TimeSince.",
    pattern=re.compile(
        rf"\b(?P<prep>{_PREP})\s+(?:{_DATE_FILLER})?(?P<month>{MONTH_NAME_PATTERN})\b(?!\s+(?:{_YEAR}|\d))",
        re.IGNORECASE,
    ),
    build=_build_date_month,
    exclude=(_outside_seizure_context,),
    examples=(
        RuleExample(
            text="He had 5 seizures in May, but none since.",
            expected_attributes={"MonthDate": "5", "TimeSince_or_TimeOfEvent": "During"},
        ),
    ),
    provenance="Guideline Ex1 (L233).",
)


def _build_date_year(match: re.Match[str], _ctx: ExtractionContext) -> AttributeExtraction:
    return _extraction(
        match,
        {
            "YearDate": match.group("year"),
            "TimeSince_or_TimeOfEvent": _time_since(match.group("prep")),
        },
        rule_id="temporal.date_year",
    )


DATE_YEAR_RULE = RuleSpec(
    rule_id="temporal.date_year",
    group=RuleGroup.TEMPORAL_ANCHOR,
    portability=Portability.CLINICAL_EPILEPSY,
    description="<prep> <year> → YearDate + TimeSince.",
    pattern=re.compile(
        rf"\b(?P<prep>{_PREP})\s+(?P<year>{_YEAR})\b",
        re.IGNORECASE,
    ),
    build=_build_date_year,
    exclude=(_outside_seizure_context,),
    examples=(
        RuleExample(
            text="She had 2 seizures in 2014.",
            expected_attributes={"YearDate": "2014", "TimeSince_or_TimeOfEvent": "During"},
        ),
    ),
    provenance="Guideline Appendix date features.",
)


# ---------------------------------------------------------------------------
# "since (before) Christmas [<year>]" → MonthDate=12 (+ YearDate) + Since.
# Gold reads "Christmas" as December (MonthDate=12), not the LastChristmas
# point-in-time value, in the "seizure free / no seizures since Christmas"
# frame (EA0088, EA0093). Restricted to since/before/after framings so it does
# not fire on incidental "at Christmas" prose.
# ---------------------------------------------------------------------------

def _build_christmas(match: re.Match[str], _ctx: ExtractionContext) -> AttributeExtraction:
    attrs: dict[str, str] = {"MonthDate": "12", "TimeSince_or_TimeOfEvent": "Since"}
    year = match.groupdict().get("year")
    if year:
        attrs["YearDate"] = year
    return _extraction(match, attrs, rule_id="temporal.christmas_since")


CHRISTMAS_SINCE_RULE = RuleSpec(
    rule_id="temporal.christmas_since",
    group=RuleGroup.TEMPORAL_ANCHOR,
    portability=Portability.CLINICAL_EPILEPSY,
    description="'since/before/after Christmas [<year>]' → MonthDate=12 (+YearDate) + Since.",
    pattern=re.compile(
        rf"\bsince\s+(?:before\s+|after\s+)?(?:the\s+)?christmas\b(?:\s+(?P<year>{_YEAR}))?",
        re.IGNORECASE,
    ),
    build=_build_christmas,
    exclude=(_outside_seizure_context,),
    examples=(
        RuleExample(
            text="He has been seizure free since before Christmas.",
            expected_attributes={"MonthDate": "12", "TimeSince_or_TimeOfEvent": "Since"},
        ),
        RuleExample(
            text="She has had no seizures since Christmas 2015.",
            expected_attributes={
                "MonthDate": "12", "YearDate": "2015",
                "TimeSince_or_TimeOfEvent": "Since",
            },
        ),
    ),
    provenance="Gold convention: Christmas read as December (EA0088/EA0093).",
)


# ---------------------------------------------------------------------------
# "last seizure was <date>" → NumberOfSeizures=0 + Since + date (L247/L249)
# ---------------------------------------------------------------------------

def _build_last_seizure_date(
    match: re.Match[str], _ctx: ExtractionContext
) -> AttributeExtraction | None:
    month = match.groupdict().get("month")
    year = match.groupdict().get("year")
    day = match.groupdict().get("day")
    if not (month or year):
        return None
    attrs: dict[str, str] = {"NumberOfSeizures": "0", "TimeSince_or_TimeOfEvent": "Since"}
    if day:
        attrs["DayDate"] = day
    if month:
        attrs["MonthDate"] = normalize_month(month)
    if year:
        attrs["YearDate"] = year
    return _extraction(match, attrs, rule_id="temporal.last_seizure_date")


LAST_SEIZURE_DATE_RULE = RuleSpec(
    rule_id="temporal.last_seizure_date",
    group=RuleGroup.TEMPORAL_ANCHOR,
    portability=Portability.CLINICAL_EPILEPSY,
    description="'last seizure [was] in/on <date>' → NumberOfSeizures=0 + Since + date.",
    pattern=re.compile(
        rf"\b{_LAST_SEIZURE}\s+(?:was\s+)?(?:in|on)\s+"
        rf"(?:(?P<day>\d{{1,2}})(?:st|nd|rd|th)?\s+)?"
        rf"(?:(?P<month>{MONTH_NAME_PATTERN})\s*)?(?P<year>{_YEAR})?",
        re.IGNORECASE,
    ),
    build=_build_last_seizure_date,
    examples=(
        RuleExample(
            text="Her last seizure was in September 2012.",
            expected_attributes={
                "NumberOfSeizures": "0", "MonthDate": "9", "YearDate": "2012",
                "TimeSince_or_TimeOfEvent": "Since",
            },
        ),
    ),
    provenance="Guideline Ex6/L247-L249: last seizure in <date> = 0 Since.",
)


# ---------------------------------------------------------------------------
# "last seizure was N <period> ago" → 0 + period (NO TimeSince per Ex3)
# ---------------------------------------------------------------------------

def _build_last_seizure_ago(
    match: re.Match[str], _ctx: ExtractionContext
) -> AttributeExtraction:
    return _extraction(
        match,
        {
            "NumberOfSeizures": "0",
            "NumberOfTimePeriods": normalize_count(match.group("count")),
            "TimePeriod": normalize_unit(match.group("unit")),
        },
        rule_id="temporal.last_seizure_ago",
    )


LAST_SEIZURE_AGO_RULE = RuleSpec(
    rule_id="temporal.last_seizure_ago",
    group=RuleGroup.TEMPORAL_ANCHOR,
    portability=Portability.CLINICAL_EPILEPSY,
    description="'last seizure was N <period> ago' → 0 + period, no TimeSince.",
    pattern=re.compile(
        rf"\b{_LAST_SEIZURE}\s+(?:was\s+)?(?P<count>\d+|{NUMBER_WORD_PATTERN})\s+"
        rf"(?P<unit>day|week|month|year)s?\s+ago\b",
        re.IGNORECASE,
    ),
    build=_build_last_seizure_ago,
    examples=(
        RuleExample(
            text="His last generalised seizure was 5 years ago.",
            expected_attributes={
                "NumberOfSeizures": "0", "NumberOfTimePeriods": "5", "TimePeriod": "Year",
            },
        ),
    ),
    provenance="Guideline Ex3 (L237): period-ago carries no TimeSince.",
)


# ---------------------------------------------------------------------------
# Ordered rule list. "last seizure" rules first so their richer (count=0 + date)
# extraction wins overlap resolution against the bare date rules; DMY/MY before
# month/year so the richest date wins.
# ---------------------------------------------------------------------------

TEMPORAL_RULES: list[RuleSpec] = [
    LAST_SEIZURE_DATE_RULE,
    LAST_SEIZURE_AGO_RULE,
    CHRISTMAS_SINCE_RULE,
    PIT_SINCE_RULE,
    DATE_DMY_RULE,
    DATE_MY_RULE,
    DATE_MONTH_RULE,
    DATE_YEAR_RULE,
]
