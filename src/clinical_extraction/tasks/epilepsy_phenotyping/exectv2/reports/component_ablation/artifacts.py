"""Artifact writers and architecture ladder builder."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.frontend_review import REPO_ROOT
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation.component_off import (
    build_component_off_replay_configs,
    build_component_off_readout_payload,
    build_full200_component_off_readout_payload,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation.definitions import (
    CLAIM_BOUNDARY,
    DEFAULT_COMPONENT_OFF_JSON,
    DEFAULT_COMPONENT_OFF_JSONL,
    DEFAULT_COMPONENT_OFF_MD,
    DEFAULT_FULL200_COMPONENT_OFF_JSON,
    DEFAULT_FULL200_COMPONENT_OFF_JSONL,
    DEFAULT_FULL200_COMPONENT_OFF_MD,
    DEFAULT_GENERATED_ON,
    DEFAULT_REPLAY_SPECS,
    LAYER_DEFINITIONS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation.layers import (
    has_layer,
    layer_impacts,
    layer_score,
    load_summary,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation.telemetry import (
    aggregate_operational_counts,
    aggregate_validity_rates,
    deterministic_action_counts,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation.render import (
    render_component_ablation_markdown,
    render_component_off_readout_markdown,
    render_component_off_replay_config,
    render_full200_component_off_readout_markdown,
    render_replay_config,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation.types import ComponentImpactReplaySpec

def build_architecture_layer_ladder(
    spec: ComponentImpactReplaySpec,
    *,
    generated_on: str = DEFAULT_GENERATED_ON,
    claim_boundary: str = CLAIM_BOUNDARY,
    include_telemetry: bool = False,
) -> dict[str, Any]:
    summary = load_summary(spec.source_summary_path)
    layers = [
        layer_score(summary, layer) for layer in LAYER_DEFINITIONS if has_layer(summary, layer)
    ]
    impacts = layer_impacts(
        run_id=spec.run_id,
        layers=layers,
        generated_on=generated_on,
        claim_boundary=claim_boundary,
    )
    final_layer = layers[-1]
    architecture = {
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
        "layer_impacts": impacts,
        "source_artifacts": [
            spec.source_summary_path.as_posix(),
            spec.source_jsonl_path.as_posix(),
        ],
        "claim_boundary": claim_boundary,
        "row_inspection_policy": "aggregate_only",
    }
    if include_telemetry and isinstance(summary.get("lane_diagnostics"), dict):
        architecture.update(
            {
                "validity_rates": aggregate_validity_rates(summary, spec.row_count),
                "operational_counts": aggregate_operational_counts(summary),
                "deterministic_action_counts": deterministic_action_counts(summary),
            }
        )
    return architecture


def write_component_ablation_artifacts(
    specs: tuple[ComponentImpactReplaySpec, ...] = DEFAULT_REPLAY_SPECS,
    *,
    json_path: Path = Path("experiments/exectv2_component_ablation_replay_dev140_20260624.json"),
    jsonl_path: Path = Path("experiments/exectv2_component_ablation_replay_dev140_20260624.jsonl"),
    md_path: Path = Path("experiments/exectv2_component_ablation_replay_dev140_20260624.md"),
    config_dir: Path = Path("configs/exectv2/ablations"),
    frontend_path: Path | None = Path("frontend/public/mock-data/exectv2/component-ablation.json"),
    component_off_json_path: Path = DEFAULT_COMPONENT_OFF_JSON,
    component_off_jsonl_path: Path = DEFAULT_COMPONENT_OFF_JSONL,
    component_off_md_path: Path = DEFAULT_COMPONENT_OFF_MD,
    generated_on: str = DEFAULT_GENERATED_ON,
) -> dict[str, Path]:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation_replay import build_component_ablation_payload

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
    ladder_json: Path = Path("experiments/exectv2_component_ablation_replay_dev140_20260624.json"),
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
        "\n".join(json.dumps(ablation, ensure_ascii=False) for ablation in readout["ablations"])
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


def write_full200_component_off_readout_artifacts(
    *,
    json_path: Path = DEFAULT_FULL200_COMPONENT_OFF_JSON,
    jsonl_path: Path = DEFAULT_FULL200_COMPONENT_OFF_JSONL,
    md_path: Path = DEFAULT_FULL200_COMPONENT_OFF_MD,
    generated_on: str = DEFAULT_GENERATED_ON,
    code_hash: str = "not_recorded",
    worktree_state: str = "not_recorded",
) -> dict[str, Path]:
    readout = build_full200_component_off_readout_payload(
        generated_on=generated_on,
        code_hash=code_hash,
        worktree_state=worktree_state,
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
        "\n".join(json.dumps(ablation, ensure_ascii=False) for ablation in readout["ablations"])
        + "\n",
        encoding="utf-8",
    )
    (REPO_ROOT / md_path).write_text(
        render_full200_component_off_readout_markdown(
            readout,
            json_path=json_path,
            jsonl_path=jsonl_path,
        ),
        encoding="utf-8",
    )
    return resolved


@lru_cache(maxsize=1)
def cached_component_ablation_payload() -> dict[str, Any]:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation_replay import build_component_ablation_payload

    return build_component_ablation_payload()


@lru_cache(maxsize=1)
def cached_component_ablation_json() -> str:
    return json.dumps(cached_component_ablation_payload(), ensure_ascii=False)
