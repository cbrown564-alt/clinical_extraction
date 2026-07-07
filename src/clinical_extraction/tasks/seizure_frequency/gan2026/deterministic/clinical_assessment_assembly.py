"""Deterministic clinical-assessment assembly from model-owned drafts."""
# ruff: noqa: F401 — some imported helpers are re-exported and accessed via module attribute
# (e.g. ``_assembly._frequency_burden_from_multi_month_bucket_phrase`` in assessment_probe).

from __future__ import annotations

from pydantic import ValidationError

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.assessment_draft import (
    AssessmentDraft,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.clinical_assessment import (
    ClinicalAssessment,
    SeizureFreeInstrumentation,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.assessment.burden_normalization import (
    _frequency_burden_from_multi_month_bucket_phrase,
    _is_unrenderable_seizure_free_burden,
    normalize_assessment_burden,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.assessment.common import (
    DISABLED_SWITCH_ISSUE_PREFIX,
    NORMALIZATION_POLICY_ID,
    _disabled_switch_issue,
    _normalize_phrase_for_parse,
    _validate_candidate_references,
    _validation_error_messages,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.assessment.draft_repair import (
    _apply_deterministic_assessment_overrides,
    _apply_deterministic_assessment_repairs,
    _repair_candidate_role_ids,
    _repair_multi_primary_nonadditive_policy,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.assessment.seizure_free import (
    _instrument_seizure_free_duration,
)

# Backward-compatible re-exports for tests and internal callers that reach into
# private helpers via ``clinical_assessment_assembly``.

__all__ = [
    "DISABLED_SWITCH_ISSUE_PREFIX",
    "NORMALIZATION_POLICY_ID",
    "assemble_clinical_assessment",
    "normalize_assessment_burden",
]


def assemble_clinical_assessment(
    draft: AssessmentDraft | None,
    *,
    candidate_set: CandidateSet,
    component_owner: str,
    disabled_ablation_switches: set[str] | frozenset[str] | None = None,
) -> tuple[ClinicalAssessment | None, list[str]]:
    """Assemble a clinical assessment from model-owned fields."""

    if draft is None:
        return None, ["assessment_draft_missing"]
    disabled_switches = frozenset(disabled_ablation_switches or ())

    draft, role_repair_issues = _repair_candidate_role_ids(draft)
    draft, override_issues = _apply_deterministic_assessment_overrides(
        draft,
        candidate_set=candidate_set,
    )
    draft, repair_issues = _apply_deterministic_assessment_repairs(
        draft,
        candidate_set=candidate_set,
        disabled_ablation_switches=disabled_switches,
    )
    draft, post_repair_role_issues = _repair_candidate_role_ids(draft)
    errors = _validate_candidate_references(draft, candidate_set)
    normalized_burden, normalization_issues = normalize_assessment_burden(
        draft,
        candidate_set=candidate_set,
        disabled_ablation_switches=disabled_switches,
    )
    seizure_free_instrumentation: SeizureFreeInstrumentation | None = None
    if (
        draft.assessment_kind == "seizure_free"
        and "normalize_seizure_free_duration_date_instrumentation" not in disabled_switches
    ):
        (
            normalized_burden,
            seizure_free_instrumentation,
            instrumentation_issues,
        ) = _instrument_seizure_free_duration(
            draft,
            candidate_set=candidate_set,
            normalized_burden=normalized_burden,
            disabled_ablation_switches=disabled_switches,
        )
        normalization_issues.extend(instrumentation_issues)
    elif (
        draft.assessment_kind == "seizure_free"
        and "normalize_seizure_free_duration_date_instrumentation" in disabled_switches
        and _is_unrenderable_seizure_free_burden(normalized_burden)
    ):
        normalization_issues.append(
            _disabled_switch_issue("normalize_seizure_free_duration_date_instrumentation")
        )
    normalization_issues = [
        *role_repair_issues,
        *override_issues,
        *repair_issues,
        *post_repair_role_issues,
        *normalization_issues,
    ]
    try:
        assessment = ClinicalAssessment(
            source_row_index=candidate_set.source_row_index,
            component_owner=component_owner,
            assessment_kind=draft.assessment_kind,
            primary_candidate_ids=draft.primary_candidate_ids,
            supporting_candidate_ids=draft.supporting_candidate_ids,
            rejected_candidate_ids=draft.rejected_candidate_ids,
            aggregation_policy=draft.aggregation_policy,  # type: ignore[arg-type]
            normalized_burden=normalized_burden,
            seizure_free_instrumentation=seizure_free_instrumentation,
            normalization_policy_id=NORMALIZATION_POLICY_ID,
            normalization_issues=normalization_issues,
            assessment_summary=draft.assessment_summary,
            uncertainty_flags=draft.uncertainty_flags,
        )
    except ValidationError as exc:
        errors.extend(_validation_error_messages(exc))
        return None, errors
    if errors:
        return None, errors
    return assessment, errors
