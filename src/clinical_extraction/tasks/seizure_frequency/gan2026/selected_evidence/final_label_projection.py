from __future__ import annotations

import re
from dataclasses import dataclass

from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    repair_prediction_label,
    repair_prediction_label_clean_scorer_facing,
    repair_prediction_label_with_evidence,
)


@dataclass(frozen=True)
class FinalLabelProjection:
    """Named final-label projection over model-selected labels and evidence."""

    final_label: str | None
    projection_families: tuple[str, ...]
    source_label: str | None


def project_final_label_from_selected_evidence(
    *,
    raw_label: str | None,
    mechanical_label: str | None,
    selected_evidence: str,
    context_text: str | None = None,
) -> FinalLabelProjection:
    """Project a final Gan label without choosing a different clinical fact."""

    families: list[str] = []
    source_label = mechanical_label
    raw_fallback = False
    if source_label is None and raw_label:
        source_label = raw_label
        raw_fallback = True
        families.append("raw_label_fallback")
    if source_label is None:
        return FinalLabelProjection(None, tuple(families), None)

    projected = source_label
    if not raw_fallback:
        clean = repair_prediction_label_clean_scorer_facing(source_label)
        if clean != source_label:
            families.append("clean_scorer_facing_policy")
        projected = clean

    weekday = _vague_weekday_label_from_selected_evidence(selected_evidence)
    if weekday and projected != weekday:
        projected = repair_prediction_label(weekday)
        families.append("selected_evidence_vague_weekday_policy")
    elif not raw_fallback and (
        not _is_vague_frequency_label(projected)
        or _has_specific_selected_evidence_numeric_policy(selected_evidence)
    ):
        evidence_projected = repair_prediction_label_with_evidence(
            projected,
            selected_evidence,
            context_text=context_text,
        )
        if evidence_projected != projected:
            projected = evidence_projected
            families.append(_selected_evidence_projection_family(selected_evidence))

    return FinalLabelProjection(projected, tuple(families), source_label)


def _vague_weekday_label_from_selected_evidence(evidence: str) -> str | None:
    if re.search(r"\b(?:most|several|multiple)\s+weekdays\b", evidence.lower()):
        return "multiple per week"
    return None


def _selected_evidence_projection_family(evidence: str) -> str:
    normalized = evidence.lower()
    if re.search(r"\bbimonthly\b", normalized):
        return "selected_evidence_bimonthly_policy"
    if re.search(r"(?:≤|<=|\bup to\b|\bat most\b|\bno more than\b)", normalized):
        return "selected_evidence_upper_bound_policy"
    if re.search(r"\bevery\s+other\s+(?:day|week|month|year)s?\b", normalized):
        return "selected_evidence_every_other_interval"
    if re.search(
        r"\bcurrently\s+(?:reporting|reports?|describes?)\s+monthly\s+seizures?\b",
        normalized,
    ):
        return "selected_evidence_current_monthly_precedence"
    return "selected_evidence_projection"


def _is_vague_frequency_label(label: str) -> bool:
    return bool(re.fullmatch(r"multiple\s+per\s+(?:day|week|month|year|shift)", label))


def _has_specific_selected_evidence_numeric_policy(evidence: str) -> bool:
    normalized = evidence.lower()
    return bool(
        re.search(r"(?:≤|<=|\bup to\b|\bat most\b|\bno more than\b)", normalized)
        or re.search(r"\bbimonthly\b", normalized)
        or re.search(r"\bevery\s+other\s+(?:day|week|month|year)s?\b", normalized)
        or re.search(
            r"\bcurrently\s+(?:reporting|reports?|describes?)\s+monthly\s+seizures?\b",
            normalized,
        )
    )
