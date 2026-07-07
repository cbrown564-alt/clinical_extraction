"""Verification-action contracts for the Gan 2026 architecture reset."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.verification_route import (
    ROUTE_POLICY_ID,
    VerificationRouteFamily,
)

SCHEMA_VERSION = "gan2026_verification_decision_v0"
VERIFICATION_POLICY_ID = "gan2026_validation250_verification_decision_policy_v0"

VerifierAction = Literal["abstain", "human_review", "affirm", "reject"]
VerifierActionBasis = Literal[
    "route_family_policy",
    "proposed_outcome_block",
    "manual_review_required",
]


class VerificationDecision(BaseModel):
    """Deterministic baseline action for a row routed to verification."""

    model_config = ConfigDict(extra="forbid")

    source_row_index: int
    component_owner: Literal["verification_decision"]
    verification_policy_id: Literal["gan2026_validation250_verification_decision_policy_v0"] = (
        VERIFICATION_POLICY_ID
    )
    source_route_policy_id: str = ROUTE_POLICY_ID
    route_families: list[VerificationRouteFamily] = Field(default_factory=list)
    route_reasons: list[str] = Field(default_factory=list)
    action: VerifierAction
    action_reason: str
    action_basis: VerifierActionBasis
    proposed_rendered_label: str | None = None
    final_rendered_label: str | None = None
    score_context: dict[str, object] = Field(default_factory=dict)
    claim_boundary: str
    schema_version: Literal["gan2026_verification_decision_v0"] = SCHEMA_VERSION
