from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    candidate_set_diagnostics,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
    EvidenceSpan,
    ExtractedCandidate,
    FrequencyDetails,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord


def test_candidate_set_diagnostics_reports_empty_and_high_burden_rows() -> None:
    records = [
        _record(10, "Current seizures are two per month.", "2 per month"),
        _record(11, "No clear seizure frequency is documented.", "unknown"),
    ]
    rows = [
        _candidate_row(
            10,
            [
                _frequency_candidate(10, 1, "two per month"),
                _frequency_candidate(10, 2, "Current seizures are two per month"),
            ],
        ),
        _candidate_row(11, []),
    ]

    diagnostic_rows, metadata = candidate_set_diagnostics.build_candidate_set_diagnostics(
        rows,
        records,
        high_burden_threshold=2,
    )

    assert diagnostic_rows[0]["high_burden"] is True
    assert diagnostic_rows[1]["candidate_count"] == 0
    assert metadata["summary"]["high_burden_rows"] == 1
    assert metadata["summary"]["rows_with_no_candidates"] == 1
    assert metadata["summary"]["compatible_kind_coverage_rows"] == 1
    assert metadata["summary"]["by_gold_candidate_kind"]["frequency_rate"][
        "compatible_kind_coverage_rate"
    ] == 1.0
    assert metadata["summary"]["by_gold_candidate_kind"]["unknown_frequency"][
        "compatible_kind_coverage_rate"
    ] == 0.0
    assert "not normalized-label recall" in metadata["claim_boundary"]


def test_candidate_set_diagnostics_treats_missing_candidate_set_as_empty_failure() -> None:
    records = [_record(12, "No clear seizure frequency is documented.", "unknown")]
    rows = [
        {
            "source_row_index": 12,
            "split": "validation",
            "candidate_set": None,
            "call_error": "TimeoutError",
            "parse_errors": ["not_run"],
        }
    ]

    diagnostic_rows, metadata = candidate_set_diagnostics.build_candidate_set_diagnostics(
        rows,
        records,
    )

    assert diagnostic_rows[0]["candidate_set_status"] == "missing"
    assert diagnostic_rows[0]["candidate_count"] == 0
    assert diagnostic_rows[0]["diagnostic_issues"] == [
        "candidate_set_missing",
        "call_error",
        "parse_or_validation_errors",
    ]
    assert metadata["summary"]["candidate_set_missing_rows"] == 1
    assert metadata["summary"]["diagnostic_issue_rows"] == 1


def _candidate_row(source_row_index: int, candidates: list[ExtractedCandidate]) -> dict:
    candidate_set = CandidateSet(
        source_row_index=source_row_index,
        component_owner="test",
        source_artifacts=["test"],
        candidates=candidates,
    )
    return {
        "source_row_index": source_row_index,
        "split": "validation",
        "candidate_set": candidate_set.model_dump(),
    }


def _frequency_candidate(
    source_row_index: int,
    index: int,
    evidence: str,
) -> ExtractedCandidate:
    return ExtractedCandidate(
        candidate_id=f"det:{source_row_index}:{index}",
        component_owner="test",
        source_type="deterministic_candidate",
        source_artifact="test",
        source_row_index=source_row_index,
        candidate_kind="frequency_rate",
        event_type="seizure",
        frequency=FrequencyDetails(source_phrase=evidence),
        temporality="current",
        certainty="certain",
        assertion_status="asserted",
        evidence_span=EvidenceSpan(text=evidence),
        source_ids=[f"note:{source_row_index}:span:0-1"],
        clinical_or_policy="clinical",
    )


def _record(source_row_index: int, note_text: str, gold_label: str) -> GanFrequencyRecord:
    kind = FrequencyLabelKind.UNKNOWN if gold_label == "unknown" else FrequencyLabelKind.FREQUENCY
    return GanFrequencyRecord(
        source_row_index=source_row_index,
        note_text=note_text,
        gold_label=gold_label,
        gold_reference="",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label=gold_label,
        gold_label_kind=kind,
        gold_yearly_bounds=None,
        gold_monthly_frequency=1000.0 if kind is FrequencyLabelKind.UNKNOWN else 2.0,
    )
