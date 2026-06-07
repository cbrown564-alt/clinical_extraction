"""Build validation candidate-set replay artifacts for the architecture reset."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    SCHEMA_VERSION,
    CandidateSet,
    candidate_source_phrase,
    deterministic_candidate_set_from_raw,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    load_records_for_split,
    load_split_manifest,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic import (
    deterministic_extraction,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)

ARTIFACT_NAME = "gan2026_validation250_candidate_set_v0"
MAX_VALIDATION_LIMIT = 750
DEFAULT_JSONL_PATH = Path("experiments/gan2026_validation250_candidate_set_v0.jsonl")
DEFAULT_JSON_PATH = Path("experiments/gan2026_validation250_candidate_set_v0.json")
DEFAULT_REPORT_PATH = Path("experiments/gan2026_validation250_candidate_set_v0.md")


def build_validation250_candidate_set_rows(
    records: Sequence[GanFrequencyRecord],
    *,
    split: str = "validation",
    split_manifest: str = "gan2026_split_v1",
    limit: int = 250,
    artifact_name: str = ARTIFACT_NAME,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Build source-near deterministic candidate sets for the validation250 surface."""

    surface = list(records[:limit])
    rows = [
        _candidate_set_row(record, split=split, split_manifest=split_manifest)
        for record in surface
    ]
    for row in rows:
        row["artifact_name"] = artifact_name
    return rows, summarize_candidate_set_rows(
        rows,
        split=split,
        split_manifest=split_manifest,
        artifact_name=artifact_name,
    )


def summarize_candidate_set_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    split: str = "validation",
    split_manifest: str = "gan2026_split_v1",
    artifact_name: str = ARTIFACT_NAME,
) -> dict[str, Any]:
    candidates = [
        candidate
        for row in rows
        for candidate in row["candidate_set"]["candidates"]
    ]
    kind_counts = Counter(str(candidate["candidate_kind"]) for candidate in candidates)
    source_type_counts = Counter(str(candidate["source_type"]) for candidate in candidates)
    per_row_counts = [len(row["candidate_set"]["candidates"]) for row in rows]
    source_phrase_missing = sum(
        candidate_source_phrase(candidate) is None
        for row in rows
        for candidate in CandidateSet.model_validate(row["candidate_set"]).candidates
    )
    surface_label = f"validation{len(rows)}" if split == "validation" else split
    return {
        "artifact_name": artifact_name,
        "schema_version": SCHEMA_VERSION,
        "split": split,
        "split_manifest": split_manifest,
        "row_count": len(rows),
        "claim_boundary": (
            f"{surface_label} deterministic candidate-set replay only. No locked-test "
            "row-level work, scorer-facing claims, or final-label selection."
        ),
        "summary": {
            "candidate_sets": len(rows),
            "total_candidates": len(candidates),
            "rows_with_no_candidates": sum(count == 0 for count in per_row_counts),
            "min_candidates_per_row": min(per_row_counts) if per_row_counts else 0,
            "max_candidates_per_row": max(per_row_counts) if per_row_counts else 0,
            "mean_candidates_per_row": _mean(per_row_counts),
            "candidate_kind_counts": dict(sorted(kind_counts.items())),
            "source_type_counts": dict(sorted(source_type_counts.items())),
            "source_phrase_missing_candidates": source_phrase_missing,
            "assembly_issue_rows": sum(
                bool(row["candidate_set"].get("assembly_issues")) for row in rows
            ),
        },
    }


def write_summary_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_report(
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path = DEFAULT_JSONL_PATH,
    json_path: Path = DEFAULT_JSON_PATH,
) -> None:
    summary = metadata["summary"]
    lines = [
        f"# Gan 2026 {metadata['artifact_name']} Candidate Set Replay",
        "",
        str(metadata["claim_boundary"]),
        "",
        "## Artifacts",
        "",
        f"- JSONL: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        f"- Schema: `{metadata['schema_version']}`",
        "",
        "## Summary",
        "",
        f"- Rows: {metadata['row_count']}",
        f"- Candidate sets: {summary['candidate_sets']}",
        f"- Total candidates: {summary['total_candidates']}",
        f"- Rows with no candidates: {summary['rows_with_no_candidates']}",
        f"- Mean candidates per row: {summary['mean_candidates_per_row']:.2f}",
        f"- Max candidates per row: {summary['max_candidates_per_row']}",
        f"- Assembly issue rows: {summary['assembly_issue_rows']}",
        "",
        "## Candidate Kinds",
        "",
    ]
    for kind, count in summary["candidate_kind_counts"].items():
        lines.append(f"- `{kind}`: {count}")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _candidate_set_row(
    record: GanFrequencyRecord,
    *,
    split: str,
    split_manifest: str,
) -> dict[str, Any]:
    raw_candidates = deterministic_extraction._extract_candidates(record.note_text)  # noqa: SLF001
    candidate_set = deterministic_candidate_set_from_raw(
        raw_candidates,
        note_text=record.note_text,
        source_row_index=record.source_row_index,
        component_owner="deterministic_candidate_extraction",
        source_artifact="gan2026_deterministic_raw_candidates",
    )
    return {
        "artifact_name": ARTIFACT_NAME,
        "split": split,
        "split_manifest": split_manifest,
        "source_row_index": record.source_row_index,
        "candidate_set": candidate_set.model_dump(),
    }


def _mean(values: Sequence[int]) -> float:
    return sum(values) / len(values) if values else 0.0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=("validation", "test", "train"), default="validation")
    parser.add_argument("--limit", type=int, default=250)
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--artifact-name", default=ARTIFACT_NAME)
    args = parser.parse_args(argv)

    if args.limit > MAX_VALIDATION_LIMIT:
        parser.error(f"candidate-set replay is capped at validation{MAX_VALIDATION_LIMIT}")
    records = load_records_for_split(args.split)
    split_manifest = str(load_split_manifest().get("manifest_version", "gan2026_split_v1"))
    rows, metadata = build_validation250_candidate_set_rows(
        records,
        split=args.split,
        split_manifest=split_manifest,
        limit=args.limit,
        artifact_name=args.artifact_name,
    )
    write_jsonl_rows(rows, args.jsonl_path)
    write_summary_json(metadata, args.json_path)
    write_report(metadata, args.report_path, jsonl_path=args.jsonl_path, json_path=args.json_path)
    print(json.dumps(metadata["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
