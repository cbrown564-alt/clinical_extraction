"""Build row-level Gan 2026 LLM component mechanics artifacts."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

DEFAULT_RQ1_MATRIX_PATH = Path(
    "experiments/gan2026_rq1_candidate_discovery_matrix_2026-06-03.jsonl"
)
DEFAULT_RQ2_MATRIX_PATH = Path(
    "experiments/gan2026_rq2_evidence_selection_matrix_2026-06-03.jsonl"
)
DEFAULT_RQ4_MATRIX_PATH = Path(
    "experiments/gan2026_rq4_projection_decision_matrix_2026-06-03.jsonl"
)
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_llm_component_mechanics_rows_2026-06-03.jsonl"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_llm_component_mechanics_rows_2026-06-03.md"
)

RECALL_MATCH_STATUSES = {"exact_label", "purist_category", "semantic_state"}
LLM_RQ2_COMPONENTS = {
    "hybrid_adjudicator_raw",
    "llm_candidate_selector_raw",
    "llm_heavy_selected_fact",
    "claim_table_final_query",
}
PROJECTION_COMPONENTS = {
    "boundary_state_priority",
    "competing_frequency_uncertainty",
    "graph_gated_month_bucket_duration",
    "hybrid_adjudicator_raw",
    "llm_heavy_selected_fact",
    "claim_table_final_query",
    "state_graph_projection",
}


def build_llm_component_mechanics_rows(
    *,
    rq1_matrix_path: Path = DEFAULT_RQ1_MATRIX_PATH,
    rq2_matrix_path: Path = DEFAULT_RQ2_MATRIX_PATH,
    rq4_matrix_path: Path = DEFAULT_RQ4_MATRIX_PATH,
    max_examples_per_bucket: int = 12,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Build a compact row-level artifact from saved RQ1/RQ2/RQ4 matrices."""

    rq1_rows = load_jsonl_rows(rq1_matrix_path)
    rq2_rows = load_jsonl_rows(rq2_matrix_path)
    rq4_rows = load_jsonl_rows(rq4_matrix_path)

    rows: list[dict[str, Any]] = []
    rows.extend(_rq1_mechanics_rows(rq1_rows, max_examples_per_bucket=max_examples_per_bucket))
    rows.extend(_rq2_mechanics_rows(rq2_rows, max_examples_per_bucket=max_examples_per_bucket))
    rows.extend(_rq4_mechanics_rows(rq4_rows, max_examples_per_bucket=max_examples_per_bucket))
    rows.sort(
        key=lambda row: (
            row["clinical_subproblem"],
            row["mechanism_bucket"],
            row["component_name"],
            int(row["source_row_index"]),
        )
    )
    return rows, summarize_mechanics_rows(rows)


def summarize_mechanics_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    by_bucket = Counter(str(row["mechanism_bucket"]) for row in rows)
    by_component = Counter(str(row["component_name"]) for row in rows)
    by_family: Counter[str] = Counter()
    for row in rows:
        for family in row.get("hidden_families") or ["unmapped"]:
            by_family[str(family)] += 1
    return {
        "artifact_kind": "gan2026_llm_component_mechanics_rows",
        "row_count": len(rows),
        "source_row_count": len({int(row["source_row_index"]) for row in rows}),
        "by_bucket": dict(sorted(by_bucket.items())),
        "by_component": dict(sorted(by_component.items())),
        "by_hidden_family": dict(sorted(by_family.items())),
    }


def write_mechanics_jsonl(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    write_jsonl_rows(rows, path)


def write_mechanics_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Gan 2026 LLM Component Mechanics Rows",
        "",
        (
            "Compact row-level artifact for the RQ1/RQ2/RQ4 reset. This is a "
            "validation-development diagnostic artifact; deterministic outputs are "
            "included only as comparator context."
        ),
        "",
        f"- JSONL artifact: `{jsonl_path}`",
        f"- Mechanism rows: {metadata['row_count']}",
        f"- Source rows represented: {metadata['source_row_count']}",
        "",
        "## Buckets",
        "",
        "| Bucket | Rows |",
        "| --- | ---: |",
    ]
    for bucket, count in metadata["by_bucket"].items():
        lines.append(f"| `{bucket}` | {count} |")
    lines.extend(
        [
            "",
            "## Components",
            "",
            "| Component | Rows |",
            "| --- | ---: |",
        ]
    )
    for component, count in metadata["by_component"].items():
        lines.append(f"| `{component}` | {count} |")
    lines.extend(
        [
            "",
            "## Example Index",
            "",
            "| Bucket | Component | Source row | Gold | Candidate | Evidence snippet |",
            "| --- | --- | ---: | --- | --- | --- |",
        ]
    )
    for row in rows[:80]:
        lines.append(
            "| `{bucket}` | `{component}` | {source} | {gold} | {candidate} | {evidence} |".format(
                bucket=row["mechanism_bucket"],
                component=row["component_name"],
                source=row["source_row_index"],
                gold=_md(row.get("gold_label")),
                candidate=_md(row.get("candidate_label")),
                evidence=_md(_clip(row.get("evidence_snippet"))),
            )
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            (
                "Rows are sampled from saved validation and diagnostic replay matrices. "
                "They support mechanism analysis and follow-up protocol design, not "
                "holdout-transfer claims or architecture promotion."
            ),
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def _rq1_mechanics_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    max_examples_per_bucket: int,
) -> list[dict[str, Any]]:
    by_source: dict[int, dict[str, list[Mapping[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        by_source[int(row["source_row_index"])][str(row["generator_name"])].append(row)

    output: list[dict[str, Any]] = []
    for source_row_index in sorted(by_source):
        generators = by_source[source_row_index]
        llm = generators.get("llm_candidate_selector_raw", [])
        selected_state = generators.get("llm_selected_state_or_evidence", [])
        deterministic = generators.get("deterministic_candidates_all", [])
        if _recalled(llm) and not _recalled(deterministic):
            output.append(
                _rq1_row(
                    _best_recall_row(llm),
                    mechanism_bucket="rq1_llm_candidate_win_over_deterministic_miss",
                    deterministic_status="deterministic_all_not_recalled",
                )
            )
        if _recalled(deterministic) and not _recalled(llm):
            example = _first(llm) or _first(deterministic)
            output.append(
                _rq1_row(
                    example,
                    mechanism_bucket="rq1_llm_candidate_loss_vs_deterministic",
                    deterministic_status="deterministic_all_recalled",
                    component_name="llm_candidate_selector_raw",
                )
            )
        if len(llm) >= 4:
            output.append(
                _rq1_row(
                    _best_recall_row(llm) or _first(llm),
                    mechanism_bucket="rq1_llm_candidate_burden",
                    deterministic_status="deterministic_context_only",
                    note=f"{len(llm)} raw LLM candidates on this row",
                )
            )
        if selected_state and _recalled(selected_state):
            output.append(
                _rq1_row(
                    _best_recall_row(selected_state),
                    mechanism_bucket="rq1_llm_selected_state_recall",
                    deterministic_status="deterministic_context_only",
                )
            )
    return _sample_by_bucket(output, max_examples_per_bucket)


def _rq2_mechanics_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    max_examples_per_bucket: int,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in rows:
        component = str(row.get("candidate_name"))
        if component not in LLM_RQ2_COMPONENTS:
            continue
        if row.get("wrong_to_correct"):
            output.append(_rq2_row(row, "rq2_llm_wrong_to_correct"))
        if row.get("correct_to_wrong"):
            output.append(_rq2_row(row, "rq2_llm_correct_to_wrong"))
        if row.get("evidence_status") == "exact" and row.get("purist_correct") is False:
            output.append(_rq2_row(row, "rq2_exact_evidence_but_wrong_state"))
        if row.get("operand_complete") is False:
            output.append(_rq2_row(row, "rq2_incomplete_typed_operands"))
    return _sample_by_bucket_component(output, max_examples_per_bucket)


def _rq4_mechanics_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    max_examples_per_bucket: int,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in rows:
        component = str(row.get("component_name"))
        if component not in PROJECTION_COMPONENTS:
            continue
        if row.get("wrong_to_correct"):
            output.append(_rq4_row(row, "rq4_projection_wrong_to_correct"))
        if row.get("correct_to_wrong"):
            output.append(_rq4_row(row, "rq4_projection_correct_to_wrong"))
        if (
            component in {"llm_heavy_selected_fact", "claim_table_final_query"}
            and row.get("projection_correct") is False
        ):
            output.append(_rq4_row(row, "rq4_schema_near_projection_miss"))
    return _sample_by_bucket_component(output, max_examples_per_bucket)


def _rq1_row(
    row: Mapping[str, Any] | None,
    *,
    mechanism_bucket: str,
    deterministic_status: str,
    note: str = "",
    component_name: str | None = None,
) -> dict[str, Any]:
    row = row or {}
    return {
        "task": "seizure_frequency",
        "dataset": "gan2026",
        "split": row.get("split") or "validation",
        "clinical_subproblem": "candidate_generation",
        "mechanism_bucket": mechanism_bucket,
        "component_name": component_name or row.get("generator_name") or "llm_candidate_selector_raw",
        "source_row_index": int(row.get("source_row_index") or -1),
        "gold_label": row.get("gold_label") or "",
        "candidate_label": _clean_text(row.get("candidate_label")),
        "evidence_snippet": _clean_text(row.get("candidate_evidence")),
        "hidden_families": row.get("hidden_families") or [],
        "deterministic_baseline_status": deterministic_status,
        "mechanism_note": note or _rq1_mechanism_note(mechanism_bucket, row),
        "claim_boundary": "validation_development_mechanism_diagnostic",
    }


def _rq2_row(row: Mapping[str, Any], mechanism_bucket: str) -> dict[str, Any]:
    return {
        "task": "seizure_frequency",
        "dataset": "gan2026",
        "split": row.get("split") or "validation",
        "clinical_subproblem": "evidence_selection",
        "mechanism_bucket": mechanism_bucket,
        "component_name": row.get("candidate_name") or "",
        "source_row_index": int(row["source_row_index"]),
        "gold_label": row.get("gold_label") or "",
        "candidate_label": _clean_text(row.get("candidate_label")),
        "baseline_label": row.get("baseline_label") or "",
        "evidence_snippet": _clean_text(row.get("selected_evidence")),
        "hidden_families": row.get("hidden_families") or [],
        "evidence_status": row.get("evidence_status") or "",
        "source_id_status": row.get("source_id_status") or "",
        "deterministic_baseline_status": _changed_status(row, "deterministic"),
        "mechanism_note": _rq2_mechanism_note(mechanism_bucket, row),
        "claim_boundary": "validation_development_mechanism_diagnostic",
    }


def _rq4_row(row: Mapping[str, Any], mechanism_bucket: str) -> dict[str, Any]:
    return {
        "task": "seizure_frequency",
        "dataset": "gan2026",
        "split": "validation",
        "clinical_subproblem": "projection",
        "surface": row.get("surface") or "",
        "mechanism_bucket": mechanism_bucket,
        "component_name": row.get("component_name") or "",
        "source_row_index": int(row["source_row_index"]),
        "gold_label": row.get("gold_label") or "",
        "candidate_label": _clean_text(row.get("candidate_label")),
        "baseline_label": row.get("baseline_label") or "",
        "hidden_families": row.get("hidden_families") or [],
        "failure_family": row.get("failure_family") or "",
        "deterministic_baseline_status": _changed_status(row, "baseline"),
        "mechanism_note": _rq4_mechanism_note(mechanism_bucket, row),
        "claim_boundary": "validation_development_mechanism_diagnostic",
    }


def _recalled(rows: Sequence[Mapping[str, Any]]) -> bool:
    return any(row.get("gold_match_status") in RECALL_MATCH_STATUSES for row in rows)


def _best_recall_row(rows: Sequence[Mapping[str, Any]]) -> Mapping[str, Any] | None:
    for status in ("exact_label", "purist_category", "semantic_state"):
        for row in rows:
            if row.get("gold_match_status") == status:
                return row
    return None


def _first(rows: Sequence[Mapping[str, Any]]) -> Mapping[str, Any] | None:
    return rows[0] if rows else None


def _sample_by_bucket(rows: Sequence[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        bucket = str(row["mechanism_bucket"])
        if len(buckets[bucket]) < limit:
            buckets[bucket].append(row)
    return [row for bucket in sorted(buckets) for row in buckets[bucket]]


def _sample_by_bucket_component(
    rows: Sequence[dict[str, Any]],
    limit: int,
) -> list[dict[str, Any]]:
    buckets: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = (str(row["mechanism_bucket"]), str(row["component_name"]))
        if len(buckets[key]) < limit:
            buckets[key].append(row)
    return [row for key in sorted(buckets) for row in buckets[key]]


def _rq1_mechanism_note(bucket: str, row: Mapping[str, Any]) -> str:
    if bucket == "rq1_llm_candidate_win_over_deterministic_miss":
        return "LLM preserved a gold-relevant state missed by deterministic candidates."
    if bucket == "rq1_llm_candidate_loss_vs_deterministic":
        return "LLM failed to expose a gold-relevant state that deterministic candidates found."
    if bucket == "rq1_llm_selected_state_recall":
        return "LLM selected-state/evidence surface exposed a recall-positive candidate."
    missing = row.get("metadata_missing_fields") or []
    if missing:
        return f"LLM produced extra candidate burden with missing metadata: {', '.join(missing)}."
    return "LLM produced extra candidate burden requiring downstream ranking or verifier gates."


def _rq2_mechanism_note(bucket: str, row: Mapping[str, Any]) -> str:
    if bucket == "rq2_llm_wrong_to_correct":
        return "LLM evidence/state changed a deterministic-wrong row to correct."
    if bucket == "rq2_llm_correct_to_wrong":
        return "LLM evidence/state changed a deterministic-correct row to wrong."
    if bucket == "rq2_incomplete_typed_operands":
        return "LLM selected evidence but did not provide complete typed operands."
    return "LLM selected exact evidence but the supported state or projection was wrong."


def _rq4_mechanism_note(bucket: str, row: Mapping[str, Any]) -> str:
    if bucket == "rq4_projection_wrong_to_correct":
        return "Projection policy corrected the baseline on this diagnostic row."
    if bucket == "rq4_projection_correct_to_wrong":
        return "Projection policy regressed a baseline-correct row."
    return "LLM/schema output was near enough to inspect but missed final projection."


def _changed_status(row: Mapping[str, Any], baseline_name: str) -> str:
    if row.get("wrong_to_correct"):
        return f"{baseline_name}_wrong_to_component_correct"
    if row.get("correct_to_wrong"):
        return f"{baseline_name}_correct_to_component_wrong"
    if row.get("changed_from_deterministic") or row.get("changed_from_baseline"):
        return f"changed_from_{baseline_name}"
    return f"unchanged_or_not_comparable_to_{baseline_name}"


def _clip(value: Any, limit: int = 110) -> str:
    text = _clean_text(value)
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def _clean_text(value: Any) -> str:
    text = "".join(
        character if character == "\n" or character == "\t" or ord(character) >= 32 else " "
        for character in str(value or "")
    )
    return " ".join(text.split())


def _md(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rq1-matrix-path", type=Path, default=DEFAULT_RQ1_MATRIX_PATH)
    parser.add_argument("--rq2-matrix-path", type=Path, default=DEFAULT_RQ2_MATRIX_PATH)
    parser.add_argument("--rq4-matrix-path", type=Path, default=DEFAULT_RQ4_MATRIX_PATH)
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--max-examples-per-bucket", type=int, default=12)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = _parse_args(argv)
    rows, metadata = build_llm_component_mechanics_rows(
        rq1_matrix_path=args.rq1_matrix_path,
        rq2_matrix_path=args.rq2_matrix_path,
        rq4_matrix_path=args.rq4_matrix_path,
        max_examples_per_bucket=args.max_examples_per_bucket,
    )
    write_mechanics_jsonl(rows, args.jsonl_path)
    write_mechanics_report(rows, metadata, args.report_path, jsonl_path=args.jsonl_path)


if __name__ == "__main__":
    main()
