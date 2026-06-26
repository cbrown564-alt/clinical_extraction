"""Runtime types for component-ablation replay."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class ComponentImpactReplaySpec:
    run_id: str
    label: str
    source_summary_path: Path
    source_jsonl_path: Path
    model: str
    decision: str
    architecture_family: str
    split: str = "dev140"
    row_count: int = 140


@dataclass(frozen=True)
class LayerDefinition:
    layer_id: str
    label: str
    component_type: str
    score_source: str
    surface_key: str
    interpretation: str
    # Tag for structurally inert stages: on these single-lane holistic
    # architectures the surface never changes the score (every prediction passes
    # straight through). The stage is kept in the aggregate ladder for provenance
    # but the frontend hides it rather than render a permanently ~0 row.
    inert: bool = False


@dataclass(frozen=True)
class ComponentOffDefinition:
    component_id: str
    component_boundary: str
    component_type: str
    component_portability_category: str
    prediction_bearing_status: str
    baseline_surface: str
    component_off_surface: str
    scorer_view: str = "clinical_headline"
    scorer_version: str = "exectv2_component_ablation_replay_v20260626"

