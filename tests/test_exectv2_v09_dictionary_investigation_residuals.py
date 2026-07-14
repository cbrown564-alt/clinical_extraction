"""Invariant-focused tests for exectv2 v09 dictionary investigation residuals."""

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
