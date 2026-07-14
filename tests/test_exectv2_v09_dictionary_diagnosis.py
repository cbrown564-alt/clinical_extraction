"""Invariant-focused tests for exectv2 v09 dictionary diagnosis."""

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


def _policy(*, diagnosis_resolution_candidate: bool = False) -> LensPolicy:
    return LensPolicy(
        producer_id=_PRODUCER,
        source_lane="single_gpt_structured_v09",
        ownership_label="single_gpt",
        portability="benchmark_format",
        diagnosis_resolution_candidate=diagnosis_resolution_candidate,
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


def test_diagnosis_dictionary_lens_recovers_patient_absence_seizures() -> None:
    note = (
        "Medical diagnosis: Generalised epilepsy with absences and GTCS. "
        "Rachel started having absence seizures at around the age of 8."
    )
    store = _store(
        note,
        [
            {
                "entity": "Diagnosis",
                "text": "generalised epilepsy",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": "Generalised epilepsy",
            }
        ],
    )

    result = DiagnosisDictionaryLens(
        lens_id="diagnosis_convention_dictionary_v09", entity="Diagnosis"
    ).reconcile(store, policy=_policy(diagnosis_resolution_candidate=True))

    absence = next(finding for finding in result.findings if finding.text == "absence seizures")
    addition = next(
        event
        for event in absence.provenance
        if event.action == "added_diagnosis_residual_from_dictionary"
    )
    assert addition.portability == "clinical_epilepsy"
    assert addition.detail["rule_category"] == "clinical_epilepsy"


def test_diagnosis_dictionary_lens_keeps_required_symptomatic_fragment() -> None:
    note = (
        "Diagnosis: Symptomatic epilepsy with generalised tonic clonic seizures "
        "with right temporal meningioma."
    )
    store = _store(
        note,
        [
            {
                "entity": "Diagnosis",
                "text": "symptomatic epilepsy",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": note,
            }
        ],
    )

    result = DiagnosisDictionaryLens(
        lens_id="diagnosis_convention_dictionary_v09", entity="Diagnosis"
    ).reconcile(store, policy=_policy(diagnosis_resolution_candidate=True))

    assert "symptomatic" in [finding.text for finding in result.findings]


def test_diagnosis_dictionary_lens_avoids_generic_generalised_subtype_duplicate() -> None:
    note = "Diagnosis: genetic generalised epilepsy."
    store = _store(
        note,
        [
            {
                "entity": "Diagnosis",
                "text": "genetic generalised epilepsy",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": "genetic generalised epilepsy",
            }
        ],
    )

    result = DiagnosisDictionaryLens(
        lens_id="diagnosis_convention_dictionary_v09", entity="Diagnosis"
    ).reconcile(store, policy=_policy(diagnosis_resolution_candidate=True))

    texts = [finding.text for finding in result.findings]
    assert "genetic generalised epilepsy" in texts
    assert "generalised epilepsy" not in texts
