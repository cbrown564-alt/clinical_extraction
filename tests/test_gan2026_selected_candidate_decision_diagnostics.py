from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    selected_candidate_decision_diagnostics as diagnostics,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
    EvidenceSpan,
    ExtractedCandidate,
    FrequencyDetails,
    SourcePhraseOnlyDetails,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.selected_fact import (
    SelectedCandidateDecision,
)


def test_selected_candidate_decision_diagnostics_summarizes_sources_and_modes() -> None:
    rows = [
        _selection_row(
            10,
            [
                _frequency_candidate("det:10:1", "two seizures yesterday"),
                _frequency_candidate("llm:10:2", "one seizure today"),
            ],
            SelectedCandidateDecision(
                source_row_index=10,
                component_owner="llm_candidate_set_selector",
                selected_candidate_ids=["det:10:1", "llm:10:2"],
                selection_mode="related_candidate_group",
                rationale="Both candidates describe the same current short-window burden.",
            ),
        ),
        _selection_row(
            11,
            [_unknown_candidate("llm:11:1", "frequency unclear")],
            SelectedCandidateDecision(
                source_row_index=11,
                component_owner="llm_candidate_set_selector",
                selected_candidate_ids=[],
                selection_mode="no_reliable_candidate",
                rationale="No usable current frequency candidate is available.",
            ),
        ),
    ]

    diagnostic_rows, metadata = diagnostics.build_selected_candidate_decision_diagnostics(
        rows,
        high_burden_threshold=2,
    )

    assert diagnostic_rows[0]["selected_source_composition"] == "mixed"
    assert diagnostic_rows[0]["high_burden"] is True
    assert diagnostic_rows[0]["related_group_coherence_flags"] == []
    assert metadata["summary"]["selection_mode_counts"] == {
        "no_reliable_candidate": 1,
        "related_candidate_group": 1,
    }
    assert metadata["summary"]["selected_source_type_counts"] == {
        "deterministic_candidate": 1,
        "llm_candidate": 1,
    }
    assert metadata["summary"]["high_burden_rows"] == 1
    assert "does not score" in metadata["claim_boundary"]


def test_selected_candidate_decision_diagnostics_flags_invalid_references() -> None:
    rows = [
        _selection_row(
            12,
            [_frequency_candidate("det:12:1", "two seizures per month")],
            SelectedCandidateDecision(
                source_row_index=12,
                component_owner="llm_candidate_set_selector",
                selected_candidate_ids=["missing:12:1"],
                selection_mode="single_candidate",
            ),
        )
    ]

    diagnostic_rows, metadata = diagnostics.build_selected_candidate_decision_diagnostics(rows)

    assert diagnostic_rows[0]["unknown_selected_candidate_ids"] == ["missing:12:1"]
    assert metadata["summary"]["invalid_selected_reference_rows"] == 1
    assert metadata["summary"]["invalid_reference_source_row_indices"] == [12]


def test_selected_candidate_decision_diagnostics_flags_mixed_related_groups() -> None:
    rows = [
        _selection_row(
            13,
            [
                _frequency_candidate("det:13:1", "two seizures yesterday"),
                _unknown_candidate("llm:13:2", "several events today"),
            ],
            SelectedCandidateDecision(
                source_row_index=13,
                component_owner="llm_candidate_set_selector",
                selected_candidate_ids=["det:13:1", "llm:13:2"],
                selection_mode="related_candidate_group",
            ),
        )
    ]

    diagnostic_rows, metadata = diagnostics.build_selected_candidate_decision_diagnostics(rows)

    assert diagnostic_rows[0]["related_group_coherence_flags"] == [
        "mixed_candidate_kind",
        "no_cluster_or_shared_kind_signal",
    ]
    assert metadata["summary"]["related_group_with_coherence_flags"] == 1


def _selection_row(
    source_row_index: int,
    candidates: list[ExtractedCandidate],
    decision: SelectedCandidateDecision,
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
        "selected_candidate_decision": decision.model_dump(),
        "parse_errors": [],
        "call_error": None,
    }


def _frequency_candidate(candidate_id: str, evidence: str) -> ExtractedCandidate:
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
        temporality="current",
        certainty="certain",
        assertion_status="asserted",
        evidence_span=EvidenceSpan(text=evidence),
        source_ids=[f"note:{source_row_index}:span:0-1"],
        clinical_or_policy="clinical",
    )


def _unknown_candidate(candidate_id: str, evidence: str) -> ExtractedCandidate:
    source_row_index = int(candidate_id.split(":")[1])
    return ExtractedCandidate(
        candidate_id=candidate_id,
        component_owner="test",
        source_type="llm_candidate",
        source_artifact="test",
        source_row_index=source_row_index,
        candidate_kind="unknown_frequency",
        event_type="seizure",
        unknown_frequency=SourcePhraseOnlyDetails(source_phrase=evidence),
        temporality="current",
        certainty="uncertain",
        certainty_reason="vague_count",
        assertion_status="asserted",
        evidence_span=EvidenceSpan(text=evidence),
        source_ids=[f"note:{source_row_index}:span:0-1"],
        clinical_or_policy="clinical",
    )
