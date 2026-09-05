"""Always-on contract for one-call find, encode, and select."""

from __future__ import annotations

import json

from clinical_extraction.paper.gan import verify_gan
from clinical_extraction.paper.methods import LIVE_METHODS
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    prompt_llm_extract_encode_select as extract_encode_select,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    build_prompt_input,
    parse_structured_json,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_extract import (
    llm_extract_prompt_template,
)

_ENCODE_SELECT_BANNED_PHRASES = (
    "source-near",
    "slim events",
    "slim clinical",
    "fully normalized",
    "dated anchor",
    "clinical target",
    "semiologies",
)


def _record() -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=10,
        note_text="Present seizure frequency: two seizures per month.",
        gold_label="2 per month",
        gold_reference="two seizures per month",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label="2 per month",
        gold_label_kind=FrequencyLabelKind.FREQUENCY,
        gold_yearly_bounds=(24.0, 24.0),
        gold_monthly_frequency=2.0,
    )


def test_one_call_prompt_is_self_contained() -> None:
    baseline = llm_extract_prompt_template()
    variant = extract_encode_select.llm_extract_encode_select_prompt_template()
    blob = json.dumps(variant)
    assert variant["task"] != baseline["task"]
    assert "event_schema" not in variant
    assert "fact_schema" in variant
    assert "source-near" in json.dumps(baseline)
    leaked = [phrase for phrase in _ENCODE_SELECT_BANNED_PHRASES if phrase in blob]
    assert leaked == []
    assert "raw_value" in variant["fact_schema"]
    assert "normalised_label" in variant["fact_schema"]
    assert "null" not in variant["fact_schema"]["raw_value"]
    assert "null" not in variant["fact_schema"]["normalised_label"]
    assert "fact_id" in variant["fact_schema"]
    assert "f1" in variant["fact_schema"]["fact_id"]
    assert "e1" not in variant["fact_schema"]["fact_id"]
    assert "event_id" not in variant["fact_schema"]
    assert "assertion_status" not in variant["fact_schema"]
    assert "notes" not in variant["fact_schema"]
    assert "selected_fact_ids" in variant["selection_schema"]
    assert "selected_event_ids" not in variant["selection_schema"]
    assert "confidence" not in variant["selection_schema"]
    instruction_blob = " ".join(variant["instructions"])
    assert "raw_value" in instruction_blob
    assert "normalised_label" in instruction_blob
    assert "assertion_status" not in instruction_blob
    assert "confidence" not in instruction_blob
    assert "highest current or recent" not in instruction_blob
    assert "clinically most severe subtype" not in instruction_blob
    assert "Do not select seizure-free" not in instruction_blob
    assert "event_id" not in instruction_blob
    assert "For each fact," in instruction_blob
    assert "cannot write both" in instruction_blob
    assert variant["label_forms"]["rules"] == extract_encode_select.LABEL_FORM_RULES
    assert variant["label_forms"]["forms"] == extract_encode_select.LABEL_FORMS
    assert [row["title"] for row in variant["cases"]] == [
        "Usual gap",
        "Usual rate, not a year total",
        "Recent seizures after a quiet spell",
        "Not epileptic seizures",
        "Month counts",
        "Dated seizures",
        "Burst after a change",
        "Short quiet spell after a last seizure",
        "Overall count",
        "Do not choose seizure-free while seizures continue",
    ]
    assert variant["instructions"][-1] == extract_encode_select.SELECT_BRIDGE
    assert "first choice" not in blob.lower()
    assert "first_choice" not in blob
    for row in variant["cases"]:
        assert set(row) == set(extract_encode_select.CASE_KEYS)
        assert set(row["example"]) == set(extract_encode_select.EXAMPLE_KEYS)
        assert "event_id" not in json.dumps(row["example"])
        assert "events" not in row["example"]
        assert "first_choice" not in row["example"]


def test_one_call_payload_is_model_facing_and_registered() -> None:
    payload = json.loads(
        build_prompt_input(
            _record(),
            prompt_version=extract_encode_select.GAN_LLM_EXTRACT_ENCODE_SELECT,
        )
    )
    blob = json.dumps(payload)
    assert set(payload) == set(
        extract_encode_select.LLM_EXTRACT_ENCODE_SELECT_AUTHORED_KEYS
    )
    assert payload["note_text"] == _record().note_text
    assert "prompt_version" not in payload
    assert "source_row_index" not in payload
    assert "Gan 2026" not in blob
    assert "gan_llm" not in blob
    assert "codebook" not in blob.lower()
    assert "benchmark" not in blob.lower()
    assert LIVE_METHODS["gan_llm_extract_encode_select"]["paper_cell"] is False
    verified = verify_gan(
        "gan_llm_extract_encode_select", "test450", "gemini37flash"
    )
    assert verified["ok"] is True
    assert verified["row_policy"] == "aggregate_only"
    assert verified["prompt_version"] == (
        extract_encode_select.GAN_LLM_EXTRACT_ENCODE_SELECT
    )


def test_one_call_example_shape_parses() -> None:
    raw_output = json.dumps(extract_encode_select.CASES[0]["example"])
    extraction, normalized_events, errors = parse_structured_json(raw_output)
    assert errors == []
    assert extraction is not None
    assert [event.event_id for event in extraction.events] == ["f1", "f2"]
    assert extraction.selection.selected_event_ids == ["f2"]
    assert extraction.selection.final_kind == "frequency"
    assert normalized_events[1].normalized_label == "1 per 2 week"


def test_one_call_output_parses_without_dropped_fields() -> None:
    raw_output = json.dumps(
        {
            "facts": [
                {
                    "fact_id": "f1",
                    "kind": "frequency_rate",
                    "raw_value": "two seizures per month",
                    "normalised_label": "2 per month",
                    "applies_to": "seizures",
                    "time_window": "per month",
                    "temporality": "current",
                    "evidence": "two seizures per month",
                }
            ],
            "selection": {
                "selected_fact_ids": ["f1"],
                "final_kind": "frequency",
                "final_label": "2 per month",
                "evidence": "two seizures per month",
                "rationale": "stated monthly rate",
            },
        }
    )
    extraction, normalized_events, errors = parse_structured_json(raw_output)
    assert errors == []
    assert extraction is not None
    assert extraction.events[0].normalised_label == "2 per month"
    assert extraction.events[0].assertion_status == "asserted"
    assert extraction.selection.confidence == "medium"
    assert normalized_events[0].normalized_label == "2 per month"
