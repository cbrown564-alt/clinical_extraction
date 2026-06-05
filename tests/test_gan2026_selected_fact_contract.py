import pytest
from pydantic import ValidationError

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.selected_fact import (
    SelectedClinicalFact,
    referenced_candidate_ids,
)


def test_selected_clinical_fact_accepts_source_near_candidate_selection() -> None:
    selection = SelectedClinicalFact(
        source_row_index=101,
        component_owner="candidate_set_selector",
        source_artifacts=["gan2026_validation250_candidate_set_v2_high_recall"],
        selection_status="selected",
        selection_basis="direct_candidate_selection",
        clinical_fact_kind="frequency_rate",
        selected_candidate_ids=["det:101:1"],
        rejected_candidate_ids=["llm:101:2"],
        primary_evidence=[{"text": "two seizures per month", "start_char": 20, "end_char": 42}],
        source_ids=["note:101:span:20-42"],
        temporality="current",
        certainty="certain",
        rationale="The selected candidate is the current explicit rate.",
    )

    assert selection.schema_version == "gan2026_selected_clinical_fact_v0"
    assert selection.clinical_or_policy == "clinical"
    assert referenced_candidate_ids(selection) == {"det:101:1", "llm:101:2"}


def test_unknown_by_absence_does_not_select_a_candidate() -> None:
    selection = SelectedClinicalFact(
        source_row_index=102,
        component_owner="candidate_set_selector",
        source_artifacts=["gan2026_validation250_candidate_set_v2_high_recall"],
        selection_status="no_reliable_candidate",
        selection_basis="absence_of_evidence",
        clinical_fact_kind="unknown_frequency",
        unknown_basis="absence_of_usable_frequency_evidence",
        source_reliability_flags=["no_current_frequency_candidate"],
        rationale="The row has no usable current frequency evidence.",
    )

    assert selection.selected_candidate_ids == []
    assert selection.primary_evidence == []
    assert selection.unknown_basis == "absence_of_usable_frequency_evidence"


def test_selected_unknown_candidate_must_state_unknown_basis() -> None:
    payload = {
        "source_row_index": 103,
        "component_owner": "candidate_set_selector",
        "source_artifacts": ["candidate_set"],
        "selection_status": "selected",
        "selection_basis": "direct_candidate_selection",
        "clinical_fact_kind": "unknown_frequency",
        "selected_candidate_ids": ["llm:103:1"],
        "primary_evidence": [{"text": "seizure frequency is unclear"}],
    }

    with pytest.raises(ValidationError, match="selected unknown_frequency facts require"):
        SelectedClinicalFact.model_validate(payload)


def test_selection_rejects_overlapping_selected_and_rejected_ids() -> None:
    payload = {
        "source_row_index": 104,
        "component_owner": "candidate_set_selector",
        "source_artifacts": ["candidate_set"],
        "selection_status": "selected",
        "selection_basis": "direct_candidate_selection",
        "clinical_fact_kind": "seizure_free",
        "selected_candidate_ids": ["det:104:1"],
        "rejected_candidate_ids": ["det:104:1"],
        "primary_evidence": [{"text": "seizure free for six months"}],
    }

    with pytest.raises(ValidationError, match="must not overlap"):
        SelectedClinicalFact.model_validate(payload)


def test_ambiguity_requires_flags_or_multiple_supporting_candidates() -> None:
    payload = {
        "source_row_index": 105,
        "component_owner": "candidate_set_selector",
        "source_artifacts": ["candidate_set"],
        "selection_status": "ambiguous",
        "selection_basis": "ambiguity_between_candidates",
        "supporting_candidate_ids": ["det:105:1"],
    }

    with pytest.raises(ValidationError, match="ambiguity_flags"):
        SelectedClinicalFact.model_validate(payload)
