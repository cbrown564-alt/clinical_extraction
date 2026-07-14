"""Invariant-focused tests for exectv2 v09 dictionary seizure frequency."""

from __future__ import annotations

from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.clinical_finding import (
    ClinicalFinding,
    FindingSource,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.finding_store import (
    ClinicalFindingStore,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.lenses import (
    LensPolicy,
    PrescriptionDictionaryLens,
    SeizureFrequencyDictionaryLens,
)

_PRODUCER = "key_entities_structured_v09"


def _source() -> FindingSource:
    return FindingSource(
        producer_id=_PRODUCER,
        artifact_path="x.jsonl",
        pipeline_family="exectv2_hybrid_key_family_event_ledger",
        model="openai/gpt-4.1-mini",
        prompt_version="exectv2_hybrid_key_family_event_ledger_v0.9",
        mode="live",
        ownership_label="single_gpt_key_family_event_ledger",
        source_lane="single_gpt_structured_v09",
    )


def _store(note_text: str, mentions: list[dict[str, Any]]) -> ClinicalFindingStore:
    store = ClinicalFindingStore("L1", note_text)
    for index, mention in enumerate(mentions):
        evidence = str(mention.get("evidence", ""))
        store.add(
            ClinicalFinding.from_mention_row(
                mention,
                finding_id=f"L1:{_PRODUCER}:{mention['entity']}:scored:{index}",
                letter_id="L1",
                entity=mention["entity"],
                source=_source(),
                diagnostics={},
                raw_surface=False,
                evidence_valid=bool(evidence) and evidence in note_text,
            )
        )
    return store


def _policy() -> LensPolicy:
    return LensPolicy(
        producer_id=_PRODUCER,
        source_lane="single_gpt_structured_v09",
        ownership_label="single_gpt",
        portability="benchmark_format",
    )


def test_sf_dictionary_lens_applies_benchmark_rewrite() -> None:
    note = "She had a cluster of 3 in March."
    store = _store(
        note,
        [
            {
                "entity": "SeizureFrequency",
                "text": "cluster of 3",
                "attributes": {"NumberOfSeizures": "1", "MonthDate": "3"},
                "evidence": "cluster of 3 in March",
            }
        ],
    )
    result = SeizureFrequencyDictionaryLens(
        lens_id="sf_convention_dictionary_v09", entity="SeizureFrequency"
    ).reconcile(store, policy=_policy())
    finding = result.findings[0]
    assert finding.text == "seizure cluster"
    assert finding.attributes["CUI"] == "C3203523"
    assert finding.attributes["CUIPhrase"] == "seizure cluster"


def test_sf_dictionary_lens_drops_v0921_contextual_overemissions() -> None:
    note = (
        "The absences were relatively infrequent at the age of 8. "
        "Up until February he was having around 3 seizures per month. "
        "focal to bilateral convulsive seizure 2019. "
        "his last one was on Christmas day 2009. "
        "He has had three episodes whilst asleep."
    )
    store = _store(
        note,
        [
            {
                "entity": "SeizureFrequency",
                "text": "absences",
                "attributes": {"CUI": "C0563606", "CUIPhrase": "absences"},
                "evidence": "The absences were relatively infrequent at the age of 8.",
            },
            {
                "entity": "SeizureFrequency",
                "text": "seizures",
                "attributes": {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": "3",
                    "TimePeriod": "Month",
                },
                "evidence": "around 3 seizures per month",
            },
            {
                "entity": "SeizureFrequency",
                "text": "focal to bilateral convulsive seizure",
                "attributes": {
                    "CUI": "C0877017",
                    "CUIPhrase": "focal to bilateral convulsive seizure",
                    "NumberOfSeizures": "1",
                },
                "evidence": "focal to bilateral convulsive seizure 2019",
            },
        ],
    )

    result = SeizureFrequencyDictionaryLens(
        lens_id="sf_convention_dictionary_v09", entity="SeizureFrequency"
    ).reconcile(store, policy=_policy())

    assert result.findings == ()


def test_sf_dictionary_lens_repairs_qwen_state_and_noise_residuals() -> None:
    note = (
        "I think that the focal seizures are completely under control on the dose. "
        "The epileptic seizures seems to be well controlled on lamotrigine. "
        "She has not had any further seizures since then. "
        "His last seizures were in his teenage years where he probably had around "
        "3 or 4 focal to bilateral convulsive seizures. "
        "She has been getting episodes around twice a week of an unusual thought. "
        "Even though he has only had one seizure he is at risk of further seizures."
    )
    store = _store(
        note,
        [
            {
                "entity": "SeizureFrequency",
                "text": "focal seizures",
                "attributes": {
                    "CUI": "C0751495",
                    "CUIPhrase": "focal seizures",
                    "FrequencyChange": "Decreased",
                },
                "evidence": (
                    "I think that the focal seizures are completely under control on the dose."
                ),
            },
            {
                "entity": "SeizureFrequency",
                "text": "epileptic seizures",
                "attributes": {"FrequencyChange": "Decreased"},
                "evidence": "The epileptic seizures seems to be well controlled on lamotrigine.",
            },
            {
                "entity": "SeizureFrequency",
                "text": "further seizures",
                "attributes": {"NumberOfSeizures": "0"},
                "evidence": "She has not had any further seizures since then.",
            },
            {
                "entity": "SeizureFrequency",
                "text": "focal to bilateral convulsive seizures",
                "attributes": {
                    "CUI": "C0877017",
                    "CUIPhrase": "focal to bilateral convulsive seizures",
                    "NumberOfSeizures": "0",
                },
                "evidence": (
                    "His last seizures were in his teenage years where he probably "
                    "had around 3 or 4 focal to bilateral convulsive seizures."
                ),
            },
            {
                "entity": "SeizureFrequency",
                "text": "episodes around twice a week",
                "attributes": {"NumberOfSeizures": "2", "TimePeriod": "Week"},
                "evidence": (
                    "She has been getting episodes around twice a week of an unusual thought."
                ),
            },
            {
                "entity": "SeizureFrequency",
                "text": "one seizure",
                "attributes": {"NumberOfSeizures": "1"},
                "evidence": (
                    "Even though he has only had one seizure he is at risk of further seizures."
                ),
            },
        ],
    )

    result = SeizureFrequencyDictionaryLens(
        lens_id="sf_convention_dictionary_v09", entity="SeizureFrequency"
    ).reconcile(store, policy=_policy())
    by_text = {finding.text: finding for finding in result.findings}

    assert by_text["focal seizures"].attributes["NumberOfSeizures"] == "0"
    assert "FrequencyChange" not in by_text["focal seizures"].attributes
    assert by_text["seizures"].attributes["CUI"] == "C0036572"
    assert "episodes around twice a week" not in by_text
    assert "one seizure" not in by_text
    assert result.diagnostics["rewritten_dictionary_findings"] == 4
    assert result.diagnostics["dropped_dictionary_findings"] == 3


def test_sf_dictionary_lens_adds_bounded_residual_frequency_patterns() -> None:
    note = (
        "Seizure type and frequency: 2 generalised tonic clonic seizures 2014, "
        "absence like seizures 2014. "
        "Seizure type and frequency: Focal seizures with altered awareness "
        "approximately 1 per fortnight. "
        "Unfortunately after the period of seizure freedom the seizures have returned. "
        "Although she did have a cluster of seizures in August, 2017 where she had "
        "6-9 seizures every week for 3 weeks."
    )
    store = _store(
        note,
        [
            {
                "entity": "SeizureFrequency",
                "text": "seizures",
                "attributes": {"NumberOfSeizures": "0"},
                "evidence": "the seizures have returned",
            }
        ],
    )

    result = SeizureFrequencyDictionaryLens(
        lens_id="sf_convention_dictionary_v09", entity="SeizureFrequency"
    ).reconcile(store, policy=_policy())
    by_text = {finding.text: finding for finding in result.findings}

    assert by_text["generalised tonic clonic seizures"].attributes["YearDate"] == "2014"
    assert by_text["absence like seizures"].attributes["NumberOfSeizures"] == "1"
    assert by_text["focal seizures with altered awareness"].attributes["TimePeriod"] == ("Week")
    assert by_text["seizure"].attributes["FrequencyChange"] == "Increased"
    assert by_text["cluster of seizures"].attributes["CUI"] == "C3203523"
    assert result.diagnostics["added_dictionary_findings"] == 5


def test_sf_dictionary_lens_adds_v0916_source_residuals() -> None:
    note = (
        "Unfortunately he forgot his dose last week and had a generalised tonic "
        "clonic seizure. "
        "More recently there has been an increase in her seizures. She is currently "
        "having seizures on a weekly basis. "
        "Focal to bilateral convulsive seizures August 2014 and September 2015. "
        "Complex partial seizures (deja-vu, automatism) 1-2 per month. "
        "Secondary generalised seizures 3-4 per year. "
        "He reported more of his typical absences since the last clinic appointment."
    )
    store = ClinicalFindingStore("L1", note)
    store.register_source(_source())

    result = SeizureFrequencyDictionaryLens(
        lens_id="sf_convention_dictionary_v09", entity="SeizureFrequency"
    ).reconcile(store, policy=_policy())

    ftb_years = {
        finding.attributes.get("YearDate")
        for finding in result.findings
        if finding.attributes.get("CUI") == "C0877017"
    }
    by_cui = {finding.attributes.get("CUI"): finding for finding in result.findings}
    typical = next(
        finding for finding in result.findings if finding.attributes.get("CUI") == "C4316903"
    )

    assert by_cui["C0494475"].attributes["PointInTime"] == "Last_Week"
    assert {"2014", "2015"} <= ftb_years
    assert by_cui["C0149958"].attributes["TimePeriod"] == "Month"
    assert by_cui["C0270838"].attributes["TimePeriod"] == "Year"
    assert typical.attributes["FrequencyChange"] == "Same"
    assert result.diagnostics["added_dictionary_findings"] >= 7


def test_sf_dictionary_lens_repairs_v0914_state_residuals() -> None:
    note = (
        "focal to bilateral seizures 2 events in total, last event 10 years ago. "
        "She has had four in the last three weeks but has had up to five weeks "
        "seizure free. "
        "On Sunday and Monday, he was having generalised tonic clonic seizures "
        "in the night. "
        "Her seizure was about 2 months ago. "
        "Last week she had around 10-15 of these seizures over 2 days. "
        "The absences continue to happen maybe every week. "
        "The seizure frequency has improved after starting levetiracetam. "
        "These happen a few times every month."
    )
    store = _store(
        note,
        [
            {
                "entity": "SeizureFrequency",
                "text": "focal to bilateral seizures",
                "attributes": {
                    "CUI": "C0877017",
                    "CUIPhrase": "focal to bilateral seizures",
                    "NumberOfSeizures": "2",
                },
                "evidence": (
                    "focal to bilateral seizures 2 events in total, last event 10 years ago"
                ),
            },
            {
                "entity": "SeizureFrequency",
                "text": "generalised tonic clonic seizures",
                "attributes": {
                    "CUI": "C0494475",
                    "CUIPhrase": "generalised tonic clonic seizures",
                    "NumberOfSeizures": "0",
                },
                "evidence": (
                    "She has had four in the last three weeks but has had up to "
                    "five weeks seizure free."
                ),
            },
            {
                "entity": "SeizureFrequency",
                "text": "generalised tonic clonic seizures",
                "attributes": {
                    "CUI": "C0494475",
                    "CUIPhrase": "generalised tonic clonic seizures",
                    "FrequencyChange": "Frequent",
                },
                "evidence": (
                    "On Sunday and Monday, he was having generalised tonic clonic "
                    "seizures in the night."
                ),
            },
            {
                "entity": "SeizureFrequency",
                "text": "seizure",
                "attributes": {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizure",
                    "NumberOfSeizures": "1",
                },
                "evidence": "Her seizure was about 2 months ago.",
            },
            {
                "entity": "SeizureFrequency",
                "text": "these seizures",
                "attributes": {
                    "LowerNumberOfSeizures": "10",
                    "UpperNumberOfSeizures": "15",
                    "NumberOfTimePeriods": "2",
                    "TimePeriod": "days",
                },
                "evidence": "Last week she had around 10-15 of these seizures over 2 days.",
            },
            {
                "entity": "SeizureFrequency",
                "text": "absence seizures",
                "attributes": {
                    "NumberOfSeizures": "1",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Week",
                },
                "evidence": "The absences continue to happen maybe every week.",
            },
            {
                "entity": "SeizureFrequency",
                "text": "seizure frequency",
                "attributes": {"FrequencyChange": "Decreased"},
                "evidence": "The seizure frequency has improved after starting levetiracetam.",
            },
            {
                "entity": "SeizureFrequency",
                "text": "mini shakes",
                "attributes": {"NumberOfSeizures": "3"},
                "evidence": "These happen a few times every month.",
            },
        ],
    )

    result = SeizureFrequencyDictionaryLens(
        lens_id="sf_convention_dictionary_v09", entity="SeizureFrequency"
    ).reconcile(store, policy=_policy())
    by_evidence = {finding.evidence: finding for finding in result.findings}

    ftb = by_evidence["focal to bilateral seizures 2 events in total, last event 10 years ago"]
    assert ftb.text == "focal to bilateral convulsive seizures"
    assert ftb.attributes["NumberOfSeizures"] == "0"
    assert (
        "NumberOfSeizures"
        not in by_evidence[
            "She has had four in the last three weeks but has had up to five weeks seizure free."
        ].attributes
    )
    assert (
        by_evidence[
            "On Sunday and Monday, he was having generalised tonic clonic seizures in the night."
        ].attributes["NumberOfSeizures"]
        == "1"
    )
    assert by_evidence["Her seizure was about 2 months ago."].attributes["NumberOfSeizures"] == "0"
    assert (
        by_evidence["Last week she had around 10-15 of these seizures over 2 days."].attributes[
            "CUI"
        ]
        == "C0036572"
    )
    assert (
        by_evidence["The absences continue to happen maybe every week."].attributes["CUI"]
        == "C0563606"
    )
    assert result.diagnostics["rewritten_dictionary_findings"] == 6
    assert result.diagnostics["dropped_dictionary_findings"] == 2


def test_sf_dictionary_lens_rewrites_generic_seizure_free_state_concept() -> None:
    note = "She has been seizure free since starting antiepileptic medication."
    store = _store(
        note,
        [
            {
                "entity": "SeizureFrequency",
                "text": "seizures",
                "attributes": {"CUI": "C0036572", "NumberOfSeizures": "0"},
                "evidence": "She has been seizure free since starting antiepileptic medication.",
            }
        ],
    )

    result = SeizureFrequencyDictionaryLens(
        lens_id="sf_convention_dictionary_v09", entity="SeizureFrequency"
    ).reconcile(store, policy=_policy())

    assert result.findings[0].text == "seizure-free"
    assert result.findings[0].attributes["CUI"] == "C1299590"


def test_sf_dictionary_lens_rewrites_typical_absences_since_last_clinic() -> None:
    note = "He has had more of his typical absences since the last clinic appointment."
    store = _store(
        note,
        [
            {
                "entity": "SeizureFrequency",
                "text": "typical absences",
                "attributes": {
                    "CUI": "C4316903",
                    "CUIPhrase": "typical absences",
                    "NumberOfSeizures": "0",
                    "PointInTime": "LastClinic",
                    "TimeSince_or_TimeOfEvent": "Since",
                },
                "evidence": "typical absences",
            }
        ],
    )

    result = SeizureFrequencyDictionaryLens(
        lens_id="sf_convention_dictionary_v09", entity="SeizureFrequency"
    ).reconcile(store, policy=_policy())

    assert result.findings[0].attributes["FrequencyChange"] == "Same"
    assert "NumberOfSeizures" not in result.findings[0].attributes


def test_sf_dictionary_lens_adds_seizure_free_source_residuals() -> None:
    note = (
        "Diagnosis: epilepsy. "
        "Richard tells me that he remains seizrue free which is good news. "
        "His seizures have stopped since reaching the current dose."
    )
    store = _store(
        note,
        [
            {
                "entity": "Diagnosis",
                "text": "epilepsy",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": "Diagnosis: epilepsy.",
            }
        ],
    )

    result = SeizureFrequencyDictionaryLens(
        lens_id="sf_convention_dictionary_v09", entity="SeizureFrequency"
    ).reconcile(store, policy=_policy())
    keys = {(finding.text, finding.attributes["CUI"]) for finding in result.findings}

    assert ("seizure-free", "C1299590") in keys
    assert ("seizures", "C0036572") in keys
    assert result.diagnostics["added_dictionary_findings"] == 2


def test_sf_dictionary_lens_drops_contextual_rate_overcalls() -> None:
    note = (
        "He is not able to drive until he has been 1 year free of seizures. "
        "Previously she has been more than eight years seizure free. "
        "She has no had 4 events in total. "
        "Sine the last appointment Mr Richards has had 4 more attacks."
    )
    store = _store(
        note,
        [
            {
                "entity": "SeizureFrequency",
                "text": "seizures",
                "attributes": {"CUI": "C0036572", "NumberOfSeizures": "0"},
                "evidence": "drive until he has been 1 year free of seizures",
            },
            {
                "entity": "SeizureFrequency",
                "text": "seizure free",
                "attributes": {"CUI": "C1299590", "NumberOfSeizures": "0"},
                "evidence": "Previously she has been more than eight years seizure free.",
            },
            {
                "entity": "SeizureFrequency",
                "text": "events",
                "attributes": {"NumberOfSeizures": "4"},
                "evidence": "She has no had 4 events in total.",
            },
            {
                "entity": "SeizureFrequency",
                "text": "attacks",
                "attributes": {"NumberOfSeizures": "4"},
                "evidence": "Sine the last appointment Mr Richards has had 4 more attacks.",
            },
        ],
    )

    result = SeizureFrequencyDictionaryLens(
        lens_id="sf_convention_dictionary_v09", entity="SeizureFrequency"
    ).reconcile(store, policy=_policy())

    assert result.findings == ()
    assert result.diagnostics["dropped_dictionary_findings"] == 4


def test_prescription_dictionary_lens_normalizes_name_and_unit() -> None:
    note = "Current treatment is lamtorigine 250 mgs bd."
    store = _store(
        note,
        [
            {
                "entity": "Prescription",
                "text": "lamtorigine 250 mgs bd",
                "attributes": {
                    "DrugName": "lamtorigine",
                    "DrugDose": "250",
                    "DoseUnit": "mgs",
                    "Frequency": "2",
                },
                "evidence": "lamtorigine 250 mgs bd",
            }
        ],
    )
    result = PrescriptionDictionaryLens(
        lens_id="prescription_dictionary_v09", entity="Prescription"
    ).reconcile(store, policy=_policy())
    attrs = dict(result.findings[0].attributes)
    assert attrs["DrugName"] == "lamotrigine"
    assert attrs["DoseUnit"] == "mg"
