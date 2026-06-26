"""Layered ExECTv2 component-impact artifacts.

The Component Impact surface needs a layered view, not a single ablation row:
each selected architecture should show how the score changes as the replay moves
from raw model/lane candidates through validation, dictionaries, semantic
additions, assembly, and headline projection. This module materializes that
aggregate-only ladder from saved finding-assembly summary JSON files. It makes
no model calls and emits no row-level failures.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.frontend_review import REPO_ROOT
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.target_indicator_report import (
    TARGET_INDICATORS,
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
DEFAULT_COMPONENT_OFF_JSON = Path(
    "experiments/exectv2_component_off_replay_dev140_20260626.json"
)
DEFAULT_COMPONENT_OFF_JSONL = Path(
    "experiments/exectv2_component_off_replay_dev140_20260626.jsonl"
)
DEFAULT_COMPONENT_OFF_MD = Path(
    "experiments/exectv2_component_off_replay_dev140_20260626.md"
)


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


DEFAULT_REPLAY_SPECS: tuple[ComponentImpactReplaySpec, ...] = (
    ComponentImpactReplaySpec(
        run_id="exectv2_holistic_finding_assembly_v08_dev140",
        label="v08 dev140 control",
        source_summary_path=Path(
            "experiments/exectv2_holistic_finding_assembly_v08_dev140_20260621.json"
        ),
        source_jsonl_path=Path(
            "experiments/exectv2_holistic_finding_assembly_v08_dev140_20260621.jsonl"
        ),
        model="openai/gpt-4.1-mini",
        decision="control",
        architecture_family="holistic_finding_assembly",
    ),
    ComponentImpactReplaySpec(
        run_id="exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140",
        label="v09 partial hybrid simplification",
        source_summary_path=Path(
            "experiments/_archive/exectv2_richschema_iterations/"
            "exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140_20260621.json"
        ),
        source_jsonl_path=Path(
            "experiments/_archive/exectv2_richschema_iterations/"
            "exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140_20260621.jsonl"
        ),
        model="openai/gpt-4.1-mini",
        decision="simplification",
        architecture_family="partial_hybrid",
    ),
    ComponentImpactReplaySpec(
        run_id="exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140",
        label="DeepSeek v0.9.16 dev140 diagnostic",
        source_summary_path=Path(
            "experiments/_archive/exectv2_richschema_iterations/"
            "exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140_20260622.json"
        ),
        source_jsonl_path=Path(
            "experiments/_archive/exectv2_richschema_iterations/"
            "exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140_20260622.jsonl"
        ),
        model="deepseek/deepseek-chat",
        decision="diagnostic",
        architecture_family="single_gpt_reparse",
    ),
    ComponentImpactReplaySpec(
        run_id="exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140",
        label="Qwen v0.9.22 dev140 diagnostic",
        source_summary_path=Path(
            "experiments/_archive/exectv2_richschema_iterations/"
            "exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140_20260622.json"
        ),
        source_jsonl_path=Path(
            "experiments/_archive/exectv2_richschema_iterations/"
            "exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140_20260622.jsonl"
        ),
        model="ollama_chat/qwen3.6:35b",
        decision="diagnostic",
        architecture_family="single_gpt_reparse",
    ),
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


def build_component_ablation_payload(
    specs: tuple[ComponentImpactReplaySpec, ...] = DEFAULT_REPLAY_SPECS,
    *,
    generated_on: str = DEFAULT_GENERATED_ON,
) -> dict[str, Any]:
    architectures = [
        build_architecture_layer_ladder(spec, generated_on=generated_on)
        for spec in specs
    ]
    impact_rows = [
        impact
        for architecture in architectures
        for impact in architecture["layer_impacts"]
    ]
    return {
        "artifact_kind": "exectv2_component_ablation_set",
        "dataset": "exectv2",
        "generated_on": generated_on,
        "row_inspection_policy": "aggregate_only",
        "allow_model_calls": False,
        "allow_post_run_tuning": False,
        "claim_boundary": CLAIM_BOUNDARY,
        "provenance_policy": PROVENANCE_POLICY,
        "layers": [layer.__dict__ for layer in LAYER_DEFINITIONS],
        "architectures": architectures,
        "ablations": impact_rows,
    }


def build_component_off_replay_configs(
    payload: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Build named one-component-off replay configs from saved dev140 surfaces."""

    source_payload = payload or build_component_ablation_payload()
    configs = [
        _component_off_replay_config(architecture, definition)
        for architecture in source_payload["architectures"]
        for definition in COMPONENT_OFF_DEFINITIONS
    ]
    validate_component_off_replay_configs(configs)
    return configs


def build_component_off_readout_payload(
    payload: dict[str, Any] | None = None,
    *,
    generated_on: str = DEFAULT_GENERATED_ON,
    ladder_json: Path = Path(
        "experiments/exectv2_component_ablation_replay_dev140_20260624.json"
    ),
) -> dict[str, Any]:
    """Build the aggregate one-component-off readout from saved dev140 surfaces."""

    source_payload = payload or build_component_ablation_payload(
        generated_on=generated_on,
    )
    ablations = build_component_off_replay_configs(source_payload)
    component_summaries = [
        _component_off_summary(component_id, ablations)
        for component_id in _ordered_component_ids(ablations)
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


@lru_cache(maxsize=1)
def cached_component_ablation_payload() -> dict[str, Any]:
    return build_component_ablation_payload()


@lru_cache(maxsize=1)
def cached_component_ablation_json() -> str:
    return json.dumps(cached_component_ablation_payload(), ensure_ascii=False)


def build_architecture_layer_ladder(
    spec: ComponentImpactReplaySpec,
    *,
    generated_on: str = DEFAULT_GENERATED_ON,
) -> dict[str, Any]:
    summary = _load_summary(spec.source_summary_path)
    layers = [
        _layer_score(summary, layer)
        for layer in LAYER_DEFINITIONS
        if _has_layer(summary, layer)
    ]
    layer_impacts = _layer_impacts(
        run_id=spec.run_id,
        layers=layers,
        generated_on=generated_on,
    )
    final_layer = layers[-1]
    return {
        "artifact_kind": "exectv2_component_architecture_ladder",
        "dataset": "exectv2",
        "generated_on": generated_on,
        "run_id": spec.run_id,
        "label": spec.label,
        "model": spec.model,
        "decision": spec.decision,
        "architecture_family": spec.architecture_family,
        "split": spec.split,
        "row_count": int(summary.get("row_count", spec.row_count)),
        "final_score": final_layer["scores"],
        "layers": layers,
        "layer_impacts": layer_impacts,
        "source_artifacts": [
            spec.source_summary_path.as_posix(),
            spec.source_jsonl_path.as_posix(),
        ],
        "claim_boundary": CLAIM_BOUNDARY,
        "row_inspection_policy": "aggregate_only",
    }


def write_component_ablation_artifacts(
    specs: tuple[ComponentImpactReplaySpec, ...] = DEFAULT_REPLAY_SPECS,
    *,
    json_path: Path = Path(
        "experiments/exectv2_component_ablation_replay_dev140_20260624.json"
    ),
    jsonl_path: Path = Path(
        "experiments/exectv2_component_ablation_replay_dev140_20260624.jsonl"
    ),
    md_path: Path = Path(
        "experiments/exectv2_component_ablation_replay_dev140_20260624.md"
    ),
    config_dir: Path = Path("configs/exectv2/ablations"),
    frontend_path: Path | None = Path(
        "frontend/public/mock-data/exectv2/component-ablation.json"
    ),
    component_off_json_path: Path = DEFAULT_COMPONENT_OFF_JSON,
    component_off_jsonl_path: Path = DEFAULT_COMPONENT_OFF_JSONL,
    component_off_md_path: Path = DEFAULT_COMPONENT_OFF_MD,
    generated_on: str = DEFAULT_GENERATED_ON,
) -> dict[str, Path]:
    payload = build_component_ablation_payload(specs, generated_on=generated_on)
    resolved = {
        "json": json_path,
        "jsonl": jsonl_path,
        "markdown": md_path,
        "configs": config_dir,
    }
    for path in (json_path, jsonl_path, md_path):
        (REPO_ROOT / path).parent.mkdir(parents=True, exist_ok=True)
    resolved_config_dir = REPO_ROOT / config_dir
    resolved_config_dir.mkdir(parents=True, exist_ok=True)
    for stale_pattern in (
        "exectv2_holistic_finding_assembly_*__layer_*.yaml",
        "exectv2_holistic_finding_assembly_*__without_deterministic_projection.yaml",
        "exectv2_holistic_finding_assembly_*__component_off_*.yaml",
    ):
        for stale_path in resolved_config_dir.glob(stale_pattern):
            stale_path.unlink()

    (REPO_ROOT / json_path).write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (REPO_ROOT / jsonl_path).write_text(
        "\n".join(
            json.dumps(architecture, ensure_ascii=False)
            for architecture in payload["architectures"]
        )
        + "\n",
        encoding="utf-8",
    )
    (REPO_ROOT / md_path).write_text(
        render_component_ablation_markdown(
            payload,
            json_path=json_path,
            jsonl_path=jsonl_path,
        ),
        encoding="utf-8",
    )
    for architecture in payload["architectures"]:
        for impact in architecture["layer_impacts"]:
            config_path = config_dir / (
                f"{architecture['run_id']}__layer_{impact['layer_id']}.yaml"
            )
            (REPO_ROOT / config_path).write_text(
                render_replay_config(architecture, impact, payload_json=json_path),
                encoding="utf-8",
            )
    for config in build_component_off_replay_configs(payload):
        config_path = config_dir / (
            f"{config['baseline_run_id']}__component_off_{config['component_id']}.yaml"
        )
        (REPO_ROOT / config_path).write_text(
            render_component_off_replay_config(config),
            encoding="utf-8",
        )
    if frontend_path is not None:
        (REPO_ROOT / frontend_path).parent.mkdir(parents=True, exist_ok=True)
        (REPO_ROOT / frontend_path).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    resolved.update(
        write_component_off_readout_artifacts(
            payload,
            json_path=component_off_json_path,
            jsonl_path=component_off_jsonl_path,
            md_path=component_off_md_path,
            generated_on=generated_on,
            ladder_json=json_path,
        )
    )
    return resolved


def write_component_off_readout_artifacts(
    payload: dict[str, Any] | None = None,
    *,
    json_path: Path = DEFAULT_COMPONENT_OFF_JSON,
    jsonl_path: Path = DEFAULT_COMPONENT_OFF_JSONL,
    md_path: Path = DEFAULT_COMPONENT_OFF_MD,
    generated_on: str = DEFAULT_GENERATED_ON,
    ladder_json: Path = Path(
        "experiments/exectv2_component_ablation_replay_dev140_20260624.json"
    ),
) -> dict[str, Path]:
    readout = build_component_off_readout_payload(
        payload,
        generated_on=generated_on,
        ladder_json=ladder_json,
    )
    resolved = {
        "component_off_json": json_path,
        "component_off_jsonl": jsonl_path,
        "component_off_markdown": md_path,
    }
    for path in (json_path, jsonl_path, md_path):
        (REPO_ROOT / path).parent.mkdir(parents=True, exist_ok=True)
    (REPO_ROOT / json_path).write_text(
        json.dumps(readout, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (REPO_ROOT / jsonl_path).write_text(
        "\n".join(
            json.dumps(ablation, ensure_ascii=False) for ablation in readout["ablations"]
        )
        + "\n",
        encoding="utf-8",
    )
    (REPO_ROOT / md_path).write_text(
        render_component_off_readout_markdown(
            readout,
            json_path=json_path,
            jsonl_path=jsonl_path,
        ),
        encoding="utf-8",
    )
    return resolved


def render_component_ablation_markdown(
    payload: dict[str, Any],
    *,
    json_path: Path,
    jsonl_path: Path,
) -> str:
    lines = [
        "# ExECTv2 Layered Component Impact Replay",
        "",
        f"- Generated: `{payload['generated_on']}`",
        f"- JSON: `{json_path.as_posix()}`",
        f"- JSONL: `{jsonl_path.as_posix()}`",
        f"- Claim boundary: {payload['claim_boundary']}",
        "- Row inspection policy: `aggregate_only`",
        "- No model calls; replay is computed from saved dev140 summary artifacts.",
        "",
        "## Architecture Summary",
        "",
        (
            "| Architecture | Decision | Final F1 | Raw candidates | Dictionary | "
            "Residual semantic | Headline projection |"
        ),
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for architecture in payload["architectures"]:
        scores = {
            layer["layer_id"]: layer["scores"]["overall"]["f1"]
            for layer in architecture["layers"]
        }
        lines.append(
            f"| `{architecture['run_id']}` | {architecture['decision']} | "
            f"{architecture['final_score']['overall']['f1']:.4f} | "
            f"{scores.get('raw_lane_candidates', 0.0):.4f} | "
            f"{scores.get('dictionary_normalized', 0.0):.4f} | "
            f"{scores.get('residual_semantic_added', 0.0):.4f} | "
            f"{scores.get('headline_projection', 0.0):.4f} |"
        )
    lines.extend(
        [
            "",
            "## Layer Impacts",
            "",
            "| Architecture | Layer | Overall delta | Diagnosis | SF | Rx | Inv |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for impact in payload["ablations"]:
        deltas = impact["family_deltas"]
        lines.append(
            f"| `{impact['run_id']}` | {impact['layer_label']} | "
            f"{impact['overall_delta_from_previous']:+.4f} | "
            f"{deltas['Diagnosis']:+.4f} | "
            f"{deltas['SeizureFrequency']:+.4f} | "
            f"{deltas['Prescription']:+.4f} | "
            f"{deltas['Investigations']:+.4f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation Boundary",
            "",
            (
                "These are layered aggregate replays. A positive delta means the "
                "score increased from the previous saved surface to the current "
                "surface. A zero delta means the layer did not change that score "
                "surface for that architecture."
            ),
            "",
            "No full-200 or holdout-facing row-level inspection is introduced.",
            "",
        ]
    )
    return "\n".join(lines)


def render_replay_config(
    architecture: dict[str, Any],
    impact: dict[str, Any],
    *,
    payload_json: Path,
) -> str:
    return (
        f"candidate: {architecture['run_id']}\n"
        f"split: {architecture['split']}\n"
        "scorer_view: layered_component_impact\n"
        "source_artifacts:\n"
        f"  baseline_summary: {architecture['source_artifacts'][0]}\n"
        f"  baseline_assembly: {architecture['source_artifacts'][1]}\n"
        f"  aggregate_json: {payload_json.as_posix()}\n"
        f"component_boundary: {impact['layer_id']}\n"
        f"component_type: {impact['component_type']}\n"
        f"previous_surface: {impact['previous_layer_id']}\n"
        f"current_surface: {impact['layer_id']}\n"
        "row_inspection_policy: aggregate_only\n"
        "allow_model_calls: false\n"
        "allow_post_run_tuning: false\n"
        f"claim_boundary: {CLAIM_BOUNDARY}\n"
    )


def render_component_off_readout_markdown(
    payload: dict[str, Any],
    *,
    json_path: Path,
    jsonl_path: Path,
) -> str:
    lines = [
        "# ExECTv2 One-Component-Off Aggregate Readout (dev140)",
        "",
        f"- Generated: `{payload['generated_on']}`",
        f"- JSON: `{json_path.as_posix()}`",
        f"- JSONL: `{jsonl_path.as_posix()}`",
        f"- Layer ladder: `{payload['ladder_json']}`",
        f"- Claim boundary: {payload['claim_boundary']}",
        "- Row inspection policy: `aggregate_only`",
        "- No model calls; replay is computed from saved dev140 summary artifacts.",
        "- Reported separately from the reliability scorecard.",
        "",
        "## Aggregate Component-Off Table",
        "",
        (
            "| Architecture | Component | Baseline F1 | Component-off F1 | "
            "Contribution delta | Diagnosis | SF | Rx | Inv |"
        ),
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for ablation in payload["ablations"]:
        baseline_f1 = ablation["baseline_aggregate_score"]["overall"]["f1"]
        off_f1 = ablation["component_off_aggregate_score"]["overall"]["f1"]
        deltas = ablation["family_component_contribution_deltas"]
        lines.append(
            f"| `{ablation['baseline_run_id']}` | {ablation['component_id']} | "
            f"{baseline_f1:.4f} | {off_f1:.4f} | "
            f"{ablation['overall_component_contribution_delta']:+.4f} | "
            f"{deltas['Diagnosis']:+.4f} | "
            f"{deltas['SeizureFrequency']:+.4f} | "
            f"{deltas['Prescription']:+.4f} | "
            f"{deltas['Investigations']:+.4f} |"
        )
    lines.extend(["", "## Component Claim Use", ""])
    for summary in payload["component_summaries"]:
        lines.extend(
            [
                f"### {summary['component_id']}",
                "",
                (
                    f"- Type: `{summary['component_type']}`; "
                    f"prediction-bearing: `{summary['prediction_bearing_status']}`"
                ),
                f"- Claim use: {summary['claim_use']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Interpretation Boundary",
            "",
            (
                "Contribution delta is baseline minus component-off on the declared "
                "`clinical_headline` scorer. A positive delta means removing the "
                "component lowered the score on this split. A zero delta means the "
                "saved surface did not change when the component was removed."
            ),
            "",
            (
                "These rows are component-impact evidence only. They do not prove a "
                "component is unnecessary in general, and they must not be blended "
                "into reliability-scorecard claims."
            ),
            "",
            "No full-200 or holdout-facing row-level inspection is introduced.",
            "",
        ]
    )
    return "\n".join(lines)


def render_component_off_replay_config(config: dict[str, Any]) -> str:
    """Render a deterministic YAML-like config without requiring YAML at runtime."""

    lines: list[str] = []
    for key, value in config.items():
        lines.extend(_yaml_lines(key, value))
    return "\n".join(lines) + "\n"


def _ordered_component_ids(ablations: list[dict[str, Any]]) -> list[str]:
    seen: list[str] = []
    for ablation in ablations:
        component_id = str(ablation["component_id"])
        if component_id not in seen:
            seen.append(component_id)
    return seen


def _component_off_summary(
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
        "claim_use": _component_claim_use(component_id, rows),
        "rows": [
            {
                "baseline_run_id": row["baseline_run_id"],
                "overall_component_contribution_delta": row[
                    "overall_component_contribution_delta"
                ],
                "family_component_contribution_deltas": row[
                    "family_component_contribution_deltas"
                ],
            }
            for row in rows
        ],
    }


def _component_claim_use(
    component_id: str,
    rows: list[dict[str, Any]],
) -> str:
    overall_deltas = [
        float(row["overall_component_contribution_delta"]) for row in rows
    ]
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
        row
        for row in rows
        if float(row["overall_component_contribution_delta"]) == max_delta
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


def _component_off_replay_config(
    architecture: dict[str, Any],
    definition: ComponentOffDefinition,
) -> dict[str, Any]:
    layers = {
        str(layer["layer_id"]): layer
        for layer in architecture["layers"]
    }
    if (
        definition.baseline_surface not in layers
        or definition.component_off_surface not in layers
    ):
        raise ValueError(
            f"{architecture['run_id']} lacks surfaces for {definition.component_id}"
        )
    baseline = layers[definition.baseline_surface]
    component_off = layers[definition.component_off_surface]
    baseline_score = baseline["scores"]
    off_score = component_off["scores"]
    overall_delta = _delta(
        off_score["overall"]["f1"],
        baseline_score["overall"]["f1"],
    )
    component_delta = _delta(
        baseline_score["overall"]["f1"],
        off_score["overall"]["f1"],
    )
    family_component_contribution_deltas = {
        family: _delta(
            baseline_score["families"][family]["f1"],
            off_score["families"][family]["f1"],
        )
        for family in TARGET_INDICATORS
    }
    family_component_off_deltas = {
        family: _delta(
            off_score["families"][family]["f1"],
            baseline_score["families"][family]["f1"],
        )
        for family in TARGET_INDICATORS
    }
    return {
        "artifact_kind": "exectv2_component_off_replay_config",
        "dataset": "exectv2",
        "ablation_id": (
            f"{architecture['run_id']}__without_{definition.component_id}"
        ),
        "baseline_run_id": architecture["run_id"],
        "component_off_run_id": (
            f"{architecture['run_id']}__without_{definition.component_id}"
        ),
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
        "validity_rates": {
            "schema_validity": "not_recorded_in_source_summary",
            "evidence_validity": "not_recorded_in_source_summary",
        },
        "operational_counts": {
            "call_failures": "not_recorded_in_source_summary",
            "parse_failures": "not_recorded_in_source_summary",
            "abstentions": "not_recorded_in_source_summary",
            "missing_outputs": "not_recorded_in_source_summary",
        },
        "row_inspection_policy": "aggregate_only",
        "allow_model_calls": False,
        "allow_post_run_tuning": False,
        "claim_boundary": COMPONENT_OFF_CLAIM_BOUNDARY,
        "stop_rule": COMPONENT_OFF_STOP_RULE,
    }


def _yaml_lines(key: str, value: Any, *, indent: int = 0) -> list[str]:
    prefix = " " * indent
    if isinstance(value, dict):
        lines = [f"{prefix}{key}:"]
        for child_key, child_value in value.items():
            lines.extend(_yaml_lines(str(child_key), child_value, indent=indent + 2))
        return lines
    if isinstance(value, list):
        lines = [f"{prefix}{key}:"]
        for item in value:
            if isinstance(item, dict):
                lines.append(f"{prefix}  -")
                for child_key, child_value in item.items():
                    lines.extend(
                        _yaml_lines(str(child_key), child_value, indent=indent + 4)
                    )
            else:
                lines.append(f"{prefix}  - {_yaml_scalar(item)}")
        return lines
    return [f"{prefix}{key}: {_yaml_scalar(value)}"]


def _yaml_scalar(value: Any) -> str:
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


def _load_summary(path: Path) -> dict[str, Any]:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _has_layer(summary: dict[str, Any], layer: LayerDefinition) -> bool:
    if layer.score_source == "score_ladder":
        return layer.surface_key in summary.get("score_ladder", {})
    return layer.surface_key in summary.get("score_ladder", {}).get("materialized_surfaces", {})


def _layer_score(summary: dict[str, Any], layer: LayerDefinition) -> dict[str, Any]:
    if layer.score_source == "score_ladder":
        score = summary["score_ladder"][layer.surface_key]
    else:
        score = summary["score_ladder"]["materialized_surfaces"][layer.surface_key]
    return {
        "layer_id": layer.layer_id,
        "label": layer.label,
        "component_type": layer.component_type,
        "surface_key": layer.surface_key,
        "interpretation": layer.interpretation,
        "inert": layer.inert,
        "scores": _surface_scores(score),
    }


def _layer_impacts(
    *,
    run_id: str,
    layers: list[dict[str, Any]],
    generated_on: str,
) -> list[dict[str, Any]]:
    impacts: list[dict[str, Any]] = []
    for index, layer in enumerate(layers):
        previous = layers[index - 1] if index > 0 else None
        previous_scores = previous["scores"] if previous else None
        current_scores = layer["scores"]
        overall_delta = (
            0.0
            if previous_scores is None
            else _delta(current_scores["overall"]["f1"], previous_scores["overall"]["f1"])
        )
        family_deltas = {
            family: (
                0.0
                if previous_scores is None
                else _delta(
                    current_scores["families"][family]["f1"],
                    previous_scores["families"][family]["f1"],
                )
            )
            for family in TARGET_INDICATORS
        }
        impacts.append(
            {
                "artifact_kind": "exectv2_component_layer_impact",
                "dataset": "exectv2",
                "generated_on": generated_on,
                "run_id": run_id,
                "layer_id": layer["layer_id"],
                "layer_label": layer["label"],
                "component_type": layer["component_type"],
                "previous_layer_id": previous["layer_id"] if previous else "",
                "previous_layer_label": previous["label"] if previous else "",
                "overall_delta_from_previous": overall_delta,
                "family_deltas": family_deltas,
                "current_score": current_scores,
                "previous_score": previous_scores,
                "claim_boundary": CLAIM_BOUNDARY,
                "row_inspection_policy": "aggregate_only",
            }
        )
    return impacts


def _surface_scores(surface: dict[str, Any]) -> dict[str, Any]:
    return {
        "overall": _score_counts(surface["overall"]),
        "families": {
            family: _score_counts(surface["by_indicator"][family])
            for family in TARGET_INDICATORS
        },
    }


def _score_counts(score: dict[str, Any]) -> dict[str, Any]:
    fields = (
        "precision",
        "recall",
        "f1",
        "tp",
        "fp",
        "fn",
        "pred_count",
        "gold_count",
        "precision_tp",
        "recall_tp",
    )
    out: dict[str, Any] = {}
    for field in fields:
        if field in score:
            value = score[field]
            out[field] = round(float(value), 4) if isinstance(value, float) else value
    return out


def _delta(after: float, before: float) -> float:
    return round(float(after) - float(before), 4)


def main() -> None:
    generated_on = date.today().isoformat()
    paths = write_component_ablation_artifacts(
        DEFAULT_REPLAY_SPECS,
        generated_on=generated_on,
    )
    print(f"Wrote {paths['json']}")
    print(f"Wrote {paths['jsonl']}")
    print(f"Wrote {paths['markdown']}")
    print(f"Wrote configs under {paths['configs']}")
    print(f"Wrote {paths['component_off_json']}")
    print(f"Wrote {paths['component_off_jsonl']}")
    print(f"Wrote {paths['component_off_markdown']}")


if __name__ == "__main__":
    main()
