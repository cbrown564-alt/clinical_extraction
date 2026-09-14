"""Research validity: answer scoring is independent of inventory validity; runtime parity."""

from __future__ import annotations

import copy
import json
from types import SimpleNamespace

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    one_shot_thinking as study,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import one_shot_measurements_r5 as r5


def test_thinking_contract_and_independent_answer_scoring() -> None:
    for case in r5.fictional_cases():
        output = case["output"]
        r5.Rich.model_validate(output)
        record = SimpleNamespace(
            note_text=case["note_text"],
            raw={
                study.old.SEIZURE_FREQUENCY_KEY: {
                    "seizure_frequency_number": output["answer"]["label"]
                }
            },
        )
        wrapped = "[[ ## structured_json ## ]]\n" + json.dumps(output) + "\n[[ ## completed ## ]]"
        result = study.inspect(wrapped, "stop", record, "r5_rich")
        assert result["answer_valid"] and result["record_valid"]
        assert result["purist_correct"] and result["pragmatic_correct"]
        if output["findings"]:
            bad = copy.deepcopy(output)
            bad["selected_finding_ids"] = []
            checked = study.inspect(
                "[[ ## structured_json ## ]]\n" + json.dumps(bad), "stop", record, "r5_rich"
            )
            assert checked["failure"] == "invalid_schema"
            assert checked["answer_valid"] and checked["purist_correct"]
        missing = copy.deepcopy(output)
        del missing["answer"]
        checked = study.inspect(
            "[[ ## structured_json ## ]]\n" + json.dumps(missing), "stop", record, "r5_rich"
        )
        assert not checked["answer_valid"]
    note = SimpleNamespace(note_text="She has two seizures per month.")
    requests = [study.body(note, c) for c in study.CONDITIONS]
    assert all(
        {k: v for k, v in r.items() if k != "messages"}
        == {k: v for k, v in requests[0].items() if k != "messages"}
        for r in requests
    )
    assert requests[0]["thinking"] == {"type": "enabled"}
    assert requests[0]["reasoning_effort"] == "low"
    assert requests[0]["max_tokens"] == 24000
    for key in ("task", "instructions", "label_forms", "cases"):
        assert r5.prompt_payload("note")[key] == study.r4.prompt_payload("note", "simple")[key]
    zero = copy.deepcopy(r5.fictional_cases()[3]["output"])
    zero["findings"][0]["measurement"]["duration"]["quantity"]["value"] = 0
    record = SimpleNamespace(
        note_text=r5.fictional_cases()[3]["note_text"],
        raw={
            study.old.SEIZURE_FREQUENCY_KEY: {"seizure_frequency_number": zero["answer"]["label"]}
        },
    )
    checked = study.inspect(
        "[[ ## structured_json ## ]]\n" + json.dumps(zero), "stop", record, "r5_rich"
    )
    assert checked["failure"] == "invalid_schema" and checked["answer_valid"]
