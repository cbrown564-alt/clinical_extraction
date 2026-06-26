"""Deterministic draft repairs and assessment overrides."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.assessment_draft import (
    AssessmentDraft,
    AssessmentDraftBurden,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
    ExtractedCandidate,
    candidate_source_phrase,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.clinical_assessment import (
    AggregationPolicy,
    NormalizedBurden,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.assessment.burden_normalization import (
    _cluster_burden,
    _frequency_burden,
    _frequency_burden_specificity_score,
    _is_renderable_cluster_burden,
    _is_renderable_frequency_burden,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.assessment.common import (
    _candidate_lookup,
    _candidates_by_ids,
    _cluster_phrases,
    _dedupe,
    _disabled_switch_issue,
    _normalization_source_phrase,
)

def _repair_candidate_role_ids(draft: AssessmentDraft) -> tuple[AssessmentDraft, list[str]]:
    """Remove recoverable duplicate and overlapping role ids from a model draft."""

    repairs: list[str] = []
    primary_ids, primary_issues = _dedupe_role_ids(
        draft.primary_candidate_ids,
        role_name="primary_candidate_ids",
    )
    supporting_ids, supporting_issues = _dedupe_role_ids(
        draft.supporting_candidate_ids,
        role_name="supporting_candidate_ids",
    )
    rejected_ids, rejected_issues = _dedupe_role_ids(
        draft.rejected_candidate_ids,
        role_name="rejected_candidate_ids",
    )
    repairs.extend([*primary_issues, *supporting_issues, *rejected_issues])

    primary = set(primary_ids)
    supporting_before = list(supporting_ids)
    supporting_ids = [
        candidate_id for candidate_id in supporting_ids if candidate_id not in primary
    ]
    for candidate_id in supporting_before:
        if candidate_id in primary:
            repairs.append(
                "candidate_role_overlap_removed:"
                f"supporting_candidate_ids:{candidate_id}:kept_primary_candidate_ids"
            )

    kept = {*primary_ids, *supporting_ids}
    rejected_before = list(rejected_ids)
    rejected_ids = [candidate_id for candidate_id in rejected_ids if candidate_id not in kept]
    for candidate_id in rejected_before:
        if candidate_id in primary:
            repairs.append(
                "candidate_role_overlap_removed:"
                f"rejected_candidate_ids:{candidate_id}:kept_primary_candidate_ids"
            )
        elif candidate_id in supporting_ids:
            repairs.append(
                "candidate_role_overlap_removed:"
                f"rejected_candidate_ids:{candidate_id}:kept_supporting_candidate_ids"
            )

    if not repairs:
        return draft, []
    return (
        draft.model_copy(
            update={
                "primary_candidate_ids": primary_ids,
                "supporting_candidate_ids": supporting_ids,
                "rejected_candidate_ids": rejected_ids,
            }
        ),
        repairs,
    )

def _dedupe_role_ids(
    candidate_ids: Sequence[str],
    *,
    role_name: str,
) -> tuple[list[str], list[str]]:
    seen: set[str] = set()
    deduped: list[str] = []
    repairs: list[str] = []
    for candidate_id in candidate_ids:
        if candidate_id in seen:
            repairs.append(f"candidate_role_duplicate_removed:{role_name}:{candidate_id}")
            continue
        seen.add(candidate_id)
        deduped.append(candidate_id)
    return deduped, repairs

def _apply_deterministic_assessment_repairs(
    draft: AssessmentDraft,
    *,
    candidate_set: CandidateSet,
    disabled_ablation_switches: frozenset[str] = frozenset(),
) -> tuple[AssessmentDraft, list[str]]:
    """Repair recoverable model policy/role inconsistencies."""

    repairs: list[str] = []
    repaired = draft
    candidate_by_id = {
        candidate.candidate_id: candidate for candidate in candidate_set.candidates
    }
    if repaired.aggregation_policy is None:
        inferred = _infer_missing_aggregation_policy(repaired, candidate_by_id)
        repaired = repaired.model_copy(update={"aggregation_policy": inferred})
        repairs.append(f"aggregation_policy_defaulted:{inferred}")

    repaired, cluster_repairs = _repair_cluster_axis_without_cluster_primary(
        repaired,
        candidate_by_id=candidate_by_id,
    )
    repairs.extend(cluster_repairs)

    repaired, single_policy_repairs = _repair_single_primary_policy(
        repaired,
        candidate_by_id=candidate_by_id,
    )
    repairs.extend(single_policy_repairs)

    repaired, multi_primary_repairs = _repair_multi_primary_nonadditive_policy(
        repaired,
        candidate_by_id=candidate_by_id,
        disabled_ablation_switches=disabled_ablation_switches,
    )
    repairs.extend(multi_primary_repairs)

    repaired, historical_repairs = _repair_historical_primary(
        repaired,
        candidate_by_id=candidate_by_id,
    )
    repairs.extend(historical_repairs)
    return repaired, repairs

def _infer_missing_aggregation_policy(
    draft: AssessmentDraft,
    candidate_by_id: Mapping[str, ExtractedCandidate],
) -> AggregationPolicy:
    primary_candidates = _candidate_lookup(candidate_by_id, draft.primary_candidate_ids)
    primary_count = len(draft.primary_candidate_ids)
    if draft.assessment_kind == "seizure_free":
        return "seizure_free_state" if primary_count else "unknown_due_to_absence"
    if draft.assessment_kind == "unknown_frequency":
        return "unknown_due_to_absence" if primary_count == 0 else "unknown_due_to_ambiguity"
    if primary_count == 0:
        return "no_reference_boundary"
    if primary_count == 1:
        return "single_fact"
    if _all_candidate_kind(primary_candidates, "frequency_rate"):
        return "additive_same_window"
    if _all_candidate_kind(primary_candidates, "cluster_frequency"):
        return "cluster_axis"
    return "primary_with_context"

def _repair_single_primary_policy(
    draft: AssessmentDraft,
    *,
    candidate_by_id: Mapping[str, ExtractedCandidate],
) -> tuple[AssessmentDraft, list[str]]:
    if len(draft.primary_candidate_ids) != 1:
        return draft, []
    primary = candidate_by_id.get(draft.primary_candidate_ids[0])
    if draft.aggregation_policy == "additive_same_window":
        return (
            draft.model_copy(update={"aggregation_policy": "single_fact"}),
            ["single_primary_additive_same_window_to_single_fact"],
        )
    if draft.aggregation_policy != "cluster_axis":
        return draft, []
    if primary is not None and primary.candidate_kind == "cluster_frequency":
        return (
            draft.model_copy(update={"aggregation_policy": "single_fact"}),
            ["single_primary_cluster_axis_to_single_fact"],
        )
    repaired_policy: AggregationPolicy = (
        "primary_with_context" if draft.supporting_candidate_ids else "single_fact"
    )
    return (
        draft.model_copy(update={"aggregation_policy": repaired_policy}),
        [f"single_primary_cluster_axis_to_{repaired_policy}"],
    )

def _repair_cluster_axis_without_cluster_primary(
    draft: AssessmentDraft,
    *,
    candidate_by_id: Mapping[str, ExtractedCandidate],
) -> tuple[AssessmentDraft, list[str]]:
    if draft.aggregation_policy != "cluster_axis":
        return draft, []
    primary_candidates = _candidate_lookup(candidate_by_id, draft.primary_candidate_ids)
    if any(candidate.candidate_kind == "cluster_frequency" for candidate in primary_candidates):
        return draft, []
    supporting_candidates = _candidate_lookup(
        candidate_by_id, draft.supporting_candidate_ids
    )
    promotable = [
        candidate
        for candidate in supporting_candidates
        if candidate.candidate_kind == "cluster_frequency"
        and _phrase_mentions_cluster_burden(candidate)
    ]
    if promotable:
        promoted = promotable[0].candidate_id
        primary_ids = [*draft.primary_candidate_ids, promoted]
        supporting_ids = [
            candidate_id
            for candidate_id in draft.supporting_candidate_ids
            if candidate_id != promoted
        ]
        return (
            draft.model_copy(
                update={
                    "primary_candidate_ids": primary_ids,
                    "supporting_candidate_ids": supporting_ids,
                }
            ),
            ["cluster_axis_supporting_cluster_promoted_to_primary"],
        )
    return (
        draft.model_copy(update={"aggregation_policy": "primary_with_context"}),
        ["cluster_axis_without_cluster_primary_to_primary_with_context"],
    )

def _repair_multi_primary_nonadditive_policy(
    draft: AssessmentDraft,
    *,
    candidate_by_id: Mapping[str, ExtractedCandidate],
    disabled_ablation_switches: frozenset[str] = frozenset(),
) -> tuple[AssessmentDraft, list[str]]:
    if len(draft.primary_candidate_ids) <= 1:
        return draft, []
    if draft.aggregation_policy in {
        "additive_same_window",
        "cluster_axis",
        "seizure_free_state",
        "unknown_due_to_ambiguity",
    }:
        return draft, []
    primary_candidates = _candidate_lookup(candidate_by_id, draft.primary_candidate_ids)
    if (
        draft.assessment_kind == "frequency_rate"
        and _all_candidate_kind(primary_candidates, "frequency_rate")
        and _same_frequency_window(primary_candidates)
    ):
        return (
            draft.model_copy(update={"aggregation_policy": "additive_same_window"}),
            ["multi_primary_nonadditive_to_additive_same_window"],
        )
    best_primary_id = _best_single_primary_candidate_id(
        primary_candidates,
        disabled_ablation_switches=disabled_ablation_switches,
    )
    if best_primary_id is None:
        return draft, ["multi_primary_nonadditive_unrepaired"]
    supporting_ids = [
        *draft.supporting_candidate_ids,
        *[
            candidate_id
            for candidate_id in draft.primary_candidate_ids
            if candidate_id != best_primary_id
        ],
    ]
    selected_primary = candidate_by_id.get(best_primary_id)
    selected_primary_phrase = (
        candidate_source_phrase(selected_primary) or selected_primary.evidence_span.text
        if selected_primary is not None
        else draft.normalized_burden.source_normalized_phrase
    )
    if selected_primary is not None and _is_major_recent_relapse_candidate(
        selected_primary
    ):
        repair_issues = ["major_recent_relapse_over_background_frequency"]
    elif "project_major_recent_relapse_over_background_frequency" in disabled_ablation_switches:
        repair_issues = [
            _disabled_switch_issue(
                "project_major_recent_relapse_over_background_frequency"
            )
        ]
    else:
        repair_issues = ["multi_primary_nonadditive_demoted_to_supporting"]
    return (
        draft.model_copy(
            update={
                "primary_candidate_ids": [best_primary_id],
                "supporting_candidate_ids": _dedupe(supporting_ids),
                "normalized_burden": draft.normalized_burden.model_copy(
                    update={"source_normalized_phrase": selected_primary_phrase}
                ),
            }
        ),
        repair_issues,
    )

def _repair_historical_primary(
    draft: AssessmentDraft,
    *,
    candidate_by_id: Mapping[str, ExtractedCandidate],
) -> tuple[AssessmentDraft, list[str]]:
    primary_candidates = _candidate_lookup(candidate_by_id, draft.primary_candidate_ids)
    if not any(candidate.temporality == "historical" for candidate in primary_candidates):
        return draft, []
    candidate_pool = [
        candidate
        for candidate in candidate_by_id.values()
        if candidate.assertion_status == "asserted"
        and candidate.candidate_kind in {"frequency_rate", "cluster_frequency", "seizure_free"}
        and candidate.temporality in {"current", "recent"}
    ]
    if not candidate_pool:
        return draft, []
    replacement = max(candidate_pool, key=_current_candidate_priority)
    historical_primary_ids = [
        candidate.candidate_id
        for candidate in primary_candidates
        if candidate.temporality == "historical"
    ]
    primary_ids = [
        replacement.candidate_id,
        *[
            candidate_id
            for candidate_id in draft.primary_candidate_ids
            if candidate_id not in historical_primary_ids
            and candidate_id != replacement.candidate_id
        ],
    ]
    supporting_ids = [
        *draft.supporting_candidate_ids,
        *historical_primary_ids,
    ]
    supporting_ids = [
        candidate_id
        for candidate_id in _dedupe(supporting_ids)
        if candidate_id != replacement.candidate_id
    ]
    return (
        draft.model_copy(
            update={
                "primary_candidate_ids": _dedupe(primary_ids),
                "supporting_candidate_ids": supporting_ids,
                "aggregation_policy": (
                    "primary_with_context" if supporting_ids else draft.aggregation_policy
                ),
            }
        ),
        [f"historical_primary_replaced_with_current:{replacement.candidate_id}"],
    )

def _all_candidate_kind(
    candidates: Sequence[ExtractedCandidate],
    candidate_kind: str,
) -> bool:
    return bool(candidates) and all(
        candidate.candidate_kind == candidate_kind for candidate in candidates
    )

def _same_frequency_window(candidates: Sequence[ExtractedCandidate]) -> bool:
    parsed = [
        _frequency_burden(candidate_source_phrase(candidate) or candidate.evidence_span.text)
        for candidate in candidates
    ]
    burdens = [burden for burden, issues in parsed if not issues]
    if len(burdens) != len(candidates) or not burdens:
        return False
    first = burdens[0]
    return all(
        burden.period_low == first.period_low
        and burden.period_high == first.period_high
        and burden.period_unit == first.period_unit
        for burden in burdens
    )

def _best_single_primary_candidate_id(
    candidates: Sequence[ExtractedCandidate],
    *,
    disabled_ablation_switches: frozenset[str] = frozenset(),
) -> str | None:
    if not candidates:
        return None
    return max(
        candidates,
        key=lambda candidate: _single_primary_priority(
            candidate,
            disabled_ablation_switches=disabled_ablation_switches,
        ),
    ).candidate_id

def _single_primary_priority(
    candidate: ExtractedCandidate,
    *,
    disabled_ablation_switches: frozenset[str] = frozenset(),
) -> tuple[int, int, int, int]:
    phrase = candidate_source_phrase(candidate) or candidate.evidence_span.text
    major_relapse_enabled = (
        "project_major_recent_relapse_over_background_frequency"
        not in disabled_ablation_switches
    )
    return (
        1 if major_relapse_enabled and _is_major_recent_relapse_candidate(candidate) else 0,
        1 if candidate.temporality in {"current", "recent"} else 0,
        1 if candidate.candidate_kind == "frequency_rate" else 0,
        1 if candidate.source_type == "deterministic_candidate" else 0,
        len(phrase),
    )

def _current_candidate_priority(candidate: ExtractedCandidate) -> tuple[int, int, int]:
    phrase = candidate_source_phrase(candidate) or candidate.evidence_span.text
    return (
        1 if candidate.temporality == "current" else 0,
        1 if candidate.candidate_kind == "frequency_rate" else 0,
        len(phrase),
    )

def _is_major_recent_relapse_candidate(candidate: ExtractedCandidate) -> bool:
    phrase = " ".join(
        value.lower()
        for value in [
            candidate_source_phrase(candidate) or "",
            candidate.evidence_span.text,
        ]
        if value
    )
    has_recent_day_cue = any(token in phrase for token in ("yesterday", "today"))
    has_major_semiology = any(
        token in phrase for token in ("tonic-clonic", "convulsive", "generalised", "generalized")
    )
    return (
        candidate.candidate_kind == "frequency_rate"
        and candidate.temporality in {"current", "recent"}
        and has_recent_day_cue
        and has_major_semiology
    )

def _phrase_mentions_cluster_burden(candidate: ExtractedCandidate) -> bool:
    phrase = " ".join(
        value.lower()
        for value in [
            candidate_source_phrase(candidate) or "",
            candidate.evidence_span.text,
        ]
        if value
    )
    return any(marker in phrase for marker in ("cluster", "clusters", "run", "runs"))

def _apply_deterministic_assessment_overrides(
    draft: AssessmentDraft,
    *,
    candidate_set: CandidateSet,
) -> tuple[AssessmentDraft, list[str]]:
    if draft.assessment_kind != "cluster_frequency":
        return draft, []
    primary_candidates = _candidates_by_ids(candidate_set, draft.primary_candidate_ids)
    source_phrase = _normalization_source_phrase(draft, primary_candidates)
    existing_cluster_burden, existing_cluster_issues = _cluster_burden(
        primary_candidates,
        source_phrase=source_phrase,
    )
    if _is_renderable_cluster_burden(existing_cluster_burden) and not existing_cluster_issues:
        return draft, []
    override = _best_frequency_override_candidate(draft, candidate_set=candidate_set)
    if override is None:
        return draft, []
    override_candidate_id, burden = override
    adjusted = draft.model_copy(
        update={
            "assessment_kind": "frequency_rate",
            "primary_candidate_ids": [override_candidate_id],
            "supporting_candidate_ids": [
                referenced_candidate_id
                for referenced_candidate_id in [
                    *draft.primary_candidate_ids,
                    *draft.supporting_candidate_ids,
                ]
                if referenced_candidate_id != override_candidate_id
            ],
            "aggregation_policy": "single_fact",
            "normalized_burden": AssessmentDraftBurden(
                source_normalized_phrase=burden.source_normalized_phrase
            ),
        }
    )
    return adjusted, ["cluster_assessment_promoted_to_frequency_rate"]

def _best_frequency_override_candidate(
    draft: AssessmentDraft,
    *,
    candidate_set: CandidateSet,
) -> tuple[str, NormalizedBurden] | None:
    by_id = {candidate.candidate_id: candidate for candidate in candidate_set.candidates}
    referenced_ids = [*draft.primary_candidate_ids, *draft.supporting_candidate_ids]
    parsed: list[tuple[tuple[int, int, int], str, NormalizedBurden]] = []
    for position, candidate_id in enumerate(referenced_ids):
        candidate = by_id.get(candidate_id)
        if candidate is None:
            continue
        if _is_medication_cadence_candidate(candidate):
            continue
        parsed_burdens = [
            _frequency_burden(phrase)
            for phrase in _frequency_override_phrases(candidate)
        ]
        renderable = [
            burden
            for burden, issues in parsed_burdens
            if _is_renderable_frequency_burden(burden)
            and not any(
                issue
                for issue in issues
                if issue
                not in {
                    "vague_count",
                    "vague_frequency_with_explicit_time_period",
                }
            )
        ]
        if not renderable:
            continue
        burden = max(renderable, key=_frequency_burden_specificity_score)
        parsed.append(
            (
                _frequency_override_score(candidate, burden, position),
                candidate_id,
                burden,
            )
        )
    if not parsed:
        return None
    _, candidate_id, burden = max(parsed, key=lambda item: item[0])
    return candidate_id, burden

def _frequency_override_phrases(candidate: ExtractedCandidate) -> list[str]:
    phrases = _cluster_phrases([candidate]) if candidate.cluster_details else []
    phrases.append(candidate_source_phrase(candidate) or candidate.evidence_span.text)
    phrases.append(candidate.evidence_span.text)
    return [phrase for phrase in _dedupe(phrases) if phrase]

def _frequency_override_score(
    candidate: ExtractedCandidate,
    burden: NormalizedBurden,
    position: int,
) -> tuple[int, int, int]:
    return (
        1 if candidate.candidate_kind == "frequency_rate" else 0,
        1 if burden.count_low is not None and burden.count_high is not None else 0,
        -position,
    )

def _is_medication_cadence_candidate(candidate: ExtractedCandidate) -> bool:
    text = " ".join(
        phrase.lower()
        for phrase in [
            candidate_source_phrase(candidate) or "",
            candidate.evidence_span.text,
        ]
        if phrase
    )
    return any(
        marker in text
        for marker in (
            "as needed",
            "as-needed",
            "clobazam",
            "rescue medication",
            "patient-led use",
            "treated with",
        )
    )
