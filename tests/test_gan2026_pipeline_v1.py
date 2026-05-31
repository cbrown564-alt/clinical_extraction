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
            (
                "July 0, August 2 brief events over one weekend, September 1 isolated event"
            ),
        ),
        (
            "She describes two clusters in the past six weeks, each comprising 1-2 brief "
            "focal-feeling spells with transient confusion and no injury.",
            "2 cluster per 6 week, 1 to 2 per cluster",
            (
                "two clusters in the past six weeks, each comprising 1-2 brief "
                "focal-feeling spells"
            ),
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


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "He remained seizure-free for 8 months after starting levetiracetam, "
            "before experiencing a generalised tonic-clonic seizure 3 Tuesdays ago, "
            "preceded by a cluster of absences.",
            "2 per 8 month",
            (
                "seizure-free for 8 months after starting levetiracetam, "
                "before experiencing a generalised tonic-clonic seizure 3 Tuesdays ago, "
                "preceded by a cluster of absences"
            ),
        ),
        (
            "On carbamazepine monotherapy he was seizure-free for five months, "
            "until a focal impaired-awareness seizure occurred three Thursdays ago.",
            "1 per 5 month",
            (
                "seizure-free for five months, until a focal impaired-awareness "
                "seizure occurred three Thursdays ago"
            ),
        ),
        (
            "She had no seizures for nearly a year following initiation of valproate, "
            "then developed myoclonic jerks leading to 3 tonic seizure 2 Saturdays ago.",
            "3 per year",
            (
                "no seizures for nearly a year following initiation of valproate, "
                "then developed myoclonic jerks leading to 3 tonic seizure 2 Saturdays ago"
            ),
        ),
        (
            "She may remain seizure-free for up to two month, but then will experience "
            "clusters of four seizures in a single day.",
            "1 cluster per 2 month, 4 per cluster",
            (
                "seizure-free for up to two month, but then will experience "
                "clusters of four seizures in a single day"
            ),
        ),
        (
            "She may remain seizure-free for up to 4 month, but then will experience "
            "clusters of three - four seizures in a single day.",
            "1 cluster per 4 month, 3 to 4 per cluster",
            (
                "seizure-free for up to 4 month, but then will experience "
                "clusters of three - four seizures in a single day"
            ),
        ),
        (
            "The driving plan is to reassess after the seizure-free interval. "
            "Follow-up in three months by video.",
            "no seizure frequency reference",
            "The driving plan is to reassess after the seizure-free interval.",
        ),
    ],
)
def test_pipeline_handles_temporal_seizure_free_distractors(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "Clinic Date: 10 August 2019. She discontinued Valproate on 10 Jul. "
            "Shortly afterwards, she experienced 2 to 3 seizures, one triggered by "
            "missed medication. She has remained seizure-free since then.",
            "2 to 3 per month",
            "Shortly afterwards, she experienced 2 to 3 seizures",
        ),
        (
            "Clinic Date: 24 March 2017. He came off Levetiracetam on 21-Feb. "
            "In the following week, he had two to three seizures, one associated "
            "with sleep deprivation. No further seizures have occurred since.",
            "2 to 3 per month",
            "In the following week, he had two to three seizures",
        ),
        (
            "Clinic Date: 05 June 2017. Lamotrigine was stopped on 4 Apr. Around "
            "that period, she had 4 seizures, one following alcohol intake. She has "
            "not had any further events since.",
            "4 per 2 month",
            "Around that period, she had 4 seizures",
        ),
        (
            "Clinic Date: 16 April 2019. He withdrew from Clobazam on 13-Jan. At "
            "that time, he had 3 - 4 seizures, one precipitated by illness. He has "
            "remained stable without seizures since.",
            "3 to 4 per 3 month",
            "At that time, he had 3 - 4 seizures",
        ),
    ],
)
def test_pipeline_extracts_medication_withdrawal_bursts_before_since_then_stability(
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
            "Clinic Date: 14 November 2014. His initial event was in July 2014 in "
            "Germany, arising from sleep. A second event occurred in Italy the "
            "following October 2014, once more during the night. He has had no "
            "further events since surgical intervention.",
            "2 per 3 month",
            (
                "His initial event was in July 2014 in Germany, arising from sleep. "
                "A second event occurred in Italy the following October 2014"
            ),
        ),
        (
            "Clinic Date: 14 November 2017. The first seizure was reported in March "
            "2017 while visiting relatives in Canada. The second and third event "
            "took place in November 2017 in the USA, again from sleep. There have "
            "been no further episodes since starting her current regimen.",
            "3 per 8 month",
            (
                "The first seizure was reported in March 2017 while visiting "
                "relatives in Canada. The second and third event took place in "
                "November 2017"
            ),
        ),
        (
            "Clinic Date: 10 April 2016. No further tonic-clonic seizures have "
            "occurred since Jan-2015, although 2 to 3 single jerks remain. There "
            "have been no absences reported by the patient or observed by family "
            "since late 2015.",
            "2 to 3 per 15 month",
            (
                "No further tonic-clonic seizures have occurred since Jan-2015, "
                "although 2 to 3 single jerks remain"
            ),
        ),
    ],
)
def test_pipeline_extracts_dated_historical_current_frequency_spans(
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
            "Her seizure control is variable but acceptable; she continues to "
            "experience epileptic spasm on a daily basis, myoclonic jerks in "
            "morning clusters, and occasional generalised tonic-clonic seizures.",
            "1 per day",
            "continues to experience epileptic spasm on a daily basis",
        ),
        (
            "Although his seizures fluctuate, his parents consider him reasonably "
            "well controlled, he still has generalised tonic-clonic seizures three "
            "nights per week, drop attacks occurring in batches.",
            "3 per week",
            "still has generalised tonic-clonic seizures three nights per week",
        ),
        (
            "Clinic Date: 23 April 2014. Seizure burden has been substantially "
            "reduced following dose adjustment, with only six focal "
            "impaired-awareness seizures reported so far this year.",
            "6 per 4 month",
            "six focal impaired-awareness seizures reported so far this year",
        ),
        (
            "Clinic Date: 24 February 2016. Following introduction of lamotrigine, "
            "there has been a clear improvement in control, with just five "
            "generalised tonic-clonic seizures documented this year to date.",
            "5 per 2 month",
            "five generalised tonic-clonic seizures documented this year to date",
        ),
        (
            "Clinic Date: 24 January 2015. His mother notes an overall improvement "
            "compared with previous years, with four tonic seizures documented in "
            "2015 so far.",
            "4 per month",
            "four tonic seizures documented in 2015 so far",
        ),
        (
            "Clinic Date: 20 May 2024. The family feel seizure frequency has "
            "decreased markedly since starting medication, with only five seizures "
            "so far this year.",
            "5 per 5 month",
            "five seizures so far this year",
        ),
    ],
)
def test_pipeline_extracts_current_daily_and_year_to_date_frequency_counts(
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
            "Clinic Date: 02 October 2025. After commencing Clobazam 10 mg nocte, "
            "she had a five month remission, then sustained a drop attack 3 Mondays "
            "ago, preceded by myoclonic jerks.",
            "2 per 5 month",
            (
                "five month remission, then sustained a drop attack 3 Mondays ago, "
                "preceded by myoclonic jerks"
            ),
        ),
        (
            "Clinic Date: 03 March 2023. On 31 January, following medication, the "
            "absences became less frequent. The last such episode occurred on 06 "
            "February and she has been stable since.",
            "1 per month",
            "last such episode occurred on 06 February",
        ),
        (
            "Clinic Date: 4 February 2021. In Nov he had 3 seizures during sleep "
            "and 1 while awake. In Jan he had five in sleep and one while awake.",
            "10 per 3 month",
            (
                "In Nov he had 3 seizures during sleep and 1 while awake. In Jan "
                "he had five in sleep and one while awake"
            ),
        ),
    ],
)
def test_pipeline_extracts_remission_date_and_monthly_summary_frequency_counts(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
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
            "Cluster burden increased since 07/Dec/2023; now weekly, five per cluster.",
            "1 cluster per week, 5 per cluster",
            "weekly, five per cluster",
        ),
        (
            "Since his last review, he reports brief episodes after work with clusters on "
            "several mornings each week, sometimes repeating two or three times within the "
            "same morning.",
            "multiple cluster per week, 2 to 3 per cluster",
            "on several mornings each week",
        ),
        (
            "Over the past six weeks, he has brief nocturnal bunching on 3-4 nights "
            "per week, with several brief episodes grouped together during the night.",
            "3 to 4 cluster per week, multiple per cluster",
            "on 3-4 nights per week",
        ),
        (
            "He has been having clusters on several evenings per fortnight, and on "
            "average each cluster involves roughly five brief spells.",
            "multiple cluster per 2 week, 5 per cluster",
            "on several evenings per fortnight",
        ),
        (
            "Monthly clusters, typically 6 to 7 seizures over 24 h.",
            "1 cluster per month, 6 to 7 per cluster",
            "Monthly clusters, typically 6 to 7 seizures over 24 h",
        ),
        (
            "New nocturnal clustering with early-morning spillover; two nocturnal "
            "clusters this month; each ~four - five events.",
            "2 cluster per month, 4 to 5 per cluster",
            "two nocturnal clusters this month; each ~four - five events",
        ),
        (
            "There have been three nocturnal clusters this month; each ~4 - 5 events.",
            "3 cluster per month, 4 to 5 per cluster",
            "three nocturnal clusters this month; each ~4 - 5 events",
        ),
        (
            "She reports 1 Travel-related clusters this month; ~4 - 6 events per episode.",
            "1 cluster per month, 4 to 6 per cluster",
            "1 Travel-related clusters this month; ~4 - 6 events per episode",
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
