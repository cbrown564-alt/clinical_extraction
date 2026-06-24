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

DEFAULT_GENERATED_ON = "2026-06-24"
CLAIM_BOUNDARY = "dev140 replay-only aggregate component-impact ladder"
PROVENANCE_POLICY = "format_only_projection_separated_from_semantic_add_drop_replace"


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
    if frontend_path is not None:
        (REPO_ROOT / frontend_path).parent.mkdir(parents=True, exist_ok=True)
        (REPO_ROOT / frontend_path).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
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
            "Final assembly | Headline projection |"
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
            f"{scores.get('final_assembly', 0.0):.4f} | "
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
    paths = write_component_ablation_artifacts(
        DEFAULT_REPLAY_SPECS,
        generated_on=date.today().isoformat(),
    )
    print(f"Wrote {paths['json']}")
    print(f"Wrote {paths['jsonl']}")
    print(f"Wrote {paths['markdown']}")
    print(f"Wrote configs under {paths['configs']}")


if __name__ == "__main__":
    main()
