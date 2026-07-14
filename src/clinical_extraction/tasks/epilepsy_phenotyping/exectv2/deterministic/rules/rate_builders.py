"""Rate-expression builders and patterns for ExECTv2 (Stack A).

RuleSpec metadata lives in ``sf_surface_registry/catalog/extract.yaml``.
``adapters/extraction.py`` assembles ``RATE_RULES`` from catalog + this module.
"""

from __future__ import annotations

import re

from clinical_extraction.tasks.shared.epilepsy.terms import (
    NUMBER_VALUE_TOKEN,
    QUALIFIED_SEIZURE_TERMS,
)

from ..candidates import AttributeExtraction, AttributeKind
from ..normalizer import clean_span, normalize_count, normalize_unit
from ..rule_metadata import (
    ExtractionContext,
    Portability,
    RuleGroup,
)
from .extract_impl_types import ExtractRuleImpl

# ---------------------------------------------------------------------------
# Token fragments
# ---------------------------------------------------------------------------

_COUNT = NUMBER_VALUE_TOKEN  # single number (digit or word), no ranges
_UNIT = r"day|week|month|year|days|weeks|months|years"
_PER = r"per|a|each|every"

# Optional seizure type qualifier before the count: "3 focal seizures per month"
_SEQ_PREFIX = rf"(?:(?:{QUALIFIED_SEIZURE_TERMS}),?\s+)?"

# Dose units include the spelled-out and plural forms ("250 milligrams twice a
# day", "250mgs once a day") — the abbreviated-only list missed those and let
# medication dosing leak in as seizure frequency.
_DOSE_UNIT = r"mgs?|g|mcg|ml|microgram(?:me)?s?|milligram(?:me)?s?|gram(?:me)?s?|units?"


def _is_medication_dose_context(match: re.Match[str], context: ExtractionContext) -> bool:
    """True if the match looks like a medication dosing frequency, not a
    seizure frequency, e.g. "lamotrigine 75 mg twice a day"."""
    preceding = context.text[max(0, match.start() - 25) : match.start()]
    return bool(re.search(rf"\b\d+\s*(?:{_DOSE_UNIT})\b\W*$", preceding, re.IGNORECASE))


# A bare adverbial ("daily", "weekly") is only a seizure frequency when a seizure
# noun sits nearby — otherwise it fires on "daily headaches", "daily living", or
# a medication-titration "daily". Rate expressions that carry their own count and
# period are far less ambiguous, so this gate is applied to the adverbial rule only.
_SF_CONTEXT = re.compile(r"seizures?|absences?|jerks?|seizure[\s-]?free|fits?", re.IGNORECASE)
_HEADER_ANCHOR = (
    r"(?:[a-z][a-z\-]*\s+){0,8}(?:seizures?|absences?|jerks?)"
    r"(?:\s+with\s+(?:loss|altered|impaired)\s+(?:of\s+)?awareness)?"
)


def _adverbial_outside_seizure_context(match: re.Match[str], context: ExtractionContext) -> bool:
    lo = max(0, match.start() - 45)
    hi = min(len(context.text), match.end() + 20)
    return not _SF_CONTEXT.search(context.text[lo:hi])


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


def _build_count_per_period(match: re.Match[str], _ctx: ExtractionContext) -> AttributeExtraction:
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


# ---------------------------------------------------------------------------
# Rule 3: lower-upper per period  ("2-5 per month", "2 to 5 per week")
# ---------------------------------------------------------------------------

# Digit-only for range bounds (gold LowerNumberOfSeizures/UpperNumberOfSeizures are digits).
_DIGIT_OR_WORD = NUMBER_VALUE_TOKEN


def _build_range_per_period(match: re.Match[str], _ctx: ExtractionContext) -> AttributeExtraction:
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


def _build_between_range_per_period(
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
        rule_id="rate.between_range_per_period",
        rule_group=RuleGroup.RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
    )


def _build_range_of_seizure_terms(
    match: re.Match[str], _ctx: ExtractionContext
) -> AttributeExtraction:
    return _candidate(
        match,
        kind=AttributeKind.RATE,
        attributes=_attrs(
            lower=match.group("lower"),
            upper=match.group("upper"),
        ),
        rule_id="rate.range_of_seizure_terms",
        rule_group=RuleGroup.RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
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


# ---------------------------------------------------------------------------
# Rule 5: N times per/a/each period  ("3 times a week", "twice per month")
# ---------------------------------------------------------------------------


def _build_n_times_per_period(match: re.Match[str], _ctx: ExtractionContext) -> AttributeExtraction:
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


# ---------------------------------------------------------------------------
# Rule 5a: N per fortnight  ("1 per fortnight")
# ---------------------------------------------------------------------------


def _build_count_per_fortnight(
    match: re.Match[str], _ctx: ExtractionContext
) -> AttributeExtraction:
    return _candidate(
        match,
        kind=AttributeKind.RATE,
        attributes=_attrs(
            count=match.group("count"),
            period_count="2",
            unit="week",
        ),
        rule_id="rate.count_per_fortnight",
        rule_group=RuleGroup.RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
    )


# ---------------------------------------------------------------------------
# Rule 5b: header continuation rate
#          ("focal seizures (...)\n 1 per week")
# ---------------------------------------------------------------------------


def _build_header_continuation_rate(
    match: re.Match[str], _ctx: ExtractionContext
) -> AttributeExtraction:
    return _candidate(
        match,
        kind=AttributeKind.RATE,
        attributes=_attrs(
            count=match.group("count"),
            period_count="1",
            unit=match.group("unit"),
        ),
        rule_id="rate.header_continuation_rate",
        rule_group=RuleGroup.RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
    )


# ---------------------------------------------------------------------------
# Rule 5c: every lower-upper periods  ("every 3 to 4 weeks")
# ---------------------------------------------------------------------------


def _build_range_every_period(match: re.Match[str], _ctx: ExtractionContext) -> AttributeExtraction:
    return _candidate(
        match,
        kind=AttributeKind.RATE,
        attributes=_attrs(
            lower=match.group("lower"),
            upper=match.group("upper"),
            period_count="1",
            unit=match.group("unit"),
        ),
        rule_id="rate.range_every_period",
        rule_group=RuleGroup.RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
    )


def _build_period_range(match: re.Match[str], _ctx: ExtractionContext) -> AttributeExtraction:
    return _candidate(
        match,
        kind=AttributeKind.RATE,
        attributes=_attrs(
            count="1",
            lower_period=match.group("lower_period"),
            upper_period=match.group("upper_period"),
            unit=match.group("unit"),
        ),
        rule_id="rate.period_range",
        rule_group=RuleGroup.RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
    )


# ---------------------------------------------------------------------------
# Rule 5d: every N periods  ("every 3 weeks", "every five years")
# ---------------------------------------------------------------------------


def _build_every_n_periods(match: re.Match[str], _ctx: ExtractionContext) -> AttributeExtraction:
    return _candidate(
        match,
        kind=AttributeKind.RATE,
        attributes=_attrs(
            count="1",
            period_count=match.group("period_count"),
            unit=match.group("unit"),
        ),
        rule_id="rate.every_n_periods",
        rule_group=RuleGroup.RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
    )


# ---------------------------------------------------------------------------
# Rule 5e: every period  ("every month", "every year")
# ---------------------------------------------------------------------------


def _build_every_period(match: re.Match[str], _ctx: ExtractionContext) -> AttributeExtraction:
    return _candidate(
        match,
        kind=AttributeKind.RATE,
        attributes=_attrs(
            count="1",
            period_count="1",
            unit=match.group("unit"),
        ),
        rule_id="rate.every_period",
        rule_group=RuleGroup.RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
    )


# ---------------------------------------------------------------------------
# Rule 5f: several times per period
# ---------------------------------------------------------------------------


def _build_several_times_per_period(
    match: re.Match[str], _ctx: ExtractionContext
) -> AttributeExtraction:
    return _candidate(
        match,
        kind=AttributeKind.RATE,
        attributes=_attrs(
            count="2",
            period_count="1",
            unit=match.group("unit"),
        ),
        rule_id="rate.several_times_per_period",
        rule_group=RuleGroup.RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
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


def _build_adverbial(match: re.Match[str], _ctx: ExtractionContext) -> AttributeExtraction:
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
            # No TimeSince: "in the last N months" is a time *period*, not a date
            # or point-in-time. Guideline D9/Ex3 (L231/L237): TimeSince is set
            # only with a date or named point-in-time, never a bare period.
        ),
        rule_id="rate.count_in_last_period",
        rule_group=RuleGroup.RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
    )


# ---------------------------------------------------------------------------
# Rule 8: N over M periods  ("5 over 3 months" — without last/past qualifier)
# ---------------------------------------------------------------------------


def _build_count_over_period(match: re.Match[str], _ctx: ExtractionContext) -> AttributeExtraction:
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


def _build_range_over_period(match: re.Match[str], _ctx: ExtractionContext) -> AttributeExtraction:
    return _candidate(
        match,
        kind=AttributeKind.RATE,
        attributes=_attrs(
            lower=match.group("lower"),
            upper=match.group("upper"),
            unit=match.group("unit"),
            period_count=match.group("period_count"),
        ),
        rule_id="rate.range_over_period",
        rule_group=RuleGroup.RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
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
    preceding = context.text[max(0, match.start() - 6) : match.start()]
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


# ---------------------------------------------------------------------------
# Rule 10: article count  ("a seizure", "an absence")
# Supplies NumberOfSeizures=1 for dated/point-in-time mentions where the count is
# expressed by the indefinite article rather than a digit/number word.
# ---------------------------------------------------------------------------


def _build_article_count(match: re.Match[str], _ctx: ExtractionContext) -> AttributeExtraction:
    return _candidate(
        match,
        kind=AttributeKind.RATE,
        attributes=_attrs(count="1"),
        rule_id="rate.article_seizure_count",
        rule_group=RuleGroup.RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
    )


RATE_EXTRACT_IMPLS: dict[str, ExtractRuleImpl] = {
    "rate.range_per_n_periods": ExtractRuleImpl(
        re.compile(
            "\\b(?:(?:(?:[a-z][a-z\\-‑–—]*\\s+){0,4}(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)),?\\s+)?(?P<lower>(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few))\\s*[-–—]\\s*(?P<upper>(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few))\\s+(?:(?:(?:[a-z][a-z\\-‑–—]*\\s+){0,4}(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)|times?)\\s+)?per\\s+(?P<period_count>\\d+)\\s+(?P<unit>day|week|month|year|days|weeks|months|years)\\b",
            re.IGNORECASE,
        ),
        _build_range_per_n_periods,
    ),
    "rate.range_per_period": ExtractRuleImpl(
        re.compile(
            "\\b(?:(?:(?:[a-z][a-z\\-‑–—]*\\s+){0,4}(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)),?\\s+)?(?P<lower>(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few))\\s*[-–—]\\s*(?P<upper>(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few))\\s+(?:(?:(?:[a-z][a-z\\-‑–—]*\\s+){0,4}(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)|times?)\\s+)?(?:per|a|each|every)\\s+(?P<unit>day|week|month|year|days|weeks|months|years)\\b",
            re.IGNORECASE,
        ),
        _build_range_per_period,
    ),
    "rate.range_to_per_period": ExtractRuleImpl(
        re.compile(
            "\\b(?:(?:(?:[a-z][a-z\\-‑–—]*\\s+){0,4}(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)),?\\s+)?(?P<lower>(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few))\\s+(?:to|or)\\s+(?P<upper>(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few))\\s+(?:(?:(?:[a-z][a-z\\-‑–—]*\\s+){0,4}(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)|times?)\\s+)?(?:per|a|each|every)\\s+(?P<unit>day|week|month|year|days|weeks|months|years)\\b",
            re.IGNORECASE,
        ),
        _build_range_to_per_period,
    ),
    "rate.between_range_per_period": ExtractRuleImpl(
        re.compile(
            "\\bbetween\\s+(?P<lower>(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few))\\s+and\\s+(?P<upper>(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few))\\s+(?:(?:(?:[a-z][a-z\\-‑–—]*\\s+){0,4}(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)|times?)\\s+)?(?:per|a|each|every)\\s+(?P<unit>day|week|month|year|days|weeks|months|years)\\b",
            re.IGNORECASE,
        ),
        _build_between_range_per_period,
    ),
    "rate.range_of_seizure_terms": ExtractRuleImpl(
        re.compile(
            "\\b(?P<lower>(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few))\\s+(?:to|or)\\s+(?P<upper>(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few))\\s+of\\s+(?:his|her|their|the)?\\s*(?:(?:[a-z][a-z\\-‑–—]*\\s+){0,4}(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus))\\b",
            re.IGNORECASE,
        ),
        _build_range_of_seizure_terms,
    ),
    "rate.count_per_n_periods": ExtractRuleImpl(
        re.compile(
            "\\b(?:(?:(?:[a-z][a-z\\-‑–—]*\\s+){0,4}(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)),?\\s+)?(?P<count>(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few))\\s+per\\s+(?P<period_count>\\d+)\\s+(?P<unit>day|week|month|year|days|weeks|months|years)\\b",
            re.IGNORECASE,
        ),
        _build_count_per_n_periods,
    ),
    "rate.count_in_last_period": ExtractRuleImpl(
        re.compile(
            "\\b(?:(?:(?:[a-z][a-z\\-‑–—]*\\s+){0,4}(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)),?\\s+)?(?P<count>(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few))\\s+(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)?\\s*(?:in|over)\\s+(?:the\\s+)?(?:last|past)\\s+(?:(?P<period_count>\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few)\\s+)?(?P<unit>day|week|month|year|days|weeks|months|years)\\b",
            re.IGNORECASE,
        ),
        _build_count_in_last_period,
    ),
    "rate.range_over_period": ExtractRuleImpl(
        re.compile(
            "\\b(?:(?:(?:[a-z][a-z\\-‑–—]*\\s+){0,4}(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)),?\\s+)?(?P<lower>(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few))\\s*[-–—]\\s*(?P<upper>(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few))\\s+(?:of\\s+(?:these\\s+)?(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)\\s+)?over\\s+(?P<period_count>\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few)\\s+(?P<unit>day|week|month|year|days|weeks|months|years)\\b",
            re.IGNORECASE,
        ),
        _build_range_over_period,
    ),
    "rate.count_over_period": ExtractRuleImpl(
        re.compile(
            "\\b(?:(?:(?:[a-z][a-z\\-‑–—]*\\s+){0,4}(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)),?\\s+)?(?P<count>(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few))\\s+(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)?\\s*over\\s+(?P<period_count>\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few)\\s+(?P<unit>day|week|month|year|days|weeks|months|years)\\b",
            re.IGNORECASE,
        ),
        _build_count_over_period,
    ),
    "rate.count_per_period": ExtractRuleImpl(
        re.compile(
            "\\b(?:(?:(?:[a-z][a-z\\-‑–—]*\\s+){0,4}(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)),?\\s+)?(?P<count>(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few))\\s+(?:(?:(?:[a-z][a-z\\-‑–—]*\\s+){0,4}(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus))\\s+)?(?:per|a|each|every)\\s+(?P<unit>day|week|month|year|days|weeks|months|years)\\b",
            re.IGNORECASE,
        ),
        _build_count_per_period,
        exclude=(_is_medication_dose_context,),
    ),
    "rate.count_per_fortnight": ExtractRuleImpl(
        re.compile(
            "\\b(?:(?:(?:[a-z][a-z\\-‑–—]*\\s+){0,4}(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)),?\\s+)?(?P<count>(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few))\\s+(?:(?:(?:[a-z][a-z\\-‑–—]*\\s+){0,4}(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus))\\s+)?(?:per|a|each|every)\\s+fortnights?\\b",
            re.IGNORECASE,
        ),
        _build_count_per_fortnight,
        exclude=(_is_medication_dose_context,),
    ),
    "rate.header_continuation_rate": ExtractRuleImpl(
        re.compile(
            "\\b(?:(?:[a-z][a-z\\-]*\\s+){0,8}(?:seizures?|absences?|jerks?)(?:\\s+with\\s+(?:loss|altered|impaired)\\s+(?:of\\s+)?awareness)?)(?:\\s*\\([^)]{1,80}\\))?\\s*(?:\\r?\\n)[\\t ]*(?P<count>(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few))\\s+(?:(?:(?:[a-z][a-z\\-‑–—]*\\s+){0,4}(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)|times?)\\s+)?(?:per|a|each|every)\\s+(?P<unit>day|week|month|year|days|weeks|months|years)\\b",
            re.IGNORECASE,
        ),
        _build_header_continuation_rate,
        exclude=(_is_medication_dose_context,),
    ),
    "rate.n_times_per_period": ExtractRuleImpl(
        re.compile(
            "\\b(?:(?:(?:[a-z][a-z\\-‑–—]*\\s+){0,4}(?:seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|jerks?|auras?|status epilepticus)),?\\s+)?(?P<count>(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few))\\s+times?\\s+(?:per|a|each|every)\\s+(?P<unit>day|week|month|year|days|weeks|months|years)\\b",
            re.IGNORECASE,
        ),
        _build_n_times_per_period,
        exclude=(_is_medication_dose_context,),
    ),
    "rate.range_every_period": ExtractRuleImpl(
        re.compile(
            "\\b(?P<lower>(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few))\\s+(?:to|or)\\s+(?P<upper>(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few))\\s+(?:per|a|each|every)\\s+(?P<unit>day|week|month|year|days|weeks|months|years)\\b",
            re.IGNORECASE,
        ),
        _build_range_every_period,
    ),
    "rate.period_range": ExtractRuleImpl(
        re.compile(
            "\\bevery\\s+(?P<lower_period>(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few))\\s+(?:to|or)\\s+(?P<upper_period>(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few))\\s+(?P<unit>days?|weeks?|months?|years?)\\b",
            re.IGNORECASE,
        ),
        _build_period_range,
    ),
    "rate.every_n_periods": ExtractRuleImpl(
        re.compile(
            "\\bevery\\s+(?P<period_count>(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few))\\s+(?P<unit>day|week|month|year|days|weeks|months|years)\\b",
            re.IGNORECASE,
        ),
        _build_every_n_periods,
        exclude=(_adverbial_outside_seizure_context,),
    ),
    "rate.every_period": ExtractRuleImpl(
        re.compile(
            "\\bevery\\s+(?P<unit>day|week|month|year|days|weeks|months|years)\\b", re.IGNORECASE
        ),
        _build_every_period,
        exclude=(_adverbial_outside_seizure_context,),
    ),
    "rate.several_times_per_period": ExtractRuleImpl(
        re.compile(
            "\\bseveral\\s+times?\\s+(?:per|a|each|every)\\s+(?P<unit>day|week|month|year|days|weeks|months|years)\\b",
            re.IGNORECASE,
        ),
        _build_several_times_per_period,
    ),
    "rate.adverbial": ExtractRuleImpl(
        re.compile(
            "\\b(?:(?P<mult>(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few))\\s+(?:times?\\s+)?)?(?P<adv>daily|weekly|monthly|fortnightly|annually|yearly)\\b",
            re.IGNORECASE,
        ),
        _build_adverbial,
        exclude=(
            _is_medication_dose_context,
            _adverbial_outside_seizure_context,
        ),
    ),
    "rate.bare_count": ExtractRuleImpl(
        re.compile(
            "\\b(?P<count>(?:multiple|\\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|single|once|twice|thrice|several|few))\\s+(?:[a-z][a-z\\-]*\\s+){0,3}?(?:seizures?|absences?|jerks?)\\b",
            re.IGNORECASE,
        ),
        _build_bare_count,
        exclude=(
            _is_medication_dose_context,
            _is_range_continuation,
        ),
    ),
    "rate.article_seizure_count": ExtractRuleImpl(
        re.compile(
            "\\b(?:a|an)\\s+(?:[a-z][a-z\\-]*\\s+){0,4}?(?:seizures?|absences?|jerks?)\\b",
            re.IGNORECASE,
        ),
        _build_article_count,
    ),
}
