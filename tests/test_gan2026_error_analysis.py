from clinical_extraction.core.pipeline import PipelineResult
from clinical_extraction.core.schemas import FinalExtraction
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.error_analysis import (
    build_row_error_record,
    summarize_row_errors,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import FrequencyLabelKind


def _record(
    *,
    gold_label: str,
    gold_kind: FrequencyLabelKind,
    gold_monthly_frequency: float,
) -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=42,
        note_text="Present Seizure Frequency: two seizures per month.",
        gold_label=gold_label,
        gold_reference="two seizures per month",
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
    evidence_valid: bool = True,
) -> PipelineResult[FinalExtraction]:
    return PipelineResult(
        output=FinalExtraction(final_value=label, rationale="Selected.", evidence="evidence"),
        diagnostics={
            "candidate_events": [{"event_id": "event_1"}],
            "evidence_valid": evidence_valid,
            "final_selection": {
                "final_label": label,
                "final_kind": kind,
                "monthly_frequency": monthly_frequency,
                "evidence": "evidence",
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
