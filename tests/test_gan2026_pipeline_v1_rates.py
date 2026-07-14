"""Invariant-focused tests for gan2026 pipeline v1 rates."""

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
            "These events have been occurring multiple times in past week.",
            "multiple per week",
            "occurring multiple times in past week",
        ),
        (
            "Current status: Several episodes per week, plus two tonic-clonic events "
            "over the past six months.",
            "multiple per week",
            "Several episodes per week",
        ),
        (
            "Brief focal episodes are now happening on most nights of the week.",
            "multiple per week",
            "happening on most nights of the week",
        ),
        (
            "Petit mal occur on a near-daily basis, sometimes dozens in a day, "
            "making accurate quantification challenging.",
            "multiple per day",
            "Petit mal occur on a near-daily basis, sometimes dozens in a day",
        ),
        (
            "Generalised tonic-clonic seizures are rare, typically 3 events per year. "
            "Focal sensory episodes occur several times each week, particularly in "
            "the evenings.",
            "multiple per week",
            "Focal sensory episodes occur several times each week",
        ),
        (
            "Focal tonic events occur several times per week, with convulsions only "
            "twice per year.",
            "multiple per week",
            "Focal tonic events occur several times per week",
        ),
        (
            "Generalised convulsions are rare. Focal non-motor occur several times "
            "each week, particularly in the evenings.",
            "multiple per week",
            "Focal non-motor occur several times each week",
        ),
        (
            "Generalised tonic-clonic seizures are rare. Focal sensory occur several "
            "times each week.",
            "multiple per week",
            "Focal sensory occur several times each week",
        ),
        (
            "She describes brief absence-like spells on most days, with two "
            "generalised tonic-clonic seizures in the past eight weeks.",
            "multiple per week",
            "She describes brief absence-like spells on most days",
        ),
    ],
)
def test_pipeline_prioritizes_qualitative_high_frequency_current_patterns(
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


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "Current frequency and recent course: By his account, events have been occurring "
            "intermittently over the past three months, with two generalised convulsions in "
            "that period and approximately four focal impaired-awareness episodes, often "
            "clustering after a week of late shifts.",
            "6 per 3 month",
            (
                "over the past three months, with two generalised convulsions in that period "
                "and approximately four focal impaired-awareness episodes"
            ),
        ),
        (
            "Seizures: Over the past three months they report two brief myoclonic jerks on "
            "awakening and one generalised tonic-clonic event at approximately 03:00 in early "
            "September.",
            "3 per 3 month",
            (
                "Over the past three months they report two brief myoclonic jerks on "
                "awakening and one generalised tonic-clonic event"
            ),
        ),
        (
            "Present Seizure Frequency: Patient describes brief events most commonly "
            "clustering as they are drifting off to sleep. Over the past six weeks, four "
            "episodes have occurred, each lasting under two minutes.",
            "4 per 6 week",
            "Over the past six weeks, four episodes have occurred",
        ),
        (
            "He and his partner report that the spells tend to cluster during periods of "
            "heightened psychological pressure at work. Over the past three months he notes "
            "approximately 3-5 focal seizures per month.",
            "3 to 5 per month",
            "3-5 focal seizures per month",
        ),
    ],
)
def test_pipeline_extracts_contextual_period_first_frequency_counts(
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
            "Against this backdrop, he reports an increase in brief absence episodes and "
            "two myoclonic clusters over the past three weeks, alongside one generalised "
            "tonic-clonic seizure occurring late morning at work.",
            "2 cluster per 3 week, multiple per cluster",
            "two myoclonic clusters over the past three weeks",
        ),
        (
            "Seizures: The diary shows infrequent events predominantly aligned with delayed "
            "or missed ASM doses. Specifically: - 2025: January 0; February 1 generalised "
            "convulsion after missing evening valproate; March 0; April 0; May 1 absence "
            "cluster after late morning lamotrigine; June 0; July 0; August 1 generalised "
            "convulsion following two late doses; September 0.",
            "3 per 9 month",
            (
                "2025: January 0; February 1 generalised convulsion after missing evening "
                "valproate; March 0; April 0; May 1 absence cluster after late morning "
                "lamotrigine; June 0; July 0; August 1 generalised convulsion following "
                "two late doses; September 0"
            ),
        ),
        (
            "Frequency has increased: July x 3 focal aware motor; August x 4 focal aware "
            "motor; September x 5 focal aware motor with two focal to bilateral "
            "tonic-clonic.",
            "5 per month",
            "September x 5 focal aware motor",
        ),
        (
            "Seizures: Patient describes rare events that occur exclusively during prolonged "
            "physical exertion at work. Last event: 3 weeks ago on-site following extended "
            "machinery loading; prior to that, one event in late May 2025 during a "
            "high-demand shift.",
            "1 per 1 to 2 month",
            (
                "Last event: 3 weeks ago on-site following extended machinery loading; "
                "prior to that, one event in late May 2025"
            ),
        ),
    ],
)
def test_pipeline_extracts_contextual_trigger_and_diary_frequency_patterns(
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
            "There were two generalised tonic-clonic seizures in the past fortnight after "
            "many months without a convulsion.",
            "2 per 2 week",
            "two generalised tonic-clonic seizures in the past fortnight",
        ),
        (
            "Over the last three weeks, there have been four brief episodes featuring "
            "impaired awareness and post-event fatigue.",
            "4 per 3 week",
            (
                "Over the last three weeks, there have been four brief episodes featuring "
                "impaired awareness"
            ),
        ),
        (
            "Clips recorded on the family phone over the last eight weeks indicate brief "
            "generalised episodes occurring approximately twice weekly.",
            "2 per week",
            "occurring approximately twice weekly",
        ),
        (
            "Over the past six weeks he has experienced three clusters requiring recovery "
            "time off work, each comprising two to four brief events over 24-48 hours.",
            "3 cluster per 6 week, 2 to 4 per cluster",
            (
                "Over the past six weeks he has experienced three clusters requiring recovery "
                "time off work, each comprising two to four brief events"
            ),
        ),
        (
            "Clustering over the past six weeks (four focal impaired-awareness episodes "
            "and two focal aware auras).",
            "6 per 6 week",
            (
                "over the past six weeks (four focal impaired-awareness episodes "
                "and two focal aware auras"
            ),
        ),
        (
            "Over the last 12 weeks he recorded: July 0, August 2 brief events over one "
            "weekend, September 1 isolated event; no prolonged confusion reported.",
            "3 per 3 month",
            ("July 0, August 2 brief events over one weekend, September 1 isolated event"),
        ),
        (
            "She describes two clusters in the past six weeks, each comprising 1-2 brief "
            "focal-feeling spells with transient confusion and no injury.",
            "2 cluster per 6 week, 1 to 2 per cluster",
            ("two clusters in the past six weeks, each comprising 1-2 brief focal-feeling spells"),
        ),
        (
            "Since commencing ketogenic diet therapy, the family notes only seven brief "
            "seizures recorded in 2024 so far.",
            "7 per year",
            "seven brief seizures recorded in 2024 so far",
        ),
        (
            "Prior to commencing Lacosamide, episodes occurred at a rate of three to five "
            "focal sensory per week. Since titration to the current dose, the frequency has "
            "remained unchanged.",
            "3 to 5 per week",
            "rate of three to five focal sensory per week",
        ),
        (
            "The diary over the past two months records five focal automatisms per week on "
            "average, often clustering in the evening.",
            "5 per week",
            "records five focal automatisms per week",
        ),
        (
            "He describes warning features and reports 2 to 4 focal non-motor per week, "
            "usually clustering in the late afternoon.",
            "2 to 4 per week",
            "reports 2 to 4 focal non-motor per week",
        ),
        (
            "Weekly morning clusters reported; number per cluster not documented.",
            "1 cluster per week, multiple per cluster",
            "Weekly morning clusters reported",
        ),
        (
            "Seizure History This Quarter: Patient reports two clusters this quarter, both "
            "occurring in the context of poor sleep. Within each cluster, events were brief "
            "focal aware seizures.",
            "2 cluster per 3 month, multiple per cluster",
            "two clusters this quarter",
        ),
        (
            "With respect to seizures, he describes three clusters this quarter, each "
            "lasting 1-2 days with several brief episodes.",
            "3 cluster per 3 month, multiple per cluster",
            "three clusters this quarter, each lasting 1-2 days with several brief episodes",
        ),
        (
            "Diagnosis: Generalised epilepsy with ongoing nocturnal clusters 3x/month; good "
            "response to valproate.",
            "3 cluster per month, multiple per cluster",
            "nocturnal clusters 3x/month",
        ),
        (
            "Cluster frequency unclear this month; last month ≈4 clusters.",
            "4 cluster per month, multiple per cluster",
            "last month ≈4 clusters",
        ),
        (
            "Cluster frequency unclear this month; last month ≈three clusters.",
            "3 cluster per month, multiple per cluster",
            "last month ≈three clusters",
        ),
    ],
)
def test_pipeline_extracts_trigger_assertion_heavy_frequency_rows(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True
