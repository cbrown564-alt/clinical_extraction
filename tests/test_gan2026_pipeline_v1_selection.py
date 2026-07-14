"""Invariant-focused tests for gan2026 pipeline v1 selection."""

import pytest

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


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "His seizures typically occur in clusters, generally spaced four days "
            "apart, though brief periods of daily seizures have been reported.",
            "1 per 4 day",
            "seizures typically occur in clusters, generally spaced four days apart",
        ),
        (
            "His seizures typically occur in clusters, generally spaced four to "
            "five days apart, though brief periods of daily seizures have been "
            "reported.",
            "1 per 4 to 5 day",
            ("seizures typically occur in clusters, generally spaced four to five days apart"),
        ),
        (
            "His seizures typically occur in clusters, generally spaced 5 days "
            "apart, though brief periods of daily seizures have been reported.",
            "1 per 5 day",
            "seizures typically occur in clusters, generally spaced 5 days apart",
        ),
    ],
)
def test_pipeline_prefers_cluster_spacing_over_incidental_daily_mentions(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "Clinic Date: 21 April 2011. He had a cluster of three seizures in "
            "Dec (short, not full convulsions, fluctuating awareness, "
            "self-terminating). In Feb he had 7 nocturnal seizures, and in Apr "
            "a single tonic seizure was recorded during respite care.",
            "11 per 5 month",
            (
                "He had a cluster of three seizures in Dec (short, not full "
                "convulsions, fluctuating awareness, self-terminating). In Feb "
                "he had 7 nocturnal seizures, and in Apr a single tonic seizure "
                "was recorded"
            ),
        ),
        (
            "Clinic Date: 24 August 2012. In March he had a run of six seizures "
            "within half an hour (not full generalised tonic-clonic, fluctuating "
            "in intensity, resolved without medication). In June there was two "
            "further seizures at night, and in August another during physiotherapy.",
            "9 per 6 month",
            (
                "In March he had a run of six seizures within half an hour (not "
                "full generalised tonic-clonic, fluctuating in intensity, resolved "
                "without medication). In June there was two further seizures at "
                "night, and in August another"
            ),
        ),
    ],
)
def test_pipeline_extracts_sparse_parenthetical_month_event_lists(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize("count", ["two", "3", "four"])
def test_pipeline_selects_more_frequent_no_more_than_weekly_semiology(count: str) -> None:
    result = Gan2026PipelineV1().run(
        _record(
            "Over the past year seizure control has been relatively stable. "
            f"She experiences {count} generalised tonic-clonic seizures every "
            "2 months. Absence seizures remain infrequent, usually no more than "
            "twice weekly, and myoclonic jerks are reported only occasionally."
        )
    )

    assert result.output.final_value == "2 per week"
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == "no more than twice weekly"
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "He suffers clusters of absence seizures on four to five days each week. "
            "Nocturnal tonic seizures continue to occur around once per year.",
            "4 to 5 cluster per week, multiple per cluster",
            "clusters of absence seizures on four to five days each week",
        ),
        (
            "He suffers clusters of absence seizures on five days each month. "
            "Nocturnal tonic seizures continue to occur around once per year.",
            "5 cluster per month, multiple per cluster",
            "clusters of absence seizures on five days each month",
        ),
    ],
)
def test_pipeline_extracts_cluster_days_per_period(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("period", "expected_label"),
    [("daily", "1 per day"), ("weekly", "1 per week"), ("monthly", "1 per month")],
)
def test_pipeline_extracts_persistent_adverbial_semiology_rates(
    period: str,
    expected_label: str,
) -> None:
    result = Gan2026PipelineV1().run(
        _record(
            "Only a single tonic-clonic seizure occurred over the past six months. "
            f"Brief myoclonic jerks persist {period} on awakening but are considered "
            "tolerable."
        )
    )

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == (
        f"Brief myoclonic jerks persist {period}"
    )
    assert result.diagnostics["evidence_valid"] is True


def test_pipeline_extracts_counted_adverbial_monthly_events() -> None:
    result = Gan2026PipelineV1().run(
        _record(
            "He has experienced ongoing focal impaired-awareness seizures, typically "
            "four episodes monthly. These resolve spontaneously."
        )
    )

    assert result.output.final_value == "4 per month"
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == "typically four episodes monthly"
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "Prior to this period the seizures were occurring every 1 or 2 weeks. "
            "Over the past year, however, the current pattern is <= two or four per year.",
            "2 to 4 per year",
            "two or four per year",
        ),
        (
            "Previously, the seizure frequency was weekly clusters, usually three events. "
            "Over the past five months on the present regimen, events have reduced to "
            "<= once per month.",
            "1 per month",
            "once per month",
        ),
        (
            "Prior to recent lifestyle changes, the patient reports five focal onset "
            "seizures and four focal automatisms in the past two months. The patient "
            "now describes a simple partial seizure monthly.",
            "1 per month",
            "simple partial seizure monthly",
        ),
    ],
)
def test_pipeline_prefers_current_improved_frequency_over_historical_baseline(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "Dose is levetiracetam 1 g twice a day. Patient reports 5 or 7 epileptic "
            "spasms this year.",
            "5 to 7 per year",
            "5 or 7 epileptic spasms this year",
        ),
        (
            "Current treatment is levetiracetam 500 mg twice a day. Over the last "
            "two months he has documented five to six focal automatisms during the "
            "last two months.",
            "5 to 6 per 2 month",
            "five to six focal automatisms during the last two months",
        ),
        (
            "Carbamazepine dose is 200 mg twice a day. Patient reports an absence "
            "seizure every other week.",
            "1 per 2 week",
            "seizure every other week",
        ),
    ],
)
def test_pipeline_ignores_medication_dose_frequencies(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "She reports brief absences occurring on most weekdays, often clustering "
            "around late afternoon. There has been one tonic-clonic seizure in the "
            "last eight weeks.",
            "multiple per week",
            "brief absences occurring on most weekdays",
        ),
        (
            "Since the last review, the patient reports several focal seizures last "
            "week characterised by brief behavioural arrest.",
            "multiple per week",
            "several focal seizures last week",
        ),
        (
            "She reports nocturnal episodes occurring once per night on average for "
            "the past three months. Sumatriptan is used <=4 per month for migraine.",
            "1 per day",
            "occurring once per night",
        ),
    ],
)
def test_pipeline_extracts_current_qualitative_high_frequency_phrasing(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] in {
        FrequencyLabelKind.FREQUENCY,
        FrequencyLabelKind.UNRESOLVED_MULTIPLE,
    }
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


def test_pipeline_prefers_convulsive_event_count_over_nonprogressive_myoclonic_jerks() -> None:
    result = Gan2026PipelineV1().run(
        _record(
            "He described a clear increase in events over the last quarter, noting "
            "two drop attacks and nine convulsions in the past three months. The "
            "diary still records intermittent myoclonic jerks upon awakening once "
            "or twice per week without progression to convulsion."
        )
    )

    assert result.output.final_value == "11 per 3 month"
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == (
        "two drop attacks and nine convulsions in the past three months"
    )
    assert result.diagnostics["evidence_valid"] is True
