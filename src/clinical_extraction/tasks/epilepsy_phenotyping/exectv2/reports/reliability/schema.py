"""Pydantic validation for the cross-model reliability run catalog."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ReliabilityRunRecord(BaseModel):
    """One reliability scorecard run entry in catalog.yaml."""

    model_config = ConfigDict(extra="forbid")

    candidate: str = Field(min_length=1)
    model_label: str = Field(min_length=1)
    rows_path: str = Field(min_length=1)
    summary_path: str | None = None
    surface_id: str = Field(default="rich_schema_reliability", min_length=1)
    role: str = ""
    claim_boundary: str = ""


class ReliabilityCatalog(BaseModel):
    """Top-level catalog for retained rich-schema reliability runs."""

    model_config = ConfigDict(extra="forbid")

    rich_schema_runs: tuple[ReliabilityRunRecord, ...]
