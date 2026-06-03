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
        projected = repair_prediction_label_with_evidence(
            source_label,
            selected_evidence,
            context_text=context_text,
        )
        if projected != source_label:
            families.append("selected_evidence_projection")

        clean = repair_prediction_label_clean_scorer_facing(projected)
        if clean != projected:
            families.append("clean_scorer_facing_policy")
        projected = clean

    weekday = _vague_weekday_label_from_selected_evidence(selected_evidence)
    if weekday and projected != weekday:
        projected = repair_prediction_label(weekday)
        families.append("selected_evidence_vague_weekday_policy")

    return FinalLabelProjection(projected, tuple(families), source_label)


def _vague_weekday_label_from_selected_evidence(evidence: str) -> str | None:
    if re.search(r"\b(?:most|several|multiple)\s+weekdays\b", evidence.lower()):
        return "multiple per week"
    return None
