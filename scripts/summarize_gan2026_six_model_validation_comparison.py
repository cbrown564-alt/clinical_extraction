"""Validate and summarize the Gan six-model validation method comparison."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)

TRACE_SCHEMA_VERSION = "gan2026.row_trace.v1"
BLOCKING_PREFIXES = (
    "invalid_json:",
    "json_parse_error:",
    "schema_validation_error:",
    "unscorable_final_label:",
    "not_run",
)


def summarize_condition_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    expected_indices: set[int],
    method: str,
) -> dict[str, Any]:
    indices = [int(row["source_row_index"]) for row in rows]
    unique_indices = set(indices)
    trace_rows = sum(
        (row.get("row_trace") or {}).get("schema_version") == TRACE_SCHEMA_VERSION
        and (row.get("row_trace") or {}).get("method") == method
        for row in rows
    )
    model_records = sum(
        (row.get("row_trace") or {}).get("model_prediction", {}).get("record")
        is not None
        for row in rows
    )
    model_to_final_changed = sum(
        _model_boundary_label(row, method=method) != _final_label(row, method=method)
        for row in rows
        if _model_boundary_label(row, method=method) is not None
        and _final_label(row, method=method) is not None
    )
    evidence_valid = sum(_evidence_valid(row, method=method) for row in rows)
    purist_correct = sum(bool((row.get("comparison") or {}).get("purist_correct")) for row in rows)
    pragmatic_correct = sum(
        bool((row.get("comparison") or {}).get("pragmatic_correct")) for row in rows
    )
    blocking_failures = sum(
        any(str(event).startswith(BLOCKING_PREFIXES) for event in row.get("parse_errors") or [])
        for row in rows
    )
    repair_rows = sum(
        bool((row.get("row_trace") or {}).get("deterministic_adapter", {}).get("events"))
        or bool((row.get("row_trace") or {}).get("deterministic_semantic", {}).get("events"))
        for row in rows
    )
    row_count = len(rows)
    complete = (
        row_count == len(expected_indices)
        and len(unique_indices) == len(expected_indices)
        and unique_indices == expected_indices
        and trace_rows == row_count
    )
    return {
        "complete": complete,
        "row_count": row_count,
        "unique_source_rows": len(unique_indices),
        "expected_source_rows": len(expected_indices),
        "missing_source_rows": len(expected_indices - unique_indices),
        "unexpected_source_rows": len(unique_indices - expected_indices),
        "duplicate_source_rows": row_count - len(unique_indices),
        "trace_rows": trace_rows,
        "model_prediction_records": model_records,
        "call_failures": sum(bool(row.get("call_error")) for row in rows),
        "blocking_parse_or_schema_failures": blocking_failures,
        "evidence_valid": evidence_valid,
        "model_to_final_changed": model_to_final_changed,
        "deterministic_repair_rows": repair_rows,
        "purist_correct": purist_correct,
        "purist_accuracy": round(purist_correct / row_count, 6) if row_count else None,
        "pragmatic_correct": pragmatic_correct,
        "pragmatic_accuracy": round(pragmatic_correct / row_count, 6) if row_count else None,
    }


def compare_method_rows(
    llm_only_rows: Sequence[Mapping[str, Any]],
    llm_with_rules_rows: Sequence[Mapping[str, Any]],
) -> dict[str, int]:
    llm_only_by_index = {int(row["source_row_index"]): row for row in llm_only_rows}
    rules_by_index = {int(row["source_row_index"]): row for row in llm_with_rules_rows}
    shared_indices = sorted(set(llm_only_by_index) & set(rules_by_index))
    counts = {
        "aligned_rows": len(shared_indices),
        "changed_labels": 0,
        "unchanged_correct": 0,
        "unchanged_wrong": 0,
        "llm_only_wrong_to_rules_correct": 0,
        "llm_only_correct_to_rules_wrong": 0,
        "changed_still_wrong": 0,
        "changed_rows_llm_only_evidence_valid": 0,
        "changed_rows_rules_evidence_valid": 0,
        "changed_rows_both_evidence_valid": 0,
    }
    for index in shared_indices:
        llm_only = llm_only_by_index[index]
        rules = rules_by_index[index]
        llm_only_correct = bool((llm_only.get("comparison") or {}).get("purist_correct"))
        rules_correct = bool((rules.get("comparison") or {}).get("purist_correct"))
        changed = _final_label(llm_only, method="llm_only") != _final_label(
            rules, method="llm_with_rules"
        )
        if not changed:
            key = "unchanged_correct" if llm_only_correct and rules_correct else "unchanged_wrong"
            counts[key] += 1
            continue
        counts["changed_labels"] += 1
        llm_evidence = _evidence_valid(llm_only, method="llm_only")
        rules_evidence = _evidence_valid(rules, method="llm_with_rules")
        counts["changed_rows_llm_only_evidence_valid"] += int(llm_evidence)
        counts["changed_rows_rules_evidence_valid"] += int(rules_evidence)
        counts["changed_rows_both_evidence_valid"] += int(llm_evidence and rules_evidence)
        if not llm_only_correct and rules_correct:
            counts["llm_only_wrong_to_rules_correct"] += 1
        elif llm_only_correct and not rules_correct:
            counts["llm_only_correct_to_rules_wrong"] += 1
        elif not llm_only_correct and not rules_correct:
            counts["changed_still_wrong"] += 1
    return counts


def build_summary(repo_root: Path, config_path: Path) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    expected_indices = {
        int(record.source_row_index) for record in load_records_for_split("validation")
    }
    artifact_root = repo_root / str(config["artifact_root"])
    condition_summaries: list[dict[str, Any]] = []
    rows_by_model_method: dict[tuple[str, str], list[dict[str, Any]]] = {}

    for condition in config["conditions"]:
        for method in config["methods"]:
            model_slug = str(condition["slug"])
            method_name = str(method["method"])
            relative_path = (
                Path(str(config["artifact_root"]))
                / model_slug
                / method_name
                / "validation750.rows.jsonl"
            )
            path = repo_root / relative_path
            rows = load_jsonl_rows(path) if path.is_file() else []
            rows_by_model_method[(model_slug, method_name)] = rows
            row_summary = summarize_condition_rows(
                rows,
                expected_indices=expected_indices,
                method=method_name,
            )
            condition_summaries.append(
                {
                    "model_slug": model_slug,
                    "model": condition["model"],
                    "method": method_name,
                    "prompt_version": method["prompt_version"],
                    "artifact": relative_path.as_posix(),
                    "artifact_sha256": _sha256(path) if path.is_file() else None,
                    "state": (
                        "complete"
                        if row_summary["complete"]
                        else "partial"
                        if rows
                        else "missing"
                    ),
                    **row_summary,
                }
            )

    comparisons: list[dict[str, Any]] = []
    for condition in config["conditions"]:
        slug = str(condition["slug"])
        llm_only = rows_by_model_method[(slug, "llm_only")]
        llm_with_rules = rows_by_model_method[(slug, "llm_with_rules")]
        if not llm_only or not llm_with_rules:
            continue
        comparisons.append(
            {
                "model_slug": slug,
                "model": condition["model"],
                **compare_method_rows(llm_only, llm_with_rules),
            }
        )

    return {
        "schema_version": "gan2026.six_model_validation_comparison.v1",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "protocol": config["protocol"],
        "configuration": config_path.relative_to(repo_root).as_posix(),
        "dataset": config["dataset"],
        "split": config["split"],
        "split_manifest": config["split_manifest"],
        "expected_rows_per_condition": len(expected_indices),
        "artifact_root": artifact_root.relative_to(repo_root).as_posix(),
        "conditions": condition_summaries,
        "method_comparisons": comparisons,
        "complete_condition_count": sum(
            item["state"] == "complete" for item in condition_summaries
        ),
        "expected_condition_count": len(condition_summaries),
    }


def write_markdown(summary: Mapping[str, Any], path: Path) -> None:
    lines = [
        "# Gan 2026 six-model validation comparison",
        "",
        f"Generated: {summary['generated_at_utc']}",
        "",
        "Development evidence on `validation750`; not holdout evidence or clinical validation.",
        "",
        "## Conditions",
        "",
        "| Model | Method | State | Rows | Purist | Pragmatic | Evidence | Repairs |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in summary["conditions"]:
        purist = (
            f"{item['purist_correct']}/{item['row_count']}"
            if item["row_count"]
            else "—"
        )
        pragmatic = (
            f"{item['pragmatic_correct']}/{item['row_count']}"
            if item["row_count"]
            else "—"
        )
        lines.append(
            f"| {item['model_slug']} | `{item['method']}` | {item['state']} | "
            f"{item['row_count']} | {purist} | {pragmatic} | {item['evidence_valid']} | "
            f"{item['deterministic_repair_rows']} |"
        )
    if summary["method_comparisons"]:
        lines.extend(
            [
                "",
                "## Matched method transitions",
                "",
                (
                    "| Model | Changed | LLM-only wrong → rules correct | "
                    "LLM-only correct → rules wrong | Both evidence-valid |"
                ),
                "| --- | ---: | ---: | ---: | ---: |",
            ]
        )
        for item in summary["method_comparisons"]:
            lines.append(
                f"| {item['model_slug']} | {item['changed_labels']} | "
                f"{item['llm_only_wrong_to_rules_correct']} | "
                f"{item['llm_only_correct_to_rules_wrong']} | "
                f"{item['changed_rows_both_evidence_valid']} |"
            )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _model_boundary_label(row: Mapping[str, Any], *, method: str) -> str | None:
    record = (row.get("row_trace") or {}).get("model_prediction", {}).get("record")
    if not isinstance(record, Mapping):
        return None
    if method == "llm_only":
        value = record.get("final_label")
    else:
        selection = record.get("selection") or {}
        value = selection.get("final_label") if isinstance(selection, Mapping) else None
    return str(value) if value is not None else None


def _final_label(row: Mapping[str, Any], *, method: str) -> str | None:
    if method == "llm_only":
        record = row.get("decision_record") or {}
        value = record.get("final_label") if isinstance(record, Mapping) else None
    else:
        record = row.get("structured_record") or {}
        selection = record.get("selection") if isinstance(record, Mapping) else None
        value = selection.get("final_label") if isinstance(selection, Mapping) else None
    return str(value) if value is not None else None


def _evidence_valid(row: Mapping[str, Any], *, method: str) -> bool:
    key = "evidence_text_contained" if method == "llm_only" else "evidence_valid"
    return bool(row.get(key))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/gan2026/six_model_validation_comparison_20260718.json"),
    )
    parser.add_argument(
        "--json",
        type=Path,
        default=Path("experiments/gan2026_six_model_validation_comparison_20260718.json"),
    )
    parser.add_argument(
        "--markdown",
        type=Path,
        default=Path("docs/experiments/gan2026/gan2026_six_model_validation_comparison_2026-07-18.md"),
    )
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()
    config_path = args.config if args.config.is_absolute() else repo_root / args.config
    json_path = args.json if args.json.is_absolute() else repo_root / args.json
    markdown_path = (
        args.markdown if args.markdown.is_absolute() else repo_root / args.markdown
    )
    summary = build_summary(repo_root, config_path)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_markdown(summary, markdown_path)
    print(
        json.dumps(
            {
                "complete": summary["complete_condition_count"],
                "expected": summary["expected_condition_count"],
                "json": str(json_path),
                "markdown": str(markdown_path),
            },
            sort_keys=True,
        )
    )
    return 0 if summary["complete_condition_count"] == summary["expected_condition_count"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
