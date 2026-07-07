"""Diagnostics for validation250 CandidateSet replay artifacts."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.candidate_set_replay import (  # noqa: E501
    DEFAULT_JSONL_PATH as DEFAULT_CANDIDATE_SET_JSONL_PATH,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateKind,
    CandidateSet,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

DEFAULT_JSONL_PATH = Path("experiments/gan2026_validation250_candidate_set_diagnostics_v0.jsonl")
DEFAULT_JSON_PATH = Path("experiments/gan2026_validation250_candidate_set_diagnostics_v0.json")
DEFAULT_REPORT_PATH = Path("experiments/gan2026_validation250_candidate_set_diagnostics_v0.md")
HIGH_BURDEN_THRESHOLD = 4
MAX_EXAMPLES_PER_SECTION = 12


def build_candidate_set_diagnostics(
    candidate_rows: Sequence[Mapping[str, Any]],
    records: Sequence[GanFrequencyRecord],
    *,
    high_burden_threshold: int = HIGH_BURDEN_THRESHOLD,
    source_artifact: str = str(DEFAULT_CANDIDATE_SET_JSONL_PATH),
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records_by_index = {record.source_row_index: record for record in records}
    diagnostics = [
        _diagnostic_row(
            row,
            record=records_by_index[int(row["source_row_index"])],
            high_burden_threshold=high_burden_threshold,
        )
        for row in candidate_rows
    ]
    return diagnostics, summarize_diagnostics(
        diagnostics,
        high_burden_threshold=high_burden_threshold,
        source_artifact=source_artifact,
    )


def summarize_diagnostics(
    diagnostics: Sequence[Mapping[str, Any]],
    *,
    high_burden_threshold: int = HIGH_BURDEN_THRESHOLD,
    source_artifact: str = str(DEFAULT_CANDIDATE_SET_JSONL_PATH),
) -> dict[str, Any]:
    rows_by_gold_kind: dict[str, Counter[str]] = defaultdict(Counter)
    compatible_by_gold_kind: dict[str, Counter[str]] = defaultdict(Counter)
    candidate_kind_rows: dict[str, int] = Counter()
    no_candidate_rows = []
    high_burden_rows = []
    incompatible_rows = []
    for row in diagnostics:
        gold_kind = str(row["gold_candidate_kind"])
        rows_by_gold_kind[gold_kind]["rows"] += 1
        if row["candidate_count"] == 0:
            no_candidate_rows.append(row)
        if row["candidate_count"] >= high_burden_threshold:
            high_burden_rows.append(row)
        if row["compatible_candidate_present"]:
            compatible_by_gold_kind[gold_kind]["covered"] += 1
        else:
            incompatible_rows.append(row)
        for kind in row["candidate_kinds_present"]:
            candidate_kind_rows[str(kind)] += 1

    return {
        "artifact_name": "gan2026_validation250_candidate_set_diagnostics_v0",
        "source_artifact": source_artifact,
        "row_count": len(diagnostics),
        "high_burden_threshold": high_burden_threshold,
        "claim_boundary": (
            "Validation250 extract-stage diagnostics only. Compatible-kind coverage "
            "is not normalized-label recall and makes no benchmark-comparable claim."
        ),
        "summary": {
            "rows_with_no_candidates": len(no_candidate_rows),
            "high_burden_rows": len(high_burden_rows),
            "compatible_kind_coverage_rows": sum(
                bool(row["compatible_candidate_present"]) for row in diagnostics
            ),
            "compatible_kind_coverage_rate": _rate(
                sum(bool(row["compatible_candidate_present"]) for row in diagnostics),
                len(diagnostics),
            ),
            "incompatible_or_empty_rows": len(incompatible_rows),
            "candidate_set_missing_rows": sum(
                row["candidate_set_status"] == "missing" for row in diagnostics
            ),
            "diagnostic_issue_rows": sum(bool(row["diagnostic_issues"]) for row in diagnostics),
            "candidate_kind_row_counts": dict(sorted(candidate_kind_rows.items())),
            "by_gold_candidate_kind": {
                kind: {
                    "rows": counts["rows"],
                    "compatible_kind_covered_rows": compatible_by_gold_kind[kind]["covered"],
                    "compatible_kind_coverage_rate": _rate(
                        compatible_by_gold_kind[kind]["covered"],
                        counts["rows"],
                    ),
                }
                for kind, counts in sorted(rows_by_gold_kind.items())
            },
            "no_candidate_source_row_indices": [
                int(row["source_row_index"]) for row in no_candidate_rows
            ],
            "high_burden_source_row_indices": [
                int(row["source_row_index"]) for row in high_burden_rows
            ],
            "incompatible_or_empty_source_row_indices": [
                int(row["source_row_index"]) for row in incompatible_rows
            ],
        },
        "inspection_examples": {
            "no_candidate_rows": _inspection_examples(no_candidate_rows),
            "high_burden_rows": _inspection_examples(high_burden_rows),
            "incompatible_or_empty_rows": _inspection_examples(incompatible_rows),
        },
    }


def write_summary_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_report(
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path = DEFAULT_JSONL_PATH,
    json_path: Path = DEFAULT_JSON_PATH,
) -> None:
    summary = metadata["summary"]
    lines = [
        "# Gan 2026 Validation250 Candidate Set Diagnostics",
        "",
        str(metadata["claim_boundary"]),
        "",
        "## Artifacts",
        "",
        f"- Diagnostic JSONL: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        f"- Candidate-set source: `{metadata['source_artifact']}`",
        "",
        "## Summary",
        "",
        f"- Rows: {metadata['row_count']}",
        f"- Rows with no candidates: {summary['rows_with_no_candidates']}",
        f"- High-burden rows: {summary['high_burden_rows']}",
        f"- Missing candidate-set rows: {summary['candidate_set_missing_rows']}",
        f"- Rows with diagnostic issues: {summary['diagnostic_issue_rows']}",
        (
            "- Compatible-kind coverage: "
            f"{summary['compatible_kind_coverage_rows']}/{metadata['row_count']} "
            f"({summary['compatible_kind_coverage_rate']:.3f})"
        ),
        f"- Incompatible or empty rows: {summary['incompatible_or_empty_rows']}",
        "",
        "## Coverage By Gold Candidate Kind",
        "",
        "| Gold candidate kind | Rows | Compatible-kind covered | Coverage rate |",
        "| --- | ---: | ---: | ---: |",
    ]
    for kind, values in summary["by_gold_candidate_kind"].items():
        lines.append(
            f"| `{kind}` | {values['rows']} | "
            f"{values['compatible_kind_covered_rows']} | "
            f"{values['compatible_kind_coverage_rate']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Inspection Examples",
            "",
            _example_section(
                "No Candidate Rows", metadata["inspection_examples"]["no_candidate_rows"]
            ),
            "",
            _example_section(
                "High-Burden Rows", metadata["inspection_examples"]["high_burden_rows"]
            ),
            "",
            _example_section(
                "Incompatible Or Empty Rows",
                metadata["inspection_examples"]["incompatible_or_empty_rows"],
            ),
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _diagnostic_row(
    row: Mapping[str, Any],
    *,
    record: GanFrequencyRecord,
    high_burden_threshold: int,
) -> dict[str, Any]:
    candidate_set_payload = row.get("candidate_set")
    candidate_set = (
        CandidateSet.model_validate(candidate_set_payload)
        if candidate_set_payload is not None
        else None
    )
    candidates = candidate_set.candidates if candidate_set is not None else []
    candidate_kinds = sorted({candidate.candidate_kind for candidate in candidates})
    gold_candidate_kind = _gold_candidate_kind(record)
    compatible = _compatible_kind_present(gold_candidate_kind, candidate_kinds)
    evidence = [candidate.evidence_span.text for candidate in candidates]
    diagnostic_issues = []
    if candidate_set is None:
        diagnostic_issues.append("candidate_set_missing")
    if row.get("call_error"):
        diagnostic_issues.append("call_error")
    if row.get("parse_errors"):
        diagnostic_issues.append("parse_or_validation_errors")
    return {
        "source_row_index": record.source_row_index,
        "split": row.get("split", "validation"),
        "candidate_set_status": "present" if candidate_set is not None else "missing",
        "candidate_count": len(candidates),
        "candidate_kinds_present": candidate_kinds,
        "gold_label": record.gold_normalized_label,
        "gold_label_kind": record.gold_label_kind.value,
        "gold_candidate_kind": gold_candidate_kind,
        "compatible_candidate_present": compatible,
        "high_burden": len(candidates) >= high_burden_threshold,
        "diagnostic_issues": diagnostic_issues,
        "call_error": row.get("call_error"),
        "parse_errors": list(row.get("parse_errors") or []),
        "candidate_evidence": evidence,
        "note_excerpt": _note_excerpt(record.note_text),
    }


def _gold_candidate_kind(record: GanFrequencyRecord) -> CandidateKind:
    normalized = record.gold_normalized_label
    if "cluster" in normalized:
        return "cluster_frequency"
    if record.gold_label_kind is FrequencyLabelKind.FREQUENCY:
        return "frequency_rate"
    if record.gold_label_kind is FrequencyLabelKind.SEIZURE_FREE:
        return "seizure_free"
    if record.gold_label_kind in {
        FrequencyLabelKind.UNKNOWN,
        FrequencyLabelKind.UNRESOLVED_MULTIPLE,
    }:
        return "unknown_frequency"
    return "no_reference"


def _compatible_kind_present(
    gold_candidate_kind: str,
    candidate_kinds: Sequence[str],
) -> bool:
    return gold_candidate_kind in set(candidate_kinds)


def _inspection_examples(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "source_row_index": int(row["source_row_index"]),
            "candidate_count": int(row["candidate_count"]),
            "gold_label": row["gold_label"],
            "gold_candidate_kind": row["gold_candidate_kind"],
            "candidate_kinds_present": list(row["candidate_kinds_present"]),
            "candidate_evidence": list(row["candidate_evidence"])[:5],
            "note_excerpt": row["note_excerpt"],
        }
        for row in rows[:MAX_EXAMPLES_PER_SECTION]
    ]


def _example_section(title: str, examples: Sequence[Mapping[str, Any]]) -> str:
    lines = [f"### {title}", ""]
    if not examples:
        lines.append("- None.")
        return "\n".join(lines)
    for row in examples:
        evidence = "; ".join(str(item) for item in row["candidate_evidence"]) or "none"
        lines.append(
            "- "
            f"{row['source_row_index']}: gold `{row['gold_label']}` "
            f"({row['gold_candidate_kind']}), candidates "
            f"{row['candidate_count']} [{', '.join(row['candidate_kinds_present']) or 'none'}], "
            f"evidence: {evidence}. Excerpt: {row['note_excerpt']}"
        )
    return "\n".join(lines)


def _note_excerpt(note_text: str, *, max_chars: int = 220) -> str:
    text = " ".join(note_text.split())
    return text if len(text) <= max_chars else text[: max_chars - 3] + "..."


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--candidate-set-jsonl", type=Path, default=DEFAULT_CANDIDATE_SET_JSONL_PATH
    )
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    candidate_rows = load_jsonl_rows(args.candidate_set_jsonl)
    records = load_records_for_split("validation")[: len(candidate_rows)]
    diagnostic_rows, metadata = build_candidate_set_diagnostics(
        candidate_rows,
        records,
        source_artifact=str(args.candidate_set_jsonl),
    )
    write_jsonl_rows(diagnostic_rows, args.jsonl_path)
    write_summary_json(metadata, args.json_path)
    write_report(metadata, args.report_path, jsonl_path=args.jsonl_path, json_path=args.json_path)
    print(json.dumps(metadata["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
