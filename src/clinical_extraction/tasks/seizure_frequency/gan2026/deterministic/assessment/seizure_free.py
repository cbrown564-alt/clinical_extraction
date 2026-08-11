"""Seizure-free duration instrumentation for clinical assessment assembly."""

from __future__ import annotations

import re
from collections.abc import Sequence

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.assessment_draft import (
    AssessmentDraft,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
    ExtractedCandidate,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.clinical_assessment import (
    AntecedentReference,
    ComputedDuration,
    DateReference,
    NormalizedBurden,
    SeizureFreeInstrumentation,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.assessment.common import (
    _candidate_parse_phrases,
    _candidates_by_ids,
    _clean_phrase,
    _dedupe,
    _disabled_switch_issue,
    _normalization_source_phrase,
    _source_ids_from_candidates,
)
from clinical_extraction.tasks.shared.epilepsy.terms import MONTH_NAME_PATTERN

from .burden_normalization import (
    _is_unrenderable_seizure_free_burden,
)
from .date_anchor_parsing import (
    _extract_seizure_free_anchor_date,
    _mentions_since_anchor,
    _whole_months_between,
)


def _instrument_seizure_free_duration(
    draft: AssessmentDraft,
    *,
    candidate_set: CandidateSet,
    normalized_burden: NormalizedBurden,
    disabled_ablation_switches: frozenset[str] = frozenset(),
) -> tuple[NormalizedBurden, SeizureFreeInstrumentation | None, list[str]]:
    if not _is_unrenderable_seizure_free_burden(normalized_burden):
        return normalized_burden, None, []

    primary_candidates = _candidates_by_ids(candidate_set, draft.primary_candidate_ids)
    source_phrase = _normalization_source_phrase(draft, primary_candidates)
    reference = candidate_set.row_context.reference_date
    anchor: DateReference | None = None
    anchor_issues: list[str] = []
    antecedent: AntecedentReference | None = None
    instrumentation_source_phrase = source_phrase
    for phrase in _seizure_free_instrumentation_phrases(draft, primary_candidates):
        anchor, anchor_issues = _extract_seizure_free_anchor_date(
            phrase,
            reference_date=reference.date if reference is not None else None,
        )
        if anchor is not None:
            instrumentation_source_phrase = phrase
            break
    if anchor is None:
        antecedent, anchor_issues = _extract_same_note_since_then_antecedent(
            draft,
            primary_candidates,
            reference_date=reference.date if reference is not None else None,
        )
        if antecedent is not None:
            anchor = antecedent.anchor_date
    if anchor is None and _mentions_prior_encounter_anchor(source_phrase):
        if "normalize_seizure_free_prior_encounter_anchor" in disabled_ablation_switches:
            anchor_issues.append(
                _disabled_switch_issue("normalize_seizure_free_prior_encounter_anchor")
            )
        else:
            prior_encounter = candidate_set.row_context.prior_encounter
            if prior_encounter is not None:
                anchor = DateReference(
                    date=prior_encounter.date,
                    date_precision=prior_encounter.date_precision,
                    source=(f"candidate_set.row_context.prior_encounter:{prior_encounter.source}"),
                    source_phrase=prior_encounter.source_phrase,
                )
                anchor_issues = [
                    "seizure_free_anchor_from_prior_encounter_context",
                    "prior_encounter_derived_seizure_free_duration",
                    *prior_encounter.issues,
                ]
    if anchor is None:
        if _mentions_since_anchor(source_phrase):
            instrumentation = SeizureFreeInstrumentation(
                state_kind="unresolved_anchor",
                source_phrase=source_phrase,
                source_candidate_ids=list(draft.primary_candidate_ids),
                source_ids=_source_ids_from_candidates(primary_candidates),
                instrumentation_issues=["seizure_free_since_date_anchor_unparsed"],
            )
            return (
                normalized_burden,
                instrumentation,
                ["seizure_free_since_date_anchor_unparsed", *anchor_issues],
            )
        return normalized_burden, None, []

    if reference is None:
        instrumentation = SeizureFreeInstrumentation(
            state_kind="unresolved_anchor",
            source_phrase=instrumentation_source_phrase,
            anchor_date=anchor,
            antecedent=antecedent,
            source_candidate_ids=list(draft.primary_candidate_ids),
            source_ids=_source_ids_from_candidates(primary_candidates),
            instrumentation_issues=["reference_date_missing_for_since_date"],
        )
        return normalized_burden, instrumentation, ["reference_date_missing_for_since_date"]

    duration_months = _whole_months_between(anchor.date, reference.date)
    if duration_months is None:
        instrumentation = SeizureFreeInstrumentation(
            state_kind="unresolved_anchor",
            source_phrase=instrumentation_source_phrase,
            anchor_date=anchor,
            antecedent=antecedent,
            reference_date=DateReference(
                date=reference.date,
                date_precision=reference.date_precision,
                source=f"candidate_set.row_context.reference_date:{reference.source}",
                source_phrase=reference.source_phrase,
            ),
            source_candidate_ids=list(draft.primary_candidate_ids),
            source_ids=_source_ids_from_candidates(primary_candidates),
            instrumentation_issues=["seizure_free_since_date_duration_uncomputed"],
        )
        return (
            normalized_burden,
            instrumentation,
            ["seizure_free_since_date_duration_uncomputed"],
        )

    instrumentation = SeizureFreeInstrumentation(
        state_kind="since_date",
        source_phrase=instrumentation_source_phrase,
        anchor_date=anchor,
        antecedent=antecedent,
        reference_date=DateReference(
            date=reference.date,
            date_precision=reference.date_precision,
            source=f"candidate_set.row_context.reference_date:{reference.source}",
            source_phrase=reference.source_phrase,
        ),
        computed_duration=ComputedDuration(
            low=float(duration_months),
            high=float(duration_months),
            unit="month",
        ),
        source_candidate_ids=list(draft.primary_candidate_ids),
        source_ids=_source_ids_from_candidates(primary_candidates),
    )
    return (
        normalized_burden.model_copy(
            update={
                "seizure_free_duration_low": float(duration_months),
                "seizure_free_duration_high": float(duration_months),
                "seizure_free_duration_unit": "month",
            }
        ),
        instrumentation,
        ["seizure_free_duration_instrumented_from_since_date", *anchor_issues],
    )


def _seizure_free_instrumentation_phrases(
    draft: AssessmentDraft,
    primary_candidates: Sequence[ExtractedCandidate],
) -> list[str]:
    source_phrase = _normalization_source_phrase(draft, primary_candidates)
    phrases = [source_phrase]
    for candidate in primary_candidates:
        phrases.extend(_candidate_parse_phrases(candidate))
    return [phrase for phrase in _dedupe([_clean_phrase(phrase) for phrase in phrases]) if phrase]


def _extract_same_note_since_then_antecedent(
    draft: AssessmentDraft,
    primary_candidates: Sequence[ExtractedCandidate],
    *,
    reference_date: str | None,
) -> tuple[AntecedentReference | None, list[str]]:
    if reference_date is None:
        return None, []
    source_phrase = _normalization_source_phrase(draft, primary_candidates)
    if not _mentions_since_then_anchor(source_phrase):
        return None, []

    candidates: list[tuple[str, DateReference, list[str]]] = []
    for context in _same_note_antecedent_contexts(draft, primary_candidates):
        for phrase in _antecedent_date_phrases(context):
            anchor, issues = _extract_seizure_free_anchor_date(
                f"since {phrase}",
                reference_date=reference_date,
            )
            if anchor is None:
                continue
            candidates.append(
                (
                    _clean_phrase(_antecedent_source_phrase(context, phrase)),
                    anchor,
                    issues,
                )
            )

    deduped: list[tuple[str, DateReference, list[str]]] = []
    seen: set[tuple[str, str]] = set()
    for source_phrase, anchor, issues in candidates:
        key = (anchor.date, source_phrase.lower())
        if key in seen:
            continue
        seen.add(key)
        deduped.append((source_phrase, anchor, issues))
    unique_dates = {anchor.date for _, anchor, _ in deduped}
    if len(deduped) != 1 or len(unique_dates) != 1:
        return None, []

    source_phrase, anchor, issues = deduped[0]
    return (
        AntecedentReference(
            source_phrase=source_phrase,
            anchor_date=anchor,
            link_type="local_since_then_antecedent",
            source_candidate_ids=list(draft.primary_candidate_ids),
        ),
        [
            "seizure_free_anchor_from_same_note_antecedent",
            *issues,
        ],
    )


def _mentions_since_then_anchor(source_phrase: str) -> bool:
    normalized = source_phrase.strip().lower()
    return bool(
        re.search(r"\bsince\s+then\b", normalized) or re.search(r"\bsince\s*\.?$", normalized)
    )


def _mentions_prior_encounter_anchor(source_phrase: str) -> bool:
    return bool(
        re.search(
            r"\bsince\s+(?:(?:the|his|her|their)\s+)?(?:last|previous)\s+"
            r"(?:appointment|visit|review|consultation|clinic assessment)\b",
            source_phrase,
            flags=re.IGNORECASE,
        )
    )


def _same_note_antecedent_contexts(
    draft: AssessmentDraft,
    primary_candidates: Sequence[ExtractedCandidate],
) -> list[str]:
    contexts = [draft.assessment_summary]
    for candidate in primary_candidates:
        contexts.extend(_candidate_parse_phrases(candidate))
    return [
        context for context in _dedupe([_clean_phrase(context) for context in contexts]) if context
    ]


def _antecedent_date_phrases(context: str) -> list[str]:
    phrases: list[str] = []
    month = rf"(?:{MONTH_NAME_PATTERN})"
    patterns = [
        rf"\b\d{{1,2}}(?:\s+|-){month}(?:\s+|-)\d{{4}}\b",
        rf"\b\d{{1,2}}(?:\s+|-){month}\b",
        rf"\b(?:early|mid|late)\s+{month}\s+\d{{4}}\b",
        rf"\b(?:early|mid|late)\s+{month}\b",
        rf"\b{month}\s+\d{{4}}\b",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, context, flags=re.IGNORECASE):
            phrases.append(match.group(0))
    return _dedupe(phrases)


def _antecedent_source_phrase(context: str, phrase: str) -> str:
    lower_context = context.lower()
    lower_phrase = phrase.lower()
    position = lower_context.find(lower_phrase)
    if position < 0:
        return phrase
    punctuation_before = [
        lower_context.rfind(separator, 0, position) for separator in (".", ";", ":")
    ]
    start = max(punctuation_before) + 1
    punctuation_after = [
        found
        for separator in (".", ";", ":")
        for found in [lower_context.find(separator, position + len(phrase))]
        if found >= 0
    ]
    end = min(punctuation_after) if punctuation_after else len(context)
    return context[start:end].strip() or phrase
