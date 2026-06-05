"""Synthetic hard/control expansion panel for structured candidate seed slices."""

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

PANEL_NAME = "gan2026_structured_seed_expansion_panel_v0"
POLICY_NAME = "gan2026_structured_seed_expansion_panel_v0"
SYNTHETIC_SOURCE_INDEX_BASE = 910_000
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_structured_seed_expansion_panel_v0_2026-06-05.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_structured_seed_expansion_panel_v0_2026-06-05.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_structured_seed_expansion_panel_v0_2026-06-05.md"
)


def build_seed_expansion_panel_rows() -> list[dict[str, Any]]:
    """Build a deterministic synthetic hard/control panel from clean seed slices."""

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


def summarize_seed_expansion_panel(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize the generated structured seed expansion panel."""

    family_counts = Counter(str(row["seed_family"]) for row in rows)
    hard_family_counts = Counter(
        str(row["seed_family"]) for row in rows if row["panel_role"] == "synthetic_hard"
    )
    control_family_counts = Counter(
        str(row["seed_family"]) for row in rows if row["panel_role"] == "synthetic_control"
    )
    exact_evidence_rows = sum(
        str(row["expected_evidence_substring"]) in str(row["source_note_text"])
        for row in rows
    )
    return {
        "artifact_kind": "gan2026_structured_seed_expansion_panel_summary",
        "policy_name": POLICY_NAME,
        "row_count": len(rows),
        "hard_case_rows": sum(row["panel_role"] == "synthetic_hard" for row in rows),
        "control_rows": sum(row["panel_role"] == "synthetic_control" for row in rows),
        "family_counts": dict(sorted(family_counts.items())),
        "hard_family_counts": dict(sorted(hard_family_counts.items())),
        "control_family_counts": dict(sorted(control_family_counts.items())),
        "exact_evidence_rows": exact_evidence_rows,
        "claim_boundary": (
            "Synthetic validation-development mechanism panel derived from clean "
            "structured seed slices. It is not validation750, not holdout, and not "
            "benchmark evidence."
        ),
        "decision": (
            "ready_for_structured_generator_smoke"
            if len(rows) == exact_evidence_rows
            and sum(row["panel_role"] == "synthetic_hard" for row in rows) >= 60
            else "panel_contract_failed"
        ),
        "recommended_next_step": (
            "Run the next typed event generator on this synthetic hard/control panel. "
            "Promote only to validation hard/control panels if it emits hard-case "
            "candidates while suppressing matched controls with exact evidence."
        ),
    }


def materialize_seed_expansion_panel(
    *,
    output_jsonl_path: Path = DEFAULT_JSONL_PATH,
    output_json_path: Path = DEFAULT_JSON_PATH,
    output_report_path: Path = DEFAULT_REPORT_PATH,
) -> dict[str, Any]:
    rows = build_seed_expansion_panel_rows()
    summary = summarize_seed_expansion_panel(rows)
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
        "# Gan 2026 Structured Seed Expansion Panel",
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
        f"| synthetic hard rows | {summary['hard_case_rows']} |",
        f"| synthetic control rows | {summary['control_rows']} |",
        f"| exact evidence rows | {summary['exact_evidence_rows']} |",
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
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            str(summary["recommended_next_step"]),
            "",
            "## Artifacts",
            "",
            f"- Panel JSONL: `{jsonl_path}`",
            f"- Summary JSON: `{json_path}`",
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
        "artifact_kind": "gan2026_structured_seed_expansion_panel_row",
        "policy_name": POLICY_NAME,
        "source_row_index": SYNTHETIC_SOURCE_INDEX_BASE + row_offset,
        "split": "synthetic_hard_control",
        "split_manifest": PANEL_NAME,
        "panel_role": panel_role,
        "seed_family": family["name"],
        "seed_slice": family["seed_slice"],
        "expected_generator_action": "emit_candidate" if is_hard else "suppress_candidate",
        "current_label": (
            family["hard_current_label"] if is_hard else family["control_current_label"]
        ),
        "expected_candidate_label": family["expected_candidate_label"] if is_hard else None,
        "unsafe_candidate_label": None if is_hard else family["unsafe_candidate_label"],
        "expected_final_label": (
            family["expected_final_label"] if is_hard else family["control_current_label"]
        ),
        "expected_event_kind": family["event_kind"],
        "expected_evidence_substring": evidence,
        "source_note_text": note_text,
        "claim_boundary": "synthetic_development_only_no_holdout_use",
    }


def _family_specs() -> list[dict[str, Any]]:
    return [
        {
            "name": "seizure_free_to_unknown",
            "seed_slice": "current_to_proposed_family=seizure_free->unknown",
            "hard_current_label": "seizure free for multiple year",
            "control_current_label": "seizure free for multiple year",
            "expected_candidate_label": "unknown",
            "unsafe_candidate_label": "unknown",
            "expected_final_label": "unknown",
            "event_kind": "unknown_frequency",
            "hard_case": _seizure_free_unknown_hard,
            "control_case": _seizure_free_unknown_control,
        },
        {
            "name": "yearly_to_daily",
            "seed_slice": "current_to_proposed_family=yearly->daily",
            "hard_current_label": "4 per year",
            "control_current_label": "4 per year",
            "expected_candidate_label": "1 per day",
            "unsafe_candidate_label": "1 per day",
            "expected_final_label": "1 per day",
            "event_kind": "frequency_rate",
            "hard_case": _yearly_daily_hard,
            "control_case": _yearly_daily_control,
        },
        {
            "name": "cluster_completion",
            "seed_slice": "current_to_proposed_family=monthly->cluster",
            "hard_current_label": "1 per month",
            "control_current_label": "1 per month",
            "expected_candidate_label": "1 cluster per month, 4 per cluster",
            "unsafe_candidate_label": "1 cluster per month, 4 per cluster",
            "expected_final_label": "1 cluster per month, 4 per cluster",
            "event_kind": "cluster_frequency",
            "hard_case": _cluster_completion_hard,
            "control_case": _cluster_completion_control,
        },
    ]


def _seizure_free_unknown_hard(index: int) -> tuple[str, str]:
    evidence = f"brief focal episodes continue without a reliable count in week {index + 1}"
    note = (
        "Clinic update: the historical problem list still says seizure-free for years. "
        f"However, the current interval history states that {evidence}. "
        "No numeric seizure frequency is documented."
    )
    return note, evidence


def _seizure_free_unknown_control(index: int) -> tuple[str, str]:
    evidence = f"no seizures or suspicious episodes have occurred in month {index + 1}"
    note = (
        "Clinic update: prior remission is reviewed. The current interval history says "
        f"that {evidence}, and medication adherence is stable."
    )
    return note, evidence


def _yearly_daily_hard(index: int) -> tuple[str, str]:
    evidence = f"now has one absence seizure per day over the last {index + 2} weeks"
    note = (
        "Background section lists four convulsions per year before medication changes. "
        f"The current history states the patient {evidence}, without convulsive injuries."
    )
    return note, evidence


def _yearly_daily_control(index: int) -> tuple[str, str]:
    evidence = "daily headaches but only four seizures per year"
    note = (
        "The patient describes daily symptoms during titration. These are clarified as "
        f"{evidence}; no daily seizures are reported."
    )
    return note, evidence


def _cluster_completion_hard(index: int) -> tuple[str, str]:
    evidence = "one cluster every month, usually four seizures in each cluster"
    note = (
        "Seizure diary review: simple monthly count alone underestimates burden. "
        f"The diary states {evidence}, with recovery between clusters."
    )
    return note, evidence


def _cluster_completion_control(index: int) -> tuple[str, str]:
    evidence = f"one seizure per month and no clustering in diary month {index + 1}"
    note = (
        "Seizure diary review: the patient reports a stable pattern of "
        f"{evidence}. There are no grouped events."
    )
    return note, evidence


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--output-report-path", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)
    summary = materialize_seed_expansion_panel(
        output_jsonl_path=args.output_jsonl_path,
        output_json_path=args.output_json_path,
        output_report_path=args.output_report_path,
    )
    print(
        json.dumps(
            {"decision": summary["decision"], "row_count": summary["row_count"]},
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
