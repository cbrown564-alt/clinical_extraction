"""Constants and layer definitions for component-ablation replay."""

from __future__ import annotations

from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation.loader import (
    load_component_off_definitions,
    load_full200_component_off_definitions,
    load_full200_specs,
    load_layer_definitions,
    load_replay_specs,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation.types import (
    ComponentImpactReplaySpec,
    ComponentOffDefinition,
    LayerDefinition,
)

DEFAULT_GENERATED_ON = "2026-06-26"
CLAIM_BOUNDARY = "dev140 replay-only aggregate component-impact ladder"
PROVENANCE_POLICY = "format_only_projection_separated_from_semantic_add_drop_replace"
COMPONENT_OFF_CLAIM_BOUNDARY = (
    "dev140 replay-only one-component-off aggregate component-impact config"
)
COMPONENT_OFF_STOP_RULE = (
    "config-only pre-readout contract; no model calls, row-level failure inspection, "
    "or post-run tuning authorized"
)
COMPONENT_OFF_READOUT_CLAIM_BOUNDARY = (
    "dev140 replay-only one-component-off aggregate component-impact readout; "
    "separate from reliability scorecard"
)
COMPONENT_OFF_READOUT_STOP_RULE = (
    "aggregate readout only; no model calls, row-level failure inspection, "
    "or post-run tuning authorized"
)
FULL200_COMPONENT_OFF_CLAIM_BOUNDARY = (
    "full-200 aggregate-only component-impact replay under the frozen "
    "2026-06-26 predeclaration; separate from reliability scorecard evidence"
)
FULL200_COMPONENT_OFF_STOP_RULE = (
    "report null, negative, and positive aggregate deltas as final component-impact "
    "evidence; no model calls, row-level full-200 inspection, or tuning authorized"
)
FULL200_ROW_INSPECTION_BOUNDARY = "aggregate_only_no_full200_or_holdout_row_level_inspection"
FULL200_COMPONENT_OFF_PREDECLARATION = Path(
    "docs/experiments/exectv2/reliability/"
    "exectv2_component_off_full200_predeclaration_2026-06-26.md"
)
DEFAULT_COMPONENT_OFF_JSON = Path("experiments/exectv2_component_off_replay_dev140_20260626.json")
DEFAULT_COMPONENT_OFF_JSONL = Path("experiments/exectv2_component_off_replay_dev140_20260626.jsonl")
DEFAULT_COMPONENT_OFF_MD = Path("experiments/exectv2_component_off_replay_dev140_20260626.md")
DEFAULT_FULL200_COMPONENT_OFF_JSON = Path(
    "experiments/exectv2_component_off_replay_full200_20260626.json"
)
DEFAULT_FULL200_COMPONENT_OFF_JSONL = Path(
    "experiments/exectv2_component_off_replay_full200_20260626.jsonl"
)
DEFAULT_FULL200_COMPONENT_OFF_MD = Path(
    "experiments/exectv2_component_off_replay_full200_20260626.md"
)


LAYER_DEFINITIONS: tuple[LayerDefinition, ...] = load_layer_definitions()
COMPONENT_OFF_DEFINITIONS: tuple[ComponentOffDefinition, ...] = load_component_off_definitions()
FULL200_COMPONENT_OFF_DEFINITIONS: tuple[ComponentOffDefinition, ...] = (
    load_full200_component_off_definitions()
)


DEFAULT_REPLAY_SPECS: tuple[ComponentImpactReplaySpec, ...] = load_replay_specs()
DEFAULT_FULL200_COMPONENT_OFF_REPLAY_SPECS: tuple[ComponentImpactReplaySpec, ...] = (
    load_full200_specs()
)


REQUIRED_COMPONENT_OFF_CONFIG_FIELDS = (
    "artifact_kind",
    "ablation_id",
    "baseline_run_id",
    "component_off_run_id",
    "split",
    "row_count",
    "scorer_view",
    "scorer_version",
    "component_id",
    "component_type",
    "component_portability_category",
    "prediction_bearing_status",
    "baseline_surface",
    "component_off_surface",
    "baseline_aggregate_score",
    "component_off_aggregate_score",
    "overall_delta",
    "family_component_contribution_deltas",
    "validity_rates",
    "row_inspection_policy",
    "allow_model_calls",
    "allow_post_run_tuning",
    "claim_boundary",
    "stop_rule",
)
