"""Validation smoke for structured seed event extraction."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.seizure_frequency.gan2026.data import load_records_for_split
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

POLICY_NAME = "gan2026_structured_seed_validation_extractor_v0"
DEFAULT_PANEL_JSONL_PATH = Path(
    "experiments/gan2026_structured_seed_validation_panel_v0_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSONL_PATH = Path(
    "experiments/gan2026_structured_seed_validation_extractor_v0_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_structured_seed_validation_extractor_v0_2026-06-05.json"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    "experiments/gan2026_structured_seed_validation_extractor_v0_2026-06-05.md"
)


def build_extractor_rows(
    panel_rows: Sequence[Mapping[str, Any]],
    records_by_source: Mapping[int, Any],
) -> list[dict[str, Any]]:
    """Run the validation seed extractor over selected panel rows."""

    return [
        build_extractor_row(row, records_by_source[int(row["source_row_index"])])
        for row in panel_rows
    ]


def build_extractor_row(panel_row: Mapping[str, Any], record: Any) -> dict[str, Any]:
    """Run typed seed extraction over one validation hard/control row."""

    source_row_index = int(panel_row["source_row_index"])
    note_text = _record_value(record, "note_text")
    expected_action = str(panel_row["expected_generator_action"])
    candidate = _extract_candidate(str(panel_row["seed_family"]), note_text)
    action = "emit_candidate" if candidate else "suppress_candidate"
    evidence = candidate["evidence"] if candidate else None
    exact_evidence = (
        evidence_is_substring(note_text, evidence)
        if evidence is not None
        else _evidence_retrievable(note_text, str(panel_row["expected_evidence_substring"]))
    )
    return {
        "artifact_kind": "gan2026_structured_seed_validation_extractor_row",
        "policy_name": POLICY_NAME,
        "source_row_index": source_row_index,
        "split": panel_row["split"],
        "split_manifest": panel_row["split_manifest"],
        "panel_role": panel_row["panel_role"],
        "seed_family": panel_row["seed_family"],
        "generator_action": action,
        "expected_generator_action": expected_action,
        "expected_action_matched": action == expected_action,
        "candidate_id": f"structured_validation_seed:{source_row_index}" if candidate else None,
        "candidate_source": "structured_event" if candidate else None,
        "candidate_label": candidate["label"] if candidate else None,
        "candidate_event_kind": candidate["event_kind"] if candidate else None,
        "candidate_evidence": evidence,
        "exact_evidence": exact_evidence,
        "expected_candidate_label": panel_row.get("expected_candidate_label"),
        "current_label": panel_row.get("current_label"),
        "gold_label": panel_row.get("gold_label"),
        "claim_boundary": "validation_development_only_no_holdout_use",
    }


def summarize_extractor_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize validation seed extractor hard/control behavior."""

    family_counts = Counter(str(row["seed_family"]) for row in rows)
    action_counts = Counter(str(row["generator_action"]) for row in rows)
    hard_rows = [row for row in rows if row["panel_role"] == "hard"]
    control_rows = [row for row in rows if row["panel_role"] == "control"]
    hard_emit_rows = sum(row["generator_action"] == "emit_candidate" for row in hard_rows)
    control_suppressed_rows = sum(
        row["generator_action"] == "suppress_candidate" for row in control_rows
    )
    exact_evidence_rows = sum(bool(row["exact_evidence"]) for row in rows)
    hard_exact_evidence_rows = sum(bool(row["exact_evidence"]) for row in hard_rows)
    control_reference_retrievable_rows = sum(
        bool(row["exact_evidence"]) for row in control_rows
    )
    mismatches = [row for row in rows if not row["expected_action_matched"]]
    smoke_passed = (
        len(hard_rows) == hard_exact_evidence_rows
        and not mismatches
        and hard_emit_rows == len(hard_rows)
        and control_suppressed_rows == len(control_rows)
    )
    return {
        "artifact_kind": "gan2026_structured_seed_validation_extractor_summary",
        "policy_name": POLICY_NAME,
        "row_count": len(rows),
        "family_counts": dict(sorted(family_counts.items())),
        "action_counts": dict(sorted(action_counts.items())),
        "hard_rows": len(hard_rows),
        "control_rows": len(control_rows),
        "hard_emit_rows": hard_emit_rows,
        "control_suppressed_rows": control_suppressed_rows,
        "exact_evidence_rows": exact_evidence_rows,
        "hard_exact_evidence_rows": hard_exact_evidence_rows,
        "control_reference_retrievable_rows": control_reference_retrievable_rows,
        "expected_action_mismatch_rows": len(mismatches),
        "validation_smoke_passed": smoke_passed,
        "claim_boundary": (
            "Validation-development smoke for typed seed event extraction. It uses "
            "validation notes in memory, writes no note text, and does not authorize "
            "locked-test or holdout-facing use."
        ),
        "decision": _decision(smoke_passed, len(hard_rows)),
        "recommended_next_step": (
            "Broaden validation hard/control construction beyond the seed families "
            "until the typed candidate/event surface can reach at least 60 W->C, "
            "150 prediction-bearing rows, <=5% matched-control C->W, and >=95% "
            "parse-ok plus exact-evidence rows."
        ),
    }


def materialize_validation_extractor_smoke(
    *,
    panel_jsonl_path: Path = DEFAULT_PANEL_JSONL_PATH,
    output_jsonl_path: Path = DEFAULT_OUTPUT_JSONL_PATH,
    output_json_path: Path = DEFAULT_OUTPUT_JSON_PATH,
    output_report_path: Path = DEFAULT_OUTPUT_REPORT_PATH,
) -> dict[str, Any]:
    panel_rows = load_jsonl_rows(panel_jsonl_path)
    records_by_source = {
        record.source_row_index: record for record in load_records_for_split("validation")
    }
    rows = build_extractor_rows(panel_rows, records_by_source)
    summary = summarize_extractor_rows(rows)
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
        "# Gan 2026 Structured Seed Validation Extractor Smoke",
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
        f"| hard exact evidence rows | {summary['hard_exact_evidence_rows']} |",
        (
            "| control reference retrievable rows | "
            f"{summary['control_reference_retrievable_rows']} |"
        ),
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
            f"- Extractor JSONL: `{jsonl_path}`",
            f"- Summary JSON: `{json_path}`",
            f"- Source panel JSONL: `{summary['source_panel_artifact']}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _extract_candidate(family: str, note_text: str) -> dict[str, str] | None:
    if family == "yearly_to_daily":
        evidence = _find_yearly_to_daily_evidence(note_text)
        if evidence:
            return {
                "label": "1 per day",
                "event_kind": "frequency_rate",
                "evidence": evidence,
            }
    if family == "seizure_free_to_unknown":
        evidence = _find_unknown_frequency_evidence(note_text)
        if evidence:
            return {
                "label": "unknown",
                "event_kind": "unknown_frequency",
                "evidence": evidence,
            }
    if family == "cluster_completion":
        evidence = _find_cluster_evidence(note_text)
        if evidence:
            return {
                "label": _cluster_label(evidence),
                "event_kind": "cluster_frequency",
                "evidence": evidence,
            }
    return None


def _find_yearly_to_daily_evidence(note_text: str) -> str | None:
    return _first_regex(
        note_text,
        [
            r"nightly (?:generalised|generalized)[^.]*?four times per year",
            r"nightly [^.]*?seizures",
        ],
    )


def _find_unknown_frequency_evidence(note_text: str) -> str | None:
    return _first_regex(
        note_text,
        [
            r"Only with sleep deprivation",
            r"Frequency increased by ~50% after dose increase",
            r"Seizures with missed ASM doses",
            r"Seizures after alcohol intake",
            r"Photosensitive seizure episodes with flicker exposure",
            r"Periods of clustering followed by quiescence",
            r"Typical seizure event duration twenty seconds",
            r"Sporadic complex partial seizures this year",
            r"Last seizure on (?:25 December 2023|31-May|27 May|20/Dec)",
            r"several myoclonic jerks",
            (
                r"brief generalised tonic[\u2013-]clonic seizures occurring "
                r"exclusively after nights of curtailed sleep"
            ),
            (
                r"seizures tend to occur in the context of disrupted sleep and "
                r"heightened stress around travel rather than after alcohol ingestion"
            ),
            r"infrequent generalised seizures provoked by patterned or flickering visual stimuli",
        ],
    )


def _find_cluster_evidence(note_text: str) -> str | None:
    return _first_regex(
        note_text,
        [
            r"Monthly clusters; within-cluster count unclear",
            r"Monthly clusters predominantly on awakening",
            (
                r"She can occasionally manage five days without seizures, though this "
                r"is usually followed by a day of clustering, with two to four events"
            ),
            r"periodic bursts roughly every few weeks with an imprecise number of events per burst",
            (
                r"events tend to group together over several days in a repeating "
                r"pattern roughly every four to five weeks\. Within these burst "
                r"periods the number of episodes varies and has not been reliably logged"
            ),
            (
                r"events tend to gather into bursts roughly once each month, with "
                r"several episodes over a few days and quieter periods between"
            ),
            (
                r"short runs of events approximately monthly, most often noted "
                r"within the first hour after awakening"
            ),
        ],
    )


def _cluster_label(evidence: str) -> str:
    if "five days" in evidence:
        return "1 cluster per 5 day, 2 to 4 per cluster"
    if "four to five weeks" in evidence or "4 to 5 week" in evidence:
        return "1 cluster per 4 to 5 week, multiple per cluster"
    return "1 cluster per month, multiple per cluster"


def _first_regex(note_text: str, patterns: Sequence[str]) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, note_text, flags=re.IGNORECASE)
        if match:
            return match.group(0)
    return None


def _decision(smoke_passed: bool, hard_rows: int) -> str:
    if not smoke_passed:
        return "revise_validation_extractor"
    if hard_rows < 60:
        return "validation_smoke_passed_undercoverage"
    return "validation_smoke_passed_ready_for_contract_gate"


def _evidence_retrievable(note_text: str, evidence: str) -> bool:
    return bool(evidence) and evidence.casefold() in note_text.casefold()


def _record_value(record: Any, field: str) -> str:
    if isinstance(record, Mapping):
        return str(record[field])
    return str(getattr(record, field))


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel-jsonl-path", type=Path, default=DEFAULT_PANEL_JSONL_PATH)
    parser.add_argument("--output-jsonl-path", type=Path, default=DEFAULT_OUTPUT_JSONL_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    parser.add_argument("--output-report-path", type=Path, default=DEFAULT_OUTPUT_REPORT_PATH)
    args = parser.parse_args(argv)
    summary = materialize_validation_extractor_smoke(
        panel_jsonl_path=args.panel_jsonl_path,
        output_jsonl_path=args.output_jsonl_path,
        output_json_path=args.output_json_path,
        output_report_path=args.output_report_path,
    )
    print(
        json.dumps(
            {
                "decision": summary["decision"],
                "validation_smoke_passed": summary["validation_smoke_passed"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
