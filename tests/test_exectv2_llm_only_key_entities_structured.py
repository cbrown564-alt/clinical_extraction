"""Tests for the ExECTv2 four-family structured-event extractor."""

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
from tests.test_exectv2_llm_only_sf import FORBIDDEN_PHRASES

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
    assert med_example["correct_event"]["mentions"][0]["text"] == (
        "lamotrigine 200 mg twice daily"
    )
    split_med_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"] == "Current medication: Epilim 300 mg mane and 600 mg nocte."
    )
    assert [
        m["attributes"]["Frequency"]
        for m in split_med_example["correct_event"]["mentions"]
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
    assert interval_example["correct_event"]["mentions"][0]["attributes"][
        "LowerNumberOfTimePeriods"
    ] == "3"
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
    assert [
        mention["text"]
        for mention in dated_type_example["correct_event"]["mentions"]
    ] == [
        "generalised tonic clonic seizures",
        "absence like seizures",
    ]
    assert dated_type_example["correct_event"]["mentions"][1]["attributes"][
        "NumberOfSeizures"
    ] == "1"
    returned_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"].startswith(
            "Unfortunately after a period of seizure freedom"
        )
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
        m["attributes"]["Certainty"]
        for m in focal_temporal_example["correct_event"]["mentions"]
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
        m["attributes"]["Certainty"]
        for m in unclassified_example["correct_event"]["mentions"]
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
    assert generic_specific_example["correct_event"]["mentions"][0]["attributes"][
        "Certainty"
    ] == "5"
    assert generic_specific_example["correct_event"]["mentions"][1]["attributes"][
        "Certainty"
    ] == "4"
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
    assert absence_like_example["correct_event"]["mentions"][0]["text"] == (
        "absence like seizures"
    )
    assert absence_like_example["correct_event"]["mentions"][0]["attributes"][
        "DiagCategory"
    ] == "MultipleSeizures"
    assert absence_like_example["correct_event"]["mentions"][1]["attributes"][
        "NumberOfSeizures"
    ] == "1"
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
    assert several_example["correct_event"]["mentions"][0]["attributes"][
        "NumberOfSeizures"
    ] == "3"
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
    assert last_event_example["correct_event"]["mentions"][0]["attributes"][
        "NumberOfSeizures"
    ] == "0"
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
    assert "do not render bare modifiers" in rules
    assert "Do not render myoclonic jerks" in rules
    assert "never emit an SF mention with empty attributes" in rules
    assert "SeizureFrequency headings are high-value evidence" in rules
    assert "NumberOfSeizures='1', YearDate='2014'" in rules
    assert "both entity and text" in rules
    assert "Do not invent CUI values" in rules
    assert compact["candidate_evidence_ledger"]
    heading_example = next(
        example
        for example in compact["worked_examples"]
        if example["note_fragment"].startswith("Seizure type and frequency: Uncertain")
    )
    assert heading_example["correct_event"]["mentions"][0]["attributes"][
        "NumberOfSeizures"
    ] == "3"
    dated_example = next(
        example
        for example in compact["worked_examples"]
        if example["note_fragment"] == "Seizure type and frequency: absence like seizures 2014."
    )
    assert dated_example["correct_event"]["mentions"][0]["attributes"][
        "NumberOfSeizures"
    ] == "1"


def test_candidate_evidence_ledger_types_family_lanes() -> None:
    note = (
        "Current medication lamotrigine 200 mg twice daily. "
        "I will request a repeat MRI scan next year. "
        "MRI 2016 showed left hippocampal sclerosis. "
        "EEG did show temporal slowing. "
        "Diagnosis: focal epilepsy. "
        "Family history includes epilepsy. "
        "He has not had any events which resemble absences, myoclonus or focal seizures. "
        "She has not had any further seizures since last clinic."
    )
    letter = ExectLetter(letter_id="TEST002", note_text=note)

    ledger = structured.candidate_evidence_ledger_for_letter(letter)

    assert any(
        item["family"] == "medication" and item["lane_hint"] == "current_regimen"
        for item in ledger
    )
    assert any(
        item["family"] == "investigation" and item["lane_hint"] == "planned_investigation"
        for item in ledger
    )
    assert any(
        item["family"] == "investigation" and item["lane_hint"] == "performed_investigation"
        and item["anchor_hint"] == "EEG"
        for item in ledger
    )
    assert any(
        item["family"] == "diagnosis" and item["lane_hint"] == "diagnosis_assertion"
        for item in ledger
    )
    assert any(
        item["family"] == "diagnosis" and item["lane_hint"] == "diagnosis_context_only"
        for item in ledger
    )
    assert any(
        item["family"] == "diagnosis" and item["lane_hint"] == "symptom_or_nonepileptic"
        for item in ledger
    )
    assert any(
        item["family"] == "seizure_frequency" and item["lane_hint"] == "reject"
        for item in ledger
    )
    assert any(
        item["family"] == "seizure_frequency"
        and item["lane_hint"] == "seizure_free_anchor"
        for item in ledger
    )


def test_parse_structured_events_coerces_nested_values() -> None:
    raw = json.dumps(
        {
            "clinical_events": [
                {
                    "family": "medication",
                    "anchor_text": "lamotrigine",
                    "evidence": "lamotrigine 200 mg twice daily",
                    "event_state": {"dose": 200},
                    "mentions": [
                        {
                            "entity": PRESCRIPTION.name,
                            "text": "lamotrigine",
                            "attributes": {
                                "DrugName": "lamotrigine",
                                "DrugDose": 200,
                                "DoseUnit": "mg",
                                "Frequency": 2,
                            },
                        }
                    ],
                    "confidence": "high",
                    "rationale": "Medication stated.",
                }
            ]
        }
    )

    record, errors = structured.parse_structured_events_json(raw)

    assert record is not None
    event = record.clinical_events[0]
    assert event.event_state["dose"] == "200"
    assert event.mentions[0].attributes["DrugDose"] == "200"
    assert event.mentions[0].attributes["Frequency"] == "2"
    assert any("coerced_attribute_value" in error for error in errors)


def test_parse_structured_events_repairs_python_literal_dialect() -> None:
    raw = (
        "{'clinical_events': [{'family': 'diagnosis', 'anchor_text': 'epilepsy', "
        "'evidence': 'Diagnosis: epilepsy', 'event_state': {'certainty': 5}, "
        "'mentions': [{'entity': 'Diagnosis', 'text': 'epilepsy', "
        "'attributes': {'DiagCategory': 'Epilepsy', 'Certainty': 5, "
        "'Negation': 'Affirmed'}}], 'confidence': 'high', "
        "'rationale': 'Diagnosis stated.'}]}"
    )

    record, errors = structured.parse_structured_events_json(raw)

    assert record is not None
    assert record.clinical_events[0].mentions[0].attributes["Certainty"] == "5"
    assert "json_dialect_repaired: python_literal" in errors


def test_parse_structured_events_drops_no_mention_reject_events() -> None:
    raw = json.dumps(
        {
            "clinical_events": [
                {
                    "family": "reject",
                    "anchor_text": "limb shaking",
                    "evidence": "limb shaking with retained consciousness",
                    "mentions": [],
                    "confidence": "low",
                    "rationale": "The event is explicitly rejected as non-epileptic.",
                },
                {
                    "family": "diagnosis",
                    "anchor_text": "epilepsy",
                    "evidence": "Diagnosis: epilepsy",
                    "mentions": [
                        {
                            "entity": DIAGNOSIS.name,
                            "text": "epilepsy",
                            "attributes": {
                                "DiagCategory": "Epilepsy",
                                "Certainty": "5",
                                "Negation": "Affirmed",
                            },
                        }
                    ],
                    "confidence": "high",
                    "rationale": "Diagnosis stated.",
                },
            ]
        }
    )

    record, errors = structured.parse_structured_events_json(raw)

    assert record is not None
    assert [event.family for event in record.clinical_events] == ["diagnosis"]
    assert "dropped_no_mention_reject_event: event[0]" in errors


def test_parse_structured_events_accepts_top_level_event_array() -> None:
    raw = json.dumps(
        [
            {
                "family": "diagnosis",
                "anchor_text": "epilepsy",
                "evidence": "Diagnosis: epilepsy",
                "mentions": [
                    {
                        "entity": DIAGNOSIS.name,
                        "text": "epilepsy",
                        "attributes": {
                            "DiagCategory": "Epilepsy",
                            "Certainty": "5",
                            "Negation": "Affirmed",
                        },
                    }
                ],
                "confidence": "high",
                "rationale": "Diagnosis stated.",
            }
        ]
    )

    record, errors = structured.parse_structured_events_json(raw)

    assert record is not None
    assert record.clinical_events[0].anchor_text == "epilepsy"
    assert not any(error.startswith("schema_validation_error") for error in errors)


def test_parse_structured_events_drops_malformed_nested_mentions() -> None:
    raw = json.dumps(
        {
            "clinical_events": [
                {
                    "family": "investigation",
                    "anchor_text": "EEG recording",
                    "evidence": "confirmed with an EEG recording",
                    "mentions": [
                        {
                            "entity": INVESTIGATIONS.name,
                            "text": "EEG recording",
                            "attributes": {
                                "EEG_Performed": "Yes",
                                "EEG_Results": "Abnormal",
                            },
                        },
                        {"attributes": {"CUI": "UMLS CUI not available in text"}},
                        "not a mention object",
                    ],
                    "confidence": "high",
                    "rationale": "EEG recording is stated.",
                }
            ]
        }
    )

    record, errors = structured.parse_structured_events_json(raw)

    assert record is not None
    assert len(record.clinical_events[0].mentions) == 1
    assert record.clinical_events[0].mentions[0].entity == INVESTIGATIONS.name
    assert any("missing=entity,text" in error for error in errors)
    assert any("not_object" in error for error in errors)
    assert not any(error.startswith("schema_validation_error") for error in errors)


def test_flatten_events_preserves_cross_entity_renderings() -> None:
    raw = json.dumps(
        {
            "clinical_events": [
                {
                    "family": "seizure_frequency",
                    "anchor_text": "focal seizures",
                    "evidence": "focal epilepsy with 2 focal seizures per month",
                    "event_state": {"rate": "2 per 1 Month"},
                    "mentions": [
                        {
                            "entity": DIAGNOSIS.name,
                            "text": "focal epilepsy",
                            "attributes": {
                                "DiagCategory": "Epilepsy",
                                "Certainty": "5",
                                "Negation": "Affirmed",
                            },
                        },
                        {
                            "entity": DIAGNOSIS.name,
                            "text": "focal seizures",
                            "attributes": {
                                "DiagCategory": "MultipleSeizures",
                                "Certainty": "5",
                                "Negation": "Affirmed",
                            },
                        },
                        {
                            "entity": SEIZURE_FREQUENCY.name,
                            "text": "focal seizures",
                            "attributes": {
                                "NumberOfSeizures": "2",
                                "NumberOfTimePeriods": "1",
                                "TimePeriod": "Month",
                            },
                        },
                    ],
                    "confidence": "high",
                    "rationale": "Diagnosis and rate are stated.",
                }
            ]
        }
    )
    record, errors = structured.parse_structured_events_json(raw)
    assert record is not None
    assert errors == []

    mentions = structured.flatten_events(record)

    assert [mention.entity for mention in mentions] == [
        DIAGNOSIS.name,
        DIAGNOSIS.name,
        SEIZURE_FREQUENCY.name,
    ]
    assert all(
        mention.evidence == "focal epilepsy with 2 focal seizures per month"
        for mention in mentions
    )


def test_to_predicted_letter_gates_evidence_and_projects_cuis() -> None:
    mentions = [
        structured.MentionForEvidence(
            entity=DIAGNOSIS.name,
            text="focal epilepsy",
            attributes={
                "CUI": "WRONG",
                "CUIPhrase": "wrong phrase",
                "DiagCategory": "Epilepsy",
                "Certainty": "5",
                "FrequencyChange": "Increased",
            },
            evidence="focal epilepsy with 2 focal seizures per month",
            confidence="high",
            rationale="Diagnosis stated.",
        ),
        structured.MentionForEvidence(
            entity=SEIZURE_FREQUENCY.name,
            text="focal seizures",
            attributes={"NumberOfSeizures": "2", "DiagCategory": "Epilepsy"},
            evidence="focal epilepsy with 2 focal seizures per month",
            confidence="high",
            rationale="Frequency stated.",
        ),
        structured.MentionForEvidence(
            entity=SEIZURE_FREQUENCY.name,
            text="focal seizures",
            attributes={"Negation": "Affirmed"},
            evidence="focal epilepsy with 2 focal seizures per month",
            confidence="high",
            rationale="No frequency-state attributes.",
        ),
        structured.MentionForEvidence(
            entity=INVESTIGATIONS.name,
            text="MRI",
            attributes={"MRI_Performed": "Yes"},
            evidence="MRI brain was normal",
            confidence="high",
            rationale="Duplicate modality-only rendering.",
        ),
        structured.MentionForEvidence(
            entity=INVESTIGATIONS.name,
            text="MRI brain",
            attributes={"MRI_Performed": "Yes", "MRI_Results": "Normal"},
            evidence="MRI brain was normal",
            confidence="high",
            rationale="Result-bearing rendering.",
        ),
        structured.MentionForEvidence(
            entity="PatientHistory",
            text="focal seizures",
            attributes={},
            evidence="focal epilepsy with 2 focal seizures per month",
        ),
        structured.MentionForEvidence(
            entity=INVESTIGATIONS.name,
            text="EEG",
            attributes={"EEG_Performed": "Yes"},
            evidence="not in the note",
        ),
        structured.MentionForEvidence(
            entity=PRESCRIPTION.name,
            text="lamotrigine 200 mg twice daily",
            attributes={
                "DrugName": "lamotrigine",
                "DrugDose": "200",
                "DoseUnit": "mg",
                "Frequency": "2",
            },
            evidence="Current treatment: lamotrigine 200 mg twice daily",
            confidence="high",
            rationale="Mention text itself is exact source evidence.",
        ),
        structured.MentionForEvidence(
            entity=DIAGNOSIS.name,
            text="focal seizures",
            attributes={
                "DiagCategory": "MultipleSeizures",
                "Certainty": "5",
                "Negation": "Affirmed",
            },
            evidence="wrong wrapper focal seizures",
            confidence="high",
            rationale="Diagnosis mention text itself is exact source evidence.",
        ),
    ]

    letter, warnings = structured.to_predicted_letter("TEST001", mentions, note_text=_NOTE)

    assert [mention.entity for mention in letter.mentions] == [
        DIAGNOSIS.name,
        SEIZURE_FREQUENCY.name,
        INVESTIGATIONS.name,
        PRESCRIPTION.name,
        DIAGNOSIS.name,
    ]
    diagnosis = letter.mentions[0]
    sf = letter.mentions[1]
    assert diagnosis.attributes["CUI"] == "C0014547"
    assert diagnosis.attributes["CUIPhrase"] == "focal epilepsy"
    assert "FrequencyChange" not in diagnosis.attributes
    assert sf.attributes["CUI"] == "C0751495"
    assert "DiagCategory" not in sf.attributes
    assert letter.mentions[2].text == "MRI brain"
    assert letter.mentions[3].evidence == "lamotrigine 200 mg twice daily"
    assert letter.mentions[4].evidence == "focal seizures"
    assert any("dropped_out_of_scope_entity" in warning for warning in warnings)
    assert any("dropped_evidence_not_substring" in warning for warning in warnings)
    assert any("repaired_evidence_from_mention_text" in warning for warning in warnings)
    assert any("Diagnosis: dropped_illegal_attribute" in warning for warning in warnings)
    assert any(
        "Diagnosis: dropped_model_supplied_projection_attribute" in warning
        for warning in warnings
    )
    assert any("dropped_no_frequency_state_rendering" in warning for warning in warnings)
    assert any("dropped_duplicate_modality_only_rendering" in warning for warning in warnings)


def test_summarize_rows_scores_only_key_entities() -> None:
    rows = [
        {
            "letter_id": "TEST001",
            "parse_errors": [],
            "n_events_raw": 2,
            "n_mentions_raw": 4,
            "n_mentions_scored": 4,
            "n_evidence_invalid": 0,
            "gold_mentions": [
                {
                    "entity": DIAGNOSIS.name,
                    "text": "focal epilepsy",
                    "attributes": {"DiagCategory": "Epilepsy"},
                },
                {
                    "entity": SEIZURE_FREQUENCY.name,
                    "text": "focal seizures",
                    "attributes": {"NumberOfSeizures": "2"},
                },
                {
                    "entity": PRESCRIPTION.name,
                    "text": "lamotrigine 200 mg twice daily",
                    "attributes": {
                        "DrugName": "lamotrigine",
                        "DrugDose": "200",
                        "DoseUnit": "mg",
                        "Frequency": "twice daily",
                    },
                },
                {
                    "entity": INVESTIGATIONS.name,
                    "text": "MRI",
                    "attributes": {"MRI_Performed": "Yes"},
                },
                {
                    "entity": "PatientHistory",
                    "text": "ignored",
                    "attributes": {},
                },
            ],
            "predicted_mentions": [
                {
                    "entity": DIAGNOSIS.name,
                    "text": "focal epilepsy",
                    "attributes": {"DiagCategory": "Epilepsy"},
                },
                {
                    "entity": SEIZURE_FREQUENCY.name,
                    "text": "focal seizures",
                    "attributes": {"NumberOfSeizures": "2"},
                },
                {
                    "entity": PRESCRIPTION.name,
                    "text": "lamotrigine 200 mg twice daily",
                    "attributes": {
                        "DrugName": "lamotrigine",
                        "DrugDose": "200",
                        "DoseUnit": "mg",
                        "Frequency": "twice daily",
                    },
                },
                {
                    "entity": INVESTIGATIONS.name,
                    "text": "MRI",
                    "attributes": {"MRI_Performed": "Yes"},
                },
            ],
        }
    ]

    summary = structured.summarize_rows(rows)

    assert summary["scores"]["semantic"]["per_item"]["f1"] == 1.0
    assert set(summary["scores"]["semantic"]["per_entity"]) == set(structured.KEY_ENTITY_NAMES)
    assert summary["clinical_recovery"]["target_headline_f1"] == 0.8
    assert set(summary["clinical_recovery"]["per_entity"]) == set(structured.KEY_ENTITY_NAMES)
    assert summary["clinical_recovery"]["per_entity"][PRESCRIPTION.name]["f1"] == 1.0
    assert summary["clinical_recovery"]["per_entity"][DIAGNOSIS.name]["f1"] == 1.0
    assert summary["clinical_recovery"]["per_entity"][SEIZURE_FREQUENCY.name]["f1"] == 1.0
    assert summary["clinical_recovery"]["per_entity"][INVESTIGATIONS.name]["f1"] == 1.0
    assert summary["n_events_raw"] == 2
    assert summary["diagnostic_ladder"]["source_near"]["overall"]["overlap"]["f1"] == 1.0


def test_write_report_includes_goal_and_diagnostic_ladder(tmp_path) -> None:
    rows = [
        {
            "letter_id": "TEST001",
            "parse_errors": [],
            "n_events_raw": 0,
            "n_mentions_raw": 0,
            "n_mentions_scored": 0,
            "n_evidence_invalid": 0,
            "gold_mentions": [],
            "predicted_mentions": [],
        }
    ]
    report_path = tmp_path / "report.md"

    structured.write_report(
        rows,
        {
            "prompt_version": structured.PROMPT_VERSION,
            "pipeline_family": structured.PIPELINE_FAMILY,
            "split": "dev",
            "model": "test-model",
            "mode": "prompt-only",
            "is_checkpoint": True,
            "total_letters": 140,
        },
        report_path,
        jsonl_path=tmp_path / "rows.jsonl",
    )

    text = report_path.read_text(encoding="utf-8")
    assert "CHECKPOINT ONLY: processed 1 / 140 letters" in text
    assert "Goal item F1" in text
    assert "## Key Clinical-Recovery Headlines" in text
    assert "## Diagnostic Scoring Ladder" in text


def test_runner_auto_path_slug_is_windows_safe() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners import (
        run_llm_only_key_entities_structured as runner,
    )

    path = runner._auto_path(
        "dev",
        "ollama_chat/qwen3.6:35b",
        140,
        "jsonl",
        prompt_profile="qwen_compact",
    )

    assert path.name.startswith(
        "exectv2_llm_only_key_entities_structured_qwen_compact_dev140_qwen3635b_"
    )
    assert ":" not in path.name
