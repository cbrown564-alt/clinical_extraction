"""Invariant-focused tests for gan2026 pipeline v1 selection."""

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanRecord,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.pipeline_v1 import (
    Gan2026PipelineV1,
)


def _record(note_text: str, gold_label: str = "unknown") -> GanRecord:
    return GanRecord(
        source_row_index=1,
        note_text=note_text,
        gold_label=gold_label,
        gold_reference="",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
    )


def test_pipeline_prefers_cluster_spacing_over_incidental_daily_mentions() -> None:
    note_text = (
        "His seizures typically occur in clusters, generally spaced four days "
        "apart, though brief periods of daily seizures have been reported."
    )
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == "1 per 4 day"
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert (
        result.diagnostics["final_selection"]["evidence"]
        == "seizures typically occur in clusters, generally spaced four days apart"
    )
    assert result.diagnostics["evidence_valid"] is True


def test_pipeline_extracts_sparse_parenthetical_month_event_lists() -> None:
    note_text = (
        "Clinic Date: 21 April 2011. He had a cluster of three seizures in "
        "Dec (short, not full convulsions, fluctuating awareness, "
        "self-terminating). In Feb he had 7 nocturnal seizures, and in Apr "
        "a single tonic seizure was recorded during respite care."
    )
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == "11 per 5 month"
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == (
        "He had a cluster of three seizures in Dec (short, not full "
        "convulsions, fluctuating awareness, self-terminating). In Feb "
        "he had 7 nocturnal seizures, and in Apr a single tonic seizure "
        "was recorded"
    )
    assert result.diagnostics["evidence_valid"] is True


def test_pipeline_selects_more_frequent_no_more_than_weekly_semiology() -> None:
    result = Gan2026PipelineV1().run(
        _record(
            "Over the past year seizure control has been relatively stable. "
            "She experiences two generalised tonic-clonic seizures every "
            "2 months. Absence seizures remain infrequent, usually no more than "
            "twice weekly, and myoclonic jerks are reported only occasionally."
        )
    )

    assert result.output.final_value == "2 per week"
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == "no more than twice weekly"
    assert result.diagnostics["evidence_valid"] is True


def test_pipeline_extracts_persistent_adverbial_semiology_rates() -> None:
    result = Gan2026PipelineV1().run(
        _record(
            "Only a single tonic-clonic seizure occurred over the past six months. "
            "Brief myoclonic jerks persist daily on awakening but are considered "
            "tolerable."
        )
    )

    assert result.output.final_value == "1 per day"
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == (
        "Brief myoclonic jerks persist daily"
    )
    assert result.diagnostics["evidence_valid"] is True


def test_pipeline_prefers_current_improved_frequency_over_historical_baseline() -> None:
    note_text = (
        "Prior to this period the seizures were occurring every 1 or 2 weeks. "
        "Over the past year, however, the current pattern is <= two or four per year."
    )
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == "2 to 4 per year"
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == "two or four per year"
    assert result.diagnostics["evidence_valid"] is True


def test_pipeline_ignores_medication_dose_frequencies() -> None:
    note_text = (
        "Dose is levetiracetam 1 g twice a day. Patient reports 5 or 7 epileptic "
        "spasms this year."
    )
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == "5 to 7 per year"
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == "5 or 7 epileptic spasms this year"
    assert result.diagnostics["evidence_valid"] is True
