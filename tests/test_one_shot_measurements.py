"""Always-on v2 safeguards: measurement semantics cannot collapse during parsing."""

from __future__ import annotations

import copy
import json

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    one_shot_measurements_dev as dev,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    one_shot_measurements as v2,
)


def test_measurement_variants_and_paired_examples_preserve_source_semantics() -> None:
    cases = {c["name"]: c for c in v2.fictional_cases()}
    for case in cases.values():
        output = case["output"]
        rich = v2.inspect_output(json.dumps(output), case["note_text"], "rich")
        assert rich["failure"] is None
        assert rich["output"] == output
        assert rich["quote_slots"] == rich["exact_quotes"]
        simple = v2.inspect_output(
            json.dumps({"answer": output["answer"]}), case["note_text"], "simple"
        )
        assert simple["failure"] is None
        assert rich["categories"] == simple["categories"]
        for condition in v2.v1.CONDITIONS:
            value = output if condition == "rich" else {"answer": output["answer"]}
            raw = json.dumps(value)
            wrapped = "[[ ## structured_json ## ]]\n" + raw + "\n[[ ## completed ## ]]"
            checked = dev.inspect(wrapped, case["note_text"], condition)
            assert checked["failure"] is None
            assert checked["categories"] == rich["categories"]
            assert checked["schema_valid"] and checked["envelope_valid"]
            assert checked["quote_slots"] == checked["exact_quotes"]
            assert (
                dev.inspect(wrapped, case["note_text"], condition, "length")["failure"]
                == "truncation"
            )
            assert dev.inspect(raw, case["note_text"], condition)["failure"] == "invalid_envelope"
            assert (
                dev.inspect(wrapped + wrapped, case["note_text"], condition)["failure"]
                == "invalid_envelope"
            )

    rich_prompt = v2.prompt_payload("fictional", "rich")
    simple_prompt = v2.prompt_payload("fictional", "simple")
    original = v2.v1.historical.llm_extract_encode_select_prompt_template()
    for key in ("task", "label_forms", "cases"):
        assert rich_prompt[key] == simple_prompt[key] == original[key]
    assert {
        k: v for k, v in rich_prompt.items() if k not in {"output_schema", "schema_instructions"}
    } == {
        k: v for k, v in simple_prompt.items() if k not in {"output_schema", "schema_instructions"}
    }
    assert rich_prompt["schema_instructions"][:2] == simple_prompt["schema_instructions"][:2]
    simple_instructions = " ".join(
        simple_prompt["instructions"] + simple_prompt["schema_instructions"]
    )
    for field in (
        "finding_id",
        "selected_finding_ids",
        "measurement.interval",
        "observation_period",
    ):
        assert field not in simple_instructions
    assert set(simple_prompt["output_schema"]["properties"]) == {"answer"}
    assert v2.messages("fictional", "rich")[0] == v2.messages("fictional", "simple")[0]
    for index, instruction in enumerate(original["instructions"]):
        if index not in {1, 2, 3}:  # Only instructions tied to replaced schema fields.
            assert rich_prompt["instructions"][index] == instruction
    assert "examples" not in rich_prompt  # Additional fixtures are checks, not new few-shots.
    messages = v2.messages("fictional", "rich")
    assert [m["role"] for m in messages] == ["system", "user"]
    assert "[[ ## prompt_input_json ## ]]" in messages[1]["content"]
    assert json.dumps(rich_prompt, ensure_ascii=False, sort_keys=True) in messages[1]["content"]

    def finding(name):
        return cases[name]["output"]["findings"][0]

    assert finding("observed_count")["measurement"]["kind"] == "observed_count"
    assert finding("upper_bound")["measurement"]["count"]["relation"] == "at_most"
    assert "measurement_assertion" not in v2.Finding.model_fields
    assert finding("seizure_free")["measurement"]["kind"] == "seizure_free_interval"
    assert finding("nonclustered_pattern")["measurement"]["wording"] == "not clustered"
    assert finding("reduced_not_absent")["measurement"]["kind"] == "qualitative_frequency"
    assert finding("subtype_seizure_free")["event"]["description"] == "tonic-clonic seizures"
    assert finding("subtype_seizure_free")["event"]["grouping"] == "one_type"
    assert finding("last_seizure")["measurement"]["when"]["wording"] == "in March"
    assert finding("last_seizure")["measurement"]["when"]["precision"] == "month"
    assert finding("conditional")["condition"] == "only when medication is missed"
    assert finding("qualitative")["event"]["seizure_interpretation"] == "uncertain_seizure"
    assert "raw_value" not in v2.Finding.model_fields
    assert "negated" not in v2.Finding.model_fields
    assert "certainty" not in v2.Finding.model_fields


def test_invalid_measurements_fail_without_inference_or_repair() -> None:
    original = v2.fictional_cases()[0]
    candidates = []
    reversed_range = copy.deepcopy(original["output"])
    reversed_range["findings"][0]["measurement"]["count"]["lower"] = 4
    candidates.append(reversed_range)
    zero_denominator = copy.deepcopy(original["output"])
    zero_denominator["findings"][0]["measurement"]["denominator"]["quantity"]["value"] = 0
    candidates.append(zero_denominator)
    bad_link = copy.deepcopy(original["output"])
    bad_link["selected_finding_ids"] = ["f2"]
    candidates.append(bad_link)
    missing_answer = copy.deepcopy(original["output"])
    del missing_answer["answer"]["label"]
    candidates.append(missing_answer)
    kind_mismatch = copy.deepcopy(original["output"])
    kind_mismatch["findings"][0]["measurement"]["kind"] = "last_seizure"
    candidates.append(kind_mismatch)
    numeric_string = copy.deepcopy(original["output"])
    numeric_string["findings"][0]["measurement"]["count"]["lower"] = "2"
    candidates.append(numeric_string)
    for payload in candidates:
        result = v2.inspect_output(json.dumps(payload), original["note_text"], "rich")
        assert result["failure"] == "invalid_schema"
        assert result["output"] is None
    assert (
        v2.inspect_output('{"answer": 1, "answer": 2}', "", "rich")["failure"] == "invalid_syntax"
    )
    assert v2.inspect_output(None, "", "rich")["failure"] == "no_response"
