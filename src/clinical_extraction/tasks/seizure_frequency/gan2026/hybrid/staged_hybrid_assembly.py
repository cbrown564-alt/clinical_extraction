"""Assembly surface for the Gan 2026 staged hybrid validation candidate."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    selected_state_union_replay,
    suspicious_selected_state_routing,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    abstention_policy_predeclaration,
    component_evidence_matrix,
    exact_label_selector_ablation,
    last_event_date_instrumentation,
    residual_nonprediction_audit,
    selective_abstention_pressure,
    selective_verifier,
    staged_decision_policy,
    trigger_context_release_rule,
    trigger_release_promotion_analysis,
    validation_surface_inventory,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    DEFAULT_DATA_PATH,
    DEFAULT_SPLIT_MANIFEST_PATH,
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

CANDIDATE_VERSION = "hybrid_multi_component_staged_assembly_v0"
ARTIFACT_STEM = "gan2026_hybrid_multi_component_staged_assembly_v0"
POLICY_NAME = "staged_hybrid_assembly_validation_development_v0"
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_staged_hybrid_assembly_no_call_replay_2026-06-04.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_staged_hybrid_assembly_no_call_replay_2026-06-04.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_staged_hybrid_assembly_no_call_replay_2026-06-04.md"
)
DEFAULT_RICH_STATE_REPLAY_PATH = selected_state_union_replay.DEFAULT_RICH_STATE_REPLAY_PATH
DEFAULT_BOUNDARY_V3_JSONL_PATH = selected_state_union_replay.DEFAULT_BOUNDARY_V3_JSONL_PATH
DEFAULT_PANEL_JSONL_PATH = selected_state_union_replay.DEFAULT_PANEL_JSONL_PATH
DEFAULT_VERIFIER_JSONL_PATH = Path(
    "experiments/"
    "gan2026_selective_verifier_binary_quote_highest_strongprompt_live_gpt41mini_"
    "2026-06-04.jsonl"
)
DEFAULT_VALIDATION750_JSONL_PATH = Path(
    "experiments/gan2026_staged_hybrid_assembly_validation750_no_call_2026-06-04.jsonl"
)
DEFAULT_VALIDATION750_JSON_PATH = Path(
    "experiments/gan2026_staged_hybrid_assembly_validation750_no_call_2026-06-04.json"
)
DEFAULT_VALIDATION750_REPORT_PATH = Path(
    "experiments/gan2026_staged_hybrid_assembly_validation750_no_call_2026-06-04.md"
)
DEFAULT_DECISION_JSONL_PATH = Path(
    "experiments/gan2026_staged_hybrid_decision_layer_validation750_no_call_2026-06-04.jsonl"
)
DEFAULT_DECISION_JSON_PATH = Path(
    "experiments/gan2026_staged_hybrid_decision_layer_validation750_no_call_2026-06-04.json"
)
DEFAULT_DECISION_REPORT_PATH = Path(
    "experiments/gan2026_staged_hybrid_decision_layer_validation750_no_call_2026-06-04.md"
)
DEFAULT_RESIDUAL_AUDIT_JSONL_PATH = Path(
    "experiments/gan2026_staged_hybrid_residual_nonprediction_audit_2026-06-04.jsonl"
)
DEFAULT_RESIDUAL_AUDIT_JSON_PATH = Path(
    "experiments/gan2026_staged_hybrid_residual_nonprediction_audit_2026-06-04.json"
)
DEFAULT_RESIDUAL_AUDIT_REPORT_PATH = Path(
    "experiments/gan2026_staged_hybrid_residual_nonprediction_audit_2026-06-04.md"
)
DEFAULT_ABSTENTION_PRESSURE_JSONL_PATH = Path(
    "experiments/gan2026_staged_hybrid_selective_abstention_pressure_2026-06-04.jsonl"
)
DEFAULT_ABSTENTION_PRESSURE_JSON_PATH = Path(
    "experiments/gan2026_staged_hybrid_selective_abstention_pressure_2026-06-04.json"
)
DEFAULT_ABSTENTION_PRESSURE_REPORT_PATH = Path(
    "experiments/gan2026_staged_hybrid_selective_abstention_pressure_2026-06-04.md"
)
DEFAULT_ABSTENTION_POLICY_JSON_PATH = Path(
    "experiments/gan2026_staged_hybrid_abstention_policy_predeclaration_2026-06-04.json"
)
DEFAULT_ABSTENTION_POLICY_REPORT_PATH = Path(
    "experiments/gan2026_staged_hybrid_abstention_policy_predeclaration_2026-06-04.md"
)
DEFAULT_TRIGGER_RELEASE_JSONL_PATH = Path(
    "experiments/gan2026_staged_hybrid_trigger_context_release_rule_2026-06-04.jsonl"
)
DEFAULT_TRIGGER_RELEASE_PROPOSED_JSONL_PATH = Path(
    "experiments/"
    "gan2026_staged_hybrid_trigger_context_release_proposed_decisions_2026-06-04.jsonl"
)
DEFAULT_TRIGGER_RELEASE_JSON_PATH = Path(
    "experiments/gan2026_staged_hybrid_trigger_context_release_rule_2026-06-04.json"
)
DEFAULT_TRIGGER_RELEASE_REPORT_PATH = Path(
    "experiments/gan2026_staged_hybrid_trigger_context_release_rule_2026-06-04.md"
)
DEFAULT_LAST_EVENT_DATE_JSONL_PATH = Path(
    "experiments/"
    "gan2026_staged_hybrid_last_event_date_instrumentation_2026-06-04.jsonl"
)
DEFAULT_LAST_EVENT_DATE_JSON_PATH = Path(
    "experiments/"
    "gan2026_staged_hybrid_last_event_date_instrumentation_2026-06-04.json"
)
DEFAULT_LAST_EVENT_DATE_REPORT_PATH = Path(
    "experiments/"
    "gan2026_staged_hybrid_last_event_date_instrumentation_2026-06-04.md"
)
DEFAULT_COMPONENT_MATRIX_CSV_PATH = Path(
    "experiments/"
    "gan2026_hybrid_multi_component_staged_assembly_v0_validation750_"
    "component_matrix_2026-06-04.csv"
)
DEFAULT_COMPONENT_MATRIX_JSON_PATH = Path(
    "experiments/"
    "gan2026_hybrid_multi_component_staged_assembly_v0_validation750_"
    "component_matrix_2026-06-04.json"
)
DEFAULT_COMPONENT_MATRIX_REPORT_PATH = Path(
    "experiments/"
    "gan2026_hybrid_multi_component_staged_assembly_v0_validation750_"
    "component_matrix_2026-06-04.md"
)
DEFAULT_TRIGGER_PROMOTION_JSON_PATH = Path(
    "experiments/"
    "gan2026_hybrid_multi_component_staged_assembly_v0_validation750_"
    "trigger_release_promotion_2026-06-04.json"
)
DEFAULT_TRIGGER_PROMOTION_REPORT_PATH = Path(
    "experiments/"
    "gan2026_hybrid_multi_component_staged_assembly_v0_validation750_"
    "trigger_release_promotion_2026-06-04.md"
)
DEFAULT_CANDIDATE_DISCOVERY_JSONL_PATH = Path(
    "experiments/gan2026_rq1_candidate_discovery_matrix_2026-06-03.jsonl"
)
DEFAULT_SELECTOR_ABLATION_CSV_PATH = Path(
    "experiments/"
    "gan2026_hybrid_multi_component_staged_assembly_v0_validation750_"
    "exact_label_selector_ablation_2026-06-05.csv"
)
DEFAULT_SELECTOR_ABLATION_JSON_PATH = Path(
    "experiments/"
    "gan2026_hybrid_multi_component_staged_assembly_v0_validation750_"
    "exact_label_selector_ablation_2026-06-05.json"
)
DEFAULT_SELECTOR_ABLATION_REPORT_PATH = Path(
    "experiments/"
    "gan2026_hybrid_multi_component_staged_assembly_v0_validation750_"
    "exact_label_selector_ablation_2026-06-05.md"
)
DEFAULT_REASONER_JSONL_PATH = validation_surface_inventory.DEFAULT_REASONER_JSONL_PATH
DEFAULT_SAFETY_FLOOR_JSONL_PATH = (
    validation_surface_inventory.DEFAULT_SAFETY_FLOOR_JSONL_PATH
)
DEFAULT_SAFETY_FLOOR_JSON_PATH = validation_surface_inventory.DEFAULT_SAFETY_FLOOR_JSON_PATH
DEFAULT_ROUTER_JSONL_PATH = validation_surface_inventory.DEFAULT_ROUTER_JSONL_PATH
DEFAULT_ROUTER_JSON_PATH = validation_surface_inventory.DEFAULT_ROUTER_JSON_PATH


def build_no_call_validation_development_replay(
    saved_rich_state_rows: Sequence[Mapping[str, Any]],
    boundary_candidate_rows: Sequence[Mapping[str, Any]],
    *,
    panel_rows: Sequence[Mapping[str, Any]] = (),
    verifier_rows: Sequence[Mapping[str, Any]] = (),
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    """Compose the currently promoted no-call replay components.

    This is the first assembly surface for the staged hybrid candidate. It
    deliberately wires existing component outputs together without hiding their
    independent reports or ownership.
    """

    selected_state_rows, selected_state_metadata = (
        selected_state_union_replay.build_selected_state_union_replay_rows(
            saved_rich_state_rows,
            boundary_candidate_rows,
            panel_rows=panel_rows,
        )
    )
    suspicious_rows, suspicious_metadata = (
        suspicious_selected_state_routing.build_suspicious_routing_rows(
            saved_rich_state_rows,
            panel_rows=panel_rows,
        )
    )
    outputs = {
        "selected_state_union": selected_state_rows,
        "suspicious_state_routing": suspicious_rows,
    }
    component_outputs: dict[str, dict[str, Any]] = {
        "selected_state_union": {
            "component_owner": "hybrid_selected_state_union",
            "source_metadata": selected_state_metadata,
        },
        "suspicious_state_routing": {
            "component_owner": "deterministic_suspicious_state_policy",
            "source_metadata": suspicious_metadata,
        },
    }
    metrics = {
        "selected_state_rows": len(selected_state_rows),
        "suspicious_routing_rows": len(suspicious_rows),
        "projection_source_id_inconsistent_rows": selected_state_metadata["metrics"][
            "projection_source_id_inconsistent_rows"
        ],
        "suspicious_state_rows": suspicious_metadata["metrics"][
            "suspicious_state_rows"
        ],
        "suspicious_route_review_rows": suspicious_metadata["metrics"][
            "route_review_rows"
        ],
        "suspicious_route_unknown_rows": suspicious_metadata["metrics"][
            "route_unknown_rows"
        ],
    }
    if verifier_rows:
        verifier_summary = selective_verifier.summarize_saved_binary_verifier_rows(
            verifier_rows
        )
        outputs["selective_verifier"] = list(verifier_rows)
        component_outputs["selective_verifier"] = {
            "component_owner": "llm_selective_verifier",
            "source_metadata": verifier_summary,
        }
        metrics.update(
            {
                "selective_verifier_rows": verifier_summary["row_count"],
                "selective_verifier_w_to_c_rows": verifier_summary[
                    "w_to_c_vs_routing_rows"
                ],
                "selective_verifier_c_to_w_rows": verifier_summary[
                    "c_to_w_vs_routing_rows"
                ],
                "selective_verifier_c_to_review_rows": verifier_summary[
                    "c_to_review_vs_routing_rows"
                ],
                "selective_verifier_w_to_review_rows": verifier_summary[
                    "w_to_review_vs_routing_rows"
                ],
            }
        )

    assembly_rows = build_assembly_rows(outputs)
    metrics.update(_assembly_coverage_metrics(assembly_rows))

    return outputs, {
        "artifact_kind": "gan2026_staged_hybrid_no_call_validation_development_replay",
        "policy_name": POLICY_NAME,
        "split_manifest": "gan2026_split_v1",
        "split": "validation",
        "claim_language": (
            "Validation-development assembly replay over saved artifacts only. "
            "No new live LLM calls, locked-test inspection, whole-pipeline "
            "promotion, or benchmark-comparable claim."
        ),
        "component_outputs": component_outputs,
        "metrics": metrics,
    }


def build_assembly_rows(
    component_outputs: Mapping[str, Sequence[Mapping[str, Any]]],
) -> list[dict[str, Any]]:
    """Join component outputs into one row per source row for inspection."""

    selected_by_source = _by_source(component_outputs.get("selected_state_union", ()))
    suspicious_by_source = _by_source(component_outputs.get("suspicious_state_routing", ()))
    verifier_by_source = _by_source(component_outputs.get("selective_verifier", ()))
    source_indices = sorted(
        set(selected_by_source) | set(suspicious_by_source) | set(verifier_by_source)
    )
    rows = []
    for source_row_index in source_indices:
        selected = selected_by_source.get(source_row_index)
        suspicious = suspicious_by_source.get(source_row_index)
        verifier = verifier_by_source.get(source_row_index)
        rows.append(
            {
                "artifact_kind": "gan2026_staged_hybrid_assembly_row",
                "policy_name": POLICY_NAME,
                "source_row_index": source_row_index,
                "split": _first_value("split", selected, suspicious, verifier)
                or "validation",
                "split_manifest": _first_value(
                    "split_manifest", selected, suspicious, verifier
                )
                or "gan2026_split_v1",
                "gold_label": _first_value("gold_label", selected, suspicious),
                "selected_state_union": selected,
                "suspicious_state_routing": suspicious,
                "selective_verifier": verifier,
                "component_presence": {
                    "selected_state_union": selected is not None,
                    "suspicious_state_routing": suspicious is not None,
                    "selective_verifier": verifier is not None,
                },
            }
        )
    return rows


def build_validation750_no_call_replay(
    reasoner_rows: Sequence[Mapping[str, Any]],
    safety_floor_rows: Sequence[Mapping[str, Any]],
    router_rows: Sequence[Mapping[str, Any]],
    *,
    safety_floor_summary: Mapping[str, Any] | None = None,
    router_summary: Mapping[str, Any] | None = None,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    """Compose the available full-validation saved component surfaces."""

    inventory = validation_surface_inventory.build_validation_surface_inventory(
        reasoner_rows=reasoner_rows,
        safety_floor_rows=safety_floor_rows,
        router_rows=router_rows,
        safety_floor_summary=safety_floor_summary,
        router_summary=router_summary,
    )
    outputs = {
        "hybrid_reasoner_replay": adapt_reasoner_replay_rows(reasoner_rows),
        "selective_safety_floor_gate_v0": adapt_safety_floor_gate_rows(
            safety_floor_rows
        ),
        "rq9_selective_action_router_v3": adapt_selective_action_router_rows(
            router_rows
        ),
    }
    assembly_rows = build_validation750_assembly_rows(outputs)
    metrics = {
        "assembly_rows": len(assembly_rows),
        "reasoner_rows": len(outputs["hybrid_reasoner_replay"]),
        "safety_floor_rows": len(outputs["selective_safety_floor_gate_v0"]),
        "router_rows": len(outputs["rq9_selective_action_router_v3"]),
        "assembly_rows_with_reasoner": sum(
            row["component_presence"]["hybrid_reasoner_replay"]
            for row in assembly_rows
        ),
        "assembly_rows_with_safety_floor": sum(
            row["component_presence"]["selective_safety_floor_gate_v0"]
            for row in assembly_rows
        ),
        "assembly_rows_with_router": sum(
            row["component_presence"]["rq9_selective_action_router_v3"]
            for row in assembly_rows
        ),
        "router_predict_rows": inventory["available_components"][2][
            "action_counts"
        ].get("predict", 0),
        "router_abstain_rows": inventory["available_components"][2][
            "action_counts"
        ].get("abstain", 0),
        "router_human_review_rows": inventory["available_components"][2][
            "action_counts"
        ].get("human_review", 0),
        "safety_floor_selected_evidence_exact_rows": inventory[
            "available_components"
        ][1]["selected_evidence_exact_rows"],
        "safety_floor_selected_source_ids_exist_rows": inventory[
            "available_components"
        ][1]["selected_source_ids_exist_rows"],
    }

    return outputs, {
        "artifact_kind": "gan2026_staged_hybrid_validation750_no_call_assembly",
        "policy_name": POLICY_NAME,
        "split_manifest": "gan2026_split_v1",
        "split": "validation",
        "claim_language": (
            "Validation750 staged assembly over saved component artifacts only. "
            "No new model calls, locked-test inspection, whole-pipeline "
            "promotion, verifier full-validation effect estimate, or "
            "benchmark-comparable claim."
        ),
        "component_outputs": {
            component["component_name"]: {
                "component_owner": component["component_name"],
                "source_metadata": component,
            }
            for component in inventory["available_components"]
        },
        "missing_component_inputs": inventory["missing_component_inputs"],
        "next_assembly_action": (
            "Add the explicit prediction-bearing decision layer over the assembled "
            "validation750 component rows, keeping verifier slice evidence separate "
            "until a full-validation verifier protocol exists."
        ),
        "metrics": metrics,
    }


def adapt_reasoner_replay_rows(
    rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Adapt saved reasoner replay rows without copying prompt payload strings."""

    adapted = []
    for row in rows:
        score_layers = row.get("score_layers", {})
        llm_candidate_record = row.get("structured_llm_candidate_record") or {}
        adapted.append(
            {
                "artifact_kind": "gan2026_assembly_reasoner_replay_component",
                "source_row_index": row["source_row_index"],
                "split": row.get("split", "validation"),
                "split_manifest": row.get("split_manifest", "gan2026_split_v1"),
                "reference": row.get("reference", {}),
                "component_status": row.get("component_status", {}),
                "selected_candidate": row.get("structured_adjudicator_record", {}),
                "llm_candidate_selection": llm_candidate_record.get("selection", {}),
                "score_layer": score_layers.get(
                    "hybrid_adjudicator_with_adapters", {}
                ),
                "saved_prompt_payloads_omitted": True,
            }
        )
    return adapted


def adapt_safety_floor_gate_rows(
    rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Adapt saved safety-floor gate rows for assembly inspection."""

    adapted = []
    for row in rows:
        adapted.append(
            {
                "artifact_kind": "gan2026_assembly_safety_floor_gate_component",
                "source_row_index": row["source_row_index"],
                "gold_label": row.get("gold_label"),
                "baseline_label": row.get("baseline_label"),
                "primary_layer": row.get("primary_layer"),
                "first_failure_owner": row.get("first_failure_owner"),
                "first_failure_reason": row.get("first_failure_reason"),
                "hidden_families": row.get("hidden_families", []),
                "selected_evidence_exact": row.get("selected_evidence_exact"),
                "selected_source_ids_exist": row.get("selected_source_ids_exist"),
                "selected_operand_complete": row.get("selected_operand_complete"),
                "selected_source_provenance": row.get("selected_source_provenance"),
                "gate_variants": row.get("gate_variants", {}),
            }
        )
    return adapted


def adapt_selective_action_router_rows(
    rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Adapt saved selective-action router rows for assembly inspection."""

    adapted = []
    for row in rows:
        adapted.append(
            {
                "artifact_kind": "gan2026_assembly_selective_action_router_component",
                "source_row_index": row["source_row_index"],
                "split": row.get("split", "validation"),
                "split_manifest": row.get("split_manifest", "gan2026_split_v1"),
                "router_version": row.get("router_version"),
                "source_layer": row.get("source_layer"),
                "selective_action": row.get("selective_action"),
                "final_label": row.get("final_label"),
                "primary_reason": row.get("primary_reason"),
                "secondary_reasons": row.get("secondary_reasons", []),
                "source_candidate": row.get("source_candidate", {}),
                "router_packet": row.get("router_packet", {}),
                "development_accounting": row.get("development_accounting", {}),
            }
        )
    return adapted


def build_validation750_assembly_rows(
    component_outputs: Mapping[str, Sequence[Mapping[str, Any]]],
) -> list[dict[str, Any]]:
    """Join full-validation component surfaces into one row per source row."""

    reasoner_by_source = _by_source(component_outputs.get("hybrid_reasoner_replay", ()))
    safety_by_source = _by_source(
        component_outputs.get("selective_safety_floor_gate_v0", ())
    )
    router_by_source = _by_source(
        component_outputs.get("rq9_selective_action_router_v3", ())
    )
    source_indices = sorted(
        set(reasoner_by_source) | set(safety_by_source) | set(router_by_source)
    )
    rows = []
    for source_row_index in source_indices:
        reasoner = reasoner_by_source.get(source_row_index)
        safety = safety_by_source.get(source_row_index)
        router = router_by_source.get(source_row_index)
        rows.append(
            {
                "artifact_kind": "gan2026_staged_hybrid_validation750_assembly_row",
                "policy_name": POLICY_NAME,
                "source_row_index": source_row_index,
                "split": _first_value("split", reasoner, router) or "validation",
                "split_manifest": _first_value("split_manifest", reasoner, router)
                or "gan2026_split_v1",
                "gold_label": _nested_first_value(
                    ("reference", "gold_label"),
                    reasoner,
                )
                or _first_value("gold_label", safety),
                "hybrid_reasoner_replay": reasoner,
                "selective_safety_floor_gate_v0": safety,
                "rq9_selective_action_router_v3": router,
                "component_presence": {
                    "hybrid_reasoner_replay": reasoner is not None,
                    "selective_safety_floor_gate_v0": safety is not None,
                    "rq9_selective_action_router_v3": router is not None,
                },
            }
        )
    return rows


def write_summary_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path = DEFAULT_JSONL_PATH,
    json_path: Path = DEFAULT_JSON_PATH,
) -> None:
    metrics = metadata["metrics"]
    lines = [
        "# Gan 2026 Staged Hybrid Assembly No-Call Replay",
        "",
        "This report assembles saved component artifacts only. It makes no live "
        "model calls and does not authorize locked-test inspection, whole-pipeline "
        "promotion, or benchmark-comparable language.",
        "",
        "## Coverage",
        "",
        (
            f"The joined assembly has {metrics['assembly_rows']} source rows. "
            f"Selected-state union and suspicious routing cover "
            f"{metrics['selected_state_rows']} and {metrics['suspicious_routing_rows']} "
            "rows respectively. The promoted verifier saved replay covers "
            f"{metrics.get('selective_verifier_rows', 0)} rows, so verifier impact is "
            "currently a slice readout, not a full validation750 readout."
        ),
        "",
        "## Claim Boundary",
        "",
        str(metadata["claim_language"]),
        "",
        "## Artifacts",
        "",
        f"- Assembly JSONL: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in metrics.items():
        lines.append(f"| {key.replace('_', ' ')} | {_format_metric(value)} |")
    lines.extend(
        [
            "",
            "## Component Outputs",
            "",
            "| Component | Owner | Rows |",
            "| --- | --- | ---: |",
        ]
    )
    for name, component in metadata["component_outputs"].items():
        source_metadata = component["source_metadata"]
        lines.append(
            f"| `{name}` | `{component['component_owner']}` | "
            f"{source_metadata.get('row_count', 0)} |"
        )
    verifier_regressions = (
        metadata["component_outputs"]
        .get("selective_verifier", {})
        .get("source_metadata", {})
        .get("regression_source_row_indices", [])
    )
    if verifier_regressions:
        lines.extend(
            [
                "",
                "## Verifier Regression Boundary",
                "",
                "The saved promoted-verifier slice still contains C->W rows versus "
                f"routing: {', '.join(str(row) for row in verifier_regressions)}. "
                "These remain visible and must be adjudicated or gated before any "
                "automatic prediction-bearing full-validation use.",
            ]
        )
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_validation750_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path = DEFAULT_VALIDATION750_JSONL_PATH,
    json_path: Path = DEFAULT_VALIDATION750_JSON_PATH,
) -> None:
    metrics = metadata["metrics"]
    lines = [
        "# Gan 2026 Staged Hybrid Validation750 No-Call Assembly",
        "",
        "This report assembles saved validation750 component artifacts only. It "
        "makes no live model calls and does not authorize locked-test inspection, "
        "whole-pipeline promotion, verifier full-validation effect estimates, or "
        "benchmark-comparable language.",
        "",
        "## Coverage",
        "",
        (
            f"The joined assembly has {metrics['assembly_rows']} source rows. "
            f"Reasoner replay, safety-floor gate, and selective router cover "
            f"{metrics['reasoner_rows']}, {metrics['safety_floor_rows']}, and "
            f"{metrics['router_rows']} rows respectively."
        ),
        "",
        "## Selective Routing",
        "",
        (
            f"The router predicts on {metrics['router_predict_rows']} rows, "
            f"abstains on {metrics['router_abstain_rows']}, and routes "
            f"{metrics['router_human_review_rows']} to human review."
        ),
        "",
        "## Claim Boundary",
        "",
        str(metadata["claim_language"]),
        "",
        "## Artifacts",
        "",
        f"- Assembly JSONL: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in metrics.items():
        lines.append(f"| {key.replace('_', ' ')} | {_format_metric(value)} |")

    lines.extend(
        [
            "",
            "## Component Outputs",
            "",
            "| Component | Owner | Rows |",
            "| --- | --- | ---: |",
        ]
    )
    for name, component in metadata["component_outputs"].items():
        source_metadata = component["source_metadata"]
        lines.append(
            f"| `{name}` | `{component['component_owner']}` | "
            f"{source_metadata.get('row_count', 0)} |"
        )

    lines.extend(
        [
            "",
            "## Missing Inputs Kept Out Of This Replay",
            "",
            "| Component | Status |",
            "| --- | --- |",
        ]
    )
    for component in metadata["missing_component_inputs"]:
        lines.append(f"| `{component['component_name']}` | {component['status']} |")

    lines.extend(
        [
            "",
            "## Prompt Payload Boundary",
            "",
            "Historical reasoner prompt payload strings remain in the original saved "
            "artifact rows, but are omitted from this assembly artifact. The "
            "assembly rows keep compact status, candidate, scoring, gate, and "
            "router records only.",
            "",
            "## Next Assembly Action",
            "",
            str(metadata["next_assembly_action"]),
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_decision_layer_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path = DEFAULT_DECISION_JSONL_PATH,
    json_path: Path = DEFAULT_DECISION_JSON_PATH,
) -> None:
    metrics = metadata["metrics"]
    lines = [
        "# Gan 2026 Staged Hybrid Decision Layer Validation750 No-Call Replay",
        "",
        "This report describes the explicit prediction-bearing decision layer over "
        "the assembled validation750 component rows. It makes no live model calls "
        "and does not authorize locked-test inspection, whole-pipeline promotion, "
        "verifier full-validation effect estimates, or benchmark-comparable "
        "language.",
        "",
        "## Decision Policy",
        "",
        str(metadata["claim_language"]),
        "",
        "## Coverage",
        "",
        (
            f"The decision layer has {metrics['row_count']} rows: "
            f"{metrics['prediction_bearing_rows']} prediction-bearing rows and "
            f"{metrics['non_prediction_rows']} non-prediction rows."
        ),
        "",
        "## Actions",
        "",
        "| Action | Rows |",
        "| --- | ---: |",
    ]
    for action, count in metadata["action_counts"].items():
        lines.append(f"| `{action}` | {count} |")

    lines.extend(
        [
            "",
            "## Development Accounting",
            "",
            "| Metric | Value |",
            "| --- | ---: |",
            (
                "| selective purist accuracy | "
                f"{_format_metric(metrics['selective_purist_accuracy'])} |"
            ),
            (
                "| selective pragmatic accuracy | "
                f"{_format_metric(metrics['selective_pragmatic_accuracy'])} |"
            ),
            f"| verifier rows used | {metrics['verifier_rows_used']} |",
            "",
            "## Artifacts",
            "",
            f"- Decision JSONL: `{jsonl_path}`",
            f"- Decision summary JSON: `{json_path}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _assembly_coverage_metrics(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    return {
        "assembly_rows": len(rows),
        "assembly_rows_with_selected_state_union": sum(
            row["component_presence"]["selected_state_union"] for row in rows
        ),
        "assembly_rows_with_suspicious_routing": sum(
            row["component_presence"]["suspicious_state_routing"] for row in rows
        ),
        "assembly_rows_with_selective_verifier": sum(
            row["component_presence"]["selective_verifier"] for row in rows
        ),
    }


def _by_source(rows: Sequence[Mapping[str, Any]]) -> dict[int, Mapping[str, Any]]:
    return {int(row["source_row_index"]): row for row in rows}


def _first_value(key: str, *rows: Mapping[str, Any] | None) -> Any:
    for row in rows:
        if row and row.get(key) is not None:
            return row.get(key)
    return None


def _nested_first_value(path: tuple[str, ...], *rows: Mapping[str, Any] | None) -> Any:
    for row in rows:
        current: Any = row
        for key in path:
            if not isinstance(current, Mapping):
                current = None
                break
            current = current.get(key)
        if current is not None:
            return current
    return None


def _format_metric(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("hard-panel", "validation750"),
        default="hard-panel",
        help="Assembly surface to materialize.",
    )
    parser.add_argument(
        "--rich-state-replay-path", type=Path, default=DEFAULT_RICH_STATE_REPLAY_PATH
    )
    parser.add_argument(
        "--boundary-v3-jsonl-path", type=Path, default=DEFAULT_BOUNDARY_V3_JSONL_PATH
    )
    parser.add_argument("--panel-jsonl-path", type=Path, default=DEFAULT_PANEL_JSONL_PATH)
    parser.add_argument("--verifier-jsonl-path", type=Path, default=DEFAULT_VERIFIER_JSONL_PATH)
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--reasoner-jsonl-path", type=Path, default=DEFAULT_REASONER_JSONL_PATH)
    parser.add_argument("--data-path", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument(
        "--split-manifest-path", type=Path, default=DEFAULT_SPLIT_MANIFEST_PATH
    )
    parser.add_argument(
        "--safety-floor-jsonl-path", type=Path, default=DEFAULT_SAFETY_FLOOR_JSONL_PATH
    )
    parser.add_argument(
        "--safety-floor-json-path", type=Path, default=DEFAULT_SAFETY_FLOOR_JSON_PATH
    )
    parser.add_argument("--router-jsonl-path", type=Path, default=DEFAULT_ROUTER_JSONL_PATH)
    parser.add_argument("--router-json-path", type=Path, default=DEFAULT_ROUTER_JSON_PATH)
    parser.add_argument("--decision-jsonl-path", type=Path, default=DEFAULT_DECISION_JSONL_PATH)
    parser.add_argument("--decision-json-path", type=Path, default=DEFAULT_DECISION_JSON_PATH)
    parser.add_argument(
        "--decision-report-path", type=Path, default=DEFAULT_DECISION_REPORT_PATH
    )
    parser.add_argument(
        "--residual-audit-jsonl-path",
        type=Path,
        default=DEFAULT_RESIDUAL_AUDIT_JSONL_PATH,
    )
    parser.add_argument(
        "--residual-audit-json-path",
        type=Path,
        default=DEFAULT_RESIDUAL_AUDIT_JSON_PATH,
    )
    parser.add_argument(
        "--residual-audit-report-path",
        type=Path,
        default=DEFAULT_RESIDUAL_AUDIT_REPORT_PATH,
    )
    parser.add_argument(
        "--abstention-pressure-jsonl-path",
        type=Path,
        default=DEFAULT_ABSTENTION_PRESSURE_JSONL_PATH,
    )
    parser.add_argument(
        "--abstention-pressure-json-path",
        type=Path,
        default=DEFAULT_ABSTENTION_PRESSURE_JSON_PATH,
    )
    parser.add_argument(
        "--abstention-pressure-report-path",
        type=Path,
        default=DEFAULT_ABSTENTION_PRESSURE_REPORT_PATH,
    )
    parser.add_argument(
        "--abstention-policy-json-path",
        type=Path,
        default=DEFAULT_ABSTENTION_POLICY_JSON_PATH,
    )
    parser.add_argument(
        "--abstention-policy-report-path",
        type=Path,
        default=DEFAULT_ABSTENTION_POLICY_REPORT_PATH,
    )
    parser.add_argument(
        "--trigger-release-jsonl-path",
        type=Path,
        default=DEFAULT_TRIGGER_RELEASE_JSONL_PATH,
    )
    parser.add_argument(
        "--trigger-release-proposed-jsonl-path",
        type=Path,
        default=DEFAULT_TRIGGER_RELEASE_PROPOSED_JSONL_PATH,
    )
    parser.add_argument(
        "--trigger-release-json-path",
        type=Path,
        default=DEFAULT_TRIGGER_RELEASE_JSON_PATH,
    )
    parser.add_argument(
        "--trigger-release-report-path",
        type=Path,
        default=DEFAULT_TRIGGER_RELEASE_REPORT_PATH,
    )
    parser.add_argument(
        "--last-event-date-jsonl-path",
        type=Path,
        default=DEFAULT_LAST_EVENT_DATE_JSONL_PATH,
    )
    parser.add_argument(
        "--last-event-date-json-path",
        type=Path,
        default=DEFAULT_LAST_EVENT_DATE_JSON_PATH,
    )
    parser.add_argument(
        "--last-event-date-report-path",
        type=Path,
        default=DEFAULT_LAST_EVENT_DATE_REPORT_PATH,
    )
    parser.add_argument(
        "--component-matrix-csv-path",
        type=Path,
        default=DEFAULT_COMPONENT_MATRIX_CSV_PATH,
    )
    parser.add_argument(
        "--component-matrix-json-path",
        type=Path,
        default=DEFAULT_COMPONENT_MATRIX_JSON_PATH,
    )
    parser.add_argument(
        "--component-matrix-report-path",
        type=Path,
        default=DEFAULT_COMPONENT_MATRIX_REPORT_PATH,
    )
    parser.add_argument(
        "--trigger-promotion-json-path",
        type=Path,
        default=DEFAULT_TRIGGER_PROMOTION_JSON_PATH,
    )
    parser.add_argument(
        "--trigger-promotion-report-path",
        type=Path,
        default=DEFAULT_TRIGGER_PROMOTION_REPORT_PATH,
    )
    parser.add_argument(
        "--candidate-discovery-jsonl-path",
        type=Path,
        default=DEFAULT_CANDIDATE_DISCOVERY_JSONL_PATH,
    )
    parser.add_argument(
        "--selector-ablation-csv-path",
        type=Path,
        default=DEFAULT_SELECTOR_ABLATION_CSV_PATH,
    )
    parser.add_argument(
        "--selector-ablation-json-path",
        type=Path,
        default=DEFAULT_SELECTOR_ABLATION_JSON_PATH,
    )
    parser.add_argument(
        "--selector-ablation-report-path",
        type=Path,
        default=DEFAULT_SELECTOR_ABLATION_REPORT_PATH,
    )
    args = parser.parse_args(argv)

    if args.mode == "validation750":
        reasoner_rows = load_jsonl_rows(args.reasoner_jsonl_path)
        safety_floor_rows = load_jsonl_rows(args.safety_floor_jsonl_path)
        router_rows = load_jsonl_rows(args.router_jsonl_path)
        outputs, metadata = build_validation750_no_call_replay(
            reasoner_rows,
            safety_floor_rows,
            router_rows,
            safety_floor_summary=_load_json(args.safety_floor_json_path),
            router_summary=_load_json(args.router_json_path),
        )
        assembly_rows = build_validation750_assembly_rows(outputs)
        jsonl_path = (
            args.jsonl_path
            if args.jsonl_path != DEFAULT_JSONL_PATH
            else DEFAULT_VALIDATION750_JSONL_PATH
        )
        json_path = (
            args.json_path
            if args.json_path != DEFAULT_JSON_PATH
            else DEFAULT_VALIDATION750_JSON_PATH
        )
        report_path = (
            args.report_path
            if args.report_path != DEFAULT_REPORT_PATH
            else DEFAULT_VALIDATION750_REPORT_PATH
        )
        metadata = {
            **metadata,
            "source_artifacts": {
                "reasoner_jsonl": str(args.reasoner_jsonl_path),
                "safety_floor_jsonl": str(args.safety_floor_jsonl_path),
                "safety_floor_json": str(args.safety_floor_json_path),
                "router_jsonl": str(args.router_jsonl_path),
                "router_json": str(args.router_json_path),
            },
        }
        write_jsonl_rows(assembly_rows, jsonl_path)
        write_summary_json(metadata, json_path)
        write_validation750_report(
            assembly_rows,
            metadata,
            report_path,
            jsonl_path=jsonl_path,
            json_path=json_path,
        )
        decision_rows = staged_decision_policy.build_decision_rows(assembly_rows)
        decision_summary = staged_decision_policy.summarize_decision_rows(
            decision_rows
        )
        decision_metadata = {
            "artifact_kind": "gan2026_staged_hybrid_decision_layer_validation750",
            "policy_name": staged_decision_policy.POLICY_NAME,
            "split": "validation",
            "split_manifest": "gan2026_split_v1",
            "claim_language": decision_summary["claim_language"],
            "metrics": {
                "row_count": decision_summary["row_count"],
                "prediction_bearing_rows": decision_summary[
                    "prediction_bearing_rows"
                ],
                "non_prediction_rows": decision_summary["non_prediction_rows"],
                "selective_purist_accuracy": decision_summary[
                    "selective_purist_accuracy"
                ],
                "selective_pragmatic_accuracy": decision_summary[
                    "selective_pragmatic_accuracy"
                ],
                "verifier_rows_used": decision_summary["verifier_rows_used"],
            },
            "action_counts": decision_summary["action_counts"],
            "source_artifacts": {
                "assembly_jsonl": str(jsonl_path),
                "assembly_json": str(json_path),
            },
        }
        write_jsonl_rows(decision_rows, args.decision_jsonl_path)
        write_summary_json(decision_metadata, args.decision_json_path)
        write_decision_layer_report(
            decision_rows,
            decision_metadata,
            args.decision_report_path,
            jsonl_path=args.decision_jsonl_path,
            json_path=args.decision_json_path,
        )
        residual_rows = (
            residual_nonprediction_audit.build_residual_nonprediction_rows(
                decision_rows,
                assembly_rows,
            )
        )
        residual_summary = (
            residual_nonprediction_audit.summarize_residual_nonpredictions(
                residual_rows
            )
        )
        residual_summary = {
            **residual_summary,
            "artifact_kind": "gan2026_staged_hybrid_residual_nonprediction_audit",
            "source_artifacts": {
                "assembly_jsonl": str(jsonl_path),
                "decision_jsonl": str(args.decision_jsonl_path),
            },
        }
        write_jsonl_rows(residual_rows, args.residual_audit_jsonl_path)
        residual_nonprediction_audit.write_summary_json(
            residual_summary,
            args.residual_audit_json_path,
        )
        residual_nonprediction_audit.write_report(
            residual_rows,
            residual_summary,
            args.residual_audit_report_path,
            jsonl_path=args.residual_audit_jsonl_path,
            json_path=args.residual_audit_json_path,
        )
        pressure_rows = selective_abstention_pressure.build_pressure_review_rows(
            residual_rows
        )
        pressure_summary = selective_abstention_pressure.summarize_pressure_review(
            pressure_rows
        )
        pressure_summary = {
            **pressure_summary,
            "artifact_kind": "gan2026_staged_hybrid_selective_abstention_pressure",
            "source_artifacts": {
                "residual_audit_jsonl": str(args.residual_audit_jsonl_path),
                "decision_jsonl": str(args.decision_jsonl_path),
            },
        }
        write_jsonl_rows(pressure_rows, args.abstention_pressure_jsonl_path)
        selective_abstention_pressure.write_summary_json(
            pressure_summary,
            args.abstention_pressure_json_path,
        )
        selective_abstention_pressure.write_report(
            pressure_rows,
            pressure_summary,
            args.abstention_pressure_report_path,
            jsonl_path=args.abstention_pressure_jsonl_path,
            json_path=args.abstention_pressure_json_path,
        )
        abstention_policy = abstention_policy_predeclaration.build_predeclaration(
            pressure_rows
        )
        abstention_policy = {
            **abstention_policy,
            "source_artifacts": {
                "pressure_jsonl": str(args.abstention_pressure_jsonl_path),
                "pressure_json": str(args.abstention_pressure_json_path),
            },
        }
        abstention_policy_predeclaration.write_summary_json(
            abstention_policy,
            args.abstention_policy_json_path,
        )
        abstention_policy_predeclaration.write_report(
            abstention_policy,
            args.abstention_policy_report_path,
            json_path=args.abstention_policy_json_path,
        )
        last_event_date_rows = (
            last_event_date_instrumentation.build_last_event_date_rows(
                pressure_rows,
                residual_rows,
                source_records=load_records_for_split(
                    "validation",
                    data_path=args.data_path,
                    manifest_path=args.split_manifest_path,
                ),
            )
        )
        last_event_date_summary = (
            last_event_date_instrumentation.summarize_last_event_date_rows(
                last_event_date_rows
            )
        )
        last_event_date_summary = {
            **last_event_date_summary,
            "artifact_kind": (
                "gan2026_staged_hybrid_last_event_date_instrumentation"
            ),
            "source_artifacts": {
                "pressure_jsonl": str(args.abstention_pressure_jsonl_path),
                "residual_audit_jsonl": str(args.residual_audit_jsonl_path),
                "abstention_policy_json": str(args.abstention_policy_json_path),
                "data_path": str(args.data_path),
                "split_manifest_path": str(args.split_manifest_path),
            },
        }
        write_jsonl_rows(last_event_date_rows, args.last_event_date_jsonl_path)
        last_event_date_instrumentation.write_summary_json(
            last_event_date_summary,
            args.last_event_date_json_path,
        )
        last_event_date_instrumentation.write_report(
            last_event_date_rows,
            last_event_date_summary,
            args.last_event_date_report_path,
            jsonl_path=args.last_event_date_jsonl_path,
            json_path=args.last_event_date_json_path,
        )
        trigger_release_rows = trigger_context_release_rule.build_release_rows(
            pressure_rows,
            residual_rows,
        )
        proposed_decision_rows = trigger_context_release_rule.apply_release_rows(
            decision_rows,
            trigger_release_rows,
        )
        trigger_release_summary = (
            trigger_context_release_rule.summarize_proposed_decisions(
                proposed_decision_rows
            )
        )
        trigger_release_summary = {
            **trigger_release_summary,
            "artifact_kind": "gan2026_staged_hybrid_trigger_context_release_rule",
            "source_artifacts": {
                "decision_jsonl": str(args.decision_jsonl_path),
                "pressure_jsonl": str(args.abstention_pressure_jsonl_path),
                "residual_audit_jsonl": str(args.residual_audit_jsonl_path),
                "abstention_policy_json": str(args.abstention_policy_json_path),
            },
        }
        write_jsonl_rows(trigger_release_rows, args.trigger_release_jsonl_path)
        write_jsonl_rows(
            proposed_decision_rows,
            args.trigger_release_proposed_jsonl_path,
        )
        trigger_context_release_rule.write_summary_json(
            trigger_release_summary,
            args.trigger_release_json_path,
        )
        trigger_context_release_rule.write_report(
            trigger_release_rows,
            trigger_release_summary,
            args.trigger_release_report_path,
            release_jsonl_path=args.trigger_release_jsonl_path,
            proposed_jsonl_path=args.trigger_release_proposed_jsonl_path,
            json_path=args.trigger_release_json_path,
        )
        matrix_rows = component_evidence_matrix.build_matrix_rows(
            assembly_rows,
            decision_rows,
            trigger_release_rows=trigger_release_rows,
            last_event_rows=last_event_date_rows,
            candidate_version=CANDIDATE_VERSION,
        )
        matrix_summary = component_evidence_matrix.summarize_matrix_rows(
            matrix_rows
        )
        contract_issues = component_evidence_matrix.validate_matrix_contract(
            matrix_rows
        )
        matrix_summary = {
            **matrix_summary,
            "artifact_kind": "gan2026_hybrid_multi_component_staged_assembly_component_matrix",
            "candidate_version": CANDIDATE_VERSION,
            "artifact_stem": ARTIFACT_STEM,
            "contract_issues": contract_issues,
            "source_artifacts": {
                "assembly_jsonl": str(jsonl_path),
                "decision_jsonl": str(args.decision_jsonl_path),
                "trigger_release_jsonl": str(args.trigger_release_jsonl_path),
                "last_event_date_jsonl": str(args.last_event_date_jsonl_path),
            },
        }
        component_evidence_matrix.write_csv_rows(
            matrix_rows,
            args.component_matrix_csv_path,
        )
        component_evidence_matrix.write_summary_json(
            matrix_summary,
            args.component_matrix_json_path,
        )
        component_evidence_matrix.write_report(
            matrix_summary,
            args.component_matrix_report_path,
            csv_path=args.component_matrix_csv_path,
            json_path=args.component_matrix_json_path,
        )
        trigger_promotion = (
            trigger_release_promotion_analysis.build_promotion_analysis(
                trigger_release_rows,
                proposed_decision_rows,
                matrix_rows,
            )
        )
        trigger_promotion = {
            **trigger_promotion,
            "artifact_kind": (
                "gan2026_hybrid_multi_component_staged_assembly_trigger_release_promotion"
            ),
            "candidate_version": CANDIDATE_VERSION,
            "source_artifacts": {
                "trigger_release_jsonl": str(args.trigger_release_jsonl_path),
                "proposed_decision_jsonl": str(
                    args.trigger_release_proposed_jsonl_path
                ),
                "component_matrix_csv": str(args.component_matrix_csv_path),
            },
        }
        trigger_release_promotion_analysis.write_summary_json(
            trigger_promotion,
            args.trigger_promotion_json_path,
        )
        trigger_release_promotion_analysis.write_report(
            trigger_promotion,
            args.trigger_promotion_report_path,
            json_path=args.trigger_promotion_json_path,
        )
        candidate_discovery_rows = load_jsonl_rows(args.candidate_discovery_jsonl_path)
        selector_ablation_rows = (
            exact_label_selector_ablation.build_selector_ablation_rows(
                matrix_rows,
                candidate_discovery_rows,
            )
        )
        selector_ablation_summary = (
            exact_label_selector_ablation.summarize_selector_ablation_rows(
                selector_ablation_rows,
                matrix_rows,
            )
        )
        selector_ablation_summary = {
            **selector_ablation_summary,
            "artifact_kind": (
                "gan2026_hybrid_multi_component_staged_assembly_"
                "exact_label_selector_ablation"
            ),
            "candidate_version": CANDIDATE_VERSION,
            "source_artifacts": {
                "component_matrix_csv": str(args.component_matrix_csv_path),
                "candidate_discovery_jsonl": str(args.candidate_discovery_jsonl_path),
            },
        }
        exact_label_selector_ablation.write_csv_rows(
            selector_ablation_rows,
            args.selector_ablation_csv_path,
        )
        exact_label_selector_ablation.write_summary_json(
            selector_ablation_summary,
            args.selector_ablation_json_path,
        )
        exact_label_selector_ablation.write_report(
            selector_ablation_summary,
            args.selector_ablation_report_path,
            csv_path=args.selector_ablation_csv_path,
            json_path=args.selector_ablation_json_path,
        )
        return 0

    saved_rows = load_jsonl_rows(args.rich_state_replay_path)
    boundary_rows = load_jsonl_rows(args.boundary_v3_jsonl_path)
    panel_rows = load_jsonl_rows(args.panel_jsonl_path) if args.panel_jsonl_path.exists() else []
    verifier_rows = (
        load_jsonl_rows(args.verifier_jsonl_path)
        if args.verifier_jsonl_path.exists()
        else []
    )
    outputs, metadata = build_no_call_validation_development_replay(
        saved_rows,
        boundary_rows,
        panel_rows=panel_rows,
        verifier_rows=verifier_rows,
    )
    assembly_rows = build_assembly_rows(outputs)
    metadata = {
        **metadata,
        "source_artifacts": {
            "rich_state_replay": str(args.rich_state_replay_path),
            "boundary_v3": str(args.boundary_v3_jsonl_path),
            "panel": str(args.panel_jsonl_path),
            "verifier": str(args.verifier_jsonl_path)
            if args.verifier_jsonl_path.exists()
            else None,
        },
    }
    write_jsonl_rows(assembly_rows, args.jsonl_path)
    write_summary_json(metadata, args.json_path)
    write_report(
        assembly_rows,
        metadata,
        args.report_path,
        jsonl_path=args.jsonl_path,
        json_path=args.json_path,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
