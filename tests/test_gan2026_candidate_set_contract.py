import pytest
from pydantic import ValidationError

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    candidate_set_replay,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
    ExtractedCandidate,
    deterministic_candidate_set_from_raw,
    extract_row_context,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.candidates import (
    CandidateKind,
    RawCandidate,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)


def test_candidate_set_contract_accepts_source_near_deterministic_candidate() -> None:
    note_text = "Current baseline is two seizures per month."
    raw = RawCandidate(
        kind=CandidateKind.FREQUENCY_RATE,
        label="2 per month",
        evidence="two seizures per month",
        rule_id="rate.test",
    )

    candidate_set = deterministic_candidate_set_from_raw(
        [raw],
        note_text=note_text,
        source_row_index=101,
    )

    assert candidate_set.schema_version == "gan2026_candidate_set_source_near_v0"
    candidate = candidate_set.candidates[0]
    assert candidate.source_type == "deterministic_candidate"
    assert candidate.candidate_kind == "frequency_rate"
    assert candidate.frequency is not None
    assert candidate.frequency.source_phrase == "two seizures per month"
    assert candidate.frequency.count is None
    assert candidate.evidence_span.start_char == note_text.index("two")
    assert candidate.extraction_issues == [
        "deterministic_label_carried_as_extraction_provenance_only"
    ]
    assert candidate_set.row_context.reference_date is None
    assert candidate_set.row_context.context_issues == ["reference_date_missing"]


def test_candidate_set_row_context_extracts_clinic_date_header() -> None:
    note_text = (
        "Department of Neurology\n\n"
        "Clinic Date: 02 October 2025\n\n"
        "Current baseline is two seizures per month."
    )
    raw = RawCandidate(
        kind=CandidateKind.FREQUENCY_RATE,
        label="2 per month",
        evidence="two seizures per month",
        rule_id="rate.test",
    )

    candidate_set = deterministic_candidate_set_from_raw(
        [raw],
        note_text=note_text,
        source_row_index=102,
    )

    reference_date = candidate_set.row_context.reference_date
    assert reference_date is not None
    assert reference_date.date == "2025-10-02"
    assert reference_date.date_precision == "day"
    assert reference_date.source == "note_header"
    assert reference_date.source_phrase == "Clinic Date: 02 October 2025"
    assert reference_date.source_span.start_char == note_text.index("Clinic Date")
    assert candidate_set.row_context.context_issues == []


def test_row_context_extracts_email_sent_header_date() -> None:
    note_text = (
        "From: Dr Thomas Reid\n"
        "Sent: 14 October 2019 10:15\n"
        "Subject: Telephone review\n\n"
        "Two events over the last five months."
    )

    context = extract_row_context(note_text)

    reference_date = context.reference_date
    assert reference_date is not None
    assert reference_date.date == "2019-10-14"
    assert reference_date.source == "email_header"
    assert reference_date.source_phrase == "Sent: 14 October 2019 10:15"
    assert context.context_issues == []


def test_row_context_marks_missing_reference_date_without_guessing() -> None:
    context = extract_row_context("Current baseline is two seizures per month.")

    assert context.reference_date is None
    assert context.context_issues == ["reference_date_missing"]


def test_candidate_requires_matching_kind_specific_detail_object() -> None:
    payload = {
        "candidate_id": "bad-1",
        "component_owner": "test",
        "source_type": "llm_candidate",
        "source_artifact": "test",
        "source_row_index": 1,
        "candidate_kind": "frequency_rate",
        "event_type": "seizure",
        "seizure_free": {"source_phrase": "seizure free"},
        "temporality": "current",
        "certainty": "certain",
        "assertion_status": "asserted",
        "evidence_span": {"text": "seizure free"},
        "source_ids": ["note:1"],
        "clinical_or_policy": "clinical",
    }

    with pytest.raises(ValidationError, match="candidate_kind must have exactly one"):
        ExtractedCandidate.model_validate(payload)


def test_candidate_set_replay_summarizes_validation_surface_without_labels() -> None:
    records = [
        _record(
            201,
            "Current baseline is two seizures per month.",
        ),
        _record(
            202,
            "No seizure-frequency reference is documented here.",
        ),
    ]

    rows, metadata = candidate_set_replay.build_validation250_candidate_set_rows(
        records,
        limit=2,
    )

    assert len(rows) == 2
    assert metadata["artifact_name"] == "gan2026_validation250_candidate_set_v0"
    assert metadata["summary"]["candidate_sets"] == 2
    assert "gold_label" not in str(rows)
    CandidateSet.model_validate(rows[0]["candidate_set"])


def _record(source_row_index: int, note_text: str) -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=source_row_index,
        note_text=note_text,
        gold_label="unknown",
        gold_reference="",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label="unknown",
        gold_label_kind=FrequencyLabelKind.UNKNOWN,
        gold_yearly_bounds=None,
        gold_monthly_frequency=0.0,
    )
