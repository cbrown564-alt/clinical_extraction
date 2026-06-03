"""Build the Gan 2026 RQ2 evidence-selection matrix from saved artifacts."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

DEFAULT_ARTIFACT_PATHS = (
    Path(
        "experiments/"
        "gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_"
        "deterministic_safety_floor_replay_2026-06-03.jsonl"
    ),
    Path(
        "experiments/"
        "gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_"
        "gpt41mini_v1_live_2026-06-03.jsonl"
    ),
    Path(
        "experiments/"
        "gan2026_llm_only_claim_table_selector_validation250_gpt41mini_v5_max2400_"
        "2026-06-01.jsonl"
    ),
)
DEFAULT_ATLAS_CSV_PATH = Path(
    "experiments/gan2026_hidden_family_first_failure_atlas_2026-06-03.csv"
)
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_rq2_evidence_selection_matrix_2026-06-03.jsonl"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_rq2_evidence_selection_matrix_2026-06-03.md"
)


def build_evidence_selection_matrix(
    artifact_paths: Sequence[Path] = DEFAULT_ARTIFACT_PATHS,
    *,
    atlas_csv_path: Path | None = DEFAULT_ATLAS_CSV_PATH,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    atlas = load_atlas_lookup(atlas_csv_path) if atlas_csv_path else {}
    rows: list[dict[str, Any]] = []
    for artifact_path in artifact_paths:
        artifact_name = artifact_path.name
        for artifact_row in load_jsonl_rows(artifact_path):
            rows.extend(_rows_for_artifact_row(artifact_row, artifact_path, artifact_name, atlas))
    rows.sort(
        key=lambda row: (
            row["source_row_index"],
            row["candidate_name"],
            row["component_owner"],
            row["artifact_path"],
        )
    )
    return rows, summarize_evidence_rows(rows)


def load_atlas_lookup(path: Path) -> dict[tuple[str, int], dict[str, Any]]:
    if not path.exists():
        return {}
    lookup: dict[tuple[str, int], dict[str, Any]] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            try:
                source_row_index = int(row["source_row_index"])
            except (KeyError, TypeError, ValueError):
                continue
            lookup[(row.get("artifact_name") or "", source_row_index)] = {
                "hidden_families": [
                    item for item in (row.get("hidden_families") or "").split(";") if item
                ],
                "first_failure_owner": row.get("first_failure_owner") or "",
            }
    return lookup


def summarize_evidence_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    by_component: dict[str, dict[str, Any]] = {}
    rows_by_component: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    rows_by_family: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        component = str(row["candidate_name"])
        rows_by_component[component].append(row)
        families = row.get("hidden_families") or ["unmapped"]
        for family in families:
            rows_by_family[(component, str(family))].append(row)

    for component, component_rows in sorted(rows_by_component.items()):
        by_component[component] = _summary_for_rows(component_rows)

    hidden_family_summary = {
        f"{component}::{family}": _summary_for_rows(family_rows)
        for (component, family), family_rows in sorted(rows_by_family.items())
    }
    return {
        "artifact_kind": "gan2026_rq2_evidence_selection_matrix",
        "row_count": len(rows),
        "source_row_count": len({int(row["source_row_index"]) for row in rows}),
        "by_component": by_component,
        "hidden_family_summary": hidden_family_summary,
    }


def write_matrix_jsonl(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    write_jsonl_rows(rows, path)


def write_matrix_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Gan 2026 RQ2 Evidence-Selection Matrix",
        "",
        (
            "Replay-first component matrix for RQ2 evidence selection. This is a "
            "validation-development artifact, not a benchmark or locked-holdout claim."
        ),
        "",
        f"- JSONL artifact: `{jsonl_path}`",
        f"- Matrix rows: {metadata['row_count']}",
        f"- Source rows represented: {metadata['source_row_count']}",
        "",
        "## Component Summary",
        "",
        (
            "| Component | Rows | Exact evidence | Source-id valid | Scorable | Purist "
            "correct | Operand complete | Changed | W->C | C->W |"
        ),
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for component, summary in metadata["by_component"].items():
        lines.append(
            (
                "| {component} | {rows} | {exact:.3f} | {source_ids:.3f} | "
                "{scorable:.3f} | {purist:.3f} | {operands:.3f} | {changed} | "
                "{wtc} | {ctw} |"
            ).format(
                component=component,
                rows=summary["rows"],
                exact=summary["exact_evidence_rate"],
                source_ids=summary["source_id_valid_rate"],
                scorable=summary["scorable_rate"],
                purist=summary["purist_correct_rate"],
                operands=summary["operand_complete_rate"],
                changed=summary["changed_from_deterministic"],
                wtc=summary["wrong_to_correct"],
                ctw=summary["correct_to_wrong"],
            )
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            (
                "This matrix measures selected evidence validity, selected source-id "
                "validity, typed operand completeness, and correctness of the label "
                "supported by the selected evidence where saved artifacts expose those "
                "fields. Missing source-id instrumentation is reported separately and "
                "does not support an exact-source-id claim."
            ),
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def _rows_for_artifact_row(
    artifact_row: Mapping[str, Any],
    artifact_path: Path,
    artifact_name: str,
    atlas: Mapping[tuple[str, int], Mapping[str, Any]],
) -> list[dict[str, Any]]:
    source_row_index = int(artifact_row["source_row_index"])
    context = _row_context(artifact_row, artifact_name, source_row_index, atlas)
    rows: list[dict[str, Any]] = []
    component_inputs = artifact_row.get("component_inputs") or {}
    score_layers = artifact_row.get("score_layers") or {}

    deterministic_top = component_inputs.get("deterministic_top")
    if isinstance(deterministic_top, Mapping):
        rows.append(
            _matrix_row(
                artifact_path=artifact_path,
                context=context,
                candidate_name="deterministic_top_candidate",
                component_owner="deterministic_rule",
                selected_evidence=_text(
                    deterministic_top.get("evidence")
                    or (deterministic_top.get("selected_decision") or {}).get("evidence")
                ),
                selected_source_ids=deterministic_top.get("selected_event_ids") or [],
                score_layer=score_layers.get("deterministic_top_candidate"),
                evidence_valid=None,
                operand_complete=None,
            )
        )

    state_graph_projection = component_inputs.get("state_graph_projection")
    if isinstance(state_graph_projection, Mapping):
        rows.append(
            _matrix_row(
                artifact_path=artifact_path,
                context=context,
                candidate_name="state_graph_projection",
                component_owner="graph_projection",
                selected_evidence=_text(state_graph_projection.get("evidence")),
                selected_source_ids=state_graph_projection.get("selected_node_ids") or [],
                score_layer=score_layers.get("state_graph_projection"),
                evidence_valid=None,
                operand_complete=None,
            )
        )

    llm_selection = component_inputs.get("llm_candidate_selection")
    if isinstance(llm_selection, Mapping):
        rows.append(
            _matrix_row(
                artifact_path=artifact_path,
                context=context,
                candidate_name="llm_candidate_selector_raw",
                component_owner="llm_clinical_selection",
                selected_evidence=_text(llm_selection.get("selected_evidence")),
                selected_source_ids=llm_selection.get("selected_candidate_ids") or [],
                score_layer=score_layers.get("llm_candidate_selector_raw"),
                evidence_valid=None,
                operand_complete=None,
            )
        )

    adjudicator = artifact_row.get("structured_adjudicator_record")
    if isinstance(adjudicator, Mapping):
        rows.append(
            _matrix_row(
                artifact_path=artifact_path,
                context=context,
                candidate_name="hybrid_adjudicator_raw",
                component_owner="llm_clinical_selection",
                selected_evidence=_text(adjudicator.get("selected_evidence")),
                selected_source_ids=adjudicator.get("selected_source_ids") or [],
                score_layer=score_layers.get("hybrid_adjudicator_raw"),
                evidence_valid=(artifact_row.get("diagnostics") or {}).get(
                    "selected_evidence_exact"
                ),
                operand_complete=None,
            )
        )

    evidence_summary = artifact_row.get("evidence_summary") or {}
    structured = artifact_row.get("structured_record") or {}
    selected_fact = structured.get("selected_fact") or {}
    if selected_fact or artifact_row.get("pipeline_family") == (
        "llm_heavy_evidence_selection_with_deterministic_adapters"
    ):
        rows.append(
            _matrix_row(
                artifact_path=artifact_path,
                context=context,
                candidate_name="llm_heavy_selected_fact",
                component_owner="llm_clinical_selection",
                selected_evidence=_text(
                    selected_fact.get("evidence")
                    or evidence_summary.get("selected_fact_evidence")
                    or evidence_summary.get("raw_model_selected_evidence")
                ),
                selected_source_ids=[],
                score_layer=score_layers.get("raw_model_clinical_selection")
                or score_layers.get("raw_model_parser_label"),
                evidence_valid=evidence_summary.get("selected_evidence_valid"),
                operand_complete=(artifact_row.get("mechanical_adapter") or {}).get(
                    "operand_complete"
                ),
            )
        )

    final_query = structured.get("final_query") or {}
    if final_query or artifact_row.get("pipeline_name") == (
        "gan2026_llm_only_claim_table_selector_v5"
    ):
        rows.append(
            _matrix_row(
                artifact_path=artifact_path,
                context=context,
                candidate_name="claim_table_final_query",
                component_owner="llm_clinical_selection",
                selected_evidence=_text(
                    final_query.get("evidence") or evidence_summary.get("selected_evidence")
                ),
                selected_source_ids=final_query.get("selected_claim_ids") or [],
                score_layer=score_layers.get("raw"),
                evidence_valid=evidence_summary.get("selected_evidence_valid"),
                operand_complete=None,
            )
        )

    return rows


def _row_context(
    artifact_row: Mapping[str, Any],
    artifact_name: str,
    source_row_index: int,
    atlas: Mapping[tuple[str, int], Mapping[str, Any]],
) -> dict[str, Any]:
    reference = artifact_row.get("reference") or {}
    component_inputs = artifact_row.get("component_inputs") or {}
    typed_input = artifact_row.get("typed_input") or {}
    note_text = component_inputs.get("note_text") or typed_input.get("note_text") or ""
    deterministic_layer = (artifact_row.get("score_layers") or {}).get(
        "deterministic_top_candidate"
    ) or {}
    atlas_row = (
        atlas.get((artifact_name, source_row_index))
        or atlas.get(("", source_row_index))
        or {}
    )
    return {
        "source_row_index": source_row_index,
        "split": artifact_row.get("split") or "",
        "split_manifest": artifact_row.get("split_manifest") or "gan2026_split_v1",
        "distribution": _distribution_for_row(artifact_row, artifact_name),
        "pipeline_name": artifact_row.get("pipeline_name")
        or artifact_row.get("pipeline_family")
        or artifact_row.get("architecture")
        or "",
        "note_text": note_text,
        "gold_label": reference.get("gold_label") or reference.get("gold_normalized_label") or "",
        "hidden_families": list(atlas_row.get("hidden_families") or []),
        "first_failure_owner": atlas_row.get("first_failure_owner") or "",
        "deterministic_label": deterministic_layer.get("final_label") or "",
        "deterministic_purist_correct": deterministic_layer.get("purist_correct"),
    }


def _matrix_row(
    *,
    artifact_path: Path,
    context: Mapping[str, Any],
    candidate_name: str,
    component_owner: str,
    selected_evidence: str,
    selected_source_ids: Sequence[Any],
    score_layer: Any,
    evidence_valid: Any,
    operand_complete: Any,
) -> dict[str, Any]:
    score = score_layer if isinstance(score_layer, Mapping) else {}
    candidate_label = _text(score.get("final_label"))
    purist_correct = score.get("purist_correct")
    changed = (
        bool(candidate_label)
        and bool(context.get("deterministic_label"))
        and candidate_label != context.get("deterministic_label")
    )
    baseline_correct = context.get("deterministic_purist_correct")
    return {
        "task": "seizure_frequency",
        "dataset": "gan2026",
        "source_row_index": context["source_row_index"],
        "split": context["split"],
        "split_manifest": context["split_manifest"],
        "distribution": context["distribution"],
        "artifact_path": artifact_path.as_posix(),
        "pipeline_name": context["pipeline_name"],
        "clinical_subproblem": "evidence_selection",
        "candidate_name": candidate_name,
        "component_owner": component_owner,
        "selected_evidence": selected_evidence,
        "evidence_status": _evidence_status(
            selected_evidence=selected_evidence,
            note_text=str(context.get("note_text") or ""),
            evidence_valid=evidence_valid,
        ),
        "selected_source_ids": [str(item) for item in selected_source_ids],
        "source_id_status": _source_id_status(selected_source_ids),
        "candidate_label": candidate_label,
        "gold_label": context["gold_label"],
        "scorable": bool(score.get("scorable")),
        "purist_correct": purist_correct,
        "pragmatic_correct": score.get("pragmatic_correct"),
        "operand_complete": operand_complete,
        "baseline_label": context.get("deterministic_label") or "",
        "baseline_purist_correct": baseline_correct,
        "changed_from_deterministic": changed,
        "wrong_to_correct": bool(changed and baseline_correct is False and purist_correct is True),
        "correct_to_wrong": bool(changed and baseline_correct is True and purist_correct is False),
        "hidden_families": context["hidden_families"],
        "first_failure_owner": context["first_failure_owner"],
    }


def _summary_for_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    exact_rows = [row for row in rows if row.get("evidence_status") == "exact"]
    source_id_judged = [row for row in rows if row.get("source_id_status") != "not_instrumented"]
    source_id_valid = [row for row in source_id_judged if row.get("source_id_status") == "valid"]
    scorable = [row for row in rows if row.get("scorable")]
    purist_judged = [row for row in rows if row.get("purist_correct") is not None]
    purist_correct = [row for row in purist_judged if row.get("purist_correct") is True]
    operand_judged = [row for row in rows if row.get("operand_complete") is not None]
    operand_complete = [row for row in operand_judged if row.get("operand_complete") is True]
    return {
        "rows": len(rows),
        "exact_evidence_rows": len(exact_rows),
        "exact_evidence_rate": _rate(len(exact_rows), len(rows)),
        "source_id_judged_rows": len(source_id_judged),
        "source_id_valid_rows": len(source_id_valid),
        "source_id_valid_rate": _rate(len(source_id_valid), len(source_id_judged)),
        "scorable_rows": len(scorable),
        "scorable_rate": _rate(len(scorable), len(rows)),
        "purist_judged_rows": len(purist_judged),
        "purist_correct_rows": len(purist_correct),
        "purist_correct_rate": _rate(len(purist_correct), len(purist_judged)),
        "operand_judged_rows": len(operand_judged),
        "operand_complete_rows": len(operand_complete),
        "operand_complete_rate": _rate(len(operand_complete), len(operand_judged)),
        "changed_from_deterministic": sum(
            1 for row in rows if row.get("changed_from_deterministic")
        ),
        "wrong_to_correct": sum(1 for row in rows if row.get("wrong_to_correct")),
        "correct_to_wrong": sum(1 for row in rows if row.get("correct_to_wrong")),
    }


def _evidence_status(*, selected_evidence: str, note_text: str, evidence_valid: Any) -> str:
    if not selected_evidence:
        return "missing"
    if evidence_valid is True:
        return "exact"
    if evidence_valid is False:
        return "invalid"
    if note_text and selected_evidence in note_text:
        return "exact"
    if note_text:
        return "source_near"
    return "not_applicable"


def _source_id_status(selected_source_ids: Sequence[Any]) -> str:
    if not selected_source_ids:
        return "not_instrumented"
    if all(str(item).strip() for item in selected_source_ids):
        return "valid"
    return "invalid"


def _distribution_for_row(row: Mapping[str, Any], artifact_name: str = "") -> str:
    for distribution in ("validation25", "validation50", "validation250", "validation750"):
        if distribution in artifact_name:
            return distribution
    split = row.get("split") or ""
    if split == "validation":
        return "validation750"
    if split == "test":
        return "locked_holdout_audit"
    return str(split or "unknown")


def _text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).strip().split())


def _rate(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifacts", nargs="*", type=Path, default=list(DEFAULT_ARTIFACT_PATHS))
    parser.add_argument("--atlas-csv", type=Path, default=DEFAULT_ATLAS_CSV_PATH)
    parser.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    artifact_paths = args.artifacts or list(DEFAULT_ARTIFACT_PATHS)
    rows, metadata = build_evidence_selection_matrix(
        artifact_paths,
        atlas_csv_path=args.atlas_csv,
    )
    write_matrix_jsonl(rows, args.jsonl)
    write_matrix_report(rows, metadata, args.report, jsonl_path=args.jsonl)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
