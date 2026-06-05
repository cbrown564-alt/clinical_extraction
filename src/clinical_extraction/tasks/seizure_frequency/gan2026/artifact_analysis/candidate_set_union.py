"""Build deterministic+LLM CandidateSet union artifacts for validation250."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.candidate_set_replay import (  # noqa: E501
    DEFAULT_JSONL_PATH as DEFAULT_DETERMINISTIC_JSONL_PATH,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
    ExtractedCandidate,
    candidate_source_phrase,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

DEFAULT_LLM_JSONL_PATH = Path("experiments/gan2026_validation250_llm_candidate_set_v0.jsonl")
DEFAULT_JSONL_PATH = Path("experiments/gan2026_validation250_candidate_set_v1.jsonl")
DEFAULT_JSON_PATH = Path("experiments/gan2026_validation250_candidate_set_v1.json")
DEFAULT_REPORT_PATH = Path("experiments/gan2026_validation250_candidate_set_v1.md")
ARTIFACT_NAME = "gan2026_validation250_candidate_set_v1"


def build_candidate_set_union_rows(
    deterministic_rows: Sequence[Mapping[str, Any]],
    llm_rows: Sequence[Mapping[str, Any]],
    *,
    artifact_name: str = ARTIFACT_NAME,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    llm_by_index = {int(row["source_row_index"]): row for row in llm_rows}
    rows = [
        _union_row(
            deterministic_row,
            llm_by_index.get(int(deterministic_row["source_row_index"])),
            artifact_name=artifact_name,
        )
        for deterministic_row in deterministic_rows
    ]
    return rows, summarize_union_rows(rows, artifact_name=artifact_name)


def summarize_union_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    artifact_name: str = ARTIFACT_NAME,
) -> dict[str, Any]:
    candidates = [
        candidate
        for row in rows
        for candidate in row["candidate_set"]["candidates"]
    ]
    kind_counts = Counter(str(candidate["candidate_kind"]) for candidate in candidates)
    source_counts = Counter(str(candidate["source_type"]) for candidate in candidates)
    per_row_counts = [len(row["candidate_set"]["candidates"]) for row in rows]
    return {
        "artifact_name": artifact_name,
        "row_count": len(rows),
        "claim_boundary": (
            "Validation250 extract-stage deterministic+LLM candidate-set union only. "
            "No selection, normalization, projection, scoring, or locked-test work."
        ),
        "summary": {
            "candidate_sets": len(rows),
            "total_candidates": len(candidates),
            "candidate_kind_counts": dict(sorted(kind_counts.items())),
            "source_type_counts": dict(sorted(source_counts.items())),
            "rows_with_no_candidates": sum(count == 0 for count in per_row_counts),
            "mean_candidates_per_row": _mean(per_row_counts),
            "max_candidates_per_row": max(per_row_counts) if per_row_counts else 0,
            "rows_with_union_assembly_issues": sum(
                bool(row["candidate_set"]["assembly_issues"]) for row in rows
            ),
            "llm_candidate_set_missing_rows": sum(
                "llm_candidate_set_missing" in row["candidate_set"]["assembly_issues"]
                for row in rows
            ),
            "llm_call_error_rows": sum(
                any(issue.startswith("llm_call_error:") for issue in row["candidate_set"]["assembly_issues"])
                for row in rows
            ),
            "llm_parse_or_validation_issue_rows": sum(
                any(
                    issue.startswith("llm_parse_or_validation_error:")
                    for issue in row["candidate_set"]["assembly_issues"]
                )
                for row in rows
            ),
            "merged_duplicate_candidates": sum(
                "merged_duplicate_candidate" in issue
                for row in rows
                for candidate in row["candidate_set"]["candidates"]
                for issue in candidate.get("extraction_issues", [])
            ),
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
        "# Gan 2026 Validation250 CandidateSet Union V1",
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


def _union_row(
    deterministic_row: Mapping[str, Any],
    llm_row: Mapping[str, Any] | None,
    *,
    artifact_name: str,
) -> dict[str, Any]:
    source_row_index = int(deterministic_row["source_row_index"])
    deterministic_set = CandidateSet.model_validate(deterministic_row["candidate_set"])
    llm_set = (
        CandidateSet.model_validate(llm_row.get("candidate_set"))
        if llm_row and llm_row.get("candidate_set") is not None
        else None
    )
    candidates = list(deterministic_set.candidates)
    merged_by_key = {_dedupe_key(candidate): index for index, candidate in enumerate(candidates)}
    duplicate_count = 0
    if llm_set is not None:
        for candidate in llm_set.candidates:
            key = _dedupe_key(candidate)
            if key in merged_by_key:
                existing_index = merged_by_key[key]
                candidates[existing_index] = _merge_duplicate(candidates[existing_index], candidate)
                duplicate_count += 1
                continue
            merged_by_key[key] = len(candidates)
            candidates.append(candidate)

    assembly_issues = [
        *deterministic_set.assembly_issues,
        *([] if llm_set is None else llm_set.assembly_issues),
        *_llm_row_issues(llm_row),
    ]
    if duplicate_count:
        assembly_issues.append(f"merged_duplicate_candidate_count:{duplicate_count}")

    candidate_set = CandidateSet(
        source_row_index=source_row_index,
        component_owner="candidate_set_union_deterministic_llm_v1",
        source_artifacts=sorted(
            set(deterministic_set.source_artifacts)
            | (set(llm_set.source_artifacts) if llm_set is not None else set())
        ),
        candidates=candidates,
        assembly_issues=assembly_issues,
    )
    return {
        "artifact_name": artifact_name,
        "split": deterministic_row.get("split", "validation"),
        "split_manifest": deterministic_row.get("split_manifest", "gan2026_split_v1"),
        "source_row_index": source_row_index,
        "candidate_set": candidate_set.model_dump(),
        "union_summary": {
            "deterministic_candidate_count": len(deterministic_set.candidates),
            "llm_candidate_count": len(llm_set.candidates) if llm_set is not None else 0,
            "merged_duplicate_candidate_count": duplicate_count,
            "union_candidate_count": len(candidate_set.candidates),
        },
        "call_error": llm_row.get("call_error") if llm_row else None,
        "parse_errors": list(llm_row.get("parse_errors") or []) if llm_row else [],
    }


def _merge_duplicate(
    existing: ExtractedCandidate,
    duplicate: ExtractedCandidate,
) -> ExtractedCandidate:
    return existing.model_copy(
        update={
            "source_ids": sorted(set(existing.source_ids) | set(duplicate.source_ids)),
            "extraction_issues": [
                *existing.extraction_issues,
                (
                    "merged_duplicate_candidate:"
                    f"{duplicate.source_type}:{duplicate.candidate_id}"
                ),
                *[
                    f"duplicate_issue:{issue}"
                    for issue in duplicate.extraction_issues
                ],
            ],
        }
    )


def _llm_row_issues(llm_row: Mapping[str, Any] | None) -> list[str]:
    if llm_row is None or llm_row.get("candidate_set") is None:
        issues = ["llm_candidate_set_missing"]
    else:
        issues = []
    if llm_row and llm_row.get("call_error"):
        issues.append(f"llm_call_error:{llm_row['call_error']}")
    if llm_row:
        issues.extend(
            f"llm_parse_or_validation_error:{error}"
            for error in llm_row.get("parse_errors") or []
        )
    return issues


def _dedupe_key(candidate: ExtractedCandidate) -> tuple[str, str, str]:
    return (
        candidate.candidate_kind,
        _normalize(candidate.evidence_span.text),
        _normalize(candidate_source_phrase(candidate) or ""),
    )


def _normalize(text: str) -> str:
    return " ".join(text.strip().lower().split())


def _mean(values: Sequence[int]) -> float:
    return sum(values) / len(values) if values else 0.0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deterministic-jsonl", type=Path, default=DEFAULT_DETERMINISTIC_JSONL_PATH)
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
