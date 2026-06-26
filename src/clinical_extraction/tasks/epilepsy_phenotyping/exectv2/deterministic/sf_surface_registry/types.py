"""Core types for the canonical SF surface registry."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rule_metadata import (
    Portability,
    RuleGroup,
)


class SurfacePhase(StrEnum):
    EXTRACT = "extract"
    REWRITE = "rewrite"
    NOISE = "noise"
    RESIDUAL_ADD = "residual_add"
    PROJECT = "project"
    EVIDENCE_REPAIR = "evidence_repair"
    SUPPRESS = "suppress"


class SurfaceRule(BaseModel):
    rule_id: str
    phases: frozenset[SurfacePhase]
    group: RuleGroup | None = None
    portability: Portability | None = None
    quarantine_family: str | None = None
    pattern_id: str | None = None
    source_stack: str | None = None

    model_config = {"frozen": True}
