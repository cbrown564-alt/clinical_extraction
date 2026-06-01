from __future__ import annotations

import re

from .candidates import (
    CandidateKind,
    RawCandidate,
)
from .deterministic_candidate_pruning import (
    has_historical_lead_in as _has_historical_lead_in,
)
from .deterministic_frequency_tokens import (
    NUMBER_TOKEN,
    NUMBER_VALUE_TOKEN,
    UNIT_TOKEN,
)
from .deterministic_frequency_tokens import (
    increment_number_token as _increment_number_token,
)
from .deterministic_frequency_tokens import (
    integer_number_token as _integer_number_token,
)
from .deterministic_frequency_tokens import (
    rate_label as _rate_label,
)
from .deterministic_rate_distractors import (
    is_medication_or_dose_rate_distractor as _is_medication_or_dose_rate_distractor,
)
from .deterministic_rate_terms import (
    QUALIFIED_SEIZURE_TERMS,
    SEIZURE_DESCRIPTOR_PHRASE,
    SEIZURE_RATE_PHRASE,
    SEIZURE_TERMS,
    SEIZURE_TYPE_DESCRIPTOR,
    WORD_TOKEN,
)
from .deterministic_text import (
    clean_evidence as _clean_evidence,
)
from .rule_metadata import (
    AblationConfig,
)
from .rules.diary import (
    DIARY_DATE_LIST_RULE,
    INCREASING_MONTHLY_COUNT_RULE,
    MONTHLY_COUNT_LOG_RULE,
    MONTHLY_DIARY_SUMMARY_RULES,
    RECORDED_MONTH_LOG_RULE,
    SEIZURE_DAY_LOG_RULE,
    SEIZURE_DAYS_FRACTION_RULE,
    SEIZURE_DAYS_PER_PERIOD_RULE,
    SLEEP_AWAKE_MONTH_SUMMARY_RULES,
    SPARSE_FULL_MONTH_LOG_RULE,
    apply_diary_rules,
)
from .rules.gan_shorthand import (
    ABS_ADJECTIVE_RATE_RULE,
    ABS_COUNT_RATE_RULE,
    Q_INTERVAL_RULE,
    TC_SZ_COUNT_RATE_RULE,
    apply_gan_shorthand_rules,
)
from .rules.rate import (
    COUNT_DURING_RECENT_WINDOW_RULE,
    COUNTED_ADVERBIAL_RATE_RULE,
    DAILY_BASIS_CURRENT_RULE,
    DAYS_OF_WEEK_RATE_RULE,
    DESCRIPTOR_RATE_RULE,
    DIRECT_RATE_RULE,
    IMPLICIT_EVERY_OTHER_INTERVAL_RULE,
    IMPLICIT_INTERVAL_RULE,
    IMPLICIT_NIGHTLY_INTERVAL_RULE,
    NIGHTS_PER_PERIOD_RULE,
    NO_MORE_THAN_ADVERBIAL_RATE_RULE,
    OCCURRING_ADJECTIVE_RATE_RULE,
    OCCURRING_EVERY_OTHER_INTERVAL_RULE,
    OCCURRING_INTERVAL_RULE,
    OCCURRING_ONCE_PER_NIGHT_RULE,
    PERIOD_FIRST_EXPERIENCED_COUNT_RULE,
    PERIOD_FIRST_FEATURING_COUNT_RULE,
    PERIOD_FIRST_OCCURRED_COUNT_RULE,
    PERIOD_FIRST_RECENT_COUNT_RULE,
    PERIOD_FIRST_TIMEFRAME_COUNT_RULE,
    PERSISTENT_ADVERBIAL_RATE_RULE,
    QUALIFIED_DIRECT_RATE_RULE,
    QUARTER_DIRECT_RATE_RULE,
    RECENT_COUNT_RULE,
    RECORDED_YEAR_COUNT_RULE,
    SEIZURE_ADJECTIVE_RATE_RULE,
    SIMPLE_PARTIAL_ADVERBIAL_RATE_RULE,
    STANDALONE_ADJECTIVE_RATE_RULE,
    THERE_HAVE_BEEN_COUNT_RULE,
    YESTERDAY_OR_TODAY_COUNT_RULE,
    apply_rate_rules,
)
from .temporal import (
    MONTH_NAME_PATTERN,
    MONTH_YEAR_DATE_PATTERN,
)
from .temporal import (
    clinic_date as _clinic_date,
)
from .temporal import (
    month_span as _month_span,
)
from .temporal import (
    month_span_inclusive as _month_span_inclusive,
)
from .temporal import (
    month_span_with_terminal_partial as _month_span_with_terminal_partial,
)
from .temporal import (
    relative_note_date as _relative_note_date,
)
from .temporal import (
    year_month_date as _year_month_date,
)

_RawCandidate = RawCandidate


def _extract_distributed_count_candidates(text: str) -> list[_RawCandidate]:
    candidates: list[_RawCandidate] = []
    event_description = r"[a-z][a-z-]*(?:\s+[a-z][a-z-]*){0,4}"
    distributed_count = re.compile(
        rf"\b(?P<count_a>{NUMBER_VALUE_TOKEN})\s+{event_description}\s+and\s+"
        rf"(?P<count_b>{NUMBER_VALUE_TOKEN})\s+{event_description}\s+"
        rf"(?:(?:in|during)\s+)?(?:the\s+)?(?:last|past|this)\s+"
        rf"(?:(?P<denominator>{NUMBER_VALUE_TOKEN})\s+)?(?P<unit>{UNIT_TOKEN})\b",
        re.IGNORECASE,
    )
    for match in distributed_count.finditer(text):
        count_a = _integer_number_token(match.group("count_a"))
        count_b = _integer_number_token(match.group("count_b"))
        if count_a is None or count_b is None:
            continue
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(
                    str(count_a + count_b),
                    match.group("unit"),
                    match.groupdict().get("denominator"),
                ),
                evidence=_clean_evidence(match.group(0)),
            )
        )
    return candidates


def extract_rate_candidates(
    text: str, ablation_config: AblationConfig | None = None
) -> list[_RawCandidate]:
    ablation_config = ablation_config or AblationConfig()
    candidates: list[_RawCandidate] = []
    remission_then_breakthrough = re.compile(
        rf"\bseizure[- ]free\s+for\s+(?P<denominator>{NUMBER_TOKEN})\s+"
        rf"(?P<unit>months?|years?)"
        rf".{{0,180}}?\b(?:before\s+experiencing|until)\b"
        rf".{{0,140}}?\b(?:{SEIZURE_TERMS})\b"
        rf"(?:\s+occurred)?(?:\s+(?:{NUMBER_TOKEN})\s+\w+days?\s+ago)?"
        rf"(?:.{{0,80}}?\bpreceded\s+by\s+a\s+cluster\s+of\s+absences\b)?",
        re.IGNORECASE,
    )
    for match in remission_then_breakthrough.finditer(text):
        evidence = _clean_evidence(match.group(0))
        count = "2" if "preceded by a cluster of absences" in evidence.lower() else "1"
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(count, match.group("unit"), match.group("denominator")),
                evidence=evidence,
            )
        )

    no_seizures_then_count = re.compile(
        rf"\bno\s+(?:{SEIZURE_TERMS})\s+for\s+nearly\s+a\s+(?P<unit>year|month)"
        rf".{{0,180}}?\bleading\s+to\s+(?P<count>{NUMBER_TOKEN})\s+"
        rf"(?:{QUALIFIED_SEIZURE_TERMS})\b"
        rf"(?:\s+(?:{NUMBER_TOKEN})\s+\w+days?\s+ago)?",
        re.IGNORECASE,
    )
    for match in no_seizures_then_count.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(match.group("count"), match.group("unit")),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    no_seizures_then_single_breakthrough = re.compile(
        rf"\b(?P<evidence>no\s+(?:{SEIZURE_TERMS})\s+for\s+nearly\s+a\s+"
        rf"(?P<unit>year|month).{{0,160}}?\bleading\s+to\s+a\s+"
        rf"(?:{QUALIFIED_SEIZURE_TERMS})(?:\s+{NUMBER_TOKEN}\s+\w+\s+ago)?)\b",
        re.IGNORECASE,
    )
    for match in no_seizures_then_single_breakthrough.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label("1", match.group("unit")),
                evidence=_clean_evidence(match.group("evidence")),
            )
        )

    no_seizures_then_precursor_count = re.compile(
        rf"\b(?P<evidence>did\s+not\s+have\s+(?:{SEIZURE_TERMS})\s+for\s+"
        rf"over\s+(?P<denominator>{NUMBER_TOKEN})\s+(?P<unit>months?|years?),?\s+"
        rf"but\s+then\s+reported\s+(?P<count>{NUMBER_TOKEN})\s+"
        rf"(?:{QUALIFIED_SEIZURE_TERMS})(?:\s+{NUMBER_TOKEN}\s+\w+\s+ago)?,\s+"
        rf"each\s+preceded\s+by\s+myoclonic\s+jerks)\b",
        re.IGNORECASE,
    )
    for match in no_seizures_then_precursor_count.finditer(text):
        precursor_count = _integer_number_token(match.group("count"))
        if precursor_count is None:
            continue
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(
                    str(precursor_count * 2),
                    match.group("unit"),
                    match.group("denominator"),
                ),
                evidence=_clean_evidence(match.group("evidence")),
            )
        )

    medication_withdrawal_burst = re.compile(
        rf"\b(?:discontinued|came off|stopped|withdrew from)\s+"
        rf"(?:{WORD_TOKEN}\s+){{0,4}}(?:on\s+)?(?P<start_date>"
        rf"\d{{1,2}}(?:[-/ ](?:{MONTH_NAME_PATTERN}))|"
        rf"\d{{1,2}}\s+(?:{MONTH_NAME_PATTERN}))\b"
        rf".{{0,120}}?\b(?P<evidence>"
        rf"(?:Shortly afterwards|Soon afterwards|In the following week|"
        rf"Around that period|At that time),?\s+"
        rf"(?:she|he|they)\s+(?:experienced|had|reported)\s+"
        rf"(?P<count>{NUMBER_TOKEN})\s+(?:{QUALIFIED_SEIZURE_TERMS}))\b",
        re.IGNORECASE,
    )
    clinic_date = _clinic_date(text)
    for match in medication_withdrawal_burst.finditer(text):
        start_date = _relative_note_date(match.group("start_date"), clinic_date)
        denominator = _month_span(start_date, clinic_date)
        if denominator is None:
            continue
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(match.group("count"), "month", str(denominator)),
                evidence=_clean_evidence(match.group("evidence")),
            )
        )

    initial_second_event = re.compile(
        rf"\b(?P<evidence>(?:His|Her|The)\s+(?:initial|first)\s+"
        rf"(?:event|seizure)\s+(?:was|was reported)\s+in\s+"
        rf"(?P<first_month>{MONTH_NAME_PATTERN})\s+(?P<first_year>\d{{4}})"
        rf".{{0,180}}?\b(?:A\s+second|The\s+second)\s+event\s+"
        rf"(?:occurred|took place)\s+.*?\b(?:the\s+following\s+)?"
        rf"(?P<second_month>{MONTH_NAME_PATTERN})\s+(?P<second_year>\d{{4}}))\b",
        re.IGNORECASE,
    )
    for match in initial_second_event.finditer(text):
        start_date = _year_month_date(match.group("first_year"), match.group("first_month"))
        end_date = _year_month_date(match.group("second_year"), match.group("second_month"))
        denominator = _month_span(start_date, end_date)
        if denominator is None:
            continue
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label("2", "month", str(denominator)),
                evidence=_clean_evidence(match.group("evidence")),
            )
        )

    first_second_third_event = re.compile(
        rf"\b(?P<evidence>The\s+first\s+seizure\s+was\s+reported\s+in\s+"
        rf"(?P<first_month>{MONTH_NAME_PATTERN})\s+(?P<first_year>\d{{4}})"
        rf".{{0,180}}?\bThe\s+second\s+and\s+third\s+event\s+took\s+place\s+in\s+"
        rf"(?P<second_month>{MONTH_NAME_PATTERN})\s+(?P<second_year>\d{{4}}))\b",
        re.IGNORECASE,
    )
    for match in first_second_third_event.finditer(text):
        start_date = _year_month_date(match.group("first_year"), match.group("first_month"))
        end_date = _year_month_date(match.group("second_year"), match.group("second_month"))
        denominator = _month_span(start_date, end_date)
        if denominator is None:
            continue
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label("3", "month", str(denominator)),
                evidence=_clean_evidence(match.group("evidence")),
            )
        )

    first_next_event_narrative = re.compile(
        rf"\b(?P<evidence>(?:His|Her|He|She)\s+first\s+"
        rf"(?:(?:experienced|had)\s+a\s+)?seizure\s+"
        rf"(?:occurred\s+)?(?:was\s+)?in\s+"
        rf"(?P<first_month>{MONTH_NAME_PATTERN})\s+(?P<first_year>\d{{4}})"
        rf".{{0,180}}?\b(?:His|Her|The)\s+"
        rf"(?:(?P<next_count_before>{NUMBER_TOKEN})\s+)?"
        rf"(?P<next_phrase>next|second(?:\s+and\s+third)?)\s+"
        rf"(?:(?P<next_count_after>{NUMBER_TOKEN})\s+)?"
        rf"(?:seizures?|events?)\s+(?:came|was|occurred|took\s+place)\s+in\s+"
        rf"(?P<second_month>{MONTH_NAME_PATTERN})\s+(?P<second_year>\d{{4}}))\b",
        re.IGNORECASE,
    )
    for match in first_next_event_narrative.finditer(text):
        start_date = _year_month_date(match.group("first_year"), match.group("first_month"))
        end_date = _year_month_date(match.group("second_year"), match.group("second_month"))
        denominator = _month_span(start_date, end_date)
        if denominator is None:
            continue
        next_count = match.groupdict().get("next_count_before") or match.groupdict().get(
            "next_count_after"
        )
        if next_count is not None:
            additional_events = _integer_number_token(next_count)
        elif "third" in match.group("next_phrase").lower():
            additional_events = 2
        else:
            additional_events = 1
        if additional_events is None:
            continue
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(str(1 + additional_events), "month", str(denominator)),
                evidence=_clean_evidence(match.group("evidence")),
            )
        )

    residual_jerks_since_date = re.compile(
        rf"\b(?P<evidence>No\s+further\s+(?:{QUALIFIED_SEIZURE_TERMS})\s+"
        rf"have\s+occurred\s+since\s+(?P<start_date>"
        rf"{MONTH_YEAR_DATE_PATTERN}),?\s+although\s+"
        rf"(?P<count>{NUMBER_TOKEN})\s+(?:single\s+)?jerks?\s+remain)\b",
        re.IGNORECASE,
    )
    for match in residual_jerks_since_date.finditer(text):
        start_date = _relative_note_date(match.group("start_date"), clinic_date)
        denominator = _month_span(start_date, clinic_date)
        if denominator is None:
            continue
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(match.group("count"), "month", str(denominator)),
                evidence=_clean_evidence(match.group("evidence")),
            )
        )

    last_tonic_clonic_with_jerks = re.compile(
        rf"\b(?P<evidence>Last\s+tonic[-‑–—]clonic\s+seizure\s+was\s+in\s+"
        rf"(?P<start_date>{MONTH_YEAR_DATE_PATTERN}),?\s+with\s+"
        rf"(?P<count>{NUMBER_TOKEN})\s+morning\s+jerks\s+since\s+then)\b",
        re.IGNORECASE,
    )
    for match in last_tonic_clonic_with_jerks.finditer(text):
        start_date = _relative_note_date(match.group("start_date"), clinic_date)
        denominator = _month_span(start_date, clinic_date)
        total_count = _increment_number_token(match.group("count"))
        if denominator is None or total_count is None:
            continue
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(total_count, "month", str(denominator)),
                evidence=_clean_evidence(match.group("evidence")),
            )
        )

    clearly_witnessed_tonic_clonic_with_jerks = re.compile(
        rf"\b(?:Her|His|The)\s+(?P<evidence>last\s+clearly\s+witnessed\s+"
        rf"tonic[-‑–—]clonic\s+seizure\s+was\s+in\s+"
        rf"(?P<start_date>{MONTH_YEAR_DATE_PATTERN}),?\s+with\s+"
        rf"(?P<count>{NUMBER_TOKEN})\s+morning\s+jerks\s+since\s+then)\b",
        re.IGNORECASE,
    )
    for match in clearly_witnessed_tonic_clonic_with_jerks.finditer(text):
        start_date = _relative_note_date(match.group("start_date"), clinic_date)
        denominator = _month_span(start_date, clinic_date)
        if denominator is None:
            continue
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(match.group("count"), "month", str(denominator)),
                evidence=_clean_evidence(match.group("evidence")),
            )
        )

    candidates.extend(
        apply_rate_rules(
            (DAILY_BASIS_CURRENT_RULE, DAYS_OF_WEEK_RATE_RULE),
            text,
            ablation_config,
        )
    )

    cluster_spacing_interval = re.compile(
        rf"\b(?P<evidence>(?:{SEIZURE_RATE_PHRASE})\s+typically\s+occur\s+in\s+"
        rf"clusters?,\s+generally\s+spaced\s+(?P<denominator>{NUMBER_TOKEN})\s+"
        rf"(?P<unit>days?|weeks?|months?)\s+apart)\b",
        re.IGNORECASE,
    )
    for match in cluster_spacing_interval.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label("1", match.group("unit"), match.group("denominator")),
                evidence=_clean_evidence(match.group("evidence")),
            )
        )

    candidates.extend(apply_rate_rules((NIGHTS_PER_PERIOD_RULE,), text, ablation_config))

    year_to_date_count = re.compile(
        rf"\b(?P<evidence>(?P<count>{NUMBER_TOKEN})\s+"
        rf"(?:{QUALIFIED_SEIZURE_TERMS})\s+"
        rf"(?:(?:reported|documented)\s+)?(?:so\s+far\s+this\s+year|"
        rf"this\s+year\s+to\s+date|in\s+\d{{4}}\s+so\s+far))\b",
        re.IGNORECASE,
    )
    for match in year_to_date_count.finditer(text):
        if clinic_date is None:
            continue
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(match.group("count"), "month", str(clinic_date.month)),
                evidence=_clean_evidence(match.group("evidence")),
            )
        )

    remission_then_drop_and_jerks = re.compile(
        rf"\b(?P<evidence>(?P<denominator>{NUMBER_TOKEN})\s+months?\s+remission,?\s+"
        rf"then\s+sustained\s+a\s+drop\s+attack(?:\s+\d+\s+\w+\s+ago)?,?\s+"
        rf"preceded\s+by\s+myoclonic\s+jerks)\b",
        re.IGNORECASE,
    )
    for match in remission_then_drop_and_jerks.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label("2", "month", match.group("denominator")),
                evidence=_clean_evidence(match.group("evidence")),
            )
        )

    last_episode_since_date = re.compile(
        rf"\b(?P<evidence>(?:His|Her|The)?\s*"
        rf"(?:last\s+(?:such\s+)?(?:event|episode)|most\s+recent\s+episode)\s+"
        rf"(?:was\s+)?(?:recorded\s+)?(?:occurred\s+)?on\s+"
        rf"(?P<start_date>\d{{1,2}}[-/ ](?:{MONTH_NAME_PATTERN})))\b",
        re.IGNORECASE,
    )
    for match in last_episode_since_date.finditer(text):
        start_date = _relative_note_date(match.group("start_date"), clinic_date)
        denominator = _month_span_with_terminal_partial(start_date, clinic_date)
        if denominator is None:
            continue
        evidence = _clean_evidence(match.group("evidence"))
        if evidence.lower().startswith("the last such episode"):
            evidence = evidence.removeprefix("The ")
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label("1", "month", str(denominator)),
                evidence=evidence,
            )
        )

    candidates.extend(
        apply_diary_rules(
            SLEEP_AWAKE_MONTH_SUMMARY_RULES,
            text,
            ablation_config,
            helpers={
                "clinic_date": _clinic_date,
                "relative_note_date": _relative_note_date,
                "month_span": _month_span,
            },
        )
    )

    candidates.extend(
        apply_diary_rules(
            MONTHLY_DIARY_SUMMARY_RULES,
            text,
            ablation_config,
            helpers={
                "clinic_date": _clinic_date,
                "relative_note_date": _relative_note_date,
                "month_span_inclusive": _month_span_inclusive,
            },
        )
    )
    candidates.extend(_extract_distributed_count_candidates(text))

    candidates.extend(apply_rate_rules((DESCRIPTOR_RATE_RULE,), text, ablation_config))
    candidates.extend(apply_rate_rules((QUALIFIED_DIRECT_RATE_RULE,), text, ablation_config))
    candidates.extend(apply_rate_rules((QUARTER_DIRECT_RATE_RULE,), text, ablation_config))

    candidates.extend(apply_rate_rules((DIRECT_RATE_RULE,), text, ablation_config))

    candidates.extend(apply_rate_rules((COUNT_DURING_RECENT_WINDOW_RULE,), text, ablation_config))

    candidates.extend(apply_rate_rules((THERE_HAVE_BEEN_COUNT_RULE,), text, ablation_config))

    over_period = re.compile(
        rf"\b(?P<count>{NUMBER_TOKEN})\s+"
        rf"(?:{QUALIFIED_SEIZURE_TERMS}|{SEIZURE_DESCRIPTOR_PHRASE})\s+"
        rf"(?:over|in|during|across)\s+(?:the\s+)?(?:last|past)?\s*"
        rf"(?:(?P<denominator>{NUMBER_TOKEN})\s+)?(?P<unit>{UNIT_TOKEN})\b",
        re.IGNORECASE,
    )
    for match in over_period.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(
                    match.group("count"),
                    match.group("unit"),
                    match.group("denominator"),
                ),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    candidates.extend(apply_rate_rules((IMPLICIT_INTERVAL_RULE,), text, ablation_config))

    candidates.extend(apply_rate_rules((IMPLICIT_NIGHTLY_INTERVAL_RULE,), text, ablation_config))

    candidates.extend(
        apply_rate_rules((IMPLICIT_EVERY_OTHER_INTERVAL_RULE,), text, ablation_config)
    )

    candidates.extend(apply_rate_rules((OCCURRING_INTERVAL_RULE,), text, ablation_config))

    candidates.extend(
        apply_rate_rules((OCCURRING_EVERY_OTHER_INTERVAL_RULE,), text, ablation_config)
    )

    fortnight_interval = re.compile(
        r"\bonce\s+in\s+a\s+fortnight\b",
        re.IGNORECASE,
    )
    for match in fortnight_interval.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label("1", "week", "2"),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    second_period_interval = re.compile(
        r"\bhappening\s+(?:about\s+|roughly\s+|approximately\s+)?every\s+second\s+"
        r"(?P<unit>day|week|month|year)\b",
        re.IGNORECASE,
    )
    for match in second_period_interval.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label("1", match.group("unit"), "2"),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    median_interval = re.compile(
        rf"\bmedian\s+inter-seizure\s+interval\s*(?:≈|~|=|is)?\s*"
        rf"(?P<denominator>{NUMBER_TOKEN})\s+(?P<unit>{UNIT_TOKEN})\b",
        re.IGNORECASE,
    )
    for match in median_interval.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label("1", match.group("unit"), match.group("denominator")),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    ranging_interval = re.compile(
        rf"\b(?:(?:{SEIZURE_TERMS})\s+occurring\s+with\s+|occurring\s+with\s+)?"
        rf"intervals\s+ranging\s+"
        rf"(?P<denominator>{NUMBER_TOKEN})\s+(?P<unit>{UNIT_TOKEN})\b",
        re.IGNORECASE,
    )
    for match in ranging_interval.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label("1", match.group("unit"), match.group("denominator")),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    standalone_every_interval = re.compile(
        rf"\bEvery\s+(?P<denominator>{NUMBER_TOKEN})\s+(?P<unit>{UNIT_TOKEN})"
        r"(?:\s+on\s+average)?\b",
        re.IGNORECASE,
    )
    for match in standalone_every_interval.finditer(text):
        if _has_historical_lead_in(text, match.start()):
            continue
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label("1", match.group("unit"), match.group("denominator")),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    typical_month_single = re.compile(
        rf"\b(?P<count>one|single|1)\s+(?:brief\s+)?(?:{SEIZURE_RATE_PHRASE})\s+"
        r"in\s+a\s+typical\s+month\b",
        re.IGNORECASE,
    )
    for match in typical_month_single.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(match.group("count"), "month"),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    implicit_a_period = re.compile(
        rf"\b(?:{SEIZURE_TERMS})\s+(?P<count>once|twice|thrice)\s+"
        rf"(?:a|an|per)\s+(?P<unit>day|week|month|year)\b",
        re.IGNORECASE,
    )
    for match in implicit_a_period.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(match.group("count"), match.group("unit")),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    frequency_a_period = re.compile(
        r"\b(?P<count>once|twice|thrice)\s+(?:a|an)\s+"
        r"(?P<unit>day|week|month|year)\b",
        re.IGNORECASE,
    )
    for match in frequency_a_period.finditer(text):
        if _is_medication_or_dose_rate_distractor(match, text):
            continue
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(match.group("count"), match.group("unit")),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    candidates.extend(apply_rate_rules((NO_MORE_THAN_ADVERBIAL_RATE_RULE,), text, ablation_config))

    candidates.extend(apply_rate_rules((OCCURRING_ONCE_PER_NIGHT_RULE,), text, ablation_config))

    candidates.extend(apply_rate_rules((PERSISTENT_ADVERBIAL_RATE_RULE,), text, ablation_config))

    qualitative_recent_multiple = re.compile(
        rf"\b(?P<evidence>(?:occurring\s+)?(?:multiple|several)\s+"
        rf"(?:times|(?:{QUALIFIED_SEIZURE_TERMS}))\s+"
        rf"(?:in\s+)?(?:the\s+)?past\s+week|"
        rf"Several\s+(?:{QUALIFIED_SEIZURE_TERMS})\s+per\s+week|"
        rf"(?:{QUALIFIED_SEIZURE_TERMS}|{SEIZURE_TYPE_DESCRIPTOR})\s+"
        rf"occur\s+several\s+times\s+"
        rf"(?:each|per)\s+week|"
        rf"(?:{QUALIFIED_SEIZURE_TERMS})\s+several\s+times\s+per\s+week|"
        rf"(?:{QUALIFIED_SEIZURE_TERMS})\s+on\s+most\s+days)\b",
        re.IGNORECASE,
    )
    for match in qualitative_recent_multiple.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label="multiple per week",
                evidence=_clean_evidence(match.group("evidence")),
            )
        )

    most_nights_rate = re.compile(
        r"\b(?P<evidence>happening\s+on\s+most\s+nights\s+of\s+the\s+week)\b",
        re.IGNORECASE,
    )
    for match in most_nights_rate.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label="multiple per week",
                evidence=_clean_evidence(match.group("evidence")),
            )
        )

    near_daily_dozens_rate = re.compile(
        rf"\b(?P<evidence>(?:{QUALIFIED_SEIZURE_TERMS}|{SEIZURE_DESCRIPTOR_PHRASE})\s+"
        rf"occur\s+on\s+a\s+"
        rf"near-daily\s+basis,\s+sometimes\s+dozens\s+in\s+a\s+day)\b",
        re.IGNORECASE,
    )
    for match in near_daily_dozens_rate.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label="multiple per day",
                evidence=_clean_evidence(match.group("evidence")),
            )
        )

    candidates.extend(apply_rate_rules((COUNTED_ADVERBIAL_RATE_RULE,), text, ablation_config))

    most_weekdays_rate = re.compile(
        rf"\b(?:(?:she|he|they|patient|carer|caregiver)\s+reports?\s+)?"
        rf"(?P<evidence>(?:{QUALIFIED_SEIZURE_TERMS})\s+occurring\s+on\s+"
        rf"most\s+weekdays)\b",
        re.IGNORECASE,
    )
    for match in most_weekdays_rate.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label="multiple per week",
                evidence=_clean_evidence(match.group("evidence")),
            )
        )

    candidates.extend(
        apply_rate_rules((SIMPLE_PARTIAL_ADVERBIAL_RATE_RULE,), text, ablation_config)
    )

    candidates.extend(apply_rate_rules((SEIZURE_ADJECTIVE_RATE_RULE,), text, ablation_config))

    candidates.extend(apply_rate_rules((STANDALONE_ADJECTIVE_RATE_RULE,), text, ablation_config))

    candidates.extend(apply_rate_rules((OCCURRING_ADJECTIVE_RATE_RULE,), text, ablation_config))

    candidates.extend(apply_rate_rules((RECENT_COUNT_RULE,), text, ablation_config))

    candidates.extend(apply_rate_rules((PERIOD_FIRST_RECENT_COUNT_RULE,), text, ablation_config))

    candidates.extend(
        apply_rate_rules((PERIOD_FIRST_EXPERIENCED_COUNT_RULE,), text, ablation_config)
    )

    candidates.extend(apply_rate_rules((PERIOD_FIRST_FEATURING_COUNT_RULE,), text, ablation_config))

    candidates.extend(apply_rate_rules((PERIOD_FIRST_TIMEFRAME_COUNT_RULE,), text, ablation_config))

    period_first_distributed_count = re.compile(
        rf"\b(?P<period>Over the past|Over the last|During the past|During the last|"
        rf"over the past|over the last|during the past|during the last)\s+"
        rf"(?P<denominator>{NUMBER_TOKEN})\s+(?P<unit>{UNIT_TOKEN}),?\s+"
        rf".{{0,80}}?\b(?P<count_a>{NUMBER_VALUE_TOKEN})\s+"
        rf"(?:{WORD_TOKEN}\s+){{0,4}}(?:{SEIZURE_TERMS}).{{0,120}}?\band\s+"
        rf"(?:approximately\s+|about\s+|around\s+)?(?P<count_b>{NUMBER_VALUE_TOKEN})\s+"
        rf"(?:{WORD_TOKEN}\s+){{0,4}}(?:{SEIZURE_TERMS})\b",
        re.IGNORECASE,
    )
    for match in period_first_distributed_count.finditer(text):
        count_a = _integer_number_token(match.group("count_a"))
        count_b = _integer_number_token(match.group("count_b"))
        if count_a is None or count_b is None:
            continue
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(
                    str(count_a + count_b),
                    match.group("unit"),
                    match.group("denominator"),
                ),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    candidates.extend(apply_rate_rules((PERIOD_FIRST_OCCURRED_COUNT_RULE,), text, ablation_config))

    adjective_count_rates = (
        (r"daily", "day"),
        (r"weekly", "week"),
        (r"monthly", "month"),
        (r"yearly", "year"),
    )
    for adjective, unit in adjective_count_rates:
        pattern = re.compile(
            rf"\b(?:occurring|occur|occurs)\s+(?:roughly\s+|approximately\s+|about\s+)?"
            rf"(?P<count>{NUMBER_TOKEN})\s+{adjective}\b",
            re.IGNORECASE,
        )
        for match in pattern.finditer(text):
            candidates.append(
                _RawCandidate(
                    kind=CandidateKind.FREQUENCY_RATE,
                    label=_rate_label(match.group("count"), unit),
                    evidence=_clean_evidence(match.group(0)),
                )
            )

    candidates.extend(apply_rate_rules((RECORDED_YEAR_COUNT_RULE,), text, ablation_config))

    candidates.extend(apply_rate_rules((YESTERDAY_OR_TODAY_COUNT_RULE,), text, ablation_config))

    candidates.extend(apply_diary_rules((SEIZURE_DAYS_PER_PERIOD_RULE,), text, ablation_config))
    candidates.extend(apply_diary_rules((SEIZURE_DAYS_FRACTION_RULE,), text, ablation_config))

    candidates.extend(
        apply_gan_shorthand_rules(
            (
                TC_SZ_COUNT_RATE_RULE,
                ABS_ADJECTIVE_RATE_RULE,
                ABS_COUNT_RATE_RULE,
                Q_INTERVAL_RULE,
            ),
            text,
            ablation_config,
        )
    )

    candidates.extend(apply_diary_rules((DIARY_DATE_LIST_RULE,), text, ablation_config))
    candidates.extend(apply_diary_rules((SEIZURE_DAY_LOG_RULE,), text, ablation_config))
    candidates.extend(apply_diary_rules((MONTHLY_COUNT_LOG_RULE,), text, ablation_config))
    candidates.extend(apply_diary_rules((SPARSE_FULL_MONTH_LOG_RULE,), text, ablation_config))

    candidates.extend(apply_diary_rules((INCREASING_MONTHLY_COUNT_RULE,), text, ablation_config))

    candidates.extend(apply_diary_rules((RECORDED_MONTH_LOG_RULE,), text, ablation_config))

    last_prior_event_interval = re.compile(
        r"\bLast event:\s*[^.;]*?\b\d+\s+weeks?\s+ago[^.;]*?;\s+prior\s+to\s+that,\s+"
        r"one\s+event\s+in\s+late\s+[A-Z][a-z]+\s+\d{4}\b",
        re.IGNORECASE,
    )
    for match in last_prior_event_interval.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label="1 per 1 to 2 month",
                evidence=_clean_evidence(match.group(0)),
            )
        )

    bad_week_ceiling = re.compile(
        rf"\bup\s+to\s+(?P<count>{NUMBER_TOKEN})\s+in\s+bad\s+weeks\b",
        re.IGNORECASE,
    )
    for match in bad_week_ceiling.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(match.group("count"), "week"),
                evidence=_clean_evidence(match.group(0)),
            )
        )
    return candidates
