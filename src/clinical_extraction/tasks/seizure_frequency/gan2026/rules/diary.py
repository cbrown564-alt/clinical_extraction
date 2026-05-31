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
WORD_TOKEN = r"[a-z][a-z\-‑–—]*"
SEIZURE_TERMS = (
    r"seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|"
    r"myoclonics?|jerks?|auras?|status epilepticus"
)
QUALIFIED_SEIZURE_TERMS = rf"(?:{WORD_TOKEN}\s+){{0,4}}(?:{SEIZURE_TERMS})"
DIARY_COUNT_TOKEN = rf"(?:{NUMBER_VALUE_TOKEN}|no|none|zero|a|an|another)"


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
        _diary_count_token(match.group("count_a")),
        _diary_count_token(match.group("count_b")),
        _diary_count_token(match.group("count_c")),
        _diary_count_token(match.group("count_d")),
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


def _build_monthly_diary_summary(
    match: re.Match[str], context: ExtractionContext, *, rule_id: str
) -> RawCandidate | None:
    clinic_date_func = cast(Callable[[str], object | None], context.helper("clinic_date"))
    clinic_date = clinic_date_func(context.text)
    if clinic_date is None:
        return None
    evidence = _trim_monthly_diary_evidence(match.group("evidence"))
    parsed = _monthly_diary_counts(evidence, clinic_date, context)
    if parsed is None:
        return None
    total, denominator = parsed
    if total <= 0 or denominator <= 0:
        return None
    return RawCandidate(
        kind=CandidateKind.FREQUENCY_RATE,
        label=_rate_label(str(total), "month", str(denominator)),
        evidence=evidence,
        rule_id=rule_id,
        rule_group=RuleGroup.DIARY_LOG_AGGREGATION,
        portability=Portability.SEIZURE_FREQUENCY,
        match_groups=match.groupdict(),
    )


def _monthly_diary_summary_builder(
    rule_id: str,
) -> Callable[[re.Match[str], ExtractionContext], RawCandidate | None]:
    def build(match: re.Match[str], context: ExtractionContext) -> RawCandidate | None:
        return _build_monthly_diary_summary(match, context, rule_id=rule_id)

    return build


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
        rf"(?:he|she)\s+had\s+(?P<count_a>{DIARY_COUNT_TOKEN})\s+(?:seizures?|episodes?|"
        rf"events?|spells?|absences?|convulsions?|spasms?|attacks?|myoclonics?|"
        rf"jerks?|auras?|status epilepticus)\s+during\s+sleep\s+and\s+"
        rf"(?P<count_b>{DIARY_COUNT_TOKEN})\s+while\s+awake\.\s+In\s+"
        rf"(?P<second_month>{MONTH_NAME_PATTERN})\s+(?:he|she)\s+had\s+"
        rf"(?P<count_c>{DIARY_COUNT_TOKEN})\s+in\s+sleep\s+and\s+"
        rf"(?P<count_d>{DIARY_COUNT_TOKEN})\s+while\s+awake)\b",
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

SLEEP_AWAKE_DIRECT_MONTH_SUMMARY_RULE = RuleSpec(
    rule_id="diary.sleep_awake_direct_month_summary",
    group=RuleGroup.DIARY_LOG_AGGREGATION,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Two-month diary summary with direct in-sleep and awake counts.",
    pattern=re.compile(
        rf"\b(?P<evidence>In\s+(?P<first_month>{MONTH_NAME_PATTERN})\s+"
        rf"(?:he|she)\s+had\s+(?P<count_a>{DIARY_COUNT_TOKEN})\s+in\s+sleep\s+"
        rf"and\s+(?P<count_b>{DIARY_COUNT_TOKEN})\s+while\s+awake\.\s+In\s+"
        rf"(?P<second_month>{MONTH_NAME_PATTERN})\s+(?:he|she)\s+had\s+"
        rf"(?P<count_c>{DIARY_COUNT_TOKEN})\s+in\s+sleep\s+and\s+"
        rf"(?P<count_d>{DIARY_COUNT_TOKEN})\s+while\s+awake)\b",
        re.IGNORECASE,
    ),
    build=_build_sleep_awake_month_summary,
    examples=(
        RuleExample(
            text=(
                "Clinic Date: 7 May 2023. In Feb he had 3 in sleep and one while "
                "awake. In Apr he had five in sleep and no while awake."
            ),
            expected_label="9 per 3 month",
            expected_evidence=(
                "In Feb he had 3 in sleep and one while awake. In Apr he had five "
                "in sleep and no while awake"
            ),
        ),
    ),
    provenance="Diary/log V1 expression.",
)

SLEEP_AWAKE_NOCTURNAL_DAYTIME_SUMMARY_RULE = RuleSpec(
    rule_id="diary.sleep_awake_nocturnal_daytime_summary",
    group=RuleGroup.DIARY_LOG_AGGREGATION,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Two-month diary summary split into nocturnal and daytime/awake counts.",
    pattern=re.compile(
        rf"\b(?P<evidence>In\s+(?P<first_month>{MONTH_NAME_PATTERN})\s+"
        rf"(?:he|she)\s+had\s+(?P<count_a>{DIARY_COUNT_TOKEN})\s+nocturnal\s+"
        rf"(?:{SEIZURE_TERMS})\s+but\s+(?P<count_b>{DIARY_COUNT_TOKEN})\s+"
        rf"daytime\s+events\.\s+In\s+(?P<second_month>{MONTH_NAME_PATTERN})\s+"
        rf"(?:he|she)\s+had\s+(?P<count_c>{DIARY_COUNT_TOKEN})\s+nocturnal\s+"
        rf"(?:{SEIZURE_TERMS})\s+and\s+(?P<count_d>{DIARY_COUNT_TOKEN})\s+"
        rf"while\s+awake)\b",
        re.IGNORECASE,
    ),
    build=_build_sleep_awake_month_summary,
    examples=(
        RuleExample(
            text=(
                "Clinic Date: 25 July 2014. In Jun he had a nocturnal seizure but "
                "no daytime events. In July he had three nocturnal seizures and "
                "5 while awake."
            ),
            expected_label="9 per 2 month",
            expected_evidence=(
                "In Jun he had a nocturnal seizure but no daytime events. In July "
                "he had three nocturnal seizures and 5 while awake"
            ),
        ),
    ),
    provenance="Diary/log V1 expression.",
)

SLEEP_AWAKE_MONTH_SUMMARY_RULES = (
    SLEEP_AWAKE_MONTH_SUMMARY_RULE,
    SLEEP_AWAKE_DIRECT_MONTH_SUMMARY_RULE,
    SLEEP_AWAKE_NOCTURNAL_DAYTIME_SUMMARY_RULE,
)

MONTHLY_DIARY_SUMMARY_RULES = (
    RuleSpec(
        rule_id="diary.monthly_summary.two_sentence_month_timeline",
        group=RuleGroup.DIARY_LOG_AGGREGATION,
        portability=Portability.SEIZURE_FREQUENCY,
        description="Two-sentence month timeline with counted seizure events.",
        pattern=re.compile(
            rf"(?:^|(?<=[.;:]\s))(?P<evidence>In\s+(?:{MONTH_NAME_PATTERN})\s+[^.]+?\.\s+"
            rf"In\s+(?:{MONTH_NAME_PATTERN})\s+[^.]+)\b",
            re.IGNORECASE,
        ),
        build=_monthly_diary_summary_builder(
            "diary.monthly_summary.two_sentence_month_timeline"
        ),
        examples=(
            RuleExample(
                text=(
                    "In September a prolonged focal seizure settled spontaneously. "
                    "In November a tonic seizure was recorded, and in February another "
                    "during physiotherapy."
                ),
                expected_label="3 per 6 month",
                expected_evidence=(
                    "In September a prolonged focal seizure settled spontaneously. "
                    "In November a tonic seizure was recorded, and in February another "
                    "during physiotherapy"
                ),
            ),
        ),
        provenance="Diary/log V1 expression restored during baseline-drift audit.",
    ),
    RuleSpec(
        rule_id="diary.monthly_summary.event_occurred_timeline",
        group=RuleGroup.DIARY_LOG_AGGREGATION,
        portability=Portability.SEIZURE_FREQUENCY,
        description="Sparse month timeline beginning with an event-occurred sentence.",
        pattern=re.compile(
            rf"\b(?P<evidence>(?:A|An)\s+(?:prolonged\s+)?"
            rf"(?:event|episode|seizure|convulsion)\s+occurred\s+in\s+"
            rf"(?:{MONTH_NAME_PATTERN})\s+(?:\([^)]+\)\s*)?[^.]*\.\s+"
            rf"In\s+(?:{MONTH_NAME_PATTERN})\s+[^.]+)\b",
            re.IGNORECASE,
        ),
        build=_monthly_diary_summary_builder(
            "diary.monthly_summary.event_occurred_timeline"
        ),
        examples=(
            RuleExample(
                text=(
                    "A prolonged event occurred in Apr (approximately 12 minutes). "
                    "In Jul she had a drop attack, and in Sep seven myoclonic jerks "
                    "were documented at college."
                ),
                expected_label="9 per 6 month",
                expected_evidence=(
                    "A prolonged event occurred in Apr (approximately 12 minutes). "
                    "In Jul she had a drop attack, and in Sep seven myoclonic jerks "
                    "were documented at college"
                ),
            ),
        ),
        provenance="Diary/log V1 expression restored during baseline-drift audit.",
    ),
    RuleSpec(
        rule_id="diary.monthly_summary.recent_reported",
        group=RuleGroup.DIARY_LOG_AGGREGATION,
        portability=Portability.SEIZURE_FREQUENCY,
        description="Recent monthly diary count summary with reported events.",
        pattern=re.compile(
            r"\b(?P<evidence>(?:She|He)\s+has\s+had\s+[^.]+?,\s+"
            r"with\s+events\s+reported\b)",
            re.IGNORECASE,
        ),
        build=_monthly_diary_summary_builder("diary.monthly_summary.recent_reported"),
        examples=(
            RuleExample(
                text=(
                    "She has had no seizures so far this month, four in August, "
                    "one in July and 3 in June, with events reported from both "
                    "daytime and nocturnal periods."
                ),
                expected_label="8 per 4 month",
                expected_evidence=(
                    "She has had no seizures so far this month, four in August, "
                    "one in July and 3 in June"
                ),
            ),
        ),
        provenance="Diary/log V1 expression.",
    ),
    RuleSpec(
        rule_id="diary.monthly_summary.experienced_or_had",
        group=RuleGroup.DIARY_LOG_AGGREGATION,
        portability=Portability.SEIZURE_FREQUENCY,
        description="Recent monthly diary count summary with experienced/had lead-in.",
        pattern=re.compile(
            r"\b(?P<evidence>(?:She|He)\s+(?:experienced|had)\s+[^.]+?,\s+"
            r"occurring\s+during\b)",
            re.IGNORECASE,
        ),
        build=_monthly_diary_summary_builder("diary.monthly_summary.experienced_or_had"),
        examples=(
            RuleExample(
                text=(
                    "He experienced 2 generalised tonic-clonic seizures so far in "
                    "Sep, one in Aug, and 0 in Jul, occurring during both wakefulness "
                    "and sleep."
                ),
                expected_label="3 per 3 month",
                expected_evidence=(
                    "2 generalised tonic-clonic seizures so far in Sep, one in Aug, "
                    "and 0 in Jul"
                ),
            ),
        ),
        provenance="Diary/log V1 expression.",
    ),
    RuleSpec(
        rule_id="diary.monthly_summary.this_month_so_far",
        group=RuleGroup.DIARY_LOG_AGGREGATION,
        portability=Portability.SEIZURE_FREQUENCY,
        description="This-month-so-far diary count summary.",
        pattern=re.compile(
            r"\b(?P<evidence>This\s+month\s+so\s+far\s+[^.]+?,\s+over\s+waking\b)",
            re.IGNORECASE,
        ),
        build=_monthly_diary_summary_builder("diary.monthly_summary.this_month_so_far"),
        examples=(
            RuleExample(
                text=(
                    "This month so far she has no seizures; earlier 4 in February, "
                    "0 in January and 7 in December, over waking hours and sleep."
                ),
                expected_label="11 per 4 month",
                expected_evidence=(
                    "This month so far she has no seizures; earlier 4 in February, "
                    "0 in January and 7 in December"
                ),
            ),
        ),
        provenance="Diary/log V1 expression.",
    ),
    RuleSpec(
        rule_id="diary.monthly_summary.reported_list",
        group=RuleGroup.DIARY_LOG_AGGREGATION,
        portability=Portability.SEIZURE_FREQUENCY,
        description="Reported or recorded month-count list.",
        pattern=re.compile(
            r"\b(?P<evidence>(?:She|He)\s+(?:reports|has\s+recorded)\s+[^.]+?,\s+"
            r"(?:from\s+both|including)\b)",
            re.IGNORECASE,
        ),
        build=_monthly_diary_summary_builder("diary.monthly_summary.reported_list"),
        examples=(
            RuleExample(
                text=(
                    "He reports 6 seizure events in September, 6 in August and "
                    "four in July, and 2 in June, from both daytime and nocturnal periods."
                ),
                expected_label="18 per 4 month",
                expected_evidence=(
                    "He reports 6 seizure events in September, 6 in August and "
                    "four in July, and 2 in June"
                ),
            ),
        ),
        provenance="Diary/log V1 expression.",
    ),
    RuleSpec(
        rule_id="diary.monthly_summary.had_both_from",
        group=RuleGroup.DIARY_LOG_AGGREGATION,
        portability=Portability.SEIZURE_FREQUENCY,
        description="Month-count list with had lead-in and both-from state summary.",
        pattern=re.compile(
            r"\b(?P<evidence>(?:She|He)\s+had\s+[^.]+?\s+both\s+from\b)",
            re.IGNORECASE,
        ),
        build=_monthly_diary_summary_builder("diary.monthly_summary.had_both_from"),
        examples=(
            RuleExample(
                text=(
                    "She had a convulsion so far in September, 6 in August, six in "
                    "July, four in June both from being awake and asleep."
                ),
                expected_label="17 per 4 month",
                expected_evidence=(
                    "She had a convulsion so far in September, 6 in August, six in "
                    "July, four in June"
                ),
            ),
        ),
        provenance="Diary/log V1 expression restored during baseline-drift audit.",
    ),
    RuleSpec(
        rule_id="diary.monthly_summary.noted_all_from",
        group=RuleGroup.DIARY_LOG_AGGREGATION,
        portability=Portability.SEIZURE_FREQUENCY,
        description="Noted month-count list with all-from state summary.",
        pattern=re.compile(
            r"\b(?P<evidence>(?:She|He)\s+noted\s+[^.]+?,\s+all\s+from\b)",
            re.IGNORECASE,
        ),
        build=_monthly_diary_summary_builder("diary.monthly_summary.noted_all_from"),
        examples=(
            RuleExample(
                text=(
                    "She noted no seizures in June, four in May, and four in April, "
                    "all from mixed states."
                ),
                expected_label="8 per 3 month",
                expected_evidence="She noted no seizures in June, four in May, and four in April",
            ),
        ),
        provenance="Diary/log V1 expression.",
    ),
    RuleSpec(
        rule_id="diary.monthly_summary.this_month_extended",
        group=RuleGroup.DIARY_LOG_AGGREGATION,
        portability=Portability.SEIZURE_FREQUENCY,
        description="This-month diary summary with earlier month counts.",
        pattern=re.compile(
            r"\b(?P<evidence>This\s+month,\s+(?:she|he)\s+has\s+had\s+[^.]+?,\s+"
            r"across\b)",
            re.IGNORECASE,
        ),
        build=_monthly_diary_summary_builder("diary.monthly_summary.this_month_extended"),
        examples=(
            RuleExample(
                text=(
                    "This month, she has had six convulsions; 0 were in December "
                    "and 5 in November, across day and night."
                ),
                expected_label="11 per 3 month",
                expected_evidence=(
                    "This month, she has had six convulsions; 0 were in December "
                    "and 5 in November"
                ),
            ),
        ),
        provenance="Diary/log V1 expression.",
    ),
    RuleSpec(
        rule_id="diary.monthly_summary.as_of_this_month",
        group=RuleGroup.DIARY_LOG_AGGREGATION,
        portability=Portability.SEIZURE_FREQUENCY,
        description="As-of-this-month diary summary with prior month counts.",
        pattern=re.compile(
            r"\b(?P<evidence>As\s+of\s+this\s+month\s+(?:she|he)\s+reports\s+"
            r"[^.]+?\s+during\s+both\b)",
            re.IGNORECASE,
        ),
        build=_monthly_diary_summary_builder("diary.monthly_summary.as_of_this_month"),
        examples=(
            RuleExample(
                text=(
                    "As of this month she reports four seizure events; 3 in August, "
                    "three in July and five in June during both sleep and wakefulness."
                ),
                expected_label="15 per 4 month",
                expected_evidence=(
                    "As of this month she reports four seizure events; 3 in August, "
                    "three in July and five in June"
                ),
            ),
        ),
        provenance="Diary/log V1 expression.",
    ),
    RuleSpec(
        rule_id="diary.monthly_summary.sparse_cluster_event_list",
        group=RuleGroup.DIARY_LOG_AGGREGATION,
        portability=Portability.SEIZURE_FREQUENCY,
        description="Sparse month list with a cluster/run and later single events.",
        pattern=re.compile(
            rf"\b(?P<evidence>He\s+had\s+a\s+cluster\s+of\s+{NUMBER_TOKEN}\s+"
            rf"(?:{QUALIFIED_SEIZURE_TERMS})\s+in\s+(?:{MONTH_NAME_PATTERN}).+?"
            rf"a\s+single\s+(?:{QUALIFIED_SEIZURE_TERMS})\s+was\s+recorded)\b",
            re.IGNORECASE,
        ),
        build=_monthly_diary_summary_builder("diary.monthly_summary.sparse_cluster_event_list"),
        examples=(
            RuleExample(
                text=(
                    "He had a cluster of three seizures in August. In November he had "
                    "a nocturnal seizure, and in February a single tonic seizure was recorded."
                ),
                expected_label="5 per 7 month",
                expected_evidence=(
                    "He had a cluster of three seizures in August. In November he had "
                    "a nocturnal seizure, and in February a single tonic seizure was recorded"
                ),
            ),
        ),
        provenance="Diary/log V1 expression.",
    ),
    RuleSpec(
        rule_id="diary.monthly_summary.parenthetical_sparse_list",
        group=RuleGroup.DIARY_LOG_AGGREGATION,
        portability=Portability.SEIZURE_FREQUENCY,
        description="Sparse month list with parenthetical cluster detail.",
        pattern=re.compile(
            rf"\b(?P<evidence>He\s+had\s+a\s+cluster\s+of\s+{NUMBER_TOKEN}\s+"
            rf"(?:{QUALIFIED_SEIZURE_TERMS})\s+in\s+(?:{MONTH_NAME_PATTERN})\s+"
            rf"\([^)]+\)\.\s+In\s+(?:{MONTH_NAME_PATTERN})\s+[^.]+?,\s+"
            rf"and\s+in\s+(?:{MONTH_NAME_PATTERN})\s+a\s+single\s+"
            rf"(?:{QUALIFIED_SEIZURE_TERMS})\s+was\s+recorded)\b",
            re.IGNORECASE,
        ),
        build=_monthly_diary_summary_builder("diary.monthly_summary.parenthetical_sparse_list"),
        examples=(
            RuleExample(
                text=(
                    "He had a cluster of three seizures in Dec (short). In Feb he had "
                    "7 nocturnal seizures, and in Apr a single tonic seizure was recorded."
                ),
                expected_label="11 per 5 month",
                expected_evidence=(
                    "He had a cluster of three seizures in Dec (short). In Feb he had "
                    "7 nocturnal seizures, and in Apr a single tonic seizure was recorded"
                ),
            ),
        ),
        provenance="Diary/log V1 expression.",
    ),
    RuleSpec(
        rule_id="diary.monthly_summary.in_month_another",
        group=RuleGroup.DIARY_LOG_AGGREGATION,
        portability=Portability.SEIZURE_FREQUENCY,
        description="Sparse month list ending with another event.",
        pattern=re.compile(
            rf"\b(?P<evidence>In\s+(?:{MONTH_NAME_PATTERN})\s+[^.]+?\([^)]+\)\.\s+"
            rf"In\s+(?:{MONTH_NAME_PATTERN})\s+[^.]+?,\s+and\s+in\s+"
            rf"(?:{MONTH_NAME_PATTERN})\s+another)\b",
            re.IGNORECASE,
        ),
        build=_monthly_diary_summary_builder("diary.monthly_summary.in_month_another"),
        examples=(
            RuleExample(
                text=(
                    "In March he had a run of six seizures (brief). In June there was "
                    "two further seizures at night, and in August another during therapy."
                ),
                expected_label="9 per 6 month",
                expected_evidence=(
                    "In March he had a run of six seizures (brief). In June there was "
                    "two further seizures at night, and in August another"
                ),
            ),
        ),
        provenance="Diary/log V1 expression.",
    ),
    RuleSpec(
        rule_id="diary.monthly_summary.in_cluster_another",
        group=RuleGroup.DIARY_LOG_AGGREGATION,
        portability=Portability.SEIZURE_FREQUENCY,
        description="Sparse month list with in-a-cluster wording and another event.",
        pattern=re.compile(
            rf"\b(?P<evidence>In\s+(?:{MONTH_NAME_PATTERN})\s+[^.]+?\s+"
            rf"in\s+a\s+cluster\.\s+In\s+(?:{MONTH_NAME_PATTERN})\s+[^.]+?,\s+"
            rf"and\s+in\s+(?:{MONTH_NAME_PATTERN})\s+another)\b",
            re.IGNORECASE,
        ),
        build=_monthly_diary_summary_builder("diary.monthly_summary.in_cluster_another"),
        examples=(
            RuleExample(
                text=(
                    "In Apr she experienced four short absences in a cluster. "
                    "In Jul there was 2 further brief absences, and in Sep another."
                ),
                expected_label="7 per 6 month",
                expected_evidence=(
                    "In Apr she experienced four short absences in a cluster. "
                    "In Jul there was 2 further brief absences, and in Sep another"
                ),
            ),
        ),
        provenance="Diary/log V1 expression.",
    ),
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
    *SLEEP_AWAKE_MONTH_SUMMARY_RULES,
    *MONTHLY_DIARY_SUMMARY_RULES,
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


def _diary_count_token(value: str) -> int | None:
    normalized = value.strip().lower()
    if normalized in {"no", "none", "zero"}:
        return 0
    if normalized in {"a", "an", "another"}:
        return 1
    return _integer_number_token(normalized)


def _trim_monthly_diary_evidence(evidence: str) -> str:
    trimmed = _clean_evidence(evidence)
    trimmed = re.sub(
        r",?\s+(?:with events reported|occurring during|from both|including|"
        r"all from|over waking|across|during both)\b.*$",
        "",
        trimmed,
        flags=re.IGNORECASE,
    )
    trimmed = re.sub(
        rf"^((?:She|He)\s+)experienced\s+"
        rf"(?={DIARY_COUNT_TOKEN}\s+(?:{QUALIFIED_SEIZURE_TERMS}).*?\bso\s+far\s+in\s+"
        rf"(?:{MONTH_NAME_PATTERN})\b)",
        "",
        trimmed,
        flags=re.IGNORECASE,
    )
    trimmed = re.sub(
        rf"(\band\s+in\s+(?:{MONTH_NAME_PATTERN})\s+another)\s+at\s+\w+$",
        r"\1",
        trimmed,
        flags=re.IGNORECASE,
    )
    trimmed = re.sub(
        rf"(\band\s+in\s+(?:{MONTH_NAME_PATTERN})\s+another)\s+during\s+.+$",
        r"\1",
        trimmed,
        flags=re.IGNORECASE,
    )
    trimmed = re.sub(
        rf"(\band\s+in\s+(?:{MONTH_NAME_PATTERN})\s+a\s+single\s+"
        rf"(?:{QUALIFIED_SEIZURE_TERMS})\s+was\s+recorded)\s+during\s+.+$",
        r"\1",
        trimmed,
        flags=re.IGNORECASE,
    )
    return _clean_evidence(trimmed)


def _monthly_diary_counts(
    evidence: str, clinic_date: object, context: ExtractionContext
) -> tuple[int, int] | None:
    relative_note_date = cast(
        Callable[[str, object | None], object | None],
        context.helper("relative_note_date"),
    )
    month_span_inclusive = cast(
        Callable[[object | None, object | None], int | None],
        context.helper("month_span_inclusive"),
    )
    month_totals: dict[tuple[int, int], int] = {}
    compact_months: set[tuple[int, int]] = set()

    def date_key(date: object) -> tuple[int, int]:
        month_date = cast(_MonthDate, date)
        return month_date.year, month_date.month

    def add(month_text: str, raw_count: str) -> None:
        date = relative_note_date(month_text, clinic_date)
        count = _diary_count_token(raw_count)
        if date is None or count is None:
            return
        key = date_key(date)
        month_totals[key] = month_totals.get(key, 0) + count
        compact_months.add(key)

    def add_month_date(date: object, raw_count: str) -> None:
        count = _diary_count_token(raw_count)
        if count is None:
            return
        key = date_key(date)
        month_totals[key] = month_totals.get(key, 0) + count

    this_month_patterns = [
        rf"(?P<count>{DIARY_COUNT_TOKEN})\s+(?:{QUALIFIED_SEIZURE_TERMS})\s+"
        rf"so\s+far\s+this\s+month",
        rf"this\s+month\s+so\s+far\s+\w+\s+has\s+"
        rf"(?P<count>{DIARY_COUNT_TOKEN})\s+(?:{QUALIFIED_SEIZURE_TERMS})",
        rf"this\s+month,?\s+\w+\s+has\s+had\s+"
        rf"(?P<count>{DIARY_COUNT_TOKEN})\s+(?:{QUALIFIED_SEIZURE_TERMS})",
        rf"as\s+of\s+this\s+month\s+\w+\s+reports\s+"
        rf"(?P<count>{DIARY_COUNT_TOKEN})\s+(?:{QUALIFIED_SEIZURE_TERMS})",
    ]
    for pattern in this_month_patterns:
        for match in re.finditer(pattern, evidence, flags=re.IGNORECASE):
            count = _diary_count_token(match.group("count"))
            if count is not None:
                key = date_key(clinic_date)
                month_totals[key] = month_totals.get(key, 0) + count
                compact_months.add(key)

    single_to_date_month = re.compile(
        rf"\b(?P<count>a|an)\s+(?:{QUALIFIED_SEIZURE_TERMS})\s+"
        rf"(?:to\s+date\s+|so\s+far\s+)in\s+(?P<month>{MONTH_NAME_PATTERN})\b",
        re.IGNORECASE,
    )
    for match in single_to_date_month.finditer(evidence):
        add(match.group("month"), match.group("count"))

    event_occurred_month = re.compile(
        rf"\b(?:a|an)\s+(?:prolonged\s+)?(?:event|episode|seizure|convulsion)\s+"
        rf"occurred\s+in\s+(?P<month>{MONTH_NAME_PATTERN})\b",
        re.IGNORECASE,
    )
    for match in event_occurred_month.finditer(evidence):
        add(match.group("month"), "a")

    cluster_or_run_count_month = re.compile(
        rf"\b(?:cluster|run)\s+of\s+(?P<count>{NUMBER_VALUE_TOKEN})\s+"
        rf"(?:{QUALIFIED_SEIZURE_TERMS})\s+in\s+(?P<month>{MONTH_NAME_PATTERN})\b",
        re.IGNORECASE,
    )
    for match in cluster_or_run_count_month.finditer(evidence):
        add(match.group("month"), match.group("count"))

    count_before_month = re.compile(
        rf"\b(?P<count>no|none|zero|{NUMBER_VALUE_TOKEN})\s+"
        rf"(?:(?:{QUALIFIED_SEIZURE_TERMS}|events?)\s+)?"
        rf"(?:to\s+date\s+|so\s+far\s+)?"
        rf"in\s+(?P<month>{MONTH_NAME_PATTERN})\b",
        re.IGNORECASE,
    )
    for match in count_before_month.finditer(evidence):
        preceding = evidence[max(0, match.start() - 16) : match.start()].lower()
        if re.search(r"\b(?:cluster|run)\s+of\s+$", preceding):
            continue
        add(match.group("month"), match.group("count"))

    count_were_month = re.compile(
        rf"\b(?P<count>no|none|zero|{NUMBER_VALUE_TOKEN})\s+were\s+"
        rf"in\s+(?P<month>{MONTH_NAME_PATTERN})\b",
        re.IGNORECASE,
    )
    for match in count_were_month.finditer(evidence):
        add(match.group("month"), match.group("count"))

    month_leading = re.compile(
        rf"\b(?:and\s+)?in\s+(?P<month>{MONTH_NAME_PATTERN})\b(?P<body>.*?)"
        rf"(?=\b(?:and\s+)?in\s+(?:{MONTH_NAME_PATTERN})\b|[.;]|$)",
        re.IGNORECASE,
    )
    count_in_month_body = re.compile(
        rf"\b(?:cluster|run)\s+of\s+(?P<run_count>{NUMBER_VALUE_TOKEN})\s+"
        rf"(?:{QUALIFIED_SEIZURE_TERMS})\b"
        rf"|"
        rf"\b(?P<count>no|none|zero|{NUMBER_VALUE_TOKEN})\s+"
        rf"(?:further\s+)?(?:[\w-]+\s+){{0,3}}?"
        rf"(?:{SEIZURE_TERMS}|events?|while\s+awake|in\s+sleep|daytime|nocturnal)\b"
        rf"|\b(?P<single>a|an)\s+(?!run\s+of\b|cluster\s+of\b)"
        rf"(?:[\w-]+\s+){{0,3}}(?:{SEIZURE_TERMS}|events?)\b"
        rf"|\b(?P<another>another)\b",
        re.IGNORECASE,
    )
    for match in month_leading.finditer(evidence):
        date = relative_note_date(match.group("month"), clinic_date)
        if date is None:
            continue
        key = date_key(date)
        if key in compact_months:
            continue
        body = match.group("body")
        for count_match in count_in_month_body.finditer(body):
            raw_count = (
                count_match.groupdict().get("run_count")
                or count_match.groupdict().get("count")
                or count_match.groupdict().get("single")
                or count_match.groupdict().get("another")
            )
            if raw_count is not None:
                add_month_date(date, raw_count)

    if not month_totals:
        return None
    dates = [_MonthDate(year=year, month=month) for year, month in month_totals]
    start = min(dates, key=lambda date: (date.year, date.month))
    end = max(dates, key=lambda date: (date.year, date.month))
    denominator = month_span_inclusive(start, end)
    if denominator is None:
        denominator = len(month_totals)
    return sum(month_totals.values()), denominator


class _MonthDate:
    def __init__(self, *, year: int, month: int) -> None:
        self.year = year
        self.month = month


def _singular_unit(value: str) -> str:
    normalized = value.lower().strip()
    return normalized[:-1] if normalized.endswith("s") else normalized


def _clean_evidence(evidence: str) -> str:
    return evidence.strip(" .;:\n\t")
