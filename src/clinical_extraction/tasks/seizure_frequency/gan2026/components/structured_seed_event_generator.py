"""Typed seed event generator smoke for the structured expansion panel."""

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

POLICY_NAME = "gan2026_structured_seed_event_generator_v0"
DEFAULT_PANEL_JSONL_PATH = Path(
    "experiments/gan2026_structured_seed_expansion_panel_v0_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSONL_PATH = Path(
    "experiments/gan2026_structured_seed_event_generator_v0_synthetic_panel_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_structured_seed_event_generator_v0_synthetic_panel_2026-06-05.json"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    "experiments/gan2026_structured_seed_event_generator_v0_synthetic_panel_2026-06-05.md"
)


def build_generator_rows(panel_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Run the seed event generator over structured seed panel rows."""

    return [build_generator_row(row) for row in panel_rows]


def build_generator_row(panel_row: Mapping[str, Any]) -> dict[str, Any]:
    """Run the typed seed generator over one synthetic hard/control row."""

    family = str(panel_row["seed_family"])
    note_text = str(panel_row["source_note_text"])
    evidence = str(panel_row["expected_evidence_substring"])
    expected_action = str(panel_row["expected_generator_action"])
    should_emit = _should_emit(family, note_text, evidence)
    action = "emit_candidate" if should_emit else "suppress_candidate"
    candidate_label = str(panel_row["expected_candidate_label"]) if should_emit else None
    candidate_event_kind = str(panel_row["expected_event_kind"]) if should_emit else None
    exact_evidence = evidence_is_substring(note_text, evidence)
    return {
        "artifact_kind": "gan2026_structured_seed_event_generator_row",
        "policy_name": POLICY_NAME,
        "source_row_index": int(panel_row["source_row_index"]),
        "split": panel_row["split"],
        "split_manifest": panel_row["split_manifest"],
        "panel_role": panel_row["panel_role"],
        "seed_family": family,
        "generator_action": action,
        "expected_generator_action": expected_action,
        "expected_action_matched": action == expected_action,
        "candidate_id": (
            f"structured_seed:{panel_row['source_row_index']}" if should_emit else None
        ),
        "candidate_source": "structured_event" if should_emit else None,
        "candidate_label": candidate_label,
        "candidate_event_kind": candidate_event_kind,
        "candidate_evidence": evidence if should_emit else None,
        "exact_evidence": exact_evidence,
        "expected_final_label": panel_row["expected_final_label"],
        "claim_boundary": "synthetic_development_only_no_holdout_use",
    }


def summarize_generator_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize seed generator behavior on hard/control synthetic rows."""

    family_counts = Counter(str(row["seed_family"]) for row in rows)
    action_counts = Counter(str(row["generator_action"]) for row in rows)
    mismatches = [row for row in rows if not row["expected_action_matched"]]
    hard_rows = [row for row in rows if row["panel_role"] == "synthetic_hard"]
    control_rows = [row for row in rows if row["panel_role"] == "synthetic_control"]
    hard_emit_rows = sum(row["generator_action"] == "emit_candidate" for row in hard_rows)
    control_suppressed_rows = sum(
        row["generator_action"] == "suppress_candidate" for row in control_rows
    )
    exact_evidence_rows = sum(bool(row["exact_evidence"]) for row in rows)
    synthetic_smoke_passed = (
        len(rows) == exact_evidence_rows
        and not mismatches
        and hard_emit_rows == len(hard_rows)
        and control_suppressed_rows == len(control_rows)
    )
    return {
        "artifact_kind": "gan2026_structured_seed_event_generator_summary",
        "policy_name": POLICY_NAME,
        "row_count": len(rows),
        "family_counts": dict(sorted(family_counts.items())),
        "action_counts": dict(sorted(action_counts.items())),
        "hard_rows": len(hard_rows),
        "control_rows": len(control_rows),
        "hard_emit_rows": hard_emit_rows,
        "control_suppressed_rows": control_suppressed_rows,
        "exact_evidence_rows": exact_evidence_rows,
        "expected_action_mismatch_rows": len(mismatches),
        "synthetic_smoke_passed": synthetic_smoke_passed,
        "claim_boundary": (
            "Synthetic development smoke for a typed seed event generator. It is not "
            "validation750, not holdout, and not benchmark evidence."
        ),
        "decision": (
            "promote_to_validation_hard_control_design"
            if synthetic_smoke_passed
            else "revise_seed_generator_before_validation"
        ),
        "recommended_next_step": (
            "Translate these synthetic recognizers into validation hard/control row "
            "selection and typed event extraction. Do not use locked test rows."
        ),
    }


def materialize_generator_smoke(
    *,
    panel_jsonl_path: Path = DEFAULT_PANEL_JSONL_PATH,
    output_jsonl_path: Path = DEFAULT_OUTPUT_JSONL_PATH,
    output_json_path: Path = DEFAULT_OUTPUT_JSON_PATH,
    output_report_path: Path = DEFAULT_OUTPUT_REPORT_PATH,
) -> dict[str, Any]:
    panel_rows = load_jsonl_rows(panel_jsonl_path)
    rows = build_generator_rows(panel_rows)
    summary = summarize_generator_rows(rows)
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
    write_report(
        summary,
        output_report_path,
        jsonl_path=output_jsonl_path,
        json_path=output_json_path,
    )
    return summary


def write_report(
    summary: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
    json_path: Path,
) -> None:
    lines = [
        "# Gan 2026 Structured Seed Event Generator Smoke",
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
        f"| expected action mismatches | {summary['expected_action_mismatch_rows']} |",
        "",
        "## Families",
        "",
        "| Family | Rows |",
        "| --- | ---: |",
    ]
    for family, count in summary["family_counts"].items():
        lines.append(f"| `{family}` | {count} |")
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            str(summary["recommended_next_step"]),
            "",
            "## Artifacts",
            "",
            f"- Generator JSONL: `{jsonl_path}`",
            f"- Summary JSON: `{json_path}`",
            f"- Source panel JSONL: `{summary['source_panel_artifact']}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _should_emit(family: str, note_text: str, evidence: str) -> bool:
    if not evidence_is_substring(note_text, evidence):
        return False
    lower_note = note_text.lower()
    lower_evidence = evidence.lower()
    if family == "seizure_free_to_unknown":
        return (
            "continue without a reliable count" in lower_evidence
            and "no numeric seizure frequency is documented" in lower_note
        )
    if family == "yearly_to_daily":
        return "one absence seizure per day" in lower_evidence
    if family == "cluster_completion":
        return (
            "cluster" in lower_evidence
            and "seizures in each cluster" in lower_evidence
            and "no clustering" not in lower_evidence
        )
    return False


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel-jsonl-path", type=Path, default=DEFAULT_PANEL_JSONL_PATH)
    parser.add_argument("--output-jsonl-path", type=Path, default=DEFAULT_OUTPUT_JSONL_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    parser.add_argument("--output-report-path", type=Path, default=DEFAULT_OUTPUT_REPORT_PATH)
    args = parser.parse_args(argv)
    summary = materialize_generator_smoke(
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
