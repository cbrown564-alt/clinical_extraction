from __future__ import annotations

import re

from clinical_extraction.tasks.seizure_frequency.gan2026.selected_evidence_text import (
    format_prediction_rate as _format_prediction_rate,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.selected_evidence_text import (
    words_to_numbers as _words_to_numbers,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.selected_evidence_window import (
    elapsed_months_in_year_context,
)

UNIT_SYNONYMS = {
    "d": "day",
    "day": "day",
    "days": "day",
    "w": "week",
    "wk": "week",
    "wks": "week",
    "week": "week",
    "weeks": "week",
    "mo": "month",
    "mon": "month",
    "mons": "month",
    "mos": "month",
    "month": "month",
    "months": "month",
    "y": "year",
    "yr": "year",
    "yr.": "year",
    "yrs": "year",
    "year": "year",
    "years": "year",
}

_UNIT = r"day|week|month|year"
_COUNT = r"\d+(?:\s*(?:to|-|–|—|or)\s*\d+)?"


def early_rate_label_from_selected_evidence(text: str) -> str | None:
    """Derive selected-evidence rate labels that should run before cluster parsing."""
    q_interval = _q_interval_label_from_selected_evidence(text)
    if q_interval:
        return q_interval

    median_interval = _median_interval_label_from_selected_evidence(text)
    if median_interval:
        return median_interval

    if evidence_describes_current_non_epileptic_events(text):
        return "seizure free for multiple year"

    upper_bound = re.search(
        rf"(?:≤|<=|up to|at most|no more than)\s+(?P<count>{_COUNT})\s+"
        rf"(?:seizures?\s+)?per\s+(?P<unit>{_UNIT})s?\b",
        text,
    )
    if upper_bound:
        return _format_prediction_rate(upper_bound.group("count"), upper_bound.group("unit"))
    upper_bound_in_weeks = re.search(
        rf"(?:≤|<=|up to|at most|no more than)\s+(?P<count>{_COUNT})\s+"
        r"(?:[a-z]+(?:-[a-z]+)?\s+){0,4}"
        r"\bin\s+(?:bad\s+|flare\s+)?weeks?\b",
        text,
    )
    if upper_bound_in_weeks:
        return _format_prediction_rate(upper_bound_in_weeks.group("count"), "week")

    if re.search(r"\bbimonthly\b", text):
        return _format_prediction_rate("1 per 2", "month")
    every_other = re.search(rf"\bevery\s+other\s+(?P<unit>{_UNIT})\b", text)
    if every_other:
        return _format_prediction_rate("1 per 2", every_other.group("unit"))
    no_definite_recent = re.search(
        r"\bno\s+definite\s+epileptic\s+events?\b.*\b(?:past|last|this)\s+"
        rf"(?:(?P<count>\d+)\s+)?(?P<unit>{_UNIT})s?\b",
        text,
    )
    if no_definite_recent:
        count_text = no_definite_recent.group("count") or "multiple"
        return f"seizure free for {count_text} {no_definite_recent.group('unit')}"

    days_per_week = re.search(
        rf"\b(?:occurring|occur|events?|seizures?|spells?)\b.{0,60}"
        rf"\b(?:on\s+)?(?P<count>{_COUNT})\s+days?\s+of\s+the\s+week\b",
        text,
    )
    if not days_per_week:
        days_per_week = re.search(
            rf"\b(?P<count>{_COUNT})\s+days?\s+per\s+week\b",
            text,
        )
    if days_per_week:
        return _format_prediction_rate(days_per_week.group("count"), "week")

    return None


def pre_window_rate_label_from_selected_evidence(text: str) -> str | None:
    """Derive non-cluster rate labels that should run before count-window parsing."""
    yesterday = re.search(
        r"\b\d+\s+(?!(?:day|week|month|year)s?\b)"
        r"(?=(?:[a-z]+(?:-[a-z]+)?\s+){0,4}"
        r"(?:seizure|attack|convulsion|spasm|mal|event)).*\byesterday\b",
        text,
    )
    if yesterday:
        return _format_prediction_rate("1", "day")

    compact_daily = re.search(r"\b1\s*/\s*d\b", text)
    if compact_daily:
        return _format_prediction_rate("1", "day")

    return None


def late_rate_label_from_selected_evidence(
    text: str,
    context_text: str | None = None,
) -> str | None:
    """Derive selected-evidence rate labels that should run after count-window parsing."""
    slash_week = re.search(
        r"\b(?P<count>\d+)\s*/\s*7\b",
        text,
    )
    if slash_week:
        return _format_prediction_rate(slash_week.group("count"), "week")
    slash_month = re.search(
        r"\b(?P<count>\d+)\s*/\s*30\b.*\b(?:this|past|last)\s+month\b",
        text,
    )
    if slash_month:
        return _format_prediction_rate(slash_month.group("count"), "month")
    fortnight = re.search(
        rf"\b(?P<count>{_COUNT})\s+(?:[a-z]+(?:-[a-z]+)?\s+){{0,4}}"
        r"(?:over|in|during|for)?\s*(?:the\s+)?(?:past|last)\s+fortnight\b",
        text,
    )
    if not fortnight:
        fortnight = re.search(
            r"\b(?:past|last)\s+fortnight\b.*?"
            rf"\b(?P<count>{_COUNT})\s+(?:[a-z]+(?:-[a-z]+)?\s+){{0,4}}"
            r"(?:seizure|attack|convulsion|spasm|event|episode)",
            text,
        )
    if fortnight:
        return _format_prediction_rate(f"{fortnight.group('count')} per 2", "week")

    monthly_shorthand = re.search(
        rf"\b(?P<count>{_COUNT})\s+(?:[a-z]+\s+){{0,4}}monthly\b",
        text,
    )
    if monthly_shorthand:
        return _format_prediction_rate(monthly_shorthand.group("count"), "month")

    single_last_period = re.search(
        rf"\b(?:single|1)\b.*\b(?:last|past)\s+(?P<unit>{_UNIT})\b",
        text,
    )
    if single_last_period:
        return _format_prediction_rate("1", single_last_period.group("unit"))

    quarter = re.search(
        rf"\b(?P<count>{_COUNT})\s+(?:seizures?\s+)?per\s+quarter\b",
        text,
    )
    if quarter:
        return _format_prediction_rate(quarter.group("count"), "3 month")
    this_quarter = re.search(
        rf"\b(?P<count>{_COUNT})\s+(?:[a-z]+(?:-[a-z]+)?\s+){{0,4}}"
        r"(?:this|past|last)\s+quarter\b",
        text,
    )
    if this_quarter:
        return _format_prediction_rate(this_quarter.group("count"), "3 month")

    this_year = re.search(
        rf"\b(?P<count>{_COUNT})\s+(?:[a-z]+(?:-[a-z]+)?\s+){{0,4}}"
        r"(?:this|past|last)\s+year\b",
        text,
    )
    if this_year:
        elapsed_months = elapsed_months_in_year_context(context_text)
        if elapsed_months:
            return _format_prediction_rate(
                f"{this_year.group('count')} per {elapsed_months}",
                "month",
            )
        return _format_prediction_rate(this_year.group("count"), "year")
    year_to_date = re.search(
        rf"\b(?P<count>{_COUNT})\s+(?:[a-z]+(?:-[a-z]+)?\s+){{0,5}}"
        r"(?:so\s+far\s+this\s+year|this\s+year\s+to\s+date|"
        r"\d{4}\s+so\s+far)\b",
        text,
    )
    if year_to_date:
        elapsed_months = elapsed_months_in_year_context(context_text)
        if elapsed_months:
            return _format_prediction_rate(
                f"{year_to_date.group('count')} per {elapsed_months}",
                "month",
            )
        return _format_prediction_rate(year_to_date.group("count"), "year")

    daily = daily_label_from_selected_evidence(text)
    if daily:
        return daily

    times_every = re.search(
        rf"\b(?P<count>\d+)\s+(?:times|seizures?)?\s*every\s+"
        rf"(?P<period>\d+)\s+(?P<unit>{_UNIT})s?\b",
        text,
    )
    if times_every:
        return _format_prediction_rate(
            f"{times_every.group('count')} per {times_every.group('period')}",
            times_every.group("unit"),
        )

    every_range = re.search(
        rf"\bevery\s+(?P<count>{_COUNT})\s+(?P<unit>{_UNIT})s?\b",
        text,
    )
    if every_range:
        return _format_prediction_rate(
            f"1 per {every_range.group('count')}",
            every_range.group("unit"),
        )

    interval_range = re.search(
        rf"\bintervals?\s+ranging\s+(?P<count>{_COUNT})\s+"
        rf"(?P<unit>{_UNIT})s?\b",
        text,
    )
    if interval_range:
        return _format_prediction_rate(
            f"1 per {interval_range.group('count')}",
            interval_range.group("unit"),
        )

    return None


def daily_label_from_selected_evidence(text: str) -> str | None:
    if re.search(r"\b(?:no|without)\b.{0,80}\b(?:events?|spells?|seizures?)\b", text):
        return None
    if re.search(r"\bdaily\s+(?:entries|diary|logs?)\b", text):
        return None
    if re.search(
        r"\b(?:dozens?|scores?)\b.{0,30}\b(?:in|per|each|a)\s+(?:day|24\s*hours?)\b",
        text,
    ):
        return "multiple per day"
    if re.search(
        r"\b(?:multiple|several|many|daily)\b.{0,40}"
        r"\b(?:events?|seizures?|spells?)\b",
        text,
    ):
        return "multiple per day"
    if re.search(r"\b(?:daily|every night|each night|nightly)\b", text):
        return _format_prediction_rate("1", "day")
    return None


def evidence_describes_current_non_epileptic_events(text: str) -> bool:
    return bool(
        re.search(
            r"\b(?:events?|episodes?|spells?|seizure-like episodes?)\b"
            r".{0,80}\b(?:currently|current|present|at present)\b"
            r".{0,80}\bnon-epileptic\b",
            text,
        )
        or re.search(
            r"\b(?:currently|current|present|at present)\b"
            r".{0,80}\bnon-epileptic\b"
            r".{0,80}\b(?:events?|episodes?|spells?|seizure-like episodes?)\b",
            text,
        )
    )


def _q_interval_label_from_selected_evidence(text: str) -> str | None:
    interval = r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)"
    interval_range = rf"{interval}(?:\s*(?:to|-|–|—)\s*{interval})?"
    match = re.search(
        rf"\bq\s*(?P<interval>{interval_range})\s*"
        r"(?P<unit>d|day|wk|week|mo|month|yr|year)\b",
        text,
    )
    if not match:
        match = re.search(
            rf"\bq(?P<interval>{interval_range})\s*"
            r"(?P<unit>d|day|wk|week|mo|month|yr|year)\b",
            text,
        )
    if not match:
        return None
    unit = UNIT_SYNONYMS.get(match.group("unit"), match.group("unit"))
    return _format_prediction_rate(
        f"1 per {_words_to_numbers(match.group('interval'))}",
        unit,
    )


def _median_interval_label_from_selected_evidence(text: str) -> str | None:
    match = re.search(
        r"\bmedian inter-seizure interval\s*(?:≈|~|about|approximately|around)?\s*"
        r"(?P<interval>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+(?P<unit>day|week|month|year)s?\b",
        text,
    )
    if not match:
        return None
    return _format_prediction_rate(f"1 per {match.group('interval')}", match.group("unit"))
