"""Constants and layer definitions for component-ablation replay."""

from __future__ import annotations

from pathlib import Path

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


LAYER_DEFINITIONS: tuple[LayerDefinition, ...] = (
    LayerDefinition(
        layer_id="raw_lane_candidates",
        label="Raw lane candidates",
        component_type="llm_producer",
        score_source="score_ladder",
        surface_key="raw_lane_score",
        interpretation="Prediction-bearing producer outputs before downstream cleanup.",
    ),
    LayerDefinition(
        layer_id="source_scored",
        label="Source-scored mentions",
        component_type="llm_producer",
        score_source="materialized_surfaces",
        surface_key="source_scored",
        interpretation=(
            "Scored source mentions before evidence/dictionary/projection layers. "
            "Inert on these single-lane holistic runs: scoring attaches confidence "
            "but adds or drops no mention, so the score is unchanged."
        ),
        inert=True,
    ),
    LayerDefinition(
        layer_id="evidence_valid",
        label="Evidence-valid mentions",
        component_type="evidence_validation",
        score_source="materialized_surfaces",
        surface_key="evidence_valid",
        interpretation=(
            "Mentions after exact-evidence validation. Inert on these runs: the "
            "producers only emit verbatim-grounded mentions, so nothing fails the "
            "guard and the surface is identical to source-scored."
        ),
        inert=True,
    ),
    LayerDefinition(
        layer_id="dictionary_normalized",
        label="Dictionary normalized",
        component_type="dictionary",
        score_source="materialized_surfaces",
        surface_key="dictionary_normalized",
        interpretation="Standard dictionaries and format-normalization layers applied.",
    ),
    LayerDefinition(
        layer_id="residual_semantic_added",
        label="Residual semantic additions",
        component_type="semantic_lens",
        score_source="materialized_surfaces",
        surface_key="residual_benchmark_added",
        interpretation=(
            "Residual recovery and semantic add/drop/replace layers applied. This "
            "is the full assembled mention set fed to headline projection."
        ),
    ),
    LayerDefinition(
        layer_id="headline_projection",
        label="Headline projection",
        component_type="deterministic_projection",
        score_source="score_ladder",
        surface_key="headline_target",
        interpretation="Clinical headline / projection surface used for final reporting.",
    ),
)


COMPONENT_OFF_DEFINITIONS: tuple[ComponentOffDefinition, ...] = (
    ComponentOffDefinition(
        component_id="evidence_validation",
        component_boundary="evidence_valid",
        component_type="evidence_validation",
        component_portability_category="general",
        prediction_bearing_status="no",
        baseline_surface="evidence_valid",
        component_off_surface="source_scored",
    ),
    ComponentOffDefinition(
        component_id="standard_dictionary",
        component_boundary="dictionary_normalized",
        component_type="dictionary",
        component_portability_category="clinical_epilepsy",
        prediction_bearing_status="conditional",
        baseline_surface="dictionary_normalized",
        component_off_surface="evidence_valid",
    ),
    ComponentOffDefinition(
        component_id="residual_semantic_lens",
        component_boundary="residual_semantic_added",
        component_type="semantic_lens",
        component_portability_category="benchmark_format",
        prediction_bearing_status="yes",
        baseline_surface="residual_semantic_added",
        component_off_surface="dictionary_normalized",
    ),
    ComponentOffDefinition(
        component_id="headline_projection",
        component_boundary="headline_projection",
        component_type="deterministic_projection",
        component_portability_category="benchmark_format",
        prediction_bearing_status="no",
        baseline_surface="headline_projection",
        component_off_surface="residual_semantic_added",
    ),
)


FULL200_COMPONENT_OFF_DEFINITIONS: tuple[ComponentOffDefinition, ...] = tuple(
    definition
    for definition in COMPONENT_OFF_DEFINITIONS
    if definition.component_id
    in {"standard_dictionary", "residual_semantic_lens", "headline_projection"}
)


from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation.loader import (
    load_full200_specs,
    load_replay_specs,
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
