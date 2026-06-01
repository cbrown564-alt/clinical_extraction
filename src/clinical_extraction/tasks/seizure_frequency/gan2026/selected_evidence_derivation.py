from __future__ import annotations

import re

from clinical_extraction.tasks.seizure_frequency.gan2026.label_parser import (
    normalize_frequency_label,
)

NUM_WORDS = {
    "zero": "0",
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
    "eleven": "11",
    "twelve": "12",
}
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


def _words_to_numbers(text: str) -> str:
    return re.sub(
        r"\b(" + "|".join(NUM_WORDS) + r")\b",
        lambda match: NUM_WORDS[match.group(0)],
        text,
    )


def _once_twice_thrice(text: str) -> str:
    text = re.sub(r"\bonce\b", "1", text)
    text = re.sub(r"\btwice\b", "2", text)
    return re.sub(r"\bthrice\b", "3", text)


def prediction_label_from_selected_evidence(
    evidence: str,
    context_text: str | None = None,
) -> str | None:
    if not evidence:
        return None

    text = normalize_frequency_label(_once_twice_thrice(_words_to_numbers(evidence)))
    unit = r"day|week|month|year"
    count = r"\d+(?:\s*(?:to|-|–|—|or)\s*\d+)?"

    monthly_diary = monthly_diary_label_from_text(text)
    if monthly_diary:
        return monthly_diary

    q_interval = _q_interval_label_from_selected_evidence(text)
    if q_interval:
        return q_interval

    median_interval = _median_interval_label_from_selected_evidence(text)
    if median_interval:
        return median_interval

    if evidence_describes_current_non_epileptic_events(text):
        return "seizure free for multiple year"

    upper_bound = re.search(
        rf"(?:≤|<=|up to|at most|no more than)\s+(?P<count>{count})\s+"
        rf"(?:seizures?\s+)?per\s+(?P<unit>{unit})s?\b",
        text,
    )
    if upper_bound:
        return _format_prediction_rate(upper_bound.group("count"), upper_bound.group("unit"))
    upper_bound_in_weeks = re.search(
        rf"(?:≤|<=|up to|at most|no more than)\s+(?P<count>{count})\s+"
        r"(?:[a-z]+(?:-[a-z]+)?\s+){0,4}"
        r"\bin\s+(?:bad\s+|flare\s+)?weeks?\b",
        text,
    )
    if upper_bound_in_weeks:
        return _format_prediction_rate(upper_bound_in_weeks.group("count"), "week")

    if re.search(r"\bbimonthly\b", text):
        return _format_prediction_rate("1 per 2", "month")
    every_other = re.search(rf"\bevery\s+other\s+(?P<unit>{unit})\b", text)
    if every_other:
        return _format_prediction_rate("1 per 2", every_other.group("unit"))
    no_definite_recent = re.search(
        r"\bno\s+definite\s+epileptic\s+events?\b.*\b(?:past|last|this)\s+"
        rf"(?:(?P<count>\d+)\s+)?(?P<unit>{unit})s?\b",
        text,
    )
    if no_definite_recent:
        count_text = no_definite_recent.group("count") or "multiple"
        return f"seizure free for {count_text} {no_definite_recent.group('unit')}"

    days_per_week = re.search(
        rf"\b(?:occurring|occur|events?|seizures?|spells?)\b.{0,60}"
        rf"\b(?:on\s+)?(?P<count>{count})\s+days?\s+of\s+the\s+week\b",
        text,
    )
    if not days_per_week:
        days_per_week = re.search(
            rf"\b(?P<count>{count})\s+days?\s+per\s+week\b",
            text,
        )
    if days_per_week:
        return _format_prediction_rate(days_per_week.group("count"), "week")

    cluster_label = _cluster_label_from_selected_evidence(text)
    if cluster_label:
        return cluster_label
    if re.search(r"\bclusters?\b", text):
        return None

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

    range_count = _range_count_over_window(text)
    if range_count:
        return range_count

    summed = _sum_counts_over_window(text)
    if summed:
        return summed

    single_count = _single_count_over_window(text)
    if single_count:
        return single_count

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
        rf"\b(?P<count>{count})\s+(?:[a-z]+(?:-[a-z]+)?\s+){{0,4}}"
        r"(?:over|in|during|for)?\s*(?:the\s+)?(?:past|last)\s+fortnight\b",
        text,
    )
    if not fortnight:
        fortnight = re.search(
            r"\b(?:past|last)\s+fortnight\b.*?"
            rf"\b(?P<count>{count})\s+(?:[a-z]+(?:-[a-z]+)?\s+){{0,4}}"
            r"(?:seizure|attack|convulsion|spasm|event|episode)",
            text,
        )
    if fortnight:
        return _format_prediction_rate(f"{fortnight.group('count')} per 2", "week")

    monthly_shorthand = re.search(
        rf"\b(?P<count>{count})\s+(?:[a-z]+\s+){{0,4}}monthly\b",
        text,
    )
    if monthly_shorthand:
        return _format_prediction_rate(monthly_shorthand.group("count"), "month")

    single_last_period = re.search(
        rf"\b(?:single|1)\b.*\b(?:last|past)\s+(?P<unit>{unit})\b",
        text,
    )
    if single_last_period:
        return _format_prediction_rate("1", single_last_period.group("unit"))

    quarter = re.search(
        rf"\b(?P<count>{count})\s+(?:seizures?\s+)?per\s+quarter\b",
        text,
    )
    if quarter:
        return _format_prediction_rate(quarter.group("count"), "3 month")
    this_quarter = re.search(
        rf"\b(?P<count>{count})\s+(?:[a-z]+(?:-[a-z]+)?\s+){{0,4}}"
        r"(?:this|past|last)\s+quarter\b",
        text,
    )
    if this_quarter:
        return _format_prediction_rate(this_quarter.group("count"), "3 month")

    this_year = re.search(
        rf"\b(?P<count>{count})\s+(?:[a-z]+(?:-[a-z]+)?\s+){{0,4}}"
        r"(?:this|past|last)\s+year\b",
        text,
    )
    if this_year:
        elapsed_months = _elapsed_months_in_year_context(context_text)
        if elapsed_months:
            return _format_prediction_rate(
                f"{this_year.group('count')} per {elapsed_months}",
                "month",
            )
        return _format_prediction_rate(this_year.group("count"), "year")
    year_to_date = re.search(
        rf"\b(?P<count>{count})\s+(?:[a-z]+(?:-[a-z]+)?\s+){{0,5}}"
        r"(?:so\s+far\s+this\s+year|this\s+year\s+to\s+date|"
        r"\d{4}\s+so\s+far)\b",
        text,
    )
    if year_to_date:
        elapsed_months = _elapsed_months_in_year_context(context_text)
        if elapsed_months:
            return _format_prediction_rate(
                f"{year_to_date.group('count')} per {elapsed_months}",
                "month",
            )
        return _format_prediction_rate(year_to_date.group("count"), "year")

    daily = _daily_label_from_selected_evidence(text)
    if daily:
        return daily

    times_every = re.search(
        rf"\b(?P<count>\d+)\s+(?:times|seizures?)?\s*every\s+"
        rf"(?P<period>\d+)\s+(?P<unit>{unit})s?\b",
        text,
    )
    if times_every:
        return _format_prediction_rate(
            f"{times_every.group('count')} per {times_every.group('period')}",
            times_every.group("unit"),
        )

    every_range = re.search(
        rf"\bevery\s+(?P<count>{count})\s+(?P<unit>{unit})s?\b",
        text,
    )
    if every_range:
        return _format_prediction_rate(
            f"1 per {every_range.group('count')}",
            every_range.group("unit"),
        )

    interval_range = re.search(
        rf"\bintervals?\s+ranging\s+(?P<count>{count})\s+"
        rf"(?P<unit>{unit})s?\b",
        text,
    )
    if interval_range:
        return _format_prediction_rate(
            f"1 per {interval_range.group('count')}",
            interval_range.group("unit"),
        )

    return None


def should_prefer_selected_evidence_label(
    raw: str,
    raw_repaired: str,
    evidence: str,
    evidence_label: str,
) -> bool:
    normalized_raw = normalize_frequency_label(_words_to_numbers(str(raw)))
    normalized_evidence = normalize_frequency_label(_words_to_numbers(evidence))
    if any(
        marker in normalized_evidence
        for marker in (
            "quarter",
            "≤",
            "<=",
            "up to",
            "bimonthly",
            "fortnight",
            "median inter-seizure interval",
        )
    ):
        return True
    if re.search(r"\b(?:this|past|last)\s+(?:quarter|year)\b", normalized_evidence):
        return True
    if re.search(
        r"\b(?:so\s+far\s+this\s+year|this\s+year\s+to\s+date|\d{4}\s+so\s+far)\b",
        normalized_evidence,
    ):
        return True
    if re.search(r"\b\d+\s*/\s*30\b.*\b(?:this|past|last)\s+month\b", normalized_evidence):
        return True
    if re.search(r"\b\d+(?:\s*(?:to|-|–|—|or)\s*\d+)?\s+\w*\s*monthly\b", normalized_evidence):
        return True
    if re.search(r"\bevery\s+(?:other|\d+)\s+(?:day|week|month|year)s?\b", normalized_evidence):
        return True
    if re.search(
        r"\bq(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)",
        normalized_evidence,
    ):
        return True
    if monthly_diary_label_from_text(normalized_evidence):
        return True
    if _daily_label_from_selected_evidence(normalized_evidence) == evidence_label:
        return True
    if evidence_label == "1 per day" and re.search(
        r"\bclusters?\s+of\s+(?:jumps?|jerks?)\b.{0,40}\b(?:almost\s+)?daily\b",
        normalized_evidence,
    ):
        return True
    if " to " in evidence_label and " to " not in raw_repaired:
        return True
    if _sum_counts_over_window(normalized_evidence) == evidence_label:
        return True
    if "cluster" in evidence_label and re.search(
        r"\b(?:clusters?|bursts?|grouped|when they recur|without seizures)\b",
        normalized_evidence,
    ):
        return True
    if raw_repaired in {"unknown", "no seizure frequency reference"}:
        return True
    if raw_repaired.startswith("multiple per "):
        return True
    if normalized_raw != raw_repaired and any(
        marker in normalized_raw
        for marker in ("≤", "<=", "up to", "at most", "no more than", "quarter")
    ):
        return True
    return not _raw_label_is_simple_rate(normalized_raw)


def _raw_label_is_simple_rate(normalized_raw: str) -> bool:
    return bool(
        re.match(
            r"^(?:multiple|\d+(?:\s*to\s*\d+)?)\s+per\s+"
            r"(?:(?:multiple|\d+(?:\s*to\s*\d+)?)\s+)?"
            r"(?:day|week|month|year)s?$",
            normalized_raw,
        )
    )


def _calendar_log_label_from_selected_evidence(text: str) -> str | None:
    entries = re.findall(
        r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s*x\s*(\d+)\b",
        text,
    )
    if len(entries) < 2:
        entries = re.findall(
            r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)"
            r"[a-z]*\s*:\s*(\d+)\s+days?\b",
            text,
        )
    if len(entries) < 2:
        return None
    return _format_prediction_rate(
        f"{sum(int(value) for value in entries)} per {len(entries)}",
        "month",
    )


def monthly_diary_label_from_text(text: str) -> str | None:
    """Sum source-near monthly diary counts from selected evidence or LLM events."""
    normalized = normalize_frequency_label(_once_twice_thrice(_words_to_numbers(text)))
    for parser in (
        _calendar_log_label_from_selected_evidence,
        _month_sleep_awake_log_label_from_selected_evidence,
        _general_monthly_diary_label_from_selected_evidence,
    ):
        label = parser(normalized)
        if label:
            return label
    return None


def _month_sleep_awake_log_label_from_selected_evidence(text: str) -> str | None:
    month_pattern = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*"
    count_pattern = r"\d+|no|zero|a|an"
    state_pattern = r"sleep|asleep|night|nocturnal|awake|waking|daytime|day"
    counts_by_month: dict[str, int] = {}
    for sentence in re.split(r"(?<=[.;])\s+", text):
        month_match = re.search(rf"\b(?P<month>{month_pattern})\b", sentence)
        if not month_match or not re.search(rf"\b(?:{state_pattern})\b", sentence):
            continue
        state_counts = []
        for match in re.finditer(
            rf"\b(?P<count>{count_pattern})\s+(?!in\s+)"
            rf"(?:\w+\s+){{0,3}}(?:{state_pattern})\b",
            sentence,
        ):
            count_value = _diary_count_value(match.group("count"))
            if count_value <= 100:
                state_counts.append(count_value)
        for match in re.finditer(
            rf"\b(?P<count>{count_pattern})\s+in\s+"
            rf"(?:{state_pattern})\b",
            sentence,
        ):
            count_value = _diary_count_value(match.group("count"))
            if count_value <= 100:
                state_counts.append(count_value)
        if state_counts:
            count_sum = sum(state_counts)
            if count_sum <= 100:
                counts_by_month.setdefault(month_match.group("month"), count_sum)
    counts = list(counts_by_month.values())
    if len(counts) < 2:
        return None
    return _format_prediction_rate(f"{sum(counts)} per {len(counts)}", "month")


def _general_monthly_diary_label_from_selected_evidence(text: str) -> str | None:
    month = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*"
    number = r"\d+|no|zero|a|an"
    month_counts: dict[str, int] = {}

    def add(month_key: str, count_text: str) -> None:
        count_value = _diary_count_value(count_text)
        if count_value > 100:
            return
        month_counts.setdefault(month_key, count_value)

    for match in re.finditer(
        rf"\b(?P<count>{number})\s+"
        r"(?:[a-z]+(?:-[a-z]+)?\s+){0,4}"
        rf"(?:seizures?|events?|convulsions?)\s+(?:so\s+far\s+)?in\s+(?P<month>{month})\b",
        text,
    ):
        add(match.group("month"), match.group("count"))
    for match in re.finditer(
        rf"\b(?P<count>{number})\s+(?:were\s+)?in\s+(?P<month>{month})\b",
        text,
    ):
        add(match.group("month"), match.group("count"))
    for match in re.finditer(
        rf"\b(?P<count>{number})\s+in\s+(?P<month>{month})\b",
        text,
    ):
        add(match.group("month"), match.group("count"))
    for match in re.finditer(
        rf"\bin\s+(?P<month>{month})\b[^.;]*?\b(?:had|recorded|reports?)\s+"
        rf"(?P<count>{number})\b",
        text,
    ):
        add(match.group("month"), match.group("count"))
    this_month = re.search(
        rf"\b(?:this\s+month|as\s+of\s+this\s+month)\b[^.;]*?\b"
        rf"(?:had|has\s+had|reports?|recorded)?\s*(?P<count>{number})\s+"
        r"(?:seizures?|events?|convulsions?)\b",
        text,
    )
    if not this_month:
        this_month = re.search(
            rf"\b(?P<count>{number})\s+"
            r"(?:seizures?|events?|convulsions?)\s+(?:so\s+far\s+)?"
            r"(?:this\s+month|to\s+date\s+in\s+this\s+month)\b",
            text,
        )
    if this_month:
        add("this_month", this_month.group("count"))

    if len(month_counts) < 2:
        return None
    return _format_prediction_rate(
        f"{sum(month_counts.values())} per {len(month_counts)}",
        "month",
    )


def _diary_count_value(count_text: str) -> int:
    if count_text in {"a", "an"}:
        return 1
    return 0 if count_text in {"no", "zero"} else int(count_text)


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


def _daily_label_from_selected_evidence(text: str) -> str | None:
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


def _cluster_label_from_selected_evidence(text: str) -> str | None:
    if re.search(
        r"\bclusters?\s+of\s+(?:jumps?|jerks?)\b.{0,40}\b(?:almost\s+)?daily\b",
        text,
    ):
        return "1 per day"
    if re.search(
        r"\bclusters?\s+of\s+(?:jumps?|jerks?)\b.{0,40}\balmost\s+1\s+per\s+day\b",
        text,
    ):
        return "1 per day"

    recurrence_cluster = re.search(
        r"\b(?:go|remain|stretches?)\b.{0,50}"
        r"\b(?:nearly|almost|about|around|up to\s+)?"
        r"(?P<interval>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+"
        r"(?P<unit>day|week|month)s?\b.{0,80}"
        r"\b(?:when they recur|then)\b.{0,80}"
        r"\b(?P<per>\d+(?:\s*(?:to|-|–|—|and)\s*\d+)?)\b"
        r".{0,30}\b(?:one|1)\s+day\b",
        text,
    )
    if recurrence_cluster:
        per_cluster = re.sub(r"\s*(?:-|–|—|and)\s*", " to ", recurrence_cluster.group("per"))
        return (
            f"1 cluster per {recurrence_cluster.group('interval')} "
            f"{recurrence_cluster.group('unit')}, {per_cluster} per cluster"
        )
    recurrence_cluster_between = re.search(
        r"\b(?:go|remain|stretches?)\b.{0,50}"
        r"\b(?:nearly|almost|about|around|up to\s+)?"
        r"(?P<interval>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+"
        r"(?P<unit>day|week|month)s?\b.{0,120}"
        r"\b(?:between|often between)\s+"
        r"(?P<per>\d+(?:\s*(?:to|-|–|—|and)\s*\d+)?)\b",
        text,
    )
    if recurrence_cluster_between:
        per_cluster = re.sub(
            r"\s*(?:-|–|—|and)\s*",
            " to ",
            recurrence_cluster_between.group("per"),
        )
        return (
            f"1 cluster per {recurrence_cluster_between.group('interval')} "
            f"{recurrence_cluster_between.group('unit')}, {per_cluster} per cluster"
        )

    seizure_free_cluster_day = re.search(
        r"\b(?:seizure-free|without\s+seizures?)\s+for\s+"
        r"(?P<interval>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+"
        r"(?:consecutive\s+)?(?P<unit>day|week|month)s?\b.{0,120}"
        r"\b(?:followed\s+by|then)\s+(?:a\s+)?day\b.{0,100}"
        r"\b(?:multiple|several|batches?|clusters?|clustering)\b.{0,80}"
        r"\b(?:typically\s+)?(?P<per>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\b",
        text,
    )
    if seizure_free_cluster_day:
        per_cluster = re.sub(
            r"\s*(?:-|–|—|and)\s*",
            " to ",
            seizure_free_cluster_day.group("per"),
        )
        return (
            f"1 cluster per {seizure_free_cluster_day.group('interval')} "
            f"{seizure_free_cluster_day.group('unit')}, {per_cluster} per cluster"
        )

    seizure_free_batch = re.search(
        r"\b(?:go|manage|remain)\b.{0,30}"
        r"(?P<interval>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+"
        r"(?P<unit>day|week|month)s?\s+without\s+seizures?\b.{0,140}"
        r"\b(?:batches?|clusters?|clustering)\b.{0,80}?"
        r"\b(?:with\s+)?(?P<per>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\b"
        r".{0,40}\b(?:within\s+24\s+hours?|events?)\b",
        text,
    )
    if seizure_free_batch:
        per_cluster = re.sub(
            r"\s*(?:-|–|—|and)\s*",
            " to ",
            seizure_free_batch.group("per"),
        )
        return (
            f"1 cluster per {seizure_free_batch.group('interval')} "
            f"{seizure_free_batch.group('unit')}, {per_cluster} per cluster"
        )

    cluster_multiple_days = re.search(
        r"\b(?:past|last)\s+month\b.{0,120}\bclusters?\b.{0,80}"
        r"\b(?:on|over)\s+multiple\s+days?\b",
        text,
    )
    if cluster_multiple_days and _evidence_implies_multiple_per_cluster(text):
        return "multiple cluster per month, multiple per cluster"

    monthly_cluster = re.search(r"\bmonthly\s+clusters?\b", text)
    if monthly_cluster:
        monthly_per_cluster_match = re.search(
            r"\b(?P<count>\d+(?:\s*to\s*\d+)?)\s+"
            r"(?=(?:[a-z]+(?:-[a-z]+)?\s+){0,4}"
            r"(?:seizure|absence|attack|convulsion|spasm|event|mal))",
            text[monthly_cluster.end() :],
        )
        if monthly_per_cluster_match:
            return f"1 cluster per month, {monthly_per_cluster_match.group('count')} per cluster"
        if _evidence_implies_multiple_per_cluster(text):
            return "1 cluster per month, multiple per cluster"

    monthly_burst = re.search(
        r"\b(?:clusters?|bursts?)\b.*\b(?:once\s+each|1\s+each|once\s+per|1\s+per)\s+month\b",
        text,
    )
    if monthly_burst and _evidence_implies_multiple_per_cluster(text):
        return "1 cluster per month, multiple per cluster"

    weekly_cluster = re.search(r"\bweekly\b.*\bclusters?\b", text)
    if weekly_cluster and _evidence_implies_multiple_per_cluster(text):
        return "1 cluster per week, multiple per cluster"
    cluster_weekly_per_cluster = re.search(
        r"\bclusters?\b.*\b(?:now\s+)?weekly\b.*?"
        r"\b(?P<count>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+"
        r"(?:or\s+more\s+)?(?:events?|seizures?)?(?:\s+within\b.*)?"
        r"(?:per\s+cluster)?\b",
        text,
    )
    if cluster_weekly_per_cluster:
        return (
            "1 cluster per week, "
            f"{cluster_weekly_per_cluster.group('count')} per cluster"
        )
    weekly_cluster_count = re.search(
        r"\bweekly\b.*\bclusters?\b.*?"
        r"\b(?P<count>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+"
        r"(?:or\s+more\s+)?(?:events?|seizures?)\b",
        text,
    )
    if weekly_cluster_count:
        return f"1 cluster per week, {weekly_cluster_count.group('count')} per cluster"

    cluster_days_month = re.search(
        r"\b(?:cluster\s+days?|clusters?)\s+"
        r"(?:(?P<count_word>twice)|(?P<count>\d+(?:\s*(?:to|-|–|—)\s*\d+)?))\s+"
        r"this\s+month\b.*?"
        r"(?:sizes?\s+unrecorded|typically\s+(?P<per>\d+(?:\s*(?:to|-|–|—|or)\s*\d+)?)"
        r"(?:\s+or\s+more)?\s+(?:seizures?|events?)\s+in\s+24\s*h)",
        text,
    )
    if cluster_days_month:
        count_text = (
            "2"
            if cluster_days_month.group("count_word")
            else cluster_days_month.group("count")
        )
        per_cluster = cluster_days_month.group("per") or "multiple"
        return f"{count_text} cluster per month, {per_cluster} per cluster"

    cluster_days_month_reversed = re.search(
        r"\b(?P<count>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+cluster\s+days?\s+"
        r"this\s+month\b.*?(?:sizes?\s+unrecorded|typically\s+"
        r"(?P<per>\d+(?:\s*(?:to|-|–|—|or)\s*\d+)?)"
        r"(?:\s+or\s+more)?\s+(?:seizures?|events?)\s+in\s+24\s*h)",
        text,
    )
    if cluster_days_month_reversed:
        per_cluster = cluster_days_month_reversed.group("per") or "multiple"
        return (
            f"{cluster_days_month_reversed.group('count')} cluster per month, "
            f"{per_cluster} per cluster"
        )

    clusters_x_month = re.search(
        r"\bclusters?\s+(?P<count>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s*×\s*/\s*month\b"
        r".*?(?P<per>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+events?\b",
        text,
    )
    if clusters_x_month:
        return (
            f"{clusters_x_month.group('count')} cluster per month, "
            f"{clusters_x_month.group('per')} per cluster"
        )

    quarterly_cluster = re.search(
        r"\bquarterly\s+clusters?\b.*?\b(?P<per>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+"
        r"(?:convulsions?|seizures?|events?)\s+per\s+episode\b",
        text,
    )
    if quarterly_cluster:
        return f"1 cluster per 3 month, {quarterly_cluster.group('per')} per cluster"

    burst_monthly = re.search(
        r"\b(?:bursts?|clusters?)\b.*\b(?:around\s+the\s+beginning\s+of\s+most|"
        r"roughly\s+(?:once|1)\s+a|(?:once|1)\s+a|each)\s+month\b",
        text,
    )
    if burst_monthly:
        return "1 cluster per month, multiple per cluster"

    grouped_weekly = re.search(
        r"\b(?P<count>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+"
        r"(?:nights?|mornings?|evenings?)\s+per\s+week\b.*\b"
        r"(?:several|multiple|grouped|clusters?|bursts?)\b",
        text,
    )
    if grouped_weekly:
        return (
            f"{grouped_weekly.group('count')} cluster per week, "
            "multiple per cluster"
        )

    several_per_fortnight = re.search(
        r"\bclusters?\s+arise\s+on\s+several\s+(?:evenings?|mornings?|days?)\s+"
        r"per\s+fortnight\b.*?\b(?P<count>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+"
        r"(?:spells?|seizures?|events?)\b",
        text,
    )
    if several_per_fortnight:
        return (
            "multiple cluster per 2 week, "
            f"{several_per_fortnight.group('count')} per cluster"
        )

    every_cluster = re.search(
        r"\b(?:clusters?|bursts?)\b.*\bevery\s+"
        r"(?P<count>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+"
        r"(?P<unit>day|week|month|year)s?\b",
        text,
    )
    if every_cluster:
        if _evidence_implies_multiple_per_cluster(text):
            return (
                f"1 cluster per {every_cluster.group('count')} "
                f"{every_cluster.group('unit')}, multiple per cluster"
            )
        return _format_prediction_rate(
            f"1 per {every_cluster.group('count')}",
            every_cluster.group("unit"),
        )

    cluster_match = re.search(
        r"\b(?:≈|~|about\s+|approximately\s+|around\s+)?"
        r"(?P<count>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+clusters?\s+"
        r"(?:(?:per|every)\s+(?:(?P<den>\d+)\s+)?(?P<unit>day|week|month|year)"
        r"|(?:this|past|last)\s+(?P<period>day|week|month|year|quarter))\b",
        text,
    )
    if not cluster_match:
        return None

    tail = text[cluster_match.end() :]
    per_cluster_match = re.search(
        r"\b(?:each|per\s+cluster|cluster(?:s)?\s+(?:with|of|having))\s+"
        r"(?:≈|~|about\s+|approximately\s+|around\s+)?(?P<count>\d+)\s+"
        r"(?=(?:[a-z]+(?:-[a-z]+)?\s+){0,4}"
        r"(?:seizure|absence|attack|convulsion|spasm|event|mal))",
        tail,
    )
    denominator = cluster_match.group("den") or "1"
    unit = cluster_match.group("unit") or cluster_match.group("period")
    if unit == "quarter":
        denominator = "3"
        unit = "month"
    den_text = f"{denominator} " if denominator != "1" else ""
    if not per_cluster_match:
        return (
            f"{cluster_match.group('count')} cluster per {den_text}{unit}, "
            "multiple per cluster"
        )
    return (
        f"{cluster_match.group('count')} cluster per {den_text}{unit}, "
        f"{per_cluster_match.group('count')} per cluster"
    )


def _evidence_implies_multiple_per_cluster(text: str) -> bool:
    return bool(
        re.search(
            r"\b(?:several|multiple|bursts?|flurries|episodes?\s+over\s+"
            r"(?:a\s+)?few\s+days|over\s+(?:several|multiple)\s+days|"
            r"lasting\s+\d+\s*(?:to|-|–|—)\s*\d+\s+days|"
            r"number\s+per\s+cluster\s+not\s+documented|"
            r"imprecise\s+number\s+of\s+events\s+per\s+burst)\b",
            text,
        )
    )


def _sum_counts_over_window(text: str) -> str | None:
    window = re.search(
        r"\b(?:in|over|during|for)\s+(?:the\s+)?(?:past|last)\s+"
        r"(?:(?P<count>\d+)\s+)?(?P<unit>day|week|month|year)s?\b",
        text,
    )
    if not window:
        return None

    prefix = text
    counts = [
        int(value)
        for value in re.findall(
            r"\b(\d+)\s+(?!(?:day|week|month|year)s?\b)"
            r"(?!(?:seizure[- ]free|free)\b)"
            r"(?=(?:tonic(?:-clonic)?|drop|absence|"
            r"(?:[a-z]+(?:-[a-z]+)?\s+){0,4}"
            r"(?:seizure|attack|convulsion|spasm|mal|event)))",
            prefix,
        )
    ]
    if not counts:
        return None

    denominator = window.group("count") or "1"
    unit = window.group("unit")
    return _format_prediction_rate(f"{sum(counts)} per {denominator}", unit)


def _range_count_over_window(text: str) -> str | None:
    window = re.search(
        r"\b(?:in|over|during|for)\s+(?:the\s+)?(?:past|last)\s+"
        r"(?:(?P<count>\d+)\s+)?(?P<unit>day|week|month|year)s?\b",
        text,
    )
    if not window:
        return None

    range_match = re.search(
        r"\b(?P<low>\d+)\s*(?:to|-|–|—|or)\s*(?P<high>\d+)\s+"
        r"(?=(?:[a-z]+(?:-[a-z]+)?\s+){0,4}"
        r"(?:seizure|attack|convulsion|spasm|mal|event|tonic))",
        text,
    )
    if not range_match:
        return None

    denominator = window.group("count") or "1"
    unit = window.group("unit")
    return _format_prediction_rate(
        f"{range_match.group('low')} to {range_match.group('high')} per {denominator}",
        unit,
    )


def _single_count_over_window(text: str) -> str | None:
    match = re.search(
        r"\b(?P<count>\d+)\s+(?:[a-z]+(?:-[a-z]+)?\s+){0,4}"
        r"(?:seizure|attack|convulsion|spasm|mal|event|episode)s?\s+"
        r"(?:in|over|during|for)\s+(?:the\s+)?(?:past|last)?\s*"
        r"(?P<denominator>\d+)\s+(?P<unit>day|week|month|year)s?\b",
        text,
    )
    if not match:
        return None
    return _format_prediction_rate(
        f"{match.group('count')} per {match.group('denominator')}",
        match.group("unit"),
    )


def _format_prediction_rate(count_text: str, unit_text: str) -> str:
    count = re.sub(r"\s*(?:-|–|—)\s*", " to ", count_text.strip())
    count = re.sub(r"\s+or\s+", " to ", count)
    count = re.sub(r"\s+", " ", count)
    unit = unit_text.rstrip("s").strip()
    if " per " in count:
        return f"{count} {unit}"
    return f"{count} per {unit}"


def _elapsed_months_in_year_context(context_text: str | None) -> int | None:
    if not context_text:
        return None
    text = normalize_frequency_label(context_text)
    month_names = {
        "january": 1,
        "february": 2,
        "march": 3,
        "april": 4,
        "may": 5,
        "june": 6,
        "july": 7,
        "august": 8,
        "september": 9,
        "october": 10,
        "november": 11,
        "december": 12,
    }
    month_pattern = "|".join(month_names)
    match = re.search(
        rf"\b(?:clinic\s+date|sent)\s*:\s*\d{{1,2}}\s+({month_pattern})\s+\d{{4}}\b",
        text,
    )
    if not match:
        return None
    return month_names[match.group(1)]
