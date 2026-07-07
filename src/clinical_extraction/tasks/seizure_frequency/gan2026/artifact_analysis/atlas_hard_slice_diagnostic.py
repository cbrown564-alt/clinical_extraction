"""No-call diagnostics over atlas-derived Gan 2026 hard slices."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    projection_arbitration_ablation,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

DEFAULT_MANIFEST_PATH = Path(
    "experiments/gan2026_atlas_candidate_generation_projection_hard_slices_2026-06-03.json"
)
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_atlas_candidate_generation_projection_hard_slice_diagnostic_2026-06-03.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_atlas_candidate_generation_projection_hard_slice_diagnostic_2026-06-03.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_atlas_candidate_generation_projection_hard_slice_diagnostic_2026-06-03.md"
)

SCORE_LAYERS = (
    "deterministic_top_candidate",
    "llm_candidate_selector_raw",
    "state_graph_projection",
    "hybrid_adjudicator_raw",
    "hybrid_adjudicator_with_adapters",
    "raw_model_clinical_selection",
    "mechanical_adapter_label",
    "benchmark_convention_adapter",
    "final_projected_label",
)


def load_manifest(path: Path = DEFAULT_MANIFEST_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_atlas_hard_slice_diagnostic(
    manifest: Mapping[str, Any],
    *,
    artifact_dir: Path = Path("experiments"),
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Replay fixed atlas slices against saved artifacts without model calls."""

    artifact_rows = _load_artifact_rows(manifest, artifact_dir=artifact_dir)
    diagnostic_rows: list[dict[str, Any]] = []
    projection_inputs: list[dict[str, Any]] = []
    projection_input_keys: list[tuple[str, int, str]] = []

    for slice_record in manifest.get("slices", []):
        slice_name = str(slice_record["slice_name"])
        for member in slice_record.get("members", []):
            key = (str(member["artifact_name"]), int(member["source_row_index"]))
            source_row = artifact_rows[key]
            diagnostic = _diagnostic_row(slice_name, member, source_row)
            diagnostic_rows.append(diagnostic)
            projection_input = _projection_input_for_row(diagnostic, source_row)
            if projection_input is not None:
                projection_inputs.append(projection_input)
                projection_input_keys.append((slice_name, key[1], key[0]))

    projection_by_key: dict[tuple[str, int, str], Mapping[str, Any]] = {}
    projection_metadata: Mapping[str, Any] = {}
    if projection_inputs:
        projection_rows, projection_metadata = (
            projection_arbitration_ablation.run_projection_arbitration_ablation(
                projection_inputs,
                split="validation_hard_slices",
                split_manifest=str(manifest.get("split_manifest", "gan2026_split_v1")),
            )
        )
        projection_by_key = {
            key: row for key, row in zip(projection_input_keys, projection_rows, strict=True)
        }

    for diagnostic in diagnostic_rows:
        key = (
            diagnostic["slice_name"],
            diagnostic["source_row_index"],
            diagnostic["artifact_name"],
        )
        projection = projection_by_key.get(key)
        if projection:
            diagnostic["projection_arbitration"] = projection["variant_results"]
            diagnostic["projection_graph_node_count"] = projection["graph_node_count"]

    metadata = {
        "artifact_kind": "gan2026_atlas_hard_slice_no_call_diagnostic",
        "date": "2026-06-03",
        "source_manifest": manifest.get("source_atlas_csv"),
        "hard_slice_manifest_kind": manifest.get("artifact_kind"),
        "split_manifest": manifest.get("split_manifest", "gan2026_split_v1"),
        "row_count": len(diagnostic_rows),
        "unique_source_rows": len(
            {(row["artifact_name"], row["source_row_index"]) for row in diagnostic_rows}
        ),
        "claim_language": (
            "Diagnostic validation-cycle no-call replay over saved artifacts; not a benchmark, "
            "holdout, prompt-change, scorer-change, or production-policy promotion."
        ),
        "projection_variants": projection_metadata.get("projection_variants", {}),
        "summary": _summary(diagnostic_rows),
        "would_change_rows": _would_change_rows(diagnostic_rows),
    }
    return diagnostic_rows, metadata


def write_diagnostic_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_diagnostic_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
    json_path: Path,
) -> None:
    summary = metadata["summary"]
    lines = [
        "# Gan 2026 Atlas Hard-Slice No-Call Diagnostic",
        "",
        "Diagnostic validation-cycle replay over saved artifacts. This does not change the "
        "pipeline, scorer, prompts, graph projection policy, or holdout status.",
        "",
        f"- Split manifest: `{metadata['split_manifest']}`",
        f"- Rows: {metadata['row_count']} slice memberships",
        f"- Unique source rows: {metadata['unique_source_rows']}",
        f"- JSONL artifact: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        "",
        "## Slice Summary",
        "",
        "| Slice | Rows | Baseline correct | LLM sidecar scorable | LLM sidecar correct | "
        "LLM rescues | Graph replay rows | Best projection corrections | "
        "Projection regressions |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for slice_name, stats in sorted(summary["slices"].items()):
        lines.append(
            f"| `{slice_name}` | {stats['rows']} | {stats['baseline_correct']} | "
            f"{stats['llm_sidecar_scorable']} | {stats['llm_sidecar_correct']} | "
            f"{stats['llm_sidecar_rescues']} | {stats['graph_projection_replay_rows']} | "
            f"{stats['best_non_oracle_projection_corrections']} | "
            f"{stats['baseline_correct_to_projection_wrong']} |"
        )

    lines.extend(
        [
            "",
            "## Projection Variants",
            "",
            "| Variant | Rows | Exact | Corrections vs baseline | Regressions vs baseline |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for variant, stats in sorted(summary["projection_variants"].items()):
        lines.append(
            f"| `{variant}` | {stats.get('rows', 0)} | {stats.get('exact', 0)} | "
            f"{stats.get('baseline_wrong_to_variant_correct', 0)} | "
            f"{stats.get('baseline_correct_to_variant_wrong', 0)} |"
        )

    lines.extend(_would_change_report_lines(metadata["would_change_rows"]))
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            _interpret(summary),
            "",
            "The candidate-generation sidecar signal is useful diagnostically where the saved "
            "LLM candidate selector is scorable and correct, but it is not promoted into the "
            "final label here. Projection rows are replayed only when the saved artifact contains "
            "state-graph nodes; Decision 0007 final-projection misses remain counted as "
            "projection-family rows but are not graph-arbitration replays.",
            "",
            "## Interpretation Required After Generation",
            "",
            "The tables above are generated mechanically from saved artifacts. A human reviewer "
            "must add post-hoc interpretation before any candidate change is predeclared or "
            "implemented: verify whether each proposed changed row reflects a portable clinical "
            "mechanism, a Gan-specific convention, scorer-category equivalence rather than exact "
            "label equivalence, or an artifact of saved sidecar/projection diagnostics. Do not "
            "promote any row-level change from this report alone.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _load_artifact_rows(
    manifest: Mapping[str, Any],
    *,
    artifact_dir: Path,
) -> dict[tuple[str, int], dict[str, Any]]:
    artifact_names = {
        str(member["artifact_name"])
        for slice_record in manifest.get("slices", [])
        for member in slice_record.get("members", [])
    }
    rows: dict[tuple[str, int], dict[str, Any]] = {}
    for artifact_name in artifact_names:
        artifact_path = artifact_dir / artifact_name
        for row in load_jsonl_rows(artifact_path):
            rows[(artifact_name, int(row["source_row_index"]))] = row
    return rows


def _diagnostic_row(
    slice_name: str,
    member: Mapping[str, Any],
    source_row: Mapping[str, Any],
) -> dict[str, Any]:
    primary_layer = str(member["primary_layer"])
    scores = {
        layer_name: _score_summary(source_row, layer_name)
        for layer_name in SCORE_LAYERS
        if layer_name in (source_row.get("score_layers") or {})
    }
    baseline = scores.get(primary_layer, {})
    llm_sidecar = scores.get("llm_candidate_selector_raw", {})
    deterministic = scores.get("deterministic_top_candidate", {})
    diagnostics = source_row.get("diagnostics") or {}
    return {
        "slice_name": slice_name,
        "artifact_name": str(member["artifact_name"]),
        "source_row_index": int(member["source_row_index"]),
        "primary_layer": primary_layer,
        "gold_label": str(member["gold_label"]),
        "baseline_label": str(member["predicted_label"]),
        "baseline_correct": bool(baseline.get("purist_correct", False)),
        "hidden_families": list(member.get("hidden_families") or []),
        "first_failure_owner": str(member["first_failure_owner"]),
        "first_failure_reason": str(member["first_failure_reason"]),
        "evidence_exact": member.get("evidence_exact"),
        "selected_operand_complete": member.get("selected_operand_complete"),
        "deterministic_correct": _correct_or_none(deterministic, diagnostics),
        "llm_candidate_selector_scorable": bool(llm_sidecar.get("scorable", False)),
        "llm_candidate_selector_correct": _correct_or_none(
            llm_sidecar,
            {"llm_candidate_correct": diagnostics.get("llm_candidate_correct")},
            diagnostic_key="llm_candidate_correct",
        ),
        "llm_candidate_selector_label": llm_sidecar.get("final_label"),
        "llm_candidate_rescue": (
            _correct_or_none(deterministic, diagnostics) is False
            and _correct_or_none(
                llm_sidecar,
                {"llm_candidate_correct": diagnostics.get("llm_candidate_correct")},
                diagnostic_key="llm_candidate_correct",
            )
            is True
        ),
        "score_layers": scores,
        "decision_repairs": list(diagnostics.get("decision_repairs") or []),
        "selected_source_ids_exist": diagnostics.get("selected_source_ids_exist"),
    }


def _score_summary(row: Mapping[str, Any], layer_name: str) -> dict[str, Any]:
    layer = (row.get("score_layers") or {}).get(layer_name) or {}
    return {
        "final_label": layer.get("final_label"),
        "scorable": bool(layer.get("scorable", False)),
        "purist_correct": layer.get("purist_correct"),
        "pragmatic_correct": layer.get("pragmatic_correct"),
        "predicted_monthly_frequency": layer.get("predicted_monthly_frequency"),
        "error": layer.get("error"),
    }


def _correct_or_none(
    score: Mapping[str, Any],
    diagnostics: Mapping[str, Any],
    *,
    diagnostic_key: str = "deterministic_correct",
) -> bool | None:
    if "purist_correct" in score and score.get("purist_correct") is not None:
        return bool(score["purist_correct"])
    if diagnostic_key in diagnostics and diagnostics.get(diagnostic_key) is not None:
        return bool(diagnostics[diagnostic_key])
    return None


def _projection_input_for_row(
    diagnostic: Mapping[str, Any],
    source_row: Mapping[str, Any],
) -> dict[str, Any] | None:
    graph = _graph_from_hybrid_row(source_row)
    if graph is None:
        return None
    reference = source_row.get("reference") or {}
    parsed = label_to_frequency_record(str(diagnostic["gold_label"]))
    return {
        "source_row_index": diagnostic["source_row_index"],
        "source": diagnostic["slice_name"],
        "source_artifact": diagnostic["artifact_name"],
        "gold_normalized_label": diagnostic["gold_label"],
        "gold_label_kind": reference.get("gold_label_kind") or parsed.kind.value,
        "gold_monthly_frequency": reference.get("gold_monthly_frequency")
        or parsed.monthly_frequency,
        "graph": graph,
        "baseline_projection_label": diagnostic["baseline_label"],
        "failure_family": diagnostic["first_failure_owner"],
    }


def _graph_from_hybrid_row(row: Mapping[str, Any]) -> dict[str, Any] | None:
    component_inputs = row.get("component_inputs") or {}
    nodes = component_inputs.get("state_graph_nodes") or []
    if not nodes:
        return None
    return {
        "source_row_index": row.get("source_row_index"),
        "nodes": [_graph_node(node) for node in nodes],
    }


def _graph_node(node: Mapping[str, Any]) -> dict[str, Any]:
    converted = dict(node)
    evidence = converted.get("evidence")
    if isinstance(evidence, str):
        converted["evidence"] = {"text": evidence}
    return converted


def _summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    by_slice: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        by_slice[str(row["slice_name"])].append(row)
    projection_variants: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        projection = row.get("projection_arbitration") or {}
        baseline_correct = bool((projection.get("baseline_v0") or {}).get("correct"))
        for variant, result in projection.items():
            projection_variants[variant]["rows"] += 1
            if result.get("correct"):
                projection_variants[variant]["exact"] += 1
            if not baseline_correct and result.get("correct"):
                projection_variants[variant]["baseline_wrong_to_variant_correct"] += 1
            if baseline_correct and not result.get("correct"):
                projection_variants[variant]["baseline_correct_to_variant_wrong"] += 1
    return {
        "slices": {
            slice_name: _slice_summary(slice_rows)
            for slice_name, slice_rows in sorted(by_slice.items())
        },
        "first_failure_owners": dict(Counter(str(row["first_failure_owner"]) for row in rows)),
        "projection_variants": {
            variant: {
                "rows": counts.get("rows", 0),
                "exact": counts.get("exact", 0),
                "baseline_wrong_to_variant_correct": counts.get(
                    "baseline_wrong_to_variant_correct", 0
                ),
                "baseline_correct_to_variant_wrong": counts.get(
                    "baseline_correct_to_variant_wrong", 0
                ),
            }
            for variant, counts in sorted(projection_variants.items())
        },
    }


def _would_change_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    llm_rows: dict[tuple[str, int], dict[str, Any]] = {}
    projection_rows: dict[tuple[str, int], dict[str, Any]] = {}
    for row in rows:
        key = (str(row["artifact_name"]), int(row["source_row_index"]))
        if row.get("llm_candidate_rescue") is True:
            llm_rows.setdefault(key, _llm_would_change_row(row))
        projection_changes = _correct_non_oracle_projection_variants(row)
        if projection_changes:
            existing = projection_rows.get(key)
            current = _projection_would_change_row(row, projection_changes)
            if existing is None:
                projection_rows[key] = current
            else:
                existing["correct_variants"].update(current["correct_variants"])
                existing["variant_evidence"].update(current["variant_evidence"])
                existing["slice_names"] = sorted(
                    set(existing["slice_names"]) | set(current["slice_names"])
                )
    return {
        "llm_candidate_sidecar_rescues": sorted(
            llm_rows.values(), key=lambda item: item["source_row_index"]
        ),
        "projection_variant_corrections": sorted(
            projection_rows.values(), key=lambda item: item["source_row_index"]
        ),
    }


def _llm_would_change_row(row: Mapping[str, Any]) -> dict[str, Any]:
    scores = row.get("score_layers") or {}
    deterministic = scores.get("deterministic_top_candidate") or {}
    return {
        "source_row_index": row["source_row_index"],
        "artifact_name": row["artifact_name"],
        "slice_names": [row["slice_name"]],
        "gold_label": row["gold_label"],
        "current_final_label": row["baseline_label"],
        "deterministic_label": deterministic.get("final_label"),
        "llm_sidecar_label": row.get("llm_candidate_selector_label"),
        "llm_sidecar_purist_correct": row.get("llm_candidate_selector_correct"),
        "hidden_families": row.get("hidden_families", []),
        "why": (
            "LLM candidate selector raw layer is Purist-correct while deterministic "
            "safety-floor final label is Purist-wrong."
        ),
    }


def _projection_would_change_row(
    row: Mapping[str, Any],
    projection_changes: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    projection = row.get("projection_arbitration") or {}
    return {
        "source_row_index": row["source_row_index"],
        "artifact_name": row["artifact_name"],
        "slice_names": [row["slice_name"]],
        "gold_label": row["gold_label"],
        "current_final_label": row["baseline_label"],
        "graph_baseline_label": (projection.get("baseline_v0") or {}).get("final_label"),
        "correct_variants": {
            variant: result.get("final_label")
            for variant, result in sorted(projection_changes.items())
        },
        "variant_evidence": {
            variant: result.get("evidence")
            for variant, result in sorted(projection_changes.items())
        },
        "hidden_families": row.get("hidden_families", []),
        "why": (
            "Saved state graph contains a gold-compatible node; a named non-oracle "
            "projection variant selects it."
        ),
    }


def _correct_non_oracle_projection_variants(
    row: Mapping[str, Any],
) -> dict[str, Mapping[str, Any]]:
    projection = row.get("projection_arbitration") or {}
    return {
        variant: result
        for variant, result in projection.items()
        if variant != "oracle_gold_node" and bool(result.get("correct"))
    }


def _would_change_report_lines(
    would_change: Mapping[str, Sequence[Mapping[str, Any]]],
) -> list[str]:
    llm_rows = list(would_change.get("llm_candidate_sidecar_rescues", []))
    projection_rows = list(would_change.get("projection_variant_corrections", []))
    lines = [
        "",
        "## Rows That Would Change",
        "",
        "These rows are generated from diagnostic sidecars and ablation variants. They describe "
        "what would change under a hypothetical gate or projection variant; they are not current "
        "production-policy changes.",
        "",
        "### LLM Candidate Sidecar Rescues",
        "",
        "| Row | Gold | Current final | Deterministic label | LLM sidecar | Families | Why |",
        "| ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for row in llm_rows:
        lines.append(
            f"| {row['source_row_index']} | `{_md(row['gold_label'])}` | "
            f"`{_md(row['current_final_label'])}` | `{_md(row.get('deterministic_label'))}` | "
            f"`{_md(row.get('llm_sidecar_label'))}` | "
            f"{_md(';'.join(row.get('hidden_families', [])))} | {_md(row['why'])} |"
        )

    lines.extend(
        [
            "",
            "### Projection Variant Corrections",
            "",
            "| Row | Gold | Current final | Graph baseline | Correct variant output | "
            "Variant evidence | Families | Why |",
            "| ---: | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in projection_rows:
        variant_output = "; ".join(
            f"{variant}: {label}" for variant, label in row["correct_variants"].items()
        )
        variant_evidence = "; ".join(
            f"{variant}: {evidence}" for variant, evidence in row["variant_evidence"].items()
        )
        lines.append(
            f"| {row['source_row_index']} | `{_md(row['gold_label'])}` | "
            f"`{_md(row['current_final_label'])}` | "
            f"`{_md(row.get('graph_baseline_label'))}` | `{_md(variant_output)}` | "
            f"{_md(variant_evidence)} | {_md(';'.join(row.get('hidden_families', [])))} | "
            f"{_md(row['why'])} |"
        )
    return lines


def _md(value: Any) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def _slice_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    graph_rows = [row for row in rows if row.get("projection_arbitration")]
    return {
        "rows": len(rows),
        "baseline_correct": sum(bool(row["baseline_correct"]) for row in rows),
        "deterministic_correct": sum(row.get("deterministic_correct") is True for row in rows),
        "llm_sidecar_scorable": sum(bool(row["llm_candidate_selector_scorable"]) for row in rows),
        "llm_sidecar_correct": sum(
            row.get("llm_candidate_selector_correct") is True for row in rows
        ),
        "llm_sidecar_rescues": sum(bool(row["llm_candidate_rescue"]) for row in rows),
        "graph_projection_replay_rows": len(graph_rows),
        "best_non_oracle_projection_corrections": sum(
            _has_non_oracle_projection_correction(row) for row in graph_rows
        ),
        "baseline_correct_to_projection_wrong": sum(
            _has_non_oracle_projection_regression(row) for row in graph_rows
        ),
        "evidence_exact": sum(row.get("evidence_exact") is True for row in rows),
        "source_ids_valid": sum(row.get("selected_source_ids_exist") is True for row in rows),
    }


def _has_non_oracle_projection_correction(row: Mapping[str, Any]) -> bool:
    projection = row.get("projection_arbitration") or {}
    baseline_correct = bool((projection.get("baseline_v0") or {}).get("correct"))
    return (not baseline_correct) and any(
        bool(result.get("correct"))
        for variant, result in projection.items()
        if variant != "oracle_gold_node"
    )


def _has_non_oracle_projection_regression(row: Mapping[str, Any]) -> bool:
    projection = row.get("projection_arbitration") or {}
    baseline_correct = bool((projection.get("baseline_v0") or {}).get("correct"))
    return baseline_correct and any(
        not bool(result.get("correct"))
        for variant, result in projection.items()
        if variant != "oracle_gold_node"
    )


def _interpret(summary: Mapping[str, Any]) -> str:
    candidate = summary["slices"].get("candidate_generation_rescue", {})
    projection = summary["slices"].get("projection_arbitration", {})
    return (
        "Saved sidecars show "
        f"{candidate.get('llm_sidecar_rescues', 0)} LLM-candidate rescues on the "
        "candidate-generation rescue slice, while graph projection replay supplies "
        f"{projection.get('best_non_oracle_projection_corrections', 0)} non-oracle "
        "projection corrections on the projection-arbitration slice. Treat this as a "
        "revise/design signal, not a promotion: the next change should target the sidecar "
        "mechanism with an explicit safety-floor gate and regression accounting."
    )


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
    parser.add_argument("--artifact-dir", type=Path, default=Path("experiments"))
    parser.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    manifest = load_manifest(args.manifest)
    rows, metadata = run_atlas_hard_slice_diagnostic(
        manifest,
        artifact_dir=args.artifact_dir,
    )
    write_jsonl_rows(rows, args.jsonl)
    write_diagnostic_json(metadata, args.json)
    write_diagnostic_report(
        rows,
        metadata,
        args.markdown,
        jsonl_path=args.jsonl,
        json_path=args.json,
    )
    print(json.dumps(metadata["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
