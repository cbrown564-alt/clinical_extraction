"""Synthetic hard/control data for structured projection opportunity expansion."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)

PANEL_NAME = "gan2026_structured_synthetic_hard_opportunity_panel_v0"
POLICY_NAME = PANEL_NAME
SYNTHETIC_SOURCE_INDEX_BASE = 920_000
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_structured_synthetic_hard_opportunity_panel_v0_2026-06-05.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_structured_synthetic_hard_opportunity_panel_v0_2026-06-05.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_structured_synthetic_hard_opportunity_panel_v0_2026-06-05.md"
)


def build_synthetic_panel_rows() -> list[dict[str, Any]]:
    """Build synthetic hard/control rows for undercovered projection mechanisms."""

    rows = []
    row_offset = 0
    for family in _family_specs():
        for index in range(30):
            rows.append(
                _build_row(
                    family,
                    index,
                    panel_role="synthetic_hard",
                    row_offset=row_offset,
                )
            )
            row_offset += 1
        for index in range(30):
            rows.append(
                _build_row(
                    family,
                    index,
                    panel_role="synthetic_control",
                    row_offset=row_offset,
                )
            )
            row_offset += 1
    return rows


def summarize_synthetic_panel_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize the synthetic hard opportunity panel contract."""

    exact_evidence_rows = sum(
        str(row["expected_evidence_substring"]) in str(row["source_note_text"])
        for row in rows
    )
    family_counts = Counter(str(row["target_family"]) for row in rows)
    hard_family_counts = Counter(
        str(row["target_family"]) for row in rows if row["panel_role"] == "synthetic_hard"
    )
    control_family_counts = Counter(
        str(row["target_family"])
        for row in rows
        if row["panel_role"] == "synthetic_control"
    )
    projection_owner_counts = Counter(str(row["projection_owner"]) for row in rows)
    ready = (
        bool(rows)
        and exact_evidence_rows == len(rows)
        and sum(row["panel_role"] == "synthetic_hard" for row in rows) >= 60
        and all(bool(row["projection_ownership_explicit"]) for row in rows)
    )
    return {
        "artifact_kind": "gan2026_structured_synthetic_hard_opportunity_panel_summary",
        "policy_name": POLICY_NAME,
        "row_count": len(rows),
        "hard_rows": sum(row["panel_role"] == "synthetic_hard" for row in rows),
        "control_rows": sum(row["panel_role"] == "synthetic_control" for row in rows),
        "exact_evidence_rows": exact_evidence_rows,
        "family_counts": dict(sorted(family_counts.items())),
        "hard_family_counts": dict(sorted(hard_family_counts.items())),
        "control_family_counts": dict(sorted(control_family_counts.items())),
        "projection_owner_counts": dict(sorted(projection_owner_counts.items())),
        "holdout_authorized": False,
        "locked_test_row_level_artifacts_used": 0,
        "claim_boundary": (
            "Synthetic development data for undercovered structured projection "
            "opportunity mechanisms. It is not validation750, not holdout, not "
            "benchmark evidence, and not a final-label promotion artifact."
        ),
        "decision": (
            "ready_for_structured_projection_generator_smoke"
            if ready
            else "synthetic_panel_contract_failed"
        ),
        "recommended_next_step": (
            "Run a synthetic projection generator smoke over this panel. Promote "
            "only mechanism behavior that emits hard rows, suppresses matched "
            "controls, preserves exact evidence, and keeps projection ownership explicit."
        ),
    }


def materialize_synthetic_panel(
    *,
    output_jsonl_path: Path = DEFAULT_JSONL_PATH,
    output_json_path: Path = DEFAULT_JSON_PATH,
    output_report_path: Path = DEFAULT_REPORT_PATH,
) -> dict[str, Any]:
    rows = build_synthetic_panel_rows()
    summary = summarize_synthetic_panel_rows(rows)
    summary = {
        **summary,
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
        "# Gan 2026 Structured Synthetic Hard Opportunity Panel v0",
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
        f"| exact evidence rows | {summary['exact_evidence_rows']} |",
        f"| holdout authorized | {summary['holdout_authorized']} |",
        "",
        "## Families",
        "",
        "| Family | Total | Hard | Control |",
        "| --- | ---: | ---: | ---: |",
    ]
    for family, count in summary["family_counts"].items():
        lines.append(
            f"| `{family}` | {count} | "
            f"{summary['hard_family_counts'].get(family, 0)} | "
            f"{summary['control_family_counts'].get(family, 0)} |"
        )
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
            f"- Panel JSONL: `{summary['jsonl_artifact']}`",
            f"- Summary JSON: `{summary['json_artifact']}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _build_row(
    family: Mapping[str, Any],
    index: int,
    *,
    panel_role: str,
    row_offset: int,
) -> dict[str, Any]:
    is_hard = panel_role == "synthetic_hard"
    note_text, evidence = family["hard_case"](index) if is_hard else family["control_case"](index)
    return {
        "artifact_kind": "gan2026_structured_synthetic_hard_opportunity_panel_row",
        "policy_name": POLICY_NAME,
        "source_row_index": SYNTHETIC_SOURCE_INDEX_BASE + row_offset,
        "split": "synthetic_hard_control",
        "split_manifest": PANEL_NAME,
        "panel_role": panel_role,
        "target_family": family["target_family"],
        "expected_generator_action": "emit_candidate" if is_hard else "suppress_candidate",
        "current_label": family["hard_current_label"] if is_hard else family["control_label"],
        "expected_candidate_label": family["expected_candidate_label"] if is_hard else None,
        "unsafe_candidate_label": None if is_hard else family["unsafe_candidate_label"],
        "gold_label": family["expected_candidate_label"] if is_hard else family["control_label"],
        "expected_event_kind": family["event_kind"],
        "clinical_event_owner": family["clinical_event_owner"],
        "projection_owner": family["projection_owner"],
        "projection_ownership_basis": family["target_family"],
        "projection_stage": "clinical_event_to_benchmark_label",
        "projection_policy_id": family["projection_policy_id"],
        "benchmark_format_rule_id": family["benchmark_format_rule_id"],
        "projection_ownership_explicit": True,
        "expected_evidence_substring": evidence,
        "source_note_text": note_text,
        "claim_boundary": "synthetic_development_only_no_holdout_use",
    }


def _family_specs() -> list[dict[str, Any]]:
    return [
        {
            "target_family": "unknown_frequency",
            "hard_current_label": "seizure free for multiple year",
            "control_label": "seizure free for multiple year",
            "expected_candidate_label": "unknown",
            "unsafe_candidate_label": "unknown",
            "event_kind": "unknown_frequency",
            "clinical_event_owner": "typed_boundary_classifier",
            "projection_owner": "boundary_projection_policy",
            "projection_policy_id": "gan2026_boundary_projection_policy_v0",
            "benchmark_format_rule_id": "none_boundary_state_only",
            "hard_case": _unknown_hard,
            "control_case": _unknown_control,
        },
        {
            "target_family": "cluster_frequency",
            "hard_current_label": "1 per month",
            "control_label": "1 per month",
            "expected_candidate_label": "1 cluster per month, 3 per cluster",
            "unsafe_candidate_label": "1 cluster per month, 3 per cluster",
            "event_kind": "cluster_frequency",
            "clinical_event_owner": "typed_event_extractor",
            "projection_owner": "cluster_projection_policy",
            "projection_policy_id": "gan2026_cluster_projection_policy_v0",
            "benchmark_format_rule_id": "gan_cluster_completion",
            "hard_case": _cluster_hard,
            "control_case": _cluster_control,
        },
        {
            "target_family": "daily_frequency",
            "hard_current_label": "4 per year",
            "control_label": "4 per year",
            "expected_candidate_label": "1 per day",
            "unsafe_candidate_label": "1 per day",
            "event_kind": "frequency_rate",
            "clinical_event_owner": "typed_event_extractor",
            "projection_owner": "rate_projection_policy",
            "projection_policy_id": "gan2026_rate_projection_policy_v0",
            "benchmark_format_rule_id": "none_rate_projection_only",
            "hard_case": _daily_hard,
            "control_case": _daily_control,
        },
        {
            "target_family": "other_frequency",
            "hard_current_label": "no seizure frequency reference",
            "control_label": "no seizure frequency reference",
            "expected_candidate_label": "2 per week",
            "unsafe_candidate_label": "2 per week",
            "event_kind": "frequency_rate",
            "clinical_event_owner": "typed_event_extractor",
            "projection_owner": "rate_projection_policy",
            "projection_policy_id": "gan2026_rate_projection_policy_v0",
            "benchmark_format_rule_id": "none_rate_projection_only",
            "hard_case": _other_frequency_hard,
            "control_case": _other_frequency_control,
        },
    ]


def _unknown_hard(index: int) -> tuple[str, str]:
    evidence = f"events recur only with missed medication in month {index + 1}"
    return (
        "Interval history: prior summary says seizure-free for years. "
        f"The current account states that {evidence}; no reliable baseline count is kept.",
        evidence,
    )


def _unknown_control(index: int) -> tuple[str, str]:
    evidence = f"no seizures or aura-like spells have occurred during month {index + 1}"
    return (
        "Interval history: remission remains stable. "
        f"The family confirms that {evidence}.",
        evidence,
    )


def _cluster_hard(index: int) -> tuple[str, str]:
    evidence = (
        "one cluster every month with three seizures in each cluster "
        f"during cycle {index + 1}"
    )
    return (
        "Diary review: a simple monthly count misses grouped events. "
        f"The diary states {evidence}, with recovery between clusters.",
        evidence,
    )


def _cluster_control(index: int) -> tuple[str, str]:
    evidence = f"one seizure per month and no grouped events in diary cycle {index + 1}"
    return (
        "Diary review: the pattern is isolated rather than clustered. "
        f"The diary records {evidence}.",
        evidence,
    )


def _daily_hard(index: int) -> tuple[str, str]:
    evidence = f"one absence seizure each day over the last {index + 2} weeks"
    return (
        "Background lists a few convulsions per year. "
        f"The current school diary instead records {evidence}.",
        evidence,
    )


def _daily_control(index: int) -> tuple[str, str]:
    evidence = f"daily headaches but only four seizures per year in year {index + 1}"
    return (
        "The patient reports daily non-seizure symptoms during titration. "
        f"These are clarified as {evidence}.",
        evidence,
    )


def _other_frequency_hard(index: int) -> tuple[str, str]:
    evidence = f"two focal impaired-awareness seizures per week during block {index + 1}"
    return (
        "The assessment template initially omitted a frequency field. "
        f"The seizure diary nevertheless documents {evidence}.",
        evidence,
    )


def _other_frequency_control(index: int) -> tuple[str, str]:
    evidence = f"two brief dizzy spells per week but no epileptic seizures in block {index + 1}"
    return (
        "The symptom diary contains non-epileptic events. "
        f"It specifies {evidence}.",
        evidence,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Materialize synthetic structured hard-opportunity data."
    )
    parser.add_argument("--output-jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--output-report-path", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args()
    summary = materialize_synthetic_panel(
        output_jsonl_path=args.output_jsonl_path,
        output_json_path=args.output_json_path,
        output_report_path=args.output_report_path,
    )
    print(
        json.dumps(
            {
                "decision": summary["decision"],
                "hard_rows": summary["hard_rows"],
                "row_count": summary["row_count"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
