"""Deterministic assessment burden normalization."""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.assessment_draft import (
    AssessmentDraft,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
    ExtractedCandidate,
    candidate_source_phrase,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.clinical_assessment import (
    NormalizedBurden,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic import (
    deterministic_extraction,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.assessment.common import (
    DISABLED_SWITCH_ISSUE_PREFIX,
    _candidate_parse_phrases,
    _candidates_by_ids,
    _clean_phrase,
    _cluster_phrases,
    _disabled_switch_issue,
    _duration_unit,
    _normalization_source_phrase,
    _normalize_phrase_for_parse,
    _small_number_to_float,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.assessment.date_anchor_parsing import (
    _extract_explicit_multi_month_window_months,
    _extract_frequency_anchor_window_date,
    _extract_frequency_article_month_bucket_matches,
    _extract_frequency_current_month_bucket_match,
    _extract_frequency_multi_month_bucket_matches,
    _extract_frequency_summary_count_with_month_list,
    _extract_month_mentions,
    _inclusive_month_span,
    _reference_month_iso,
    _whole_months_between,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.candidates import (
    CandidateKind as DeterministicCandidateKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.selected_evidence import (
    selected_evidence_derivation,
)

def _frequency_burden_specificity_score(burden: NormalizedBurden) -> tuple[int, int]:
    return (
        1 if burden.count_low is not None and burden.count_high is not None else 0,
        len(burden.source_normalized_phrase),
    )

def _is_renderable_frequency_burden(burden: NormalizedBurden) -> bool:
    if burden.period_low is None or burden.period_high is None or burden.period_unit is None:
        return False
    return (
        burden.vague_count is not None
        or (burden.count_low is not None and burden.count_high is not None)
    )

def _is_renderable_cluster_burden(burden: NormalizedBurden) -> bool:
    return (
        burden.cluster_count_low is not None
        and burden.cluster_count_high is not None
        and burden.cluster_period_low is not None
        and burden.cluster_period_high is not None
        and burden.cluster_period_unit is not None
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

def _frequency_burden(
    source_phrase: str,
    *,
    disabled_ablation_switches: frozenset[str] = frozenset(),
) -> tuple[NormalizedBurden, list[str]]:
    parse_phrase = _normalize_phrase_for_parse(source_phrase)
    if _is_relative_only_trend_phrase(parse_phrase):
        return NormalizedBurden(source_normalized_phrase=source_phrase), [
            "relative_change_without_current_baseline"
        ]
    if _is_conditional_only_trigger_phrase(parse_phrase):
        return NormalizedBurden(source_normalized_phrase=source_phrase), [
            "conditional_only_trigger_without_baseline"
        ]
    selected_evidence_label = (
        selected_evidence_derivation.prediction_label_from_selected_evidence(parse_phrase)
    )
    if (
        selected_evidence_label is not None
        and selected_evidence_label.startswith("multiple per ")
        and _is_vague_frequency_with_explicit_time_period_phrase(parse_phrase)
    ):
        burden, issues = _burden_from_label(
            selected_evidence_label,
            source_phrase=source_phrase,
        )
        return burden, ["vague_frequency_with_explicit_time_period", *issues]
    if (
        _is_previous_month_active_rate_phrase(parse_phrase)
        and "project_previous_active_month_over_current_month_zero"
        not in disabled_ablation_switches
    ):
        return (
            NormalizedBurden(
                vague_count="multiple",
                period_low=1,
                period_high=1,
                period_unit="month",
                source_normalized_phrase=source_phrase,
            ),
            ["previous_month_active_rate_over_current_zero", "vague_count"],
        )
    if (
        _is_previous_month_active_rate_phrase(parse_phrase)
        and "project_previous_active_month_over_current_month_zero"
        in disabled_ablation_switches
    ):
        return NormalizedBurden(source_normalized_phrase=source_phrase), [
            _disabled_switch_issue(
                "project_previous_active_month_over_current_month_zero"
            )
        ]
    label = _deterministic_label_from_source_phrase(
        parse_phrase,
        preferred_kind=DeterministicCandidateKind.FREQUENCY_RATE,
    )
    if label is None:
        return NormalizedBurden(source_normalized_phrase=source_phrase), [
            "frequency_rate_values_unparsed"
        ]
    burden, issues = _burden_from_label(label, source_phrase=source_phrase)
    if (
        not _is_unrenderable_frequency_burden(burden)
        and _is_explicit_summary_rate_phrase(parse_phrase)
        and "project_current_summary_rate_priority" not in disabled_ablation_switches
    ):
        issues = ["explicit_summary_rate_over_long_period_average", *issues]
    elif (
        not _is_unrenderable_frequency_burden(burden)
        and _is_explicit_summary_rate_phrase(parse_phrase)
        and "project_current_summary_rate_priority" in disabled_ablation_switches
    ):
        return NormalizedBurden(source_normalized_phrase=source_phrase), [
            _disabled_switch_issue("project_current_summary_rate_priority")
        ]
    if _has_cluster_label(label):
        issues.append("frequency_rate_label_derivation_returned_cluster")
    if _has_seizure_free_label(label):
        issues.append("frequency_rate_label_derivation_returned_seizure_free")
    return burden, issues

def _frequency_burden_from_anchor_window_primary_candidates(
    primary_candidates: Sequence[ExtractedCandidate],
    *,
    candidate_set: CandidateSet,
    disabled_ablation_switches: frozenset[str] = frozenset(),
) -> tuple[NormalizedBurden | None, list[str], bool]:
    parsed: list[tuple[tuple[int, int], NormalizedBurden, list[str]]] = []
    matched_any = False
    disabled_issues: list[str] = []
    reference_date = (
        candidate_set.row_context.reference_date.date
        if candidate_set.row_context.reference_date is not None
        else None
    )
    for candidate in primary_candidates:
        if candidate.candidate_kind != "frequency_rate":
            continue
        for phrase in _candidate_parse_phrases(candidate):
            burden, issues, matched = _frequency_burden_from_anchor_window_phrase(
                phrase,
                reference_date=reference_date,
                disabled_ablation_switches=disabled_ablation_switches,
            )
            if not matched:
                continue
            matched_any = True
            if burden is None:
                disabled_issues = issues
                continue
            parsed.append(
                (
                    _frequency_burden_specificity_score(burden),
                    burden,
                    issues,
                )
            )
    if parsed:
        _score, burden, issues = max(parsed, key=lambda item: item[0])
        return burden, issues, True
    return None, disabled_issues, matched_any

def _frequency_burden_from_multi_month_bucket_primary_candidates(
    primary_candidates: Sequence[ExtractedCandidate],
    *,
    candidate_set: CandidateSet,
    disabled_ablation_switches: frozenset[str] = frozenset(),
) -> tuple[NormalizedBurden | None, list[str], bool]:
    parsed: list[tuple[tuple[int, int], NormalizedBurden, list[str]]] = []
    matched_any = False
    disabled_issues: list[str] = []
    reference_date = (
        candidate_set.row_context.reference_date.date
        if candidate_set.row_context.reference_date is not None
        else None
    )
    for candidate in primary_candidates:
        if candidate.candidate_kind != "frequency_rate":
            continue
        for phrase in _candidate_parse_phrases(candidate):
            burden, issues, matched = _frequency_burden_from_multi_month_bucket_phrase(
                phrase,
                reference_date=reference_date,
                disabled_ablation_switches=disabled_ablation_switches,
            )
            if not matched:
                continue
            matched_any = True
            if burden is None:
                disabled_issues = issues
                continue
            parsed.append(
                (
                    _frequency_burden_specificity_score(burden),
                    burden,
                    issues,
                )
            )
    if parsed:
        _score, burden, issues = max(parsed, key=lambda item: item[0])
        return burden, issues, True
    return None, disabled_issues, matched_any

def _frequency_burden_from_multi_month_bucket_phrase(
    source_phrase: str,
    *,
    reference_date: str | None,
    disabled_ablation_switches: frozenset[str] = frozenset(),
) -> tuple[NormalizedBurden | None, list[str], bool]:
    normalized = _normalize_phrase_for_parse(source_phrase)
    if _has_per_cluster_frequency_terms(normalized):
        return None, [], False
    bucket_matches = _extract_frequency_multi_month_bucket_matches(
        normalized,
        reference_date=reference_date,
    )
    current_month_bucket = _extract_frequency_current_month_bucket_match(
        normalized,
        reference_date=reference_date,
    )
    if current_month_bucket is not None and not any(
        match["month_iso"] == current_month_bucket["month_iso"]
        for match in bucket_matches
    ):
        bucket_matches.append(current_month_bucket)
    for article_match in _extract_frequency_article_month_bucket_matches(
        normalized,
        reference_date=reference_date,
    ):
        if any(match["month_iso"] == article_match["month_iso"] for match in bucket_matches):
            continue
        bucket_matches.append(article_match)
    explicit_window_months = _extract_explicit_multi_month_window_months(normalized)
    if not bucket_matches:
        summary_count = _extract_frequency_summary_count_with_month_list(
            normalized,
            reference_date=reference_date,
        )
        if summary_count is None or explicit_window_months is None:
            return None, [], False
        count_low, count_high, inferred_year = summary_count
        if "normalize_frequency_multi_month_bucket_value_recovery" in disabled_ablation_switches:
            return (
                None,
                [_disabled_switch_issue("normalize_frequency_multi_month_bucket_value_recovery")],
                True,
            )
        issues = [
            "frequency_rate_values_repaired_from_multi_month_bucket",
            "frequency_rate_multi_month_window_from_source_phrase",
        ]
        if inferred_year:
            issues.append("frequency_rate_bucket_year_inferred_from_reference_date")
        return (
            NormalizedBurden(
                count_low=count_low,
                count_high=count_high,
                period_low=float(explicit_window_months),
                period_high=float(explicit_window_months),
                period_unit="month",
                source_normalized_phrase=normalized,
            ),
            issues,
            True,
        )
    if len(bucket_matches) < 2 and explicit_window_months is None:
        return None, [], False
    if "normalize_frequency_multi_month_bucket_value_recovery" in disabled_ablation_switches:
        return (
            None,
            [_disabled_switch_issue("normalize_frequency_multi_month_bucket_value_recovery")],
            True,
        )
    count_low = sum(match["count_low"] for match in bucket_matches)
    count_high = sum(match["count_high"] for match in bucket_matches)
    if explicit_window_months is not None:
        denominator_months = explicit_window_months
        denominator_issue = "frequency_rate_multi_month_window_from_source_phrase"
    else:
        denominator_months = _inclusive_month_span(
            [match["month_iso"] for match in bucket_matches]
        )
        denominator_issue = "frequency_rate_multi_month_window_from_named_buckets"
    if denominator_months is None or denominator_months <= 1:
        return None, [], False
    issues = [
        "frequency_rate_values_repaired_from_multi_month_bucket",
        denominator_issue,
    ]
    if any(match["year_inferred"] for match in bucket_matches):
        issues.append("frequency_rate_bucket_year_inferred_from_reference_date")
    return (
        NormalizedBurden(
            count_low=float(count_low),
            count_high=float(count_high),
            period_low=float(denominator_months),
            period_high=float(denominator_months),
            period_unit="month",
            source_normalized_phrase=normalized,
        ),
        issues,
        True,
    )

def _frequency_burden_from_anchor_window_phrase(
    source_phrase: str,
    *,
    reference_date: str | None,
    disabled_ablation_switches: frozenset[str] = frozenset(),
) -> tuple[NormalizedBurden | None, list[str], bool]:
    normalized = _normalize_phrase_for_parse(source_phrase)
    if reference_date is None:
        return None, [], False
    count_match = re.search(
        r"\b(?P<low>\d+|one|two|three|four|five|six|seven|eight|nine|ten|"
        r"eleven|twelve)"
        r"(?:\s+to\s+(?P<high>\d+|one|two|three|four|five|six|seven|eight|"
        r"nine|ten|eleven|twelve))?"
        r"(?:\s+\w+){0,4}\s+"
        r"(?:jerks?|seizures?|events?|episodes?|absences?|spasms?)\b",
        normalized,
        flags=re.IGNORECASE,
    )
    if count_match is None:
        return None, [], False
    low = _small_number_to_float(count_match.group("low"))
    high = _small_number_to_float(count_match.group("high") or count_match.group("low"))
    if low is None or high is None:
        return None, [], False
    anchor_date, anchor_issues, matched = _extract_frequency_anchor_window_date(
        normalized,
        reference_date=reference_date,
    )
    if anchor_date is None or not matched:
        return None, [], False
    if "normalize_frequency_anchor_window_value_recovery" in disabled_ablation_switches:
        return (
            None,
            [_disabled_switch_issue("normalize_frequency_anchor_window_value_recovery")],
            True,
        )
    elapsed_months = _whole_months_between(anchor_date, reference_date)
    if elapsed_months is None or elapsed_months <= 0:
        return None, [], False
    anchor_bonus = 1 if "frequency_rate_anchor_from_last_event_phrase" in anchor_issues else 0
    return (
        NormalizedBurden(
            count_low=low + anchor_bonus,
            count_high=high + anchor_bonus,
            period_low=float(elapsed_months),
            period_high=float(elapsed_months),
            period_unit="month",
            source_normalized_phrase=normalized,
        ),
        ["frequency_rate_values_repaired_from_anchor_window", *anchor_issues],
        True,
    )

def _frequency_burden_from_primary_candidates(
    primary_candidates: Sequence[ExtractedCandidate],
    *,
    disabled_ablation_switches: frozenset[str] = frozenset(),
) -> tuple[NormalizedBurden, list[str]] | None:
    parsed: list[tuple[tuple[int, int], NormalizedBurden, list[str]]] = []
    for candidate in primary_candidates:
        if candidate.candidate_kind != "frequency_rate":
            continue
        for phrase in _candidate_parse_phrases(candidate):
            burden, issues = _frequency_burden(
                phrase,
                disabled_ablation_switches=disabled_ablation_switches,
            )
            if _is_unrenderable_frequency_burden(burden):
                continue
            parsed.append(
                (
                    _frequency_burden_specificity_score(burden),
                    burden,
                    [issue for issue in issues if issue != "vague_count"],
                )
            )
    if not parsed:
        return None
    _score, burden, issues = max(parsed, key=lambda item: item[0])
    return burden, issues

def _additive_frequency_burden(
    primary_candidates: Sequence[ExtractedCandidate],
    *,
    source_phrase: str,
    disabled_ablation_switches: frozenset[str] = frozenset(),
) -> tuple[NormalizedBurden, list[str]]:
    parsed = [
        _frequency_burden(
            candidate_source_phrase(candidate) or candidate.evidence_span.text,
            disabled_ablation_switches=disabled_ablation_switches,
        )
        for candidate in primary_candidates
    ]
    issues = [issue for _, burden_issues in parsed for issue in burden_issues]
    burdens = [burden for burden, _ in parsed]
    if not burdens:
        return NormalizedBurden(source_normalized_phrase=source_phrase), [
            "additive_frequency_primary_candidates_missing"
        ]
    first = burdens[0]
    same_period = all(
        burden.period_low == first.period_low
        and burden.period_high == first.period_high
        and burden.period_unit == first.period_unit
        for burden in burdens
    )
    if not same_period:
        # Fall back to the most specific single primary candidate's rate
        fallback = _frequency_burden_from_primary_candidates(
            primary_candidates,
            disabled_ablation_switches=disabled_ablation_switches,
        )
        if fallback is not None:
            fallback_burden, fallback_issues = fallback
            return fallback_burden, [
                *issues,
                "additive_frequency_period_mismatch",
                "additive_frequency_fallback_to_primary_candidate",
                *fallback_issues,
            ]
        return NormalizedBurden(source_normalized_phrase=source_phrase), [
            *issues,
            "additive_frequency_period_mismatch",
        ]
    if any(burden.count_low is None or burden.count_high is None for burden in burdens):
        # Fall back to the most specific single primary candidate's rate
        fallback = _frequency_burden_from_primary_candidates(
            primary_candidates,
            disabled_ablation_switches=disabled_ablation_switches,
        )
        if fallback is not None:
            fallback_burden, fallback_issues = fallback
            return fallback_burden, [
                *issues,
                "additive_frequency_count_unparsed",
                "additive_frequency_fallback_to_primary_candidate",
                *fallback_issues,
            ]
        return NormalizedBurden(source_normalized_phrase=source_phrase), [
            *issues,
            "additive_frequency_count_unparsed",
        ]
    return (
        NormalizedBurden(
            count_low=sum(float(burden.count_low or 0) for burden in burdens),
            count_high=sum(float(burden.count_high or 0) for burden in burdens),
            period_low=first.period_low,
            period_high=first.period_high,
            period_unit=first.period_unit,
            source_normalized_phrase=source_phrase,
        ),
        issues,
    )

def _cluster_burden(
    primary_candidates: Sequence[ExtractedCandidate],
    *,
    source_phrase: str,
) -> tuple[NormalizedBurden, list[str]]:
    text = "; ".join(_cluster_phrases(primary_candidates)) or source_phrase
    label = _deterministic_label_from_source_phrase(
        text,
        preferred_kind=DeterministicCandidateKind.CLUSTER_FREQUENCY,
    )
    if label is None:
        return NormalizedBurden(source_normalized_phrase=source_phrase), [
            "cluster_frequency_values_unparsed"
        ]
    burden, issues = _cluster_burden_from_label(label, source_phrase=source_phrase)
    return burden, issues

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

def _has_per_cluster_frequency_terms(source_phrase: str) -> bool:
    return bool(
        re.search(r"\bper\s+cluster\b", source_phrase, flags=re.IGNORECASE)
        or re.search(r"\bclusters?\s+every\b", source_phrase, flags=re.IGNORECASE)
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

def _is_unrenderable_frequency_burden(burden: NormalizedBurden) -> bool:
    return not _is_renderable_frequency_burden(burden)

def _is_unrenderable_seizure_free_burden(burden: NormalizedBurden) -> bool:
    return (
        burden.seizure_free_duration_low is None
        or burden.seizure_free_duration_high is None
        or burden.seizure_free_duration_unit is None
    )

def _is_relative_only_trend_phrase(source_phrase: str) -> bool:
    return bool(
        re.search(
            r"\bfrequency\s+"
            r"(?:increased|decreased|improved|worsened|reduced)\s+"
            r"(?:by\s+)?(?:about\s+|approximately\s+|~)?"
            r"(?:\d+(?:\.\d+)?\s*%|\d+(?:\.\d+)?)\b",
            source_phrase,
            flags=re.IGNORECASE,
        )
    )

def _is_vague_frequency_with_explicit_time_period_phrase(source_phrase: str) -> bool:
    return bool(
        re.search(
            r"\b(?:several|multiple|many|few|a few)\b"
            r".{0,60}\b(?:day|week|month|year)s?\b",
            source_phrase,
            flags=re.IGNORECASE,
        )
    )

def _is_conditional_only_trigger_phrase(source_phrase: str) -> bool:
    return bool(
        re.search(
            r"\b(?:seizures?|events?|episodes?)\b.*\b(?:only|exclusively)\s+"
            r"(?:after|when|if|with|during)\b",
            source_phrase,
            flags=re.IGNORECASE,
        )
        or re.search(
            r"\b(?:seizures?|events?|episodes?)\b.*\b(?:when|if|with|during)\b"
            r".{0,60}\bonly\b",
            source_phrase,
            flags=re.IGNORECASE,
        )
    )

def _is_explicit_summary_rate_phrase(source_phrase: str) -> bool:
    has_long_window_summary = re.search(
        r"\b(?:so\s+far\s+this\s+year|year\s+to\s+date|this\s+year\s+to\s+date)\b",
        source_phrase,
        flags=re.IGNORECASE,
    )
    has_current_summary_cue = re.search(
        r"\b(?:at\s+present|currently|now)\b",
        source_phrase,
        flags=re.IGNORECASE,
    ) or re.search(
        r"\b(?:his|her|their|the)\s+(?:current|typical)\s+pattern\s+is\b",
        source_phrase,
        flags=re.IGNORECASE,
    )
    has_rate_language = re.search(
        r"\b(?:daily|weekly|monthly|yearly|annually|per\s+day|per\s+week|per\s+month|"
        r"per\s+year|once|twice)\b",
        source_phrase,
        flags=re.IGNORECASE,
    )
    return bool(has_long_window_summary and has_current_summary_cue and has_rate_language)

def _is_previous_month_active_rate_phrase(source_phrase: str) -> bool:
    return bool(
        re.search(
            r"\b(?:handful|multiple|several|many|few)\b[^.]{0,120}\b"
            r"(?:(?:during|in)\s+(?:the\s+)?(?:previous|last)\s+month|"
            r"occurred\s+(?:the\s+)?last\s+month)\b",
            source_phrase,
            flags=re.IGNORECASE,
        )
        and re.search(
            r"\b(?:(?:current|this)\s+month(?:\s+to\s+date)?|so\s+far\s+this\s+month)\b"
            r"[^.]{0,120}\b(?:there\s+have\s+been\s+)?no\s+(?:events?|seizures?|episodes?)\b",
            source_phrase,
            flags=re.IGNORECASE,
        )
    )

def _deterministic_label_from_source_phrase(
    source_phrase: str,
    *,
    preferred_kind: DeterministicCandidateKind,
) -> str | None:
    candidates = deterministic_extraction._extract_candidates(source_phrase)
    preferred = [
        candidate.label
        for candidate in candidates
        if candidate.kind is preferred_kind and candidate.label
    ]
    if preferred:
        return _prefer_most_specific_label(preferred)
    fallback = selected_evidence_derivation.prediction_label_from_selected_evidence(
        source_phrase
    )
    return fallback

def _prefer_most_specific_label(labels: Sequence[str]) -> str:
    return max(labels, key=_label_specificity_score)

def _label_specificity_score(label: str) -> tuple[int, int]:
    normalized = label.lower()
    return (
        1 if "multiple" not in normalized and "unknown" not in normalized else 0,
        len(normalized),
    )

def _burden_from_label(
    label: str,
    *,
    source_phrase: str,
) -> tuple[NormalizedBurden, list[str]]:
    normalized = " ".join(label.lower().split())
    if _has_seizure_free_label(normalized):
        return _seizure_free_burden_from_label(normalized, source_phrase=source_phrase)
    if _has_cluster_label(normalized):
        return _cluster_burden_from_label(normalized, source_phrase=source_phrase)
    if normalized in {"unknown", "no seizure frequency reference"}:
        return NormalizedBurden(source_normalized_phrase=source_phrase), []
    return _rate_burden_from_label(normalized, source_phrase=source_phrase)

def _cluster_burden_from_label(
    label: str,
    *,
    source_phrase: str,
) -> tuple[NormalizedBurden, list[str]]:
    normalized = " ".join(label.lower().split())
    if not _has_cluster_label(normalized):
        burden, issues = _rate_burden_from_label(normalized, source_phrase=source_phrase)
        return (
            NormalizedBurden(
                cluster_count_low=burden.count_low,
                cluster_count_high=burden.count_high,
                cluster_period_low=burden.period_low,
                cluster_period_high=burden.period_high,
                cluster_period_unit=burden.period_unit,
                source_normalized_phrase=source_phrase,
            ),
            issues,
        )
    match = re.match(
        r"^(?P<count>multiple|\d+(?:\.\d+)?(?:\s+to\s+\d+(?:\.\d+)?)?)\s+"
        r"clusters?\s+per\s+"
        r"(?:(?P<period_count>\d+(?:\.\d+)?(?:\s+to\s+\d+(?:\.\d+)?)?)\s+)?"
        r"(?P<period_unit>day|week|month|year),\s+"
        r"(?P<events>multiple|\d+(?:\.\d+)?(?:\s+to\s+\d+(?:\.\d+)?)?)\s+"
        r"per\s+cluster$",
        normalized,
    )
    if not match:
        return NormalizedBurden(source_normalized_phrase=source_phrase), [
            "cluster_label_values_unparsed"
        ]
    count_low, count_high, count_issue = _parse_label_range(match.group("count"))
    period_low, period_high, period_issue = _parse_label_range(
        match.group("period_count") or "1"
    )
    events_low, events_high, events_issue = _parse_label_range(match.group("events"))
    issues = [
        issue
        for issue in (count_issue, period_issue, events_issue)
        if issue is not None
    ]
    return (
        NormalizedBurden(
            cluster_count_low=count_low,
            cluster_count_high=count_high,
            cluster_period_low=period_low,
            cluster_period_high=period_high,
            cluster_period_unit=match.group("period_unit"),  # type: ignore[arg-type]
            events_per_cluster_low=events_low,
            events_per_cluster_high=events_high,
            source_normalized_phrase=source_phrase,
        ),
        issues,
    )

def _rate_burden_from_label(
    label: str,
    *,
    source_phrase: str,
) -> tuple[NormalizedBurden, list[str]]:
    match = re.match(
        r"^(?P<count>multiple|\d+(?:\.\d+)?(?:\s+to\s+\d+(?:\.\d+)?)?)\s+"
        r"per\s+"
        r"(?:(?P<period_count>multiple|\d+(?:\.\d+)?(?:\s+to\s+\d+(?:\.\d+)?)?)\s+)?"
        r"(?P<period_unit>day|week|month|year)$",
        label,
    )
    if not match:
        return NormalizedBurden(source_normalized_phrase=source_phrase), [
            "frequency_label_values_unparsed"
        ]
    count_low, count_high, count_issue = _parse_label_range(match.group("count"))
    period_low, period_high, period_issue = _parse_label_range(
        match.group("period_count") or "1"
    )
    issues = [issue for issue in (count_issue, period_issue) if issue is not None]
    return (
        NormalizedBurden(
            count_low=count_low,
            count_high=count_high,
            vague_count="multiple" if count_issue == "vague_count" else None,
            period_low=period_low,
            period_high=period_high,
            period_unit=match.group("period_unit"),  # type: ignore[arg-type]
            source_normalized_phrase=source_phrase,
        ),
        issues,
    )

def _seizure_free_burden_from_label(
    label: str,
    *,
    source_phrase: str,
) -> tuple[NormalizedBurden, list[str]]:
    match = re.match(
        r"^seizure free for (?P<count>multiple|\d+(?:\.\d+)?) "
        r"(?P<unit>day|week|month|year)$",
        label,
    )
    if not match:
        return NormalizedBurden(source_normalized_phrase=source_phrase), [
            "seizure_free_label_values_unparsed"
        ]
    low, high, issue = _parse_label_range(match.group("count"))
    return (
        NormalizedBurden(
            seizure_free_duration_low=low,
            seizure_free_duration_high=high,
            seizure_free_duration_unit=match.group("unit"),  # type: ignore[arg-type]
            source_normalized_phrase=source_phrase,
        ),
        [issue] if issue else [],
    )

def _parse_label_range(value: str) -> tuple[float | None, float | None, str | None]:
    if value == "multiple":
        return None, None, "vague_count"
    if " to " in value:
        left, right = value.split(" to ", maxsplit=1)
        left_value = float(left)
        right_value = float(right)
        return min(left_value, right_value), max(left_value, right_value), None
    parsed = float(value)
    return parsed, parsed, None

def _has_cluster_label(label: str) -> bool:
    return "cluster" in label

def _has_seizure_free_label(label: str) -> bool:
    return label.startswith("seizure free for ")
