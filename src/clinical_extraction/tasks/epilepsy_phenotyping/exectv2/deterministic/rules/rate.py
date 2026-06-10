"""Seizure-frequency rate extraction rules for ExECTv2.

Covers: N per/a/each period, N per N periods, lower-upper per period,
twice-daily/weekly/monthly adverbials, N times per period, and
count-in-last-period historical forms.

Each rule produces an AttributeExtraction with SeizureFrequency attributes,
to be merged onto the nearest anchor phrase by association. Gold mentions
almost never carry an explicit ``Negation`` key (it is implicitly Affirmed),
so these rules leave it absent; CUI/CUIPhrase/Certainty are also left absent
(scored with an extended ignore set in the runner).
"""
from __future__ import annotations

import re

from clinical_extraction.tasks.shared.epilepsy.terms import (
    NUMBER_VALUE_TOKEN,
    NUMBER_WORD_PATTERN,
    QUALIFIED_SEIZURE_TERMS,
    SEIZURE_TERMS,
)

from ..candidates import AttributeExtraction, AttributeKind
from ..normalizer import clean_span, normalize_count, normalize_unit
from ..rule_metadata import (
    AblationConfig,
    ExtractionContext,
    Portability,
    RuleExample,
    RuleGroup,
    RuleSpec,
)

# ---------------------------------------------------------------------------
# Token fragments
# ---------------------------------------------------------------------------

_COUNT = NUMBER_VALUE_TOKEN   # single number (digit or word), no ranges
_UNIT = r"day|week|month|year|days|weeks|months|years"
_PER = r"per|a|each|every"

# Optional seizure type qualifier before the count: "3 focal seizures per month"
_SEQ_PREFIX = rf"(?:(?:{QUALIFIED_SEIZURE_TERMS}),?\s+)?"

_DOSE_UNIT = r"mg|g|mcg|ml|micrograms?"


def _is_medication_dose_context(match: re.Match[str], context: ExtractionContext) -> bool:
    """True if the match looks like a medication dosing frequency, not a
    seizure frequency, e.g. "lamotrigine 75 mg twice a day"."""
    preceding = context.text[max(0, match.start() - 25): match.start()]
    return bool(re.search(rf"\b\d+\s*(?:{_DOSE_UNIT})\b\W*$", preceding, re.IGNORECASE))


def _attrs(
    *,
    count: str | None = None,
    lower: str | None = None,
    upper: str | None = None,
    period_count: str | None = None,
    lower_period: str | None = None,
    upper_period: str | None = None,
    unit: str | None = None,
    time_since: str | None = None,
) -> dict[str, str]:
    d: dict[str, str] = {}
    if count is not None:
        d["NumberOfSeizures"] = normalize_count(count)
    if lower is not None:
        d["LowerNumberOfSeizures"] = normalize_count(lower)
    if upper is not None:
        d["UpperNumberOfSeizures"] = normalize_count(upper)
    if period_count is not None:
        d["NumberOfTimePeriods"] = normalize_count(period_count)
    if lower_period is not None:
        d["LowerNumberOfTimePeriods"] = normalize_count(lower_period)
    if upper_period is not None:
        d["UpperNumberOfTimePeriods"] = normalize_count(upper_period)
    if unit is not None:
        d["TimePeriod"] = normalize_unit(unit)
    if time_since is not None:
        d["TimeSince_or_TimeOfEvent"] = time_since
    return d


def _candidate(
    match: re.Match[str],
    kind: AttributeKind,
    attributes: dict[str, str],
    rule_id: str,
    rule_group: RuleGroup,
    portability: Portability,
) -> AttributeExtraction:
    evidence = clean_span(match.group(0))
    return AttributeExtraction(
        evidence=evidence,
        span=(match.start(), match.end()),
        attributes=attributes,
        kind=kind,
        rule_id=rule_id,
        rule_group=rule_group,
        portability=portability,
    )


# ---------------------------------------------------------------------------
# Rule 1: N per/a/each/every period  ("3 per month", "2 a week")
# ---------------------------------------------------------------------------

def _build_count_per_period(
    match: re.Match[str], _ctx: ExtractionContext
) -> AttributeExtraction:
    return _candidate(
        match,
        kind=AttributeKind.RATE,
        attributes=_attrs(
            count=match.group("count"),
            unit=match.group("unit"),
            period_count="1",
        ),
        rule_id="rate.count_per_period",
        rule_group=RuleGroup.RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
    )


COUNT_PER_PERIOD_RULE = RuleSpec(
    rule_id="rate.count_per_period",
    group=RuleGroup.RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="N per/a/each/every period — exact seizure count in one period.",
    pattern=re.compile(
        rf"\b{_SEQ_PREFIX}"
        rf"(?P<count>{_COUNT})\s+(?:(?:{QUALIFIED_SEIZURE_TERMS})\s+)?(?:{_PER})\s+(?P<unit>{_UNIT})\b",
        re.IGNORECASE,
    ),
    build=_build_count_per_period,
    exclude=(_is_medication_dose_context,),
    examples=(
        RuleExample(
            text="Seizure type and frequency: 3 per month.",
            expected_evidence="3 per month",
            expected_attributes={"NumberOfSeizures": "3", "NumberOfTimePeriods": "1", "TimePeriod": "Month"},
        ),
        RuleExample(
            text="Patient experiences 2 episodes a week.",
            expected_evidence="2 episodes a week",
            expected_attributes={"NumberOfSeizures": "2", "NumberOfTimePeriods": "1", "TimePeriod": "Week"},
        ),
    ),
    provenance="Portable SF rate expression.",
)


# ---------------------------------------------------------------------------
# Rule 2: N per N periods  ("3 per 2 months")
# ---------------------------------------------------------------------------

def _build_count_per_n_periods(
    match: re.Match[str], _ctx: ExtractionContext
) -> AttributeExtraction:
    return _candidate(
        match,
        kind=AttributeKind.RATE,
        attributes=_attrs(
            count=match.group("count"),
            unit=match.group("unit"),
            period_count=match.group("period_count"),
        ),
        rule_id="rate.count_per_n_periods",
        rule_group=RuleGroup.RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
    )


COUNT_PER_N_PERIODS_RULE = RuleSpec(
    rule_id="rate.count_per_n_periods",
    group=RuleGroup.RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="N per M periods — exact count over multiple periods.",
    pattern=re.compile(
        rf"\b{_SEQ_PREFIX}"
        rf"(?P<count>{_COUNT})\s+per\s+(?P<period_count>\d+)\s+(?P<unit>{_UNIT})\b",
        re.IGNORECASE,
    ),
    build=_build_count_per_n_periods,
    examples=(
        RuleExample(
            text="She has 3 seizures per 2 months.",
            expected_evidence="3 seizures per 2 months",
            expected_attributes={
                "NumberOfSeizures": "3",
                "NumberOfTimePeriods": "2",
                "TimePeriod": "Month",
            },
        ),
    ),
    provenance="Portable SF multi-period rate.",
)


# ---------------------------------------------------------------------------
# Rule 3: lower-upper per period  ("2-5 per month", "2 to 5 per week")
# ---------------------------------------------------------------------------

# Digit-only for range bounds (gold LowerNumberOfSeizures/UpperNumberOfSeizures are digits).
_DIGIT_OR_WORD = NUMBER_VALUE_TOKEN


def _build_range_per_period(
    match: re.Match[str], _ctx: ExtractionContext
) -> AttributeExtraction:
    return _candidate(
        match,
        kind=AttributeKind.RATE,
        attributes=_attrs(
            lower=match.group("lower"),
            upper=match.group("upper"),
            unit=match.group("unit"),
            period_count="1",
        ),
        rule_id="rate.range_per_period",
        rule_group=RuleGroup.RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
    )


RANGE_PER_PERIOD_RULE = RuleSpec(
    rule_id="rate.range_per_period",
    group=RuleGroup.RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="lower-upper per period — range count in one period.",
    pattern=re.compile(
        rf"\b{_SEQ_PREFIX}"
        rf"(?P<lower>{_DIGIT_OR_WORD})\s*[-–—]\s*(?P<upper>{_DIGIT_OR_WORD})"
        rf"\s+(?:{_PER})\s+(?P<unit>{_UNIT})\b",
        re.IGNORECASE,
    ),
    build=_build_range_per_period,
    examples=(
        RuleExample(
            text="Seizure type and frequency: 2-5 per month.",
            expected_evidence="2-5 per month",
            expected_attributes={
                "LowerNumberOfSeizures": "2",
                "UpperNumberOfSeizures": "5",
                "NumberOfTimePeriods": "1",
                "TimePeriod": "Month",
            },
        ),
    ),
    provenance="Portable SF range rate expression.",
)


def _build_range_to_per_period(
    match: re.Match[str], _ctx: ExtractionContext
) -> AttributeExtraction:
    return _candidate(
        match,
        kind=AttributeKind.RATE,
        attributes=_attrs(
            lower=match.group("lower"),
            upper=match.group("upper"),
            unit=match.group("unit"),
            period_count="1",
        ),
        rule_id="rate.range_to_per_period",
        rule_group=RuleGroup.RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
    )


RANGE_TO_PER_PERIOD_RULE = RuleSpec(
    rule_id="rate.range_to_per_period",
    group=RuleGroup.RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="lower to upper per period — range with 'to' in one period.",
    pattern=re.compile(
        rf"\b{_SEQ_PREFIX}"
        rf"(?P<lower>{_DIGIT_OR_WORD})\s+(?:to|or)\s+(?P<upper>{_DIGIT_OR_WORD})"
        rf"\s+(?:{_PER})\s+(?P<unit>{_UNIT})\b",
        re.IGNORECASE,
    ),
    build=_build_range_to_per_period,
    examples=(
        RuleExample(
            text="Focal onset seizures: 1 to 3 per week.",
            expected_evidence="1 to 3 per week",
            expected_attributes={
                "LowerNumberOfSeizures": "1",
                "UpperNumberOfSeizures": "3",
                "NumberOfTimePeriods": "1",
                "TimePeriod": "Week",
            },
        ),
    ),
    provenance="Portable SF range-to rate expression.",
)


# ---------------------------------------------------------------------------
# Rule 4: range per N periods  ("2-5 per 2 months")
# ---------------------------------------------------------------------------

def _build_range_per_n_periods(
    match: re.Match[str], _ctx: ExtractionContext
) -> AttributeExtraction:
    return _candidate(
        match,
        kind=AttributeKind.RATE,
        attributes=_attrs(
            lower=match.group("lower"),
            upper=match.group("upper"),
            unit=match.group("unit"),
            period_count=match.group("period_count"),
        ),
        rule_id="rate.range_per_n_periods",
        rule_group=RuleGroup.RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
    )


RANGE_PER_N_PERIODS_RULE = RuleSpec(
    rule_id="rate.range_per_n_periods",
    group=RuleGroup.RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="lower-upper per N periods — range count over multiple periods.",
    pattern=re.compile(
        rf"\b{_SEQ_PREFIX}"
        rf"(?P<lower>{_DIGIT_OR_WORD})\s*[-–—]\s*(?P<upper>{_DIGIT_OR_WORD})"
        rf"\s+per\s+(?P<period_count>\d+)\s+(?P<unit>{_UNIT})\b",
        re.IGNORECASE,
    ),
    build=_build_range_per_n_periods,
    examples=(
        RuleExample(
            text="She experiences 3-9 episodes per 3 months.",
            expected_evidence="3-9 episodes per 3 months",
            expected_attributes={
                "LowerNumberOfSeizures": "3",
                "UpperNumberOfSeizures": "9",
                "NumberOfTimePeriods": "3",
                "TimePeriod": "Month",
            },
        ),
    ),
    provenance="Portable SF multi-period range rate.",
)


# ---------------------------------------------------------------------------
# Rule 5: N times per/a/each period  ("3 times a week", "twice per month")
# ---------------------------------------------------------------------------

def _build_n_times_per_period(
    match: re.Match[str], _ctx: ExtractionContext
) -> AttributeExtraction:
    return _candidate(
        match,
        kind=AttributeKind.RATE,
        attributes=_attrs(
            count=match.group("count"),
            unit=match.group("unit"),
            period_count="1",
        ),
        rule_id="rate.n_times_per_period",
        rule_group=RuleGroup.RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
    )


N_TIMES_PER_PERIOD_RULE = RuleSpec(
    rule_id="rate.n_times_per_period",
    group=RuleGroup.RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="N times per/a/each period — explicit 'times' construction.",
    pattern=re.compile(
        rf"\b{_SEQ_PREFIX}"
        rf"(?P<count>{_COUNT})\s+times?\s+(?:{_PER})\s+(?P<unit>{_UNIT})\b",
        re.IGNORECASE,
    ),
    build=_build_n_times_per_period,
    exclude=(_is_medication_dose_context,),
    examples=(
        RuleExample(
            text="He has seizures 3 times per week.",
            expected_evidence="3 times per week",
            expected_attributes={"NumberOfSeizures": "3", "NumberOfTimePeriods": "1", "TimePeriod": "Week"},
        ),
        RuleExample(
            text="Episodes occur twice a month.",
            expected_evidence="twice a month",
            expected_attributes={"NumberOfSeizures": "2", "NumberOfTimePeriods": "1", "TimePeriod": "Month"},
        ),
    ),
    provenance="Portable SF times-per-period expression.",
)


# ---------------------------------------------------------------------------
# Rule 6: adverbial frequencies  (daily, weekly, monthly, fortnightly, ...)
# With optional multiplier: twice daily, three times weekly.
# ---------------------------------------------------------------------------

_ADVERB_MAP: dict[str, tuple[str, str, str]] = {
    # adverb → (count, period_count, TimePeriod)
    "daily": ("1", "1", "Day"),
    "weekly": ("1", "1", "Week"),
    "monthly": ("1", "1", "Month"),
    "fortnightly": ("1", "2", "Week"),
    "annually": ("1", "1", "Year"),
    "yearly": ("1", "1", "Year"),
}

_ADV_PATTERN = "|".join(_ADVERB_MAP)


def _build_adverbial(
    match: re.Match[str], _ctx: ExtractionContext
) -> AttributeExtraction:
    adv = match.group("adv").lower()
    raw_mult = match.group("mult")
    base_count, base_period_count, time_period = _ADVERB_MAP[adv]
    if raw_mult:
        count = normalize_count(raw_mult.strip())
    else:
        count = base_count
    return _candidate(
        match,
        kind=AttributeKind.RATE,
        attributes=_attrs(
            count=count,
            period_count=base_period_count,
            unit=time_period.lower(),
        ),
        rule_id="rate.adverbial",
        rule_group=RuleGroup.RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
    )


ADVERBIAL_RULE = RuleSpec(
    rule_id="rate.adverbial",
    group=RuleGroup.RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Adverbial frequency: daily/weekly/monthly/fortnightly, optionally with multiplier.",
    pattern=re.compile(
        rf"\b(?:(?P<mult>{_COUNT})\s+(?:times?\s+)?)?(?P<adv>{_ADV_PATTERN})\b",
        re.IGNORECASE,
    ),
    build=_build_adverbial,
    exclude=(_is_medication_dose_context,),
    examples=(
        RuleExample(
            text="She experiences absence seizures daily.",
            expected_evidence="daily",
            expected_attributes={"NumberOfSeizures": "1", "NumberOfTimePeriods": "1", "TimePeriod": "Day"},
        ),
        RuleExample(
            text="Tonic-clonic seizures: twice weekly.",
            expected_evidence="twice weekly",
            expected_attributes={"NumberOfSeizures": "2", "NumberOfTimePeriods": "1", "TimePeriod": "Week"},
        ),
        RuleExample(
            text="Cluster events occur fortnightly.",
            expected_evidence="fortnightly",
            expected_attributes={"NumberOfSeizures": "1", "NumberOfTimePeriods": "2", "TimePeriod": "Week"},
        ),
    ),
    provenance="Portable SF adverbial frequency.",
)


# ---------------------------------------------------------------------------
# Rule 7: N seizures in/over the last/past M period(s)
#          ("3 in the last month", "5 over the past 3 months")
# ---------------------------------------------------------------------------

def _build_count_in_last_period(
    match: re.Match[str], _ctx: ExtractionContext
) -> AttributeExtraction:
    period_count = match.group("period_count") or "1"
    return _candidate(
        match,
        kind=AttributeKind.RATE,
        attributes=_attrs(
            count=match.group("count"),
            unit=match.group("unit"),
            period_count=period_count,
            time_since="Since",
        ),
        rule_id="rate.count_in_last_period",
        rule_group=RuleGroup.RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
    )


COUNT_IN_LAST_PERIOD_RULE = RuleSpec(
    rule_id="rate.count_in_last_period",
    group=RuleGroup.RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="N events in/over the last M period — historical count with Since.",
    pattern=re.compile(
        rf"\b{_SEQ_PREFIX}"
        rf"(?P<count>{_COUNT})\s+(?:{SEIZURE_TERMS})?\s*"
        rf"(?:in|over)\s+(?:the\s+)?(?:last|past)\s+"
        rf"(?:(?P<period_count>\d+|{NUMBER_WORD_PATTERN})\s+)?(?P<unit>{_UNIT})\b",
        re.IGNORECASE,
    ),
    build=_build_count_in_last_period,
    examples=(
        RuleExample(
            text="She had 3 seizures in the last month.",
            expected_evidence="3 seizures in the last month",
            expected_attributes={
                "NumberOfSeizures": "3",
                "NumberOfTimePeriods": "1",
                "TimePeriod": "Month",
                "TimeSince_or_TimeOfEvent": "Since",
            },
        ),
        RuleExample(
            text="He reported 5 episodes over the past 3 months.",
            expected_evidence="5 episodes over the past 3 months",
            expected_attributes={
                "NumberOfSeizures": "5",
                "NumberOfTimePeriods": "3",
                "TimePeriod": "Month",
                "TimeSince_or_TimeOfEvent": "Since",
            },
        ),
    ),
    provenance="Portable SF historical count expression.",
)


# ---------------------------------------------------------------------------
# Rule 8: N over M periods  ("5 over 3 months" — without last/past qualifier)
# ---------------------------------------------------------------------------

def _build_count_over_period(
    match: re.Match[str], _ctx: ExtractionContext
) -> AttributeExtraction:
    return _candidate(
        match,
        kind=AttributeKind.RATE,
        attributes=_attrs(
            count=match.group("count"),
            unit=match.group("unit"),
            period_count=match.group("period_count"),
        ),
        rule_id="rate.count_over_period",
        rule_group=RuleGroup.RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
    )


COUNT_OVER_PERIOD_RULE = RuleSpec(
    rule_id="rate.count_over_period",
    group=RuleGroup.RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="N over M periods — count spread over a period (no last/past).",
    pattern=re.compile(
        rf"\b{_SEQ_PREFIX}"
        rf"(?P<count>{_COUNT})\s+(?:{SEIZURE_TERMS})?\s*"
        rf"over\s+(?P<period_count>\d+|{NUMBER_WORD_PATTERN})\s+(?P<unit>{_UNIT})\b",
        re.IGNORECASE,
    ),
    build=_build_count_over_period,
    examples=(
        RuleExample(
            text="She had 5 seizures over 3 months.",
            expected_evidence="5 seizures over 3 months",
            expected_attributes={"NumberOfSeizures": "5", "NumberOfTimePeriods": "3", "TimePeriod": "Month"},
        ),
    ),
    provenance="Portable SF count-over-period expression.",
)


# ---------------------------------------------------------------------------
# Rule 9: bare seizure count  ("5 seizures", "3 focal seizures") with no period.
# Supplies NumberOfSeizures for date/point-in-time mentions ("5 seizures in
# May", "3 seizures since last clinic") where the count is not part of a
# per-period rate. Overlap resolution drops it whenever a richer rate/range rule
# covers the same span.
# ---------------------------------------------------------------------------

_SF_COUNT_NOUN = r"seizures?|absences?|jerks?"


def _is_range_continuation(match: re.Match[str], context: ExtractionContext) -> bool:
    """True if the count is the upper bound of a range ("2 to 3 seizures",
    "2-5 seizures") — let the range rules own it, not the bare-count rule."""
    preceding = context.text[max(0, match.start() - 6): match.start()]
    return bool(re.search(r"(?:\bto|\bor|[-–—])\s*$", preceding, re.IGNORECASE))


def _build_bare_count(match: re.Match[str], _ctx: ExtractionContext) -> AttributeExtraction:
    return _candidate(
        match,
        kind=AttributeKind.RATE,
        attributes=_attrs(count=match.group("count")),
        rule_id="rate.bare_count",
        rule_group=RuleGroup.RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
    )


BARE_COUNT_RULE = RuleSpec(
    rule_id="rate.bare_count",
    group=RuleGroup.RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="N <seizure noun> with no period — bare seizure count.",
    pattern=re.compile(
        rf"\b(?P<count>{_COUNT})\s+(?:[a-z][a-z\-]*\s+){{0,3}}?(?:{_SF_COUNT_NOUN})\b",
        re.IGNORECASE,
    ),
    build=_build_bare_count,
    exclude=(_is_medication_dose_context, _is_range_continuation),
    examples=(
        RuleExample(
            text="He had 5 seizures in May.",
            expected_evidence="5 seizures",
            expected_attributes={"NumberOfSeizures": "5"},
        ),
        RuleExample(
            text="She had 3 focal seizures since her last clinic.",
            expected_evidence="3 focal seizures",
            expected_attributes={"NumberOfSeizures": "3"},
        ),
    ),
    provenance="Supplies NumberOfSeizures for temporal SF mentions.",
)


# ---------------------------------------------------------------------------
# Ordered rule list (order matters for overlap resolution priority)
# ---------------------------------------------------------------------------

RATE_RULES: list[RuleSpec] = [
    # Range rules before count rules so "2-5 per month" → range, not "5 per month"
    RANGE_PER_N_PERIODS_RULE,
    RANGE_PER_PERIOD_RULE,
    RANGE_TO_PER_PERIOD_RULE,
    COUNT_PER_N_PERIODS_RULE,
    COUNT_IN_LAST_PERIOD_RULE,
    COUNT_OVER_PERIOD_RULE,
    COUNT_PER_PERIOD_RULE,
    N_TIMES_PER_PERIOD_RULE,
    ADVERBIAL_RULE,
    BARE_COUNT_RULE,
]
