"""Validation hard/control panel for boundary event contract v1."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    boundary_benchmark_validation_panel,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import load_records_for_split
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)

POLICY_NAME = "gan2026_boundary_event_validation_panel_v1"
DEFAULT_OUTPUT_JSONL_PATH = Path(
    "experiments/gan2026_boundary_event_validation_panel_v1_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_boundary_event_validation_panel_v1_2026-06-05.json"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    "experiments/gan2026_boundary_event_validation_panel_v1_2026-06-05.md"
)
DEFAULT_MAX_ROWS_PER_SLICE = (
    boundary_benchmark_validation_panel.DEFAULT_MAX_ROWS_PER_SLICE
)


def build_validation_panel_rows(
    records: Sequence[Any],
    *,
    max_rows_per_slice: int = DEFAULT_MAX_ROWS_PER_SLICE,
) -> list[dict[str, Any]]:
    """Build supported v1 typed-event validation rows."""

    base_rows = boundary_benchmark_validation_panel.build_validation_panel_rows(
        records,
        max_rows_per_slice=max_rows_per_slice,
    )
    return [_to_v1_row(row) for row in base_rows]


def build_rows_and_summary(
    records: Sequence[Any],
    *,
    max_rows_per_slice: int = DEFAULT_MAX_ROWS_PER_SLICE,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Build rows plus suppression-aware summary."""

    rows = build_validation_panel_rows(
        records,
        max_rows_per_slice=max_rows_per_slice,
    )
    summary = summarize_validation_panel_rows(
        rows,
        source_record_count=len(records),
    )
    return rows, summary


def summarize_validation_panel_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    source_record_count: int | None = None,
) -> dict[str, Any]:
    """Summarize the v1 typed-event validation panel."""

    source_record_count = len(rows) if source_record_count is None else source_record_count
    exact_evidence_rows = sum(row["exact_evidence"] is True for row in rows)
    source_note_text_rows = sum(bool(row["source_note_text_present"]) for row in rows)
    final_policy_connected = any(row.get("final_label_policy_connected") for row in rows)
    typed_event_complete_rows = sum(
        _clinical_event_complete(row["clinical_event"]) for row in rows
    )
    projection_policy_complete_rows = sum(
        _projection_policy_complete(row["projection_policy"]) for row in rows
    )
    unsupported_candidate_rows = sum(
        row.get("generator_action") == "suppress_unsupported_candidate"
        for row in rows
    )
    boundary_rows = [
        row for row in rows if row["target_mechanism"] == "seizure_free_boundary_event_v0"
    ]
    renderer_rows = [
        row for row in rows if row["target_mechanism"] == "benchmark_convention_renderer_v0"
    ]
    passed = (
        bool(rows)
        and exact_evidence_rows == len(rows)
        and source_note_text_rows == 0
        and typed_event_complete_rows == len(rows)
        and projection_policy_complete_rows == len(rows)
        and unsupported_candidate_rows == 0
        and bool(boundary_rows)
        and bool(renderer_rows)
        and not final_policy_connected
    )
    return {
        "artifact_kind": "gan2026_boundary_event_validation_panel_v1_summary",
        "policy_name": POLICY_NAME,
        "source_record_count": source_record_count,
        "row_count": len(rows),
        "suppressed_source_records": max(source_record_count - len(rows), 0),
        "unsupported_candidate_rows": unsupported_candidate_rows,
        "boundary_rows": len(boundary_rows),
        "renderer_rows": len(renderer_rows),
        "hard_rows": sum(row["panel_role"] == "hard" for row in rows),
        "control_rows": sum(row["panel_role"] == "control" for row in rows),
        "exact_evidence_rows": exact_evidence_rows,
        "source_note_text_rows": source_note_text_rows,
        "typed_event_complete_rows": typed_event_complete_rows,
        "projection_policy_complete_rows": projection_policy_complete_rows,
        "final_label_policy_connected": final_policy_connected,
        "slice_counts": dict(
            sorted(Counter(str(row["slice_id"]) for row in rows).items())
        ),
        "event_kind_counts": dict(
            sorted(
                Counter(str(row["clinical_event"]["event_kind"]) for row in rows).items()
            )
        ),
        "projection_owner_counts": dict(
            sorted(
                Counter(
                    str(row["projection_policy"]["projection_owner"]) for row in rows
                ).items()
            )
        ),
        "target_mechanism_counts": dict(
            sorted(Counter(str(row["target_mechanism"]) for row in rows).items())
        ),
        "claim_boundary": (
            "Validation-development boundary_event_validation_panel_v1. It emits "
            "only supported exact-evidence typed-event rows, suppresses unsupported "
            "records from the row artifact, omits source note text, and keeps "
            "final-label policy disconnected. It does not authorize candidate "
            "assembly or holdout use."
        ),
        "decision": (
            "boundary_event_validation_panel_v1_ready"
            if passed
            else "boundary_event_validation_panel_v1_failed"
        ),
        "recommended_next_step": (
            "Run h7_minimal_pair_panel_v1 and benchmark_renderer_fixture_v1 before "
            "connecting this typed-event surface to validation diagnostic assembly."
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
    rows, summary = build_rows_and_summary(
        records,
        max_rows_per_slice=max_rows_per_slice,
    )
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
        "# Gan 2026 Boundary Event Validation Panel v1",
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
        f"| source records scanned | {summary['source_record_count']} |",
        f"| emitted rows | {summary['row_count']} |",
        f"| suppressed source records | {summary['suppressed_source_records']} |",
        f"| unsupported candidate rows | {summary['unsupported_candidate_rows']} |",
        f"| boundary rows | {summary['boundary_rows']} |",
        f"| renderer rows | {summary['renderer_rows']} |",
        f"| hard rows | {summary['hard_rows']} |",
        f"| control rows | {summary['control_rows']} |",
        f"| exact evidence rows | {summary['exact_evidence_rows']} |",
        f"| source-note-text rows | {summary['source_note_text_rows']} |",
        f"| typed-event complete rows | {summary['typed_event_complete_rows']} |",
        f"| projection-policy complete rows | {summary['projection_policy_complete_rows']} |",
        f"| final-label policy connected | {summary['final_label_policy_connected']} |",
        "",
        "## Slices",
        "",
        "| Slice | Rows |",
        "| --- | ---: |",
    ]
    for slice_id, count in summary["slice_counts"].items():
        lines.append(f"| `{slice_id}` | {count} |")
    lines.extend(["", "## Event Kinds", "", "| Event kind | Rows |", "| --- | ---: |"])
    for event_kind, count in summary["event_kind_counts"].items():
        lines.append(f"| `{event_kind}` | {count} |")
    lines.extend(
        ["", "## Projection Owners", "", "| Owner | Rows |", "| --- | ---: |"]
    )
    for owner, count in summary["projection_owner_counts"].items():
        lines.append(f"| `{owner}` | {count} |")
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


def _to_v1_row(base_row: Mapping[str, Any]) -> dict[str, Any]:
    clinical_event = _clinical_event(base_row)
    projection_policy = _projection_policy(base_row)
    return {
        "artifact_kind": "gan2026_boundary_event_validation_panel_v1_row",
        "policy_name": POLICY_NAME,
        "source_row_index": base_row["source_row_index"],
        "split": base_row["split"],
        "split_manifest": base_row["split_manifest"],
        "slice_id": base_row["slice_id"],
        "panel_role": base_row["panel_role"],
        "target_family": base_row["target_family"],
        "target_mechanism": base_row["target_mechanism"],
        "clinical_event": clinical_event,
        "boundary_state": base_row["expected_boundary_state"],
        "selected_frequency_state": base_row["expected_clinical_final_state"],
        "projection_policy": projection_policy,
        "gan_rendered_label": base_row["expected_gan_rendered_label"],
        "evidence": base_row["expected_evidence_substring"],
        "exact_evidence": base_row["exact_evidence"],
        "gold_label": base_row["gold_label"],
        "source_note_text": None,
        "source_note_text_present": False,
        "generator_action": "emit_typed_event_candidate",
        "unsupported_candidate_suppressed": False,
        "final_label_policy_connected": False,
        "promotion_scope": "validation_event_panel_no_final_label_promotion",
        "claim_boundary": "validation_development_only_no_holdout_use",
    }


def _clinical_event(row: Mapping[str, Any]) -> dict[str, str]:
    component_owner = str(row["expected_component"])
    selected_state = str(row["expected_clinical_final_state"])
    event_kind = (
        "benchmark_format_convention"
        if component_owner == "benchmark_renderer"
        else selected_state
    )
    return {
        "event_target": "seizure",
        "event_kind": event_kind,
        "event_state": selected_state,
        "component_owner": component_owner,
    }


def _projection_policy(row: Mapping[str, Any]) -> dict[str, str]:
    if row["expected_component"] == "benchmark_renderer":
        policy_id = "gan2026_benchmark_renderer_policy_v1"
        owner = "benchmark_renderer"
        stage = "benchmark_format_rendering"
    else:
        policy_id = "gan2026_boundary_projection_policy_v1"
        owner = "boundary_projection_policy"
        stage = "clinical_event_to_benchmark_label"
    return {
        "projection_policy_id": policy_id,
        "projection_owner": owner,
        "projection_stage": stage,
        "benchmark_format_rule_id": str(row["expected_benchmark_format_rule_id"]),
    }


def _clinical_event_complete(clinical_event: Mapping[str, Any]) -> bool:
    return all(
        bool(clinical_event.get(field))
        for field in ("event_target", "event_kind", "event_state", "component_owner")
    )


def _projection_policy_complete(projection_policy: Mapping[str, Any]) -> bool:
    return all(
        bool(projection_policy.get(field))
        for field in (
            "projection_policy_id",
            "projection_owner",
            "projection_stage",
            "benchmark_format_rule_id",
        )
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
