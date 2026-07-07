"""Layered ExECTv2 component-impact artifacts.

The Component Impact surface needs a layered view, not a single ablation row:
each selected architecture should show how the score changes as the replay moves
from raw model/lane candidates through validation, dictionaries, semantic
additions, assembly, and headline projection. This module materializes that
aggregate-only ladder from saved finding-assembly summary JSON files. It makes
no model calls and emits no row-level failures.
"""
# ruff: noqa: F401 — re-exports submodule symbols accessed via this module's namespace.

from __future__ import annotations

from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.frontend_review import REPO_ROOT
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation.artifacts import (
    build_architecture_layer_ladder,
    cached_component_ablation_json,
    cached_component_ablation_payload,
    write_component_ablation_artifacts,
    write_component_off_readout_artifacts,
    write_full200_component_off_readout_artifacts,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation.component_off import (
    build_component_off_readout_payload,
    build_component_off_replay_configs,
    build_full200_component_off_readout_payload,
    validate_component_off_replay_configs,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation.definitions import (
    CLAIM_BOUNDARY,
    COMPONENT_OFF_CLAIM_BOUNDARY,
    COMPONENT_OFF_DEFINITIONS,
    COMPONENT_OFF_READOUT_CLAIM_BOUNDARY,
    COMPONENT_OFF_READOUT_STOP_RULE,
    COMPONENT_OFF_STOP_RULE,
    DEFAULT_COMPONENT_OFF_JSON,
    DEFAULT_COMPONENT_OFF_JSONL,
    DEFAULT_COMPONENT_OFF_MD,
    DEFAULT_FULL200_COMPONENT_OFF_JSON,
    DEFAULT_FULL200_COMPONENT_OFF_JSONL,
    DEFAULT_FULL200_COMPONENT_OFF_MD,
    DEFAULT_FULL200_COMPONENT_OFF_REPLAY_SPECS,
    DEFAULT_GENERATED_ON,
    DEFAULT_REPLAY_SPECS,
    FULL200_COMPONENT_OFF_CLAIM_BOUNDARY,
    FULL200_COMPONENT_OFF_DEFINITIONS,
    FULL200_COMPONENT_OFF_PREDECLARATION,
    FULL200_COMPONENT_OFF_STOP_RULE,
    FULL200_ROW_INSPECTION_BOUNDARY,
    LAYER_DEFINITIONS,
    PROVENANCE_POLICY,
    REQUIRED_COMPONENT_OFF_CONFIG_FIELDS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation.render import (
    render_component_ablation_markdown,
    render_component_off_readout_markdown,
    render_component_off_replay_config,
    render_full200_component_off_readout_markdown,
    render_replay_config,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation.types import (
    ComponentImpactReplaySpec,
    ComponentOffDefinition,
    LayerDefinition,
)


def build_component_ablation_payload(
    specs: tuple[ComponentImpactReplaySpec, ...] = DEFAULT_REPLAY_SPECS,
    *,
    generated_on: str = DEFAULT_GENERATED_ON,
    claim_boundary: str = CLAIM_BOUNDARY,
    include_telemetry: bool = False,
) -> dict[str, object]:
    architectures = [
        build_architecture_layer_ladder(
            spec,
            generated_on=generated_on,
            claim_boundary=claim_boundary,
            include_telemetry=include_telemetry,
        )
        for spec in specs
    ]
    impact_rows = [
        impact for architecture in architectures for impact in architecture["layer_impacts"]
    ]
    return {
        "artifact_kind": "exectv2_component_ablation_set",
        "dataset": "exectv2",
        "generated_on": generated_on,
        "row_inspection_policy": "aggregate_only",
        "allow_model_calls": False,
        "allow_post_run_tuning": False,
        "claim_boundary": claim_boundary,
        "provenance_policy": PROVENANCE_POLICY,
        "layers": [layer.__dict__ for layer in LAYER_DEFINITIONS],
        "architectures": architectures,
        "ablations": impact_rows,
    }
