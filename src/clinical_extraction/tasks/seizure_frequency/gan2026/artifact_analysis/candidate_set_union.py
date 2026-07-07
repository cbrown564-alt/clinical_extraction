"""Build deterministic+LLM CandidateSet union artifacts for validation250."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.candidate_set_replay import (  # noqa: E501
    DEFAULT_JSONL_PATH as DEFAULT_DETERMINISTIC_JSONL_PATH,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.candidate_set_union import (
    DEFAULT_ARTIFACT_NAME,
    build_candidate_set_union_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

DEFAULT_LLM_JSONL_PATH = Path("experiments/gan2026_validation250_llm_candidate_set_v0.jsonl")
DEFAULT_JSONL_PATH = Path("experiments/gan2026_validation250_candidate_set_v1.jsonl")
DEFAULT_JSON_PATH = Path("experiments/gan2026_validation250_candidate_set_v1.json")
DEFAULT_REPORT_PATH = Path("experiments/gan2026_validation250_candidate_set_v1.md")
ARTIFACT_NAME = DEFAULT_ARTIFACT_NAME


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
        f"# {metadata['artifact_name']}",
        "",
        str(metadata["claim_boundary"]),
        "",
        "## Artifacts",
        "",
        f"- JSONL: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        "",
        "## Summary",
        "",
        f"- Rows: {metadata['row_count']}",
        f"- Total candidates: {summary['total_candidates']}",
        f"- Rows with no candidates: {summary['rows_with_no_candidates']}",
        f"- Mean candidates per row: {summary['mean_candidates_per_row']:.2f}",
        f"- Max candidates per row: {summary['max_candidates_per_row']}",
        f"- Rows with union assembly issues: {summary['rows_with_union_assembly_issues']}",
        f"- LLM missing candidate-set rows: {summary['llm_candidate_set_missing_rows']}",
        f"- LLM call-error rows: {summary['llm_call_error_rows']}",
        f"- LLM parse/validation issue rows: {summary['llm_parse_or_validation_issue_rows']}",
        f"- Merged duplicate candidates: {summary['merged_duplicate_candidates']}",
        (f"- Merged nested duplicate candidates: {summary['merged_nested_duplicate_candidates']}"),
        "",
        "## Candidate Kinds",
        "",
    ]
    for kind, count in summary["candidate_kind_counts"].items():
        lines.append(f"- `{kind}`: {count}")
    lines.extend(["", "## Source Types", ""])
    for source_type, count in summary["source_type_counts"].items():
        lines.append(f"- `{source_type}`: {count}")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--deterministic-jsonl",
        type=Path,
        default=DEFAULT_DETERMINISTIC_JSONL_PATH,
    )
    parser.add_argument("--llm-jsonl", type=Path, default=DEFAULT_LLM_JSONL_PATH)
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--artifact-name", default=ARTIFACT_NAME)
    args = parser.parse_args(argv)

    rows, metadata = build_candidate_set_union_rows(
        load_jsonl_rows(args.deterministic_jsonl),
        load_jsonl_rows(args.llm_jsonl),
        artifact_name=args.artifact_name,
    )
    write_jsonl_rows(rows, args.jsonl_path)
    write_summary_json(metadata, args.json_path)
    write_report(metadata, args.report_path, jsonl_path=args.jsonl_path, json_path=args.json_path)
    print(json.dumps(metadata["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
