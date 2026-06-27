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


class LayerDefinitionRecord(BaseModel):
    """One layer in the component-impact ladder."""

    model_config = ConfigDict(extra="forbid")

    layer_id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    component_type: str = Field(min_length=1)
    score_source: str = Field(min_length=1)
    surface_key: str = Field(min_length=1)
    interpretation: str = Field(min_length=1)
    inert: bool = False


class ComponentOffDefinitionRecord(BaseModel):
    """One one-component-off ablation definition."""

    model_config = ConfigDict(extra="forbid")

    component_id: str = Field(min_length=1)
    component_boundary: str = Field(min_length=1)
    component_type: str = Field(min_length=1)
    component_portability_category: str = Field(min_length=1)
    prediction_bearing_status: str = Field(min_length=1)
    baseline_surface: str = Field(min_length=1)
    component_off_surface: str = Field(min_length=1)
    scorer_view: str = Field(default="clinical_headline", min_length=1)
    scorer_version: str = Field(
        default="exectv2_component_ablation_replay_v20260626",
        min_length=1,
    )


class DefinitionsCatalog(BaseModel):
    """Layer ladder and component-off definitions."""

    model_config = ConfigDict(extra="forbid")

    layers: tuple[LayerDefinitionRecord, ...]
    component_off: tuple[ComponentOffDefinitionRecord, ...]
    full200_component_ids: tuple[str, ...]
