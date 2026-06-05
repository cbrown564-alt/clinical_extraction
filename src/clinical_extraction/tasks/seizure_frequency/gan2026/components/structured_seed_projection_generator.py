"""Projection-owner-aware structured seed generator smoke."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    structured_seed_event_generator,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

POLICY_NAME = "gan2026_structured_seed_projection_generator_v0"
REPRESENTATION_VERSION = "structured_event_projection_v0"
DEFAULT_PANEL_JSONL_PATH = Path(
    "experiments/gan2026_structured_seed_expansion_panel_v0_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSONL_PATH = Path(
    "experiments/gan2026_structured_seed_projection_generator_v0_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_structured_seed_projection_generator_v0_2026-06-05.json"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    "experiments/gan2026_structured_seed_projection_generator_v0_2026-06-05.md"
)


def build_projection_generator_rows(
    panel_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Run the projection-owner-aware seed generator over panel rows."""

    rows = [build_projection_generator_row(row) for row in panel_rows]
    rows.sort(key=lambda row: (row["seed_family"], row["panel_role"], row["source_row_index"]))
    return rows


def build_projection_generator_row(panel_row: Mapping[str, Any]) -> dict[str, Any]:
    """Run seed event generation and attach explicit projection ownership."""

    generator_row = structured_seed_event_generator.build_generator_row(panel_row)
    seed_family = str(panel_row["seed_family"])
    ownership = _ownership_for_seed_family(seed_family)
    return {
        **generator_row,
        "artifact_kind": "gan2026_structured_seed_projection_generator_row",
        "policy_name": POLICY_NAME,
        "representation_version": REPRESENTATION_VERSION,
        "candidate_source": (
            "structured_event" if generator_row["generator_action"] == "emit_candidate" else None
        ),
        "clinical_event_owner": ownership["clinical_event_owner"],
        "projection_owner": ownership["projection_owner"],
        "projection_ownership_basis": seed_family,
        "projection_stage": ownership["projection_stage"],
        "projection_ownership_explicit": True,
        "projection_input_label": panel_row["current_label"],
        "gan_rendered_label": generator_row["candidate_label"],
        "source_note_text": None,
        "source_note_text_present": False,
        "final_label_policy_connected": False,
        "promotion_scope": (
            "synthetic_structured_event_projection_generator_no_final_label_promotion"
        ),
        "claim_boundary": "synthetic_development_only_no_holdout_use",
    }


def summarize_projection_generator_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize synthetic projection-owner generator behavior."""

    hard_rows = [row for row in rows if row["panel_role"] == "synthetic_hard"]
    control_rows = [row for row in rows if row["panel_role"] == "synthetic_control"]
    hard_emit_rows = sum(row["generator_action"] == "emit_candidate" for row in hard_rows)
    control_suppressed_rows = sum(
        row["generator_action"] == "suppress_candidate" for row in control_rows
    )
    exact_evidence_rows = sum(bool(row["exact_evidence"]) for row in rows)
    mismatches = [row for row in rows if not row["expected_action_matched"]]
    projection_ownership_explicit_rows = sum(
        bool(row["projection_ownership_explicit"]) for row in rows
    )
    source_note_text_rows = sum(bool(row["source_note_text_present"]) for row in rows)
    synthetic_smoke_passed = (
        len(rows) == exact_evidence_rows
        and len(rows) == projection_ownership_explicit_rows
        and source_note_text_rows == 0
        and not mismatches
        and hard_emit_rows == len(hard_rows)
        and control_suppressed_rows == len(control_rows)
    )
    return {
        "artifact_kind": "gan2026_structured_seed_projection_generator_summary",
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
            sorted(Counter(str(row["seed_family"]) for row in rows).items())
        ),
        "clinical_event_owner_counts": dict(
            sorted(Counter(str(row["clinical_event_owner"]) for row in rows).items())
        ),
        "projection_owner_counts": dict(
            sorted(Counter(str(row["projection_owner"]) for row in rows).items())
        ),
        "holdout_authorized": False,
        "locked_test_row_level_artifacts_used": 0,
        "claim_boundary": (
            "Synthetic validation-development smoke for projection-owner-aware "
            "structured event generation. It writes no source note text, uses no "
            "locked-test artifacts, and is not benchmark evidence."
        ),
        "decision": (
            "promote_to_validation_projection_owner_panel"
            if synthetic_smoke_passed
            else "revise_projection_owner_generator"
        ),
        "recommended_next_step": (
            "Port this projection-owner schema to validation hard/control expansion, "
            "including matched controls and the boundary C->W no-regression case. "
            "Do not write a frozen test450 protocol until validation gates pass."
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
        "# Gan 2026 Structured Seed Projection Generator v0",
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
        "## Projection Owners",
        "",
        "| Owner | Rows |",
        "| --- | ---: |",
    ]
    for owner, count in summary["projection_owner_counts"].items():
        lines.append(f"| `{owner}` | {count} |")
    lines.extend(["", "## Families", "", "| Family | Rows |", "| --- | ---: |"])
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
            f"- Projection generator JSONL: `{summary['jsonl_artifact']}`",
            f"- Summary JSON: `{summary['json_artifact']}`",
            f"- Source panel JSONL: `{summary['source_panel_artifact']}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _ownership_for_seed_family(seed_family: str) -> dict[str, str]:
    if seed_family == "seizure_free_to_unknown":
        return {
            "clinical_event_owner": "typed_boundary_classifier",
            "projection_owner": "boundary_projection_policy",
            "projection_stage": "clinical_event_to_benchmark_label",
        }
    if seed_family == "yearly_to_daily":
        return {
            "clinical_event_owner": "typed_event_extractor",
            "projection_owner": "rate_projection_policy",
            "projection_stage": "clinical_event_to_benchmark_label",
        }
    if seed_family == "cluster_completion":
        return {
            "clinical_event_owner": "typed_event_extractor",
            "projection_owner": "cluster_projection_policy",
            "projection_stage": "clinical_event_to_benchmark_label",
        }
    return {
        "clinical_event_owner": "typed_event_extractor",
        "projection_owner": "structured_event_projection_policy",
        "projection_stage": "clinical_event_to_benchmark_label",
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Materialize the projection-owner-aware seed generator smoke."
    )
    parser.add_argument("--panel-jsonl-path", type=Path, default=DEFAULT_PANEL_JSONL_PATH)
    parser.add_argument("--output-jsonl-path", type=Path, default=DEFAULT_OUTPUT_JSONL_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    parser.add_argument("--output-report-path", type=Path, default=DEFAULT_OUTPUT_REPORT_PATH)
    args = parser.parse_args()
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
