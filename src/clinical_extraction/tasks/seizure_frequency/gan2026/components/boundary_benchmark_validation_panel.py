"""Validation hard-slice panel for boundary and benchmark-renderer typed fields."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.seizure_frequency.gan2026.data import load_records_for_split
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)

POLICY_NAME = "gan2026_boundary_benchmark_validation_panel_v0"
DEFAULT_OUTPUT_JSONL_PATH = Path(
    "experiments/gan2026_boundary_benchmark_validation_panel_v0_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_boundary_benchmark_validation_panel_v0_2026-06-05.json"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    "experiments/gan2026_boundary_benchmark_validation_panel_v0_2026-06-05.md"
)
DEFAULT_MAX_ROWS_PER_SLICE = 8


@dataclass(frozen=True)
class TypedFieldSpec:
    slice_id: str
    panel_role: str
    target_family: str
    target_mechanism: str
    expected_component: str
    expected_candidate_exposure: str
    expected_boundary_state: str
    expected_clinical_final_state: str
    expected_gan_rendered_label: str
    expected_benchmark_policy_id: str
    expected_benchmark_format_rule_id: str
    expected_format_only_change: bool
    expected_scorer_sentinel_used: bool


def build_validation_panel_rows(
    records: Sequence[Any],
    *,
    max_rows_per_slice: int = DEFAULT_MAX_ROWS_PER_SLICE,
) -> list[dict[str, Any]]:
    """Build a bounded validation-only panel for stable typed fields."""

    rows = []
    slice_counts: Counter[str] = Counter()
    for record in records:
        spec = _typed_field_spec(record)
        if spec is None or slice_counts[spec.slice_id] >= max_rows_per_slice:
            continue
        if not _evidence_exact(record):
            continue
        rows.append(_panel_row(record, spec))
        slice_counts[spec.slice_id] += 1
    rows.sort(
        key=lambda row: (
            row["target_mechanism"],
            row["slice_id"],
            row["panel_role"],
            row["source_row_index"],
        )
    )
    return rows


def summarize_validation_panel_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize the validation hard-slice typed-field panel."""

    slice_counts = Counter(str(row["slice_id"]) for row in rows)
    family_counts = Counter(str(row["target_family"]) for row in rows)
    mechanism_counts = Counter(str(row["target_mechanism"]) for row in rows)
    boundary_rows = [
        row for row in rows if row["target_mechanism"] == "seizure_free_boundary_event_v0"
    ]
    renderer_rows = [
        row for row in rows if row["target_mechanism"] == "benchmark_convention_renderer_v0"
    ]
    exact_evidence_rows = sum(bool(row["exact_evidence"]) for row in rows)
    final_policy_connected = any(row.get("final_label_policy_connected") for row in rows)
    ready = (
        bool(rows)
        and exact_evidence_rows == len(rows)
        and bool(boundary_rows)
        and bool(renderer_rows)
        and not final_policy_connected
    )
    return {
        "artifact_kind": "gan2026_boundary_benchmark_validation_panel_summary",
        "policy_name": POLICY_NAME,
        "row_count": len(rows),
        "boundary_rows": len(boundary_rows),
        "renderer_rows": len(renderer_rows),
        "hard_rows": sum(row["panel_role"] == "hard" for row in rows),
        "control_rows": sum(row["panel_role"] == "control" for row in rows),
        "exact_evidence_rows": exact_evidence_rows,
        "final_label_policy_connected": final_policy_connected,
        "slice_counts": dict(sorted(slice_counts.items())),
        "target_family_counts": dict(sorted(family_counts.items())),
        "target_mechanism_counts": dict(sorted(mechanism_counts.items())),
        "boundary_state_counts": dict(
            sorted(Counter(str(row["expected_boundary_state"]) for row in rows).items())
        ),
        "benchmark_rule_counts": dict(
            sorted(
                Counter(
                    str(row["expected_benchmark_format_rule_id"]) for row in rows
                ).items()
            )
        ),
        "claim_boundary": (
            "Validation-development hard-slice panel for stable boundary and "
            "benchmark-renderer typed fields. It reads validation notes in memory, "
            "writes no note text, keeps clinical state separate from Gan-rendered "
            "labels, and does not authorize holdout use or final-label promotion."
        ),
        "decision": (
            "ready_for_boundary_renderer_validation_contract"
            if ready
            else "boundary_renderer_validation_panel_contract_failed"
        ),
        "recommended_next_step": (
            "Run a validation contract smoke over this panel that checks typed-field "
            "classification, exact evidence, and renderer transparency before any "
            "candidate assembly or holdout-facing protocol."
        ),
    }


def materialize_validation_panel(
    *,
    output_jsonl_path: Path = DEFAULT_OUTPUT_JSONL_PATH,
    output_json_path: Path = DEFAULT_OUTPUT_JSON_PATH,
    output_report_path: Path = DEFAULT_OUTPUT_REPORT_PATH,
    max_rows_per_slice: int = DEFAULT_MAX_ROWS_PER_SLICE,
) -> dict[str, Any]:
    records = load_records_for_split("validation")
    rows = build_validation_panel_rows(records, max_rows_per_slice=max_rows_per_slice)
    summary = summarize_validation_panel_rows(rows)
    summary = {
        **summary,
        "jsonl_artifact": str(output_jsonl_path),
        "json_artifact": str(output_json_path),
        "report_artifact": str(output_report_path),
        "source_split": "validation",
        "split_manifest": "gan2026_split_v1",
    }
    write_jsonl_rows(rows, output_jsonl_path)
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(summary, output_report_path)
    return summary


def write_report(summary: Mapping[str, Any], path: Path) -> None:
    lines = [
        "# Gan 2026 Boundary/Benchmark Validation Panel v0",
        "",
        str(summary["claim_boundary"]),
        "",
        "## Decision",
        "",
        str(summary["decision"]),
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| rows | {summary['row_count']} |",
        f"| boundary rows | {summary['boundary_rows']} |",
        f"| renderer rows | {summary['renderer_rows']} |",
        f"| hard rows | {summary['hard_rows']} |",
        f"| control rows | {summary['control_rows']} |",
        f"| exact evidence rows | {summary['exact_evidence_rows']} |",
        f"| final-label policy connected | {summary['final_label_policy_connected']} |",
        "",
        "## Slices",
        "",
        "| Slice | Rows |",
        "| --- | ---: |",
    ]
    for slice_id, count in summary["slice_counts"].items():
        lines.append(f"| `{slice_id}` | {count} |")
    lines.extend(
        [
            "",
            "## Benchmark Rules",
            "",
            "| Rule | Rows |",
            "| --- | ---: |",
        ]
    )
    for rule, count in summary["benchmark_rule_counts"].items():
        lines.append(f"| `{rule}` | {count} |")
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            str(summary["recommended_next_step"]),
            "",
            "## Artifacts",
            "",
            f"- Panel JSONL: `{summary['jsonl_artifact']}`",
            f"- Summary JSON: `{summary['json_artifact']}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _typed_field_spec(record: Any) -> TypedFieldSpec | None:
    gold_reference = _record_value(record, "gold_reference")
    gold_label = _record_value(record, "gold_label")
    reference_lower = gold_reference.lower()
    label_lower = gold_label.lower()

    if _is_cluster_multiple_label(label_lower) and _is_unresolved_cluster_reference(
        reference_lower
    ):
        return _renderer_spec(
            slice_id="cluster_multiple_per_cluster",
            panel_role="hard",
            clinical_state="cluster_frequency_with_unresolved_burden",
            gan_label=gold_label,
            rule_id="gan_cluster_multiple_per_cluster",
            scorer_sentinel_used=True,
        )
    if _is_vague_multiple_label(label_lower) and _is_vague_multiple_reference(
        reference_lower
    ):
        return _renderer_spec(
            slice_id="vague_multiple_frequency",
            panel_role="hard",
            clinical_state="vague_multiple_current_events",
            gan_label=gold_label,
            rule_id="gan_vague_multiple_frequency",
            scorer_sentinel_used=True,
        )
    if label_lower == "unknown" and _is_unknown_sentinel_reference(reference_lower):
        return _renderer_spec(
            slice_id="unknown_sentinel",
            panel_role="hard",
            clinical_state="unknown_frequency",
            gan_label="unknown",
            rule_id="gan_unknown_sentinel",
            scorer_sentinel_used=True,
        )
    if "non-epileptic" in reference_lower:
        return _boundary_spec(
            slice_id="non_epileptic_current_events",
            panel_role="hard",
            boundary_state="non_epileptic_current_events",
            clinical_state="non_epileptic_current_events",
            gan_label=gold_label,
            scorer_sentinel_used=False,
        )
    if _is_conditional_trigger_reference(reference_lower):
        return _boundary_spec(
            slice_id="conditional_or_trigger_only",
            panel_role="hard",
            boundary_state="conditional_or_trigger_only",
            clinical_state="conditional_or_trigger_only",
            gan_label="unknown",
            scorer_sentinel_used=True,
        )
    if reference_lower.startswith("last seizure on"):
        return _boundary_spec(
            slice_id="last_event_only",
            panel_role="hard",
            boundary_state="last_event_only",
            clinical_state="last_event_only",
            gan_label="unknown",
            scorer_sentinel_used=True,
        )
    if _is_asserted_seizure_free_reference(reference_lower):
        return _boundary_spec(
            slice_id="asserted_seizure_free_interval",
            panel_role="control",
            boundary_state="asserted_seizure_free_interval",
            clinical_state="seizure_free_interval",
            gan_label=gold_label,
            scorer_sentinel_used=False,
        )
    return None


def _panel_row(record: Any, spec: TypedFieldSpec) -> dict[str, Any]:
    gold_reference = _record_value(record, "gold_reference")
    return {
        "artifact_kind": "gan2026_boundary_benchmark_validation_panel_row",
        "policy_name": POLICY_NAME,
        "source_row_index": int(_record_value(record, "source_row_index")),
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "slice_id": spec.slice_id,
        "panel_role": spec.panel_role,
        "target_family": spec.target_family,
        "target_mechanism": spec.target_mechanism,
        "expected_component": spec.expected_component,
        "expected_candidate_exposure": spec.expected_candidate_exposure,
        "expected_boundary_state": spec.expected_boundary_state,
        "expected_clinical_final_state": spec.expected_clinical_final_state,
        "expected_gan_rendered_label": spec.expected_gan_rendered_label,
        "expected_benchmark_policy_id": spec.expected_benchmark_policy_id,
        "expected_benchmark_format_rule_id": spec.expected_benchmark_format_rule_id,
        "expected_format_only_change": spec.expected_format_only_change,
        "expected_scorer_sentinel_used": spec.expected_scorer_sentinel_used,
        "expected_evidence_substring": gold_reference,
        "exact_evidence": True,
        "gold_label": _record_value(record, "gold_label"),
        "source_note_text": None,
        "final_label_policy_connected": False,
        "promotion_scope": "validation_typed_field_panel_no_final_label_promotion",
        "claim_boundary": "validation_development_only_no_holdout_use",
    }


def _boundary_spec(
    *,
    slice_id: str,
    panel_role: str,
    boundary_state: str,
    clinical_state: str,
    gan_label: str,
    scorer_sentinel_used: bool,
) -> TypedFieldSpec:
    return TypedFieldSpec(
        slice_id=slice_id,
        panel_role=panel_role,
        target_family="seizure_free_duration",
        target_mechanism="seizure_free_boundary_event_v0",
        expected_component="typed_boundary_classifier",
        expected_candidate_exposure="typed_boundary_event_present",
        expected_boundary_state=boundary_state,
        expected_clinical_final_state=clinical_state,
        expected_gan_rendered_label=gan_label,
        expected_benchmark_policy_id="gan2026_boundary_projection_policy_v0",
        expected_benchmark_format_rule_id="none_boundary_state_only",
        expected_format_only_change=False,
        expected_scorer_sentinel_used=scorer_sentinel_used,
    )


def _renderer_spec(
    *,
    slice_id: str,
    panel_role: str,
    clinical_state: str,
    gan_label: str,
    rule_id: str,
    scorer_sentinel_used: bool,
) -> TypedFieldSpec:
    return TypedFieldSpec(
        slice_id=slice_id,
        panel_role=panel_role,
        target_family="benchmark_format_convention",
        target_mechanism="benchmark_convention_renderer_v0",
        expected_component="benchmark_renderer",
        expected_candidate_exposure="typed_clinical_state_present",
        expected_boundary_state="not_applicable",
        expected_clinical_final_state=clinical_state,
        expected_gan_rendered_label=gan_label,
        expected_benchmark_policy_id="gan2026_benchmark_renderer_policy_v0",
        expected_benchmark_format_rule_id=rule_id,
        expected_format_only_change=True,
        expected_scorer_sentinel_used=scorer_sentinel_used,
    )


def _evidence_exact(record: Any) -> bool:
    return evidence_is_substring(
        _record_value(record, "note_text"),
        _record_value(record, "gold_reference"),
    )


def _record_value(record: Any, field: str) -> str:
    if isinstance(record, Mapping):
        return str(record[field])
    return str(getattr(record, field))


def _is_cluster_multiple_label(label_lower: str) -> bool:
    return "cluster" in label_lower and "multiple per cluster" in label_lower


def _is_unresolved_cluster_reference(reference_lower: str) -> bool:
    return (
        "within-cluster count unclear" in reference_lower
        or "number per cluster not documented" in reference_lower
        or "cluster frequency unclear" in reference_lower
    )


def _is_vague_multiple_label(label_lower: str) -> bool:
    return label_lower.startswith("multiple per")


def _is_vague_multiple_reference(reference_lower: str) -> bool:
    return (
        reference_lower.startswith("several ")
        or reference_lower.startswith("multiple ")
        or "several episodes per" in reference_lower
    )


def _is_unknown_sentinel_reference(reference_lower: str) -> bool:
    return (
        "frequency changed unclear direction" in reference_lower
        or "frequency unclear" in reference_lower
        or "not enough information" in reference_lower
        or "not documented" in reference_lower
    )


def _is_conditional_trigger_reference(reference_lower: str) -> bool:
    return (
        reference_lower.startswith("only with ")
        or "with missed asm doses" in reference_lower
        or "after alcohol intake" in reference_lower
        or "photosensitive seizure episodes" in reference_lower
    )


def _is_asserted_seizure_free_reference(reference_lower: str) -> bool:
    return (
        reference_lower.startswith("seizure-free")
        or reference_lower.startswith("no seizures since")
        or reference_lower.startswith("no events for")
        or reference_lower.startswith("ongoing seizure-free interval")
        or reference_lower.startswith("remains seizure-free")
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-jsonl-path", type=Path, default=DEFAULT_OUTPUT_JSONL_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    parser.add_argument("--output-report-path", type=Path, default=DEFAULT_OUTPUT_REPORT_PATH)
    parser.add_argument("--max-rows-per-slice", type=int, default=DEFAULT_MAX_ROWS_PER_SLICE)
    args = parser.parse_args(argv)
    summary = materialize_validation_panel(
        output_jsonl_path=args.output_jsonl_path,
        output_json_path=args.output_json_path,
        output_report_path=args.output_report_path,
        max_rows_per_slice=args.max_rows_per_slice,
    )
    print(
        json.dumps(
            {"decision": summary["decision"], "row_count": summary["row_count"]},
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
