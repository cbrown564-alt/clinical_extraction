from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    candidate_set_union,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
    EvidenceSpan,
    ExtractedCandidate,
    FrequencyDetails,
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


def _row(
    source_row_index: int,
    candidates: list[ExtractedCandidate],
) -> dict:
    candidate_set = CandidateSet(
        source_row_index=source_row_index,
        component_owner="test",
        source_artifacts=["test"],
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
        evidence_span=EvidenceSpan(text=evidence),
        source_ids=[f"{source_type}:{source_row_index}:span"],
        clinical_or_policy="clinical",
    )
