import pytest
from pydantic import ValidationError

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.selected_fact import (
    SelectedCandidateDecision,
    referenced_candidate_ids,
)


def test_selected_candidate_decision_accepts_single_candidate() -> None:
    selection = SelectedCandidateDecision(
        source_row_index=101,
        component_owner="llm_candidate_set_selector",
        selected_candidate_ids=["det:101:1"],
        selection_mode="single_candidate",
        rationale="The candidate is the current explicit rate.",
    )

    assert selection.schema_version == "gan2026_selected_candidate_decision_v0"
    assert referenced_candidate_ids(selection) == {"det:101:1"}


def test_selected_candidate_decision_accepts_related_candidate_group() -> None:
    selection = SelectedCandidateDecision(
        source_row_index=102,
        component_owner="llm_candidate_set_selector",
        selected_candidate_ids=["det:102:1", "llm:102:2"],
        selection_mode="related_candidate_group",
        rationale="Both candidates describe the same current short-window burden.",
    )

    assert selection.selected_candidate_ids == ["det:102:1", "llm:102:2"]


def test_single_candidate_requires_exactly_one_id() -> None:
    payload = {
        "source_row_index": 103,
        "component_owner": "llm_candidate_set_selector",
        "selected_candidate_ids": ["det:103:1", "llm:103:2"],
        "selection_mode": "single_candidate",
    }

    with pytest.raises(ValidationError, match="exactly one"):
        SelectedCandidateDecision.model_validate(payload)


def test_related_candidate_group_requires_multiple_ids() -> None:
    payload = {
        "source_row_index": 104,
        "component_owner": "llm_candidate_set_selector",
        "selected_candidate_ids": ["det:104:1"],
        "selection_mode": "related_candidate_group",
    }

    with pytest.raises(ValidationError, match="two or more"):
        SelectedCandidateDecision.model_validate(payload)


def test_defer_modes_do_not_select_ids() -> None:
    for mode in ("no_reliable_candidate", "ambiguous", "conflict"):
        payload = {
            "source_row_index": 105,
            "component_owner": "llm_candidate_set_selector",
            "selected_candidate_ids": ["det:105:1"],
            "selection_mode": mode,
        }

        with pytest.raises(ValidationError, match="must not select"):
            SelectedCandidateDecision.model_validate(payload)


def test_selected_candidate_ids_must_be_unique() -> None:
    payload = {
        "source_row_index": 106,
        "component_owner": "llm_candidate_set_selector",
        "selected_candidate_ids": ["det:106:1", "det:106:1"],
        "selection_mode": "related_candidate_group",
    }

    with pytest.raises(ValidationError, match="must be unique"):
        SelectedCandidateDecision.model_validate(payload)
