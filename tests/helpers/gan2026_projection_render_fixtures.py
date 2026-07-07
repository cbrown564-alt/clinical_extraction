"""Shared fixtures for Gan2026 clinical assessment projection/render tests."""

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
    EvidenceSpan,
    ExtractedCandidate,
    FrequencyDetails,
    PriorEncounterContext,
    ReferenceDateContext,
    RowContext,
    SeizureFreeDetails,
    SourcePhraseOnlyDetails,
)


def candidate_set(
    source_row_index: int,
    *,
    evidence: str = "two seizures per month",
    candidate_kind: str = "frequency_rate",
    cluster_frequency: str = "approximately once monthly",
    cluster_period: str | None = None,
    events_per_cluster: str | None = None,
) -> CandidateSet:
    frequency = (
        FrequencyDetails(source_phrase=evidence) if candidate_kind == "frequency_rate" else None
    )
    return CandidateSet(
        source_row_index=source_row_index,
        component_owner="candidate_set_union",
        source_artifacts=["test"],
        candidates=[
            ExtractedCandidate(
                candidate_id=f"llm:{source_row_index}:1",
                component_owner="test",
                source_type="llm_candidate",
                source_artifact="test",
                source_row_index=source_row_index,
                candidate_kind=candidate_kind,
                event_type="seizure",
                frequency=frequency,
                cluster_details=(
                    {
                        "cluster_frequency": cluster_frequency,
                        "events_per_cluster": events_per_cluster,
                        "cluster_count": None,
                        "cluster_period": cluster_period,
                    }
                    if candidate_kind == "cluster_frequency"
                    else None
                ),
                temporality="current",
                certainty="certain",
                assertion_status="asserted",
                evidence_span=EvidenceSpan(text=evidence, start_char=0, end_char=20),
                source_ids=[f"note:{source_row_index}:span:0-20"],
                clinical_or_policy="clinical",
            )
        ],
    )


def row_context(
    reference_date: str,
    *,
    prior_encounter_date: str | None = None,
    prior_encounter_phrase: str | None = None,
) -> RowContext:
    return RowContext(
        reference_date=ReferenceDateContext(
            date=reference_date,
            date_precision="day",
            source="note_header",
            source_phrase=f"Clinic Date: {reference_date}",
            source_span=EvidenceSpan(
                text=f"Clinic Date: {reference_date}",
                start_char=0,
                end_char=len(f"Clinic Date: {reference_date}"),
            ),
        ),
        prior_encounter=(
            PriorEncounterContext(
                date=prior_encounter_date,
                date_precision="day",
                source="explicit_relative_interval",
                source_phrase=prior_encounter_phrase or "",
                source_span=EvidenceSpan(
                    text=prior_encounter_phrase or "",
                    start_char=0,
                    end_char=len(prior_encounter_phrase or ""),
                ),
                issues=["prior_encounter_date_inferred_from_relative_interval"],
            )
            if prior_encounter_date is not None
            else None
        ),
    )


def unknown_candidate(
    source_row_index: int,
    candidate_id: str,
    evidence: str,
    *,
    event_type: str = "seizure",
) -> ExtractedCandidate:
    return ExtractedCandidate(
        candidate_id=candidate_id,
        component_owner="test",
        source_type="llm_candidate",
        source_artifact="test",
        source_row_index=source_row_index,
        candidate_kind="unknown_frequency",
        event_type=event_type,
        unknown_frequency=SourcePhraseOnlyDetails(source_phrase=evidence),
        temporality="recent",
        certainty="certain",
        assertion_status="asserted",
        evidence_span=EvidenceSpan(text=evidence, start_char=0, end_char=len(evidence)),
        source_ids=[f"note:{source_row_index}:span:0-{len(evidence)}"],
        clinical_or_policy="clinical",
    )


def seizure_free_candidate(
    source_row_index: int,
    candidate_id: str,
    evidence: str,
    *,
    source_ids: list[str] | None = None,
) -> ExtractedCandidate:
    return ExtractedCandidate(
        candidate_id=candidate_id,
        component_owner="test",
        source_type="llm_candidate",
        source_artifact="test",
        source_row_index=source_row_index,
        candidate_kind="seizure_free",
        event_type="seizure",
        seizure_free=SeizureFreeDetails(source_phrase=evidence),
        temporality="recent",
        certainty="certain",
        assertion_status="asserted",
        evidence_span=EvidenceSpan(text=evidence, start_char=0, end_char=len(evidence)),
        source_ids=source_ids or [f"note:{source_row_index}:span:0-{len(evidence)}"],
        clinical_or_policy="clinical",
    )
