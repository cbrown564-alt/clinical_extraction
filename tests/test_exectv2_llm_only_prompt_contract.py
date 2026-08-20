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
        _LETTER, prompt_version=structured.COMPACT_LEDGER
    )
    leaked = [phrase for phrase in FORBIDDEN_PHRASES if phrase in payload_str]
    assert leaked == []
    payload = json.loads(payload_str)
    assert "prompt_version" not in payload
    assert "clinical_events" in payload["output_schema"]
    assert set(payload["attribute_vocabulary"]) == {
        "medication",
        "diagnosis",
        "seizure_frequency",
        "investigation",
    }


def _prompt_fields_without_letter(payload: dict) -> str:
    return json.dumps(
        {key: value for key, value in payload.items() if key != "letter_text"}
    )


def test_no_prompt_version_mentions_cui() -> None:
    original = structured.PROMPT_VERSION
    versions = [
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
    assert structured.compact_rule_count(payload["clinical_rules"]) == 54
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
    assert list(vocab["medication"]) == [
        "dose",
        "frequency",
        "name",
        "unit",
    ]
    assert vocab["medication"]["dose"] == "Numeric dose only, without the unit."
    assert vocab["medication"]["unit"] == ["g", "mg"]
    assert vocab["medication"]["frequency"] == ["1", "2", "3", "as_required"]
    assert vocab["medication"]["name"] == "Drug name as written."
    assert "DrugDose" not in vocab["medication"]
    assert "DrugName" not in vocab["medication"]
    assert list(vocab["diagnosis"]) == ["DiagCategory"]
    assert vocab["diagnosis"]["DiagCategory"] == [
        "Epilepsy",
        "MultipleSeizures",
        "SingleSeizure",
    ]
    assert "Certainty" not in vocab["diagnosis"]
    assert "Certainty" not in vocab["seizure_frequency"]
    assert "Negation" not in vocab["seizure_frequency"]
    assert vocab["seizure_frequency"]["TimeSince_or_TimeOfEvent"] == [
        "During",
        "Since",
    ]
    assert vocab["seizure_frequency"]["PointInTime"] == [
        "Birthday",
        "DrugChange",
        "LastClinic",
        "Last_Month",
        "Last_Week",
        "Last_Year",
        "Surgery",
    ]
    assert vocab["seizure_frequency"]["FrequencyChange"] == [
        "Decreased",
        "Frequent",
        "Increased",
        "Infrequent",
        "Same",
    ]
    assert vocab["seizure_frequency"]["TimePeriod"] == [
        "Day",
        "Month",
        "Week",
        "Year",
    ]
    assert vocab["seizure_frequency"]["AgeUnit"] == ["Month", "Year"]
    assert set(vocab["investigation"]) == {
        "CT_Performed",
        "CT_Results",
        "EEG_Performed",
        "EEG_Results",
        "MRI_Performed",
        "MRI_Results",
    }

    compact_text = json.dumps(
        {key: value for key, value in payload.items() if key != "letter_text"}
    )
    assert "event_state" not in compact_text
    assert "EEG_Type" not in compact_text
    assert "EEG type" not in compact_text
    assert "Certainty" not in compact_text
    assert "Negation" not in compact_text
    assert '"confidence"' not in compact_text
    assert "rationale" not in compact_text.lower()
    assert "mention text" not in compact_text
    assert "Return only clinical_events" not in compact_text
    assert "Never write 'tonic chronic'" in compact_text
    assert "Keep, reject, split, or merge facts based only" not in compact_text
    assert "Numeric dose only, without the unit." in compact_text
    assert "Write diagnosis fact as only the short syndrome" in compact_text
    assert "frequency='1'" in compact_text
    assert "Frequency='1'" not in compact_text


def test_compact_seizure_rules_keep_prior_wording() -> None:
    payload = json.loads(
        structured.build_prompt_input(
            _LETTER, prompt_version=structured.COMPACT_LEDGER
        )
    )
    sf_rules = " ".join(payload["clinical_rules"]["seizure_frequency"])
    assert payload["categories"]["seizure_frequency"][2] == (
        "qualitative_change: frequent/infrequent/increased/decreased/returned/controlled"
    )
    assert (
        "must include NumberOfSeizures, LowerNumberOfSeizures, "
        "FrequencyChange, TimeSince_or_TimeOfEvent, PointInTime, DayDate, "
        "MonthDate, YearDate, AgeLower, or AgeUpper"
    ) in sf_rules
    assert "NumberOfSeizures='1', YearDate='2014'" in sf_rules
    assert "TimeSince_or_TimeOfEvent='During'" in sf_rules
    assert "TimeSince_or_TimeOfEvent='Since'" in sf_rules
    assert "PointInTime='LastClinic'" in sf_rules
    assert "TimePeriod='Week'" in sf_rules
    assert "FrequencyChange only" in sf_rules
    assert "since period is present" in sf_rules
    assert "since-age time point" in sf_rules
    assert "since, last, date, or drug-change frame" in sf_rules
    assert "count='1'" not in sf_rules
    assert "when='since'" not in sf_rules
    assert "point='last_clinic'" not in sf_rules
    assert "Do not set change='returned'" not in sf_rules


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
    assert structured.compact_rule_count(llm_only["clinical_rules"]) == 52
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


def test_paper_names_are_aliases_of_compact() -> None:
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


def test_compact_format_retry_schema_is_flat_fact_events() -> None:
    schema = structured.format_retry_schema_for(structured.COMPACT_LEDGER)
    event = schema["$defs"]["CompactClinicalEvent"]["properties"]
    assert list(event) == ["family", "evidence", "fact", "attributes"]
    assert "anchor_text" not in event
    assert "mentions" not in event
    assert "confidence" not in event
    assert "rationale" not in event
