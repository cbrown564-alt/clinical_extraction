"""One-component-off replay config and readout builders."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.frontend_review import REPO_ROOT
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation.definitions import (
    COMPONENT_OFF_CLAIM_BOUNDARY,
    COMPONENT_OFF_DEFINITIONS,
    COMPONENT_OFF_READOUT_CLAIM_BOUNDARY,
    COMPONENT_OFF_READOUT_STOP_RULE,
    COMPONENT_OFF_STOP_RULE,
    DEFAULT_FULL200_COMPONENT_OFF_REPLAY_SPECS,
    DEFAULT_GENERATED_ON,
    FULL200_COMPONENT_OFF_CLAIM_BOUNDARY,
    FULL200_COMPONENT_OFF_DEFINITIONS,
    FULL200_COMPONENT_OFF_PREDECLARATION,
    FULL200_COMPONENT_OFF_STOP_RULE,
    FULL200_ROW_INSPECTION_BOUNDARY,
    REQUIRED_COMPONENT_OFF_CONFIG_FIELDS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation.layers import (
    delta,
    has_declared_surface,
    load_summary,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation.types import (
    ComponentImpactReplaySpec,
    ComponentOffDefinition,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.target_indicator_report import (
    TARGET_INDICATORS,
)


def build_component_off_replay_configs(
    payload: dict[str, Any] | None = None,
    *,
    definitions: tuple[ComponentOffDefinition, ...] = COMPONENT_OFF_DEFINITIONS,
    claim_boundary: str = COMPONENT_OFF_CLAIM_BOUNDARY,
    stop_rule: str = COMPONENT_OFF_STOP_RULE,
) -> list[dict[str, Any]]:
    """Build named one-component-off replay configs from saved dev140 surfaces."""

    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation_replay import (
        build_component_ablation_payload,
    )

    source_payload = payload or build_component_ablation_payload()
    configs = [
        component_off_replay_config(
            architecture,
            definition,
            claim_boundary=claim_boundary,
            stop_rule=stop_rule,
        )
        for architecture in source_payload["architectures"]
        for definition in definitions
    ]
    validate_component_off_replay_configs(configs)
    return configs


def build_component_off_readout_payload(
    payload: dict[str, Any] | None = None,
    *,
    generated_on: str = DEFAULT_GENERATED_ON,
    ladder_json: Path = Path("experiments/exectv2_component_ablation_replay_dev140_20260624.json"),
) -> dict[str, Any]:
    """Build the aggregate one-component-off readout from saved dev140 surfaces."""

    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation_replay import (
        build_component_ablation_payload,
    )

    source_payload = payload or build_component_ablation_payload(
        generated_on=generated_on,
    )
    ablations = build_component_off_replay_configs(source_payload)
    component_summaries = [
        component_off_summary(component_id, ablations)
        for component_id in ordered_component_ids(ablations)
    ]
    return {
        "artifact_kind": "exectv2_component_off_readout_set",
        "dataset": "exectv2",
        "generated_on": generated_on,
        "split": "dev140",
        "row_count": 140,
        "scorer_view": "clinical_headline",
        "scorer_version": "exectv2_component_ablation_replay_v20260626",
        "row_inspection_policy": "aggregate_only",
        "allow_model_calls": False,
        "allow_post_run_tuning": False,
        "claim_boundary": COMPONENT_OFF_READOUT_CLAIM_BOUNDARY,
        "stop_rule": COMPONENT_OFF_READOUT_STOP_RULE,
        "ladder_json": ladder_json.as_posix(),
        "ablations": ablations,
        "component_summaries": component_summaries,
    }


def build_full200_component_off_readout_payload(
    specs: tuple[ComponentImpactReplaySpec, ...] = DEFAULT_FULL200_COMPONENT_OFF_REPLAY_SPECS,
    *,
    generated_on: str = DEFAULT_GENERATED_ON,
    code_hash: str = "not_recorded",
    worktree_state: str = "not_recorded",
    predeclaration_path: Path = FULL200_COMPONENT_OFF_PREDECLARATION,
) -> dict[str, Any]:
    """Build the frozen full-200 aggregate component-off readout.

    This reads only summary JSON artifacts and excludes row-level full-200 JSONL
    inspection by construction.
    """

    preflight_rows = [full200_preflight(spec, FULL200_COMPONENT_OFF_DEFINITIONS) for spec in specs]
    eligible_specs = [
        spec
        for spec, preflight in zip(specs, preflight_rows, strict=True)
        if preflight["status"] == "pass"
    ]
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation_replay import (
        build_component_ablation_payload,
    )

    source_payload = build_component_ablation_payload(
        tuple(eligible_specs),
        generated_on=generated_on,
        claim_boundary=FULL200_COMPONENT_OFF_CLAIM_BOUNDARY,
        include_telemetry=True,
    )
    ablations = build_component_off_replay_configs(
        source_payload,
        definitions=FULL200_COMPONENT_OFF_DEFINITIONS,
        claim_boundary=FULL200_COMPONENT_OFF_CLAIM_BOUNDARY,
        stop_rule=FULL200_COMPONENT_OFF_STOP_RULE,
    )
    component_summaries = [
        component_off_summary(component_id, ablations)
        for component_id in ordered_component_ids(ablations)
    ]
    return {
        "artifact_kind": "exectv2_component_off_full200_readout_set",
        "dataset": "exectv2",
        "generated_on": generated_on,
        "split": "full200",
        "row_count": 200,
        "scorer_view": "clinical_headline",
        "scorer_version": "exectv2_component_ablation_replay_v20260626",
        "primary_surface": "clinical_headline",
        "predeclaration_path": predeclaration_path.as_posix(),
        "code_hash": code_hash,
        "worktree_state": worktree_state,
        "row_inspection_policy": "aggregate_only",
        "row_inspection_boundary": FULL200_ROW_INSPECTION_BOUNDARY,
        "allow_model_calls": False,
        "allow_post_run_tuning": False,
        "claim_boundary": FULL200_COMPONENT_OFF_CLAIM_BOUNDARY,
        "stop_rule": FULL200_COMPONENT_OFF_STOP_RULE,
        "stop_rule_outcome": full200_stop_rule_outcome(ablations),
        "selected_components": [
            {
                "component_id": definition.component_id,
                "component_type": definition.component_type,
                "component_portability_category": (definition.component_portability_category),
                "prediction_bearing_status": definition.prediction_bearing_status,
                "baseline_surface": definition.baseline_surface,
                "component_off_surface": definition.component_off_surface,
            }
            for definition in FULL200_COMPONENT_OFF_DEFINITIONS
        ],
        "preflight": preflight_rows,
        "source_artifacts": [
            artifact
            for architecture in source_payload["architectures"]
            for artifact in architecture["source_artifacts"]
        ],
        "ablations": ablations,
        "component_summaries": component_summaries,
    }


def validate_component_off_replay_configs(configs: list[dict[str, Any]]) -> None:
    """Fail closed when a Component Impact replay config omits contract fields."""

    for index, config in enumerate(configs):
        for field in REQUIRED_COMPONENT_OFF_CONFIG_FIELDS:
            if field not in config:
                raise ValueError(f"component-off config {index} missing {field}")
        validity_rates = config["validity_rates"]
        if not isinstance(validity_rates, dict):
            raise ValueError(f"component-off config {index} validity_rates must be a mapping")
        for field in ("schema_validity", "evidence_validity"):
            if field not in validity_rates:
                raise ValueError(f"component-off config {index} missing validity_rates.{field}")
        if config["row_inspection_policy"] != "aggregate_only":
            raise ValueError(f"component-off config {index} must be aggregate_only")
        if config["allow_model_calls"] is not False:
            raise ValueError(f"component-off config {index} must disallow model calls")
        if config["allow_post_run_tuning"] is not False:
            raise ValueError(f"component-off config {index} must disallow post-run tuning")


def ordered_component_ids(ablations: list[dict[str, Any]]) -> list[str]:
    seen: list[str] = []
    for ablation in ablations:
        component_id = str(ablation["component_id"])
        if component_id not in seen:
            seen.append(component_id)
    return seen


def component_off_summary(
    component_id: str,
    ablations: list[dict[str, Any]],
) -> dict[str, Any]:
    rows = [row for row in ablations if row["component_id"] == component_id]
    if not rows:
        raise ValueError(f"missing component-off rows for {component_id}")
    first = rows[0]
    return {
        "component_id": component_id,
        "component_type": first["component_type"],
        "prediction_bearing_status": first["prediction_bearing_status"],
        "claim_use": component_claim_use(component_id, rows),
        "rows": [
            {
                "baseline_run_id": row["baseline_run_id"],
                "overall_component_contribution_delta": row["overall_component_contribution_delta"],
                "family_component_contribution_deltas": row["family_component_contribution_deltas"],
            }
            for row in rows
        ],
    }


def component_claim_use(
    component_id: str,
    rows: list[dict[str, Any]],
) -> str:
    overall_deltas = [float(row["overall_component_contribution_delta"]) for row in rows]
    if all(delta == 0.0 for delta in overall_deltas):
        if component_id == "evidence_validation":
            return (
                "On these single-lane holistic dev140 runs the evidence guard is "
                "structurally inert: producers only emit verbatim-grounded mentions, "
                "so removing validation leaves the clinical_headline score unchanged. "
                "Use this as a grounding guard check, not as proof that evidence "
                "validation is globally unnecessary."
            )
        return (
            f"Removing `{component_id}` left the dev140 clinical_headline score "
            "unchanged across all four saved architectures on this replay surface."
        )

    max_delta = max(overall_deltas)
    max_row = next(
        row for row in rows if float(row["overall_component_contribution_delta"]) == max_delta
    )
    family_deltas = max_row["family_component_contribution_deltas"]
    top_family = max(
        family_deltas,
        key=lambda family: abs(float(family_deltas[family])),
    )
    family_delta = float(family_deltas[top_family])

    if component_id == "standard_dictionary":
        return (
            "Dictionary normalization contributes benchmark-format recovery on dev140, "
            f"most visibly on `{max_row['baseline_run_id']}` "
            f"(overall +{max_delta:.4f}, mainly {top_family} +{family_delta:.4f}). "
            "Report as conditional dictionary impact on the declared scorer, not as "
            "proof that dictionaries are globally required."
        )
    if component_id == "residual_semantic_lens":
        return (
            "Residual semantic recovery is prediction-bearing on dev140: removing the "
            f"lens lowers clinical_headline by up to +{max_delta:.4f} on "
            f"`{max_row['baseline_run_id']}` with the largest family effect on "
            f"{top_family} (+{family_delta:.4f}). This is component-impact evidence "
            "for semantic add/drop/replace layers, not a reliability-scorecard claim."
        )
    if component_id == "headline_projection":
        return (
            "Headline projection is a deterministic format layer on dev140: removing "
            f"it lowers clinical_headline by up to +{max_delta:.4f} on "
            f"`{max_row['baseline_run_id']}`, concentrated in {top_family} "
            f"(+{family_delta:.4f}). Treat this as projection/format contribution "
            "separate from semantic fact changes."
        )
    return (
        f"Removing `{component_id}` changes the dev140 clinical_headline score by up "
        f"to +{max_delta:.4f} on `{max_row['baseline_run_id']}`."
    )


def component_off_replay_config(
    architecture: dict[str, Any],
    definition: ComponentOffDefinition,
    *,
    claim_boundary: str,
    stop_rule: str,
) -> dict[str, Any]:
    layers = {str(layer["layer_id"]): layer for layer in architecture["layers"]}
    if definition.baseline_surface not in layers or definition.component_off_surface not in layers:
        raise ValueError(f"{architecture['run_id']} lacks surfaces for {definition.component_id}")
    baseline = layers[definition.baseline_surface]
    component_off = layers[definition.component_off_surface]
    baseline_score = baseline["scores"]
    off_score = component_off["scores"]
    overall_delta = delta(
        off_score["overall"]["f1"],
        baseline_score["overall"]["f1"],
    )
    component_delta = delta(
        baseline_score["overall"]["f1"],
        off_score["overall"]["f1"],
    )
    family_component_contribution_deltas = {
        family: delta(
            baseline_score["families"][family]["f1"],
            off_score["families"][family]["f1"],
        )
        for family in TARGET_INDICATORS
    }
    family_component_off_deltas = {
        family: delta(
            off_score["families"][family]["f1"],
            baseline_score["families"][family]["f1"],
        )
        for family in TARGET_INDICATORS
    }
    return {
        "artifact_kind": "exectv2_component_off_replay_config",
        "dataset": "exectv2",
        "ablation_id": (f"{architecture['run_id']}__without_{definition.component_id}"),
        "baseline_run_id": architecture["run_id"],
        "component_off_run_id": (f"{architecture['run_id']}__without_{definition.component_id}"),
        "split": architecture["split"],
        "row_count": architecture["row_count"],
        "scorer_view": definition.scorer_view,
        "scorer_version": definition.scorer_version,
        "component_id": definition.component_id,
        "component_boundary": definition.component_boundary,
        "component_type": definition.component_type,
        "component_portability_category": definition.component_portability_category,
        "prediction_bearing_status": definition.prediction_bearing_status,
        "baseline_surface": definition.baseline_surface,
        "component_off_surface": definition.component_off_surface,
        "source_artifacts": architecture["source_artifacts"],
        "baseline_aggregate_score": baseline_score,
        "component_off_aggregate_score": off_score,
        "overall_delta": overall_delta,
        "overall_component_contribution_delta": component_delta,
        "family_component_contribution_deltas": family_component_contribution_deltas,
        "family_component_off_deltas": family_component_off_deltas,
        "validity_rates": architecture.get(
            "validity_rates",
            {
                "schema_validity": "not_recorded_in_source_summary",
                "evidence_validity": "not_recorded_in_source_summary",
            },
        ),
        "operational_counts": architecture.get(
            "operational_counts",
            {
                "call_failures": "not_recorded_in_source_summary",
                "parse_failures": "not_recorded_in_source_summary",
                "abstentions": "not_recorded_in_source_summary",
                "missing_outputs": "not_recorded_in_source_summary",
            },
        ),
        "deterministic_action_counts": architecture.get(
            "deterministic_action_counts",
            {},
        ),
        "row_inspection_policy": "aggregate_only",
        "allow_model_calls": False,
        "allow_post_run_tuning": False,
        "claim_boundary": claim_boundary,
        "stop_rule": stop_rule,
    }


def full200_preflight(
    spec: ComponentImpactReplaySpec,
    definitions: tuple[ComponentOffDefinition, ...],
) -> dict[str, Any]:
    summary_path = REPO_ROOT / spec.source_summary_path
    jsonl_path = REPO_ROOT / spec.source_jsonl_path
    row: dict[str, Any] = {
        "run_id": spec.run_id,
        "source_summary_path": spec.source_summary_path.as_posix(),
        "source_jsonl_path": spec.source_jsonl_path.as_posix(),
        "status": "pass",
        "split": "missing",
        "row_count": 0,
        "surface_status": "missing",
        "telemetry_status": "missing",
        "model_calls_disabled": True,
        "row_inspection_boundary": FULL200_ROW_INSPECTION_BOUNDARY,
        "issues": [],
    }
    if not summary_path.exists():
        row["status"] = "preflight_null"
        row["issues"].append("missing_summary_json")
        return row
    if not jsonl_path.exists():
        row["status"] = "preflight_null"
        row["issues"].append("missing_source_jsonl")
    summary = load_summary(spec.source_summary_path)
    row["split"] = summary.get("split", "missing")
    row["row_count"] = int(summary.get("row_count", 0) or 0)
    if row["split"] != "full200":
        row["status"] = "preflight_null"
        row["issues"].append("split_not_full200")
    if row["row_count"] != 200:
        row["status"] = "preflight_null"
        row["issues"].append("row_count_not_200")
    missing_surfaces = []
    for definition in definitions:
        for surface in (definition.baseline_surface, definition.component_off_surface):
            if not has_declared_surface(summary, surface):
                missing_surfaces.append(surface)
    if missing_surfaces:
        row["status"] = "preflight_null"
        row["issues"].append("missing_surfaces:" + ",".join(sorted(set(missing_surfaces))))
    else:
        row["surface_status"] = "pass"
    lane_diagnostics = summary.get("lane_diagnostics", {})
    telemetry_fields = {
        "call_failures",
        "parse_schema_failures",
        "evidence_invalid_dropped",
        "exact_evidence_rate",
    }
    telemetry_ok = bool(lane_diagnostics) and all(
        isinstance(stats, dict) and telemetry_fields.issubset(stats)
        for stats in lane_diagnostics.values()
    )
    if telemetry_ok:
        row["telemetry_status"] = "pass"
    else:
        row["status"] = "preflight_null"
        row["issues"].append("missing_lane_diagnostics")
    return row


def full200_stop_rule_outcome(ablations: list[dict[str, Any]]) -> str:
    if any(float(row["overall_component_contribution_delta"]) <= 0.0 for row in ablations):
        return "non_positive_delta_observed_stop_no_tuning"
    return "all_selected_component_deltas_positive_limited_claim"


def yaml_lines(key: str, value: Any, *, indent: int = 0) -> list[str]:
    prefix = " " * indent
    if isinstance(value, dict):
        lines = [f"{prefix}{key}:"]
        for child_key, child_value in value.items():
            lines.extend(yaml_lines(str(child_key), child_value, indent=indent + 2))
        return lines
    if isinstance(value, list):
        lines = [f"{prefix}{key}:"]
        for item in value:
            if isinstance(item, dict):
                lines.append(f"{prefix}  -")
                for child_key, child_value in item.items():
                    lines.extend(yaml_lines(str(child_key), child_value, indent=indent + 4))
            else:
                lines.append(f"{prefix}  - {yaml_scalar(item)}")
        return lines
    return [f"{prefix}{key}: {yaml_scalar(value)}"]


def yaml_scalar(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    if isinstance(value, int | float):
        return str(value)
    text = str(value)
    if text == "" or any(char in text for char in ":#[]{}&,*?|-<>=!%@`"):
        return json.dumps(text)
    return text
