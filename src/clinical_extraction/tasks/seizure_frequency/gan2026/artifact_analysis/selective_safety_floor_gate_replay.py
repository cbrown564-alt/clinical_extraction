"""Validation-only no-call selective safety-floor gate replay for fixed atlas slices."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
    label_to_frequency_record,
    label_to_monthly_frequency,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist
from clinical_extraction.tasks.seizure_frequency.gan2026.state_graph import (
    ClinicalFrequencyStateGraph,
    GanGraphProjection,
    ProjectionPolicy,
    project_graph_to_gan,
)

DEFAULT_MANIFEST_PATH = Path(
    "experiments/gan2026_atlas_candidate_generation_projection_hard_slices_2026-06-03.json"
)
DEFAULT_PREDECLARATION_PATH = Path(
    "experiments/gan2026_selective_safety_floor_gate_predeclaration_2026-06-03.json"
)
DEFAULT_SOURCE_ARTIFACT_PATH = Path(
    "experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl"
)
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_selective_safety_floor_gate_replay_2026-06-03.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_selective_safety_floor_gate_replay_2026-06-03.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_selective_safety_floor_gate_replay_2026-06-03.md"
)

BASELINE_VARIANT = "baseline_safety_floor_v2"
PROJECTION_VARIANT = "projection_boundary_state_priority_gate_v0"
LLM_VARIANT = "llm_candidate_sidecar_rescue_gate_v0"
COMBINED_VARIANT = "combined_selective_gate_v0"
COMPETING_FREQUENCY_VARIANT = "competing_frequency_uncertainty"
LOWEST_FREQUENCY_VARIANT = "lowest_current_frequency"
RESCUE_FAMILIES = {"unknown_boundary", "seizure_free_duration", "current_vs_historical"}
VARIANTS = (
    BASELINE_VARIANT,
    PROJECTION_VARIANT,
    COMPETING_FREQUENCY_VARIANT,
    LOWEST_FREQUENCY_VARIANT,
    LLM_VARIANT,
    COMBINED_VARIANT,
)


def run_selective_safety_floor_gate_replay(
    manifest: Mapping[str, Any],
    *,
    source_artifact: Path | None = None,
    artifact_dir: Path = Path("experiments"),
    manifest_path: str | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Replay fixed-slice selective safety-floor gates from saved artifact rows."""

    if not manifest.get("slices") and manifest.get("surfaces"):
        predeclaration_path = (
            Path(manifest_path)
            if manifest_path
            else artifact_dir / DEFAULT_PREDECLARATION_PATH.name
        )
        manifest = _surface_manifest_from_predeclaration(
            manifest,
            predeclaration_path=predeclaration_path,
            fallback_manifest_dir=artifact_dir,
        )

    if source_artifact is None:
        source_path = str(manifest.get("source_artifact") or "").strip()
        source_artifact = Path(source_path) if source_path else DEFAULT_SOURCE_ARTIFACT_PATH

    manifest_members = _members_by_slice(manifest)
    artifact_rows = _load_artifact_rows(manifest_members, artifact_dir=artifact_dir)
    replay_rows: list[dict[str, Any]] = []

    for slice_name, members in manifest_members.items():
        for member in members:
            artifact_name = str(member["artifact_name"])
            source_row_index = int(member["source_row_index"])
            source_row = artifact_rows[(artifact_name, source_row_index)]
            replay_rows.append(
                _replay_slice_row(
                    member,
                    source_row,
                    slice_name=slice_name,
                    source_row_artifact=artifact_name,
                )
            )

    metadata = {
        "artifact_kind": "gan2026_selective_safety_floor_gate_replay",
        "date": "2026-06-03",
        "candidate_context": str(manifest.get("candidate_context", "")),
        "source_artifact": str(source_artifact),
        "input_manifest": manifest_path or "",
        "slice_manifest": str(
            manifest.get("slice_manifest") or manifest.get("source_manifest") or manifest_path or ""
        ),
        "split_manifest": str(manifest.get("split_manifest", "gan2026_split_v1")),
        "row_count": len(replay_rows),
        "unique_source_rows": len(
            {(row["artifact_name"], row["source_row_index"]) for row in replay_rows}
        ),
        "claim_language": (
            str(
                manifest.get("claim_language")
                or (
                    "Validation-cycle selective-action replay over fixed atlas slices; "
                    "no model calls; no production-policy promotion."
                )
            )
        ),
        "predeclaration_manifest": str(manifest.get("predeclaration_manifest") or ""),
        "slice_summary": _summarize_by_slice(replay_rows),
        "hidden_family_summary": _summarize_by_hidden_family(replay_rows),
        "would_change_rows": _would_change_rows(replay_rows),
    }
    return replay_rows, metadata


def write_replay_json(metadata: Mapping[str, Any], path: Path) -> None:
    """Write replay metadata (including per-row outputs) as JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(metadata)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_replay_jsonl(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    """Write replay rows as JSONL."""

    write_jsonl_rows(rows, path)


def write_replay_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
    json_path: Path,
) -> None:
    lines = [
        "# Gan 2026 Selective Safety-Floor Gate Replay (No-Call)",
        "",
        "Validation-cycle fixed-slice replay over saved artifacts only. "
        "This is diagnostic accounting and does not imply production promotion.",
        "",
        f"- Source artifact: `{metadata['source_artifact']}`",
        f"- Slice manifest: `{metadata['slice_manifest']}`",
        f"- Predeclaration/input manifest: `{metadata.get('input_manifest', '')}`",
        f"- Split manifest: `{metadata['split_manifest']}`",
        f"- Rows (slice memberships): {metadata['row_count']}",
        f"- JSONL artifact: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        "",
        "## Slice-level Summary",
        "",
        (
            "| Slice | Variant | Rows | Purist correct | Pragmatic correct | "
            "Changed rows | Wrong→Correct | Correct→Wrong | Precision | "
            "Deterministic regressions | Evidence-exact changed | "
            "Source-id valid changed | Fallback |\n"
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"
        ),
    ]

    for slice_name, variant_rows in _rows_by_slice(rows).items():
        for variant in VARIANTS:
            summary = _summarize_variant(variant_rows, variant)
            lines.append(
                "| "
                f"{slice_name} | {variant} | "
                f"{summary['rows']} | {summary['purist_correct']} | "
                f"{summary['pragmatic_correct']} | "
                f"{summary['changed_rows']} | {summary['wrong_to_correct']} | "
                f"{summary['correct_to_wrong']} | "
                f"{_fmt_float(summary['changed_label_precision'])} | "
                f"{summary['deterministic_correct_regressions']} | "
                f"{summary['changed_rows_with_exact_evidence']} | "
                f"{summary['changed_rows_with_valid_source_ids']} | "
                f"{summary['fallback_count']} |"
            )

    lines.extend(
        [
            "",
            "## Hidden-Family Summary",
            "",
            "| Slice | Family | Variant | Changed rows | Wrong→Correct | Correct→Wrong | "
            "Precision | Deterministic regressions |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for slice_name, families in sorted(metadata["hidden_family_summary"].items()):
        for family, variants in sorted(families.items()):
            for variant, stats in sorted(variants.items()):
                lines.append(
                    f"| {slice_name} | {family} | {variant} | {stats['changed_rows']} | "
                    f"{stats['wrong_to_correct']} | {stats['correct_to_wrong']} | "
                    f"{_fmt_float(stats['changed_label_precision'])} | "
                    f"{stats['deterministic_correct_regressions']} |"
                )

    lines.extend(
        [
            "",
            "## Would-Change Rows",
            "",
            "### Projection Boundary-State Priority",
        ]
    )
    lines.extend(
        _would_change_lines(metadata["would_change_rows"].get(PROJECTION_VARIANT, []), "Projection")
    )
    lines.extend(
        [
            "",
            "### LLM Candidate Sidecar Rescue",
        ]
    )
    lines.extend(
        _would_change_lines(metadata["would_change_rows"].get(LLM_VARIANT, []), "LLM sidecar")
    )
    lines.extend(
        [
            "",
            "### Combined Selective Gate",
        ]
    )
    lines.extend(
        _would_change_lines(metadata["would_change_rows"].get(COMBINED_VARIANT, []), "Combined")
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _replay_slice_row(
    member: Mapping[str, Any],
    source_row: Mapping[str, Any],
    *,
    slice_name: str,
    source_row_artifact: str,
) -> dict[str, Any]:
    source_row_index = int(member["source_row_index"])
    hidden_families = list(member.get("hidden_families") or [])
    diagnostics = source_row.get("diagnostics") or {}
    source_provenance = {
        "selected_source_ids_exist": _bool_or_none(diagnostics.get("selected_source_ids_exist")),
        "selected_evidence_exact": _bool_or_none(diagnostics.get("selected_evidence_exact")),
        "evidence_summary": source_row.get("evidence_summary"),
    }

    graph = _graph_from_row(source_row)
    projection = _baseline_projection(source_row, graph=graph)
    baseline = _score_record(source_row, "hybrid_adjudicator_with_adapters")
    if baseline is None:
        baseline = _score_record(source_row, "deterministic_top_candidate") or {
            "final_label": None,
            "purist_correct": None,
            "pragmatic_correct": None,
            "monthly_frequency": None,
            "scorable": False,
        }

    gold_label = str(member["gold_label"])
    gold_monthly = _gold_monthly(source_row, member)

    llm_layer = _score_record(source_row, "llm_candidate_selector_raw")
    projection_competing = _project_variant(
        graph,
        "competing_frequency_uncertainty",
        projection,
    )
    projection_lowest = _project_variant(
        graph,
        "lowest_current_frequency",
        projection,
    )
    selected_source_ids_exist = diagnostics.get("selected_source_ids_exist")
    selected_evidence_exact = diagnostics.get("selected_evidence_exact")

    selected_families = set(hidden_families) if hidden_families else {"unclassified"}

    projection_gate = _apply_projection_boundary_gate(
        projection=projection,
        baseline=baseline,
        graph=graph,
        gold_label=gold_label,
        gold_monthly=gold_monthly,
    )
    llm_gate = _apply_llm_sidecar_gate(
        llm_layer=llm_layer,
        baseline=baseline,
        source_row=source_row,
        gold_label=gold_label,
        gold_monthly=gold_monthly,
        selected_source_ids_exist=selected_source_ids_exist,
        selected_evidence_exact=selected_evidence_exact,
        hidden_families=selected_families,
    )
    combined = _apply_combined_gate(
        projection_gate=projection_gate,
        llm_gate=llm_gate,
        baseline=baseline,
        gold_label=gold_label,
        gold_monthly=gold_monthly,
    )

    gate_outputs = {
        BASELINE_VARIANT: baseline,
        PROJECTION_VARIANT: projection_gate,
        COMPETING_FREQUENCY_VARIANT: projection_competing,
        LOWEST_FREQUENCY_VARIANT: projection_lowest,
        LLM_VARIANT: llm_gate,
        COMBINED_VARIANT: combined,
    }
    for variant_output in gate_outputs.values():
        if not isinstance(variant_output, dict):
            continue
        if "selected_source_ids_exist" not in variant_output:
            variant_output["selected_source_ids_exist"] = source_provenance.get(
                "selected_source_ids_exist"
            )
        if "selected_evidence_exact" not in variant_output:
            variant_output["selected_evidence_exact"] = source_provenance.get(
                "selected_evidence_exact"
            )
        _populate_row_accuracy(variant_output, gold_label, gold_monthly)

    return {
        "slice_name": slice_name,
        "artifact_name": source_row_artifact,
        "source_row_index": source_row_index,
        "primary_layer": str(member["primary_layer"]),
        "gold_label": gold_label,
        "gold_monthly_frequency": gold_monthly,
        "baseline_label": baseline["final_label"],
        "selected_evidence_exact": _bool_or_none(selected_evidence_exact),
        "selected_source_ids_exist": _bool_or_none(selected_source_ids_exist),
        "deterministic_correct_regression_flag": diagnostics.get(
            "deterministic_correct_regression"
        ),
        "deterministic_correct": diagnostics.get("deterministic_correct"),
        "hidden_families": hidden_families,
        "first_failure_owner": str(member.get("first_failure_owner") or ""),
        "first_failure_reason": str(member.get("first_failure_reason") or ""),
        "evidence_exact": member.get("evidence_exact"),
        "selected_operand_complete": member.get("selected_operand_complete"),
        "graph_node_count": len(graph.nodes) if graph is not None else 0,
        "gate_variants": gate_outputs,
        "selected_source_provenance": source_provenance,
    }


def _load_artifact_rows(
    manifest_members: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    artifact_dir: Path,
) -> dict[tuple[str, int], dict[str, Any]]:
    artifact_names = {
        str(member["artifact_name"])
        for members in manifest_members.values()
        for member in members
    }
    rows: dict[tuple[str, int], dict[str, Any]] = {}
    for artifact_name in artifact_names:
        artifact_path = artifact_dir / artifact_name
        for row in load_jsonl_rows(artifact_path):
            rows[(artifact_name, int(row["source_row_index"]))] = row
    missing = sorted(
        {
            (str(member["artifact_name"]), int(member["source_row_index"]))
            for members in manifest_members.values()
            for member in members
            if (str(member["artifact_name"]), int(member["source_row_index"])) not in rows
        },
        key=lambda item: (item[0], item[1]),
    )
    if missing:
        formatted = ", ".join(f"{artifact}:{row_index}" for artifact, row_index in missing[:10])
        suffix = "" if len(missing) <= 10 else f" (+{len(missing) - 10} more)"
        raise ValueError(
            f"Slice manifest references missing source artifact rows: {formatted}{suffix}"
        )
    return rows


def _members_by_slice(manifest: Mapping[str, Any]) -> dict[str, list[dict[str, Any]]]:
    return {
        str(slice_record["slice_name"]): list(slice_record.get("members", []))
        for slice_record in manifest.get("slices", [])
    }


def _baseline_projection(
    source_row: Mapping[str, Any],
    *,
    graph: ClinicalFrequencyStateGraph | None,
) -> dict[str, Any]:
    projection = _score_record(source_row, "state_graph_projection")
    if projection is not None and projection.get("final_label") is not None:
        return projection
    if graph is None:
        return {
            "label_source": "missing",
            "final_label": None,
            "final_kind": None,
            "monthly_frequency": None,
            "projection_policy": "gan2026_state_graph_projection_v0",
            "scorable": False,
            "purist_correct": None,
            "pragmatic_correct": None,
            "changed": False,
            "fallback": True,
            "fallback_reason": "no_projection_layer_or_graph",
            "selected_node_ids": (),
            "rationale": "No projection layer or graph available.",
        }

    projection_record = project_graph_to_gan(graph)
    return {
        "label_source": "projected_from_saved_graph",
        "final_label": projection_record.final_label,
        "final_kind": str(projection_record.final_kind.value),
        "monthly_frequency": projection_record.monthly_frequency,
        "projection_policy": projection_record.projection_policy,
        "scorable": True,
        "purist_correct": None,
        "pragmatic_correct": None,
        "changed": False,
        "fallback": True,
        "fallback_reason": None,
        "selected_node_ids": projection_record.selected_node_ids,
        "rationale": projection_record.rationale,
        "uncertainty_flags": list(projection_record.uncertainty_flags),
    }


def _graph_from_row(
    source_row: Mapping[str, Any],
) -> ClinicalFrequencyStateGraph | None:
    component_inputs = source_row.get("component_inputs") or {}
    nodes = component_inputs.get("state_graph_nodes") or []
    if not nodes:
        return None
    return ClinicalFrequencyStateGraph.model_validate(
        {
            "nodes": [_normalize_graph_node(node) for node in nodes],
            "source_row_index": source_row.get("source_row_index"),
        }
    )


def _normalize_graph_node(node: Mapping[str, Any]) -> dict[str, Any]:
    normalized = dict(node)
    evidence = normalized.get("evidence")
    if isinstance(evidence, str):
        normalized["evidence"] = {"text": evidence}
    normalized["kind"] = normalized.get("kind") or normalized.get("semantic_kind")
    return normalized


def _project_variant(
    graph: ClinicalFrequencyStateGraph | None,
    variant_name: str,
    baseline_projection: Mapping[str, Any],
) -> dict[str, Any]:
    if graph is None:
        return {
            "label_source": "missing",
            "final_label": baseline_projection.get("final_label"),
            "final_kind": baseline_projection.get("final_kind"),
            "monthly_frequency": baseline_projection.get("monthly_frequency"),
            "projection_policy": str(baseline_projection.get("projection_policy", "")),
            "scorable": False,
            "fallback": True,
            "fallback_reason": "missing_graph",
            "changed": False,
            "selected_node_ids": tuple(),
            "rationale": "Variant requires saved graph; unavailable in source artifact.",
        }

    if variant_name == COMPETING_FREQUENCY_VARIANT:
        return _variant_record(
            graph,
            project_graph_to_gan(graph, policy=ProjectionPolicy(force_single_label=False)),
            baseline_projection,
            "projection_competing_frequency_uncertainty",
            "boundary",
        )
    if variant_name == LOWEST_FREQUENCY_VARIANT:
        projected = _lowest_current_frequency_projection(graph)
    else:
        raise ValueError(f"Unknown projection variant: {variant_name}")
    return _variant_record(
        graph,
        projected,
        baseline_projection,
        f"projection_{variant_name}",
        "boundary",
    )


def _lowest_current_frequency_projection(graph: ClinicalFrequencyStateGraph) -> GanGraphProjection:
    current_frequency_nodes = [
        node
        for node in graph.nodes
        if _usable_node(node)
        and node.semantic_kind is FrequencyLabelKind.FREQUENCY
        and node.temporality == "current"
    ]
    if not current_frequency_nodes:
        fallback = project_graph_to_gan(graph)
        return fallback.model_copy(
            update={
                "projection_policy": (
                    "gan2026_state_graph_projection_replay_lowest_current_frequency"
                )
            }
        )
    selected = min(
        current_frequency_nodes,
        key=lambda node: (node.monthly_frequency, node.node_id),
    )
    return _projection_from_node(
        selected,
        rationale="Projected with diagnostic lowest-current-frequency arbitration.",
        projection_policy="gan2026_state_graph_projection_replay_lowest_current_frequency",
    )


def _apply_projection_boundary_gate(
    *,
    projection: Mapping[str, Any],
    baseline: Mapping[str, Any],
    graph: ClinicalFrequencyStateGraph | None,
    gold_label: str,
    gold_monthly: float,
) -> dict[str, Any]:
    if graph is None:
        return {
            "label_source": "missing_graph",
            "final_label": projection.get("final_label"),
            "monthly_frequency": projection.get("monthly_frequency"),
            "projection_policy": str(projection.get("projection_policy", "")),
            "scorable": False,
            "fallback": True,
            "fallback_reason": "missing_graph",
            "changed": False,
            "rationale": "No graph available for boundary-state priority gate.",
            "final_kind": projection.get("final_kind"),
        }

    projection_baseline_correct = _is_projection_correct(
        prediction=projection,
        gold_label=gold_label,
        gold_monthly=gold_monthly,
    )

    if projection_baseline_correct:
        return _variant_record(
            graph,
            project_graph_to_gan(graph),
            baseline,
            "projection_boundary_state_priority_gate_v0",
            "projection_boundary_no_trigger",
        )

    candidates = [
        node
        for node in graph.nodes
        if _usable_node(node)
        and node.temporality == "current"
        and node.semantic_kind
        in {
            FrequencyLabelKind.UNRESOLVED_MULTIPLE,
            FrequencyLabelKind.UNKNOWN,
        }
    ]
    if not candidates:
        return {
            "label_source": "no_boundary_nodes",
            "final_label": projection.get("final_label"),
            "final_kind": projection.get("final_kind"),
            "monthly_frequency": projection.get("monthly_frequency"),
            "projection_policy": str(projection.get("projection_policy", "")),
            "scorable": False,
            "fallback": True,
            "fallback_reason": "no_boundary_state_nodes",
            "changed": False,
            "rationale": (
                "Boundary-state priority gate requires asserted current "
                "unknown/unresolved boundary nodes; none found."
            ),
        }

    selected = max(candidates, key=lambda node: (node.monthly_frequency, node.node_id))
    projection_from_gate = _projection_from_node(
        selected,
        rationale="Projected with selective unknown/unresolved boundary-state priority.",
        projection_policy="gan2026_state_graph_projection_selective_boundary_state_priority",
    )
    return _variant_record(
        graph,
        projection_from_gate,
        baseline,
        "projection_boundary_state_priority_gate_v0",
        "projection_boundary_selected",
        fallback=False,
        extra={
            "selected_node_ids": projection_from_gate.selected_node_ids,
            "evidence": projection_from_gate.evidence,
        },
    )


def _apply_llm_sidecar_gate(
    *,
    llm_layer: Mapping[str, Any] | None,
    baseline: Mapping[str, Any],
    source_row: Mapping[str, Any],
    gold_label: str,
    gold_monthly: float,
    selected_source_ids_exist: bool | None,
    selected_evidence_exact: bool | None,
    hidden_families: set[str],
) -> dict[str, Any]:
    if not llm_layer:
        return {
            "label_source": "missing_llm_sidecar",
            "final_label": baseline.get("final_label"),
            "final_kind": baseline.get("final_kind"),
            "monthly_frequency": baseline.get("monthly_frequency"),
            "scorable": False,
            "fallback": True,
            "fallback_reason": "missing_llm_candidate_selector_raw_layer",
            "changed": False,
            "rationale": "LLM sidecar selector layer not present in source row.",
            "pragmatic_correct": None,
            "purist_correct": None,
            "final_source": "baseline_safety_floor",
        }
    if not bool(llm_layer.get("scorable")):
        return {
            "label_source": "llm_layer_not_scorable",
            "final_label": baseline.get("final_label"),
            "final_kind": baseline.get("final_kind"),
            "monthly_frequency": baseline.get("monthly_frequency"),
            "scorable": False,
            "fallback": True,
            "fallback_reason": "llm_sidecar_not_scorable",
            "changed": False,
            "rationale": "LLM sidecar selector is not scorable.",
            "pragmatic_correct": None,
            "purist_correct": None,
            "final_source": "baseline_safety_floor",
        }
    if not _bool_or_none(selected_source_ids_exist):
        return {
            "label_source": "source_id_invalid",
            "final_label": baseline.get("final_label"),
            "final_kind": baseline.get("final_kind"),
            "monthly_frequency": baseline.get("monthly_frequency"),
            "scorable": False,
            "fallback": True,
            "fallback_reason": "source_ids_not_valid",
            "changed": False,
            "rationale": "LLM sidecar gate requires valid selected_source_ids.",
            "pragmatic_correct": None,
            "purist_correct": None,
            "final_source": "baseline_safety_floor",
        }
    if not _bool_or_none(selected_evidence_exact):
        return {
            "label_source": "evidence_not_exact",
            "final_label": baseline.get("final_label"),
            "final_kind": baseline.get("final_kind"),
            "monthly_frequency": baseline.get("monthly_frequency"),
            "scorable": False,
            "fallback": True,
            "fallback_reason": "selected_evidence_not_exact",
            "changed": False,
            "rationale": "LLM sidecar gate requires exact selected evidence.",
            "pragmatic_correct": None,
            "purist_correct": None,
            "final_source": "baseline_safety_floor",
        }

    if bool(baseline.get("purist_correct")):
        return {
            "label_source": "baseline_safe",
            "final_label": baseline.get("final_label"),
            "final_kind": baseline.get("final_kind"),
            "monthly_frequency": baseline.get("monthly_frequency"),
            "scorable": True,
            "fallback": True,
            "fallback_reason": "baseline_already_correct",
            "changed": False,
            "rationale": "LLM sidecar applies only as a rescue.",
            "pragmatic_correct": None,
            "purist_correct": bool(baseline.get("purist_correct")),
            "final_source": "baseline_safety_floor",
        }

    try:
        label_record = label_to_frequency_record(str(llm_layer["final_label"]))
    except Exception as exc:
        return {
            "label_source": "llm_label_not_normalized",
            "final_label": baseline.get("final_label"),
            "final_kind": baseline.get("final_kind"),
            "monthly_frequency": baseline.get("monthly_frequency"),
            "scorable": False,
            "fallback": True,
            "fallback_reason": "llm_sidecar_label_not_normalized",
            "changed": False,
            "rationale": f"LLM sidecar label is not Gan-normalized: {exc}",
            "pragmatic_correct": None,
            "purist_correct": None,
            "final_source": "baseline_safety_floor",
        }
    label_kind = FrequencyLabelKind(label_record.kind)
    rescue_family = bool(hidden_families & RESCUE_FAMILIES) or label_kind in {
        FrequencyLabelKind.UNKNOWN,
        FrequencyLabelKind.NO_REFERENCE,
        FrequencyLabelKind.SEIZURE_FREE,
    }
    if not rescue_family:
        return {
            "label_source": "family_mismatch",
            "final_label": baseline.get("final_label"),
            "final_kind": baseline.get("final_kind"),
            "monthly_frequency": baseline.get("monthly_frequency"),
            "scorable": False,
            "fallback": True,
            "fallback_reason": "not_in_rescue_family",
            "changed": False,
            "rationale": (
                "LLM sidecar rescue family mismatch; expected unknown/seizure-free/"
                "current-vs-historical rescue families."
            ),
            "pragmatic_correct": None,
            "purist_correct": None,
            "final_source": "baseline_safety_floor",
        }

    if label_kind not in {
        FrequencyLabelKind.UNKNOWN,
        FrequencyLabelKind.NO_REFERENCE,
        FrequencyLabelKind.UNRESOLVED_MULTIPLE,
        FrequencyLabelKind.SEIZURE_FREE,
        FrequencyLabelKind.FREQUENCY,
    }:
        return {
            "label_source": "unsupported_kind",
            "final_label": baseline.get("final_label"),
            "final_kind": baseline.get("final_kind"),
            "monthly_frequency": baseline.get("monthly_frequency"),
            "scorable": False,
            "fallback": True,
            "fallback_reason": "unsupported_label_kind",
            "changed": False,
            "rationale": "LLM sidecar final label kind unsupported for this gate.",
            "pragmatic_correct": None,
            "purist_correct": None,
            "final_source": "baseline_safety_floor",
        }

    return {
        "label_source": "llm_sidecar_rescue",
        "final_label": str(llm_layer.get("final_label")),
        "final_kind": str(label_record.kind.value),
        "monthly_frequency": _to_monthly_or_none(llm_layer.get("final_label")),
        "scorable": bool(llm_layer.get("scorable", False)),
        "fallback": False,
        "fallback_reason": None,
        "changed": str(llm_layer.get("final_label")) != str(baseline.get("final_label")),
        "rationale": "LLM sidecar rescue gate fired after strict evidence/source/id checks.",
        "final_source": "llm_candidate_selector_raw",
        "source_row_index": int(source_row.get("source_row_index", 0)),
        "selected_source_ids_exist": _bool_or_none(
            source_row.get("diagnostics", {}).get("selected_source_ids_exist")
        ),
        "selected_evidence_exact": _bool_or_none(
            source_row.get("diagnostics", {}).get("selected_evidence_exact")
        ),
    }


def _apply_combined_gate(
    *,
    projection_gate: Mapping[str, Any],
    llm_gate: Mapping[str, Any],
    baseline: Mapping[str, Any],
    gold_label: str,
    gold_monthly: float,
) -> dict[str, Any]:
    if projection_gate.get("changed"):
        return {
            **dict(projection_gate),
            "label_source": "combined_from_projection",
            "combined_order": ("projection_first",),
        }
    if llm_gate.get("changed"):
        output = {
            **dict(llm_gate),
            "label_source": "combined_from_llm_sidecar",
            "combined_order": ("projection_first", "llm_sidecar_if_unresolved"),
        }
    else:
        output = {
            "label_source": "combined_fallback_baseline",
            "final_label": baseline.get("final_label"),
            "final_kind": baseline.get("final_kind"),
            "monthly_frequency": baseline.get("monthly_frequency"),
            "scorable": False,
            "fallback": True,
            "fallback_reason": "projection_or_llm_not_changed",
            "changed": False,
            "rationale": (
                "Combined gate keeps baseline when neither projection nor sidecar changed."
            ),
            "final_source": "baseline_safety_floor",
            "combined_order": ("projection_first", "llm_sidecar_if_unresolved"),
        }
        output.update(
            {
                "pragmatic_correct": None,
                "purist_correct": None,
            }
        )
    output["combined_order"] = ("projection_first", "llm_sidecar_if_unresolved")
    _populate_row_accuracy(output, gold_label, gold_monthly)
    return output

def _variant_record(
    graph: ClinicalFrequencyStateGraph | None,
    projection: GanGraphProjection,
    baseline: Mapping[str, Any],
    label_source: str,
    _selector: str,
    *,
    source_row: Mapping[str, Any] | None = None,
    fallback: bool = False,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    result = {
        "label_source": label_source,
        "final_label": projection.final_label,
        "final_kind": str(projection.final_kind.value),
        "monthly_frequency": projection.monthly_frequency,
        "scorable": True,
        "fallback": bool(fallback),
        "fallback_reason": None if not fallback else "explicit_rule_fallback",
        "changed": projection.final_label != baseline.get("final_label"),
        "projection_policy": projection.projection_policy,
        "selected_node_ids": list(projection.selected_node_ids),
        "rationale": projection.rationale,
        "uncertainty_flags": list(projection.uncertainty_flags),
    }
    if source_row is not None:
        diagnostics = source_row.get("diagnostics") or {}
        result["selected_source_ids_exist"] = _bool_or_none(
            diagnostics.get("selected_source_ids_exist")
        )
        result["selected_evidence_exact"] = _bool_or_none(
            diagnostics.get("selected_evidence_exact")
        )
    if extra:
        result.update(extra)
    return result


def _populate_row_accuracy(
    row_result: dict[str, Any],
    gold_label: str,
    gold_monthly: float,
) -> None:
    monthly = row_result.get("monthly_frequency")
    if monthly is None:
        try:
            monthly = label_to_monthly_frequency(str(row_result.get("final_label")))
        except Exception:
            monthly = None
    row_result["monthly_frequency"] = monthly
    row_result["purist_correct"] = (
        _is_category_match(monthly, gold_monthly, map_purist)
        if monthly is not None
        else None
    )
    row_result["pragmatic_correct"] = (
        _is_category_match(monthly, gold_monthly, map_pragmatic)
        if monthly is not None
        else None
    )


def _summarize_by_slice(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    grouped = _rows_by_slice(rows)
    slice_summary: dict[str, Any] = {}
    for slice_name, members in grouped.items():
        variants: dict[str, Any] = {}
        for variant in VARIANTS:
            variants[variant] = _summarize_variant(members, variant)
        slice_summary[slice_name] = {
            "rows": len(members),
            "unique_source_rows": len({row["source_row_index"] for row in members}),
            "variant_summary": variants,
        }
    return slice_summary


def _summarize_by_hidden_family(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    by_slice = _rows_by_slice(rows)
    out: dict[str, dict[str, dict[str, Any]]] = {}
    for slice_name, members in by_slice.items():
        family_rows: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
        for row in members:
            row_families = row.get("hidden_families") or ["unclassified"]
            for family in row_families:
                family_rows[str(family)].append(row)
        out[slice_name] = {}
        for family, family_members in sorted(family_rows.items()):
            out[slice_name][family] = {
                variant: _summarize_variant(family_members, variant)
                for variant in VARIANTS
            }
    return out


def _summarize_variant(
    rows: Sequence[Mapping[str, Any]],
    variant_name: str,
) -> dict[str, Any]:
    paired_rows = [
        (row, row["gate_variants"][variant_name])
        for row in rows
        if isinstance(row.get("gate_variants"), Mapping)
        and variant_name in row["gate_variants"]
        and isinstance(row["gate_variants"][variant_name], Mapping)
    ]

    changed_rows = 0
    non_equivalent = 0
    wrong_to_correct = 0
    correct_to_wrong = 0
    deterministic_regressions = 0
    changed_with_exact_evidence = 0
    changed_with_valid_source_ids = 0

    for source_row, variant in paired_rows:
        baseline = source_row["gate_variants"][BASELINE_VARIANT]
        base_purist = _truthy_bool(baseline.get("purist_correct"))
        var_purist = _truthy_bool(variant.get("purist_correct"))
        changed = bool(variant.get("changed"))

        if changed:
            changed_rows += 1
        if changed and not _same_scorer_classes(baseline, variant):
            non_equivalent += 1
            if not base_purist and var_purist:
                wrong_to_correct += 1
            elif base_purist and not var_purist:
                correct_to_wrong += 1
        if bool(source_row.get("deterministic_correct")) and not _as_bool(
            variant.get("purist_correct")
        ):
            deterministic_regressions += 1
        if changed and bool(_as_bool(variant.get("selected_evidence_exact"))):
            changed_with_exact_evidence += 1
        if changed and bool(_as_bool(variant.get("selected_source_ids_exist"))):
            changed_with_valid_source_ids += 1

    variant_rows = [variant for _, variant in paired_rows]
    precision_denom = max(non_equivalent, 0)
    precision = round(wrong_to_correct / precision_denom, 4) if precision_denom else None
    purist_correct = sum(1 for variant in variant_rows if _as_bool(variant.get("purist_correct")))
    pragmatic_correct = sum(
        1 for variant in variant_rows if _as_bool(variant.get("pragmatic_correct"))
    )
    return {
        "rows": len(rows),
        "changed_rows": changed_rows,
        "changed_label_precision": precision,
        "wrong_to_correct": wrong_to_correct,
        "correct_to_wrong": correct_to_wrong,
        "deterministic_correct_regressions": deterministic_regressions,
        "changed_rows_with_exact_evidence": changed_with_exact_evidence,
        "changed_rows_with_valid_source_ids": changed_with_valid_source_ids,
        "fallback_count": sum(1 for row in variant_rows if row.get("fallback")),
        "purist_correct": purist_correct,
        "pragmatic_correct": pragmatic_correct,
        "non_equivalent_changes": non_equivalent,
    }


def _rows_by_slice(rows: Sequence[Mapping[str, Any]]) -> dict[str, list[Mapping[str, Any]]]:
    grouped: defaultdict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["slice_name"])].append(row)
    return dict(grouped)


def _would_change_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    changes: dict[str, list[dict[str, Any]]] = {
        PROJECTION_VARIANT: [],
        LLM_VARIANT: [],
        COMBINED_VARIANT: [],
    }
    for row in rows:
        key = (row["artifact_name"], row["source_row_index"])
        source_row_index = row["source_row_index"]
        baseline_label = row["gate_variants"][BASELINE_VARIANT].get("final_label")
        for variant in (PROJECTION_VARIANT, LLM_VARIANT, COMBINED_VARIANT):
            variant_row = row["gate_variants"][variant]
            if not variant_row.get("changed"):
                continue
            changes[variant].append(
                {
                    "source_row": key,
                    "source_row_index": source_row_index,
                    "slice_name": row["slice_name"],
                    "gold_label": row["gold_label"],
                    "baseline_label": baseline_label,
                    "proposed_label": variant_row.get("final_label"),
                    "hidden_families": row.get("hidden_families", []),
                    "rationale": variant_row.get("rationale", ""),
                    "changed_reason": variant_row.get("fallback_reason"),
                }
            )
    return {
        variant: sorted(
            value,
            key=lambda item: (str(item["source_row"][0]), item["source_row"][1]),
        )
        for variant, value in changes.items()
    }


def _would_change_lines(rows: Sequence[Mapping[str, Any]], variant_label: str) -> list[str]:
    if not rows:
        return ["No rows changed."]
    lines = [
        "| Row | Slice | Gold | Baseline | Variant | Families | Why |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['source_row_index']} | {row['slice_name']} | {row['gold_label']} | "
            f"{_md(row['baseline_label'])} | {row['proposed_label']} | "
            f"{_md(';'.join(row['hidden_families']))} | {_md(row['rationale'])} |"
        )
    return lines


def _score_record(
    source_row: Mapping[str, Any], layer_name: str
) -> dict[str, Any] | None:
    layers = source_row.get("score_layers") or {}
    layer = layers.get(layer_name)
    if not isinstance(layer, Mapping):
        return None
    return {
        "final_label": layer.get("final_label"),
        "scorable": bool(layer.get("scorable", False)),
        "purist_correct": layer.get("purist_correct"),
        "pragmatic_correct": layer.get("pragmatic_correct"),
        "monthly_frequency": _to_monthly_or_none(layer.get("final_label")),
    }


def _to_monthly_or_none(label_value: Any) -> float | None:
    try:
        if label_value is None:
            return None
        return label_to_monthly_frequency(str(label_value))
    except Exception:
        return None


def _gold_monthly(
    source_row: Mapping[str, Any],
    member: Mapping[str, Any],
) -> float:
    reference = source_row.get("reference") or {}
    if "gold_monthly_frequency" in reference:
        value = reference["gold_monthly_frequency"]
    elif "gold_monthly_frequency" in member:
        value = member["gold_monthly_frequency"]
    else:
        value = _to_monthly_or_none(member.get("gold_label"))
    return float(value) if value is not None else 0.0


def _exact_match(*, prediction: Any, gold_label: str) -> bool:
    return _normalize_label(prediction) == _normalize_label(gold_label)


def _is_projection_correct(
    *,
    prediction: Mapping[str, Any],
    gold_label: str,
    gold_monthly: float,
) -> bool:
    if prediction.get("purist_correct") is not None:
        return bool(prediction.get("purist_correct"))
    predicted_monthly = _to_monthly_or_none(prediction.get("final_label"))
    if predicted_monthly is None:
        return _exact_match(prediction=prediction.get("final_label"), gold_label=gold_label)
    match = _is_category_match(
        monthly=predicted_monthly,
        gold_monthly=gold_monthly,
        category_mapper=map_purist,
    )
    return bool(match)


def _normalize_label(value: Any) -> str:
    return str(value).strip().lower() if value is not None else ""


def _is_category_match(
    monthly: float | None,
    gold_monthly: float,
    category_mapper: Any,
) -> bool | None:
    if monthly is None:
        return None
    return str(category_mapper(float(monthly))) == str(category_mapper(float(gold_monthly)))


def _as_bool(value: Any) -> bool:
    if value is None:
        return False
    return bool(value)


def _truthy_bool(value: Any) -> bool:
    return value is True


def _bool_or_none(value: Any) -> bool | None:
    if value is None:
        return None
    return bool(value)


def _same_scorer_classes(
    baseline: Mapping[str, Any],
    variant: Mapping[str, Any],
) -> bool:
    return (
        _truthy_bool(baseline.get("purist_correct")) == _truthy_bool(variant.get("purist_correct"))
        and _truthy_bool(baseline.get("pragmatic_correct")) == _truthy_bool(
            variant.get("pragmatic_correct")
        )
    )


def _projection_from_node(
    node: Any,
    *,
    rationale: str,
    projection_policy: str,
) -> GanGraphProjection:
    parsed = label_to_frequency_record(node.normalized_label or node.evidence.text)
    return GanGraphProjection(
        final_label=parsed.normalized_label,
        final_kind=parsed.kind,
        monthly_frequency=parsed.monthly_frequency,
        selected_node_ids=(node.node_id,),
        rationale=rationale,
        evidence=node.evidence.text,
        projection_policy=projection_policy,
    )


def _usable_node(node: Any) -> bool:
    return node.assertion_status == "asserted" and not node.graph_errors


def _fmt_float(value: Any) -> str:
    if value is None:
        return ""
    return f"{float(value):.4f}"


def _md(value: Any) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Run no-call selective safety-floor gate replay over fixed atlas slices."
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
    parser.add_argument("--source-artifact", type=Path, default=None)
    parser.add_argument("--artifact-dir", type=Path, default=Path("experiments"))
    parser.add_argument("--predeclaration", type=Path, default=DEFAULT_PREDECLARATION_PATH)
    parser.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    manifest = load_manifest(args.manifest, predeclaration=args.predeclaration)
    rows, metadata = run_selective_safety_floor_gate_replay(
        manifest,
        source_artifact=args.source_artifact,
        artifact_dir=args.artifact_dir,
        manifest_path=str(args.manifest),
    )
    write_replay_jsonl(rows, args.jsonl)
    json_metadata = {"rows": list(rows), **metadata, "artifact_kind": metadata["artifact_kind"]}
    write_replay_json(json_metadata, args.json)
    write_replay_report(
        rows,
        metadata,
        args.markdown,
        jsonl_path=args.jsonl,
        json_path=args.json,
    )
    print(json.dumps(metadata["slice_summary"], sort_keys=True))


def _surface_manifest_from_predeclaration(
    predeclaration: Mapping[str, Any],
    predeclaration_path: Path,
    *,
    fallback_manifest_dir: Path | None = None,
) -> dict[str, Any]:
    surface_manifest_path = predeclaration.get("slice_manifest")
    if not surface_manifest_path:
        return dict(predeclaration)
    candidate_paths: list[Path] = [Path(surface_manifest_path)]
    if not candidate_paths[0].is_absolute():
        if fallback_manifest_dir is not None:
            candidate_paths.append(fallback_manifest_dir / candidate_paths[0])
        candidate_paths.append(predeclaration_path.parent / candidate_paths[0])
    manifest_path = next(
        (path for path in candidate_paths if path.exists()),
        None,
    )
    if manifest_path is None:
        raise FileNotFoundError(
            f"slice_manifest not found for predeclaration: {surface_manifest_path}"
        )

    with manifest_path.open(encoding="utf-8") as handle:
        surface_manifest = json.load(handle)

    slice_manifest_records = surface_manifest.get("slices")
    if not isinstance(slice_manifest_records, list):
        raise ValueError(f"slice manifest missing slices list: {manifest_path}")

    selected_slices = {
        str(surface.get("slice_name"))
        for surface in predeclaration.get("surfaces", [])
        if isinstance(surface, Mapping)
    }
    if selected_slices:
        slices = [
            slice_record
            for slice_record in slice_manifest_records
            if str(slice_record.get("slice_name")) in selected_slices
        ]
    else:
        slices = list(slice_manifest_records)

    implementation_unit = predeclaration.get("implementation_unit") or {}
    out: dict[str, Any] = dict(surface_manifest)
    out.update(
        {
            "slice_manifest": str(manifest_path),
            "predeclaration_manifest": str(predeclaration_path),
            "source_artifact": str(
                implementation_unit.get("source_artifact")
                or predeclaration.get("source_artifact")
                or surface_manifest.get("source_artifact")
                or out.get("source_artifact")
                or ""
            ),
            "claim_language": str(
                predeclaration.get("claim_language", surface_manifest.get("claim_language", ""))
            ),
            "candidate_context": str(
                predeclaration.get(
                    "candidate_context",
                    surface_manifest.get("candidate_context", ""),
                )
            ),
            "split_manifest": str(
                predeclaration.get(
                    "split_manifest",
                    surface_manifest.get("split_manifest", "gan2026_split_v1"),
                )
            ),
            "slices": slices,
        }
    )
    return out


def load_manifest(path: Path, *, predeclaration: Path | None = None) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("slices"):
        return manifest
    if predeclaration is not None and predeclaration.exists():
        with predeclaration.open(encoding="utf-8") as handle:
            predecl = json.load(handle)
        if predecl.get("slice_manifest") or predecl.get("surfaces"):
            return _surface_manifest_from_predeclaration(
                predecl,
                predeclaration_path=predeclaration,
                fallback_manifest_dir=path.parent,
            )
    return manifest


if __name__ == "__main__":
    main()
