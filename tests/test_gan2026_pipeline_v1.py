import pytest

from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanRecord,
    load_records_with_monthly_frequency,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluate import (
    evaluate_frequency_records,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    FrequencyLabelKind,
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
    ("note_text", "expected_label", "expected_kind"),
    [
        (
            "Present Seizure Frequency: Two events over the last five months.",
            "2 per 5 month",
            FrequencyLabelKind.FREQUENCY,
        ),
        (
            "Regarding current events, he still has focal onset seizures four times per day, "
            "and tonic-clonic seizures 2 times per month.",
            "4 per day",
            FrequencyLabelKind.FREQUENCY,
        ),
        (
            "Over the past three months they describe several episodes per week of brief "
            "generalised events.",
            "multiple per week",
            FrequencyLabelKind.UNRESOLVED_MULTIPLE,
        ),
    ],
)
def test_pipeline_extracts_simple_current_frequency_rates(
    note_text: str,
    expected_label: str,
    expected_kind: FrequencyLabelKind,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == expected_kind
    assert result.diagnostics["final_selection"]["monthly_frequency"] is not None
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "Present Seizure Frequency: focal seizures every 6 days.",
            "1 per 6 day",
            "seizures every 6 days",
        ),
        (
            "Present Seizure Frequency: focal seizures every seven to nine days.",
            "1 per 7 to 9 day",
            "seizures every seven to nine days",
        ),
        (
            "Present Seizure Frequency: tonic-clonic seizures once a week.",
            "1 per week",
            "seizures once a week",
        ),
        (
            "Present Seizure Frequency: monthly seizures.",
            "1 per month",
            "monthly seizures",
        ),
        (
            "Present Seizure Frequency: bimonthly seizures.",
            "1 per 2 month",
            "bimonthly seizures",
        ),
        (
            "The carer reports that seizures are occurring every 2 days on average.",
            "1 per 2 day",
            "occurring every 2 days",
        ),
        (
            "Since review, events tend to cluster every seven to nine days.",
            "1 per 7 to 9 day",
            "cluster every seven to nine days",
        ),
        (
            "The patient reports ongoing episodes occurring every 3 - 4 weeks.",
            "1 per 3 to 4 week",
            "occurring every 3 - 4 weeks",
        ),
        (
            "Frequency is now reported as twice a month.",
            "2 per month",
            "twice a month",
        ),
        (
            "She describes her seizures as occurring roughly yearly.",
            "1 per year",
            "occurring roughly yearly",
        ),
        (
            "She notes the events are occurring bimonthly on average.",
            "1 per 2 month",
            "occurring bimonthly",
        ),
        (
            "Current seizure frequency is daily.",
            "1 per day",
            "daily",
        ),
        (
            "The caregiver says brief episodes occur daily.",
            "1 per day",
            "occur daily",
        ),
        (
            "In clinic they report 12 to 30 per quarter.",
            "12 to 30 per 3 month",
            "12 to 30 per quarter",
        ),
        (
            "They believe there were 3 or 5 seizures last month.",
            "3 to 5 per month",
            "3 or 5 seizures last month",
        ),
        (
            "He describes three or four seizures last week.",
            "3 to 4 per week",
            "three or four seizures last week",
        ),
        (
            "The diary shows 7 to 9 focal onset seizures in three weeks.",
            "7 to 9 per 3 week",
            "7 to 9 focal onset seizures in three weeks",
        ),
        (
            "The diary shows 21 to 28 epileptic spasms in three months.",
            "21 to 28 per 3 month",
            "21 to 28 epileptic spasms in three months",
        ),
        (
            "The diary lists six or eight petit mal over the past month.",
            "6 to 8 per month",
            "six or eight petit mal over the past month",
        ),
        (
            "The family reports 3 or 5 tonic-clonic over the past month.",
            "3 to 5 per month",
            "3 or 5 tonic-clonic over the past month",
        ),
        (
            "Family counted 3 or 4 focal impaired awareness seizures this week.",
            "3 to 4 per week",
            "3 or 4 focal impaired awareness seizures this week",
        ),
        (
            "She describes 6 to 7 myoclonic per week.",
            "6 to 7 per week",
            "6 to 7 myoclonic per week",
        ),
        (
            "The patient describes two or four seizures over the past year.",
            "2 to 4 per year",
            "two or four seizures over the past year",
        ),
        (
            "The patient reported 1 tonic-clonic seizures yesterday.",
            "1 per day",
            "1 tonic-clonic seizures yesterday",
        ),
        (
            "These have become frequent, with seizures every other day.",
            "1 per 2 day",
            "seizures every other day",
        ),
        (
            "The current pattern is seizures every other week.",
            "1 per 2 week",
            "seizures every other week",
        ),
        (
            "Focal impaired-awareness events are now occurring only every other month or so.",
            "1 per 2 month",
            "occurring only every other month",
        ),
        (
            "This week he has had 3 or 4 focal impaired awareness seizures.",
            "3 to 4 per week",
            "This week he has had 3 or 4 focal impaired awareness seizures",
        ),
        (
            "Over the past month, they estimate 3 to 4 seizures.",
            "3 to 4 per month",
            "Over the past month, they estimate 3 to 4 seizures",
        ),
        (
            "She now describes seizures every night.",
            "1 per day",
            "seizures every night",
        ),
        (
            "The current pattern is tonic-clonic every night.",
            "1 per day",
            "tonic-clonic every night",
        ),
        (
            "They report a myoclonic jerk daily.",
            "1 per day",
            "myoclonic jerk daily",
        ),
        (
            "Current diary summary: focal cognitive monthly.",
            "1 per month",
            "focal cognitive monthly",
        ),
        (
            "They report larger convulsive events occurring tonic-clonic daily.",
            "1 per day",
            "tonic-clonic daily",
        ),
        (
            "In terms of timing, he tends to experience a spell roughly once in a fortnight.",
            "1 per 2 week",
            "once in a fortnight",
        ),
        (
            "He phrased it as happening about every second week.",
            "1 per 2 week",
            "happening about every second week",
        ),
        (
            "Importantly, the median inter-seizure interval ≈ six weeks.",
            "1 per 6 week",
            "median inter-seizure interval ≈ six weeks",
        ),
        (
            "Current seizure control: Median inter-seizure interval ≈ four months.",
            "1 per 4 month",
            "Median inter-seizure interval ≈ four months",
        ),
        (
            "Seizures: Patient reports events occurring with intervals ranging 14 - 21 days.",
            "1 per 14 to 21 day",
            "events occurring with intervals ranging 14 - 21 days",
        ),
        (
            "They report intervals ranging three - four days between focal aware seizures.",
            "1 per 3 to 4 day",
            "intervals ranging three - four days",
        ),
        (
            "Event pattern: Every 8 days on average.",
            "1 per 8 day",
            "Every 8 days on average",
        ),
        (
            "Current seizure control: Median inter-seizure interval ≈ four months. "
            "Background to improvement: Prior to this, events clustered approximately "
            "every four to five days.",
            "1 per 4 month",
            "Median inter-seizure interval ≈ four months",
        ),
    ],
)
def test_pipeline_extracts_implicit_one_event_rates(
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
            "The diary records one tonic-clonic and six petit mal in last week.",
            "7 per week",
            "one tonic-clonic and six petit mal in last week",
        ),
        (
            "Family report two focal epileptic spasms and one focal non-motor in last month.",
            "3 per month",
            "two focal epileptic spasms and one focal non-motor in last month",
        ),
        (
            "She has had two drop attacks and nine absence seizures in the past six months.",
            "11 per 6 month",
            "two drop attacks and nine absence seizures in the past six months",
        ),
        (
            "He has had four absence seizures and one myoclonic this month.",
            "5 per month",
            "four absence seizures and one myoclonic this month",
        ),
        (
            "He described a single very brief event last month after night duties.",
            "1 per month",
            "single very brief event last month",
        ),
        (
            "Over the past four months, she reports three events in that timeframe.",
            "3 per 4 month",
            "Over the past four months, she reports three events in that timeframe",
        ),
        (
            "Over the past four months, she describes seizure activity separated by clear "
            "periods without symptoms, with intermittent episodes punctuated by normal "
            "intervals. She reports three events in that timeframe: two morning episodes "
            "and one evening event.",
            "3 per 4 month",
            (
                "Over the past four months, she describes seizure activity separated by clear "
                "periods without symptoms, with intermittent episodes punctuated by normal "
                "intervals. She reports three events in that timeframe"
            ),
        ),
    ],
)
def test_pipeline_sums_distributed_recent_event_counts(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


def test_pipeline_preserves_seizure_free_as_semantic_state() -> None:
    result = Gan2026PipelineV1().run(
        _record("He has been seizure free for a long duration and over several years.")
    )

    assert result.output.final_value == "seizure free for multiple year"
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.SEIZURE_FREE


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "She remains free of seizures for two years on the current regimen.",
            "seizure free for 2 year",
            "free of seizures for two years",
        ),
        (
            "There have been no seizures since the last clinic review.",
            "seizure free for multiple year",
            "no seizures since",
        ),
    ],
)
def test_pipeline_extracts_common_seizure_free_phrasing(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.SEIZURE_FREE
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


def test_pipeline_breakthrough_event_overrides_seizure_free_history() -> None:
    result = Gan2026PipelineV1().run(
        _record(
            "She had been seizure free for two years, but now reports "
            "three seizures last month."
        )
    )

    assert result.output.final_value == "3 per month"
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY


def test_pipeline_distinguishes_no_reference_from_unknown_frequency() -> None:
    result = Gan2026PipelineV1().run(
        _record("This appointment was cancelled. Medication list unchanged.")
    )

    assert result.output.final_value == "no seizure frequency reference"
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.NO_REFERENCE


def test_pipeline_keeps_cluster_structure_in_diagnostics() -> None:
    result = Gan2026PipelineV1().run(
        _record("Cluster days twice this month; typically six seizures in 24 h.")
    )

    assert result.output.final_value == "2 cluster per month, 6 per cluster"
    assert result.diagnostics["candidate_events"][0]["kind"] == "cluster_frequency"
    assert result.diagnostics["normalized_events"][0]["normalized_label"] == (
        "2 cluster per month, 6 per cluster"
    )


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "Over the past fortnight she describes a run of brief events, "
            "with three short episodes occurring on separate days.",
            "1 cluster per 2 week, 3 per cluster",
            (
                "Over the past fortnight she describes a run of brief events, "
                "with three short episodes occurring on separate days"
            ),
        ),
        (
            "Over the past month, the patient reports a cluster of short events "
            "on multiple days.",
            "multiple cluster per month, multiple per cluster",
            (
                "Over the past month, the patient reports a cluster of short events "
                "on multiple days"
            ),
        ),
        (
            "Over the past four weeks he reports 2 clusters this month; "
            "each approx five absences in the morning.",
            "2 cluster per month, 5 per cluster",
            "2 clusters this month; each approx five absences",
        ),
        (
            "Monthly clusters, typically 6 to 7 seizures over 24 h.",
            "1 cluster per month, 6 to 7 per cluster",
            "Monthly clusters, typically 6 to 7 seizures over 24 h",
        ),
    ],
)
def test_pipeline_extracts_validation_cluster_patterns(
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
            "Seizure days: six/30 this month.",
            "6 per month",
            "Seizure days: six/30 this month",
        ),
        (
            "About three seizure days per week are reported.",
            "3 per week",
            "About three seizure days per week",
        ),
        (
            "Clinic shorthand says TC *nine/mo.",
            "9 per month",
            "TC *nine/mo",
        ),
        (
            "Clinic shorthand says TC *5/wk.",
            "5 per week",
            "TC *5/wk",
        ),
        (
            "Diary summary says TC nine/mo.",
            "9 per month",
            "TC nine/mo",
        ),
        (
            "Current frequency reported as: sz ×nine/mo.",
            "9 per month",
            "sz ×nine/mo",
        ),
        (
            "Seizures worsen, up to seven in bad weeks.",
            "7 per week",
            "up to seven in bad weeks",
        ),
        (
            "Diary shorthand says abs *monthly.",
            "1 per month",
            "abs *monthly",
        ),
        (
            "Diary shorthand says abs Xmonthly.",
            "1 per month",
            "abs Xmonthly",
        ),
        (
            "On their calendar, abs 8 monthly over the past three months.",
            "8 per month",
            "abs 8 monthly",
        ),
        (
            "The current clinic shorthand is qtwo - threewk.",
            "1 per 2 to 3 week",
            "qtwo - threewk",
        ),
        (
            "The current clinic shorthand is q2 - 3wk.",
            "1 per 2 to 3 week",
            "q2 - 3wk",
        ),
        (
            "The current clinic shorthand is q1 - 2d.",
            "1 per 1 to 2 day",
            "q1 - 2d",
        ),
        (
            "Recent diary: seven to eight absence seizures this quarter.",
            "7 to 8 per 3 month",
            "seven to eight absence seizures this quarter",
        ),
        (
            "There were nineteen episode of status epilepticus in the past week.",
            "19 per week",
            "nineteen episode of status epilepticus in the past week",
        ),
        (
            "The diary documents: Seizure events on 03-07, 03-27, 05-15, 05-19, 05-24.",
            "5 per 2 month",
            "Seizure events on 03-07, 03-27, 05-15, 05-19, 05-24",
        ),
        (
            "Seizure: 2022: Jan x1, Feb x0, Mar x1, Apr x2, May x1, Jun x1, Jul x1.",
            "7 per 7 month",
            "Seizure: 2022: Jan x1, Feb x0, Mar x1, Apr x2, May x1, Jun x1, Jul x1",
        ),
    ],
)
def test_pipeline_extracts_validation_shorthand_frequency_patterns(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


def test_pipeline_handles_cluster_size_with_unknown_frequency() -> None:
    result = Gan2026PipelineV1().run(
        _record(
            "Clusters characterized by two focal impaired-awareness seizures; frequency unclear."
        )
    )

    assert result.output.final_value == "unknown, 2 per cluster"
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.UNKNOWN


def test_pipeline_can_score_a_small_known_row_subset() -> None:
    records = {
        record.source_row_index: record
        for record in load_records_with_monthly_frequency()
        if record.source_row_index in {11118, 12383, 5555, 13485, 11434}
    }
    pipeline = Gan2026PipelineV1()
    scored_rows = []
    for record in records.values():
        result = pipeline.run(record)
        scored_rows.append(
            {
                "gold_monthly_frequency": record.gold_monthly_frequency,
                "prediction": result.diagnostics["final_selection"]["monthly_frequency"],
            }
        )

    metrics = evaluate_frequency_records(scored_rows, prediction_key="prediction", method="purist")

    assert metrics["micro"]["accuracy"] >= 0.8
