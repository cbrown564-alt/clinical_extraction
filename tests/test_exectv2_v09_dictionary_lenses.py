"""Functional tests for the v09 single-GPT-engine dictionary lenses."""

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
    DiagnosisDictionaryLens,
    InvestigationsDictionaryLens,
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


def test_diagnosis_dictionary_lens_rewrites_drops_and_adds() -> None:
    note = (
        "Diagnosis: focal dyscognitive seizures. She also has myoclonic jerks. "
        "Previous episode of status epilepticus."
    )
    store = _store(
        note,
        [
            {
                "entity": "Diagnosis",
                "text": "focal dyscognitive seizures",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": "focal dyscognitive seizures",
            },
            {
                "entity": "Diagnosis",
                "text": "myoclonic jerks",
                "attributes": {
                    "DiagCategory": "SingleSeizure",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": "myoclonic jerks",
            },
        ],
    )
    result = DiagnosisDictionaryLens(
        lens_id="diagnosis_convention_dictionary_v09", entity="Diagnosis"
    ).reconcile(store, policy=_policy())
    texts = [f.text for f in result.findings]
    # alias rewrite applied
    assert "dyscognitive seizures" in texts
    # standalone symptom noise dropped
    assert "myoclonic jerks" not in texts
    # dev residual addition pulled in from note text
    assert "status epilepticus" in texts


def test_diagnosis_dictionary_lens_repairs_qwen_surface_conventions() -> None:
    note = (
        "Diagnosis: focal epilepsy-Probable temporal. "
        "Diagnosis: Epilepsy - unclassified, possibly generalised. "
        "Diagnosis: generalised tonic clonic seizures alone."
    )
    store = _store(
        note,
        [
            {
                "entity": "Diagnosis",
                "text": "temporal lobe",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": "4",
                    "Negation": "Affirmed",
                },
                "evidence": "Diagnosis: focal epilepsy-Probable temporal",
            },
            {
                "entity": "Diagnosis",
                "text": "unclassified epilepsy",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": "3",
                    "Negation": "Affirmed",
                },
                "evidence": "Diagnosis: Epilepsy - unclassified, possibly generalised.",
            },
            {
                "entity": "Diagnosis",
                "text": "possibly generalised epilepsy",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": "3",
                    "Negation": "Affirmed",
                },
                "evidence": "Diagnosis: Epilepsy - unclassified, possibly generalised.",
            },
            {
                "entity": "Diagnosis",
                "text": "generalised tonic clonic seizures alone",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": "Diagnosis: generalised tonic clonic seizures alone.",
            },
        ],
    )

    result = DiagnosisDictionaryLens(
        lens_id="diagnosis_convention_dictionary_v09", entity="Diagnosis"
    ).reconcile(store, policy=_policy())
    by_text = {finding.text: finding for finding in result.findings}

    assert "temporal lobe epilepsy" in by_text
    assert by_text["epilepsy"].attributes["Certainty"] == "5"
    assert by_text["generalised epilepsy"].attributes["Certainty"] == "3"
    assert by_text["generalised tonic clonic seizures"].attributes["DiagCategory"] == (
        "MultipleSeizures"
    )


def test_diagnosis_dictionary_lens_repairs_v0915_fragments_and_noise() -> None:
    note = (
        "Diagnosis: Epilepsy - focal onset. "
        "Diagnosis: Focal epilepsy ?left temporal lobe. "
        "Seizure type and frequency: focal seizures left arm movement. "
        "Diagnosis: Longstanding epilepsy, myoclonic jerks and generalised "
        "tonic clonic seizures. "
        "Comorbidities: left frontal cortical dysplasia. "
        "Diagnosis: Dissociative seizures."
    )
    store = _store(
        note,
        [
            {
                "entity": "Diagnosis",
                "text": "focal onset",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": "Diagnosis: Epilepsy - focal onset",
            },
            {
                "entity": "Diagnosis",
                "text": "left temporal lobe epilepsy",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": "Diagnosis: Focal epilepsy ?left temporal lobe",
            },
            {
                "entity": "Diagnosis",
                "text": "focal seizures left arm movement",
                "attributes": {
                    "DiagCategory": "MultipleSeizures",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": "Seizure type and frequency: focal seizures left arm movement",
            },
            {
                "entity": "Diagnosis",
                "text": "generalised tonic clonic seizures",
                "attributes": {
                    "DiagCategory": "MultipleSeizures",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": (
                    "Diagnosis: Longstanding epilepsy, myoclonic jerks and "
                    "generalised tonic clonic seizures"
                ),
            },
            {
                "entity": "Diagnosis",
                "text": "left frontal cortical dysplasia",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": "Comorbidities: left frontal cortical dysplasia",
            },
            {
                "entity": "Diagnosis",
                "text": "Dissociative seizures",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": "Diagnosis: Dissociative seizures",
            },
        ],
    )

    result = DiagnosisDictionaryLens(
        lens_id="diagnosis_convention_dictionary_v09", entity="Diagnosis"
    ).reconcile(store, policy=_policy())
    texts = [finding.text for finding in result.findings]

    assert "focal epilepsy" in texts
    assert "temporal lobe epilepsy" in texts
    assert "focal seizures" in texts
    assert "generalised" in texts
    assert "left frontal cortical dysplasia" not in texts
    assert "Dissociative seizures" not in texts


def test_diagnosis_dictionary_lens_repairs_deepseek_category_and_typo() -> None:
    note = (
        "Diagnosis: generalised tonic chronic seizures with myoclonic jerks, possible JME. "
        "Unfortunately he had a generalised tonic clonic seizure last week."
    )
    store = _store(
        note,
        [
            {
                "entity": "Diagnosis",
                "text": "generalised tonic chronic seizures",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": (
                    "Diagnosis: generalised tonic chronic seizures with myoclonic "
                    "jerks, possible JME."
                ),
            },
            {
                "entity": "Diagnosis",
                "text": "generalised tonic clonic seizure",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": "Unfortunately he had a generalised tonic clonic seizure last week.",
            },
        ],
    )

    result = DiagnosisDictionaryLens(
        lens_id="diagnosis_convention_dictionary_v09", entity="Diagnosis"
    ).reconcile(store, policy=_policy())
    by_text = {finding.text: finding for finding in result.findings}

    assert "generalised tonic clonic seizures" in by_text
    assert by_text["generalised tonic clonic seizures"].attributes["DiagCategory"] == (
        "MultipleSeizures"
    )
    assert by_text["generalised tonic clonic seizure"].attributes["DiagCategory"] == (
        "SingleSeizure"
    )


def test_diagnosis_dictionary_lens_suppresses_redundant_heading_and_residual_fragments() -> None:
    note = (
        "Diagnosis: symptomatic structural focal epilepsy. "
        "Seizure type and frequency: focal seizures with altered awareness every 3 weeks. "
        "Diagnosis: Complex partial seizures with secondary generalised tonic clonic seizures."
    )
    store = _store(
        note,
        [
            {
                "entity": "Diagnosis",
                "text": "symptomatic structural focal epilepsy",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": "Diagnosis: symptomatic structural focal epilepsy.",
            },
            {
                "entity": "Diagnosis",
                "text": "focal seizures with altered awareness",
                "attributes": {
                    "DiagCategory": "MultipleSeizures",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": "focal seizures with altered awareness every 3 weeks",
            },
            {
                "entity": "Diagnosis",
                "text": "Complex partial seizures",
                "attributes": {
                    "DiagCategory": "MultipleSeizures",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": (
                    "Diagnosis: Complex partial seizures with secondary generalised "
                    "tonic clonic seizures."
                ),
            },
            {
                "entity": "Diagnosis",
                "text": "secondary generalised tonic clonic seizures",
                "attributes": {
                    "DiagCategory": "MultipleSeizures",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": (
                    "Diagnosis: Complex partial seizures with secondary generalised "
                    "tonic clonic seizures."
                ),
            },
        ],
    )

    result = DiagnosisDictionaryLens(
        lens_id="diagnosis_convention_dictionary_v09", entity="Diagnosis"
    ).reconcile(store, policy=_policy())
    texts = [finding.text for finding in result.findings]

    assert "symptomatic structural focal epilepsy" in texts
    assert "focal seizures with altered awareness" in texts
    assert "secondary generalised tonic clonic seizures" in texts
    assert "focal epilepsy" not in texts
    assert "focal" not in texts
    assert "generalised" not in texts


def test_diagnosis_dictionary_lens_repairs_intractable_and_drops_noise() -> None:
    note = (
        "I reviewed this lady with intractable epilepsy in clinic today. "
        "Despite this she continues to get general and complex partial seizures. "
        "In the last 2 years he developed some minor seizures."
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
                "evidence": "I reviewed this lady with intractable epilepsy in clinic today.",
            },
            {
                "entity": "Diagnosis",
                "text": "general seizures",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": (
                    "Despite this she continues to get general and complex partial seizures."
                ),
            },
            {
                "entity": "Diagnosis",
                "text": "complex partial seizures",
                "attributes": {
                    "DiagCategory": "MultipleSeizures",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": (
                    "Despite this she continues to get general and complex partial seizures."
                ),
            },
            {
                "entity": "Diagnosis",
                "text": "minor seizures",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": "In the last 2 years he developed some minor seizures.",
            },
        ],
    )

    result = DiagnosisDictionaryLens(
        lens_id="diagnosis_convention_dictionary_v09", entity="Diagnosis"
    ).reconcile(store, policy=_policy())
    texts = [finding.text for finding in result.findings]

    assert "intractable epilepsy" in texts
    assert "complex partial seizures" in texts
    assert "epilepsy" not in texts
    assert "general seizures" not in texts
    assert "minor seizures" not in texts


def test_diagnosis_dictionary_lens_does_not_add_generic_epilepsy_companion_for_subtypes() -> None:
    note = "Diagnosis: juvenile myoclonic epilepsy. Impression: juvenile myoclonic epilepsy."
    store = _store(
        note,
        [
            {
                "entity": "Diagnosis",
                "text": "juvenile myoclonic epilepsy",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": "Diagnosis: juvenile myoclonic epilepsy.",
            },
            {
                "entity": "Diagnosis",
                "text": "juvenile myoclonic epilepsy",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": "Impression: juvenile myoclonic epilepsy.",
            },
        ],
    )

    result = DiagnosisDictionaryLens(
        lens_id="diagnosis_convention_dictionary_v09", entity="Diagnosis"
    ).reconcile(store, policy=_policy())
    texts = [finding.text for finding in result.findings]

    assert texts.count("juvenile myoclonic epilepsy") == 2
    assert "epilepsy" not in texts


def test_diagnosis_dictionary_lens_adds_explicit_generic_epilepsy_residuals() -> None:
    note = (
        "Diagnosis: Genetic epilepsy. "
        "Impression. I think that the most likely diagnosis is epilepsy. "
        "Problem Epilepsy. "
        "His epilepsy was well controlled until last December."
    )
    store = ClinicalFindingStore("L1", note)
    store.register_source(_source())

    result = DiagnosisDictionaryLens(
        lens_id="diagnosis_convention_dictionary_v09", entity="Diagnosis"
    ).reconcile(store, policy=_policy())
    texts = [finding.text for finding in result.findings]

    assert texts == ["epilepsy"]


def test_diagnosis_dictionary_lens_repairs_deepseek_structural_epilepsy_surface() -> None:
    note = "Diagnosis: Symptomatic structural epilepsy secondary to traumatic brain injury."
    store = _store(
        note,
        [
            {
                "entity": "Diagnosis",
                "text": "Symptomatic structural epilepsy",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": (
                    "Diagnosis: Symptomatic structural epilepsy secondary to "
                    "traumatic brain injury."
                ),
            },
        ],
    )

    result = DiagnosisDictionaryLens(
        lens_id="diagnosis_convention_dictionary_v09", entity="Diagnosis"
    ).reconcile(store, policy=_policy())
    texts = [finding.text for finding in result.findings]

    assert "symptomatic structural focal epilepsy" in texts
    assert "Symptomatic structural epilepsy" not in texts
    assert "epilepsy" not in texts


def test_dictionary_residuals_can_use_registered_source_without_seed_findings() -> None:
    note = (
        "Diagnosis: epilepsy - unclassified. "
        "Seizure type and frequency: seizures every 3 to 4 weeks. "
        "Investigations: EEG showed right sided sharp waves."
    )
    store = ClinicalFindingStore("L1", note)
    store.register_source(_source())

    diagnosis = DiagnosisDictionaryLens(
        lens_id="diagnosis_convention_dictionary_v09", entity="Diagnosis"
    ).reconcile(store, policy=_policy())
    sf = SeizureFrequencyDictionaryLens(
        lens_id="sf_convention_dictionary_v09", entity="SeizureFrequency"
    ).reconcile(store, policy=_policy())
    investigations = InvestigationsDictionaryLens(
        lens_id="investigations_convention_dictionary_v09", entity="Investigations"
    ).reconcile(store, policy=_policy())

    assert [finding.text for finding in diagnosis.findings] == ["epilepsy"]
    assert sf.findings[0].attributes["TimePeriod"] == "Week"
    assert investigations.findings[0].attributes["EEG_Results"] == "Abnormal"


def test_diagnosis_dictionary_lens_drops_family_history_epilepsy_context() -> None:
    note = "Interestingly a paternal aunt probably had absence epilepsy."
    store = _store(
        note,
        [
            {
                "entity": "Diagnosis",
                "text": "absence epilepsy",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": "4",
                    "Negation": "Affirmed",
                },
                "evidence": "Interestingly a paternal aunt probably had absence epilepsy.",
            },
        ],
    )

    result = DiagnosisDictionaryLens(
        lens_id="diagnosis_convention_dictionary_v09", entity="Diagnosis"
    ).reconcile(store, policy=_policy())

    assert result.findings == ()


def test_diagnosis_dictionary_lens_repairs_tle_and_drops_non_target_seizures() -> None:
    note = (
        "Diagnosis: Focal seizures, possible TLE. "
        "He had one febrile seizure as a toddler. "
        "She has non-epileptic psychogenic seizures."
    )
    store = _store(
        note,
        [
            {
                "entity": "Diagnosis",
                "text": "TLE",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": "3",
                    "Negation": "Affirmed",
                },
                "evidence": "Diagnosis: Focal seizures, possible TLE",
            },
            {
                "entity": "Diagnosis",
                "text": "febrile seizure",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": "febrile seizure",
            },
            {
                "entity": "Diagnosis",
                "text": "non-epileptic psychogenic seizures",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": "non-epileptic psychogenic seizures",
            },
        ],
    )

    result = DiagnosisDictionaryLens(
        lens_id="diagnosis_convention_dictionary_v09", entity="Diagnosis"
    ).reconcile(store, policy=_policy())
    by_text = {finding.text: finding for finding in result.findings}

    assert "temporal lobe epilepsy" in by_text
    assert "febrile seizure" not in by_text
    assert "non-epileptic psychogenic seizures" not in by_text
    assert result.diagnostics["dropped_dictionary_findings"] == 2


def test_diagnosis_dictionary_lens_drops_qwen_dev25_noise_surfaces() -> None:
    note = (
        "Diagnosis: Epilepsy - unclassified, possibly generalised. "
        "Mr Turko understands that convulsive seizures with loss of consciousness "
        "can rarely cause serious injury or even death. "
        "She continues to get a combination of epileptic and nonepileptic events. "
        "This was a craniotomy for her frontal lobe brain tumour."
    )
    store = _store(
        note,
        [
            {
                "entity": "Diagnosis",
                "text": "generalised epilepsy",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": "4",
                    "Negation": "Affirmed",
                },
                "evidence": "Diagnosis: Epilepsy - unclassified, possibly generalised.",
            },
            {
                "entity": "Diagnosis",
                "text": "convulsive seizures",
                "attributes": {
                    "DiagCategory": "MultipleSeizures",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": "convulsive seizures with loss of consciousness",
            },
            {
                "entity": "Diagnosis",
                "text": "nonepileptic events",
                "attributes": {
                    "DiagCategory": "MultipleSeizures",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": "nonepileptic events",
            },
            {
                "entity": "Diagnosis",
                "text": "frontal lobe brain tumour",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": "frontal lobe brain tumour",
            },
        ],
    )

    result = DiagnosisDictionaryLens(
        lens_id="diagnosis_convention_dictionary_v09", entity="Diagnosis"
    ).reconcile(store, policy=_policy())
    by_text = {finding.text: finding for finding in result.findings}

    assert by_text["generalised epilepsy"].attributes["Certainty"] == "3"
    assert "convulsive seizures" not in by_text
    assert "nonepileptic events" not in by_text
    assert "frontal lobe brain tumour" not in by_text


def test_investigations_dictionary_lens_prunes_qwen_cross_modality_defaults() -> None:
    note = (
        "Previous investigations have included an MRI brain which have shown a small "
        "focus of gliosis. An EEG in 2016 did show some focal slowing. "
        "There was a previous CT scan from 2017 showing a left hemisphere infarct. "
        "I am therefore arranging an MRI scan of the brain. "
        "I will arrange further tests including an MR brain and EEG. "
        "The events were confirmed with an EEG recording."
    )
    store = _store(
        note,
        [
            {
                "entity": "Investigations",
                "text": "MRI brain",
                "attributes": {
                    "MRI_Performed": "Yes",
                    "MRI_Results": "Abnormal",
                    "CT_Performed": "No",
                },
                "evidence": (
                    "Previous investigations have included an MRI brain which have "
                    "shown a small focus of gliosis."
                ),
            },
            {
                "entity": "Investigations",
                "text": "MRI brain",
                "attributes": {
                    "MRI_Performed": "Yes",
                    "MRI_Results": "Abnormal",
                    "CT_Performed": "No",
                },
                "evidence": (
                    "Previous investigations have included an MRI brain which have "
                    "shown a small focus of gliosis."
                ),
            },
            {
                "entity": "Investigations",
                "text": "EEG",
                "attributes": {
                    "EEG_Performed": "Yes",
                    "EEG_Results": "Abnormal",
                    "MRI_Performed": "No",
                    "CT_Performed": "No",
                },
                "evidence": "An EEG in 2016 did show some focal slowing.",
            },
            {
                "entity": "Investigations",
                "text": "previous CT scan from 2017",
                "attributes": {
                    "CT_Performed": "Yes",
                    "CT_Results": "Abnormal",
                    "EEG_Performed": "No",
                    "MRI_Performed": "No",
                },
                "evidence": (
                    "There was a previous CT scan from 2017 showing a left hemisphere infarct."
                ),
            },
            {
                "entity": "Investigations",
                "text": "MRI scan",
                "attributes": {"MRI_Performed": "No"},
                "evidence": "I am therefore arranging an MRI scan of the brain.",
            },
            {
                "entity": "Investigations",
                "text": "EEG",
                "attributes": {"EEG_Performed": "No", "EEG_Results": "Unknown"},
                "evidence": "I will arrange further tests including an MR brain and EEG.",
            },
            {
                "entity": "Investigations",
                "text": "EEG recording",
                "attributes": {"EEG_Performed": "Yes", "EEG_Results": "Abnormal"},
                "evidence": "confirmed with an EEG recording",
            },
        ],
    )

    result = InvestigationsDictionaryLens(
        lens_id="investigations_convention_dictionary_v09", entity="Investigations"
    ).reconcile(store, policy=_policy())
    by_text = {finding.text: finding for finding in result.findings}

    assert set(by_text) == {"MRI brain", "EEG", "previous CT scan from 2017"}
    assert "CT_Performed" not in by_text["MRI brain"].attributes
    assert "MRI_Performed" not in by_text["EEG"].attributes
    assert "CT_Performed" not in by_text["EEG"].attributes
    assert "EEG_Performed" not in by_text["previous CT scan from 2017"].attributes
    assert "MRI_Performed" not in by_text["previous CT scan from 2017"].attributes
    assert result.diagnostics["normalized_dictionary_findings"] == 3
    assert result.diagnostics["dropped_dictionary_findings"] == 4


def test_investigations_dictionary_lens_prunes_positive_cross_modality_attributes() -> None:
    note = (
        "His recent CT head and MRI brain have been normal. "
        "He had an MRI scan around 5 years ago which was normal."
    )
    store = _store(
        note,
        [
            {
                "entity": "Investigations",
                "text": "CT head",
                "attributes": {
                    "CT_Performed": "Yes",
                    "CT_Results": "Normal",
                    "MRI_Performed": "Yes",
                    "MRI_Results": "Normal",
                },
                "evidence": "His recent CT head and MRI brain have been normal.",
            },
            {
                "entity": "Investigations",
                "text": "MRI scan",
                "attributes": {
                    "EEG_Performed": "Yes",
                    "EEG_Results": "Unknown",
                    "MRI_Performed": "Yes",
                    "MRI_Results": "Normal",
                },
                "evidence": "He had an MRI scan around 5 years ago which was normal.",
            },
        ],
    )

    result = InvestigationsDictionaryLens(
        lens_id="investigations_convention_dictionary_v09", entity="Investigations"
    ).reconcile(store, policy=_policy())
    by_text = {finding.text: finding for finding in result.findings}

    assert by_text["CT head"].attributes == {
        "CT_Performed": "Yes",
        "CT_Results": "Normal",
    }
    assert by_text["MRI scan"].attributes == {
        "MRI_Performed": "Yes",
        "MRI_Results": "Normal",
    }


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


def test_prescription_dictionary_lens_normalizes_atomic_dose_value() -> None:
    note = "Current treatment is Phenytoin 75mg tds."
    store = _store(
        note,
        [
            {
                "entity": "Prescription",
                "text": "Phenytoin 75mg tds",
                "attributes": {
                    "DrugName": "phenytoin",
                    "DrugDose": "75mg",
                    "DoseUnit": "mg",
                    "Frequency": "3",
                },
                "evidence": "Phenytoin 75mg tds",
            }
        ],
    )
    result = PrescriptionDictionaryLens(
        lens_id="prescription_dictionary_v09", entity="Prescription"
    ).reconcile(store, policy=_policy())
    assert result.findings[0].attributes["DrugDose"] == "75"


def test_prescription_dictionary_lens_fills_missing_frequency_from_selected_text() -> None:
    note = "Medication: Keppra 1000 milligrams twice a day."
    store = _store(
        note,
        [
            {
                "entity": "Prescription",
                "text": "Keppra 1000 milligrams twice a day",
                "attributes": {
                    "DrugName": "keppra",
                    "DrugDose": "1000",
                    "DoseUnit": "mg",
                },
                "evidence": "Keppra 1000 milligrams twice a day",
            }
        ],
    )
    result = PrescriptionDictionaryLens(
        lens_id="prescription_dictionary_v09", entity="Prescription"
    ).reconcile(store, policy=_policy())

    assert result.findings[0].attributes["Frequency"] == "2"


def test_prescription_dictionary_lens_splits_explicit_uneven_daily_regimen() -> None:
    note = "Current antiepileptic medication: levetiracetam 750mg mane, 500 mg nocte."
    store = _store(
        note,
        [
            {
                "entity": "Prescription",
                "text": "levetiracetam 750mg mane, 500 mg nocte",
                "attributes": {
                    "DrugName": "levetiracetam",
                    "DrugDose": "750mg mane, 500 mg nocte",
                    "DoseUnit": "mg",
                    "Frequency": "2",
                },
                "evidence": "levetiracetam 750mg mane, 500 mg nocte",
            }
        ],
    )
    result = PrescriptionDictionaryLens(
        lens_id="prescription_dictionary_v09", entity="Prescription"
    ).reconcile(store, policy=_policy())
    doses = [finding.attributes["DrugDose"] for finding in result.findings]
    freqs = [finding.attributes["Frequency"] for finding in result.findings]
    assert doses == ["750", "500"]
    assert freqs == ["1", "1"]
    assert result.diagnostics["split_regimen_dictionary_findings"] == 1


def test_prescription_dictionary_lens_drops_plan_and_splits_slash_regimen() -> None:
    note = (
        "Current anti epileptic medications: Carbamazepine 400mg/400 mg/200mg. "
        "Please start lamotrigine 25mg once a day. "
        "Medication Epilpim chrono (Sodium valproate) 400mg twice a day."
    )
    store = _store(
        note,
        [
            {
                "entity": "Prescription",
                "text": "Carbamazepine 400mg/400 mg/200mg",
                "attributes": {
                    "DrugName": "carbamazepine",
                    "DrugDose": "400mg/400 mg/200mg",
                    "DoseUnit": "mg",
                    "Frequency": "3",
                },
                "evidence": "Carbamazepine 400mg/400 mg/200mg",
            },
            {
                "entity": "Prescription",
                "text": "lamotrigine 25mg once a day",
                "attributes": {
                    "DrugName": "lamotrigine",
                    "DrugDose": "25",
                    "DoseUnit": "mg",
                    "Frequency": "1",
                },
                "evidence": "Please start lamotrigine 25mg once a day",
            },
            {
                "entity": "Prescription",
                "text": "Epilpim chrono (Sodium valproate) 400mg twice a day",
                "attributes": {
                    "DrugName": "epilpim chrono (sodium valproate)",
                    "DrugDose": "400",
                    "DoseUnit": "mg",
                    "Frequency": "2",
                },
                "evidence": "Epilpim chrono (Sodium valproate) 400mg twice a day",
            },
        ],
    )

    result = PrescriptionDictionaryLens(
        lens_id="prescription_dictionary_v09", entity="Prescription"
    ).reconcile(store, policy=_policy())
    doses = [finding.attributes["DrugDose"] for finding in result.findings]
    names = [finding.attributes["DrugName"] for finding in result.findings]

    assert doses == ["400", "400", "200", "400"]
    assert "lamotrigine" not in names
    assert names[-1] == "sodium-valproate"
    assert result.diagnostics["split_regimen_dictionary_findings"] == 1
    assert result.diagnostics["dropped_dictionary_findings"] == 1


def test_prescription_dictionary_lens_does_not_split_shared_slash_evidence() -> None:
    note = (
        "Current anti epileptic medications:\n"
        "Carbamazepine 400mg/400 mg/200mg\n"
        "Zonisamide 50 mg twice a day\n"
        "Clobazam 10 mg BD\n"
        "Medication: Topiramate 60mg am, 75mg pm (5mg/kg/day)"
    )
    store = _store(
        note,
        [
            {
                "entity": "Prescription",
                "text": "Zonisamide 50 mg twice a day",
                "attributes": {
                    "DrugName": "Zonisamide",
                    "DrugDose": "50",
                    "DoseUnit": "mg",
                    "Frequency": "2",
                },
                "evidence": (
                    "Current anti epileptic medications:\n"
                    "Carbamazepine 400mg/400 mg/200mg\n"
                    "Zonisamide 50 mg twice a day\n"
                    "Clobazam 10 mg BD"
                ),
            },
            {
                "entity": "Prescription",
                "text": "Topiramate 60mg am",
                "attributes": {
                    "DrugName": "Topiramate",
                    "DrugDose": "60",
                    "DoseUnit": "mg",
                    "Frequency": "1",
                },
                "evidence": "Medication: Topiramate 60mg am, 75mg pm (5mg/kg/day)",
            },
        ],
    )

    result = PrescriptionDictionaryLens(
        lens_id="prescription_dictionary_v09", entity="Prescription"
    ).reconcile(store, policy=_policy())
    rendered = [
        (
            finding.attributes["DrugName"],
            finding.attributes["DrugDose"],
            finding.attributes["Frequency"],
        )
        for finding in result.findings
    ]

    assert ("carbamazepine", "400", "1") not in rendered
    assert ("carbamazepine", "200", "1") not in rendered
    assert ("zonisamide", "50", "2") in rendered
    assert ("clobazam", "10", "2") not in rendered
    assert ("topiramate", "60", "1") in rendered
    assert ("topiramate", "75", "1") in rendered
    assert result.diagnostics["split_regimen_dictionary_findings"] == 0


def test_prescription_dictionary_lens_repairs_rescue_and_drops_future_schedule() -> None:
    note = (
        "Rescue medication: Clobazam 10-20mg bd for seizure clusters. "
        "Buccal midazolam. "
        "He should be started on Carbamazepine 200md bd. "
        "Plan: Week 1&2: Lamotrigine 125mg AM, 150mg PM."
    )
    store = _store(
        note,
        [
            {
                "entity": "Prescription",
                "text": "Clobazam 10-20mg bd for seizure clusters",
                "attributes": {
                    "DrugName": "clobazam",
                    "DrugDose": "10-20",
                    "DoseUnit": "mg",
                    "Frequency": "2",
                },
                "evidence": "Clobazam 10-20mg bd for seizure clusters",
            },
            {
                "entity": "Prescription",
                "text": "Buccal midazolam",
                "attributes": {"DrugName": "buccal midazolam", "Frequency": "As_Required"},
                "evidence": "Buccal midazolam",
            },
            {
                "entity": "Prescription",
                "text": "Carbamazepine 200md bd",
                "attributes": {
                    "DrugName": "carbamazepine",
                    "DrugDose": "200",
                    "DoseUnit": "mg",
                    "Frequency": "2",
                },
                "evidence": "He should be started on Carbamazepine 200md bd.",
            },
            {
                "entity": "Prescription",
                "text": "Lamotrigine 125mg AM",
                "attributes": {
                    "DrugName": "lamotrigine",
                    "DrugDose": "125",
                    "DoseUnit": "mg",
                    "Frequency": "1",
                },
                "evidence": "Plan: Week 1&2: Lamotrigine 125mg AM, 150mg PM",
            },
        ],
    )

    result = PrescriptionDictionaryLens(
        lens_id="prescription_dictionary_v09", entity="Prescription"
    ).reconcile(store, policy=_policy())
    by_text = {finding.text: finding for finding in result.findings}

    assert (
        by_text["Clobazam 10-20mg bd for seizure clusters"].attributes["Frequency"] == "As_Required"
    )
    assert by_text["Buccal midazolam"].attributes["DrugName"] == "midazolam"
    assert "Carbamazepine 200md bd" not in by_text
    assert "Lamotrigine 125mg AM" not in by_text
    assert result.diagnostics["dropped_dictionary_findings"] == 2


def test_prescription_dictionary_lens_adds_current_regimen_residuals() -> None:
    note = (
        "Current medication: Clobazam 10mg on Sodium Valproate 200 mg twice a day "
        "(to be increased to 300 mg BD in steps). "
        "Medication: Topiramate 60mg am, 75mg pm. "
        "He is taking levetiracetam 1500mg bd as well as lamotrigine 200mg bd. "
        "I would also suggest changing the levetiracetam to brivetiracetam 100mg bd."
    )
    store = ClinicalFindingStore("L1", note)
    store.register_source(_source())

    result = PrescriptionDictionaryLens(
        lens_id="prescription_dictionary_v09", entity="Prescription"
    ).reconcile(store, policy=_policy())
    keys = {
        (
            finding.attributes.get("DrugName"),
            finding.attributes.get("DrugDose"),
            finding.attributes.get("DoseUnit"),
            finding.attributes.get("Frequency"),
        )
        for finding in result.findings
    }

    assert ("clobazam", "10", "mg", "1") in keys
    assert ("sodium-valproate", "200", "mg", "2") in keys
    assert ("topiramate", "60", "mg", "1") in keys
    assert ("topiramate", "75", "mg", "1") in keys
    assert ("levetiracetam", "1500", "mg", "2") in keys
    assert ("lamotrigine", "200", "mg", "2") in keys
    assert ("brivaracetam", "100", "mg", "2") not in keys


def test_investigations_dictionary_lens_adds_completed_result_residuals() -> None:
    note = (
        "Medication: lamotrigine. "
        "Investigations: MRI 2019 normal. "
        "Previous EEGs: left temporal lobe discharges. "
        "A CT head was normal."
    )
    store = _store(
        note,
        [
            {
                "entity": "Prescription",
                "text": "lamotrigine",
                "attributes": {"DrugName": "lamotrigine"},
                "evidence": "lamotrigine",
            }
        ],
    )

    result = InvestigationsDictionaryLens(
        lens_id="investigations_convention_dictionary_v09", entity="Investigations"
    ).reconcile(store, policy=_policy())
    by_text = {finding.text: finding for finding in result.findings}

    assert by_text["MRI"].attributes["MRI_Results"] == "Normal"
    assert by_text["EEG"].attributes["EEG_Results"] == "Abnormal"
    assert by_text["CT"].attributes["CT_Results"] == "Normal"
    assert result.diagnostics["added_dictionary_findings"] == 3


def test_investigations_dictionary_lens_adds_v0919_edge_residuals() -> None:
    note = (
        "There was a previous CT scan from 2017 showing a left hemisphere infarct. "
        "She had a CT head in 2013 and an ECG in clinic today shows a sinus "
        "rhythm of 72 bpm, a normal QT interval. "
        "A&E notes say a CT head did not identify any acute pathology. "
        "An MRI last year did have some movement artefact, but there was a "
        "suggestion of a small right hippocampus. "
        "There are some focal epileptiform changes on his EEG from 2010. "
        "Investigations: EEG 2016 normal EEG 2015 frequent generalised spike and wave."
    )
    store = ClinicalFindingStore("L1", note)
    store.register_source(_source())

    result = InvestigationsDictionaryLens(
        lens_id="investigations_convention_dictionary_v09", entity="Investigations"
    ).reconcile(store, policy=_policy())
    keys = {
        (
            finding.attributes.get("EEG_Results"),
            finding.attributes.get("MRI_Results"),
            finding.attributes.get("CT_Results"),
        )
        for finding in result.findings
    }

    assert (None, None, "Abnormal") in keys
    assert (None, None, "Unknown") in keys
    assert (None, None, "Normal") in keys
    assert (None, "Abnormal", None) in keys
    assert ("Abnormal", None, None) in keys
    assert ("Normal", None, None) in keys


def test_investigations_dictionary_lens_does_not_cross_sentences_for_eeg_normal() -> None:
    note = (
        "She has a primary generalised epilepsy with frequent EEG abnormalities. "
        "Previous MRI scans in June 2008 and November 2010 have been normal."
    )
    store = ClinicalFindingStore("L1", note)
    store.register_source(_source())

    result = InvestigationsDictionaryLens(
        lens_id="investigations_convention_dictionary_v09", entity="Investigations"
    ).reconcile(store, policy=_policy())
    eeg_results = {
        finding.attributes.get("EEG_Results")
        for finding in result.findings
        if finding.attributes.get("EEG_Performed") == "Yes"
    }

    assert eeg_results == {"Abnormal"}
