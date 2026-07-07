"""Shared helpers for clinical-assessment assembly."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Literal

from pydantic import ValidationError

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.assessment_draft import (
    AssessmentDraft,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
    ExtractedCandidate,
    candidate_source_phrase,
)

NORMALIZATION_POLICY_ID = "gan2026_clinical_assessment_normalization_v0"

DISABLED_SWITCH_ISSUE_PREFIX = "ablation_switch_disabled:"


def _candidate_lookup(
    candidate_by_id: Mapping[str, ExtractedCandidate],
    candidate_ids: Sequence[str],
) -> list[ExtractedCandidate]:
    return [
        candidate_by_id[candidate_id]
        for candidate_id in candidate_ids
        if candidate_id in candidate_by_id
    ]


def _dedupe(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        deduped.append(value)
    return deduped


def _candidates_by_ids(
    candidate_set: CandidateSet,
    candidate_ids: Sequence[str],
) -> list[ExtractedCandidate]:
    by_id = {candidate.candidate_id: candidate for candidate in candidate_set.candidates}
    return [by_id[candidate_id] for candidate_id in candidate_ids if candidate_id in by_id]


def _normalization_source_phrase(
    draft: AssessmentDraft,
    primary_candidates: Sequence[ExtractedCandidate],
) -> str:
    if draft.normalized_burden.source_normalized_phrase.strip():
        return _clean_phrase(draft.normalized_burden.source_normalized_phrase)
    phrases = [
        candidate_source_phrase(candidate) or candidate.evidence_span.text
        for candidate in primary_candidates
    ]
    return _clean_phrase("; ".join(phrase for phrase in phrases if phrase))


def _disabled_switch_issue(switch: str) -> str:
    return f"{DISABLED_SWITCH_ISSUE_PREFIX}{switch}"


def _small_number_to_float(value: str) -> float | None:
    if value.isdigit():
        return float(value)
    parsed = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
        "eleven": 11,
        "twelve": 12,
    }.get(value.strip().lower())
    return float(parsed) if parsed is not None else None


def _multi_month_bucket_count_to_float(value: str) -> float | None:
    normalized = value.strip().lower()
    if normalized in {"no", "zero"}:
        return 0.0
    return _small_number_to_float(value)


def _duration_unit(value: str) -> Literal["day", "week", "month", "year"] | None:
    normalized = value.strip().lower()
    if normalized.startswith("day"):
        return "day"
    if normalized.startswith("week"):
        return "week"
    if normalized.startswith("month"):
        return "month"
    if normalized.startswith("year"):
        return "year"
    return None


def _candidate_parse_phrases(candidate: ExtractedCandidate) -> list[str]:
    phrases = [
        candidate_source_phrase(candidate) or "",
        candidate.evidence_span.text,
    ]
    return [phrase for phrase in _dedupe([_clean_phrase(phrase) for phrase in phrases]) if phrase]


def _source_ids_from_candidates(candidates: Sequence[ExtractedCandidate]) -> list[str]:
    return sorted({source_id for candidate in candidates for source_id in candidate.source_ids})


def _cluster_phrases(candidates: Sequence[ExtractedCandidate]) -> list[str]:
    phrases: list[str] = []
    for candidate in candidates:
        if candidate.cluster_details is None:
            phrase = candidate_source_phrase(candidate) or candidate.evidence_span.text
            if phrase:
                phrases.append(phrase)
            continue
        details = candidate.cluster_details
        phrases.extend(
            phrase
            for phrase in (
                details.cluster_frequency,
                details.events_per_cluster,
                details.cluster_count,
                details.cluster_period,
                candidate.evidence_span.text,
            )
            if phrase
        )
    return phrases


def _clean_phrase(value: str) -> str:
    return " ".join(value.strip().split())


def _normalize_phrase_for_parse(value: str) -> str:
    text = value.lower()
    text = re.sub(r"[≈~]", "", text)
    if not re.search(r"\b\d{2}-\d{2}(?:,\s*\d{2}-\d{2})+\b", text):
        text = re.sub(r"(?<=\d)\s*[-–—]\s*(?=\d)", " to ", text)
    text = re.sub(r"\bper\s+24\s*h(?:ours?)?\b", "per day", text)
    text = re.sub(r"\b24\s*h(?:ours?)?\b", "day", text)

    # Normalize fortnight patterns to 2 weeks
    text = re.sub(r"\bfortnightly\b", "every 2 weeks", text)
    text = re.sub(r"\ba\s+fortnight\b", "2 weeks", text)
    text = re.sub(r"\bfortnight\b", "2 weeks", text)

    # Normalize range patterns like "once every X to Y weeks" -> "1 per X to Y weeks"
    text = re.sub(
        r"\bonce\s+every\s+(\d+)\s+to\s+(\d+)\s+(day|week|month|year)s?\b",
        r"1 per \1 to \2 \3s",
        text,
    )
    text = re.sub(
        r"\b(?:roughly|approximately)?\s*once\s+in\s+(\d+)\s+(day|week|month|year)s?\b",
        r"1 per \1 \2s",
        text,
    )
    text = re.sub(
        r"\b(?:roughly|approximately)?\s*once\s+in\s+a\s+"
        r"(day|week|month|year)\b",
        r"1 per 1 \1",
        text,
    )

    return " ".join(text.split())


def _validate_candidate_references(
    draft: AssessmentDraft,
    candidate_set: CandidateSet,
) -> list[str]:
    known = {candidate.candidate_id for candidate in candidate_set.candidates}
    errors: list[str] = []
    for role_name, candidate_ids in (
        ("primary_candidate_ids", draft.primary_candidate_ids),
        ("supporting_candidate_ids", draft.supporting_candidate_ids),
        ("rejected_candidate_ids", draft.rejected_candidate_ids),
    ):
        for candidate_id in candidate_ids:
            if candidate_id not in known:
                errors.append(f"{role_name}:unknown_candidate_id:{candidate_id}")
    return errors


def _validation_error_messages(exc: ValidationError) -> list[str]:
    return [str(error.get("msg", error)) for error in exc.errors()]
