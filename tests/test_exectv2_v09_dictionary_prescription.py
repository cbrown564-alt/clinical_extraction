"""Invariant-focused tests for exectv2 v09 dictionary prescription."""

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
    InvestigationsDictionaryLens,
    LensPolicy,
    PrescriptionDictionaryLens,
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
