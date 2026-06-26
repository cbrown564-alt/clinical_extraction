"""Layer ladder scoring from saved finding-assembly summaries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.frontend_review import REPO_ROOT
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.target_indicator_report import TARGET_INDICATORS
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation.definitions import LAYER_DEFINITIONS
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation.types import LayerDefinition
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation.telemetry import round_rate

def load_summary(path: Path) -> dict[str, Any]:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def has_layer(summary: dict[str, Any], layer: LayerDefinition) -> bool:
    if layer.score_source == "score_ladder":
        return layer.surface_key in summary.get("score_ladder", {})
    return layer.surface_key in summary.get("score_ladder", {}).get("materialized_surfaces", {})


def has_declared_surface(summary: dict[str, Any], surface_id: str) -> bool:
    layer = next(
        (definition for definition in LAYER_DEFINITIONS if definition.layer_id == surface_id),
        None,
    )
    if layer is None:
        return False
    return has_layer(summary, layer)


def layer_score(summary: dict[str, Any], layer: LayerDefinition) -> dict[str, Any]:
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
        "scores": surface_scores(score),
    }


def layer_impacts(
    *,
    run_id: str,
    layers: list[dict[str, Any]],
    generated_on: str,
    claim_boundary: str,
) -> list[dict[str, Any]]:
    impacts: list[dict[str, Any]] = []
    for index, layer in enumerate(layers):
        previous = layers[index - 1] if index > 0 else None
        previous_scores = previous["scores"] if previous else None
        current_scores = layer["scores"]
        overall_delta = (
            0.0
            if previous_scores is None
            else delta(current_scores["overall"]["f1"], previous_scores["overall"]["f1"])
        )
        family_deltas = {
            family: (
                0.0
                if previous_scores is None
                else delta(
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
                "claim_boundary": claim_boundary,
                "row_inspection_policy": "aggregate_only",
            }
        )
    return impacts


def surface_scores(surface: dict[str, Any]) -> dict[str, Any]:
    return {
        "overall": score_counts(surface["overall"]),
        "families": {
            family: score_counts(surface["by_indicator"][family]) for family in TARGET_INDICATORS
        },
    }


def score_counts(score: dict[str, Any]) -> dict[str, Any]:
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


def delta(after: float, before: float) -> float:
    return round(float(after) - float(before), 4)

