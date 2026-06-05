import pytest
from pydantic import ValidationError

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.clinical_assessment import (
    ClinicalAssessment,
    NormalizedBurden,
    referenced_candidate_ids,
)


def test_clinical_assessment_accepts_primary_supporting_and_rejected_roles() -> None:
    assessment = ClinicalAssessment(
        source_row_index=10,
        component_owner="test",
        assessment_kind="frequency_rate",
        primary_candidate_ids=["a"],
        supporting_candidate_ids=["b"],
        rejected_candidate_ids=["c"],
        aggregation_policy="primary_with_context",
        normalized_burden=NormalizedBurden(
            count_low=12,
            count_high=12,
            period_low=1,
            period_high=1,
            period_unit="month",
            source_normalized_phrase="12 seizures per month",
        ),
        assessment_summary="Monthly burden is primary; clustering is context.",
    )

    assert referenced_candidate_ids(assessment) == {"a", "b", "c"}
    assert assessment.schema_version == "gan2026_clinical_assessment_v0"


def test_clinical_assessment_rejects_overlapping_candidate_roles() -> None:
    with pytest.raises(ValidationError, match="overlap"):
        ClinicalAssessment(
            source_row_index=10,
            component_owner="test",
            assessment_kind="frequency_rate",
            primary_candidate_ids=["a"],
            supporting_candidate_ids=["a"],
            aggregation_policy="primary_with_context",
            normalized_burden=NormalizedBurden(source_normalized_phrase="12 per month"),
        )


def test_clinical_assessment_requires_primary_for_concrete_burden() -> None:
    with pytest.raises(ValidationError, match="requires primary_candidate_ids"):
        ClinicalAssessment(
            source_row_index=10,
            component_owner="test",
            assessment_kind="seizure_free",
            primary_candidate_ids=[],
            aggregation_policy="seizure_free_state",
            normalized_burden=NormalizedBurden(source_normalized_phrase="seizure-free"),
        )
