"""Governing contract for the ExECT mention-unit v2 research lane.

Both methods copy a clinical name from the letter. llm leftover words go
in the number fields. Hybrid leftover words stay in evidence. Hybrid may
rewrite that item only. It may not search the letter.
"""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.mention_unit import (
    COMBO_ARM_VERSIONS,
    CUE5_ARM_VERSIONS,
    HYBRID_METHOD,
    LLM_METHOD,
    MENTION_UNIT_PROMPT_VERSION,
    MentionUnitExtractor,
    build_mention_unit_prompt,
    materialize_mention_unit,
    mention_unit_prompt_version,
    parse_mention_unit_json,
)

_BANNED_PROMPT_TERMS = (
    "gold",
    "prompt_version",
    "letter_id",
    "scorer",
    "benchmark",
    "frozen",
    "control",
    "gan",
    "list 2",
    "list 9",
    "list 11",
    "named type not generic",
    "most specific",
    "cui",
    "markup",
    "umls",
    "mention",
    "span",
    "coding fields",
    "this method",
    "return only",
)
_CURRENT_SCOPE_FAMILIES = ("Diagnosis", "SeizureFrequency", "Investigations")
_FROZEN_CUE5 = (
    "List every frequency statement, including past ones: a rate, a dated "
    "count, a last event, a change, or a seizure-free duration. The "
    "clinical name may be seizures, a named type, absences, or myoclonic "
    "jerks. Do not use events, episodes, or slang. Do not list a seizure "
    "story that has no frequency."
)
_CUE5_SUFFIXES = {
    "heading": (
        "A heading that states a rate or dated count is a frequency "
        "statement. Do not replace it with a later vague estimate."
    ),
    "bare_frame": (
        "A seizure-free line, or a line that only says the seizures are "
        "well managed, needs a seizure type or a time frame. Leave it out "
        "if it has neither."
    ),
    "one_row": (
        "One frequency statement is one row. Do not list both seizures and "
        "a named type for the same count."
    ),
    "no_join": (
        "If two types share one count, write the type the count belongs to. "
        "Do not join them as one name."
    ),
}


def _letter(note: str, letter_id: str = "EA0002") -> ExectLetter:
    return ExectLetter(letter_id=letter_id, note_text=note)


def _payload_without_letter(method: str) -> dict[str, object]:
    letter = _letter("She takes lamotrigine 100 mg daily.")
    payload = json.loads(build_mention_unit_prompt(letter, method=method))
    return {key: value for key, value in payload.items() if key != "letter_text"}


def test_prompt_version_is_mention_unit_v2() -> None:
    assert MENTION_UNIT_PROMPT_VERSION == "exectv2_mention_unit_v2"


def test_prompt_uses_clinical_name_and_keeps_metadata_out() -> None:
    llm = _payload_without_letter(LLM_METHOD)
    hybrid = _payload_without_letter(HYBRID_METHOD)

    assert list(llm) == [
        "task",
        "output_schema",
        "form_table",
        "selection_cues",
        "closed_values",
    ]
    assert list(hybrid) == ["task", "output_schema", "selection_cues"]
    serialized = json.dumps(llm).lower()
    assert MENTION_UNIT_PROMPT_VERSION not in serialized
    for term in _BANNED_PROMPT_TERMS:
        assert term not in serialized
    assert "clinical name" in str(llm["task"]).lower()
    assert "clinical family" in str(llm["task"]).lower()
    assert "clinical_name" in json.dumps(llm["output_schema"]).lower()
    assert "clinical_family" in json.dumps(llm["output_schema"]).lower()
    assert '"text"' not in json.dumps(llm["output_schema"]).lower()
    assert '"family"' not in json.dumps(llm["output_schema"]).lower()
    assert "period_count" in json.dumps(llm["output_schema"]).lower()
    assert "every 3 weeks" in json.dumps(llm["form_table"]).lower()
    assert "attributes" not in json.dumps(hybrid["output_schema"]).lower()
    assert "count" not in json.dumps(hybrid["output_schema"]).lower()
    assert "form_table" not in hybrid
    assert "stay in evidence" in str(hybrid["task"]).lower()
    assert len(llm["selection_cues"]) == 7


def test_current_is_only_on_prescription_and_system_line() -> None:
    llm = _payload_without_letter(LLM_METHOD)
    task = str(llm["task"])
    cues = list(llm["selection_cues"])
    for family in _CURRENT_SCOPE_FAMILIES:
        start = task.index(f"{family}:")
        end = task.index("\n", start)
        assert "current" not in task[start:end].lower()
    schema_items = llm["output_schema"]["items"]
    assert isinstance(schema_items, list)
    for item in schema_items:
        assert isinstance(item, dict)
        family = str(item.get("clinical_family", ""))
        if family in _CURRENT_SCOPE_FAMILIES:
            assert "current" not in json.dumps(item).lower()
    assert "current" not in json.dumps(llm["form_table"]).lower()
    assert sum("current" in str(cue).lower() for cue in cues) == 1
    assert "current anti-seizure" in str(cues[6]).lower()


def test_frozen_v2_cue5_is_unchanged() -> None:
    llm = _payload_without_letter(LLM_METHOD)
    hybrid = _payload_without_letter(HYBRID_METHOD)
    assert llm["selection_cues"][4] == _FROZEN_CUE5
    assert hybrid["selection_cues"][4] == _FROZEN_CUE5
    assert MENTION_UNIT_PROMPT_VERSION == "exectv2_mention_unit_v2"


def test_cue5_study_arms_append_one_sentence_and_keep_seven_cues() -> None:
    letter = _letter("She takes lamotrigine 100 mg daily.")
    assert tuple(CUE5_ARM_VERSIONS) == ("heading", "bare_frame", "one_row", "no_join")
    for arm, suffix in _CUE5_SUFFIXES.items():
        llm = json.loads(build_mention_unit_prompt(letter, method=LLM_METHOD, cue5_arm=arm))
        hybrid = json.loads(
            build_mention_unit_prompt(letter, method=HYBRID_METHOD, cue5_arm=arm)
        )
        assert len(llm["selection_cues"]) == 7
        assert llm["selection_cues"][4] == f"{_FROZEN_CUE5} {suffix}"
        assert hybrid["selection_cues"][4] == llm["selection_cues"][4]
        frozen = list(_payload_without_letter(LLM_METHOD)["selection_cues"])
        assert llm["selection_cues"][:4] == frozen[:4]
        assert llm["selection_cues"][5:] == frozen[5:]
        serialized = json.dumps(
            {key: value for key, value in llm.items() if key != "letter_text"}
        ).lower()
        for term in _BANNED_PROMPT_TERMS:
            assert term not in serialized
        assert "current" not in llm["selection_cues"][4].lower()
        assert CUE5_ARM_VERSIONS[arm] == f"exectv2_mention_unit_v2_cue5_{arm}"


def test_combo_scaffold_adds_cheap_stack_rows_and_keeps_frozen_v2() -> None:
    letter = _letter(
        "She takes lamotrigine 100 mg daily. She has two seizures a week."
    )
    cheap = json.loads(
        structured.build_prompt_input(
            letter,
            prompt_version=structured.PROMPT_VERSION_V0_9_40_DROP_ENCODING_NON_SF_ALL_EXAMPLES,
        )
    )
    frozen_llm = json.loads(build_mention_unit_prompt(letter, method=LLM_METHOD))
    frozen_hybrid = json.loads(build_mention_unit_prompt(letter, method=HYBRID_METHOD))
    llm = json.loads(
        build_mention_unit_prompt(letter, method=LLM_METHOD, combo_arm="scaffold")
    )
    hybrid = json.loads(
        build_mention_unit_prompt(letter, method=HYBRID_METHOD, combo_arm="scaffold")
    )

    assert mention_unit_prompt_version() == MENTION_UNIT_PROMPT_VERSION
    assert mention_unit_prompt_version(combo_arm="scaffold") == (
        "exectv2_mention_unit_v2_combo_scaffold"
    )
    assert COMBO_ARM_VERSIONS["scaffold"] == "exectv2_mention_unit_v2_combo_scaffold"
    assert list(frozen_llm) == [
        "task",
        "output_schema",
        "form_table",
        "selection_cues",
        "closed_values",
        "letter_text",
    ]
    assert list(llm) == [
        "task",
        "output_schema",
        "form_table",
        "selection_cues",
        "closed_values",
        "suggested_evidence",
        "letter_text",
    ]
    assert list(hybrid) == [
        "task",
        "output_schema",
        "selection_cues",
        "suggested_evidence",
        "letter_text",
    ]
    assert llm["task"] == frozen_llm["task"]
    assert llm["output_schema"] == frozen_llm["output_schema"]
    assert llm["selection_cues"] == frozen_llm["selection_cues"]
    assert hybrid["task"] == frozen_hybrid["task"]
    assert hybrid["output_schema"] == frozen_hybrid["output_schema"]
    assert hybrid["selection_cues"] == frozen_hybrid["selection_cues"]
    assert llm["suggested_evidence"] == cheap["suggested_evidence"]
    assert hybrid["suggested_evidence"] == cheap["suggested_evidence"]
    assert llm["suggested_evidence"]
    assert set(llm["suggested_evidence"][0]) == {
        "family",
        "evidence",
        "name_hint",
        "category",
    }
    serialized = json.dumps(
        {key: value for key, value in llm.items() if key != "letter_text"}
    ).lower()
    for term in _BANNED_PROMPT_TERMS:
        assert term not in serialized
    assert "candidate_id" not in serialized
    assert "lane_hint" not in serialized
    assert "anchor_hint" not in serialized
    assert "architecture" not in serialized


def test_combo_scaffold_cannot_stack_with_cue5() -> None:
    letter = _letter("She takes lamotrigine 100 mg daily.")
    try:
        build_mention_unit_prompt(
            letter, method=HYBRID_METHOD, cue5_arm="heading", combo_arm="scaffold"
        )
    except ValueError as exc:
        assert "cannot be combined" in str(exc)
    else:
        raise AssertionError("cue5 and combo_scaffold stacked")


def test_combo_form_guide_adds_llm_form_table_to_hybrid_without_coding_fields() -> None:
    letter = _letter("She has two seizures a week.")
    frozen_llm = json.loads(build_mention_unit_prompt(letter, method=LLM_METHOD))
    frozen_hybrid = json.loads(build_mention_unit_prompt(letter, method=HYBRID_METHOD))
    llm = json.loads(
        build_mention_unit_prompt(letter, method=LLM_METHOD, combo_arm="form_guide")
    )
    hybrid = json.loads(
        build_mention_unit_prompt(letter, method=HYBRID_METHOD, combo_arm="form_guide")
    )

    assert mention_unit_prompt_version() == MENTION_UNIT_PROMPT_VERSION
    assert mention_unit_prompt_version(combo_arm="form_guide") == (
        "exectv2_mention_unit_v2_combo_form_guide"
    )
    assert COMBO_ARM_VERSIONS == {
        "scaffold": "exectv2_mention_unit_v2_combo_scaffold",
        "form_guide": "exectv2_mention_unit_v2_combo_form_guide",
    }
    assert list(hybrid) == [
        "task",
        "output_schema",
        "form_table",
        "selection_cues",
        "letter_text",
    ]
    assert hybrid["form_table"] == frozen_llm["form_table"]
    assert len(hybrid["form_table"]) == 8
    assert hybrid["output_schema"] == frozen_hybrid["output_schema"]
    assert hybrid["selection_cues"] == frozen_hybrid["selection_cues"]
    assert "count" not in json.dumps(hybrid["output_schema"]).lower()
    assert "attributes" not in json.dumps(hybrid["output_schema"]).lower()
    assert "closed_values" not in hybrid
    assert "stay in evidence" in str(hybrid["task"]).lower()
    assert "use the form table" in str(hybrid["task"]).lower()
    assert "leftover" in str(hybrid["task"]).lower()
    assert llm["form_table"] == frozen_llm["form_table"]
    assert llm["output_schema"] == frozen_llm["output_schema"]
    assert llm["selection_cues"] == frozen_llm["selection_cues"]
    assert llm["task"] == frozen_llm["task"]
    assert "form_table" not in frozen_hybrid
    serialized = json.dumps(
        {key: value for key, value in hybrid.items() if key != "letter_text"}
    ).lower()
    for term in _BANNED_PROMPT_TERMS:
        assert term not in serialized


def test_combo_form_guide_cannot_stack_with_cue5() -> None:
    letter = _letter("She takes lamotrigine 100 mg daily.")
    try:
        build_mention_unit_prompt(
            letter, method=HYBRID_METHOD, cue5_arm="heading", combo_arm="form_guide"
        )
    except ValueError as exc:
        assert "cannot be combined" in str(exc)
    else:
        raise AssertionError("cue5 and combo_form_guide stacked")


def test_rendered_payload_stays_plain_and_forbids_v1_jargon() -> None:
    letter = _letter("She takes lamotrigine 100 mg daily.")
    prompt = build_mention_unit_prompt(letter, method=LLM_METHOD)
    messages = MentionUnitExtractor(method=LLM_METHOD).render_messages(
        prompt_input_json=prompt
    )
    rendered = json.dumps(messages).lower()
    assert messages[0]["role"] == "system"
    assert "current medicine" in str(messages[0]["content"]).lower()
    for term in _BANNED_PROMPT_TERMS:
        assert term not in rendered


def test_hybrid_parser_rejects_coding_fields() -> None:
    raw = json.dumps(
        {
            "items": [
                {
                    "clinical_family": "Prescription",
                    "clinical_name": "lamotrigine",
                    "evidence": "She takes lamotrigine 100 mg daily.",
                    "dose": "100",
                }
            ]
        }
    )

    result = parse_mention_unit_json(raw, method=HYBRID_METHOD)

    assert result.record is not None
    assert result.record.items[0].text == "lamotrigine"
    assert result.record.items[0].attributes == {}
    assert result.forbidden_fields == [{"item_index": 0, "fields": ["dose"]}]
    assert any("forbidden_model_fields" in error for error in result.errors)


def test_llm_parser_keeps_period_count_and_drops_unused_keys() -> None:
    raw = json.dumps(
        {
            "items": [
                {
                    "clinical_family": "SeizureFrequency",
                    "clinical_name": "seizures",
                    "evidence": "She has a seizure every 3 weeks.",
                    "count": 1,
                    "period_count": 3,
                    "period": "week",
                    "type": "focal",
                }
            ]
        }
    )

    result = parse_mention_unit_json(raw, method=LLM_METHOD)

    assert result.record is not None
    assert result.record.items[0].text == "seizures"
    assert result.record.items[0].attributes["count"] == "1"
    assert result.record.items[0].attributes["period_count"] == "3"
    assert result.record.items[0].attributes["period"] == "week"
    assert "type" not in result.record.items[0].attributes
    assert any("dropped_unused_keys" in error for error in result.errors)


def test_llm_uses_clinical_name_and_maps_period_count() -> None:
    letter = _letter("She has a seizure every 3 weeks.")
    raw = json.dumps(
        {
            "items": [
                {
                    "clinical_family": "SeizureFrequency",
                    "clinical_name": "seizure",
                    "evidence": "She has a seizure every 3 weeks.",
                    "count": "1",
                    "period_count": "3",
                    "period": "week",
                }
            ]
        }
    )
    parsed = parse_mention_unit_json(raw, method=LLM_METHOD)
    assert parsed.record is not None

    result = materialize_mention_unit(letter, parsed.record, method=LLM_METHOD)

    assert result.prediction.mentions[0].text == "seizure"
    assert result.prediction.mentions[0].attributes["NumberOfSeizures"] == "1"
    assert result.prediction.mentions[0].attributes["NumberOfTimePeriods"] == "3"
    assert result.prediction.mentions[0].attributes["TimePeriod"] == "Week"
    assert result.prediction.mentions[0].component_owner == "model.mention_unit"


def test_hybrid_does_not_search_the_letter_or_explode_a_rate() -> None:
    letter = _letter(
        "She has epilepsy. She takes lamotrigine 100 mg daily. "
        "MRI was normal. In March she had 2 to 3 of her focal seizures."
    )
    raw = json.dumps(
        {
            "items": [
                {
                    "clinical_family": "Prescription",
                    "clinical_name": "lamotrigine",
                    "evidence": "She takes lamotrigine 100 mg daily.",
                }
            ]
        }
    )
    parsed = parse_mention_unit_json(raw, method=HYBRID_METHOD)
    assert parsed.record is not None

    result = materialize_mention_unit(letter, parsed.record, method=HYBRID_METHOD)

    assert [mention.entity for mention in result.prediction.mentions] == ["Prescription"]
    assert result.prediction.mentions[0].attributes["DrugName"] == "lamotrigine"
    assert all("MRI" not in str(trace.get("after", {})) for trace in result.rule_trace)
    assert all(trace.get("action") != "dual_family_reuse" for trace in result.rule_trace)
    assert all("trust_item" not in str(trace.get("action", "")) for trace in result.rule_trace)


def test_hybrid_splits_a_heading_but_does_not_add_later_letter_types() -> None:
    letter = _letter(
        "Diagnosis: focal epilepsy-Probable temporal. "
        "In March she had 2 to 3 of her focal seizures. "
        "four secondary generalised seizures."
    )
    raw = json.dumps(
        {
            "items": [
                {
                    "clinical_family": "Diagnosis",
                    "clinical_name": "focal epilepsy-Probable temporal",
                    "evidence": "Diagnosis: focal epilepsy-Probable temporal.",
                }
            ]
        }
    )
    parsed = parse_mention_unit_json(raw, method=HYBRID_METHOD)
    assert parsed.record is not None

    result = materialize_mention_unit(letter, parsed.record, method=HYBRID_METHOD)

    texts = sorted(mention.text.lower() for mention in result.prediction.mentions)
    entities = {mention.entity for mention in result.prediction.mentions}
    assert entities == {"Diagnosis"}
    assert texts == ["focal epilepsy", "temporal lobe epilepsy"]
    assert any(trace.get("action") == "convention_split_heading" for trace in result.rule_trace)
    assert all("secondary" not in text for text in texts)


def test_hybrid_uses_landed_encoder_on_clinical_name_and_evidence() -> None:
    letter = _letter(
        "Last seizures in teenage years. ECG was normal. EEG in 2012 was normal. "
        "She has a seizure every 3 weeks."
    )
    raw = json.dumps(
        {
            "items": [
                {
                    "clinical_family": "SeizureFrequency",
                    "clinical_name": "seizures",
                    "evidence": "Last seizures in teenage years.",
                },
                {
                    "clinical_family": "SeizureFrequency",
                    "clinical_name": "seizure",
                    "evidence": "She has a seizure every 3 weeks.",
                },
                {
                    "clinical_family": "Investigations",
                    "clinical_name": "ECG",
                    "evidence": "ECG was normal.",
                },
                {
                    "clinical_family": "Investigations",
                    "clinical_name": "EEG",
                    "evidence": "EEG in 2012 was normal.",
                },
            ]
        }
    )
    parsed = parse_mention_unit_json(raw, method=HYBRID_METHOD)
    assert parsed.record is not None

    result = materialize_mention_unit(letter, parsed.record, method=HYBRID_METHOD)

    by_text = {mention.text: mention for mention in result.prediction.mentions}
    assert "ECG" not in by_text
    assert by_text["seizures"].attributes["NumberOfSeizures"] == "0"
    assert by_text["seizure"].attributes["NumberOfSeizures"] == "1"
    assert by_text["seizure"].attributes["NumberOfTimePeriods"] == "3"
    assert by_text["seizure"].attributes["TimePeriod"] == "Week"
    assert by_text["EEG"].entity == "Investigations"
    assert all("trust_item" not in str(trace.get("action", "")) for trace in result.rule_trace)
    assert all("leftover_form" not in str(trace.get("action", "")) for trace in result.rule_trace)
    assert any(
        "encoding." in str(trace.get("action", "")) or "encoding." in str(trace.get("rule_id", ""))
        for trace in result.rule_trace
    )
