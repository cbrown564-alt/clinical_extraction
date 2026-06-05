"""Audit whether saved sources can broaden structured projection opportunities."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

POLICY_NAME = "gan2026_structured_projection_expansion_source_audit_v0"
DEFAULT_CURRENT_EXTRACTOR_JSONL_PATH = Path(
    "experiments/gan2026_structured_validation_projection_extractor_v0_2026-06-05.jsonl"
)
DEFAULT_CANDIDATE_SOURCE_JSONL_PATH = Path(
    "experiments/gan2026_structured_candidate_event_contract_v0_"
    "direct_labeler_validation750_panel_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSONL_PATH = Path(
    "experiments/gan2026_structured_projection_expansion_source_audit_v0_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_structured_projection_expansion_source_audit_v0_2026-06-05.json"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    "experiments/gan2026_structured_projection_expansion_source_audit_v0_2026-06-05.md"
)


def build_audit_rows(
    current_extractor_rows: Sequence[Mapping[str, Any]],
    candidate_source_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Compare current projection extractor coverage with a candidate source."""

    current_w_to_c_indices = {
        int(row["source_row_index"])
        for row in current_extractor_rows
        if row.get("prediction_bearing") and row.get("transition") == "W_to_C"
    }
    rows = [_audit_row(row, current_w_to_c_indices) for row in candidate_source_rows]
    rows.sort(
        key=lambda row: (
            not row["novel_clean_w_to_c"],
            row["transition"],
            row["source_row_index"],
        )
    )
    return rows


def summarize_audit_rows(
    rows: Sequence[Mapping[str, Any]],
    current_extractor_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Summarize whether the candidate source is safe for opportunity broadening."""

    current_w_to_c_rows = sum(
        row.get("prediction_bearing") and row.get("transition") == "W_to_C"
        for row in current_extractor_rows
    )
    clean_rows = [row for row in rows if row["clean_prediction_bearing"]]
    transition_counts = Counter(str(row["transition"]) for row in clean_rows)
    novel_clean_w_to_c_rows = sum(bool(row["novel_clean_w_to_c"]) for row in rows)
    candidate_clean_prediction_rows = len(clean_rows)
    candidate_clean_c_to_w_rows = transition_counts["C_to_W"]
    candidate_clean_c_to_w_rate = _rate(
        candidate_clean_c_to_w_rows,
        candidate_clean_prediction_rows,
    )
    safe_to_broaden = (
        novel_clean_w_to_c_rows >= 37
        and candidate_clean_c_to_w_rate <= 0.05
        and candidate_clean_c_to_w_rows == 0
    )
    return {
        "artifact_kind": "gan2026_structured_projection_expansion_source_audit_summary",
        "policy_name": POLICY_NAME,
        "candidate_source": "direct_labeler_structured_candidate_panel",
        "row_count": len(rows),
        "current_w_to_c_rows": current_w_to_c_rows,
        "candidate_clean_prediction_bearing_rows": candidate_clean_prediction_rows,
        "candidate_unclean_rows": sum(not row["clean_prediction_bearing"] for row in rows),
        "candidate_clean_w_to_c_rows": transition_counts["W_to_C"],
        "candidate_clean_c_to_w_rows": candidate_clean_c_to_w_rows,
        "candidate_clean_c_to_w_rate": candidate_clean_c_to_w_rate,
        "novel_clean_w_to_c_rows": novel_clean_w_to_c_rows,
        "candidate_clean_transition_counts": dict(sorted(transition_counts.items())),
        "safe_to_broaden_from_candidate_source": safe_to_broaden,
        "holdout_authorized": False,
        "locked_test_row_level_artifacts_used": 0,
        "claim_boundary": (
            "Validation-development expansion-source audit only. It compares saved "
            "validation artifacts, writes no note text, uses no locked-test row-level "
            "artifacts, and does not authorize holdout-facing use."
        ),
        "decision": (
            "direct_labeler_source_safe_for_broadening"
            if safe_to_broaden
            else "direct_labeler_source_rejected_for_broadening"
        ),
        "recommended_next_step": (
            "Do not broaden by importing the broad direct-labeler source. Build a "
            "new validation hard-opportunity panel from explicit projection-owner "
            "mechanisms and matched controls, then rerun the extractor smoke."
        ),
    }


def materialize_expansion_source_audit(
    *,
    current_extractor_jsonl_path: Path = DEFAULT_CURRENT_EXTRACTOR_JSONL_PATH,
    candidate_source_jsonl_path: Path = DEFAULT_CANDIDATE_SOURCE_JSONL_PATH,
    output_jsonl_path: Path = DEFAULT_OUTPUT_JSONL_PATH,
    output_json_path: Path = DEFAULT_OUTPUT_JSON_PATH,
    output_report_path: Path = DEFAULT_OUTPUT_REPORT_PATH,
) -> dict[str, Any]:
    current_rows = load_jsonl_rows(current_extractor_jsonl_path)
    candidate_rows = load_jsonl_rows(candidate_source_jsonl_path)
    rows = build_audit_rows(current_rows, candidate_rows)
    summary = summarize_audit_rows(rows, current_rows)
    summary = {
        **summary,
        "source_current_extractor_artifact": str(current_extractor_jsonl_path),
        "source_candidate_artifact": str(candidate_source_jsonl_path),
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
        "# Gan 2026 Structured Projection Expansion Source Audit v0",
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
        f"| current W->C rows | {summary['current_w_to_c_rows']} |",
        (
            "| candidate clean prediction-bearing rows | "
            f"{summary['candidate_clean_prediction_bearing_rows']} |"
        ),
        f"| candidate clean W->C rows | {summary['candidate_clean_w_to_c_rows']} |",
        f"| candidate clean C->W rows | {summary['candidate_clean_c_to_w_rows']} |",
        f"| novel clean W->C rows | {summary['novel_clean_w_to_c_rows']} |",
        (
            "| safe to broaden from candidate source | "
            f"{summary['safe_to_broaden_from_candidate_source']} |"
        ),
        f"| holdout authorized | {summary['holdout_authorized']} |",
        "",
        "## Clean Candidate Transitions",
        "",
        "| Transition | Rows |",
        "| --- | ---: |",
    ]
    for transition, count in summary["candidate_clean_transition_counts"].items():
        lines.append(f"| `{transition}` | {count} |")
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            str(summary["recommended_next_step"]),
            "",
            "## Artifacts",
            "",
            f"- Audit JSONL: `{summary['jsonl_artifact']}`",
            f"- Summary JSON: `{summary['json_artifact']}`",
            (
                "- Source current extractor JSONL: "
                f"`{summary['source_current_extractor_artifact']}`"
            ),
            f"- Source candidate JSONL: `{summary['source_candidate_artifact']}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _audit_row(
    row: Mapping[str, Any],
    current_w_to_c_indices: set[int],
) -> dict[str, Any]:
    source_row_index = int(row["source_row_index"])
    clean_prediction_bearing = (
        bool(row.get("prediction_bearing"))
        and bool(row.get("parse_ok"))
        and bool(row.get("exact_evidence"))
        and not row.get("contract_issues")
    )
    transition = str(row.get("transition"))
    return {
        "artifact_kind": "gan2026_structured_projection_expansion_source_audit_row",
        "policy_name": POLICY_NAME,
        "source_row_index": source_row_index,
        "candidate_id": row.get("candidate_id"),
        "candidate_source": row.get("candidate_source"),
        "clean_prediction_bearing": clean_prediction_bearing,
        "already_in_current_projection_extractor": source_row_index
        in current_w_to_c_indices,
        "novel_clean_w_to_c": (
            clean_prediction_bearing
            and transition == "W_to_C"
            and source_row_index not in current_w_to_c_indices
        ),
        "transition": transition,
        "current_label": row.get("current_label"),
        "proposed_label": row.get("proposed_label"),
        "gold_label": row.get("gold_label"),
        "event_kind": row.get("event_kind"),
        "parse_ok": bool(row.get("parse_ok")),
        "exact_evidence": bool(row.get("exact_evidence")),
        "contract_issues": list(row.get("contract_issues") or []),
        "evidence": row.get("evidence"),
        "source_note_text": None,
        "source_note_text_present": False,
        "claim_boundary": "validation_development_only_no_holdout_use",
    }


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Materialize the structured projection expansion-source audit."
    )
    parser.add_argument(
        "--current-extractor-jsonl-path",
        type=Path,
        default=DEFAULT_CURRENT_EXTRACTOR_JSONL_PATH,
    )
    parser.add_argument(
        "--candidate-source-jsonl-path",
        type=Path,
        default=DEFAULT_CANDIDATE_SOURCE_JSONL_PATH,
    )
    parser.add_argument("--output-jsonl-path", type=Path, default=DEFAULT_OUTPUT_JSONL_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    parser.add_argument("--output-report-path", type=Path, default=DEFAULT_OUTPUT_REPORT_PATH)
    args = parser.parse_args()
    summary = materialize_expansion_source_audit(
        current_extractor_jsonl_path=args.current_extractor_jsonl_path,
        candidate_source_jsonl_path=args.candidate_source_jsonl_path,
        output_jsonl_path=args.output_jsonl_path,
        output_json_path=args.output_json_path,
        output_report_path=args.output_report_path,
    )
    print(
        json.dumps(
            {
                "decision": summary["decision"],
                "novel_clean_w_to_c_rows": summary["novel_clean_w_to_c_rows"],
                "safe_to_broaden_from_candidate_source": summary[
                    "safe_to_broaden_from_candidate_source"
                ],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
