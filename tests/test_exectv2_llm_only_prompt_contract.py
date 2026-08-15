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
    assert "CUI" not in rules
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
    assert len(payload["clinical_rules"]) == 11
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


def test_v11_contract_is_leftover_extraction_job_without_codebook() -> None:
    original = structured.PROMPT_VERSION
    try:
        structured.set_active_prompt_version(structured.PROMPT_VERSION_V11)
        payload_str = structured.build_prompt_input(_LETTER)
        payload = json.loads(payload_str)
    finally:
        structured.set_active_prompt_version(original)

    leaked = [phrase for phrase in FORBIDDEN_PHRASES if phrase in payload_str]
    assert leaked == []
    assert payload["prompt_version"] == structured.PROMPT_VERSION_V11
    assert payload["prompt_version"] != structured.PROMPT_VERSION
    assert structured.PROMPT_VERSION == structured.PROMPT_VERSION_V0_9_24
    assert "architecture" not in payload
    assert "decision_procedure" not in payload
    assert "candidate_evidence_ledger" not in payload
    assert "event_lane_guide" not in payload
    assert "worked_examples" not in payload
    assert "extra_clinical_guidance" not in payload
    assert "candidate_evidence_ledger" not in payload["task"]
    joined = " ".join(payload["clinical_rules"])
    assert "several" not in joined.lower()
    assert "couple" not in joined.lower()
    assert "probable temporal" not in joined.lower()
    assert "awaiting" not in joined.lower()
    assert "LastClinic" not in joined
    assert "focal epilepsy-Probable" not in joined
    assert "CUI" not in joined
    assert set(payload["family_guidance"]) == {
        "medication",
        "diagnosis",
        "seizure_frequency",
        "investigation",
    }
    assert "DiagCategory" in payload["attribute_vocabulary"][DIAGNOSIS.name]
    assert payload["letter_id"] == "TEST001"
    assert payload["letter_text"] == _NOTE


def test_v11_dev20_payload_check_does_not_change_default() -> None:
    from scripts.run_exectv2_structured_prompt_v11_luna_dev20 import verify_payload

    before = structured.PROMPT_VERSION
    payload = verify_payload()
    assert payload["ok"] is True
    assert payload["prompt_version"] == structured.PROMPT_VERSION_V11
    assert payload["default_prompt_version"] == structured.PROMPT_VERSION_V0_9_24
    assert structured.PROMPT_VERSION == before == structured.PROMPT_VERSION_V0_9_24


def test_v11_dev20_sf_encoding_rewrite_buckets() -> None:
    from scripts.run_exectv2_structured_prompt_v11_luna_dev20 import (
        count_sf_encoding_rewrites,
    )

    mentions = [
        {
            "entity": SEIZURE_FREQUENCY.name,
            "text": "several seizures",
            "evidence": "several seizures since the last clinic",
            "attributes": {"NumberOfSeizures": "several"},
        },
        {
            "entity": SEIZURE_FREQUENCY.name,
            "text": "a few seizures",
            "evidence": "a few seizures per year",
            "attributes": {"NumberOfSeizures": "few"},
        },
        {
            "entity": SEIZURE_FREQUENCY.name,
            "text": "seizures",
            "evidence": "seizures 2-4 per month",
            "attributes": {"NumberOfSeizures": "2-4"},
        },
        {
            "entity": SEIZURE_FREQUENCY.name,
            "text": "seizures",
            "evidence": "seizures every 3 weeks",
            "attributes": {},
        },
        {
            "entity": DIAGNOSIS.name,
            "text": "epilepsy",
            "evidence": "epilepsy",
            "attributes": {},
        },
    ]
    assert count_sf_encoding_rewrites(mentions) == {
        "several": 1,
        "few": 1,
        "range_split": 1,
        "interval_missing_1": 1,
        "other_word_number": 0,
    }


def test_v11_dev20_topology_decision_thresholds() -> None:
    from scripts.run_exectv2_structured_prompt_v11_luna_dev20 import topology_failures

    sufficient = {
        "headline_f1_delta": -0.049,
        "family_f1_delta": {
            "Diagnosis": -0.079,
            "SeizureFrequency": 0.01,
            "Prescription": 0.0,
            "Investigations": -0.02,
        },
        "four_family_letter_exact_wins": 1,
        "four_family_letter_exact_losses": 3,
    }
    assert topology_failures(sufficient) == []

    missing = {
        "headline_f1_delta": -0.05,
        "family_f1_delta": {
            "Diagnosis": -0.08,
            "SeizureFrequency": 0.0,
            "Prescription": 0.0,
            "Investigations": 0.0,
        },
        "four_family_letter_exact_wins": 0,
        "four_family_letter_exact_losses": 3,
    }
    assert topology_failures(missing) == [
        "hybrid four-family F1 drop -0.05",
        "hybrid Diagnosis F1 drop -0.08",
        "hybrid net four-family letter-exact losses 3",
    ]


def test_v12_contract_is_current_scope_leftover_without_codebook() -> None:
    original = structured.PROMPT_VERSION
    try:
        structured.set_active_prompt_version(structured.PROMPT_VERSION_V12)
        payload_str = structured.build_prompt_input(_LETTER)
        payload = json.loads(payload_str)
    finally:
        structured.set_active_prompt_version(original)

    leaked = [phrase for phrase in FORBIDDEN_PHRASES if phrase in payload_str]
    assert leaked == []
    assert payload["prompt_version"] == structured.PROMPT_VERSION_V12
    assert structured.PROMPT_VERSION == structured.PROMPT_VERSION_V0_9_24
    assert "architecture" not in payload
    assert "worked_examples" not in payload
    joined = " ".join(payload["clinical_rules"]) + " " + payload["task"]
    assert "several" not in joined.lower()
    assert "couple" not in joined.lower()
    assert "LastClinic" not in joined
    assert "driving" in joined.lower()
    assert "Completed tests only" in joined
    assert "current anti-seizure" in joined
    assert "CUI" not in joined


def test_v12_dev20_payload_check_does_not_change_default() -> None:
    from scripts.run_exectv2_structured_prompt_v12_luna_dev20 import verify_payload

    before = structured.PROMPT_VERSION
    payload = verify_payload()
    assert payload["ok"] is True
    assert payload["prompt_version"] == structured.PROMPT_VERSION_V12
    assert payload["default_prompt_version"] == structured.PROMPT_VERSION_V0_9_24
    assert structured.PROMPT_VERSION == before == structured.PROMPT_VERSION_V0_9_24


def test_v13_contract_is_short_extraction_job_without_scope_sermon() -> None:
    original = structured.PROMPT_VERSION
    try:
        structured.set_active_prompt_version(structured.PROMPT_VERSION_V13)
        payload_str = structured.build_prompt_input(_LETTER)
        payload = json.loads(payload_str)
    finally:
        structured.set_active_prompt_version(original)

    leaked = [phrase for phrase in FORBIDDEN_PHRASES if phrase in payload_str]
    assert leaked == []
    assert payload["prompt_version"] == structured.PROMPT_VERSION_V13
    assert structured.PROMPT_VERSION == structured.PROMPT_VERSION_V0_9_24
    assert "architecture" not in payload
    assert "worked_examples" not in payload
    assert "candidate_evidence_ledger" not in payload
    joined = " ".join(payload["clinical_rules"]) + " " + payload["task"]
    assert "several" not in joined.lower()
    assert "couple" not in joined.lower()
    assert "LastClinic" not in joined
    assert "driving" not in joined.lower()
    assert "Completed tests only" not in joined
    assert "letter's own words" in joined
    assert "CUI" not in joined
    assert len(payload["clinical_rules"]) == 14
    assert payload["family_guidance"] == {
        "medication": (
            "Find current anti-seizure medication statements. Render Prescription "
            "with DrugName, DrugDose, DoseUnit, and Frequency when the letter "
            "states them. Mention text is the drug name, or the short regimen "
            "span when that is all the letter gives."
        ),
        "diagnosis": (
            "Find named epileptic diagnoses and named seizure types. Render "
            "Diagnosis with DiagCategory, Certainty, and Negation. Mention text "
            "is the core concept span."
        ),
        "seizure_frequency": (
            "Find how often a seizure type occurs now, including seizure-free "
            "duration, ranges, clusters, dated counts, and frequency change. "
            "Mention text is the seizure-type anchor. Put counts and dates in "
            "attributes. Choose the named type when the count belongs to that "
            "type; otherwise use the generic seizure span."
        ),
        "investigation": (
            "Find completed EEG, MRI, CT, or telemetry statements. Render "
            "performed, result, and type attributes when the letter states them. "
            "One event per modality."
        ),
    }


def test_v13_dev20_payload_check_does_not_change_default() -> None:
    from scripts.run_exectv2_structured_prompt_v13_luna_dev20 import verify_payload

    before = structured.PROMPT_VERSION
    payload = verify_payload()
    assert payload["ok"] is True
    assert payload["prompt_version"] == structured.PROMPT_VERSION_V13
    assert payload["default_prompt_version"] == structured.PROMPT_VERSION_V0_9_24
    assert structured.PROMPT_VERSION == before == structured.PROMPT_VERSION_V0_9_24


def test_v14_contract_uses_sf_roles_without_codebook() -> None:
    original = structured.PROMPT_VERSION
    try:
        structured.set_active_prompt_version(structured.PROMPT_VERSION_V14)
        payload_str = structured.build_prompt_input(_LETTER)
        payload = json.loads(payload_str)
    finally:
        structured.set_active_prompt_version(original)

    leaked = [phrase for phrase in FORBIDDEN_PHRASES if phrase in payload_str]
    assert leaked == []
    assert payload["prompt_version"] == structured.PROMPT_VERSION_V14
    assert structured.PROMPT_VERSION == structured.PROMPT_VERSION_V0_9_24
    assert "architecture" not in payload
    assert "worked_examples" not in payload
    assert "candidate_evidence_ledger" not in payload
    joined = (
        " ".join(payload["clinical_rules"])
        + " "
        + payload["task"]
        + " "
        + payload["family_guidance"]["seizure_frequency"]
    )
    assert "several" not in joined.lower()
    assert "couple" not in joined.lower()
    assert "LastClinic" not in joined
    assert "driving" not in joined.lower()
    assert "Completed tests only" not in joined
    assert "current_rate" in joined
    assert "seizure_free" in joined
    assert "change_companion" in joined
    assert "letter's own words" in joined
    assert len(payload["clinical_rules"]) == 14


def test_v14_dev20_payload_check_does_not_change_default() -> None:
    from scripts.run_exectv2_structured_prompt_v14_luna_dev20 import verify_payload

    before = structured.PROMPT_VERSION
    payload = verify_payload()
    assert payload["ok"] is True
    assert payload["prompt_version"] == structured.PROMPT_VERSION_V14
    assert payload["default_prompt_version"] == structured.PROMPT_VERSION_V0_9_24
    assert structured.PROMPT_VERSION == before == structured.PROMPT_VERSION_V0_9_24


def test_v15_contract_adds_candidate_spans_without_codebook() -> None:
    original = structured.PROMPT_VERSION
    try:
        structured.set_active_prompt_version(structured.PROMPT_VERSION_V15)
        payload_str = structured.build_prompt_input(_LETTER)
        payload = json.loads(payload_str)
    finally:
        structured.set_active_prompt_version(original)

    leaked = [phrase for phrase in FORBIDDEN_PHRASES if phrase in payload_str]
    assert leaked == []
    assert payload["prompt_version"] == structured.PROMPT_VERSION_V15
    assert structured.PROMPT_VERSION == structured.PROMPT_VERSION_V0_9_24
    assert "architecture" not in payload
    assert "worked_examples" not in payload
    assert "candidate_evidence_ledger" not in payload
    assert "decision_procedure" not in payload
    spans = payload["candidate_spans"]
    assert spans
    assert {"family", "evidence", "anchor_hint"} <= set(spans[0])
    assert "lane_hint" not in spans[0]
    joined = (
        " ".join(payload["clinical_rules"])
        + " "
        + payload["task"]
        + " "
        + payload["family_guidance"]["seizure_frequency"]
    )
    assert "several" not in joined.lower()
    assert "couple" not in joined.lower()
    assert "LastClinic" not in joined
    assert "driving" not in joined.lower()
    assert "current_rate" in joined
    assert "candidate_spans" in joined
    assert "letter's own words" in joined
    assert len(payload["clinical_rules"]) == 15


def test_v16_contract_is_v13_plus_eight_synthetic_shapes() -> None:
    original = structured.PROMPT_VERSION
    try:
        structured.set_active_prompt_version(structured.PROMPT_VERSION_V16)
        payload_str = structured.build_prompt_input(_LETTER)
        payload = json.loads(payload_str)
    finally:
        structured.set_active_prompt_version(original)

    leaked = [phrase for phrase in FORBIDDEN_PHRASES if phrase in payload_str]
    assert leaked == []
    assert payload["prompt_version"] == structured.PROMPT_VERSION_V16
    assert structured.PROMPT_VERSION == structured.PROMPT_VERSION_V0_9_24
    assert "architecture" not in payload
    assert "candidate_evidence_ledger" not in payload
    examples = payload["worked_examples"]
    assert len(examples) == 8
    assert {item["id"] for item in examples} == {
        "am_pm_split",
        "none_since_named_type",
        "named_type_not_generic",
        "typed_rate_and_return_companion",
        "please_start_not_current",
        "jme_without_jerk_diagnosis",
        "remote_lifetime_is_seizure_free",
        "seizure_like_not_current_rate",
    }
    blob = json.dumps(examples)
    assert "Williams" not in blob
    assert "probable focal" not in blob
    assert "last clinic appointment" not in blob
    joined = " ".join(payload["clinical_rules"]) + " " + payload["task"]
    assert "several" not in joined.lower()
    assert "couple" not in joined.lower()
    assert "LastClinic" not in joined
    assert len(payload["clinical_rules"]) == 14


def test_v17_contract_removes_metadata_and_preserves_semantic_order() -> None:
    payload_str = structured.build_prompt_input(
        _LETTER,
        prompt_version=structured.PROMPT_VERSION_V17,
    )
    payload = json.loads(payload_str)

    assert list(payload) == [
        "task",
        "output_schema",
        "family_guidance",
        "attribute_vocabulary",
        "clinical_rules",
        "worked_examples",
        "letter_text",
    ]
    assert "prompt_version" not in payload
    assert "letter_id" not in payload
    assert payload["letter_text"] == _LETTER.note_text
    assert len(payload["worked_examples"]) == 8
    schema = payload["output_schema"]
    assert set(schema) == {"clinical_events", "patient_history", "medication_history"}
    assert schema["patient_history"][0]["kind"].split(" | ") == [
        "unclassified_event",
        "non_epileptic_event",
        "febrile_event",
        "generic_jerk_or_absence",
        "comorbidity",
    ]
    assert schema["medication_history"][0]["kind"] == (
        "planned_medication | past_medication"
    )
    instructions = _prompt_fields_without_letter(payload).lower()
    assert "instead of diagnosis or seizurefrequency" in instructions
    assert "generic seizure with a real rate" in instructions
    assert "last-event zero" in instructions
    assert "instead of prescription" in instructions
    assert "not clinical_events or output mentions" in instructions
    assert "source-near" not in instructions
    assert "benchmark" not in instructions
    assert "scored" not in instructions


def test_v17_uses_minimal_system_message_in_rendered_model_request() -> None:
    payload_str = structured.build_prompt_input(
        _LETTER,
        prompt_version=structured.PROMPT_VERSION_V17,
    )
    program = structured.DspyKeyEntitiesStructuredExtractor(
        prompt_version=structured.PROMPT_VERSION_V17
    )
    messages = program.render_messages(prompt_input_json=payload_str)

    assert messages[0] == {
        "role": "system",
        "content": (
            "Extract structured clinical events from the supplied clinical letter. "
            "Return the requested output fields exactly."
        ),
    }
    assert messages[1]["role"] == "user"
    assert messages[1]["content"].count(payload_str) == 1
    assert "prompt_version" not in messages[1]["content"]
    assert "letter_id" not in messages[1]["content"]


def test_v16_keeps_legacy_model_message_contract() -> None:
    payload_str = structured.build_prompt_input(
        _LETTER,
        prompt_version=structured.PROMPT_VERSION_V16,
    )
    program = structured.DspyKeyEntitiesStructuredExtractor(
        prompt_version=structured.PROMPT_VERSION_V16
    )
    messages = program.render_messages(prompt_input_json=payload_str)

    assert messages[0]["content"].startswith("Your input fields are:")
    assert json.loads(payload_str)["prompt_version"] == structured.PROMPT_VERSION_V16


def test_v17_keeps_prompt_identity_in_research_record() -> None:
    original = structured.PROMPT_VERSION
    try:
        structured.set_active_prompt_version(structured.PROMPT_VERSION_V17)
        rows, _ = structured.run_split(
            [_LETTER],
            split="dev",
            model="not-called",
            temperature=0.0,
            max_tokens=900,
            mode="prompt-only",
        )
    finally:
        structured.set_active_prompt_version(original)

    assert rows[0]["prompt_version"] == structured.PROMPT_VERSION_V17


def _prompt_fields_without_letter(payload: dict) -> str:
    return json.dumps(
        {key: value for key, value in payload.items() if key != "letter_text"}
    )


def test_no_prompt_version_mentions_cui() -> None:
    original = structured.PROMPT_VERSION
    versions = [
        structured.PROMPT_VERSION_V0_9_24,
        structured.PROMPT_VERSION_V10,
        structured.PROMPT_VERSION_V11,
        structured.PROMPT_VERSION_V12,
        structured.PROMPT_VERSION_V13,
        structured.PROMPT_VERSION_V14,
        structured.PROMPT_VERSION_V15,
        structured.PROMPT_VERSION_V16,
        structured.PROMPT_VERSION_V17,
        structured.PROMPT_VERSION_V0_9_25_LUNA_SF_STATE,
        structured.PROMPT_VERSION_V0_9_25_LUNA_SF_BOUNDARY_DX,
    ]
    try:
        for version in versions:
            structured.set_active_prompt_version(version)
            payload = json.loads(structured.build_prompt_input(_LETTER))
            blob = _prompt_fields_without_letter(payload).lower()
            assert "cui" not in blob, version
            assert "umls" not in blob, version
            vocab = payload["attribute_vocabulary"]
            for family_vocab in vocab.values():
                assert "CUI" not in family_vocab
                assert "CUIPhrase" not in family_vocab
        compact = json.loads(
            structured.build_prompt_input(_LETTER, prompt_profile="qwen_compact")
        )
        compact_blob = _prompt_fields_without_letter(compact).lower()
        assert "cui" not in compact_blob
        assert "umls" not in compact_blob
    finally:
        structured.set_active_prompt_version(original)

    assert structured.PROMPT_VERSION == structured.PROMPT_VERSION_V0_9_24


def test_v13_dev140_payload_check_does_not_change_default() -> None:
    from scripts.run_exectv2_structured_prompt_v13_luna_dev140 import verify_payload

    before = structured.PROMPT_VERSION
    payload = verify_payload()
    assert payload["ok"] is True
    assert payload["prompt_version"] == structured.PROMPT_VERSION_V13
    assert payload["n_letters"] == 140
    assert structured.PROMPT_VERSION == before == structured.PROMPT_VERSION_V0_9_24


def test_v15_dev20_payload_check_does_not_change_default() -> None:
    from scripts.run_exectv2_structured_prompt_v15_luna_dev20 import verify_payload

    before = structured.PROMPT_VERSION
    payload = verify_payload()
    assert payload["ok"] is True
    assert payload["prompt_version"] == structured.PROMPT_VERSION_V15
    assert payload["default_prompt_version"] == structured.PROMPT_VERSION_V0_9_24
    assert structured.PROMPT_VERSION == before == structured.PROMPT_VERSION_V0_9_24
