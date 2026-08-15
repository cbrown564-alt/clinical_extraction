"""Invariant-focused tests for exectv2 llm only prompt contract."""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from tests.helpers.prompt_hygiene import FORBIDDEN_PHRASES

_NOTE = (
    "She has focal epilepsy with 2 focal seizures per month. "
    "Current treatment is lamotrigine 200 mg twice daily. "
    "MRI brain was normal; sleep-deprived EEG showed sharp waves."
)

_LETTER = ExectLetter(letter_id="TEST001", note_text=_NOTE)


def test_prompt_hygiene_and_four_family_schema() -> None:
    payload_str = structured.build_prompt_input(_LETTER)
    leaked = [phrase for phrase in FORBIDDEN_PHRASES if phrase in payload_str]
    assert leaked == []

    payload = json.loads(payload_str)
    assert payload["prompt_version"] == structured.PROMPT_VERSION
    assert set(payload["attribute_vocabulary"]) == {
        PRESCRIPTION.name,
        DIAGNOSIS.name,
        SEIZURE_FREQUENCY.name,
        INVESTIGATIONS.name,
    }
    assert "clinical_events" in payload["output_schema"]
    assert "_v0.9" in payload["prompt_version"]
    assert payload["architecture"]["name"] == "single hybrid key-family event ledger"
    assert payload["candidate_evidence_ledger"]
    assert payload["decision_procedure"]
    assert payload["event_lane_guide"]
    assert {
        "medication",
        "diagnosis",
        "seizure_frequency",
        "investigation",
    } <= set(payload["event_lane_guide"])
    assert "medication" in payload["family_guidance"]
    assert "seizure_frequency" in payload["family_guidance"]
    assert "DiagCategory" in payload["attribute_vocabulary"][DIAGNOSIS.name]
    assert "EEG_Type" in payload["attribute_vocabulary"][INVESTIGATIONS.name]
    clinical_rules = " ".join(payload["clinical_rules"])
    assert "First classify each candidate_evidence_ledger item" in clinical_rules
    assert "Candidate ledger rows are not predictions" in clinical_rules
    assert "one short final-justification sentence" in clinical_rules
    assert "Medication decision lane" in clinical_rules
    assert "Investigation decision lane" in clinical_rules
    assert "LowerNumberOfSeizures" in clinical_rules
    assert "LowerNumberOfTimePeriods='3'" in clinical_rules
    assert "FrequencyChange only" in clinical_rules
    assert "PointInTime='LastClinic'" in clinical_rules
    assert "Every Diagnosis mention must include Certainty and Negation" in clinical_rules
    assert "Certainty='4' for probable or likely diagnoses" in clinical_rules
    assert "render only the core clinical concept" in clinical_rules
    assert "Temporal lobe epilepsy" in clinical_rules
    assert "Do not render bare modifiers" in clinical_rules
    assert "focal epilepsy-Probable temporal" in clinical_rules
    assert "Epilepsy - unclassified, possibly generalised" in clinical_rules
    assert "use the exact abbreviation as mention" in clinical_rules
    assert "render both as separate Diagnosis mentions" in clinical_rules
    assert "plural named seizure types" in clinical_rules
    assert "Do not render vague symptoms" in clinical_rules
    assert "negated resemblance statements" in clinical_rules
    assert "childhood febrile seizures" in clinical_rules
    assert "A problem-list or Diagnosis header is not enough" in clinical_rules
    assert "myoclonic jerks" in clinical_rules
    assert "Never write 'tonic chronic'" in clinical_rules
    assert "possible JME" in clinical_rules
    assert "complex partial seizures" in clinical_rules
    assert "symptomatic structural focal epilepsy" in clinical_rules
    assert "intractable epilepsy" in clinical_rules
    assert "general and complex partial seizures" in clinical_rules
    assert "Keep plural seizure-type wording plural" in clinical_rules
    assert "generic seizure phrase" in clinical_rules
    assert "Never emit a SeizureFrequency mention with empty attributes" in clinical_rules
    assert "'several'='3'" in clinical_rules
    assert "Do not replace a heading frequency with a later vague narrative estimate" in (
        clinical_rules
    )
    assert "NumberOfSeizures='1', YearDate='2014'" in clinical_rules
    assert "last seizure" in clinical_rules
    assert "active current-rate statement" in clinical_rules
    assert "last seizure coincided" in clinical_rules
    assert "remains seizure free and is now driving" in clinical_rules
    assert "with altered awareness" in clinical_rules
    assert "Seizure type and frequency headings are high-value evidence" in clinical_rules
    assert "seizures have returned" in clinical_rules
    assert "reject generic spell anchors" in clinical_rules
    assert "risk of further seizures" in clinical_rules
    assert "episodes around twice a week of an unusual thought" in clinical_rules
    assert "generic events, blackouts" in clinical_rules
    assert "Medication current-list split dosing" in clinical_rules
    assert "Medication plan boundary" in clinical_rules
    assert "Medication frequency completion" in clinical_rules
    assert "future planned, requested, repeat, or follow-up investigations" in clinical_rules
    assert "ECG is not an ExECTv2 target investigation" in clinical_rules
    assert "EEG did show temporal slowing" in clinical_rules
    assert "Do not default a plain EEG to Standard" in clinical_rules
    assert "Every rendered mention object must include both entity and text" in clinical_rules
    med_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"] == "Current treatment is lamotrigine 200 mg twice daily."
    )
    assert med_example["correct_event"]["mentions"][0]["text"] == ("lamotrigine 200 mg twice daily")
    split_med_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"] == "Current medication: Epilim 300 mg mane and 600 mg nocte."
    )
    assert [
        m["attributes"]["Frequency"] for m in split_med_example["correct_event"]["mentions"]
    ] == ["1", "1"]
    planned_med_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"].startswith("Plan: start levetiracetam")
    )
    assert planned_med_example["correct_event"]["mentions"] == []
    keppra_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"] == "Medication: Keppra 1000 milligrams twice a day."
    )
    assert keppra_example["correct_event"]["mentions"][0]["attributes"]["Frequency"] == "2"
    interval_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"] == "She has seizures every 3 to 4 weeks."
    )
    assert (
        interval_example["correct_event"]["mentions"][0]["attributes"]["LowerNumberOfTimePeriods"]
        == "3"
    )
    first_sf_example = payload["worked_examples"][0]
    assert first_sf_example["correct_event"]["mentions"][2]["attributes"] == {
        "NumberOfSeizures": "2",
        "NumberOfTimePeriods": "1",
        "TimePeriod": "Month",
    }
    dated_type_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"].startswith(
            "Seizure type and frequency: 2 generalised tonic clonic"
        )
    )
    assert [mention["text"] for mention in dated_type_example["correct_event"]["mentions"]] == [
        "generalised tonic clonic seizures",
        "absence like seizures",
    ]
    assert (
        dated_type_example["correct_event"]["mentions"][1]["attributes"]["NumberOfSeizures"] == "1"
    )
    returned_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"].startswith("Unfortunately after a period of seizure freedom")
    )
    assert returned_example["correct_event"]["mentions"][0]["attributes"] == {
        "FrequencyChange": "Increased"
    }
    altered_awareness_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"].startswith("Focal seizures with altered awareness")
    )
    assert altered_awareness_example["correct_event"]["mentions"][0]["text"] == (
        "Focal seizures with altered awareness"
    )
    probable_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"] == "Diagnosis: probable temporal lobe epilepsy."
    )
    assert probable_example["correct_event"]["mentions"][0]["attributes"]["Certainty"] == "4"
    jme_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"] == "Diagnosis: possible JME."
    )
    assert jme_example["correct_event"]["mentions"][0]["text"] == "JME"
    assert jme_example["correct_event"]["mentions"][0]["attributes"]["Certainty"] == "3"
    focal_temporal_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"] == "Diagnosis: focal epilepsy-Probable temporal"
    )
    assert [m["text"] for m in focal_temporal_example["correct_event"]["mentions"]] == [
        "focal epilepsy",
        "temporal lobe epilepsy",
    ]
    assert [
        m["attributes"]["Certainty"] for m in focal_temporal_example["correct_event"]["mentions"]
    ] == ["5", "4"]
    temporal_lobe_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"] == "Diagnosis: Temporal lobe epilepsy."
    )
    assert [m["text"] for m in temporal_lobe_example["correct_event"]["mentions"]] == [
        "Temporal lobe epilepsy",
        "epilepsy",
    ]
    structural_focal_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"] == "Diagnosis: symptomatic structural focal epilepsy."
    )
    assert [m["text"] for m in structural_focal_example["correct_event"]["mentions"]] == [
        "symptomatic structural focal epilepsy"
    ]
    intractable_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"]
        == "I reviewed this lady with intractable epilepsy in clinic today."
    )
    assert [m["text"] for m in intractable_example["correct_event"]["mentions"]] == [
        "intractable epilepsy"
    ]
    gtc_jme_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"].startswith("Diagnosis: generalised tonic clonic")
    )
    assert [m["text"] for m in gtc_jme_example["correct_event"]["mentions"]] == [
        "generalised tonic clonic seizures",
        "JME",
    ]
    composite_dx_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"].startswith("Diagnosis: Complex partial seizures")
    )
    assert [m["text"] for m in composite_dx_example["correct_event"]["mentions"]] == [
        "Complex partial seizures",
        "secondary generalised tonic clonic seizures",
    ]
    general_complex_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"].startswith(
            "Despite this she continues to get general and complex partial seizures"
        )
    )
    assert [m["text"] for m in general_complex_example["correct_event"]["mentions"]] == [
        "complex partial seizures"
    ]
    unclassified_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"] == "Diagnosis: Epilepsy - unclassified, possibly generalised."
    )
    assert [m["text"] for m in unclassified_example["correct_event"]["mentions"]] == [
        "epilepsy",
        "generalised epilepsy",
    ]
    assert [
        m["attributes"]["Certainty"] for m in unclassified_example["correct_event"]["mentions"]
    ] == [
        "5",
        "3",
    ]
    generic_specific_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"] == "Diagnosis: epilepsy - probable focal"
    )
    assert [m["text"] for m in generic_specific_example["correct_event"]["mentions"]] == [
        "epilepsy",
        "focal epilepsy",
    ]
    assert (
        generic_specific_example["correct_event"]["mentions"][0]["attributes"]["Certainty"] == "5"
    )
    assert (
        generic_specific_example["correct_event"]["mentions"][1]["attributes"]["Certainty"] == "4"
    )
    focal_seizure_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"] == "He had a single focal seizure."
    )
    assert focal_seizure_example["correct_event"]["mentions"][0]["text"] == "focal seizure"
    absence_like_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"] == "Seizure type and frequency: absence like seizures 2014."
    )
    assert absence_like_example["correct_event"]["mentions"][0]["text"] == ("absence like seizures")
    assert (
        absence_like_example["correct_event"]["mentions"][0]["attributes"]["DiagCategory"]
        == "MultipleSeizures"
    )
    assert (
        absence_like_example["correct_event"]["mentions"][1]["attributes"]["NumberOfSeizures"]
        == "1"
    )
    planned_mri_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"] == "I will request a repeat MRI scan next year."
    )
    assert planned_mri_example["correct_event"]["mentions"] == []
    several_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"] == "He has had several seizures since the last clinic visit."
    )
    assert several_example["correct_event"]["mentions"][0]["attributes"]["NumberOfSeizures"] == "3"
    heading_several_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"].startswith("Seizure type and frequency: Uncertain")
    )
    assert heading_several_example["correct_event"]["mentions"][0]["attributes"] == {
        "NumberOfSeizures": "3",
        "TimeSince_or_TimeOfEvent": "Since",
        "PointInTime": "LastClinic",
    }
    last_event_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"]
        == "Focal to bilateral convulsive seizures, last event around Christmas 2017."
    )
    assert (
        last_event_example["correct_event"]["mentions"][0]["attributes"]["NumberOfSeizures"] == "0"
    )
    bare_seizure_free_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"] == "He remains seizure free and is now driving."
    )
    assert bare_seizure_free_example["correct_event"]["mentions"] == []
    well_controlled_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"].startswith("He suffered with generalised")
    )
    assert well_controlled_example["correct_event"]["mentions"] == []
    risk_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"].startswith("I explained that even though")
    )
    assert risk_example["correct_event"]["mentions"] == []
    unusual_thought_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"].startswith("She tells me that she has been getting")
    )
    assert unusual_thought_example["correct_event"]["mentions"] == []
    contextual_episode_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"].startswith("The episodes last no longer")
    )
    assert contextual_episode_example["correct_event"]["mentions"] == []
    teenage_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"].startswith("His last seizures were in his teenage")
    )
    assert teenage_example["correct_event"]["mentions"][0]["attributes"]["AgeLower"] == "13"
    no_event_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"] == "Unwitnessed blackouts and anxiety, no epileptic seizures."
    )
    assert no_event_example["correct_event"] == []
    generic_events_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"].startswith("The events have been going on")
    )
    assert generic_events_example["correct_event"] == []
    loss_of_consciousness_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"].startswith("He has had around 7 episodes")
    )
    assert loss_of_consciousness_example["correct_event"] == []
    jerks_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"].startswith("She has jerks while travelling")
    )
    assert jerks_example["correct_event"] == []
    ecg_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"] == "Her ECG was normal."
    )
    assert ecg_example["correct_event"]["mentions"] == []


def test_qwen_compact_prompt_profile_keeps_schema_with_shorter_payload() -> None:
    full_payload = structured.build_prompt_input(_LETTER)
    compact_str = structured.build_prompt_input(_LETTER, prompt_profile="qwen_compact")
    compact = json.loads(compact_str)

    assert len(compact_str) < len(full_payload)
    assert compact["prompt_version"] == structured.QWEN_COMPACT_PROMPT_VERSION
    assert compact["prompt_profile"] == "qwen_compact"
    assert "clinical_events" in compact["output_schema"]
    rules = " ".join(compact["rules"])
    assert "one Prescription mention per dose" in rules
    assert "render both separately" in rules
    assert "intractable epilepsy" in rules
    assert "do not render bare modifiers" in rules
    assert "Do not render myoclonic jerks" in rules
    assert "nonepileptic events" in rules
    assert "never emit an SF mention with empty attributes" in rules
    assert "SeizureFrequency headings are high-value evidence" in rules
    assert "diagnostically vague episodes" in rules
    assert "NumberOfSeizures='1', YearDate='2014'" in rules
    assert "do not default unrelated modalities to No" in rules
    assert "both entity and text" in rules
    assert "Do not invent CUI values" in rules
    assert compact["candidate_evidence_ledger"]
    heading_example = next(
        example
        for example in compact["worked_examples"]
        if example["note_fragment"].startswith("Seizure type and frequency: Uncertain")
    )
    assert heading_example["correct_event"]["mentions"][0]["attributes"]["NumberOfSeizures"] == "3"
    dated_example = next(
        example
        for example in compact["worked_examples"]
        if example["note_fragment"] == "Seizure type and frequency: absence like seizures 2014."
    )
    assert dated_example["correct_event"]["mentions"][0]["attributes"]["NumberOfSeizures"] == "1"
    intractable_example = next(
        example
        for example in compact["worked_examples"]
        if example["note_fragment"]
        == "I reviewed this lady with intractable epilepsy in clinic today."
    )
    assert intractable_example["correct_event"]["mentions"][0]["text"] == ("intractable epilepsy")
    vague_episode_example = next(
        example
        for example in compact["worked_examples"]
        if example["note_fragment"].startswith("She has been getting episodes")
    )
    assert vague_episode_example["correct_event"]["mentions"] == []
    eeg_example = next(
        example
        for example in compact["worked_examples"]
        if example["note_fragment"] == "An EEG in 2016 did show focal slowing."
    )
    assert eeg_example["correct_event"]["mentions"][0]["attributes"] == {
        "EEG_Performed": "Yes",
        "EEG_Results": "Abnormal",
    }


def test_v10_contract_drops_ledger_examples_and_later_rules() -> None:
    original = structured.PROMPT_VERSION
    try:
        structured.set_active_prompt_version(structured.PROMPT_VERSION_V10)
        payload = json.loads(structured.build_prompt_input(_LETTER))
    finally:
        structured.set_active_prompt_version(original)

    assert payload["prompt_version"] == structured.PROMPT_VERSION_V10
    assert payload["prompt_version"] != structured.PROMPT_VERSION
    assert "architecture" not in payload
    assert "decision_procedure" not in payload
    assert "candidate_evidence_ledger" not in payload
    assert "event_lane_guide" not in payload
    assert "worked_examples" not in payload
    assert "extra_clinical_guidance" not in payload
    assert "candidate_evidence_ledger" not in payload["task"]
    assert len(payload["clinical_rules"]) == 12
    assert "First classify each candidate_evidence_ledger item" not in " ".join(
        payload["clinical_rules"]
    )
    assert "clinical_events" in payload["output_schema"]
    assert set(payload["family_guidance"]) == {
        "medication",
        "diagnosis",
        "seizure_frequency",
        "investigation",
    }
    assert "DiagCategory" in payload["attribute_vocabulary"][DIAGNOSIS.name]
    assert payload["letter_id"] == "TEST001"
    assert payload["letter_text"] == _NOTE
