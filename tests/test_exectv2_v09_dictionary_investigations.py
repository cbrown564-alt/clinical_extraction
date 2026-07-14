"""Invariant-focused tests for exectv2 v09 dictionary investigations."""

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
