"""Selected-evidence gating phrase heuristics for projection/render."""

from __future__ import annotations

from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
    candidate_source_phrase,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.clinical_assessment import (
    ClinicalAssessment,
    NormalizedBurden,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.selected_evidence import (
    selected_evidence_derivation,
)


def source_ids_for_assessment(
    assessment: ClinicalAssessment,
    candidate_set: CandidateSet,
) -> list[str]:
    by_id = {candidate.candidate_id: candidate for candidate in candidate_set.candidates}
    source_ids: list[str] = []
    for candidate_id in assessment.primary_candidate_ids:
        candidate = by_id.get(candidate_id)
        if candidate is None:
            continue
        source_ids.extend(candidate.source_ids)
    return sorted(set(source_ids))


def selected_evidence_status_for_assessment(
    assessment: ClinicalAssessment,
    candidate_set: CandidateSet,
) -> dict[str, Any]:
    by_id = {candidate.candidate_id: candidate for candidate in candidate_set.candidates}
    primary_candidates = [
        candidate
        for candidate_id in assessment.primary_candidate_ids
        for candidate in [by_id.get(candidate_id)]
        if candidate is not None
    ]
    expected_source_ids = sorted(
        set(
            source_id
            for candidate in primary_candidates
            if candidate_has_exact_trace_evidence(candidate)
            for source_id in candidate.source_ids
        )
    )
    selected_source_ids = source_ids_for_assessment(assessment, candidate_set)
    if not primary_candidates:
        exact_trace: bool | None = None
        trace_basis = "no_primary_candidate"
    else:
        exact_trace = all(
            candidate_has_exact_trace_evidence(candidate) for candidate in primary_candidates
        )
        trace_basis = (
            "primary_candidate_exact_evidence"
            if exact_trace
            else "primary_candidate_evidence_missing"
        )
    missing_expected_source_ids = [
        source_id for source_id in expected_source_ids if source_id not in selected_source_ids
    ]
    unexpected_source_ids = [
        source_id for source_id in selected_source_ids if source_id not in expected_source_ids
    ]
    if exact_trace is False:
        source_id_status = "invalid"
    elif exact_trace is None:
        source_id_status = "not_applicable"
    elif not selected_source_ids:
        source_id_status = "not_instrumented"
    elif any("unresolved" in source_id for source_id in selected_source_ids):
        source_id_status = "invalid"
    elif missing_expected_source_ids:
        source_id_status = "invalid"
    else:
        source_id_status = "valid"
    return {
        "exact_trace": exact_trace,
        "source_id_status": source_id_status,
        "source_id_trace": {
            "selected_source_ids": selected_source_ids,
            "expected_source_ids": expected_source_ids,
            "missing_expected_source_ids": missing_expected_source_ids,
            "unexpected_source_ids": unexpected_source_ids,
            "trace_basis": trace_basis,
        },
    }


def exact_trace_phrases(candidate: Any) -> list[str]:
    phrases = [
        candidate_source_phrase(candidate) or "",
        candidate.evidence_span.text,
    ]
    cleaned = [phrase.strip() for phrase in phrases if phrase and phrase.strip()]
    seen: set[str] = set()
    deduped: list[str] = []
    for phrase in cleaned:
        if phrase in seen:
            continue
        seen.add(phrase)
        deduped.append(phrase)
    return deduped


def candidate_has_exact_trace_evidence(candidate: Any) -> bool:
    return bool(exact_trace_phrases(candidate))


def has_primary_medication_cadence(
    assessment: ClinicalAssessment,
    candidate_set: CandidateSet,
) -> bool:
    by_id = {candidate.candidate_id: candidate for candidate in candidate_set.candidates}
    return any(
        is_medication_cadence_text(
            " ".join(
                part
                for part in [
                    candidate_source_phrase(candidate),
                    candidate.evidence_span.text,
                ]
                if part
            )
        )
        for candidate_id in assessment.primary_candidate_ids
        for candidate in [by_id.get(candidate_id)]
        if candidate is not None
    )


def has_seizure_free_proxy_evidence_overreach(
    assessment: ClinicalAssessment,
    candidate_set: CandidateSet,
) -> bool:
    by_id = {candidate.candidate_id: candidate for candidate in candidate_set.candidates}
    primary_candidates = [
        candidate
        for candidate_id in assessment.primary_candidate_ids
        for candidate in [by_id.get(candidate_id)]
        if candidate is not None
    ]
    if not primary_candidates:
        return False
    texts = [
        canonicalize_derivation_text(
            " ".join(
                part
                for part in [
                    candidate_source_phrase(candidate),
                    candidate.evidence_span.text,
                ]
                if part
            )
        )
        for candidate in primary_candidates
    ]
    explicit = any(is_explicit_seizure_free_text(text) for text in texts)
    proxy_or_conditional = any(
        is_seizure_free_proxy_or_conditional_text(text) for text in texts
    )
    unresolved = any(
        any("unresolved" in source_id for source_id in candidate.source_ids)
        for candidate in primary_candidates
    )
    return (proxy_or_conditional or unresolved) and not explicit


def is_explicit_seizure_free_text(text: str) -> bool:
    lower = text.lower()
    return any(
        marker in lower
        for marker in (
            "no seizures",
            "no seizure",
            "no events",
            "no further events",
            "seizure-free",
            "seizure free",
            "free of seizures",
        )
    )


def is_seizure_free_proxy_or_conditional_text(text: str) -> bool:
    lower = text.lower()
    return any(
        marker in lower
        for marker in (
            "rescue medication",
            "rescue med",
            "required",
            "injur",
            "admission",
            "attendances",
            "if breakthrough events recur",
            "breakthrough events recur",
            "if this occurs",
            "better over",
        )
    )


def dominant_vague_current_burden_label(
    assessment: ClinicalAssessment,
    candidate_set: CandidateSet,
) -> str | None:
    if assessment.aggregation_policy != "additive_same_window":
        return None
    by_id = {candidate.candidate_id: candidate for candidate in candidate_set.candidates}
    derived: list[tuple[str, float, Any]] = []
    for candidate_id in assessment.primary_candidate_ids:
        candidate = by_id.get(candidate_id)
        if candidate is None:
            continue
        if candidate.temporality not in {"current", "recent"}:
            continue
        text = " ".join(
            part
            for part in [
                candidate_source_phrase(candidate),
                candidate.evidence_span.text,
            ]
            if part
        )
        text = canonicalize_derivation_text(text)
        if not text or is_medication_cadence_text(text):
            continue
        label = selected_evidence_derivation.prediction_label_from_selected_evidence(
            text
        )
        if label in {None, "unknown", "no seizure frequency reference"}:
            continue
        try:
            record = label_to_frequency_record(label)
        except ValueError:
            continue
        derived.append((label, float(record.monthly_frequency), candidate))
    vague = [
        item
        for item in derived
        if item[0].startswith("multiple per ")
        and is_dominant_vague_frequency_text(
            " ".join(
                part
                for part in [
                    candidate_source_phrase(item[2]),
                    item[2].evidence_span.text,
                ]
                if part
            )
        )
    ]
    if not vague or len(derived) < 2:
        return None
    dominant_label, dominant_frequency, _ = max(vague, key=lambda item: item[1])
    context_frequencies = [
        frequency for label, frequency, _ in derived if label != dominant_label
    ]
    if not context_frequencies:
        return None
    if all(frequency < dominant_frequency for frequency in context_frequencies):
        return dominant_label
    return None


def is_dominant_vague_frequency_text(text: str) -> bool:
    lower = text.lower()
    return any(
        marker in lower
        for marker in (
            "most weekdays",
            "most days",
            "multiple days",
            "several days",
            "many days",
        )
    )


def canonicalize_derivation_text(text: str) -> str:
    return text.replace("\u2013", "-").replace("\u2014", "-").replace("\u2212", "-")


def has_primary_cyclic_vulnerability_window(
    assessment: ClinicalAssessment,
    candidate_set: CandidateSet,
) -> bool:
    by_id = {candidate.candidate_id: candidate for candidate in candidate_set.candidates}
    return any(
        is_cyclic_vulnerability_window_text(
            " ".join(
                part
                for part in [
                    candidate_source_phrase(candidate),
                    candidate.evidence_span.text,
                ]
                if part
            )
        )
        and not has_vague_multiple_burden(
            candidate.cluster_details.events_per_cluster
            if candidate.cluster_details is not None
            else None
        )
        for candidate_id in assessment.primary_candidate_ids
        for candidate in [by_id.get(candidate_id)]
        if candidate is not None and candidate.candidate_kind == "cluster_frequency"
    )


def has_normalized_cluster_cadence(burden: NormalizedBurden) -> bool:
    return (
        burden.cluster_count_low is not None
        and burden.cluster_count_high is not None
        and burden.cluster_period_low is not None
        and burden.cluster_period_high is not None
        and burden.cluster_period_unit is not None
    )


def has_unknown_cadence_multiple_cluster_burden(
    assessment: ClinicalAssessment,
    candidate_set: CandidateSet,
) -> bool:
    by_id = {candidate.candidate_id: candidate for candidate in candidate_set.candidates}
    if has_competing_renderable_frequency_candidate(assessment, candidate_set):
        return False
    for candidate_id in assessment.primary_candidate_ids:
        candidate = by_id.get(candidate_id)
        if candidate is None or candidate.candidate_kind != "cluster_frequency":
            continue
        if candidate.event_type not in {"seizure", "seizure_like_event"}:
            continue
        if candidate.cluster_details is None:
            continue
        if has_cluster_recurrence_cadence(candidate):
            continue
        if has_vague_multiple_burden(candidate.cluster_details.events_per_cluster):
            return True
    return False


def has_competing_renderable_frequency_candidate(
    assessment: ClinicalAssessment,
    candidate_set: CandidateSet,
) -> bool:
    primary_ids = set(assessment.primary_candidate_ids)
    for candidate in candidate_set.candidates:
        if candidate.candidate_id in primary_ids:
            continue
        if candidate.candidate_kind != "frequency_rate" or candidate.frequency is None:
            continue
        text = " ".join(
            part
            for part in [candidate.frequency.source_phrase, candidate.evidence_span.text]
            if part
        )
        if is_medication_cadence_text(text):
            continue
        if looks_renderable_frequency_text(text):
            return True
    return False


def has_cluster_recurrence_cadence(candidate: Any) -> bool:
    assert candidate.cluster_details is not None
    text = " ".join(
        part
        for part in [
            candidate.cluster_details.cluster_frequency,
            candidate.cluster_details.cluster_period,
        ]
        if part
    ).lower()
    if not text:
        return False
    if any(marker in text for marker in ("unknown", "unclear", "not specified")):
        return False
    if any(
        marker in text
        for marker in (
            "single day",
            "one day",
            "24-hour",
            "24 hour",
            "within that day",
        )
    ):
        return False
    return any(
        marker in text
        for marker in (
            "per ",
            "every ",
            "daily",
            "weekly",
            "monthly",
            "yearly",
            "annually",
            "day",
            "week",
            "month",
            "year",
        )
    )


def has_vague_multiple_burden(text: str | None) -> bool:
    if not text:
        return False
    lower = text.lower()
    return any(
        marker in lower
        for marker in (
            "multiple",
            "several",
            "many",
            "few",
            "repeated",
            "cluster of events",
            "episodes",
            "events",
        )
    )


def looks_renderable_frequency_text(text: str) -> bool:
    lower = text.lower()
    return any(
        marker in lower
        for marker in (
            "per day",
            "per week",
            "per month",
            "per year",
            "daily",
            "weekly",
            "monthly",
            "yearly",
        )
    )


def is_medication_cadence_text(text: str) -> bool:
    lower = text.lower()
    return any(
        marker in lower
        for marker in (
            "as needed",
            "as-needed",
            "clobazam",
            "rescue medication",
            "patient-led use",
            "treated with",
        )
    )


def is_cyclic_vulnerability_window_text(text: str) -> bool:
    lower = text.lower()
    return any(
        marker in lower
        for marker in (
            "perimenstrual",
            "peri-menstrual",
            "catamenial",
            "menstrual",
            "menstruation",
            "period",
        )
    )


def is_sleep_restricted_phrase(text: str) -> bool:
    lower = text.lower()
    return any(
        marker in lower
        for marker in (
            "sleep deprivation",
            "sleep-deprived",
            "sleep deprived",
            "curtailed sleep",
            "disrupted sleep",
            "lack of sleep",
            "short on sleep",
            "poor sleep",
            "sleep restricted",
            "sleep restriction",
        )
    )


def has_primary_sleep_restricted_pattern(
    assessment: ClinicalAssessment,
    candidate_set: CandidateSet,
) -> bool:
    by_id = {candidate.candidate_id: candidate for candidate in candidate_set.candidates}
    return any(
        is_sleep_restricted_phrase(
            " ".join(
                part
                for part in [
                    candidate_source_phrase(candidate),
                    candidate.evidence_span.text,
                ]
                if part
            )
        )
        for candidate_id in assessment.primary_candidate_ids
        for candidate in [by_id.get(candidate_id)]
        if candidate is not None
    )


def has_primary_cyclic_window_pattern_general(
    assessment: ClinicalAssessment,
    candidate_set: CandidateSet,
) -> bool:
    by_id = {candidate.candidate_id: candidate for candidate in candidate_set.candidates}
    return any(
        is_cyclic_vulnerability_window_text(
            " ".join(
                part
                for part in [
                    candidate_source_phrase(candidate),
                    candidate.evidence_span.text,
                ]
                if part
            )
        )
        for candidate_id in assessment.primary_candidate_ids
        for candidate in [by_id.get(candidate_id)]
        if candidate is not None
    )
