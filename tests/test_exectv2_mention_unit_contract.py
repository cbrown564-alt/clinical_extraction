"""Governing contract for the ExECT mention-unit v1 research lane.

This lane asks both methods for exact letter spans. Hybrid may rewrite
that item only. It may not search the letter or explode one sentence
into a mention set.
"""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.mention_unit import (
    HYBRID_METHOD,
    LLM_METHOD,
    MENTION_UNIT_PROMPT_VERSION,
    MentionUnitExtractor,
    build_mention_unit_prompt,
    materialize_mention_unit,
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
)


def _letter(note: str, letter_id: str = "EA0002") -> ExectLetter:
    return ExectLetter(letter_id=letter_id, note_text=note)


def test_prompt_version_is_mention_unit_v1() -> None:
    assert MENTION_UNIT_PROMPT_VERSION == "exectv2_mention_unit_v1"


def test_prompt_asks_for_spans_and_keeps_metadata_out() -> None:
    letter = _letter("Current medication: lamotrigine 100 mg daily.")

    llm = json.loads(build_mention_unit_prompt(letter, method=LLM_METHOD))
    hybrid = json.loads(build_mention_unit_prompt(letter, method=HYBRID_METHOD))

    assert list(llm) == ["task", "output_schema", "family_guidance", "letter_text"]
    assert list(hybrid) == ["task", "output_schema", "family_guidance", "letter_text"]
    serialized = json.dumps({key: value for key, value in llm.items() if key != "letter_text"})
    assert MENTION_UNIT_PROMPT_VERSION not in serialized
    lowered = serialized.lower()
    for term in _BANNED_PROMPT_TERMS:
        assert term not in lowered
    assert "exact" in llm["task"].lower()
    assert "span" in llm["task"].lower()
    assert "ordinary language" not in lowered
    assert '"event"' not in json.dumps(llm["output_schema"]).lower()
    assert "attributes" not in json.dumps(hybrid["output_schema"]).lower()
    assert "count" not in json.dumps(hybrid["output_schema"]).lower()
    llm_schema = json.dumps(llm["output_schema"]).lower()
    assert "certainty" in llm_schema
    assert "count" in llm_schema
    assert "concept" not in llm_schema
    assert '"type"' not in llm_schema
    assert '"name"' not in llm_schema
    guidance = json.dumps(llm["family_guidance"]).lower()
    assert "absences" in guidance
    assert "driving" in guidance
    assert "slang" in guidance
    assert "result" in guidance
    assert "same dose" in guidance


def test_rendered_payload_stays_plain_and_metadata_free() -> None:
    letter = _letter("Current medication: lamotrigine 100 mg daily.")
    prompt = build_mention_unit_prompt(letter, method=LLM_METHOD)
    messages = MentionUnitExtractor(method=LLM_METHOD).render_messages(
        prompt_input_json=prompt
    )
    rendered = json.dumps(messages).lower()
    assert messages[0]["role"] == "system"
    assert "span" in str(messages[0]["content"]).lower()
    for term in _BANNED_PROMPT_TERMS:
        assert term not in rendered


def test_hybrid_parser_rejects_coding_fields() -> None:
    raw = json.dumps(
        {
            "items": [
                {
                    "family": "Prescription",
                    "text": "lamotrigine",
                    "evidence": "Current medication: lamotrigine 100 mg daily.",
                    "dose": "100",
                }
            ]
        }
    )

    result = parse_mention_unit_json(raw, method=HYBRID_METHOD)

    assert result.record is not None
    assert result.record.items[0].attributes == {}
    assert result.forbidden_fields == [{"item_index": 0, "fields": ["dose"]}]
    assert any("forbidden_model_fields" in error for error in result.errors)


def test_llm_parser_keeps_only_family_coding_fields() -> None:
    raw = json.dumps(
        {
            "items": [
                {
                    "family": "SeizureFrequency",
                    "text": "focal seizures",
                    "evidence": "She had 2 to 3 focal seizures in March.",
                    "count": 4,
                    "lower_count": 2,
                    "upper_count": 3,
                    "type": "focal",
                    "concept": "focal seizures",
                }
            ]
        }
    )

    result = parse_mention_unit_json(raw, method=LLM_METHOD)

    assert result.record is not None
    assert result.record.items[0].text == "focal seizures"
    assert result.record.items[0].attributes["lower_count"] == "2"
    assert result.record.items[0].attributes["upper_count"] == "3"
    assert "type" not in result.record.items[0].attributes
    assert "concept" not in result.record.items[0].attributes
    assert any("dropped_unused_keys" in error for error in result.errors)


def test_llm_uses_emitted_span_not_a_type_label() -> None:
    letter = _letter("She had 2 to 3 focal seizures in March without change in awareness.")
    raw = json.dumps(
        {
            "items": [
                {
                    "family": "SeizureFrequency",
                    "text": "focal seizures",
                    "evidence": (
                        "She had 2 to 3 focal seizures in March without change in awareness."
                    ),
                    "lower_count": "2",
                    "upper_count": "3",
                }
            ]
        }
    )
    parsed = parse_mention_unit_json(raw, method=LLM_METHOD)
    assert parsed.record is not None

    result = materialize_mention_unit(letter, parsed.record, method=LLM_METHOD)

    assert result.prediction.mentions[0].text == "focal seizures"
    assert result.prediction.mentions[0].attributes["LowerNumberOfSeizures"] == "2"
    assert result.prediction.mentions[0].component_owner == "model.mention_unit"


def test_hybrid_does_not_search_the_letter_or_explode_a_rate() -> None:
    letter = _letter(
        "She has epilepsy. Current medication: lamotrigine 100 mg daily. "
        "MRI was normal. In March she had 2 to 3 of her focal seizures."
    )
    raw = json.dumps(
        {
            "items": [
                {
                    "family": "Prescription",
                    "text": "lamotrigine",
                    "evidence": "Current medication: lamotrigine 100 mg daily.",
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
                    "family": "Diagnosis",
                    "text": "focal epilepsy-Probable temporal",
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


def test_hybrid_suppresses_ecg_and_keeps_last_event_zero() -> None:
    letter = _letter("Last seizures in teenage years. ECG was normal. EEG in 2012 was normal.")
    raw = json.dumps(
        {
            "items": [
                {
                    "family": "SeizureFrequency",
                    "text": "seizures",
                    "evidence": "Last seizures in teenage years.",
                },
                {
                    "family": "Investigations",
                    "text": "ECG",
                    "evidence": "ECG was normal.",
                },
                {
                    "family": "Investigations",
                    "text": "EEG",
                    "evidence": "EEG in 2012 was normal.",
                },
            ]
        }
    )
    parsed = parse_mention_unit_json(raw, method=HYBRID_METHOD)
    assert parsed.record is not None

    result = materialize_mention_unit(letter, parsed.record, method=HYBRID_METHOD)

    by_entity = {mention.entity: mention for mention in result.prediction.mentions}
    assert set(by_entity) == {"SeizureFrequency", "Investigations"}
    assert by_entity["SeizureFrequency"].attributes["NumberOfSeizures"] == "0"
    assert by_entity["Investigations"].text == "EEG"
    assert all(mention.text != "ECG" for mention in result.prediction.mentions)
