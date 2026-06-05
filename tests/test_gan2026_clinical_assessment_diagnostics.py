from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    clinical_assessment_diagnostics as diagnostics,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
    ClusterDetails,
    EvidenceSpan,
    ExtractedCandidate,
    FrequencyDetails,
    SeizureFreeDetails,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.clinical_assessment import (
    ClinicalAssessment,
    NormalizedBurden,
)


def test_clinical_assessment_diagnostics_flags_nonadditive_multi_primary() -> None:
    rows = [
        _assessment_row(
            10,
            [
                _frequency_candidate("det:10:1", "two seizures per month"),
                _frequency_candidate("llm:10:2", "two seizures per month"),
            ],
            ClinicalAssessment(
                source_row_index=10,
                component_owner="test",
                assessment_kind="frequency_rate",
                primary_candidate_ids=["det:10:1", "llm:10:2"],
                aggregation_policy="single_fact",
                normalized_burden=NormalizedBurden(
                    count_low=2,
                    count_high=2,
                    period_low=1,
                    period_high=1,
                    period_unit="month",
                    source_normalized_phrase="two seizures per month",
                ),
            ),
        )
    ]

    diagnostic_rows, metadata = diagnostics.build_clinical_assessment_diagnostics(rows)

    assert diagnostic_rows[0]["diagnostic_flags"] == [
        "multi_primary_nonadditive_policy",
        "single_fact_multiple_primary_candidates",
    ]
    assert metadata["summary"]["diagnostic_flag_counts"] == {
        "multi_primary_nonadditive_policy": 1,
        "single_fact_multiple_primary_candidates": 1,
    }


def test_clinical_assessment_diagnostics_flags_context_leak_in_frequency_burden() -> None:
    rows = [
        _assessment_row(
            11,
            [
                _frequency_candidate("llm:11:1", "one seizure per month"),
                _cluster_candidate("llm:11:2", "clusters after sleep loss"),
            ],
            ClinicalAssessment(
                source_row_index=11,
                component_owner="test",
                assessment_kind="frequency_rate",
                primary_candidate_ids=["llm:11:1"],
                supporting_candidate_ids=["llm:11:2"],
                aggregation_policy="primary_with_context",
                normalized_burden=NormalizedBurden(
                    count_low=1,
                    count_high=1,
                    period_low=1,
                    period_high=1,
                    period_unit="month",
                    cluster_count_low=3,
                    cluster_count_high=3,
                    source_normalized_phrase="one seizure per month, previously clustered",
                ),
            ),
        )
    ]

    diagnostic_rows, metadata = diagnostics.build_clinical_assessment_diagnostics(rows)

    assert diagnostic_rows[0]["diagnostic_flags"] == [
        "cluster_context_leak_in_frequency_burden",
        "historical_context_phrase_in_burden",
    ]
    assert metadata["summary"]["rows_with_diagnostic_flags"] == 1


def test_clinical_assessment_diagnostics_flags_seizure_free_leak_in_cluster_burden() -> None:
    rows = [
        _assessment_row(
            14,
            [_cluster_candidate("llm:14:1", "5 to 7 seizures over three weeks")],
            ClinicalAssessment(
                source_row_index=14,
                component_owner="test",
                assessment_kind="cluster_frequency",
                primary_candidate_ids=["llm:14:1"],
                aggregation_policy="single_fact",
                normalized_burden=NormalizedBurden(
                    count_low=5,
                    count_high=7,
                    period_low=3,
                    period_high=3,
                    period_unit="week",
                    seizure_free_duration_low=6,
                    seizure_free_duration_high=6,
                    seizure_free_duration_unit="week",
                    source_normalized_phrase=(
                        "5 to 7 seizures over three weeks with six seizure-free weeks after"
                    ),
                ),
            ),
        )
    ]

    diagnostic_rows, metadata = diagnostics.build_clinical_assessment_diagnostics(rows)

    assert diagnostic_rows[0]["diagnostic_flags"] == [
        "seizure_free_context_leak_in_cluster_burden"
    ]
    assert metadata["summary"]["rows_with_diagnostic_flags"] == 1


def test_clinical_assessment_diagnostics_allows_single_primary_cluster_axis() -> None:
    rows = [
        _assessment_row(
            13,
            [_cluster_candidate("llm:13:1", "clusters every 4 weeks over 1 to 2 days")],
            ClinicalAssessment(
                source_row_index=13,
                component_owner="test",
                assessment_kind="cluster_frequency",
                primary_candidate_ids=["llm:13:1"],
                aggregation_policy="cluster_axis",
                normalized_burden=NormalizedBurden(
                    period_low=4,
                    period_high=4,
                    period_unit="week",
                    cluster_period_low=1,
                    cluster_period_high=2,
                    cluster_period_unit="day",
                    source_normalized_phrase="clusters every 4 weeks over 1 to 2 days",
                ),
            ),
        )
    ]

    diagnostic_rows, metadata = diagnostics.build_clinical_assessment_diagnostics(rows)

    assert diagnostic_rows[0]["diagnostic_flags"] == []
    assert metadata["summary"]["rows_with_diagnostic_flags"] == 0


def test_clinical_assessment_diagnostics_allows_seizure_free_historical_only_primary() -> None:
    rows = [
        _assessment_row(
            15,
            [
                _seizure_free_candidate(
                    "llm:15:1",
                    "No seizures observed since initial referral",
                    temporality="historical",
                )
            ],
            ClinicalAssessment(
                source_row_index=15,
                component_owner="test",
                assessment_kind="seizure_free",
                primary_candidate_ids=["llm:15:1"],
                aggregation_policy="single_fact",
                normalized_burden=NormalizedBurden(
                    source_normalized_phrase="no seizures since initial referral",
                ),
            ),
        )
    ]

    diagnostic_rows, metadata = diagnostics.build_clinical_assessment_diagnostics(rows)

    assert diagnostic_rows[0]["diagnostic_flags"] == []
    assert metadata["claim_boundary"].startswith("1-row clinical-assessment")


def test_clinical_assessment_diagnostics_flags_historical_primary_with_recent_alternative() -> None:
    rows = [
        _assessment_row(
            16,
            [
                _frequency_candidate(
                    "llm:16:1",
                    "weekly seizures in 2020",
                    temporality="historical",
                ),
                _frequency_candidate(
                    "llm:16:2",
                    "now has monthly seizures",
                    temporality="current",
                ),
            ],
            ClinicalAssessment(
                source_row_index=16,
                component_owner="test",
                assessment_kind="frequency_rate",
                primary_candidate_ids=["llm:16:1"],
                supporting_candidate_ids=["llm:16:2"],
                aggregation_policy="primary_with_context",
                normalized_burden=NormalizedBurden(
                    source_normalized_phrase="weekly seizures in 2020",
                ),
            ),
        )
    ]

    diagnostic_rows, _ = diagnostics.build_clinical_assessment_diagnostics(rows)

    assert diagnostic_rows[0]["diagnostic_flags"] == ["historical_primary_candidate"]


def test_clinical_assessment_diagnostics_compares_selector_artifacts() -> None:
    assessment_rows = [
        _assessment_row(
            12,
            [_frequency_candidate("det:12:1", "two seizures per month")],
            ClinicalAssessment(
                source_row_index=12,
                component_owner="test",
                assessment_kind="frequency_rate",
                primary_candidate_ids=["det:12:1"],
                aggregation_policy="single_fact",
                normalized_burden=NormalizedBurden(source_normalized_phrase="two per month"),
            ),
        )
    ]
    minimal_rows = [
        {
            "source_row_index": 12,
            "selected_candidate_decision": {
                "selection_mode": "single_candidate",
                "selected_candidate_ids": ["det:12:1"],
            },
        }
    ]
    rich_rows = [
        {
            "source_row_index": 12,
            "selected_clinical_fact": {
                "clinical_fact_kind": "frequency_rate",
                "selected_candidate_ids": ["llm:12:2"],
            },
        }
    ]

    diagnostic_rows, metadata = diagnostics.build_clinical_assessment_diagnostics(
        assessment_rows,
        minimal_selector_rows=minimal_rows,
        rich_selector_rows=rich_rows,
    )

    assert diagnostic_rows[0]["minimal_selector_primary_relation"] == "same"
    assert diagnostic_rows[0]["rich_selector_primary_relation"] == "different"
    assert metadata["summary"]["minimal_selector_primary_relation_counts"] == {"same": 1}
    assert metadata["summary"]["rich_selector_primary_relation_counts"] == {"different": 1}


def _assessment_row(
    source_row_index: int,
    candidates: list[ExtractedCandidate],
    assessment: ClinicalAssessment,
) -> dict:
    candidate_set = CandidateSet(
        source_row_index=source_row_index,
        component_owner="candidate_set_union",
        source_artifacts=["test"],
        candidates=candidates,
    )
    return {
        "source_row_index": source_row_index,
        "split": "validation",
        "typed_input": {"candidate_set": candidate_set.model_dump()},
        "clinical_assessment": assessment.model_dump(),
        "parse_errors": [],
        "call_error": None,
    }


def _frequency_candidate(
    candidate_id: str,
    evidence: str,
    *,
    temporality: str = "current",
) -> ExtractedCandidate:
    source_row_index = int(candidate_id.split(":")[1])
    source_type = (
        "deterministic_candidate" if candidate_id.startswith("det:") else "llm_candidate"
    )
    return ExtractedCandidate(
        candidate_id=candidate_id,
        component_owner="test",
        source_type=source_type,
        source_artifact="test",
        source_row_index=source_row_index,
        candidate_kind="frequency_rate",
        event_type="seizure",
        frequency=FrequencyDetails(source_phrase=evidence),
        temporality=temporality,
        certainty="certain",
        assertion_status="asserted",
        evidence_span=EvidenceSpan(text=evidence),
        source_ids=[f"note:{source_row_index}:span:0-1"],
        clinical_or_policy="clinical",
    )


def _cluster_candidate(candidate_id: str, evidence: str) -> ExtractedCandidate:
    source_row_index = int(candidate_id.split(":")[1])
    return ExtractedCandidate(
        candidate_id=candidate_id,
        component_owner="test",
        source_type="llm_candidate",
        source_artifact="test",
        source_row_index=source_row_index,
        candidate_kind="cluster_frequency",
        event_type="seizure",
        cluster_details=ClusterDetails(cluster_frequency=evidence),
        temporality="current",
        certainty="certain",
        assertion_status="asserted",
        evidence_span=EvidenceSpan(text=evidence),
        source_ids=[f"note:{source_row_index}:span:0-1"],
        clinical_or_policy="clinical",
    )


def _seizure_free_candidate(
    candidate_id: str,
    evidence: str,
    *,
    temporality: str = "current",
) -> ExtractedCandidate:
    source_row_index = int(candidate_id.split(":")[1])
    return ExtractedCandidate(
        candidate_id=candidate_id,
        component_owner="test",
        source_type="llm_candidate",
        source_artifact="test",
        source_row_index=source_row_index,
        candidate_kind="seizure_free",
        event_type="seizure",
        seizure_free=SeizureFreeDetails(source_phrase=evidence),
        temporality=temporality,
        certainty="certain",
        assertion_status="asserted",
        evidence_span=EvidenceSpan(text=evidence),
        source_ids=[f"note:{source_row_index}:span:0-1"],
        clinical_or_policy="clinical",
    )
