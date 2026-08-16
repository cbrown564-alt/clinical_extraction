"""Contract tests for the ExECT semantic inventory research lane."""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.semantic_inventory import (
    HYBRID_METHOD,
    LLM_METHOD,
    SEMANTIC_PROMPT_VERSION,
    SemanticInventoryExtractor,
    build_inventory_prompt,
    materialize_inventory,
    parse_inventory_json,
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
)


def _letter(note: str, letter_id: str = "EA0002") -> ExectLetter:
    return ExectLetter(letter_id=letter_id, note_text=note)


def test_prompt_version_is_fork_a_v4() -> None:
    assert SEMANTIC_PROMPT_VERSION == "exectv2_semantic_inventory_v4"


def test_prompt_contracts_keep_metadata_out_and_separate_method_shapes() -> None:
    letter = _letter("Current medication: lamotrigine 100 mg daily.")

    llm = json.loads(build_inventory_prompt(letter, method=LLM_METHOD))
    hybrid = json.loads(build_inventory_prompt(letter, method=HYBRID_METHOD))

    assert list(llm) == ["task", "output_schema", "family_guidance", "letter_text"]
    assert list(hybrid) == ["task", "output_schema", "family_guidance", "letter_text"]
    serialized = json.dumps({key: value for key, value in llm.items() if key != "letter_text"})
    assert SEMANTIC_PROMPT_VERSION not in serialized
    for term in _BANNED_PROMPT_TERMS:
        assert term not in serialized.lower()
    attributes = llm["output_schema"]["facts"][0]["attributes"]
    assert isinstance(attributes, dict)
    assert "concept" in attributes
    assert "count" in attributes
    assert "name" in attributes
    assert "Diagnosis" not in attributes
    assert "SeizureFrequency" not in attributes
    assert "attributes" not in json.dumps(hybrid["output_schema"])
    assert "every distinct atomic" not in llm["task"].lower()
    assert "one list" in llm["task"].lower()
    assert "attributes" in llm["task"].lower()
    assert "last" in json.dumps(llm["family_guidance"]).lower()
    assert "completed" in json.dumps(llm["family_guidance"]).lower()
    assert "clumsiness" in json.dumps(llm["family_guidance"]).lower()


def test_rendered_payload_stays_plain_and_metadata_free() -> None:
    letter = _letter("Current medication: lamotrigine 100 mg daily.")
    prompt = build_inventory_prompt(letter, method=LLM_METHOD)
    messages = SemanticInventoryExtractor(method=LLM_METHOD).render_messages(
        prompt_input_json=prompt
    )
    rendered = json.dumps(messages).lower()
    assert messages[0]["role"] == "system"
    assert "current" in str(messages[0]["content"]).lower()
    for term in _BANNED_PROMPT_TERMS:
        assert term not in rendered


def test_hybrid_parser_rejects_model_attributes_but_keeps_event() -> None:
    raw = json.dumps(
        {
            "facts": [
                {
                    "family": "Prescription",
                    "event": "Current lamotrigine regimen",
                    "evidence": "Current medication: lamotrigine 100 mg daily.",
                    "attributes": {"dose": "100"},
                }
            ]
        }
    )

    result = parse_inventory_json(raw, method=HYBRID_METHOD)

    assert result.record is not None
    assert result.record.facts[0].attributes == {}
    assert result.forbidden_fields == [{"fact_index": 0, "fields": ["attributes"]}]
    assert any("forbidden_model_fields" in error for error in result.errors)


def test_llm_parser_preserves_simple_semantic_attributes() -> None:
    raw = json.dumps(
        {
            "facts": [
                {
                    "family": "Prescription",
                    "event": "lamotrigine 100 mg daily",
                    "evidence": "Current medication: lamotrigine 100 mg daily.",
                    "attributes": {
                        "name": "lamotrigine",
                        "dose": 100,
                        "unit": "mg",
                        "schedule": "daily",
                    },
                }
            ]
        }
    )

    result = parse_inventory_json(raw, method=LLM_METHOD)

    assert result.record is not None
    assert result.record.facts[0].attributes["dose"] == "100"
    assert result.record.facts[0].attributes["schedule"] == "daily"
    assert any("coerced_attribute_value" in error for error in result.errors)


def test_llm_parser_unwraps_nested_family_attribute_blobs() -> None:
    raw = json.dumps(
        {
            "facts": [
                {
                    "family": "SeizureFrequency",
                    "event": "last seizures in teenage years",
                    "evidence": "Last seizures in teenage years.",
                    "attributes": {
                        "SeizureFrequency": {
                            "type": "seizures",
                            "state": "last-event",
                            "timeframe": "teenage years",
                        }
                    },
                }
            ]
        }
    )

    result = parse_inventory_json(raw, method=LLM_METHOD)

    assert result.record is not None
    assert result.record.facts[0].attributes["type"] == "seizures"
    assert result.record.facts[0].attributes["state"] == "last-event"
    assert "SeizureFrequency" not in result.record.facts[0].attributes
    assert any("unwrapped_nested_family_attributes" in error for error in result.errors)


def test_hybrid_rules_parse_only_the_emitted_evidence() -> None:
    letter = _letter(
        "She has epilepsy. Current medication: lamotrigine 100 mg daily. "
        "MRI was normal."
    )
    raw = json.dumps(
        {
            "facts": [
                {
                    "family": "Prescription",
                    "event": "lamotrigine 100 mg daily",
                    "evidence": "Current medication: lamotrigine 100 mg daily.",
                }
            ]
        }
    )
    parsed = parse_inventory_json(raw, method=HYBRID_METHOD)
    assert parsed.record is not None

    result = materialize_inventory(
        letter,
        parsed.record,
        method=HYBRID_METHOD,
    )

    assert [mention.entity for mention in result.prediction.mentions] == ["Prescription"]
    assert result.prediction.mentions[0].attributes["DrugName"] == "lamotrigine"
    assert all("MRI" not in str(trace.get("after", {})) for trace in result.rule_trace)
    assert result.rule_trace[0]["rule_category"] == "clinical_epilepsy"


def test_hybrid_keeps_the_event_drug_when_evidence_names_two() -> None:
    letter = _letter(
        "Current medication: lamotrigine 100 mg daily and levetiracetam 500 mg twice daily."
    )
    raw = json.dumps(
        {
            "facts": [
                {
                    "family": "Prescription",
                    "event": "lamotrigine 100 mg daily",
                    "evidence": (
                        "Current medication: lamotrigine 100 mg daily and "
                        "levetiracetam 500 mg twice daily."
                    ),
                }
            ]
        }
    )
    parsed = parse_inventory_json(raw, method=HYBRID_METHOD)
    assert parsed.record is not None

    result = materialize_inventory(letter, parsed.record, method=HYBRID_METHOD)

    assert len(result.prediction.mentions) == 1
    assert result.prediction.mentions[0].attributes["DrugName"] == "lamotrigine"
    assert result.prediction.mentions[0].attributes.get("DrugDose") == "100"


def test_llm_maps_last_event_to_zero_count_and_keeps_semantic_timeframe() -> None:
    letter = _letter("Last seizures in teenage years.")
    raw = json.dumps(
        {
            "facts": [
                {
                    "family": "SeizureFrequency",
                    "event": "last seizures in teenage years",
                    "evidence": "Last seizures in teenage years.",
                    "attributes": {
                        "type": "seizures",
                        "status": "historical",
                        "timeframe": "teenage years",
                    },
                }
            ]
        }
    )
    parsed = parse_inventory_json(raw, method=LLM_METHOD)
    assert parsed.record is not None

    result = materialize_inventory(letter, parsed.record, method=LLM_METHOD)

    assert result.semantic_facts[0]["attributes"]["timeframe"] == "teenage years"
    assert result.rule_trace == []
    assert result.prediction.mentions
    assert result.prediction.mentions[0].attributes["NumberOfSeizures"] == "0"
    assert result.prediction.mentions[0].component_owner == "model.semantic_inventory"


def test_hybrid_maps_last_event_from_event_and_evidence() -> None:
    letter = _letter("Last seizures in teenage years.")
    raw = json.dumps(
        {
            "facts": [
                {
                    "family": "SeizureFrequency",
                    "event": "last seizures in teenage years",
                    "evidence": "Last seizures in teenage years.",
                }
            ]
        }
    )
    parsed = parse_inventory_json(raw, method=HYBRID_METHOD)
    assert parsed.record is not None

    result = materialize_inventory(letter, parsed.record, method=HYBRID_METHOD)

    assert result.prediction.mentions
    assert result.prediction.mentions[0].attributes["NumberOfSeizures"] == "0"
    assert any(
        "last_event" in str(trace.get("action", "")).lower()
        or "encoding.last_event_zero" in str(trace)
        for trace in result.rule_trace
    )


def test_hybrid_does_not_score_planned_investigations_or_phenomenology() -> None:
    letter = _letter(
        "She had brief tingling in the right hand. I will arrange an MRI. "
        "EEG in 2012 was normal."
    )
    raw = json.dumps(
        {
            "facts": [
                {
                    "family": "SeizureFrequency",
                    "event": "brief tingling in the right hand",
                    "evidence": "She had brief tingling in the right hand.",
                },
                {
                    "family": "Investigations",
                    "event": "planned MRI",
                    "evidence": "I will arrange an MRI.",
                },
                {
                    "family": "Investigations",
                    "event": "EEG was normal",
                    "evidence": "EEG in 2012 was normal.",
                },
            ]
        }
    )
    parsed = parse_inventory_json(raw, method=HYBRID_METHOD)
    assert parsed.record is not None

    result = materialize_inventory(letter, parsed.record, method=HYBRID_METHOD)

    entities = [mention.entity for mention in result.prediction.mentions]
    texts = [mention.text.lower() for mention in result.prediction.mentions]
    assert entities == ["Investigations"]
    assert texts == ["eeg"]
    assert result.semantic_facts[0]["projection_status"] == "semantic_only_uncoded_phenomenology"
    assert result.semantic_facts[1]["projection_status"] == "semantic_only_pending_investigation"


def test_llm_keeps_noncurrent_prescription_in_the_semantic_trace() -> None:
    letter = _letter("I will start valproate next week.")
    raw = json.dumps(
        {
            "facts": [
                {
                    "family": "Prescription",
                    "event": "planned valproate",
                    "evidence": "I will start valproate next week.",
                    "attributes": {"name": "valproate", "status": "planned"},
                }
            ]
        }
    )
    parsed = parse_inventory_json(raw, method=LLM_METHOD)
    assert parsed.record is not None

    result = materialize_inventory(letter, parsed.record, method=LLM_METHOD)

    assert result.semantic_facts[0]["attributes"]["name"] == "valproate"
    assert result.semantic_facts[0]["projection_status"] == "semantic_only_noncurrent_status"
    assert result.prediction.mentions == ()


def test_hybrid_does_not_add_letter_level_diagnosis_residual() -> None:
    letter = _letter(
        "Diagnosis: epilepsy – probable focal\nShe has juvenile myoclonic epilepsy."
    )
    raw = json.dumps(
        {
            "facts": [
                {
                    "family": "Diagnosis",
                    "event": "juvenile myoclonic epilepsy",
                    "evidence": "She has juvenile myoclonic epilepsy.",
                }
            ]
        }
    )
    parsed = parse_inventory_json(raw, method=HYBRID_METHOD)
    assert parsed.record is not None

    result = materialize_inventory(letter, parsed.record, method=HYBRID_METHOD)

    texts = {mention.text.lower() for mention in result.prediction.mentions}
    assert texts == {"juvenile myoclonic epilepsy"}
    assert all(trace.get("action") != "diagnosis_residual_addition" for trace in result.rule_trace)


def test_llm_does_not_inherit_hybrid_residual_recovery() -> None:
    letter = _letter(
        "Diagnosis: epilepsy – probable focal\nShe has juvenile myoclonic epilepsy."
    )
    raw = json.dumps(
        {
            "facts": [
                {
                    "family": "Diagnosis",
                    "event": "juvenile myoclonic epilepsy",
                    "evidence": "She has juvenile myoclonic epilepsy.",
                    "attributes": {"concept": "juvenile myoclonic epilepsy"},
                }
            ]
        }
    )
    parsed = parse_inventory_json(raw, method=LLM_METHOD)
    assert parsed.record is not None

    result = materialize_inventory(letter, parsed.record, method=LLM_METHOD)

    texts = {mention.text.lower() for mention in result.prediction.mentions}
    assert texts == {"juvenile myoclonic epilepsy"}
    assert result.rule_trace == []


def test_hybrid_splits_heading_event_and_ignores_later_types_in_evidence() -> None:
    letter = _letter(
        "Diagnosis: focal epilepsy-Probable temporal. "
        "In March she had 2 to 3 of her focal seizures. "
        "four secondary generalised seizures."
    )
    raw = json.dumps(
        {
            "facts": [
                {
                    "family": "Diagnosis",
                    "event": "focal epilepsy, probably temporal",
                    "evidence": (
                        "Diagnosis: focal epilepsy-Probable temporal. "
                        "In March she had 2 to 3 of her focal seizures. "
                        "four secondary generalised seizures."
                    ),
                }
            ]
        }
    )
    parsed = parse_inventory_json(raw, method=HYBRID_METHOD)
    assert parsed.record is not None

    result = materialize_inventory(letter, parsed.record, method=HYBRID_METHOD)

    texts = sorted(mention.text.lower() for mention in result.prediction.mentions)
    entities = {mention.entity for mention in result.prediction.mentions}
    assert entities == {"Diagnosis"}
    assert texts == ["focal epilepsy", "temporal lobe epilepsy"]
    assert any(trace.get("action") == "convention_split_heading" for trace in result.rule_trace)


def test_hybrid_dual_codes_a_typed_rate_event() -> None:
    letter = _letter(
        "In March she had 2 to 3 of her focal seizures without change in awareness."
    )
    raw = json.dumps(
        {
            "facts": [
                {
                    "family": "SeizureFrequency",
                    "event": (
                        "In March she had 2 to 3 of her focal seizures "
                        "without change in awareness"
                    ),
                    "evidence": (
                        "In March she had 2 to 3 of her focal seizures "
                        "without change in awareness."
                    ),
                }
            ]
        }
    )
    parsed = parse_inventory_json(raw, method=HYBRID_METHOD)
    assert parsed.record is not None

    result = materialize_inventory(letter, parsed.record, method=HYBRID_METHOD)

    by_entity = {mention.entity: mention for mention in result.prediction.mentions}
    assert set(by_entity) == {"Diagnosis", "SeizureFrequency"}
    assert by_entity["Diagnosis"].text.lower() == "focal seizures"
    assert by_entity["SeizureFrequency"].attributes["LowerNumberOfSeizures"] == "2"
    assert by_entity["SeizureFrequency"].attributes["UpperNumberOfSeizures"] == "3"
    assert any(trace.get("action") == "dual_family_reuse" for trace in result.rule_trace)


def test_hybrid_closed_table_rewrites_an_event_phrase() -> None:
    letter = _letter("Diagnosis: Symptomatic structural epilepsy secondary to tuberous sclerosis")
    raw = json.dumps(
        {
            "facts": [
                {
                    "family": "Diagnosis",
                    "event": "symptomatic structural epilepsy",
                    "evidence": (
                        "Diagnosis: Symptomatic structural epilepsy "
                        "secondary to tuberous sclerosis"
                    ),
                }
            ]
        }
    )
    parsed = parse_inventory_json(raw, method=HYBRID_METHOD)
    assert parsed.record is not None

    result = materialize_inventory(letter, parsed.record, method=HYBRID_METHOD)

    texts = [mention.text.lower() for mention in result.prediction.mentions]
    assert texts == ["symptomatic structural focal epilepsy"]
    assert all("focal motor" not in text for text in texts)
    assert any(trace.get("action") == "closed_table_rewrite" for trace in result.rule_trace)


def test_hybrid_parses_dose_from_the_event_not_a_second_drug_in_evidence() -> None:
    letter = _letter(
        "Previous antiepileptic medication: lamotrigine and carbamazepine. "
        "Current antiepileptic medication: levetiracetam 500 mg twice a day."
    )
    raw = json.dumps(
        {
            "facts": [
                {
                    "family": "Prescription",
                    "event": "lamotrigine",
                    "evidence": "Previous antiepileptic medication: lamotrigine and carbamazepine.",
                }
            ]
        }
    )
    parsed = parse_inventory_json(raw, method=HYBRID_METHOD)
    assert parsed.record is not None

    result = materialize_inventory(letter, parsed.record, method=HYBRID_METHOD)

    assert result.prediction.mentions == () or (
        result.prediction.mentions[0].attributes["DrugName"] == "lamotrigine"
        and "carbamazepine" not in result.prediction.mentions[0].attributes.get("DrugName", "")
    )
