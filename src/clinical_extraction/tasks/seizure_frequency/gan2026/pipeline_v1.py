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
UNIT_TOKEN = r"day|week|month|year|days|weeks|months|years"
SEIZURE_TERMS = r"seizures?|episodes?|events?|spells?|absences?|convulsions?"


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
        rf"(?:in|during)\s+(?:the\s+)?(?:last|past|this)\s+"
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

    over_period = re.compile(
        rf"\b(?P<count>{NUMBER_TOKEN})\s+(?:{SEIZURE_TERMS})\s+"
        rf"(?:over|in|during|across)\s+(?:the\s+)?(?:last|past)?\s*"
        rf"(?P<denominator>{NUMBER_TOKEN})\s+(?P<unit>{UNIT_TOKEN})\b",
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
        rf"(?:roughly\s+|approximately\s+)?every\s+"
        rf"(?:(?P<denominator>{NUMBER_TOKEN})\s+)?(?P<unit>{UNIT_TOKEN})\b",
        re.IGNORECASE,
    )
    for match in occurring_interval.finditer(text):
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

    adjective_rates = (
        (r"daily", "1 per day"),
        (r"weekly", "1 per week"),
        (r"monthly", "1 per month"),
        (r"yearly", "1 per year"),
        (r"bimonthly", "1 per 2 month"),
    )
    for adjective, label in adjective_rates:
        pattern = re.compile(
            rf"\b(?:{adjective}\s+(?:{SEIZURE_TERMS})|(?:{SEIZURE_TERMS})\s+{adjective})\b",
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

    occurring_adjective_rates = (
        (r"daily", "1 per day"),
        (r"weekly", "1 per week"),
        (r"monthly", "1 per month"),
        (r"yearly", "1 per year"),
        (r"bimonthly", "1 per 2 month"),
    )
    for adjective, label in occurring_adjective_rates:
        pattern = re.compile(
            rf"\boccurring\s+(?:roughly\s+|approximately\s+)?{adjective}\b",
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
        rf"\b(?P<count>{NUMBER_TOKEN})\s+(?:{SEIZURE_TERMS})\s+"
        rf"(?:last|this|past)\s+(?P<unit>day|week|month|year)\b",
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
