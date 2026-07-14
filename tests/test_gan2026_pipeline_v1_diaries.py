"""Invariant-focused tests for gan2026 pipeline v1 diaries."""

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
            "Clinic Date: 10 May 2015. Seizures in 2014-2015: May: 5 days with "
            "more severe seizures June: 5 days with seizures July: 12 days August: "
            "3 days, most of them at sleep time, September: 12 days, October: 3 "
            "days with seizures November: 7 days with seizures, December: 5 days "
            "with more severe seizures January: 4 days, February: 2 days with "
            "seizures March: 5 days with more severe seizures, April: 1 days with "
            "seizures.",
            "64 per 12 month",
            (
                "Seizures in 2014-2015: May: 5 days with more severe seizures "
                "June: 5 days with seizures July: 12 days August: 3 days, most of "
                "them at sleep time, September: 12 days, October: 3 days with "
                "seizures November: 7 days with seizures, December: 5 days with "
                "more severe seizures January: 4 days, February: 2 days with "
                "seizures March: 5 days with more severe seizures, April: 1 days "
                "with seizures"
            ),
        ),
        (
            "Clinic Date: 22 April 2025. Seizures in 2024-2025: Aug: 6 days, most "
            "of them at sleep time, Sep: 11 days with seizures, Oct: 1 days, Nov: "
            "7 days, most of them at sleep time, Dec: 8 days with seizures Jan: "
            "9 days, Feb: 8 days with seizures Mar: 2 days.",
            "52 per 8 month",
            (
                "Seizures in 2024-2025: Aug: 6 days, most of them at sleep time, "
                "Sep: 11 days with seizures, Oct: 1 days, Nov: 7 days, most of "
                "them at sleep time, Dec: 8 days with seizures Jan: 9 days, Feb: "
                "8 days with seizures Mar: 2 days"
            ),
        ),
    ],
)
def test_pipeline_extracts_seizure_day_annual_logs(
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
            "Clinic Date: 25 February 2022. On 25/Jan his absences improved after "
            "medication adjustment. His last event was on 30/Jan and he has "
            "remained well since.",
            "1 per month",
            "His last event was on 30/Jan",
        ),
        (
            "Clinic Date: 29 June 2020. On 28/Apr his absences improved after "
            "medication adjustment. His last event was on 03/May and he has "
            "remained well since.",
            "1 per 2 month",
            "His last event was on 03/May",
        ),
        (
            "From: Dr Thomas Reed Sent: 29 June 2020 10:15 To: epilepsy.clinic@nhs.net. "
            "On 28/Apr his absences improved after medication adjustment. His last "
            "event was on 03/May and he has remained well since.",
            "1 per 2 month",
            "His last event was on 03/May",
        ),
        (
            "Clinic Date: 16 January 2022. On 15 October his absences settled with "
            "treatment. The most recent episode was on 23 October, and since then "
            "he has been well.",
            "1 per 3 month",
            "The most recent episode was on 23 October",
        ),
    ],
)
def test_pipeline_extracts_last_event_date_summaries(
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
            "Clinic Date: 09 May 2023. Last tonic-clonic seizure was in Apr/2022, "
            "with 3 morning jerks since then.",
            "4 per 13 month",
            "Last tonic-clonic seizure was in Apr/2022, with 3 morning jerks since then",
        ),
        (
            "Clinic Date: 10 April 2025. Last tonic-clonic seizure was in 1 - 2024, "
            "with 2 to 3 morning jerks since then.",
            "3 to 4 per 15 month",
            ("Last tonic-clonic seizure was in 1 - 2024, with 2 to 3 morning jerks since then"),
        ),
        (
            "Clinic Date: 08 June 2016. Her last clearly witnessed tonic-clonic "
            "seizure was in 3/2015, with four morning jerks since then.",
            "4 per 15 month",
            (
                "last clearly witnessed tonic-clonic seizure was in 3/2015, with "
                "four morning jerks since then"
            ),
        ),
        (
            "Clinic Date: 09 August 2018. No further tonic-clonic seizures have "
            "occurred since 06/2017, although three single jerks remain.",
            "3 per 14 month",
            (
                "No further tonic-clonic seizures have occurred since 06/2017, "
                "although three single jerks remain"
            ),
        ),
        (
            "From: Dr Alice Morgan Date: 11 March 2022 To: neurology.team@nhs.net. "
            "No further tonic-clonic seizures have occurred since 12/2020, although "
            "two to three single jerks remain.",
            "2 to 3 per 15 month",
            (
                "No further tonic-clonic seizures have occurred since 12/2020, "
                "although two to three single jerks remain"
            ),
        ),
    ],
)
def test_pipeline_extracts_numeric_month_year_residual_jerk_spans(
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
            "Clinic Date: 09 June 2023. Her last convulsive seizure was recorded "
            "in 03/2022, with occasional clusters of myoclonic jerks persisting.",
            "multiple cluster per 15 month, multiple per cluster",
            (
                "Her last convulsive seizure was recorded in 03/2022, with "
                "occasional clusters of myoclonic jerks persisting"
            ),
        ),
        (
            "Clinic Date: 09 July 2019. Her last convulsive seizure was recorded "
            "in June 2018, with occasional clusters of myoclonic jerks persisting.",
            "multiple cluster per 13 month, multiple per cluster",
            (
                "Her last convulsive seizure was recorded in June 2018, with "
                "occasional clusters of myoclonic jerks persisting"
            ),
        ),
    ],
)
def test_pipeline_extracts_last_convulsive_cluster_persistence_spans(
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
            "He can sometimes go nearly two week without seizures, but when they "
            "recur he tends to have several in one day, often between 4 and 6.",
            "1 cluster per 2 week, 4 to 6 per cluster",
            (
                "go nearly two week without seizures, but when they recur he tends "
                "to have several in one day, often between 4 and 6"
            ),
        ),
        (
            "On occasions she is seizure-free for four to five consecutive days, "
            "followed by a day with multiple events, typically two tonic seizures.",
            "1 cluster per 4 to 5 day, 2 per cluster",
            (
                "seizure-free for four to five consecutive days, followed by a day "
                "with multiple events, typically two tonic seizures"
            ),
        ),
        (
            "He may go 3 days without seizures, but when they happen he often has "
            "them in batches, with four occurring within 24 hours.",
            "1 cluster per 3 day, 4 per cluster",
            (
                "go 3 days without seizures, but when they happen he often has them "
                "in batches, with four occurring within 24 hours"
            ),
        ),
    ],
)
def test_pipeline_extracts_seizure_free_interval_cluster_cycles(
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
            "His absence seizures are now occurring on two to three days of the "
            "week, whereas previously they were restricted to once every couple "
            "of weeks.",
            "2 to 3 per week",
            "absence seizures are now occurring on two to three days of the week",
        ),
        (
            "His absence seizures are now occurring on four days of the week, "
            "whereas previously they were restricted to once every couple of weeks.",
            "4 per week",
            "absence seizures are now occurring on four days of the week",
        ),
    ],
)
def test_pipeline_extracts_current_days_of_week_frequency(
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
            "Clinic Date: 13 January 2024. In October he had two seizures during "
            "sleep and none while awake. In December he had three in sleep and no "
            "while awake.",
            "5 per 3 month",
            (
                "In October he had two seizures during sleep and none while awake. "
                "In December he had three in sleep and no while awake"
            ),
        ),
        (
            "Clinic Date: 25 July 2014. In Jun he had a nocturnal seizure but no "
            "daytime events. In July he had three nocturnal seizures and 5 while awake.",
            "9 per 2 month",
            (
                "In Jun he had a nocturnal seizure but no daytime events. In July "
                "he had three nocturnal seizures and 5 while awake"
            ),
        ),
        (
            "Clinic Date: 7 May 2023. In Feb he had 3 in sleep and one while awake. "
            "In Apr he had five in sleep and no while awake.",
            "9 per 3 month",
            (
                "In Feb he had 3 in sleep and one while awake. In Apr he had five "
                "in sleep and no while awake"
            ),
        ),
    ],
)
def test_pipeline_extracts_two_month_sleep_awake_diary_summaries(
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
            "Clinic Date: 25 September 2024. She has had no seizures so far this "
            "month, four in August, one in July and 3 in June, with events reported "
            "from both daytime and nocturnal periods.",
            "8 per 4 month",
            (
                "She has had no seizures so far this month, four in August, one in "
                "July and 3 in June"
            ),
        ),
        (
            "Clinic Date: 24 September 2011. He experienced 2 generalised "
            "tonic-clonic seizures so far in Sep, one in Aug, and 0 in Jul, "
            "occurring during both wakefulness and sleep.",
            "3 per 3 month",
            ("2 generalised tonic-clonic seizures so far in Sep, one in Aug, and 0 in Jul"),
        ),
        (
            "Clinic Date: 24 March 2024. This month so far she has no seizures; "
            "earlier 4 in February, 0 in January and 7 in December, over waking "
            "hours and sleep.",
            "11 per 4 month",
            (
                "This month so far she has no seizures; earlier 4 in February, "
                "0 in January and 7 in December"
            ),
        ),
    ],
)
def test_pipeline_extracts_recent_month_count_diary_summaries(
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
            "Clinic Date: 23 September 2022. He reports 6 seizure events in "
            "September, 6 in August and four in July, and 2 in June, from both "
            "daytime and nocturnal periods.",
            "18 per 4 month",
            (
                "He reports 6 seizure events in September, 6 in August and four in "
                "July, and 2 in June"
            ),
        ),
        (
            "Clinic Date: 5 July 2019. She noted no seizures in June, four in May, "
            "and four in April, all from mixed awake/asleep states.",
            "8 per 3 month",
            "She noted no seizures in June, four in May, and four in April",
        ),
        (
            "Clinic Date: 5 October 2018. He has recorded three seizures to date in "
            "September, 4 in August and three in July, including nocturnal and "
            "daytime periods.",
            "10 per 3 month",
            ("He has recorded three seizures to date in September, 4 in August and three in July"),
        ),
    ],
)
def test_pipeline_extracts_reported_monthly_count_lists(
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
            "Clinic Date: 20 February 2024. He had a cluster of three seizures in "
            "August. In November he had a nocturnal seizure, and in February a "
            "single tonic seizure was recorded during respite care.",
            "5 per 7 month",
            (
                "He had a cluster of three seizures in August. In November he had "
                "a nocturnal seizure, and in February a single tonic seizure was "
                "recorded"
            ),
        ),
        (
            "Clinic Date: 10 October 2020. In Apr she experienced four short "
            "absences in a cluster. In Jul there was 2 further brief absences, and "
            "in Sep another at school.",
            "7 per 6 month",
            (
                "In Apr she experienced four short absences in a cluster. In Jul "
                "there was 2 further brief absences, and in Sep another"
            ),
        ),
        (
            "Clinic Date: 4 March 2026. In September a prolonged focal seizure "
            "settled spontaneously. In November a tonic seizure was recorded, "
            "and in February another during physiotherapy.",
            "3 per 6 month",
            (
                "In September a prolonged focal seizure settled spontaneously. "
                "In November a tonic seizure was recorded, and in February another"
            ),
        ),
        (
            "Clinic Date: 22 September 2010. A prolonged event occurred in Apr "
            "(approximately 12 minutes). In Jul she had a drop attack, and in Sep "
            "seven myoclonic jerks were documented at college.",
            "9 per 6 month",
            (
                "A prolonged event occurred in Apr (approximately 12 minutes). "
                "In Jul she had a drop attack, and in Sep seven myoclonic jerks "
                "were documented at college"
            ),
        ),
    ],
)
def test_pipeline_extracts_sparse_cluster_and_event_month_lists(
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
            "Clinic Date: 6 April 2019. He has recorded 2 seizures to date in "
            "March, 7 in February and six in January, including nocturnal and "
            "daytime periods. He will continue daily seizure recording.",
            "15 per 3 month",
            ("He has recorded 2 seizures to date in March, 7 in February and six in January"),
        ),
        (
            "Clinic Date: 24 January 2013. This month, she has had six convulsions; "
            "0 were in December and 5 in November, across day and night.",
            "11 per 3 month",
            ("This month, she has had six convulsions; 0 were in December and 5 in November"),
        ),
        (
            "Clinic Date: 25 September 2014. As of this month she reports four "
            "seizure events; 3 in August, three in July and five in June during "
            "both sleep and wakefulness.",
            "15 per 4 month",
            (
                "As of this month she reports four seizure events; 3 in August, "
                "three in July and five in June"
            ),
        ),
    ],
)
def test_pipeline_extracts_extended_month_count_lists(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True
