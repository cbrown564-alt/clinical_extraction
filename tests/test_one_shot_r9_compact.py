from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    one_shot_measurements_r8 as r8,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    one_shot_measurements_r9 as r9,
)
from scripts.benchmarks.prepare_one_shot_r9_compact import V03_FIXTURES, check_response


def test_rendered_r9_uses_compact_contract_and_keeps_native_cases() -> None:
    baseline = r8.prompt_payload("<NOTE_TEXT>")
    payload = r9.prompt_payload("<NOTE_TEXT>")
    assert payload["label_forms"] == baseline["label_forms"]
    assert payload["cases"] == baseline["cases"]
    assert payload["note_text"] == baseline["note_text"]
    assert payload["output_schema"] == json.loads(r9.SCHEMA_PATH.read_text())
    assert payload["output_schema"]["required"] == ["answer", "findings"]
    assert "document_dates" not in payload["output_schema"]["properties"]
    instructions = " ".join(payload["instructions"] + payload["schema_instructions"])
    for phrase in (
        "not a request to return every fact",
        "nearest earlier measured state",
        "past_or_unclear",
        "status_episode",
        "median_interval",
        "recorded or reported",
        "longest or maximum seizure-free gap",
        "contradictory source assertions",
    ):
        assert phrase in instructions
    assert "more than one calendar year" not in instructions
    messages = r9.messages("<NOTE_TEXT>")
    rendered = json.JSONDecoder().raw_decode(
        messages[1]["content"].split("[[ ## prompt_input_json ## ]]")[1].lstrip()
    )[0]
    assert rendered == payload


def test_fictional_compact_responses_have_valid_evidence_and_links() -> None:
    schema = r9.prompt_payload("<NOTE_TEXT>")["output_schema"]
    cases = json.loads(
        Path(
            "results/letter-benchmarks/gan/one_shot_frequency_compact_scope_candidate_no_call/"
            "fictional_fixtures.json"
        ).read_text()
    ) + json.loads(V03_FIXTURES.read_text())
    for case in cases:
        check_response(case["note"], case["response"], schema)

    bad_link = json.loads(json.dumps(cases[0]["response"]))
    bad_link["answer"]["claim_indices"] = [len(bad_link["findings"])]
    with pytest.raises(AssertionError):
        check_response(cases[0]["note"], bad_link, schema)

    old_shape = r8.fictional_cases()[0]["output"]
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(old_shape)
