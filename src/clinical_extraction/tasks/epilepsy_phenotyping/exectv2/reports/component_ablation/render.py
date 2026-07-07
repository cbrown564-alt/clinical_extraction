"""Markdown and YAML renderers for component-ablation artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation.component_off import (
    yaml_lines,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation.definitions import (
    CLAIM_BOUNDARY,
)


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
            layer["layer_id"]: layer["scores"]["overall"]["f1"] for layer in architecture["layers"]
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


def render_full200_component_off_readout_markdown(
    payload: dict[str, Any],
    *,
    json_path: Path,
    jsonl_path: Path,
) -> str:
    lines = [
        "# ExECTv2 One-Component-Off Aggregate Readout (full200)",
        "",
        f"- Generated: `{payload['generated_on']}`",
        f"- JSON: `{json_path.as_posix()}`",
        f"- JSONL: `{jsonl_path.as_posix()}`",
        f"- Predeclaration: `{payload['predeclaration_path']}`",
        f"- Code hash at execution: `{payload['code_hash']}`",
        f"- Worktree state at execution: `{payload['worktree_state']}`",
        f"- Claim boundary: {payload['claim_boundary']}",
        f"- Row inspection boundary: `{payload['row_inspection_boundary']}`",
        "- No model calls; replay is computed from saved full200 summary artifacts.",
        "- Component Impact evidence only, not Reliability Scorecard evidence.",
        f"- Stop-rule outcome: `{payload['stop_rule_outcome']}`",
        "",
        "## Preflight",
        "",
        "| Source family | Status | Split | Rows | Surfaces | Telemetry |",
        "| --- | --- | --- | ---: | --- | --- |",
    ]
    for row in payload["preflight"]:
        lines.append(
            f"| `{row['run_id']}` | `{row['status']}` | `{row['split']}` | "
            f"{row['row_count']} | {row['surface_status']} | "
            f"{row['telemetry_status']} |"
        )
    lines.extend(
        [
            "",
            "## Selected Components",
            "",
            "| Component | Type | Portability | Prediction-bearing | Baseline | Off |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for component in payload["selected_components"]:
        lines.append(
            f"| `{component['component_id']}` | `{component['component_type']}` | "
            f"`{component['component_portability_category']}` | "
            f"`{component['prediction_bearing_status']}` | "
            f"`{component['baseline_surface']}` | "
            f"`{component['component_off_surface']}` |"
        )
    lines.extend(
        [
            "",
            "## Aggregate Component-Off Table",
            "",
            (
                "| Source family | Component | Baseline F1 | Component-off F1 | "
                "Contribution delta | Diagnosis | SF | Rx | Inv |"
            ),
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
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
    lines.extend(
        [
            "",
            "## Validity And Operations",
            "",
            (
                "| Source family | Schema validity | Evidence validity | Calls failed | "
                "Parse/schema failures | Invalid evidence dropped |"
            ),
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    seen: set[str] = set()
    for ablation in payload["ablations"]:
        run_id = str(ablation["baseline_run_id"])
        if run_id in seen:
            continue
        seen.add(run_id)
        validity = ablation["validity_rates"]
        counts = ablation["operational_counts"]
        lines.append(
            f"| `{run_id}` | {validity['schema_validity']:.4f} | "
            f"{validity['evidence_validity']:.4f} | "
            f"{counts['call_failures']} | {counts['parse_failures']} | "
            f"{counts['evidence_invalid_dropped']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation Boundary",
            "",
            (
                "Contribution delta is baseline minus component-off on the declared "
                "`clinical_headline` scorer. Positive deltas mean removing the "
                "component lowered aggregate F1 on this source family; null or "
                "negative deltas remain valid component-impact evidence and stop "
                "the audit without tuning."
            ),
            "",
            (
                "These rows are full200 aggregate Component Impact evidence only. "
                "They are not holdout results, strict benchmark claims, or "
                "Reliability Scorecard promotion evidence."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def render_component_off_replay_config(config: dict[str, Any]) -> str:
    """Render a deterministic YAML-like config without requiring YAML at runtime."""

    lines: list[str] = []
    for key, value in config.items():
        lines.extend(yaml_lines(key, value))
    return "\n".join(lines) + "\n"
