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
                "evidence": "Diagnosis: generalised tonic chronic seizures with myoclonic jerks, possible JME.",
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
