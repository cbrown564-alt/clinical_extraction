"""Selector-output contract for source-near Gan 2026 clinical facts."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateKind,
    Certainty,
    EvidenceSpan,
    Temporality,
)

SCHEMA_VERSION = "gan2026_selected_clinical_fact_v0"

SelectionStatus = Literal[
    "selected",
    "ambiguous",
    "conflict",
    "no_reliable_candidate",
    "human_review",
]
SelectionBasis = Literal[
    "direct_candidate_selection",
    "candidate_combination",
    "ambiguity_between_candidates",
    "conflict_between_candidates",
    "absence_of_evidence",
    "verifier_referral",
]
UnknownBasis = Literal[
    "extracted_unknown_candidate",
    "absence_of_usable_frequency_evidence",
    "uncertain_only",
    "conflicting_candidates",
    "verifier_required",
    "not_applicable",
]


class SelectedClinicalFact(BaseModel):
    """Clinical selector output before normalization, projection, or scoring."""

    model_config = ConfigDict(extra="forbid")

    source_row_index: int
    component_owner: str
    source_artifacts: list[str]
    selection_status: SelectionStatus
    selection_basis: SelectionBasis
    clinical_fact_kind: CandidateKind | None = None
    selected_candidate_ids: list[str] = Field(default_factory=list)
    supporting_candidate_ids: list[str] = Field(default_factory=list)
    rejected_candidate_ids: list[str] = Field(default_factory=list)
    primary_evidence: list[EvidenceSpan] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    temporality: Temporality | Literal["mixed"] | None = None
    certainty: Certainty | Literal["mixed"] | None = None
    unknown_basis: UnknownBasis | None = None
    ambiguity_flags: list[str] = Field(default_factory=list)
    conflict_flags: list[str] = Field(default_factory=list)
    source_reliability_flags: list[str] = Field(default_factory=list)
    selection_issues: list[str] = Field(default_factory=list)
    rationale: str = ""
    clinical_or_policy: Literal["clinical"] = "clinical"
    schema_version: Literal["gan2026_selected_clinical_fact_v0"] = SCHEMA_VERSION

    @model_validator(mode="after")
    def validate_selection_contract(self) -> SelectedClinicalFact:
        selected_ids = set(self.selected_candidate_ids)
        rejected_ids = set(self.rejected_candidate_ids)
        if selected_ids & rejected_ids:
            raise ValueError("selected_candidate_ids and rejected_candidate_ids must not overlap")

        if self.selection_status == "selected":
            self._validate_selected_fact()
        elif self.selection_status == "no_reliable_candidate":
            self._validate_no_reliable_candidate()
        elif self.selection_status == "ambiguous":
            self._validate_structured_abstention("ambiguity_flags")
        elif self.selection_status == "conflict":
            self._validate_structured_abstention("conflict_flags")
        return self

    def _validate_selected_fact(self) -> None:
        if not self.selected_candidate_ids:
            raise ValueError("selected status requires at least one selected_candidate_id")
        if self.clinical_fact_kind is None:
            raise ValueError("selected status requires clinical_fact_kind")
        if not self.primary_evidence:
            raise ValueError("selected status requires primary_evidence")
        if (
            self.clinical_fact_kind != "unknown_frequency"
            and self.unknown_basis not in (None, "not_applicable")
        ):
            raise ValueError(
                "unknown_basis is only allowed for selected unknown_frequency facts"
            )
        if self.clinical_fact_kind == "unknown_frequency" and self.unknown_basis is None:
            raise ValueError(
                "selected unknown_frequency facts require an explicit unknown_basis"
            )

    def _validate_no_reliable_candidate(self) -> None:
        if self.selected_candidate_ids:
            raise ValueError("no_reliable_candidate must not select candidate ids")
        if self.unknown_basis in (None, "not_applicable"):
            raise ValueError("no_reliable_candidate requires a substantive unknown_basis")
        if self.selection_basis not in (
            "absence_of_evidence",
            "ambiguity_between_candidates",
            "conflict_between_candidates",
            "verifier_referral",
        ):
            raise ValueError(
                "no_reliable_candidate requires an abstention-compatible selection_basis"
            )

    def _validate_structured_abstention(self, flag_field: str) -> None:
        if self.selected_candidate_ids:
            raise ValueError(f"{self.selection_status} must not select candidate ids")
        flags = getattr(self, flag_field)
        if not flags and len(self.supporting_candidate_ids) < 2:
            raise ValueError(
                f"{self.selection_status} requires {flag_field} or multiple supporting ids"
            )


def referenced_candidate_ids(selection: SelectedClinicalFact) -> set[str]:
    """Return every candidate id named by a selected fact or abstention."""

    return (
        set(selection.selected_candidate_ids)
        | set(selection.supporting_candidate_ids)
        | set(selection.rejected_candidate_ids)
    )
