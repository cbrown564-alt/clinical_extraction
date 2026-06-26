"""Pydantic validation for the component-ablation replay catalog."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ReplaySpecRecord(BaseModel):
    """One replay experiment entry in catalog.yaml."""

    model_config = ConfigDict(extra="forbid")

    run_id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    source_summary_path: str = Field(min_length=1)
    source_jsonl_path: str = Field(min_length=1)
    model: str = Field(min_length=1)
    decision: str = Field(min_length=1)
    architecture_family: str = Field(min_length=1)
    split: str = Field(default="dev140", min_length=1)
    row_count: int = Field(default=140, ge=1)


class ReplayCatalog(BaseModel):
    """Top-level catalog with dev140 and full200 replay spec sections."""

    model_config = ConfigDict(extra="forbid")

    dev140: tuple[ReplaySpecRecord, ...]
    full200: tuple[ReplaySpecRecord, ...]
