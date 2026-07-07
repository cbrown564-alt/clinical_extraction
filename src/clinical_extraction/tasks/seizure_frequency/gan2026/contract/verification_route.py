"""Verification-route contracts for the Gan 2026 architecture reset."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = "gan2026_verification_route_v0"
ROUTE_POLICY_ID = "gan2026_validation250_verification_route_policy_v0"

VerificationRouteFamily = Literal[
    "seizure_free_conflict",
    "seizure_free_proxy_evidence_overreach",
    "cluster_axis_ambiguity",
    "unresolved_cluster_cadence_with_per_cluster_burden",
    "medication_cadence_ambiguity",
    "cyclic_window_without_event_count",
    "selected_evidence_missing_exact_trace",
    "selected_source_id_invalid",
    "denominator_window_mismatch",
    "conditional_only_trigger",
    "relative_only_trend",
    "mixed_window_or_vague_addition",
    "multiple_current_primary_facts",
    "projection_would_change_supported_comparator",
    "rendered_label_supported_but_policy_sensitive",
]


class VerificationRouteDecision(BaseModel):
    """Deterministic route decision before any verifier action is run."""

    model_config = ConfigDict(extra="forbid")

    source_row_index: int
    component_owner: Literal["verification_route"]
    route_policy_id: Literal["gan2026_validation250_verification_route_policy_v0"] = ROUTE_POLICY_ID
    routed: bool
    route_families: list[VerificationRouteFamily] = Field(default_factory=list)
    route_reasons: list[str] = Field(default_factory=list)
    route_evidence: dict[str, object] = Field(default_factory=dict)
    score_context: dict[str, object] = Field(default_factory=dict)
    schema_version: Literal["gan2026_verification_route_v0"] = SCHEMA_VERSION
