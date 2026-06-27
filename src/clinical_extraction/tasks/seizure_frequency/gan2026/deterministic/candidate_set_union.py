"""Merge deterministic and LLM CandidateSet rows for Gan 2026 extract-stage union."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
    ExtractedCandidate,
    RowContext,
    candidate_source_phrase,
)

DEFAULT_ARTIFACT_NAME = "gan2026_validation250_candidate_set_v1"


def build_candidate_set_union_rows(
    deterministic_rows: Sequence[Mapping[str, Any]],
    llm_rows: Sequence[Mapping[str, Any]],
    *,
    artifact_name: str = DEFAULT_ARTIFACT_NAME,
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
    artifact_name: str = DEFAULT_ARTIFACT_NAME,
) -> dict[str, Any]:
    candidates = [
        candidate
        for row in rows
        for candidate in row["candidate_set"]["candidates"]
    ]
    kind_counts = Counter(str(candidate["candidate_kind"]) for candidate in candidates)
    source_counts = Counter(str(candidate["source_type"]) for candidate in candidates)
    per_row_counts = [len(row["candidate_set"]["candidates"]) for row in rows]
    surface_label = f"validation{len(rows)}"
    return {
        "artifact_name": artifact_name,
        "row_count": len(rows),
        "claim_boundary": (
            f"{surface_label} extract-stage deterministic+LLM candidate-set union only. "
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
                any(
                    issue.startswith("llm_call_error:")
                    for issue in row["candidate_set"]["assembly_issues"]
                )
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
            "merged_nested_duplicate_candidates": sum(
                "merged_nested_duplicate_candidate" in issue
                for row in rows
                for candidate in row["candidate_set"]["candidates"]
                for issue in candidate.get("extraction_issues", [])
            ),
        },
    }


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
    candidates, nested_duplicate_count = _merge_nested_duplicate_candidates(candidates)

    assembly_issues = [
        *deterministic_set.assembly_issues,
        *([] if llm_set is None else llm_set.assembly_issues),
        *_llm_row_issues(llm_row),
    ]
    if duplicate_count:
        assembly_issues.append(f"merged_duplicate_candidate_count:{duplicate_count}")
    if nested_duplicate_count:
        assembly_issues.append(
            f"merged_nested_duplicate_candidate_count:{nested_duplicate_count}"
        )

    candidate_set = CandidateSet(
        source_row_index=source_row_index,
        component_owner="candidate_set_union_deterministic_llm_v1",
        source_artifacts=sorted(
            set(deterministic_set.source_artifacts)
            | (set(llm_set.source_artifacts) if llm_set is not None else set())
        ),
        row_context=_merge_row_context(deterministic_set, llm_set),
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
            "merged_nested_duplicate_candidate_count": nested_duplicate_count,
            "union_candidate_count": len(candidate_set.candidates),
        },
        "call_error": llm_row.get("call_error") if llm_row else None,
        "parse_errors": list(llm_row.get("parse_errors") or []) if llm_row else [],
    }


def _merge_duplicate(
    existing: ExtractedCandidate,
    duplicate: ExtractedCandidate,
    *,
    issue_prefix: str = "merged_duplicate_candidate",
) -> ExtractedCandidate:
    return existing.model_copy(
        update={
            "source_ids": sorted(set(existing.source_ids) | set(duplicate.source_ids)),
            "extraction_issues": [
                *existing.extraction_issues,
                (
                    f"{issue_prefix}:"
                    f"{duplicate.source_type}:{duplicate.candidate_id}"
                ),
                *[
                    f"duplicate_issue:{issue}"
                    for issue in duplicate.extraction_issues
                ],
            ],
        }
    )


def _merge_nested_duplicate_candidates(
    candidates: Sequence[ExtractedCandidate],
) -> tuple[list[ExtractedCandidate], int]:
    retained: list[ExtractedCandidate] = []
    merged_count = 0
    for candidate in candidates:
        merge_indices = _nested_duplicate_indices(retained, candidate)
        if not merge_indices:
            retained.append(candidate)
            continue
        retained = _merge_nested_duplicate_group(retained, candidate, merge_indices)
        merged_count += len(merge_indices)
    return retained, merged_count


def _nested_duplicate_indices(
    retained: Sequence[ExtractedCandidate],
    candidate: ExtractedCandidate,
) -> list[int]:
    return [
        index
        for index, existing in enumerate(retained)
        if _is_nested_duplicate(existing, candidate)
    ]


def _merge_nested_duplicate_group(
    retained: list[ExtractedCandidate],
    candidate: ExtractedCandidate,
    merge_indices: Sequence[int],
) -> list[ExtractedCandidate]:
    duplicate_group = [candidate, *(retained[index] for index in merge_indices)]
    preferred = max(duplicate_group, key=_candidate_detail_score)
    merged = preferred
    for duplicate in duplicate_group:
        if duplicate is preferred:
            continue
        merged = _merge_duplicate(
            merged,
            duplicate,
            issue_prefix="merged_nested_duplicate_candidate",
        )

    updated = list(retained)
    updated[merge_indices[0]] = merged
    for index in reversed(merge_indices[1:]):
        del updated[index]
    return updated


def _is_nested_duplicate(
    left: ExtractedCandidate,
    right: ExtractedCandidate,
) -> bool:
    if left.candidate_kind != right.candidate_kind:
        return False
    if left.event_type != right.event_type:
        return False
    left_span = _resolved_span(left)
    right_span = _resolved_span(right)
    left_text = _normalize(left.evidence_span.text)
    right_text = _normalize(right.evidence_span.text)
    if left_span is not None and right_span is not None:
        return (
            _span_contains(left_span, right_span)
            or _span_contains(right_span, left_span)
            or (
                _spans_overlap(left_span, right_span)
                and _text_contains(left_text, right_text)
            )
        )
    return _text_contains(left_text, right_text)


def _resolved_span(candidate: ExtractedCandidate) -> tuple[int, int] | None:
    start = candidate.evidence_span.start_char
    end = candidate.evidence_span.end_char
    if start is None or end is None:
        return None
    return (start, end)


def _span_contains(
    outer: tuple[int, int],
    inner: tuple[int, int],
) -> bool:
    return outer[0] <= inner[0] and inner[1] <= outer[1]


def _spans_overlap(
    left: tuple[int, int],
    right: tuple[int, int],
) -> bool:
    return max(left[0], right[0]) < min(left[1], right[1])


def _text_contains(left_text: str, right_text: str) -> bool:
    return bool(left_text and right_text) and (
        left_text in right_text or right_text in left_text
    )


def _candidate_detail_score(candidate: ExtractedCandidate) -> tuple[int, int]:
    span = _resolved_span(candidate)
    span_length = span[1] - span[0] if span is not None else 0
    evidence_length = len(candidate.evidence_span.text)
    return (span_length, evidence_length)


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


def _merge_row_context(
    deterministic_set: CandidateSet,
    llm_set: CandidateSet | None,
) -> RowContext:
    deterministic_context = deterministic_set.row_context
    llm_context = llm_set.row_context if llm_set is not None else RowContext()
    reference_date = (
        deterministic_context.reference_date
        or llm_context.reference_date
    )
    prior_encounter = (
        deterministic_context.prior_encounter
        or llm_context.prior_encounter
    )
    context_issues = _dedupe(
        [
            *deterministic_context.context_issues,
            *llm_context.context_issues,
        ]
    )
    if reference_date is not None:
        context_issues = [
            issue for issue in context_issues if issue != "reference_date_missing"
        ]
    return RowContext(
        reference_date=reference_date,
        prior_encounter=prior_encounter,
        context_issues=context_issues,
    )


def _dedupe(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        deduped.append(value)
    return deduped


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
