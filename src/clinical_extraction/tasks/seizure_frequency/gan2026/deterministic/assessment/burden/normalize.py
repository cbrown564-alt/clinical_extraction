"""Assessment burden normalization orchestrator."""

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
    NormalizedBurden,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.assessment.burden.cluster import (
    _cluster_burden,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.assessment.burden.frequency import (
    _additive_frequency_burden,
    _burden_from_label,
    _deterministic_label_from_source_phrase,
    _frequency_burden,
    _frequency_burden_from_anchor_window_primary_candidates,
    _frequency_burden_from_multi_month_bucket_phrase,
    _frequency_burden_from_multi_month_bucket_primary_candidates,
    _frequency_burden_from_primary_candidates,
    _has_seizure_free_label,
    _is_unrenderable_frequency_burden,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.assessment.common import (
    _candidate_parse_phrases,
    _candidates_by_ids,
    _duration_unit,
    _normalization_source_phrase,
    _small_number_to_float,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.candidates import (
    CandidateKind as DeterministicCandidateKind,
)


def normalize_assessment_burden(
    draft: AssessmentDraft,
    *,
    candidate_set: CandidateSet,
    disabled_ablation_switches: frozenset[str] = frozenset(),
) -> tuple[NormalizedBurden, list[str]]:
    """Deterministically parse source-near assessment burden values."""

    primary_candidates = _candidates_by_ids(candidate_set, draft.primary_candidate_ids)
    source_phrase = _normalization_source_phrase(draft, primary_candidates)
    reference_date = (
        candidate_set.row_context.reference_date.date
        if candidate_set.row_context.reference_date is not None
        else None
    )
    issues: list[str] = []
    if not source_phrase:
        issues.append("normalization_source_phrase_missing")

    if draft.assessment_kind == "frequency_rate":
        if draft.aggregation_policy == "additive_same_window":
            burden, additive_issues = _additive_frequency_burden(
                primary_candidates,
                source_phrase=source_phrase,
                disabled_ablation_switches=disabled_ablation_switches,
            )
            issues.extend(additive_issues)
            return burden, issues
        burden, rate_issues = _frequency_burden(
            source_phrase,
            disabled_ablation_switches=disabled_ablation_switches,
        )
        if _is_unrenderable_frequency_burden(burden):
            (
                anchor_repair,
                anchor_repair_issues,
                anchor_repair_matched,
            ) = _frequency_burden_from_anchor_window_primary_candidates(
                primary_candidates,
                candidate_set=candidate_set,
                disabled_ablation_switches=disabled_ablation_switches,
            )
            if anchor_repair is not None:
                issues.extend(
                    [
                        *rate_issues,
                        "frequency_rate_values_repaired_from_primary_candidate",
                        *anchor_repair_issues,
                    ]
                )
                return anchor_repair, issues
            if anchor_repair_matched:
                issues.extend([*rate_issues, *anchor_repair_issues])
                return burden, issues
            (
                multi_month_bucket_source_repair,
                multi_month_bucket_source_issues,
                multi_month_bucket_source_matched,
            ) = _frequency_burden_from_multi_month_bucket_phrase(
                source_phrase,
                reference_date=reference_date,
                disabled_ablation_switches=disabled_ablation_switches,
            )
            if multi_month_bucket_source_repair is not None:
                issues.extend([*rate_issues, *multi_month_bucket_source_issues])
                return multi_month_bucket_source_repair, issues
            if multi_month_bucket_source_matched:
                issues.extend([*rate_issues, *multi_month_bucket_source_issues])
                return burden, issues
            (
                multi_month_bucket_repair,
                multi_month_bucket_issues,
                multi_month_bucket_matched,
            ) = _frequency_burden_from_multi_month_bucket_primary_candidates(
                primary_candidates,
                candidate_set=candidate_set,
                disabled_ablation_switches=disabled_ablation_switches,
            )
            if multi_month_bucket_repair is not None:
                issues.extend(
                    [
                        *rate_issues,
                        "frequency_rate_values_repaired_from_primary_candidate",
                        *multi_month_bucket_issues,
                    ]
                )
                return multi_month_bucket_repair, issues
            if multi_month_bucket_matched:
                issues.extend([*rate_issues, *multi_month_bucket_issues])
                return burden, issues
            repaired = _frequency_burden_from_primary_candidates(
                primary_candidates,
                disabled_ablation_switches=disabled_ablation_switches,
            )
            if repaired is not None:
                burden, repair_issues = repaired
                issues.extend(
                    [
                        *rate_issues,
                        "frequency_rate_values_repaired_from_primary_candidate",
                        *repair_issues,
                    ]
                )
                return burden, issues
        issues.extend(rate_issues)
        return burden, issues

    if draft.assessment_kind == "cluster_frequency":
        burden, cluster_issues = _cluster_burden(primary_candidates, source_phrase=source_phrase)
        issues.extend(cluster_issues)
        return burden, issues

    if draft.assessment_kind == "seizure_free":
        burden, seizure_free_issues = _seizure_free_burden(source_phrase)
        if _is_prior_encounter_relative_interval_phrase(source_phrase):
            seizure_free_issues = [
                *seizure_free_issues,
                "seizure_free_anchor_from_prior_encounter_context",
                "prior_encounter_derived_seizure_free_duration",
            ]
        if _is_unrenderable_seizure_free_burden(burden):
            repaired = _seizure_free_burden_from_primary_candidates(primary_candidates)
            if repaired is not None:
                burden, repair_issues = repaired
                issues.extend(
                    [
                        *seizure_free_issues,
                        "seizure_free_duration_repaired_from_primary_candidate",
                        *repair_issues,
                    ]
                )
                return burden, issues
        issues.extend(seizure_free_issues)
        return burden, issues

    return NormalizedBurden(source_normalized_phrase=source_phrase), issues


def _is_prior_encounter_relative_interval_phrase(source_phrase: str) -> bool:
    return bool(
        re.search(
            r"\bsince\s+(?:(?:the|his|her|their)\s+)?(?:last|previous)\s+"
            r"(?:appointment|visit|review|consultation|clinic assessment)\s+"
            r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|"
            r"eleven|twelve)\s+(?:days?|weeks?|months?|years?)\s+ago\b",
            source_phrase,
            flags=re.IGNORECASE,
        )
    )


def _seizure_free_burden(source_phrase: str) -> tuple[NormalizedBurden, list[str]]:
    prior_encounter_burden = _prior_encounter_relative_duration_burden(source_phrase)
    if prior_encounter_burden is not None:
        return prior_encounter_burden, []
    label = _deterministic_label_from_source_phrase(
        source_phrase,
        preferred_kind=DeterministicCandidateKind.SEIZURE_FREE,
    )
    if label is None or not _has_seizure_free_label(label):
        return (
            NormalizedBurden(source_normalized_phrase=source_phrase),
            ["seizure_free_duration_unparsed"],
        )
    return _burden_from_label(label, source_phrase=source_phrase)


def _prior_encounter_relative_duration_burden(
    source_phrase: str,
) -> NormalizedBurden | None:
    match = re.search(
        r"\bsince\s+(?:(?:the|his|her|their)\s+)?(?:last|previous)\s+"
        r"(?:appointment|visit|review|consultation|clinic assessment)\s+"
        r"(?P<count>\d+|one|two|three|four|five|six|seven|eight|nine|ten|"
        r"eleven|twelve)\s+(?P<unit>days?|weeks?|months?|years?)\s+ago\b",
        source_phrase,
        flags=re.IGNORECASE,
    )
    if match is None:
        return None
    count = _small_number_to_float(match.group("count"))
    unit = _duration_unit(match.group("unit"))
    if count is None or unit is None:
        return None
    return NormalizedBurden(
        seizure_free_duration_low=count,
        seizure_free_duration_high=count,
        seizure_free_duration_unit=unit,
        source_normalized_phrase=source_phrase,
    )


def _seizure_free_burden_from_primary_candidates(
    primary_candidates: Sequence[ExtractedCandidate],
) -> tuple[NormalizedBurden, list[str]] | None:
    parsed: list[tuple[int, NormalizedBurden, list[str]]] = []
    for candidate in primary_candidates:
        if candidate.candidate_kind != "seizure_free":
            continue
        for phrase in _candidate_parse_phrases(candidate):
            burden, issues = _seizure_free_burden(phrase)
            if _is_unrenderable_seizure_free_burden(burden):
                continue
            parsed.append((len(burden.source_normalized_phrase), burden, issues))
    if not parsed:
        return None
    _score, burden, issues = max(parsed, key=lambda item: item[0])
    return burden, issues


def _is_unrenderable_seizure_free_burden(burden: NormalizedBurden) -> bool:
    return (
        burden.seizure_free_duration_low is None
        or burden.seizure_free_duration_high is None
        or burden.seizure_free_duration_unit is None
    )
