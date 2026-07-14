"""Invariant-focused tests for gan2026 pipeline v1 seizure free temporal."""

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
        (
            "Clinic Date: 28 December 2021. She reports excellent stability with a "
            "seizure-free interval since 25/06/2021.",
            "seizure free for 6 month",
            "seizure-free interval since 25/06/2021",
        ),
        (
            "The diary shows no recorded events or auras since May. They have maintained "
            "an absence of events for over four months.",
            "seizure free for 4 month",
            "absence of events for over four months",
        ),
        (
            "Since our last appointment, she has not experienced any seizures.",
            "seizure free for multiple year",
            "has not experienced any seizures",
        ),
        (
            "Present Seizure Frequency: No recurrence.",
            "seizure free for multiple year",
            "No recurrence",
        ),
        (
            "Since his last review, he reports excellent stability and seizure freedom continues.",
            "seizure free for multiple year",
            "seizure freedom continues",
        ),
        (
            "The family report that there have been No clinical seizures observed since referral.",
            "seizure free for multiple year",
            "No clinical seizures observed since",
        ),
        (
            "Seizures remain settled without recent breakthrough events, "
            "indicating ongoing control.",
            "seizure free for multiple year",
            "Seizures remain settled without recent breakthrough events",
        ),
        (
            "She confirms complete control of seizures since her last review.",
            "seizure free for multiple year",
            "complete control of seizures",
        ),
        (
            "There has been no occurrence of events suggestive of seizures since his last review "
            "twelve months ago.",
            "seizure free for 12 month",
            (
                "no occurrence of events suggestive of seizures since his last review "
                "twelve months ago"
            ),
        ),
        (
            "He described remaining free of his usual attacks over this interval.",
            "seizure free for multiple year",
            "free of his usual attacks over this interval",
        ),
        (
            "The patient reports no auras, warnings, or witnessed events for an extended period.",
            "seizure free for multiple year",
            "no auras, warnings, or witnessed events for an extended period",
        ),
        (
            "Since April, he has not described any further events suggestive of seizures.",
            "seizure free for multiple year",
            "has not described any further events suggestive of seizures",
        ),
        (
            "Recent spells are dissociative. She last had a clearly epileptic focal event "
            "approximately six months ago.",
            "seizure free for 6 month",
            "last had a clearly epileptic focal event approximately six months ago",
        ),
        (
            "Seizures: Patient reports no events, warnings, or auras for over 18 months. "
            "The note header says daily seizures.",
            "seizure free for 18 month",
            "no events, warnings, or auras for over 18 months",
        ),
        (
            "There have been effectively no spell-like events suggestive of seizures "
            "over the past six months. For context, his first seizure occurred in 2014.",
            "seizure free for 6 month",
            "no spell-like events suggestive of seizures over the past six months",
        ),
        (
            'She describes "No events suggestive of seizures" over this interval, '
            "although sleep is disrupted on two to three nights per week.",
            "seizure free for multiple year",
            "No events suggestive of seizures",
        ),
        (
            "The patient reports no recent events suggestive of seizures, "
            "with the last confirmed episode occurring over two years ago.",
            "seizure free for multiple year",
            "no recent events suggestive of seizures",
        ),
        (
            "Prior to improvement, she described weekly clusters, usually 6 events. "
            "After surgery she has had Sustained postoperative seizure freedom.",
            "seizure free for multiple year",
            "Sustained postoperative seizure freedom",
        ),
        (
            "He performs light exercise three times per week. His seizure diary shows "
            "no recorded events since June last year.",
            "seizure free for multiple year",
            "no recorded events since",
        ),
        (
            "Present Seizure Frequency: Seizure-free interval extends to eleven months.",
            "seizure free for 11 month",
            "Seizure-free interval extends to eleven months",
        ),
        (
            "The smartwatch log was reviewed. Interval history negative for seizures.",
            "seizure free for multiple year",
            "Interval history negative for seizures",
        ),
        (
            "She reports durable seizure control over the past several months.",
            "seizure free for multiple year",
            "durable seizure control",
        ),
        (
            "Clinic Date: 23 December 2021. They report Drug-free remission since 20-Jun-2021.",
            "seizure free for 6 month",
            "Drug-free remission since 20-Jun-2021",
        ),
        (
            "Clinic Date: 22 November 2017. They volunteered a clear timepoint: "
            "No focal clonic since 19-Mar-2017.",
            "seizure free for 8 month",
            "No focal clonic since 19-Mar-2017",
        ),
        (
            "The device dashboard indicates a recorded seizure rate at zero over the "
            "last six months.",
            "seizure free for 6 month",
            "recorded seizure rate at zero over the last six months",
        ),
        (
            "Entries confirm Seizure cessation following initiation of last ASM.",
            "seizure free for multiple year",
            "Seizure cessation following initiation of last ASM",
        ),
        (
            "Clinic Date: 02 October 2025. Patient reports that the prior cluster "
            "pattern resolved since 11 Aug 2023.",
            "seizure free for 25 month",
            "prior cluster pattern resolved since 11 Aug 2023",
        ),
        (
            "Clinic Date: 02 October 2025. Seizure control: Sustained remission since 29-May-2023.",
            "seizure free for 28 month",
            "Sustained remission since 29-May-2023",
        ),
        (
            "There have been no witnessed or reported seizures since the last review.",
            "seizure free for multiple year",
            "no witnessed or reported seizures since",
        ),
        (
            "The diary shows no episodes brought to attention by carers or bystanders, "
            "nor any events he has recognised as seizures, since early summer.",
            "seizure free for multiple year",
            (
                "no episodes brought to attention by carers or bystanders, nor any "
                "events he has recognised as seizures"
            ),
        ),
        (
            "Present Seizure Frequency: She has now been seizure free for one and a half years.",
            "seizure free for 1.5 year",
            "seizure free for one and a half years",
        ),
        (
            "He previously had daily absences, but has remained seizure free for a "
            "prolonged period, not experiencing any seizures in one and a half years.",
            "seizure free for 1.5 year",
            "not experiencing any seizures in one and a half years",
        ),
        (
            "He previously had convulsive events 2 times per year, but is currently "
            "in long-term remission, having been seizure free for years.",
            "seizure free for multiple year",
            "currently in long-term remission, having been seizure free for years",
        ),
        (
            "He and his family feel he is in a steady run without clear seizures at present.",
            "seizure free for multiple year",
            "steady run without clear seizures at present",
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


@pytest.mark.parametrize(
    ("note_text", "expected_label", "expected_evidence"),
    [
        (
            "Clinic Date: 02 October 2025. She had no seizures for nearly a year "
            "following initiation of Valproate, then developed myoclonic jerks "
            "leading to a tonic seizure two Saturdays ago.",
            "1 per year",
            (
                "no seizures for nearly a year following initiation of Valproate, "
                "then developed myoclonic jerks leading to a tonic seizure two "
                "Saturdays ago"
            ),
        ),
        (
            "Clinic Date: 29 December 2021. He did not have seizures for over 6 "
            "months, but then reported two generalised tonic-clonic seizures two "
            "Fridays ago, each preceded by myoclonic jerks.",
            "4 per 6 month",
            (
                "did not have seizures for over 6 months, but then reported two "
                "generalised tonic-clonic seizures two Fridays ago, each preceded "
                "by myoclonic jerks"
            ),
        ),
    ],
)
def test_pipeline_extracts_seizure_free_interval_then_breakthrough_counts(
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
            "Clinic Date: 14 November 2017. She first experienced a seizure in May "
            "2017 while living abroad. It occurred during sleep. Her next seizure "
            "came in November 2017 the same year, once more from sleep.",
            "2 per 6 month",
            (
                "She first experienced a seizure in May 2017 while living abroad. "
                "It occurred during sleep. Her next seizure came in November 2017"
            ),
        ),
        (
            "Clinic Date: 14 November 2016. She first experienced a seizure in July "
            "2016 while living abroad. Her next 4 seizure came in November 2016 "
            "the same year, once more from sleep.",
            "5 per 4 month",
            (
                "She first experienced a seizure in July 2016 while living abroad. "
                "Her next 4 seizure came in November 2016"
            ),
        ),
        (
            "Clinic Date: 20 June 2024. His first seizure occurred in January 2024 "
            "in Ireland, at night while asleep. The second and third event was in "
            "June 2024 in Scotland, also during sleep.",
            "3 per 5 month",
            (
                "His first seizure occurred in January 2024 in Ireland, at night "
                "while asleep. The second and third event was in June 2024"
            ),
        ),
    ],
)
def test_pipeline_extracts_first_next_event_narrative_spans(
    note_text: str,
    expected_label: str,
    expected_evidence: str,
) -> None:
    result = Gan2026PipelineV1().run(_record(note_text))

    assert result.output.final_value == expected_label
    assert result.diagnostics["final_selection"]["final_kind"] == FrequencyLabelKind.FREQUENCY
    assert result.diagnostics["final_selection"]["evidence"] == expected_evidence
    assert result.diagnostics["evidence_valid"] is True
