"""Aggregate-only frozen test audit for the structured projection port."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_purist

POLICY_NAME = "gan2026_structured_projection_port_promoted_v0"
DATE = "2026-06-05"
BASE_LAYER = "hybrid_adjudicator_raw"
DEFAULT_TEST_INPUT_PATH = Path(
    "experiments/"
    "gan2026_hybrid_parallel_state_candidate_reasoner_test450_gpt41mini_v0_"
    "deterministic_safety_floor_live_2026-06-03.jsonl"
)
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_structured_projection_port_test450_aggregate_audit_2026-06-05.json"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    "experiments/gan2026_structured_projection_port_test450_aggregate_audit_2026-06-05.md"
)

FAMILY_PRIORITY = (
    "cluster_frequency",
    "daily_frequency",
    "weekly_frequency",
    "seizure_free",
    "unknown_frequency",
    "other_frequency",
)
SOURCE_PRIORITY = ("llm_candidate", "deterministic_candidate")


def run_test_aggregate_audit(test_rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Run the frozen policy over saved test packets and return aggregates only."""

    aggregate_rows = [_run_aggregate_row(row) for row in test_rows]
    return summarize_aggregate_rows(aggregate_rows, test_rows)


def summarize_aggregate_rows(
    aggregate_rows: Sequence[Mapping[str, Any]],
    test_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Summarize row-level in-memory outcomes without writing row-level output."""

    transitions = Counter(str(row["transition"]) for row in aggregate_rows)
    selected_family_counts = Counter(str(row["selected_family"]) for row in aggregate_rows)
    selected_source_counts = Counter(str(row["selected_source"]) for row in aggregate_rows)
    base_correct_rows = sum(
        bool(row["score_layers"][BASE_LAYER]["purist_correct"]) for row in test_rows
    )
    final_correct_rows = base_correct_rows + transitions["W_to_C"] - transitions["C_to_W"]
    changed_rows = sum(row["selected_family"] != "keep_current" for row in aggregate_rows)
    invalid_candidate_label_rows = sum(
        bool(row["invalid_candidate_label"]) for row in aggregate_rows
    )
    row_count = len(test_rows)
    return {
        "artifact_kind": "gan2026_structured_projection_port_test450_aggregate_audit",
        "date": DATE,
        "policy_name": POLICY_NAME,
        "base_layer": BASE_LAYER,
        "source_artifact": str(DEFAULT_TEST_INPUT_PATH),
        "protocol_artifact": (
            "docs/research/"
            "gan2026_structured_projection_port_frozen_test_protocol_2026-06-05.md"
        ),
        "claim_boundary": (
            "User-authorized frozen locked-test aggregate-only audit for the "
            "structured projection port. This artifact omits test row ids, note "
            "text, evidence snippets, predictions, gold labels, and row-level "
            "failures. It is not benchmark-comparable."
        ),
        "inspection_policy": "aggregate_only_no_row_level_test_output",
        "new_llm_calls_made": 0,
        "holdout_authorized_by_user": True,
        "locked_test_row_level_artifacts_written": 0,
        "metrics": {
            "test_rows": row_count,
            "base_correct_rows": base_correct_rows,
            "final_correct_rows": final_correct_rows,
            "base_purist_proxy": _rate(base_correct_rows, row_count),
            "final_purist_proxy": _rate(final_correct_rows, row_count),
            "changed_rows": changed_rows,
            "invalid_candidate_label_rows": invalid_candidate_label_rows,
            "changed_label_precision": _rate(
                transitions["W_to_C"],
                transitions["W_to_C"] + transitions["C_to_W"],
            ),
        },
        "transition_counts": dict(sorted(transitions.items())),
        "selected_family_counts": dict(sorted(selected_family_counts.items())),
        "selected_source_counts": dict(sorted(selected_source_counts.items())),
        "family_priority": list(FAMILY_PRIORITY),
        "source_priority": list(SOURCE_PRIORITY),
        "decision": _decision(
            base_correct_rows=base_correct_rows,
            final_correct_rows=final_correct_rows,
            transitions=transitions,
            changed_rows=changed_rows,
        ),
    }


def write_summary_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_report(metadata: Mapping[str, Any], path: Path, *, json_path: Path) -> None:
    metrics = metadata["metrics"]
    lines = [
        "# Gan 2026 Structured Projection Port Test450 Aggregate Audit",
        "",
        str(metadata["claim_boundary"]),
        "",
        "## Decision",
        "",
        str(metadata["decision"]),
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in metrics.items():
        lines.append(f"| {key.replace('_', ' ')} | {_format_metric(value)} |")
    lines.extend(["", "## Transitions", "", "| Transition | Rows |", "| --- | ---: |"])
    for transition, count in metadata["transition_counts"].items():
        lines.append(f"| `{transition}` | {count} |")
    lines.extend(["", "## Selected Families", "", "| Family | Rows |", "| --- | ---: |"])
    for family, count in metadata["selected_family_counts"].items():
        lines.append(f"| `{family}` | {count} |")
    lines.extend(["", "## Selected Sources", "", "| Source | Rows |", "| --- | ---: |"])
    for source, count in metadata["selected_source_counts"].items():
        lines.append(f"| `{source}` | {count} |")
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- Summary JSON: `{json_path}`",
            f"- Protocol: `{metadata['protocol_artifact']}`",
            f"- Source test artifact: `{metadata['source_artifact']}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def materialize_test_aggregate_audit(
    *,
    test_input_path: Path = DEFAULT_TEST_INPUT_PATH,
    output_json_path: Path = DEFAULT_OUTPUT_JSON_PATH,
    output_report_path: Path = DEFAULT_OUTPUT_REPORT_PATH,
) -> dict[str, Any]:
    test_rows = load_jsonl_rows(test_input_path)
    metadata = run_test_aggregate_audit(test_rows)
    metadata = {
        **metadata,
        "source_artifact": str(test_input_path),
        "json_artifact": str(output_json_path),
        "report_artifact": str(output_report_path),
    }
    write_summary_json(metadata, output_json_path)
    write_report(metadata, output_report_path, json_path=output_json_path)
    return metadata


def _run_aggregate_row(row: Mapping[str, Any]) -> dict[str, Any]:
    base_layer = row["score_layers"][BASE_LAYER]
    base_label = str(base_layer["final_label"])
    selected = _select_candidate(row, base_label)
    final_label = selected["label"] if selected else base_label
    invalid_candidate_label = False
    try:
        final_category = _purist_category(final_label)
    except ValueError:
        final_category = str(base_layer["predicted_purist_category"])
        invalid_candidate_label = selected is not None
        final_label = base_label
        selected = None
    base_correct = bool(base_layer["purist_correct"])
    final_correct = final_category == str(base_layer["gold_purist_category"])
    return {
        "selected_family": selected["family"] if selected else "keep_current",
        "selected_source": selected["source"] if selected else "keep_current",
        "transition": _transition(base_correct=base_correct, final_correct=final_correct),
        "invalid_candidate_label": invalid_candidate_label,
    }


def _select_candidate(row: Mapping[str, Any], base_label: str) -> dict[str, str] | None:
    candidates = _candidate_options(row, base_label)
    for family in FAMILY_PRIORITY:
        for source in SOURCE_PRIORITY:
            for candidate in candidates:
                if candidate["family"] == family and candidate["source"] == source:
                    return candidate
    return None


def _candidate_options(row: Mapping[str, Any], base_label: str) -> list[dict[str, str]]:
    options = []
    llm_record = row.get("structured_llm_candidate_record") or {}
    component_inputs = row.get("component_inputs") or {}
    for candidate in llm_record.get("candidates", []):
        if str(candidate.get("assertion_status")) != "asserted":
            continue
        if str(candidate.get("temporality")) not in {"current", "recent"}:
            continue
        label = str(candidate.get("normalized_label") or "")
        family = _eligible_family(label, base_label)
        if family:
            options.append({"family": family, "label": label, "source": "llm_candidate"})
    for candidate in component_inputs.get("deterministic_candidates", []):
        label = str(candidate.get("normalized_label") or "")
        family = _eligible_family(label, base_label)
        if family:
            options.append(
                {
                    "family": family,
                    "label": label,
                    "source": "deterministic_candidate",
                }
            )
    return options


def _eligible_family(label: str, base_label: str) -> str | None:
    normalized = " ".join(label.lower().split())
    base = " ".join(base_label.lower().split())
    if not normalized or normalized == base:
        return None
    if "cluster" in normalized and "cluster" not in base:
        return "cluster_frequency"
    if "per day" in normalized and "per day" not in base:
        return "daily_frequency"
    if "per week" in normalized and "per week" not in base:
        return "weekly_frequency"
    if normalized.startswith("seizure free") and base in {
        "unknown",
        "no seizure frequency reference",
    }:
        return "seizure_free"
    if normalized == "unknown" and (
        base.startswith("seizure free") or base == "no seizure frequency reference"
    ):
        return "unknown_frequency"
    if (
        _looks_like_frequency(normalized)
        and base in {"unknown", "no seizure frequency reference"}
        and "cluster" not in normalized
    ):
        return "other_frequency"
    return None


def _looks_like_frequency(label: str) -> bool:
    return " per " in label and not label.startswith("multiple per")


def _purist_category(label: str) -> str:
    record = label_to_frequency_record(label)
    return str(map_purist(record.monthly_frequency))


def _transition(*, base_correct: bool, final_correct: bool) -> str:
    if base_correct and final_correct:
        return "C_to_C"
    if base_correct and not final_correct:
        return "C_to_W"
    if not base_correct and final_correct:
        return "W_to_C"
    return "W_to_W"


def _decision(
    *,
    base_correct_rows: int,
    final_correct_rows: int,
    transitions: Counter[str],
    changed_rows: int,
) -> str:
    if changed_rows == 0:
        return "no_effect"
    if transitions["C_to_W"] == 0 and final_correct_rows > base_correct_rows:
        return "promoted_audit_positive"
    if final_correct_rows <= base_correct_rows:
        return "promoted_audit_rejected_or_revise"
    return "promoted_audit_mixed"


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _format_metric(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test-input-path", type=Path, default=DEFAULT_TEST_INPUT_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    parser.add_argument("--output-report-path", type=Path, default=DEFAULT_OUTPUT_REPORT_PATH)
    args = parser.parse_args(argv)
    metadata = materialize_test_aggregate_audit(
        test_input_path=args.test_input_path,
        output_json_path=args.output_json_path,
        output_report_path=args.output_report_path,
    )
    print(
        json.dumps(
            {
                "decision": metadata["decision"],
                "metrics": metadata["metrics"],
                "transition_counts": metadata["transition_counts"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
