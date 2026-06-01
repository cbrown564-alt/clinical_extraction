from clinical_extraction.core.pipeline import PipelineResult
from clinical_extraction.core.schemas import FinalExtraction
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.error_analysis import (
    build_row_error_record,
    summarize_row_errors,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.label_parser import FrequencyLabelKind


def _record(
    *,
    gold_label: str,
    gold_kind: FrequencyLabelKind,
    gold_monthly_frequency: float,
    note_text: str = "Present Seizure Frequency: two seizures per month.",
    gold_reference: str = "two seizures per month",
) -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=42,
        note_text=note_text,
        gold_label=gold_label,
        gold_reference=gold_reference,
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label=gold_label,
        gold_label_kind=gold_kind,
        gold_yearly_bounds=None,
        gold_monthly_frequency=gold_monthly_frequency,
    )


def _result(
    *,
    label: str,
    kind: str,
    monthly_frequency: float,
    evidence: str = "evidence",
    candidate_events: list[dict[str, str]] | None = None,
    evidence_valid: bool = True,
) -> PipelineResult[FinalExtraction]:
    candidate_events = candidate_events or [{"event_id": "event_1", "kind": "frequency_rate"}]
    return PipelineResult(
        output=FinalExtraction(final_value=label, rationale="Selected.", evidence=evidence),
        diagnostics={
            "candidate_events": candidate_events,
            "evidence_valid": evidence_valid,
            "final_selection": {
                "final_label": label,
                "final_kind": kind,
                "monthly_frequency": monthly_frequency,
                "evidence": evidence,
                "rationale": "Selected.",
            },
        },
    )


def test_build_row_error_record_flags_missed_frequency_evidence() -> None:
    row = build_row_error_record(
        _record(
            gold_label="2 per month",
            gold_kind=FrequencyLabelKind.FREQUENCY,
            gold_monthly_frequency=2.0,
        ),
        _result(
            label="no seizure frequency reference",
            kind="no_reference",
            monthly_frequency=1000.0,
        ),
    )

    assert row.correct is False
    assert row.error_type == "missed_frequency_evidence"
    assert row.gold_category == "seizure_freq_more1mon_less1week"
    assert row.prediction_category == "seizure_freq_unknown"
    assert row.candidate_count == 1
    assert row.clinical_candidate_count == 1


def test_build_row_error_record_preserves_semantic_mismatch_when_scorer_matches() -> None:
    row = build_row_error_record(
        _record(
            gold_label="unknown",
            gold_kind=FrequencyLabelKind.UNKNOWN,
            gold_monthly_frequency=1000.0,
        ),
        _result(
            label="no seizure frequency reference",
            kind="no_reference",
            monthly_frequency=1000.0,
        ),
    )

    assert row.correct is True
    assert row.error_type == "scorer_correct_semantic_mismatch"
    assert row.gold_category == row.prediction_category == "seizure_freq_unknown"
    assert row.likely_failed_operation == "semantic_state_mapping"


def test_build_row_error_record_excludes_fallback_from_clinical_candidate_count() -> None:
    row = build_row_error_record(
        _record(
            gold_label="2 per month",
            gold_kind=FrequencyLabelKind.FREQUENCY,
            gold_monthly_frequency=2.0,
            note_text="Clinic Date: 02 October 2025\nDear Dr Smith\nTwo seizures per month.",
            gold_reference="Two seizures per month",
        ),
        _result(
            label="no seizure frequency reference",
            kind="no_reference",
            monthly_frequency=1000.0,
            evidence="Clinic Date: 02 October 2025\nDear Dr Smith",
            candidate_events=[{"event_id": "event_1", "kind": "no_reference"}],
        ),
    )

    assert row.candidate_count == 1
    assert row.clinical_candidate_count == 0
    assert row.selected_evidence_type == "header_fallback"
    assert row.likely_failed_operation == "candidate_extraction"


def test_build_row_error_record_flags_medication_distractor() -> None:
    row = build_row_error_record(
        _record(
            gold_label="5 to 7 per year",
            gold_kind=FrequencyLabelKind.FREQUENCY,
            gold_monthly_frequency=0.5,
            note_text="Levetiracetam dose 1g twice a day. Seizures: 5 or 7 this year.",
            gold_reference="5 or 7 this year",
        ),
        _result(
            label="2 per day",
            kind="frequency",
            monthly_frequency=60.0,
            evidence="Dose 1g twice a day",
        ),
    )

    assert row.error_type == "wrong_frequency_bucket"
    assert row.selected_evidence_type == "medication_or_dose"
    assert row.likely_failed_operation == "distractor_rejection"
    assert "medication_status" in row.clinical_error_modes.split("|")


def test_summarize_row_errors_counts_metrics_and_error_types() -> None:
    rows = [
        build_row_error_record(
            _record(
                gold_label="unknown",
                gold_kind=FrequencyLabelKind.UNKNOWN,
                gold_monthly_frequency=1000.0,
            ),
            _result(label="unknown", kind="unknown", monthly_frequency=1000.0),
        ),
        build_row_error_record(
            _record(
                gold_label="2 per month",
                gold_kind=FrequencyLabelKind.FREQUENCY,
                gold_monthly_frequency=2.0,
            ),
            _result(label="unknown", kind="unknown", monthly_frequency=1000.0),
        ),
    ]

    summary = summarize_row_errors(rows)

    assert summary["row_count"] == 2
    assert summary["correct_count"] == 1
    assert summary["metrics"]["micro"]["accuracy"] == 0.5
    assert summary["error_type_counts"]["correct"] == 1
    assert summary["error_type_counts"]["missed_frequency_evidence"] == 1
    assert summary["clinical_candidate_total"] == 2
    assert summary["zero_clinical_candidate_count"] == 0
    assert summary["clinical_error_mode_counts"]["none"] == 2
    assert summary["likely_failed_operation_counts"]["candidate_extraction"] == 1
