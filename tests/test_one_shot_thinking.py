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


def test_r7_representation_preserves_task_and_frozen_r5() -> None:
    """Admission: preserve source units, bounds, dates and attribution without task drift."""
    import pytest
    from pydantic import ValidationError

    from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
        one_shot_measurements_r7 as r7,
    )

    before = r5.messages("fictional note")
    cases = {c["name"]: c for c in r7.fictional_cases()}
    for case in cases.values():
        parsed = r7.Rich.model_validate(case["output"])
        assert parsed.output() == case["output"]
        assert r7.Rich.model_validate(parsed.output()) == parsed
        assert all(f.evidence in case["note_text"] for f in parsed.findings)
        assert all(d.evidence in case["note_text"] for d in parsed.document_dates)
    for key in ("task", "instructions", "label_forms", "cases"):
        assert r7.prompt_payload("note")[key] == r5.prompt_payload("note")[key]
    assert r5.messages("fictional note") == before
    with pytest.raises(ValidationError):
        r5.Rich.model_validate(cases["observed_clusters"]["output"])

    cluster = copy.deepcopy(cases["observed_clusters"]["output"])
    del cluster["findings"][0]["period"]
    with pytest.raises(ValidationError, match="require period or occurred_at"):
        r7.Rich.model_validate(cluster)
    cluster["findings"][0]["measurement"]["occurred_at"] = {
        "time": "two weeks ago",
        "form": "relative",
    }
    assert r7.Rich.model_validate(cluster).output() == cluster
    no_ref = r7.Rich.model_validate(cases["document_dates_without_findings"]["output"])
    assert no_ref.output()["answer"]["evidence"] is None
    assert no_ref.document_dates and not no_ref.findings
    example = r7.Rich.model_validate(cases["complete_dates_example"]["output"])
    assert [d.role for d in example.document_dates] == ["clinic", "letter"]
    assert example.findings[3].measurement.occurred_at.time == "that date"
    assert not example.findings[1].measurement.approximate
    interval = r7.Range.model_validate({"type": "range", "lower": 2, "upper": 3})
    assert interval.lower_inclusive and interval.upper_inclusive

    for lower, upper, inclusive in [(5, 2, True), (2, 2, False)]:
        with pytest.raises(ValidationError, match="nonempty ordered"):
            r7.Range.model_validate(
                {
                    "type": "range",
                    "lower": lower,
                    "upper": upper,
                    "lower_inclusive": inclusive,
                }
            )
    for duration in [
        {"type": "number", "value": 0, "unit": "day"},
        {"type": "range", "lower": 0, "upper": 3, "unit": "day"},
        {
            "type": "bound",
            "relation": "at_most",
            "value": {"type": "range", "lower": 0, "upper": 3},
            "unit": "day",
        },
    ]:
        with pytest.raises(ValidationError):
            r7.DURATION_ADAPTER.validate_python(duration)
    # Defaults don't weaken type checking or revive obsolete fields/aliases.
    invalid = []
    for field, value in [("selected_ids", ["missing"]), ("selected_ids", ["f1", "f1"])]:
        bad = copy.deepcopy(cases["dated_count"]["output"])
        bad[field] = value
        invalid.append(bad)
    for field, value in [("timing", "recent"), ("finding_id", "f1")]:
        bad = copy.deepcopy(cases["dated_count"]["output"])
        bad["findings"][0][field] = value
        invalid.append(bad)
    for field, value in [("approximate", "false"), ("kind", "count")]:
        bad = copy.deepcopy(cases["dated_count"]["output"])
        bad["findings"][0]["measurement"][field] = value
        invalid.append(bad)
    bad = copy.deepcopy(cases["dated_count"]["output"])
    bad["findings"][0]["measurement"]["count"]["approximate"] = True
    invalid.append(bad)
    bad = copy.deepcopy(cases["qualitative_cluster_size"]["output"])
    bad["findings"][0]["measurement"]["rate"]["type"] = "rate"
    invalid.append(bad)
    for bad in invalid:
        with pytest.raises(ValidationError):
            r7.Rich.model_validate(bad)
    schema = r7.Rich.model_json_schema()
    properties = {
        key for definition in schema["$defs"].values() for key in definition.get("properties", {})
    }
    assert not properties & {
        "kind",
        "wording",
        "precision",
        "denominator",
        "cadence",
        "grouping",
        "description",
        "finding_id",
        "temporal_status",
    }
    assert "approximate" not in schema["$defs"]["Rate"].get("required", [])
    assert "type" not in schema["$defs"]["RateDetails"]["properties"]
    assert "quantity" not in schema["$defs"]["NumberDuration"]["properties"]
