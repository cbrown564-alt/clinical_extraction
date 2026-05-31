from __future__ import annotations

import re
from collections.abc import Sequence

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
) -> list[RawCandidate]:
    context = ExtractionContext(text=text)
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

DIARY_RULES = (
    SEIZURE_DAYS_PER_PERIOD_RULE,
    SEIZURE_DAYS_FRACTION_RULE,
    DIARY_DATE_LIST_RULE,
    SEIZURE_DAY_LOG_RULE,
    MONTHLY_COUNT_LOG_RULE,
    SPARSE_FULL_MONTH_LOG_RULE,
    RECORDED_MONTH_LOG_RULE,
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


def _singular_unit(value: str) -> str:
    normalized = value.lower().strip()
    return normalized[:-1] if normalized.endswith("s") else normalized


def _clean_evidence(evidence: str) -> str:
    return evidence.strip(" .;:\n\t")
