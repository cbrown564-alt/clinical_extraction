"""Cross-task shared-component ablation from saved validation replay artifacts.

Reads ExECTv2 one-component-off JSON and Gan2026 stage-ladder JSON; emits
aggregate baseline / component-off / contribution-delta rows for components
tagged in ExECTv2 ``definitions.yaml`` with a Gan stage mapping.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]

DEFAULT_EXECTV2_COMPONENT_OFF = Path(
    "experiments/exectv2_component_off_replay_dev140_20260626.json"
)
DEFAULT_GAN2026_LADDER = Path(
    "experiments/gan2026_component_stage_ladder_validation_20260624.json"
)
DEFINITIONS_YAML = Path(
    "src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/reports/"
    "component_ablation/definitions.yaml"
)

CLAIM_BOUNDARY = (
    "validation-side cross-task shared-component ablation; aggregate-only replay "
    "from saved dev140 (ExECTv2) and validation750 (Gan2026) artifacts; no model "
    "calls, no row-level inspection, no new freeze"
)


@dataclass(frozen=True)
class GanStageMapping:
    stage_id: str
    representative_run_id: str
    mapping_note: str


@dataclass(frozen=True)
class CrossTaskComponentMapping:
    component_id: str
    component_type: str
    portability_category: str
    prediction_bearing_status: str
    exectv2_baseline_surface: str
    exectv2_component_off_surface: str
    exectv2_representative_run_id: str
    gan2026: GanStageMapping | None


# Gan mappings for shared-core components. ``None`` means no clean ladder rung.
CROSS_TASK_MAPPINGS: tuple[CrossTaskComponentMapping, ...] = (
    CrossTaskComponentMapping(
        component_id="evidence_validation",
        component_type="evidence_validation",
        portability_category="general",
        prediction_bearing_status="no",
        exectv2_baseline_surface="evidence_valid",
        exectv2_component_off_surface="source_scored",
        exectv2_representative_run_id="exectv2_holistic_finding_assembly_v08_dev140",
        gan2026=GanStageMapping(
            stage_id="evidence_trace_check",
            representative_run_id="deterministic_canonical_pipeline",
            mapping_note=(
                "Exact-substring evidence gate on the deterministic stack; "
                "hybrid/LLM architectures embed evidence logic in "
                "evidence_projection / label_repair instead of a separate gate."
            ),
        ),
    ),
    CrossTaskComponentMapping(
        component_id="standard_dictionary",
        component_type="dictionary",
        portability_category="clinical_epilepsy",
        prediction_bearing_status="conditional",
        exectv2_baseline_surface="dictionary_normalized",
        exectv2_component_off_surface="evidence_valid",
        exectv2_representative_run_id="exectv2_holistic_finding_assembly_v08_dev140",
        gan2026=GanStageMapping(
            stage_id="normalize",
            representative_run_id=(
                "gan2026_three_way_comparison_validation750_hybrid_structured_events_"
                "gpt41mini_2026-06-07"
            ),
            mapping_note=(
                "Format-level SF label normalization on hybrid structured-events; "
                "not identical to ExECTv2 CUI/dictionary normalization but the "
                "closest SF-normalization rung on the Gan ladder."
            ),
        ),
    ),
)


def load_exectv2_definitions() -> list[dict[str, Any]]:
    path = REPO_ROOT / DEFINITIONS_YAML
    catalog = yaml.safe_load(path.read_text(encoding="utf-8"))
    return list(catalog["component_off"])


def _round4(value: float) -> float:
    return round(float(value), 4)


def _contribution_delta(baseline: float, component_off: float) -> float:
    return _round4(baseline - component_off)


def extract_exectv2_row(
    payload: dict[str, Any],
    *,
    component_id: str,
    run_id: str | None = None,
) -> dict[str, Any]:
    matches = [
        row
        for row in payload["ablations"]
        if row["component_id"] == component_id
        and (run_id is None or row["baseline_run_id"] == run_id)
    ]
    if not matches:
        raise ValueError(f"no ExECTv2 ablation for {component_id!r} run={run_id!r}")
    row = matches[0]
    baseline = float(row["baseline_aggregate_score"]["overall"]["f1"])
    off = float(row["component_off_aggregate_score"]["overall"]["f1"])
    return {
        "task": "exectv2",
        "split": row["split"],
        "row_count": row["row_count"],
        "metric": "clinical_headline_f1",
        "architecture_run_id": row["baseline_run_id"],
        "component_id": component_id,
        "component_type": row["component_type"],
        "portability_category": row["component_portability_category"],
        "prediction_bearing_status": row["prediction_bearing_status"],
        "baseline_surface": row["baseline_surface"],
        "component_off_surface": row["component_off_surface"],
        "baseline_score": _round4(baseline),
        "component_off_score": _round4(off),
        "contribution_delta": _contribution_delta(baseline, off),
        "source_artifact": DEFAULT_EXECTV2_COMPONENT_OFF.as_posix(),
    }


def extract_gan2026_row(
    payload: dict[str, Any],
    *,
    mapping: GanStageMapping,
    component_id: str,
    component_type: str,
    portability_category: str,
    prediction_bearing_status: str,
) -> dict[str, Any]:
    architecture = next(
        (
            arch
            for arch in payload["architectures"]
            if arch["run_id"] == mapping.representative_run_id
        ),
        None,
    )
    if architecture is None:
        raise ValueError(f"missing Gan architecture {mapping.representative_run_id!r}")

    stages = architecture["stages"]
    stage_index = next(
        (index for index, stage in enumerate(stages) if stage["stage_id"] == mapping.stage_id),
        None,
    )
    if stage_index is None:
        raise ValueError(
            f"architecture {mapping.representative_run_id!r} lacks stage "
            f"{mapping.stage_id!r}"
        )
    baseline = float(stages[stage_index]["score"])
    if stage_index == 0:
        component_off = baseline
        component_off_stage_id = stages[0]["stage_id"]
    else:
        component_off = float(stages[stage_index - 1]["score"])
        component_off_stage_id = stages[stage_index - 1]["stage_id"]

    return {
        "task": "gan2026",
        "split": payload["split"],
        "row_count": architecture["row_count"],
        "metric": "purist_accuracy",
        "architecture_run_id": mapping.representative_run_id,
        "component_id": component_id,
        "component_type": component_type,
        "portability_category": portability_category,
        "prediction_bearing_status": prediction_bearing_status,
        "baseline_surface": mapping.stage_id,
        "component_off_surface": component_off_stage_id,
        "baseline_score": _round4(baseline),
        "component_off_score": _round4(component_off),
        "contribution_delta": _contribution_delta(baseline, component_off),
        "mapping_note": mapping.mapping_note,
        "source_artifact": DEFAULT_GAN2026_LADDER.as_posix(),
    }


def build_cross_task_ablation_payload(
    *,
    component_ids: tuple[str, ...] = ("evidence_validation",),
    exectv2_path: Path = DEFAULT_EXECTV2_COMPONENT_OFF,
    gan2026_path: Path = DEFAULT_GAN2026_LADDER,
    generated_on: str = "2026-06-27",
) -> dict[str, Any]:
    exectv2_payload = json.loads((REPO_ROOT / exectv2_path).read_text(encoding="utf-8"))
    gan2026_payload = json.loads((REPO_ROOT / gan2026_path).read_text(encoding="utf-8"))

    rows: list[dict[str, Any]] = []
    for mapping in CROSS_TASK_MAPPINGS:
        if mapping.component_id not in component_ids:
            continue
        rows.append(
            extract_exectv2_row(
                exectv2_payload,
                component_id=mapping.component_id,
                run_id=mapping.exectv2_representative_run_id,
            )
        )
        if mapping.gan2026 is not None:
            rows.append(
                extract_gan2026_row(
                    gan2026_payload,
                    mapping=mapping.gan2026,
                    component_id=mapping.component_id,
                    component_type=mapping.component_type,
                    portability_category=mapping.portability_category,
                    prediction_bearing_status=mapping.prediction_bearing_status,
                )
            )

    return {
        "artifact_kind": "cross_task_shared_component_ablation",
        "generated_on": generated_on,
        "row_inspection_policy": "aggregate_only",
        "allow_model_calls": False,
        "claim_boundary": CLAIM_BOUNDARY,
        "source_artifacts": {
            "exectv2_component_off": exectv2_path.as_posix(),
            "gan2026_stage_ladder": gan2026_path.as_posix(),
            "exectv2_definitions": DEFINITIONS_YAML.as_posix(),
        },
        "rows": rows,
    }
