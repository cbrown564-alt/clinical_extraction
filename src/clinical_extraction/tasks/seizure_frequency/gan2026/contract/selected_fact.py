"""Minimal selector contract for Gan 2026 candidate decisions."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

SCHEMA_VERSION = "gan2026_selected_candidate_decision_v0"

SelectionMode = Literal[
    "single_candidate",
    "related_candidate_group",
    "no_reliable_candidate",
    "ambiguous",
    "conflict",
]


class SelectedCandidateDecision(BaseModel):
    """Selector output: candidate ids to carry forward, or a defer mode."""

    model_config = ConfigDict(extra="forbid")

    source_row_index: int
    component_owner: str
    selected_candidate_ids: list[str] = Field(default_factory=list)
    selection_mode: SelectionMode
    rationale: str = ""
    schema_version: Literal["gan2026_selected_candidate_decision_v0"] = SCHEMA_VERSION

    @model_validator(mode="after")
    def validate_selection_mode(self) -> SelectedCandidateDecision:
        selected_count = len(self.selected_candidate_ids)
        if self.selection_mode == "single_candidate" and selected_count != 1:
            raise ValueError("single_candidate requires exactly one selected_candidate_id")
        if self.selection_mode == "related_candidate_group" and selected_count < 2:
            raise ValueError(
                "related_candidate_group requires two or more selected_candidate_ids"
            )
        if self.selection_mode in {
            "no_reliable_candidate",
            "ambiguous",
            "conflict",
        } and selected_count:
            raise ValueError(f"{self.selection_mode} must not select candidate ids")
        if selected_count != len(set(self.selected_candidate_ids)):
            raise ValueError("selected_candidate_ids must be unique")
        return self


def referenced_candidate_ids(selection: SelectedCandidateDecision) -> set[str]:
    """Return every candidate id named by a selector decision."""

    return set(selection.selected_candidate_ids)
