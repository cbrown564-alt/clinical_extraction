from __future__ import annotations

import re
from collections.abc import Callable, Sequence
from typing import cast

from clinical_extraction.tasks.seizure_frequency.gan2026.candidates import (
    CandidateKind,
    RawCandidate,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.rule_metadata import (
    AblationConfig,
    ExtractionContext,
    Portability,
    RuleExample,
    RuleGroup,
    RuleSpec,
)

NUMBER_WORDS = {
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
    "thirteen": "13",
    "fourteen": "14",
    "fifteen": "15",
    "sixteen": "16",
    "seventeen": "17",
    "eighteen": "18",
    "nineteen": "19",
    "single": "1",
    "once": "1",
    "twice": "2",
    "thrice": "3",
    "several": "multiple",
    "few": "multiple",
}
NUMBER_WORD_PATTERN = "|".join(NUMBER_WORDS)
NUMBER_VALUE_TOKEN = rf"(?:multiple|\d+|{NUMBER_WORD_PATTERN})"
NUMBER_TOKEN = (
    rf"(?:{NUMBER_VALUE_TOKEN}(?:\s+(?:to|or)\s+{NUMBER_VALUE_TOKEN}|"
    rf"\s*[-–—]\s*{NUMBER_VALUE_TOKEN})?)"
)
MONTH_ABBREVIATIONS = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}
FULL_MONTHS = {
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
MONTH_NAME_PATTERN = "|".join([*FULL_MONTHS, *MONTH_ABBREVIATIONS])


def apply_diary_rules(
    specs: Sequence[RuleSpec],
    text: str,
    ablation_config: AblationConfig,
    helpers: dict[str, object] | None = None,
) -> list[RawCandidate]:
    context = ExtractionContext(text=text, helpers=helpers)
    candidates: list[RawCandidate] = []
    for spec in specs:
        candidates.extend(
            candidate
            for candidate in spec.apply(context, ablation_config)
            if isinstance(candidate, RawCandidate)
        )
    return candidates


def _build_diary_candidate(
    match: re.Match[str],
    *,
    rule_id: str,
    label: str,
    evidence_group: str | int = 0,
) -> RawCandidate:
    return RawCandidate(
        kind=CandidateKind.FREQUENCY_RATE,
        label=label,
        evidence=_clean_evidence(match.group(evidence_group)),
        rule_id=rule_id,
        rule_group=RuleGroup.DIARY_LOG_AGGREGATION,
        portability=Portability.SEIZURE_FREQUENCY,
        match_groups=match.groupdict(),
    )


def _build_seizure_days_per_period(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_diary_candidate(
        match,
        rule_id="diary.seizure_days_per_period",
        label=_rate_label(match.group("count"), match.group("unit")),
    )


def _build_seizure_days_fraction(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _build_diary_candidate(
        match,
        rule_id="diary.seizure_days_fraction",
        label=_rate_label(match.group("count"), "month"),
    )


def _build_date_list(match: re.Match[str], _context: ExtractionContext) -> RawCandidate:
    dates = re.findall(r"(\d{2})-\d{2}", match.group("dates"))
    months = [int(month) for month in dates]
    denominator = max(max(months) - min(months), 1)
    return _build_diary_candidate(
        match,
        rule_id="diary.date_list",
        label=_rate_label(str(len(dates)), "month", str(denominator)),
    )


def _build_seizure_day_log(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate | None:
    entries = re.findall(
        rf"\b(?:{MONTH_NAME_PATTERN}):\s*(\d+)\s+days\b",
        match.group("entries"),
        flags=re.IGNORECASE,
    )
    if not entries:
        return None
    return _build_diary_candidate(
        match,
        rule_id="diary.seizure_day_log",
        label=_rate_label(str(sum(int(count) for count in entries)), "month", str(len(entries))),
    )


def _build_monthly_count_log(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate | None:
    entries = re.findall(
        r"\b(?P<month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+x(?P<count>\d+)",
        match.group("entries"),
        flags=re.IGNORECASE,
    )
    if not entries:
        return None
    total = sum(int(count) for _month, count in entries)
    denominator = len({MONTH_ABBREVIATIONS[month.lower()] for month, _count in entries})
    return _build_diary_candidate(
        match,
        rule_id="diary.monthly_count_log",
        label=_rate_label(str(total), "month", str(denominator)),
    )


def _build_sparse_full_month_log(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate | None:
    entries = re.findall(
        r"\b(?P<month>January|February|March|April|May|June|July|August|September|"
        r"October|November|December)\s+(?P<count>\d+)",
        match.group("entries"),
        flags=re.IGNORECASE,
    )
    if not entries:
        return None
    total = sum(int(count) for _month, count in entries)
    months = {FULL_MONTHS[month.lower()] for month, _count in entries}
    return _build_diary_candidate(
        match,
        rule_id="diary.sparse_full_month_log",
        label=_rate_label(str(total), "month", str(len(months))),
    )


def _build_recorded_month_log(
    match: re.Match[str], context: ExtractionContext
) -> RawCandidate | None:
    if "recorded:" not in context.text[max(0, match.start() - 80) : match.start()].lower():
        return None
    entries = re.findall(
        r"\b(?P<month>January|February|March|April|May|June|July|August|September|"
        r"October|November|December)\s+(?P<count>\d+)",
        match.group("entries"),
        flags=re.IGNORECASE,
    )
    if not entries:
        return None
    total = sum(int(count) for _month, count in entries)
    months = {FULL_MONTHS[month.lower()] for month, _count in entries}
    return _build_diary_candidate(
        match,
        rule_id="diary.recorded_month_log",
        label=_rate_label(str(total), "month", str(len(months))),
    )


def _is_in_monthly_trend_log(text: str, start: int) -> bool:
    lower_text = text.lower()
    segment_start = max(
        lower_text.rfind("frequency has increased:", 0, start),
        lower_text.rfind("frequency increased:", 0, start),
        lower_text.rfind("current diary:", 0, start),
    )
    if segment_start < 0:
        return False
    terminator = lower_text.rfind(".", 0, start)
    return terminator < segment_start


def _build_increasing_monthly_count(
    match: re.Match[str], context: ExtractionContext
) -> RawCandidate | None:
    if not _is_in_monthly_trend_log(context.text, match.start()):
        return None
    evidence = re.sub(
        r"\s+with\s+two\b.*$",
        "",
        match.group("entry"),
        flags=re.IGNORECASE,
    )
    return RawCandidate(
        kind=CandidateKind.FREQUENCY_RATE,
        label=_rate_label(match.group("count"), "month"),
        evidence=_clean_evidence(evidence),
        rule_id="diary.increasing_monthly_count",
        rule_group=RuleGroup.DIARY_LOG_AGGREGATION,
        portability=Portability.SEIZURE_FREQUENCY,
        match_groups=match.groupdict(),
    )


def _build_sleep_awake_month_summary(
    match: re.Match[str], context: ExtractionContext
) -> RawCandidate | None:
    clinic_date_func = cast(Callable[[str], object | None], context.helper("clinic_date"))
    relative_note_date = cast(
        Callable[[str, object | None], object | None],
        context.helper("relative_note_date"),
    )
    month_span = cast(
        Callable[[object | None, object | None], int | None],
        context.helper("month_span"),
    )
    clinic_date = clinic_date_func(context.text)
    if clinic_date is None:
        return None
    first_date = relative_note_date(match.group("first_month"), clinic_date)
    second_date = relative_note_date(match.group("second_month"), clinic_date)
    denominator = month_span(first_date, second_date)
    if denominator is None:
        return None
    counts = [
        _integer_number_token(match.group("count_a")),
        _integer_number_token(match.group("count_b")),
        _integer_number_token(match.group("count_c")),
        _integer_number_token(match.group("count_d")),
    ]
    integer_counts = [count for count in counts if count is not None]
    if len(integer_counts) != len(counts):
        return None
    return _build_diary_candidate(
        match,
        rule_id="diary.sleep_awake_month_summary",
        label=_rate_label(str(sum(integer_counts)), "month", str(denominator + 1)),
        evidence_group="evidence",
    )


SEIZURE_DAYS_PER_PERIOD_RULE = RuleSpec(
    rule_id="diary.seizure_days_per_period",
    group=RuleGroup.DIARY_LOG_AGGREGATION,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Diary-style seizure-day count per period.",
    pattern=re.compile(
        rf"\b(?:About\s+)?(?P<count>{NUMBER_TOKEN})\s+seizure\s+days?\s+"
        rf"per\s+(?P<unit>day|week|month|year)\b",
        re.IGNORECASE,
    ),
    build=_build_seizure_days_per_period,
    examples=(
        RuleExample(
            text="About three seizure days per week are reported.",
            expected_label="3 per week",
            expected_evidence="About three seizure days per week",
        ),
    ),
    provenance="Diary/log V1 expression.",
)

SEIZURE_DAYS_FRACTION_RULE = RuleSpec(
    rule_id="diary.seizure_days_fraction",
    group=RuleGroup.DIARY_LOG_AGGREGATION,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Seizure days fraction over 30 days this month.",
    pattern=re.compile(
        rf"\bSeizure\s+days:\s*(?P<count>{NUMBER_VALUE_TOKEN})\s*/\s*30\s+this\s+month\b",
        re.IGNORECASE,
    ),
    build=_build_seizure_days_fraction,
    examples=(
        RuleExample(
            text="Seizure days: six/30 this month.",
            expected_label="6 per month",
            expected_evidence="Seizure days: six/30 this month",
        ),
    ),
    provenance="Diary/log V1 expression.",
)

DIARY_DATE_LIST_RULE = RuleSpec(
    rule_id="diary.date_list",
    group=RuleGroup.DIARY_LOG_AGGREGATION,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Diary list of MM-DD seizure-event dates.",
    pattern=re.compile(
        r"\bSeizure events on (?P<dates>\d{2}-\d{2}(?:,\s*\d{2}-\d{2})+)\b",
        re.IGNORECASE,
    ),
    build=_build_date_list,
    examples=(
        RuleExample(
            text="Seizure events on 03-07, 03-27, 05-15, 05-19, 05-24.",
            expected_label="5 per 2 month",
            expected_evidence="Seizure events on 03-07, 03-27, 05-15, 05-19, 05-24",
        ),
    ),
    provenance="Diary/log V1 expression.",
)

SEIZURE_DAY_LOG_RULE = RuleSpec(
    rule_id="diary.seizure_day_log",
    group=RuleGroup.DIARY_LOG_AGGREGATION,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Annual seizure-day month log.",
    pattern=re.compile(
        rf"\bSeizures\s+in\s+\d{{4}}-\d{{4}}:\s*"
        rf"(?P<entries>[^.]*?(?:{MONTH_NAME_PATTERN}):\s*\d+\s+days[^.]*)",
        re.IGNORECASE,
    ),
    build=_build_seizure_day_log,
    examples=(
        RuleExample(
            text="Seizures in 2023-2024: January: 4 days, February: 2 days.",
            expected_label="6 per 2 month",
            expected_evidence="Seizures in 2023-2024: January: 4 days, February: 2 days",
        ),
    ),
    provenance="Diary/log V1 expression.",
)

MONTHLY_COUNT_LOG_RULE = RuleSpec(
    rule_id="diary.monthly_count_log",
    group=RuleGroup.DIARY_LOG_AGGREGATION,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Abbreviated month x-count seizure log.",
    pattern=re.compile(
        r"\bSeizure:\s*\d{4}:\s*"
        r"(?P<entries>(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+"
        r"x\d+,?\s*){2,})",
        re.IGNORECASE,
    ),
    build=_build_monthly_count_log,
    examples=(
        RuleExample(
            text="Seizure: 2022: Jan x1, Feb x0, Mar x1.",
            expected_label="2 per 3 month",
            expected_evidence="Seizure: 2022: Jan x1, Feb x0, Mar x1",
        ),
    ),
    provenance="Diary/log V1 expression.",
)

SPARSE_FULL_MONTH_LOG_RULE = RuleSpec(
    rule_id="diary.sparse_full_month_log",
    group=RuleGroup.DIARY_LOG_AGGREGATION,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Full-month semicolon sparse count log.",
    pattern=re.compile(
        r"\b\d{4}:\s*(?P<entries>(?:(?:January|February|March|April|May|June|July|"
        r"August|September|October|November|December)\s+\d+[^.;]*;\s*){2,}"
        r"(?:January|February|March|April|May|June|July|August|September|October|"
        r"November|December)\s+\d+[^.;]*)",
        re.IGNORECASE,
    ),
    build=_build_sparse_full_month_log,
    examples=(
        RuleExample(
            text="2025: January 0; February 1; March 2.",
            expected_label="3 per 3 month",
            expected_evidence="2025: January 0; February 1; March 2",
        ),
    ),
    provenance="Diary/log V1 expression.",
)

RECORDED_MONTH_LOG_RULE = RuleSpec(
    rule_id="diary.recorded_month_log",
    group=RuleGroup.DIARY_LOG_AGGREGATION,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Recorded full-month comma count log.",
    pattern=re.compile(
        r"\b(?P<entries>(?:(?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December)\s+\d+[^,.;]*,\s*)+"
        r"(?:January|February|March|April|May|June|July|August|September|October|"
        r"November|December)\s+\d+[^.;]*)",
        re.IGNORECASE,
    ),
    build=_build_recorded_month_log,
    examples=(
        RuleExample(
            text="Recorded: January 1 seizure, February 2 seizures, March 0 seizures.",
            expected_label="3 per 3 month",
            expected_evidence="January 1 seizure, February 2 seizures, March 0 seizures",
        ),
    ),
    provenance="Diary/log V1 expression.",
)

INCREASING_MONTHLY_COUNT_RULE = RuleSpec(
    rule_id="diary.increasing_monthly_count",
    group=RuleGroup.DIARY_LOG_AGGREGATION,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Month-by-month trend log with one candidate per month entry.",
    pattern=re.compile(
        r"\b(?P<entry>(?P<month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|"
        r"January|February|March|April|May|June|July|August|September|October|"
        r"November|December)\s+x\s*(?P<count>\d+)[^.;]*)",
        re.IGNORECASE,
    ),
    build=_build_increasing_monthly_count,
    examples=(
        RuleExample(
            text=(
                "Frequency has increased: July x 3 focal aware motor; "
                "August x 4 focal aware motor; September x 5 focal aware motor."
            ),
            expected_label="5 per month",
            expected_evidence="September x 5 focal aware motor",
        ),
    ),
    provenance="Diary/log V1 expression.",
)

SLEEP_AWAKE_MONTH_SUMMARY_RULE = RuleSpec(
    rule_id="diary.sleep_awake_month_summary",
    group=RuleGroup.DIARY_LOG_AGGREGATION,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Two-month diary summary split into sleep and awake event counts.",
    pattern=re.compile(
        rf"\b(?P<evidence>In\s+(?P<first_month>{MONTH_NAME_PATTERN})\s+"
        rf"(?:he|she)\s+had\s+(?P<count_a>{NUMBER_TOKEN})\s+(?:seizures?|episodes?|"
        rf"events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|"
        rf"jerks?|auras?|status epilepticus)\s+during\s+sleep\s+and\s+"
        rf"(?P<count_b>{NUMBER_TOKEN})\s+while\s+awake\.\s+In\s+"
        rf"(?P<second_month>{MONTH_NAME_PATTERN})\s+(?:he|she)\s+had\s+"
        rf"(?P<count_c>{NUMBER_TOKEN})\s+in\s+sleep\s+and\s+"
        rf"(?P<count_d>{NUMBER_TOKEN})\s+while\s+awake)\b",
        re.IGNORECASE,
    ),
    build=_build_sleep_awake_month_summary,
    examples=(
        RuleExample(
            text=(
                "Clinic Date: 10 March 2025. In January she had one seizure during "
                "sleep and two while awake. In February she had one in sleep and "
                "one while awake."
            ),
            expected_label="5 per 2 month",
            expected_evidence=(
                "In January she had one seizure during sleep and two while awake. "
                "In February she had one in sleep and one while awake"
            ),
        ),
    ),
    provenance="Diary/log V1 expression.",
)

DIARY_RULES = (
    SEIZURE_DAYS_PER_PERIOD_RULE,
    SEIZURE_DAYS_FRACTION_RULE,
    DIARY_DATE_LIST_RULE,
    SEIZURE_DAY_LOG_RULE,
    MONTHLY_COUNT_LOG_RULE,
    SPARSE_FULL_MONTH_LOG_RULE,
    RECORDED_MONTH_LOG_RULE,
    INCREASING_MONTHLY_COUNT_RULE,
    SLEEP_AWAKE_MONTH_SUMMARY_RULE,
)


def _rate_label(count: str, unit: str, denominator: str | None = None) -> str:
    count_value = _number_token(count)
    denominator_value = _number_token(denominator) if denominator else None
    unit_value = _singular_unit(unit)
    if unit_value == "quarter":
        unit_value = "month"
        denominator_value = "3"
    if denominator_value in {None, "1"}:
        return f"{count_value} per {unit_value}"
    return f"{count_value} per {denominator_value} {unit_value}"


def _number_token(value: str | None) -> str:
    if value is None:
        return "1"
    normalized = re.sub(r"\s*[-–—]\s*", " to ", value.lower())
    normalized = " ".join(normalized.split())
    if " to " in normalized:
        return " to ".join(_number_token(part) for part in normalized.split(" to "))
    if " or " in normalized:
        return " to ".join(_number_token(part) for part in normalized.split(" or "))
    return NUMBER_WORDS.get(normalized, normalized)


def _integer_number_token(value: str) -> int | None:
    normalized = _number_token(value)
    if normalized.isdigit():
        return int(normalized)
    return None


def _singular_unit(value: str) -> str:
    normalized = value.lower().strip()
    return normalized[:-1] if normalized.endswith("s") else normalized


def _clean_evidence(evidence: str) -> str:
    return evidence.strip(" .;:\n\t")
