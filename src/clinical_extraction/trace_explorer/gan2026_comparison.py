"""Project the retained Gan six-model panel into the frontend selector contract.

Gan's v0.7 test450 rows are sealed. The frontend may surface retained aggregate
scores, but it must never imply that row-level replays exist. The matched
LLM-only panel has not been measured, so those variants are named for comparison
completeness and explicitly marked unavailable.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal


@dataclass(frozen=True)
class ModelCondition:
    slug: str
    route: str
    label: str


MODEL_CONDITIONS = (
    ModelCondition("gpt41mini", "openai/gpt-4.1-mini", "GPT-4.1-mini"),
    ModelCondition("gpt56luna", "openai/gpt-5.6-luna", "GPT-5.6 Luna"),
    ModelCondition("gpt56sol", "openai/gpt-5.6-sol", "GPT-5.6 Sol"),
    ModelCondition(
        "deepseek_v4_flash",
        "deepseek/deepseek-v4-flash",
        "DeepSeek V4 Flash (thinking)",
    ),
    ModelCondition("qwen36_35b", "ollama_chat/qwen3.6:35b", "Qwen 3.6:35B"),
    ModelCondition("gemma4_26b", "ollama_chat/gemma4:26b", "Gemma 4 26B"),
)

PURIST_MEASUREMENT = "gan2026_six_model_test450_purist_accuracy"
PRAGMATIC_MEASUREMENT = "gan2026_six_model_test450_pragmatic_accuracy"


def build_gan2026_pipeline_families(scorecard_path: Path) -> dict[str, Any]:
    """Build the 6 + 6 + 1 Gan comparison catalog from retained aggregates."""

    payload = json.loads(scorecard_path.read_text(encoding="utf-8"))
    measurements = payload.get("measurements")
    if not isinstance(measurements, list):
        raise ValueError("shared reliability scorecard has no measurements")

    by_id = {
        str(item.get("measurement_id")): item
        for item in measurements
        if isinstance(item, dict)
    }
    purist = _measurement_values(by_id, PURIST_MEASUREMENT)
    pragmatic = _measurement_values(by_id, PRAGMATIC_MEASUREMENT)

    families: list[dict[str, Any]] = []
    for condition in MODEL_CONDITIONS:
        purist_value = _model_value(purist, condition.route, PURIST_MEASUREMENT)
        pragmatic_value = _model_value(
            pragmatic, condition.route, PRAGMATIC_MEASUREMENT
        )
        families.append(
            _model_family(
                condition,
                comparison_mode="llm_plus_rules",
                availability="aggregate_only",
                evidence_scope="test450_aggregate_only",
                metrics={
                    "row_count": 450,
                    "purist_correct": int(purist_value["correct"]),
                    "purist_accuracy": float(purist_value["accuracy"]),
                    "pragmatic_correct": int(pragmatic_value["correct"]),
                    "pragmatic_accuracy": float(pragmatic_value["accuracy"]),
                },
            )
        )

    for condition in MODEL_CONDITIONS:
        families.append(
            _model_family(
                condition,
                comparison_mode="llm_only",
                availability="not_retained",
                evidence_scope="not_measured",
                metrics=None,
            )
        )

    families.append(
        {
            "value": "rules_only",
            "run_id": "rules_only",
            "label": "Deterministic canonical",
            "display_label": "Deterministic canonical",
            "model_label": "No model",
            "executable": True,
            "kind": "rules_only",
            "architecture_family": "rules_only",
            "pipeline_family": "rules_only",
            "model": "(model-independent)",
            "comparison_mode": "deterministic_only",
            "comparison_role": "control",
            "availability": "live",
            "evidence_scope": "validation_rows",
            "has_replay_artifact": False,
            "split": "validation",
            "prompt_version": "deterministic",
            "repair_mode": "deterministic_v1",
            "run_count": 1,
        }
    )
    return {
        "generated_on": payload.get("generated_date"),
        "source_artifact": f"experiments/{scorecard_path.name}",
        "claim_boundary": (
            "Gan v0.7 test450 is aggregate-only. Matched six-model LLM-only "
            "scores and row-level v0.7 replays are not retained."
        ),
        "families": families,
    }


def write_gan2026_pipeline_families(scorecard_path: Path, output_path: Path) -> Path:
    payload = build_gan2026_pipeline_families(scorecard_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return output_path


def _measurement_values(
    measurements: dict[str, dict[str, Any]], measurement_id: str
) -> dict[str, Any]:
    measurement = measurements.get(measurement_id)
    if measurement is None:
        raise ValueError(f"missing retained measurement: {measurement_id}")
    values = measurement.get("value")
    if not isinstance(values, dict):
        raise ValueError(f"retained measurement has no model values: {measurement_id}")
    return values


def _model_value(
    values: dict[str, Any], route: str, measurement_id: str
) -> dict[str, Any]:
    value = values.get(route)
    if not isinstance(value, dict):
        raise ValueError(f"{measurement_id} has no value for {route}")
    return value


def _model_family(
    condition: ModelCondition,
    *,
    comparison_mode: Literal["llm_plus_rules", "llm_only"],
    availability: Literal["aggregate_only", "not_retained"],
    evidence_scope: Literal["test450_aggregate_only", "not_measured"],
    metrics: dict[str, Any] | None,
) -> dict[str, Any]:
    family = (
        "hybrid_structured_events"
        if comparison_mode == "llm_plus_rules"
        else "llm_only_raw_output"
    )
    kind = "hybrid" if comparison_mode == "llm_plus_rules" else "llm_only"
    run_id = f"gan2026_winning_mode_{condition.slug}_{comparison_mode}_test450"
    result: dict[str, Any] = {
        "value": run_id,
        "run_id": run_id,
        "label": condition.label,
        "display_label": condition.label,
        "model_label": condition.label,
        "executable": False,
        "kind": kind,
        "architecture_family": kind,
        "pipeline_family": family,
        "model": condition.route,
        "comparison_mode": comparison_mode,
        "comparison_role": (
            "winner" if comparison_mode == "llm_plus_rules" else "diagnostic"
        ),
        "availability": availability,
        "evidence_scope": evidence_scope,
        "has_replay_artifact": False,
        "split": "test450",
        "prompt_version": "gan2026_hybrid_structured_events_v0.7",
        "repair_mode": (
            "hybrid_full_stack" if comparison_mode == "llm_plus_rules" else "none"
        ),
        "run_count": 1,
    }
    if metrics is not None:
        result["metrics"] = metrics
    else:
        result["unavailable_reason"] = (
            "A matched six-model LLM-only Gan panel has not been retained."
        )
    return result
