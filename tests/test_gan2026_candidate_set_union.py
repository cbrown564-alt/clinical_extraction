from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    candidate_set_union,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
    EvidenceSpan,
    ExtractedCandidate,
    FrequencyDetails,
    ReferenceDateContext,
    RowContext,
)


def test_candidate_set_union_merges_exact_duplicate_candidates() -> None:
    deterministic = _row(
        10,
        [_candidate(10, "det:10:1", "deterministic_candidate", "two seizures per month")],
    )
    llm = _row(
        10,
        [_candidate(10, "llm:10:1", "llm_candidate", "two seizures per month")],
    )

    rows, metadata = candidate_set_union.build_candidate_set_union_rows([deterministic], [llm])

    union_set = CandidateSet.model_validate(rows[0]["candidate_set"])
    assert len(union_set.candidates) == 1
    assert union_set.candidates[0].source_type == "deterministic_candidate"
    assert union_set.candidates[0].source_ids == [
        "deterministic_candidate:10:span",
        "llm_candidate:10:span",
    ]
    assert union_set.candidates[0].extraction_issues == [
        "merged_duplicate_candidate:llm_candidate:llm:10:1"
    ]
    assert union_set.assembly_issues == ["merged_duplicate_candidate_count:1"]
    assert metadata["summary"]["merged_duplicate_candidates"] == 1


def test_candidate_set_union_merges_nested_duplicate_candidates_prefer_longer_span() -> None:
    deterministic = _row(
        12,
        [
            _candidate(
                12,
                "det:12:1",
                "deterministic_candidate",
                "9 per month",
                start_char=30,
                end_char=41,
            )
        ],
    )
    llm = _row(
        12,
        [
            _candidate(
                12,
                "llm:12:1",
                "llm_candidate",
                "Current average frequency is 9 per month",
                start_char=0,
                end_char=41,
            )
        ],
    )

    rows, metadata = candidate_set_union.build_candidate_set_union_rows([deterministic], [llm])

    union_set = CandidateSet.model_validate(rows[0]["candidate_set"])
    assert len(union_set.candidates) == 1
    assert union_set.candidates[0].candidate_id == "llm:12:1"
    assert union_set.candidates[0].evidence_span.text == (
        "Current average frequency is 9 per month"
    )
    assert union_set.candidates[0].source_ids == [
        "deterministic_candidate:12:span",
        "llm_candidate:12:span",
    ]
    assert union_set.candidates[0].extraction_issues == [
        "merged_nested_duplicate_candidate:deterministic_candidate:det:12:1"
    ]
    assert union_set.assembly_issues == ["merged_nested_duplicate_candidate_count:1"]
    assert rows[0]["union_summary"]["merged_nested_duplicate_candidate_count"] == 1
    assert metadata["summary"]["merged_nested_duplicate_candidates"] == 1


def test_candidate_set_union_merges_overlapping_contained_evidence_text() -> None:
    deterministic = _row(
        14,
        [
            _candidate(
                14,
                "det:14:1",
                "deterministic_candidate",
                "every 2 days on average",
                start_char=20,
                end_char=43,
            )
        ],
    )
    llm = _row(
        14,
        [
            _candidate(
                14,
                "llm:14:1",
                "llm_candidate",
                "seizures are occurring every 2 days on average",
                start_char=0,
                end_char=43,
            )
        ],
    )

    rows, metadata = candidate_set_union.build_candidate_set_union_rows([deterministic], [llm])

    union_set = CandidateSet.model_validate(rows[0]["candidate_set"])
    assert len(union_set.candidates) == 1
    assert union_set.candidates[0].candidate_id == "llm:14:1"
    assert union_set.candidates[0].evidence_span.text == (
        "seizures are occurring every 2 days on average"
    )
    assert union_set.assembly_issues == ["merged_nested_duplicate_candidate_count:1"]
    assert metadata["summary"]["merged_nested_duplicate_candidates"] == 1


def test_candidate_set_union_merges_multiple_nested_matches() -> None:
    deterministic = _row(
        15,
        [
            _candidate(
                15,
                "det:15:1",
                "deterministic_candidate",
                "occurring every 2 days",
                start_char=10,
                end_char=32,
            ),
            _candidate(
                15,
                "det:15:2",
                "deterministic_candidate",
                "every 2 days on average",
                start_char=20,
                end_char=43,
            ),
        ],
    )
    llm = _row(
        15,
        [
            _candidate(
                15,
                "llm:15:1",
                "llm_candidate",
                "seizures are occurring every 2 days on average",
                start_char=0,
                end_char=43,
            )
        ],
    )

    rows, metadata = candidate_set_union.build_candidate_set_union_rows([deterministic], [llm])

    union_set = CandidateSet.model_validate(rows[0]["candidate_set"])
    assert len(union_set.candidates) == 1
    assert union_set.candidates[0].candidate_id == "llm:15:1"
    assert union_set.candidates[0].extraction_issues == [
        "merged_nested_duplicate_candidate:deterministic_candidate:det:15:1",
        "merged_nested_duplicate_candidate:deterministic_candidate:det:15:2",
    ]
    assert union_set.assembly_issues == ["merged_nested_duplicate_candidate_count:2"]
    assert metadata["summary"]["merged_nested_duplicate_candidates"] == 2


def test_candidate_set_union_does_not_merge_same_kind_separate_mentions() -> None:
    deterministic = _row(
        13,
        [
            _candidate(
                13,
                "det:13:1",
                "deterministic_candidate",
                "6 to 7 per year",
                start_char=10,
                end_char=25,
            )
        ],
    )
    llm = _row(
        13,
        [
            _candidate(
                13,
                "llm:13:1",
                "llm_candidate",
                "seizure burden remains 6 to 7 per year",
                start_char=100,
                end_char=140,
            )
        ],
    )

    rows, metadata = candidate_set_union.build_candidate_set_union_rows([deterministic], [llm])

    union_set = CandidateSet.model_validate(rows[0]["candidate_set"])
    assert len(union_set.candidates) == 2
    assert union_set.assembly_issues == []
    assert metadata["summary"]["merged_nested_duplicate_candidates"] == 0


def test_candidate_set_union_preserves_missing_llm_candidate_set_issue() -> None:
    deterministic = _row(
        11,
        [_candidate(11, "det:11:1", "deterministic_candidate", "one seizure per week")],
    )
    llm = {
        "source_row_index": 11,
        "candidate_set": None,
        "call_error": "TimeoutError",
        "parse_errors": ["not_run"],
    }

    rows, metadata = candidate_set_union.build_candidate_set_union_rows([deterministic], [llm])

    union_set = CandidateSet.model_validate(rows[0]["candidate_set"])
    assert len(union_set.candidates) == 1
    assert union_set.assembly_issues == [
        "llm_candidate_set_missing",
        "llm_call_error:TimeoutError",
        "llm_parse_or_validation_error:not_run",
    ]
    assert rows[0]["call_error"] == "TimeoutError"
    assert rows[0]["parse_errors"] == ["not_run"]
    assert metadata["summary"]["llm_candidate_set_missing_rows"] == 1
    assert metadata["summary"]["llm_call_error_rows"] == 1


def test_candidate_set_union_preserves_deterministic_row_context() -> None:
    deterministic = _row(
        16,
        [_candidate(16, "det:16:1", "deterministic_candidate", "one seizure per week")],
        row_context=RowContext(
            reference_date=ReferenceDateContext(
                date="2025-10-02",
                date_precision="day",
                source="note_header",
                source_phrase="Clinic Date: 02 October 2025",
                source_span=EvidenceSpan(
                    text="Clinic Date: 02 October 2025",
                    start_char=20,
                    end_char=49,
                ),
            )
        ),
    )
    llm = _row(
        16,
        [_candidate(16, "llm:16:1", "llm_candidate", "one seizure per week")],
        row_context=RowContext(context_issues=["reference_date_missing"]),
    )

    rows, _metadata = candidate_set_union.build_candidate_set_union_rows(
        [deterministic],
        [llm],
    )

    union_set = CandidateSet.model_validate(rows[0]["candidate_set"])
    assert union_set.row_context.reference_date is not None
    assert union_set.row_context.reference_date.date == "2025-10-02"
    assert union_set.row_context.context_issues == []


def _row(
    source_row_index: int,
    candidates: list[ExtractedCandidate],
    *,
    row_context: RowContext | None = None,
) -> dict:
    candidate_set = CandidateSet(
        source_row_index=source_row_index,
        component_owner="test",
        source_artifacts=["test"],
        row_context=row_context or RowContext(),
        candidates=candidates,
    )
    return {
        "source_row_index": source_row_index,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "candidate_set": candidate_set.model_dump(),
    }


def _candidate(
    source_row_index: int,
    candidate_id: str,
    source_type: str,
    evidence: str,
    *,
    start_char: int | None = None,
    end_char: int | None = None,
) -> ExtractedCandidate:
    return ExtractedCandidate(
        candidate_id=candidate_id,
        component_owner="test",
        source_type=source_type,
        source_artifact="test",
        source_row_index=source_row_index,
        candidate_kind="frequency_rate",
        event_type="seizure",
        frequency=FrequencyDetails(source_phrase=evidence),
        temporality="current",
        certainty="certain",
        assertion_status="asserted",
        evidence_span=EvidenceSpan(text=evidence, start_char=start_char, end_char=end_char),
        source_ids=[f"{source_type}:{source_row_index}:span"],
        clinical_or_policy="clinical",
    )
