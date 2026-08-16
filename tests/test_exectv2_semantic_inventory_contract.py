"""Contract tests for the ExECT semantic inventory research lane."""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.semantic_inventory import (
    HYBRID_METHOD,
    LLM_METHOD,
    SEMANTIC_PROMPT_VERSION,
    build_inventory_prompt,
    materialize_inventory,
    parse_inventory_json,
)


def test_prompt_contracts_keep_metadata_out_and_separate_method_shapes() -> None:
    letter = ExectLetter(
        letter_id="EA0002", note_text="Current medication: lamotrigine 100 mg daily."
    )

    llm = json.loads(build_inventory_prompt(letter, method=LLM_METHOD))
    hybrid = json.loads(build_inventory_prompt(letter, method=HYBRID_METHOD))

    assert list(llm) == ["task", "output_schema", "family_guidance", "letter_text"]
    assert list(hybrid) == ["task", "output_schema", "family_guidance", "letter_text"]
    assert "letter_id" not in json.dumps(llm)
    assert "prompt_version" not in json.dumps(llm)
    assert "attributes" in json.dumps(llm["output_schema"])
    assert "attributes" not in json.dumps(hybrid["output_schema"])
    assert SEMANTIC_PROMPT_VERSION not in json.dumps(llm)


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


def test_hybrid_rules_parse_only_the_emitted_evidence() -> None:
    letter = ExectLetter(
        letter_id="EA0002",
        note_text=(
            "Diagnosis: focal epilepsy. Current medication: lamotrigine 100 mg daily. "
            "MRI was normal."
        ),
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


def test_llm_only_keeps_supported_fact_when_scorer_projection_is_partial() -> None:
    letter = ExectLetter(letter_id="EA0002", note_text="Last seizures in teenage years.")
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
    assert result.prediction.mentions[0].component_owner == "model.semantic_inventory"
