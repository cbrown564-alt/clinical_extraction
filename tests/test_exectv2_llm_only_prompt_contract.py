"""Invariant-focused tests for exectv2 llm only prompt contract."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines import (
    key_entities_structured as structured_pkg,
)
from tests.helpers.prompt_hygiene import FORBIDDEN_PHRASES

_NOTE = (
    "She has focal epilepsy with 2 focal seizures per month. "
    "Current treatment is lamotrigine 200 mg twice daily. "
    "MRI brain was normal; sleep-deprived EEG showed sharp waves."
)

_LETTER = ExectLetter(letter_id="TEST001", note_text=_NOTE)


def test_prompt_hygiene_and_four_family_schema() -> None:
    payload_str = structured.build_prompt_input(
        _LETTER, prompt_version=structured.FULL_LEDGER
    )
    leaked = [phrase for phrase in FORBIDDEN_PHRASES if phrase in payload_str]
    assert leaked == []

    payload = json.loads(payload_str)
    assert payload["prompt_version"] == structured.FULL_LEDGER
    assert set(payload["attribute_vocabulary"]) == {
        PRESCRIPTION.name,
        DIAGNOSIS.name,
        SEIZURE_FREQUENCY.name,
        INVESTIGATIONS.name,
    }
    assert "clinical_events" in payload["output_schema"]
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



def _prompt_fields_without_letter(payload: dict) -> str:
    return json.dumps(
        {key: value for key, value in payload.items() if key != "letter_text"}
    )


def test_no_prompt_version_mentions_cui() -> None:
    original = structured.PROMPT_VERSION
    versions = [
        structured.FULL_LEDGER,
        structured.EXECT_FULL_LEDGER,
        structured.COMPACT_LEDGER,
        structured.EXECT_LLM_WITH_RULES,
        structured.EXECT_LLM_ONLY,
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
    finally:
        structured.set_active_prompt_version(original)

    assert structured.PROMPT_VERSION == structured.COMPACT_LEDGER


def test_compact_prompt_is_authored_in_one_file() -> None:
    source = Path(structured_pkg.__file__).with_name("prompt_compact.py").read_text()
    assert "from .prompt_rules_full" not in source
    assert "from .prompt_plain_language" not in source
    assert "_event_lane_guide" not in source
    assert "_attribute_vocabulary" not in source
    assert "_clinical_rules" not in source
    assert "_clean_rule_text" not in source


def test_compact_is_authored_as_compact() -> None:
    payload = json.loads(
        structured.build_prompt_input(
            _LETTER, prompt_version=structured.COMPACT_LEDGER
        )
    )
    assert list(payload) == list(structured.COMPACT_AUTHORED_KEYS)
    assert "architecture" not in payload
    assert "worked_examples" not in payload
    assert "letter_id" not in payload
    assert "prompt_version" not in payload
    assert "candidate_evidence_ledger" not in payload
    assert "event_lane_guide" not in payload
    assert list(payload["clinical_rules"]) == [
        "suggested_evidence",
        *structured.SHARED_RULE_SECTION_KEYS,
    ]
    assert structured.compact_rule_count(payload["clinical_rules"]) == 52
    assert payload["task"].startswith(
        "Read the clinical letter once. Use the suggested evidence"
    )
    assert payload["suggested_evidence"]
    assert "medication" in payload["categories"]


def test_compact_schema_is_flat_fact_events() -> None:
    payload = json.loads(
        structured.build_prompt_input(
            _LETTER, prompt_version=structured.COMPACT_LEDGER
        )
    )
    event_schema = payload["output_schema"]["clinical_events"][0]
    assert list(event_schema) == ["family", "evidence", "fact", "attributes"]
    assert event_schema["family"] == (
        "medication | diagnosis | seizure_frequency | investigation"
    )
    assert "mentions" not in event_schema
    assert "anchor_text" not in event_schema
    assert "event_state" not in event_schema
    assert "confidence" not in event_schema
    assert "rationale" not in event_schema

    vocab = payload["attribute_vocabulary"]
    assert list(vocab) == [
        "medication",
        "diagnosis",
        "seizure_frequency",
        "investigation",
    ]
    assert list(vocab["medication"]) == ["name", "dose", "unit", "frequency"]
    assert "g or mg" in vocab["medication"]["unit"]
    assert vocab["medication"]["frequency"] == ["1", "2", "3", "as_required"]
    assert "multiple_seizures" in vocab["diagnosis"]["category"]
    assert "Certainty" not in vocab["diagnosis"]
    assert "Negation" not in vocab["seizure_frequency"]
    assert set(vocab["seizure_frequency"]) == {
        "age_lower",
        "age_unit",
        "age_upper",
        "change",
        "count",
        "count_lower",
        "count_upper",
        "day",
        "month",
        "period",
        "periods",
        "periods_lower",
        "periods_upper",
        "point",
        "when",
        "year",
    }
    assert vocab["seizure_frequency"]["when"] == ["during", "since"]
    assert vocab["seizure_frequency"]["point"] == [
        "birthday",
        "drug_change",
        "last_clinic",
        "last_month",
        "last_week",
        "last_year",
        "surgery",
    ]
    assert vocab["seizure_frequency"]["change"] == [
        "decreased",
        "frequent",
        "increased",
        "infrequent",
        "same",
    ]
    assert vocab["seizure_frequency"]["period"] == ["day", "week", "month", "year"]
    assert vocab["seizure_frequency"]["age_unit"] == ["month", "year"]
    assert set(vocab["investigation"]) == {
        "eeg_performed",
        "eeg_result",
        "mri_performed",
        "mri_result",
    }

    compact_text = json.dumps(
        {key: value for key, value in payload.items() if key != "letter_text"}
    )
    assert "event_state" not in compact_text
    assert "EEG_Type" not in compact_text
    assert "EEG type" not in compact_text
    assert "CT_Performed" not in compact_text
    assert "Certainty" not in compact_text
    assert "Negation" not in compact_text
    assert '"confidence"' not in compact_text
    assert "rationale" not in compact_text.lower()
    assert "mention text" not in compact_text
    assert "Return only clinical_events" not in compact_text
    assert "Prescription" not in compact_text
    assert "string copied from the letter" not in compact_text
    assert "tonic chronic" not in compact_text
    assert "Keep, reject, split, or merge facts based only" not in compact_text


def test_compact_seizure_rules_use_field_names() -> None:
    payload = json.loads(
        structured.build_prompt_input(
            _LETTER, prompt_version=structured.COMPACT_LEDGER
        )
    )
    sf_rules = " ".join(payload["clinical_rules"]["seizure_frequency"])
    assert payload["categories"]["seizure_frequency"][2] == (
        "qualitative_change: decreased, frequent, increased, infrequent, or same"
    )
    assert (
        "must include count, count_lower, count_upper, change, "
        "day, month, year, age_lower, or age_upper"
    ) in sf_rules
    assert "when, point, and period are not enough on their own" in sf_rules
    assert "Do not set change='returned'" in sf_rules
    assert "count='0', when='since'" in sf_rules
    assert "Do not use point for age" in sf_rules
    assert "when='since' with a day, month, year, or point" in sf_rules
    assert "Do not set change from 'well controlled'" in sf_rules
    assert "since period" not in sf_rules
    assert "since-age" not in sf_rules
    assert "time point" not in sf_rules
    assert "drug-change" not in sf_rules
    assert "active-rate" not in sf_rules


def test_compact_llm_only_omits_suggested_evidence() -> None:
    compact = json.loads(
        structured.build_prompt_input(
            _LETTER, prompt_version=structured.COMPACT_LEDGER
        )
    )
    llm_only = json.loads(
        structured.build_prompt_input(
            _LETTER, prompt_version=structured.EXECT_LLM_ONLY
        )
    )
    assert list(llm_only) == list(structured.LLM_ONLY_AUTHORED_KEYS)
    assert "suggested_evidence" not in llm_only
    assert "suggested" not in json.dumps(
        {key: value for key, value in llm_only.items() if key != "letter_text"}
    ).lower()
    assert llm_only["output_schema"] == compact["output_schema"]
    assert llm_only["attribute_vocabulary"] == compact["attribute_vocabulary"]
    assert llm_only["family_guidance"] == compact["family_guidance"]
    assert "categories" not in llm_only
    assert list(llm_only["clinical_rules"]) == list(structured.SHARED_RULE_SECTION_KEYS)
    assert llm_only["clinical_rules"] == {
        key: compact["clinical_rules"][key] for key in structured.SHARED_RULE_SECTION_KEYS
    }
    assert compact["clinical_rules"]["suggested_evidence"][0].startswith(
        "First classify each suggested-evidence row"
    )
    assert llm_only["task"].startswith("Read the clinical letter once. List the")
    assert all(
        "Keep, reject, split" not in step for step in llm_only["decision_procedure"]
    )


def test_full_is_authored_as_full() -> None:
    payload = json.loads(
        structured.build_prompt_input(_LETTER, prompt_version=structured.FULL_LEDGER)
    )
    assert payload["prompt_version"] == structured.FULL_LEDGER
    assert payload["letter_id"] == _LETTER.letter_id
    assert payload["architecture"]
    assert payload["worked_examples"]
    assert payload["candidate_evidence_ledger"]
    assert payload["event_lane_guide"]
    assert "suggested_evidence" not in payload
    assert "categories" not in payload
    assert len(payload["clinical_rules"]) == 83


def test_paper_names_are_aliases_of_compact_and_full() -> None:
    compact = json.loads(
        structured.build_prompt_input(
            _LETTER, prompt_version=structured.COMPACT_LEDGER
        )
    )
    paper_compact = json.loads(
        structured.build_prompt_input(
            _LETTER, prompt_version=structured.EXECT_LLM_WITH_RULES
        )
    )
    assert compact == paper_compact

    full = json.loads(
        structured.build_prompt_input(_LETTER, prompt_version=structured.FULL_LEDGER)
    )
    paper_full = json.loads(
        structured.build_prompt_input(
            _LETTER, prompt_version=structured.EXECT_FULL_LEDGER
        )
    )
    full.pop("prompt_version")
    paper_full.pop("prompt_version")
    assert full == paper_full


@pytest.mark.parametrize(
    "version",
    (
        "exectv2_hybrid_key_family_event_ledger_v0.9.24",
        "exectv2_hybrid_key_family_event_ledger_v0.9.40_drop_encoding_non_sf_all_examples",
        "exectv2_hybrid_key_family_event_ledger_v0.9.41_cheap_drop_ix_pending_repeat",
        "exectv2_hybrid_key_family_event_ledger_v0.9.42_cheap_drop_scaffold_reprint",
        "exectv2_hybrid_key_family_event_ledger_v0.9.43_cheap_collapse_refuse",
        "exectv2_hybrid_key_family_event_ledger_v0.9.44_cheap_stack_further_prunes",
        "exectv2_hybrid_key_family_event_ledger_v0.9.40_combo_clinical_name",
        "exectv2_full_ledger_drop_examples",
        "exectv2_full_ledger_drop_encoding_non_sf",
        "exectv2_compact_ledger_further_prune",
        "exectv2_compact_ledger_plus_encoding",
        "exectv2_compact_ledger_plus_encoding_examples",
    ),
)
def test_build_prompt_input_rejects_deleted_dump_and_prune_versions(
    version: str,
) -> None:
    with pytest.raises(ValueError, match="unsupported prompt version"):
        structured.build_prompt_input(_LETTER, prompt_version=version)


def test_format_retry_schema_is_canonical_structured_record() -> None:
    schema = structured.format_retry_schema_for(structured.FULL_LEDGER)
    assert "StructuredClinicalEvent" in schema.get("$defs", {})
    assert "V26ClinicalEventRecord" not in schema.get("$defs", {})


def test_compact_format_retry_schema_is_flat_fact_events() -> None:
    schema = structured.format_retry_schema_for(structured.COMPACT_LEDGER)
    event = schema["$defs"]["CompactClinicalEvent"]["properties"]
    assert list(event) == ["family", "evidence", "fact", "attributes"]
    assert "anchor_text" not in event
    assert "mentions" not in event
    assert "confidence" not in event
    assert "rationale" not in event
