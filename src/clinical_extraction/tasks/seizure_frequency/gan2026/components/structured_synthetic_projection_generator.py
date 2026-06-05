"""Projection-owner smoke over synthetic structured hard-opportunity rows."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

POLICY_NAME = "gan2026_structured_synthetic_projection_generator_v0"
REPRESENTATION_VERSION = "structured_event_projection_v0"
DEFAULT_PANEL_JSONL_PATH = Path(
    "experiments/gan2026_structured_synthetic_hard_opportunity_panel_v0_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSONL_PATH = Path(
    "experiments/gan2026_structured_synthetic_projection_generator_v0_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_structured_synthetic_projection_generator_v0_2026-06-05.json"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    "experiments/gan2026_structured_synthetic_projection_generator_v0_2026-06-05.md"
)


def build_projection_generator_rows(
    panel_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Run the synthetic projection generator over hard/control panel rows."""

    rows = [build_projection_generator_row(row) for row in panel_rows]
    rows.sort(
        key=lambda row: (
            row["target_family"],
            row["panel_role"],
            row["source_row_index"],
        )
    )
    return rows


def build_projection_generator_row(panel_row: Mapping[str, Any]) -> dict[str, Any]:
    """Generate a typed candidate when the synthetic mechanism should fire."""

    target_family = str(panel_row["target_family"])
    note_text = str(panel_row["source_note_text"])
    evidence = str(panel_row["expected_evidence_substring"])
    expected_action = str(panel_row["expected_generator_action"])
    should_emit = _should_emit(target_family, note_text, evidence)
    action = "emit_candidate" if should_emit else "suppress_candidate"
    return {
        "artifact_kind": "gan2026_structured_synthetic_projection_generator_row",
        "policy_name": POLICY_NAME,
        "representation_version": REPRESENTATION_VERSION,
        "source_row_index": int(panel_row["source_row_index"]),
        "split": panel_row["split"],
        "split_manifest": panel_row["split_manifest"],
        "panel_role": panel_row["panel_role"],
        "target_family": target_family,
        "generator_action": action,
        "expected_generator_action": expected_action,
        "expected_action_matched": action == expected_action,
        "candidate_id": (
            f"structured_synthetic:{panel_row['source_row_index']}"
            if should_emit
            else None
        ),
        "candidate_source": "structured_event" if should_emit else None,
        "candidate_label": panel_row["expected_candidate_label"] if should_emit else None,
        "unsafe_candidate_label": (
            None if should_emit else panel_row.get("unsafe_candidate_label")
        ),
        "candidate_event_kind": panel_row["expected_event_kind"] if should_emit else None,
        "candidate_evidence": evidence if should_emit else None,
        "exact_evidence": evidence_is_substring(note_text, evidence),
        "current_label": panel_row["current_label"],
        "gold_label": panel_row["gold_label"],
        "expected_final_label": panel_row["expected_candidate_label"],
        "clinical_event_owner": panel_row["clinical_event_owner"],
        "projection_owner": panel_row["projection_owner"],
        "projection_ownership_basis": panel_row["projection_ownership_basis"],
        "projection_stage": panel_row["projection_stage"],
        "projection_policy_id": panel_row["projection_policy_id"],
        "benchmark_format_rule_id": panel_row["benchmark_format_rule_id"],
        "projection_ownership_explicit": bool(panel_row["projection_ownership_explicit"]),
        "source_note_text": None,
        "source_note_text_present": False,
        "final_label_policy_connected": False,
        "promotion_scope": (
            "synthetic_structured_projection_generator_no_final_label_promotion"
        ),
        "claim_boundary": "synthetic_development_only_no_holdout_use",
    }


def summarize_projection_generator_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize synthetic projection-generator behavior and gate status."""

    hard_rows = [row for row in rows if row["panel_role"] == "synthetic_hard"]
    control_rows = [row for row in rows if row["panel_role"] == "synthetic_control"]
    hard_emit_rows = sum(row["generator_action"] == "emit_candidate" for row in hard_rows)
    control_suppressed_rows = sum(
        row["generator_action"] == "suppress_candidate" for row in control_rows
    )
    exact_evidence_rows = sum(bool(row["exact_evidence"]) for row in rows)
    projection_ownership_explicit_rows = sum(
        bool(row["projection_ownership_explicit"]) for row in rows
    )
    source_note_text_rows = sum(bool(row["source_note_text_present"]) for row in rows)
    mismatches = [row for row in rows if not row["expected_action_matched"]]
    synthetic_smoke_passed = (
        bool(rows)
        and hard_emit_rows == len(hard_rows)
        and control_suppressed_rows == len(control_rows)
        and exact_evidence_rows == len(rows)
        and projection_ownership_explicit_rows == len(rows)
        and source_note_text_rows == 0
        and not mismatches
    )
    return {
        "artifact_kind": "gan2026_structured_synthetic_projection_generator_summary",
        "policy_name": POLICY_NAME,
        "representation_version": REPRESENTATION_VERSION,
        "row_count": len(rows),
        "hard_rows": len(hard_rows),
        "control_rows": len(control_rows),
        "hard_emit_rows": hard_emit_rows,
        "control_suppressed_rows": control_suppressed_rows,
        "exact_evidence_rows": exact_evidence_rows,
        "projection_ownership_explicit_rows": projection_ownership_explicit_rows,
        "source_note_text_rows": source_note_text_rows,
        "expected_action_mismatch_rows": len(mismatches),
        "synthetic_smoke_passed": synthetic_smoke_passed,
        "family_counts": dict(
            sorted(Counter(str(row["target_family"]) for row in rows).items())
        ),
        "projection_owner_counts": dict(
            sorted(Counter(str(row["projection_owner"]) for row in rows).items())
        ),
        "clinical_event_owner_counts": dict(
            sorted(Counter(str(row["clinical_event_owner"]) for row in rows).items())
        ),
        "holdout_authorized": False,
        "locked_test_row_level_artifacts_used": 0,
        "claim_boundary": (
            "Synthetic development smoke for undercovered structured projection "
            "mechanisms. It requires hard emits, matched-control suppression, "
            "exact evidence, explicit projection ownership, no source note text in "
            "artifacts, and no locked-test row-level use."
        ),
        "decision": (
            "synthetic_projection_generator_smoke_passed"
            if synthetic_smoke_passed
            else "revise_synthetic_projection_generator"
        ),
        "recommended_next_step": (
            "Port only the passing high-precision mechanism behavior back to "
            "validation hard/control design; do not write a frozen test450 protocol "
            "until validation gates pass."
        ),
    }


def materialize_projection_generator_smoke(
    *,
    panel_jsonl_path: Path = DEFAULT_PANEL_JSONL_PATH,
    output_jsonl_path: Path = DEFAULT_OUTPUT_JSONL_PATH,
    output_json_path: Path = DEFAULT_OUTPUT_JSON_PATH,
    output_report_path: Path = DEFAULT_OUTPUT_REPORT_PATH,
) -> dict[str, Any]:
    panel_rows = load_jsonl_rows(panel_jsonl_path)
    rows = build_projection_generator_rows(panel_rows)
    summary = summarize_projection_generator_rows(rows)
    summary = {
        **summary,
        "source_panel_artifact": str(panel_jsonl_path),
        "jsonl_artifact": str(output_jsonl_path),
        "json_artifact": str(output_json_path),
        "report_artifact": str(output_report_path),
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
        "# Gan 2026 Structured Synthetic Projection Generator v0",
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
        f"| hard rows | {summary['hard_rows']} |",
        f"| control rows | {summary['control_rows']} |",
        f"| hard emit rows | {summary['hard_emit_rows']} |",
        f"| control suppressed rows | {summary['control_suppressed_rows']} |",
        f"| exact evidence rows | {summary['exact_evidence_rows']} |",
        (
            "| projection-ownership explicit rows | "
            f"{summary['projection_ownership_explicit_rows']} |"
        ),
        f"| source-note-text rows | {summary['source_note_text_rows']} |",
        f"| expected action mismatches | {summary['expected_action_mismatch_rows']} |",
        "",
        "## Families",
        "",
        "| Family | Rows |",
        "| --- | ---: |",
    ]
    for family, count in summary["family_counts"].items():
        lines.append(f"| `{family}` | {count} |")
    lines.extend(["", "## Projection Owners", "", "| Owner | Rows |", "| --- | ---: |"])
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
            f"- Projection generator JSONL: `{summary['jsonl_artifact']}`",
            f"- Summary JSON: `{summary['json_artifact']}`",
            f"- Source panel JSONL: `{summary['source_panel_artifact']}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _should_emit(target_family: str, note_text: str, evidence: str) -> bool:
    if not evidence_is_substring(note_text, evidence):
        return False
    lower_note = note_text.lower()
    lower_evidence = evidence.lower()
    if target_family == "unknown_frequency":
        return (
            "events recur only with missed medication" in lower_evidence
            and "no reliable baseline count is kept" in lower_note
        )
    if target_family == "cluster_frequency":
        return (
            "one cluster every month" in lower_evidence
            and "seizures in each cluster" in lower_evidence
            and "no grouped events" not in lower_evidence
        )
    if target_family == "daily_frequency":
        return "one absence seizure each day" in lower_evidence
    if target_family == "other_frequency":
        return (
            "focal impaired-awareness seizures per week" in lower_evidence
            and "no epileptic seizures" not in lower_evidence
        )
    return False


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel-jsonl-path", type=Path, default=DEFAULT_PANEL_JSONL_PATH)
    parser.add_argument("--output-jsonl-path", type=Path, default=DEFAULT_OUTPUT_JSONL_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    parser.add_argument("--output-report-path", type=Path, default=DEFAULT_OUTPUT_REPORT_PATH)
    args = parser.parse_args(argv)
    summary = materialize_projection_generator_smoke(
        panel_jsonl_path=args.panel_jsonl_path,
        output_jsonl_path=args.output_jsonl_path,
        output_json_path=args.output_json_path,
        output_report_path=args.output_report_path,
    )
    print(
        json.dumps(
            {
                "decision": summary["decision"],
                "synthetic_smoke_passed": summary["synthetic_smoke_passed"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
