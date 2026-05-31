from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from clinical_extraction.core.evidence import evidence_is_substring, locate_evidence
from clinical_extraction.core.pipeline import PipelineResult
from clinical_extraction.core.schemas import FinalExtraction
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    FrequencyLabelKind,
    label_to_frequency_record,
    repair_prediction_label,
)


class CandidateKind(StrEnum):
    FREQUENCY_RATE = "frequency_rate"
    CLUSTER_FREQUENCY = "cluster_frequency"
    SEIZURE_FREE = "seizure_free"
    UNKNOWN_FREQUENCY = "unknown_frequency"
    NO_REFERENCE = "no_reference"


class CandidateEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    event_id: str
    kind: CandidateKind
    raw_value: str | None
    evidence: str
    start_char: int | None = None
    end_char: int | None = None


class NormalizedEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    event_id: str
    normalized_label: str
    semantic_kind: FrequencyLabelKind
    monthly_frequency: float
    validation_errors: tuple[str, ...] = ()


class FinalSelection(BaseModel):
    model_config = ConfigDict(frozen=True)

    final_label: str
    final_kind: FrequencyLabelKind
    selected_event_ids: tuple[str, ...]
    rationale: str
    evidence: str
    monthly_frequency: float
    validation_errors: tuple[str, ...] = ()


@dataclass(frozen=True)
class _RawCandidate:
    kind: CandidateKind
    label: str | None
    evidence: str


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
NUMBER_VALUE_TOKEN = rf"(?:multiple|\d+|{NUMBER_WORD_PATTERN})"
NUMBER_TOKEN = (
    rf"(?:{NUMBER_VALUE_TOKEN}(?:\s+(?:to|or)\s+{NUMBER_VALUE_TOKEN}|"
    rf"\s*[-–—]\s*{NUMBER_VALUE_TOKEN})?)"
)
UNIT_TOKEN = r"day|week|month|quarter|year|days|weeks|months|quarters|years"
WORD_TOKEN = r"[a-z][a-z\-‑–—]*"
SEIZURE_TERMS = (
    r"seizures?|episodes?|events?|spells?|absences?|convulsions?|spasms?|attacks?|"
    r"myoclonics?|jerks?|status epilepticus"
)
QUALIFIED_SEIZURE_TERMS = rf"(?:[a-z][a-z-]*\s+){{0,4}}(?:{SEIZURE_TERMS})"
SEIZURE_RATE_PHRASE = (
    rf"(?:(?:tonic-clonic|myoclonic|convulsive|focal|absence|drop|epileptic|"
    rf"impaired awareness|focal onset|petit mal|brief)\s+){{0,4}}(?:{SEIZURE_TERMS})"
)
SEIZURE_RATE_DESCRIPTOR = (
    r"(?:tonic-clonic|myoclonic|convulsive|focal|absence|drop|epileptic|"
    r"impaired awareness|focal onset|petit mal)"
)
SEIZURE_DESCRIPTOR_PHRASE = (
    r"(?:tonic-clonic|myoclonic|convulsive|focal(?:\s+[a-z][a-z-]*){0,3}|"
    r"absence|drop|epileptic|impaired awareness|focal onset|petit mal)"
)


class Gan2026PipelineV1:
    """First deterministic, schema-shaped seizure-frequency baseline."""

    def run(self, item: GanRecord) -> PipelineResult[FinalExtraction]:
        candidates = _extract_candidates(item.note_text)
        if not candidates:
            candidates = [
                _RawCandidate(
                    kind=CandidateKind.NO_REFERENCE,
                    label="no seizure frequency reference",
                    evidence=_fallback_evidence(item.note_text),
                )
            ]

        candidate_events = [
            _candidate_event(index=index, candidate=candidate, note_text=item.note_text)
            for index, candidate in enumerate(candidates, start=1)
        ]
        normalized_events = [
            _normalize_candidate(event, raw_candidate)
            for event, raw_candidate in zip(candidate_events, candidates, strict=True)
        ]
        final_selection = _select_final_event(candidate_events, normalized_events)
        output = FinalExtraction(
            final_value=final_selection.final_label,
            rationale=final_selection.rationale,
            evidence=final_selection.evidence,
        )

        diagnostics = {
            "candidate_events": [event.model_dump(mode="json") for event in candidate_events],
            "normalized_events": [event.model_dump(mode="json") for event in normalized_events],
            "final_selection": final_selection.model_dump(mode="json"),
            "evidence_valid": evidence_is_substring(item.note_text, final_selection.evidence),
        }
        return PipelineResult(output=output, diagnostics=diagnostics)


def _extract_candidates(note_text: str) -> list[_RawCandidate]:
    normalized = _normalize_note_text(note_text)
    candidates: list[_RawCandidate] = []
    candidates.extend(_extract_cluster_candidates(normalized))
    candidates.extend(_extract_seizure_free_candidates(normalized))
    candidates.extend(_extract_rate_candidates(normalized))
    candidates.extend(_extract_unknown_candidates(normalized))
    return _dedupe_candidates(candidates)


def _extract_cluster_candidates(text: str) -> list[_RawCandidate]:
    candidates: list[_RawCandidate] = []
    cluster_rate = re.compile(
        rf"\bcluster(?: days?|s)?\s+(?P<count>{NUMBER_TOKEN})\s+(?:this|per)\s+"
        rf"(?P<period>{UNIT_TOKEN}).{{0,80}}?(?:typically|usually|each|with)?\s*"
        rf"(?P<per_cluster>{NUMBER_TOKEN})\s+(?:{SEIZURE_TERMS})?\s*(?:in\s+24\s+h|per cluster)?",
        re.IGNORECASE,
    )
    for match in cluster_rate.finditer(text):
        count = _number_token(match.group("count"))
        period = _singular_unit(match.group("period"))
        per_cluster = _number_token(match.group("per_cluster"))
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.CLUSTER_FREQUENCY,
                label=f"{count} cluster per {period}, {per_cluster} per cluster",
                evidence=_clean_evidence(match.group(0)),
            )
        )

    monthly_cluster_rate = re.compile(
        rf"\bMonthly\s+clusters?,?\s+(?:typically|usually|each|with)?\s*"
        rf"(?P<per_cluster>{NUMBER_TOKEN})\s+(?:{SEIZURE_TERMS})\s+over\s+24\s+h\b",
        re.IGNORECASE,
    )
    for match in monthly_cluster_rate.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.CLUSTER_FREQUENCY,
                label=(
                    "1 cluster per month, "
                    f"{_number_token(match.group('per_cluster'))} per cluster"
                ),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    unknown_cluster = re.compile(
        rf"\bclusters? characterized by (?P<per_cluster>{NUMBER_TOKEN})\s+.*?"
        rf"(?:frequency unclear|cannot specify how often|unclear frequency)",
        re.IGNORECASE,
    )
    for match in unknown_cluster.finditer(text):
        per_cluster = _number_token(match.group("per_cluster"))
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.UNKNOWN_FREQUENCY,
                label=f"unknown, {per_cluster} per cluster",
                evidence=_clean_evidence(match.group(0)),
            )
        )

    cluster_days = re.compile(
        rf"\b(?P<count>{NUMBER_TOKEN})\s+clusters?\s+this\s+(?P<period>month|week);?\s+"
        rf"each\s+(?:approx|≈|about|around)?\s*(?P<per_cluster>{NUMBER_TOKEN})\s+"
        rf"(?:{SEIZURE_TERMS})\b",
        re.IGNORECASE,
    )
    for match in cluster_days.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.CLUSTER_FREQUENCY,
                label=(
                    f"{_number_token(match.group('count'))} cluster per "
                    f"{_singular_unit(match.group('period'))}, "
                    f"{_number_token(match.group('per_cluster'))} per cluster"
                ),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    cluster_over_period = re.compile(
        rf"\b(?P<count>{NUMBER_TOKEN})\s+(?:{WORD_TOKEN}\s+){{0,3}}clusters?\s+"
        rf"over\s+(?:the\s+)?(?:past|last)\s+"
        rf"(?:(?P<denominator>{NUMBER_TOKEN})\s+)?(?P<unit>{UNIT_TOKEN})\b",
        re.IGNORECASE,
    )
    for match in cluster_over_period.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.CLUSTER_FREQUENCY,
                label=(
                    f"{_number_token(match.group('count'))} cluster per "
                    f"{_period_label(match.group('unit'), match.group('denominator'))}, "
                    "multiple per cluster"
                ),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    run_of_events = re.compile(
        rf"\bover\s+the\s+past\s+(?P<period>fortnight|month|week),?\s+"
        rf".{{0,80}}?\b(?:cluster|run)\b.{{0,80}}?\bwith\s+"
        rf"(?P<per_cluster>{NUMBER_TOKEN})\s+(?:short\s+)?(?:{SEIZURE_TERMS})\s+"
        r"occurring on separate days\b",
        re.IGNORECASE,
    )
    for match in run_of_events.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.CLUSTER_FREQUENCY,
                label=(
                    f"1 cluster per {_period_unit_label(match.group('period'))}, "
                    f"{_number_token(match.group('per_cluster'))} per cluster"
                ),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    vague_cluster_days = re.compile(
        r"\bover\s+the\s+past\s+(?P<period>month|week|fortnight),?\s+"
        r".{0,80}?\bcluster\b.{0,80}?\bon\s+(?P<days>multiple|several)\s+days\b",
        re.IGNORECASE,
    )
    for match in vague_cluster_days.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.CLUSTER_FREQUENCY,
                label=(
                    f"{_number_token(match.group('days'))} cluster per "
                    f"{_period_unit_label(match.group('period'))}, multiple per cluster"
                ),
                evidence=_clean_evidence(match.group(0)),
            )
        )
    return candidates


def _extract_seizure_free_candidates(text: str) -> list[_RawCandidate]:
    candidates: list[_RawCandidate] = []
    seizure_free = re.compile(
        rf"\b(?:seizure[- ]free|free of (?:{SEIZURE_TERMS})|"
        rf"no (?:further )?(?:{SEIZURE_TERMS})).{{0,80}}?"
        rf"(?:(?P<count>{NUMBER_TOKEN})\s+(?P<unit>months|month|years|year)|"
        r"several years|long duration|since\b)",
        re.IGNORECASE,
    )
    for match in seizure_free.finditer(text):
        count = match.groupdict().get("count")
        unit = match.groupdict().get("unit")
        if count and unit:
            label = f"seizure free for {_number_token(count)} {_singular_unit(unit)}"
        else:
            label = "seizure free for multiple year"
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.SEIZURE_FREE,
                label=label,
                evidence=_clean_evidence(match.group(0)),
            )
        )
    return candidates


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


def _extract_rate_candidates(text: str) -> list[_RawCandidate]:
    candidates: list[_RawCandidate] = []
    candidates.extend(_extract_distributed_count_candidates(text))

    direct_rate = re.compile(
        rf"\b(?P<count>{NUMBER_TOKEN})\s+"
        rf"(?:times?|{SEIZURE_TERMS})?\s*(?:per|each|every)\s+"
        rf"(?:(?P<denominator>{NUMBER_TOKEN})\s+)?(?P<unit>{UNIT_TOKEN})\b",
        re.IGNORECASE,
    )
    for match in direct_rate.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(
                    match.group("count"),
                    match.group("unit"),
                    match.groupdict().get("denominator"),
                ),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    qualified_direct_rate = re.compile(
        rf"\b(?P<count>{NUMBER_TOKEN})\s+"
        rf"(?:(?!day|days|week|weeks|month|months|quarter|quarters|year|years)"
        rf"{WORD_TOKEN}\s+){{0,4}}(?:{SEIZURE_TERMS})\s+"
        rf"(?:per|each|every)\s+"
        rf"(?:(?P<denominator>{NUMBER_TOKEN})\s+)?(?P<unit>{UNIT_TOKEN})\b",
        re.IGNORECASE,
    )
    for match in qualified_direct_rate.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(
                    match.group("count"),
                    match.group("unit"),
                    match.groupdict().get("denominator"),
                ),
                evidence=_clean_evidence(match.group(0)),
            )
        )

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

    implicit_interval = re.compile(
        rf"\b(?:{SEIZURE_TERMS})\s+every\s+"
        rf"(?:(?P<denominator>{NUMBER_TOKEN})\s+)?(?P<unit>{UNIT_TOKEN})\b",
        re.IGNORECASE,
    )
    for match in implicit_interval.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label("1", match.group("unit"), match.group("denominator")),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    implicit_nightly_interval = re.compile(
        rf"\b(?:{SEIZURE_RATE_PHRASE}|{SEIZURE_DESCRIPTOR_PHRASE})\s+every\s+night\b",
        re.IGNORECASE,
    )
    for match in implicit_nightly_interval.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label("1", "day"),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    implicit_other_interval = re.compile(
        rf"\b(?:{SEIZURE_TERMS})\s+every\s+other\s+(?P<unit>day|week|month|year)\b",
        re.IGNORECASE,
    )
    for match in implicit_other_interval.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label("1", match.group("unit"), "2"),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    occurring_interval = re.compile(
        rf"\b(?P<verb>occurring|occur|occurs|cluster|clusters)\s+"
        rf"(?:only\s+|roughly\s+|approximately\s+)?every\s+"
        rf"(?:(?P<denominator>{NUMBER_TOKEN})\s+)?(?P<unit>{UNIT_TOKEN})\b",
        re.IGNORECASE,
    )
    for match in occurring_interval.finditer(text):
        if _has_historical_lead_in(text, match.start()):
            continue
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label("1", match.group("unit"), match.group("denominator")),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    occurring_other_interval = re.compile(
        r"\b(?P<verb>occurring|occur|occurs)\s+"
        r"(?:only\s+|roughly\s+|approximately\s+)?every\s+other\s+"
        r"(?P<unit>day|week|month|year)\b",
        re.IGNORECASE,
    )
    for match in occurring_other_interval.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label("1", match.group("unit"), "2"),
                evidence=_clean_evidence(match.group(0)),
            )
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
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(match.group("count"), match.group("unit")),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    direct_per_period = re.compile(
        rf"\b(?P<count>{NUMBER_TOKEN})\s+per\s+(?P<unit>quarter)\b",
        re.IGNORECASE,
    )
    for match in direct_per_period.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(match.group("count"), match.group("unit")),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    adjective_rates = (
        (r"daily", "1 per day"),
        (r"weekly", "1 per week"),
        (r"monthly", "1 per month"),
        (r"yearly", "1 per year"),
        (r"bimonthly", "1 per 2 month"),
    )
    for adjective, label in adjective_rates:
        pattern = re.compile(
            rf"\b(?:{adjective}\s+(?:{SEIZURE_RATE_PHRASE})|"
            rf"(?:(?:{SEIZURE_RATE_PHRASE})|{SEIZURE_DESCRIPTOR_PHRASE})\s+{adjective})\b",
            re.IGNORECASE,
        )
        for match in pattern.finditer(text):
            candidates.append(
                _RawCandidate(
                    kind=CandidateKind.FREQUENCY_RATE,
                    label=label,
                    evidence=_clean_evidence(match.group(0)),
                )
            )

    standalone_adjective_rates = (
        (r"daily", "1 per day"),
        (r"weekly", "1 per week"),
        (r"monthly", "1 per month"),
        (r"yearly", "1 per year"),
        (r"bimonthly", "1 per 2 month"),
    )
    for adjective, label in standalone_adjective_rates:
        pattern = re.compile(
            rf"\b(?:frequency|pattern|rate)\s+(?:is\s+|was\s+|reported as\s+)?{adjective}\b",
            re.IGNORECASE,
        )
        for _match in pattern.finditer(text):
            candidates.append(
                _RawCandidate(
                    kind=CandidateKind.FREQUENCY_RATE,
                    label=label,
                    evidence=adjective,
                )
            )

    occurring_adjective_rates = (
        (r"daily", "1 per day"),
        (r"weekly", "1 per week"),
        (r"monthly", "1 per month"),
        (r"yearly", "1 per year"),
        (r"bimonthly", "1 per 2 month"),
    )
    for adjective, label in occurring_adjective_rates:
        pattern = re.compile(
            rf"\b(?:occurring|occur|occurs)\s+(?:roughly\s+|approximately\s+)?{adjective}\b",
            re.IGNORECASE,
        )
        for match in pattern.finditer(text):
            candidates.append(
                _RawCandidate(
                    kind=CandidateKind.FREQUENCY_RATE,
                    label=label,
                    evidence=_clean_evidence(match.group(0)),
                )
            )

    recent_count = re.compile(
        rf"\b(?P<count>{NUMBER_TOKEN})\s+(?:{QUALIFIED_SEIZURE_TERMS})\s+"
        rf"(?:last|this|past)\s+(?P<unit>day|week|month|quarter|year)\b",
        re.IGNORECASE,
    )
    for match in recent_count.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(match.group("count"), match.group("unit")),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    period_first_recent_count = re.compile(
        rf"\b(?P<period>This|Over the past|Over the last|During the past|During the last)\s+"
        rf"(?P<unit>day|week|month|year),?\s+"
        rf".{{0,60}}?\b(?P<count>{NUMBER_TOKEN})\s+(?:{QUALIFIED_SEIZURE_TERMS})\b",
        re.IGNORECASE,
    )
    for match in period_first_recent_count.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(match.group("count"), match.group("unit")),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    period_first_timeframe_count = re.compile(
        rf"\b(?P<period>Over the past|Over the last|During the past|During the last)\s+"
        rf"(?P<denominator>{NUMBER_TOKEN})\s+(?P<unit>{UNIT_TOKEN}),?\s+"
        rf".{{0,260}}?\b(?P<count>{NUMBER_TOKEN})\s+(?:{QUALIFIED_SEIZURE_TERMS})\s+"
        r"in\s+that\s+timeframe\b",
        re.IGNORECASE,
    )
    for match in period_first_timeframe_count.finditer(text):
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

    period_first_occurred_count = re.compile(
        rf"\b(?P<period>Over the past|Over the last|During the past|During the last)\s+"
        rf"(?P<denominator>{NUMBER_TOKEN})\s+(?P<unit>{UNIT_TOKEN}),?\s+"
        rf"(?P<count>{NUMBER_TOKEN})\s+(?:{QUALIFIED_SEIZURE_TERMS})\s+"
        r"have\s+occurred\b",
        re.IGNORECASE,
    )
    for match in period_first_occurred_count.finditer(text):
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

    yesterday_count = re.compile(
        rf"\b(?P<count>{NUMBER_TOKEN})\s+(?:{QUALIFIED_SEIZURE_TERMS})\s+"
        r"(?:yesterday|today)\b",
        re.IGNORECASE,
    )
    for match in yesterday_count.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(match.group("count"), "day"),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    seizure_days_per_period = re.compile(
        rf"\b(?:About\s+)?(?P<count>{NUMBER_TOKEN})\s+seizure\s+days?\s+"
        rf"per\s+(?P<unit>day|week|month|year)\b",
        re.IGNORECASE,
    )
    for match in seizure_days_per_period.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(match.group("count"), match.group("unit")),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    seizure_days_fraction = re.compile(
        rf"\bSeizure\s+days:\s*(?P<count>{NUMBER_VALUE_TOKEN})\s*/\s*30\s+this\s+month\b",
        re.IGNORECASE,
    )
    for match in seizure_days_fraction.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(match.group("count"), "month"),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    compact_tc_rate = re.compile(
        rf"\b(?:TC|sz)\s+(?:[*x×]\s*)?(?P<count>{NUMBER_VALUE_TOKEN})\s*/\s*"
        r"(?P<unit>d|day|wk|week|mo|month|yr|year)\b",
        re.IGNORECASE,
    )
    for match in compact_tc_rate.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(
                    match.group("count"),
                    _expanded_compact_unit(match.group("unit")),
                ),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    compact_abs_adjective_rate = re.compile(
        r"\babs\s+(?:[*x×]\s*)?(?P<period>daily|weekly|monthly|yearly|bimonthly)\b",
        re.IGNORECASE,
    )
    period_labels = {
        "daily": "1 per day",
        "weekly": "1 per week",
        "monthly": "1 per month",
        "yearly": "1 per year",
        "bimonthly": "1 per 2 month",
    }
    for match in compact_abs_adjective_rate.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=period_labels[match.group("period").lower()],
                evidence=_clean_evidence(match.group(0)),
            )
        )

    compact_abs_count_rate = re.compile(
        rf"\babs\s+(?P<count>{NUMBER_TOKEN})\s+"
        r"(?P<period>daily|weekly|monthly|yearly|bimonthly)\b",
        re.IGNORECASE,
    )
    period_units = {
        "daily": ("day", None),
        "weekly": ("week", None),
        "monthly": ("month", None),
        "yearly": ("year", None),
        "bimonthly": ("month", "2"),
    }
    for match in compact_abs_count_rate.finditer(text):
        unit, denominator = period_units[match.group("period").lower()]
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(match.group("count"), unit, denominator),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    compact_q_interval = re.compile(
        rf"\bq(?P<denominator>{NUMBER_TOKEN})\s*(?P<unit>d|day|wk|week|mo|month|yr|year)\b",
        re.IGNORECASE,
    )
    for match in compact_q_interval.finditer(text):
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(
                    "1",
                    _expanded_compact_unit(match.group("unit")),
                    match.group("denominator"),
                ),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    diary_date_list = re.compile(
        r"\bSeizure events on (?P<dates>\d{2}-\d{2}(?:,\s*\d{2}-\d{2})+)\b",
        re.IGNORECASE,
    )
    for match in diary_date_list.finditer(text):
        dates = re.findall(r"(\d{2})-\d{2}", match.group("dates"))
        months = [int(month) for month in dates]
        denominator = max(max(months) - min(months), 1)
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(str(len(dates)), "month", str(denominator)),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    monthly_count_log = re.compile(
        r"\bSeizure:\s*\d{4}:\s*"
        r"(?P<entries>(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+"
        r"x\d+,?\s*){2,})",
        re.IGNORECASE,
    )
    for match in monthly_count_log.finditer(text):
        entries = re.findall(
            r"\b(?P<month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+x(?P<count>\d+)",
            match.group("entries"),
            flags=re.IGNORECASE,
        )
        if not entries:
            continue
        total = sum(int(count) for _month, count in entries)
        denominator = len({MONTH_ABBREVIATIONS[month.lower()] for month, _count in entries})
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(str(total), "month", str(denominator)),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    sparse_full_month_log = re.compile(
        r"\b\d{4}:\s*(?P<entries>(?:(?:January|February|March|April|May|June|July|"
        r"August|September|October|November|December)\s+\d+[^.;]*;\s*){2,}"
        r"(?:January|February|March|April|May|June|July|August|September|October|"
        r"November|December)\s+\d+[^.;]*)",
        re.IGNORECASE,
    )
    for match in sparse_full_month_log.finditer(text):
        entries = re.findall(
            r"\b(?P<month>January|February|March|April|May|June|July|August|September|"
            r"October|November|December)\s+(?P<count>\d+)",
            match.group("entries"),
            flags=re.IGNORECASE,
        )
        if not entries:
            continue
        total = sum(int(count) for _month, count in entries)
        months = {FULL_MONTHS[month.lower()] for month, _count in entries}
        candidates.append(
            _RawCandidate(
                kind=CandidateKind.FREQUENCY_RATE,
                label=_rate_label(str(total), "month", str(len(months))),
                evidence=_clean_evidence(match.group(0)),
            )
        )

    increasing_monthly_counts = re.compile(
        r"\b(?:Frequency has increased|Frequency increased|Current diary):\s*"
        r"(?P<entries>(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|"
        r"January|February|March|April|May|June|July|August|September|October|"
        r"November|December)\s+x\s*\d+[^.;]*;\s*)+"
        r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|"
        r"March|April|May|June|July|August|September|October|November|December)"
        r"\s+x\s*\d+[^.;]*)",
        re.IGNORECASE,
    )
    for match in increasing_monthly_counts.finditer(text):
        entries = list(
            re.finditer(
                r"\b(?P<month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|"
                r"January|February|March|April|May|June|July|August|September|"
                r"October|November|December)\s+x\s*(?P<count>\d+)[^.;]*",
                match.group("entries"),
                flags=re.IGNORECASE,
            )
        )
        for entry in entries:
            evidence = re.sub(r"\s+with\s+two\b.*$", "", entry.group(0), flags=re.IGNORECASE)
            candidates.append(
                _RawCandidate(
                    kind=CandidateKind.FREQUENCY_RATE,
                    label=_rate_label(entry.group("count"), "month"),
                    evidence=_clean_evidence(evidence),
                )
            )

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


def _extract_unknown_candidates(text: str) -> list[_RawCandidate]:
    unknown = re.compile(
        r"\b(?:frequency unclear|unclear frequency|cannot specify how often|last seizure\b.*?)",
        re.IGNORECASE,
    )
    return [
        _RawCandidate(
            kind=CandidateKind.UNKNOWN_FREQUENCY,
            label="unknown",
            evidence=_clean_evidence(match.group(0)),
        )
        for match in unknown.finditer(text)
    ]


def _candidate_event(index: int, candidate: _RawCandidate, note_text: str) -> CandidateEvent:
    evidence = _exact_evidence(note_text, candidate.evidence)
    span = locate_evidence(note_text, evidence)
    start_char, end_char = span if span else (None, None)
    return CandidateEvent(
        event_id=f"event_{index}",
        kind=candidate.kind,
        raw_value=candidate.label,
        evidence=evidence,
        start_char=start_char,
        end_char=end_char,
    )


def _normalize_candidate(event: CandidateEvent, candidate: _RawCandidate) -> NormalizedEvent:
    label = repair_prediction_label(candidate.label)
    errors: tuple[str, ...] = ()
    try:
        record = label_to_frequency_record(label)
    except ValueError as exc:
        record = label_to_frequency_record("unknown")
        label = "unknown"
        errors = (str(exc),)
    return NormalizedEvent(
        event_id=event.event_id,
        normalized_label=label,
        semantic_kind=record.kind,
        monthly_frequency=record.monthly_frequency,
        validation_errors=errors,
    )


def _select_final_event(
    candidate_events: list[CandidateEvent],
    normalized_events: list[NormalizedEvent],
) -> FinalSelection:
    pairs = list(zip(candidate_events, normalized_events, strict=True))
    selected_event, selected_normalized = max(pairs, key=_selection_score)
    return FinalSelection(
        final_label=selected_normalized.normalized_label,
        final_kind=selected_normalized.semantic_kind,
        selected_event_ids=(selected_event.event_id,),
        rationale=_selection_rationale(selected_normalized),
        evidence=selected_event.evidence,
        monthly_frequency=selected_normalized.monthly_frequency,
        validation_errors=selected_normalized.validation_errors,
    )


def _selection_score(pair: tuple[CandidateEvent, NormalizedEvent]) -> tuple[int, float]:
    _, normalized = pair
    if normalized.semantic_kind is FrequencyLabelKind.FREQUENCY:
        return 4, normalized.monthly_frequency
    if normalized.semantic_kind is FrequencyLabelKind.UNRESOLVED_MULTIPLE:
        return 3, 0.0
    if normalized.semantic_kind is FrequencyLabelKind.SEIZURE_FREE:
        return 2, 0.0
    if normalized.semantic_kind is FrequencyLabelKind.UNKNOWN:
        return 1, 0.0
    return 0, 0.0


def _selection_rationale(normalized: NormalizedEvent) -> str:
    if normalized.semantic_kind is FrequencyLabelKind.FREQUENCY:
        return "Selected the highest normalized current frequency candidate."
    if normalized.semantic_kind is FrequencyLabelKind.UNRESOLVED_MULTIPLE:
        return "Selected an unresolved multiple-frequency candidate."
    if normalized.semantic_kind is FrequencyLabelKind.SEIZURE_FREE:
        return "Selected the explicit seizure-free statement."
    if normalized.semantic_kind is FrequencyLabelKind.UNKNOWN:
        return "Selected seizure-frequency evidence that could not be converted to a rate."
    return "No seizure-frequency evidence was found."


def _rate_label(count: str, unit: str, denominator: str | None = None) -> str:
    count_value = _number_token(count)
    unit_value = _singular_unit(unit)
    denominator_value = _number_token(denominator) if denominator else None
    if unit_value == "quarter":
        unit_value = "month"
        denominator_value = _quarter_month_denominator(denominator_value)
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


def _quarter_month_denominator(denominator: str | None) -> str:
    if denominator in {None, "1"}:
        return "3"
    if denominator and denominator.isdigit():
        return str(int(denominator) * 3)
    return f"3 {denominator}"


def _singular_unit(value: str) -> str:
    normalized = value.lower().strip()
    return normalized[:-1] if normalized.endswith("s") else normalized


def _period_unit_label(value: str) -> str:
    normalized = value.lower().strip()
    if normalized == "fortnight":
        return "2 week"
    return _singular_unit(normalized)


def _period_label(unit: str, denominator: str | None = None) -> str:
    denominator_value = _number_token(denominator) if denominator else None
    unit_value = _singular_unit(unit)
    if denominator_value in {None, "1"}:
        return unit_value
    return f"{denominator_value} {unit_value}"


def _expanded_compact_unit(value: str) -> str:
    return {
        "d": "day",
        "day": "day",
        "wk": "week",
        "week": "week",
        "mo": "month",
        "month": "month",
        "yr": "year",
        "year": "year",
    }[value.lower()]


def _has_historical_lead_in(text: str, start: int) -> bool:
    preceding = text[max(0, start - 140) : start].lower()
    return any(
        marker in preceding
        for marker in (
            "prior to this",
            "historical description",
            "before improvement",
            "previously",
        )
    )


def _normalize_note_text(note_text: str) -> str:
    return re.sub(r"\s+", " ", note_text)


def _clean_evidence(evidence: str) -> str:
    return evidence.strip(" .;:\n\t")


def _fallback_evidence(note_text: str) -> str:
    first_sentence = re.split(r"(?<=[.!?])\s+", note_text.strip(), maxsplit=1)[0]
    return first_sentence[:240] if first_sentence else ""


def _exact_evidence(note_text: str, evidence: str) -> str:
    if evidence in note_text:
        return evidence
    pattern = r"\s+".join(re.escape(part) for part in evidence.split())
    match = re.search(pattern, note_text)
    if match:
        return note_text[match.start() : match.end()].strip(" .;:\n\t")
    return evidence


def _dedupe_candidates(candidates: list[_RawCandidate]) -> list[_RawCandidate]:
    seen: set[tuple[CandidateKind, str | None, str]] = set()
    deduped: list[_RawCandidate] = []
    for candidate in candidates:
        key = (candidate.kind, candidate.label, candidate.evidence)
        if key not in seen:
            seen.add(key)
            deduped.append(candidate)
    return deduped
