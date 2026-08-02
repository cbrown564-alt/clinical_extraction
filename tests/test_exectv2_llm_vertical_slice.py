"""Contract tests for the active ExECT LLM-only vertical slice."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from clinical_extraction.architecture import stage_manifest
from clinical_extraction.architecture.teaching_case import build_exect_case
from clinical_extraction.operational.io import InputNote
from clinical_extraction.operational.runtime import RuntimeConfig
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter

RAW_ARTIFACT = Path(
    "experiments/exectv2_six_model_single_call_gpt56sol_dev140_20260715_structured.jsonl"
)
BASELINE = Path("tests/fixtures/exectv2_llm_base_7c9d8b5d_fingerprint.json")
BASELINE_FIELDS = (
    "letter_id",
    "model",
    "prompt_version",
    "prompt_profile",
    "prompt_input_json",
    "raw_output",
    "initial_parse_errors",
    "parse_errors",
    "format_retry_output",
    "format_retry_notes",
    "structured_events",
    "predicted_mentions",
    "n_events_raw",
    "n_mentions_raw",
    "n_mentions_scored",
    "n_evidence_invalid",
    "gate_warnings",
    "call_error",
)


def _letter() -> ExectLetter:
    return ExectLetter(
        letter_id="LLM-VERTICAL-1",
        note_text=(
            "Diagnosis: focal epilepsy. MRI brain normal. "
            "Levetiracetam 500 mg twice daily. She has two seizures per month."
        ),
    )


def _raw() -> str:
    return json.dumps(
        {
            "clinical_events": [
                {
                    "family": "diagnosis",
                    "anchor_text": "focal epilepsy",
                    "evidence": "Diagnosis: focal epilepsy",
                    "event_state": {},
                    "mentions": [
                        {"entity": "Diagnosis", "text": "focal epilepsy", "attributes": {}}
                    ],
                    "confidence": "high",
                    "rationale": "The diagnosis is explicit.",
                },
                {
                    "family": "investigation",
                    "anchor_text": "MRI brain normal",
                    "evidence": "MRI brain normal",
                    "event_state": {},
                    "mentions": [
                        {"entity": "Investigations", "text": "MRI", "attributes": {}}
                    ],
                    "confidence": "high",
                    "rationale": "The investigation is explicit.",
                },
                {
                    "family": "medication",
                    "anchor_text": "Levetiracetam 500 mg twice daily",
                    "evidence": "Levetiracetam 500 mg twice daily",
                    "event_state": {},
                    "mentions": [
                        {
                            "entity": "Prescription",
                            "text": "Levetiracetam",
                            "attributes": {"DoseUnit": "mg", "Frequency": "2"},
                        }
                    ],
                    "confidence": "high",
                    "rationale": "The prescription is explicit.",
                },
                {
                    "family": "seizure_frequency",
                    "anchor_text": "seizures",
                    "evidence": "She has two seizures per month",
                    "event_state": {},
                    "mentions": [
                        {
                            "entity": "SeizureFrequency",
                            "text": "seizures",
                            "attributes": {"NumberOfSeizures": "2", "TimePeriod": "Month"},
                        }
                    ],
                    "confidence": "high",
                    "rationale": "The frequency is explicit.",
                },
            ]
        },
        separators=(",", ":"),
    )


def _fingerprint(records: list[dict[str, Any]]) -> str:
    payload = "\n".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        for record in records
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _baseline_rows() -> list[dict[str, Any]]:
    return [json.loads(line) for line in RAW_ARTIFACT.read_text(encoding="utf-8").splitlines()]


def test_exect_llm_identity_accepts_only_its_exact_aliases() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.naming import (
        LLM_METHOD_ALIASES,
        active_method_name,
        retained_method_id,
    )

    assert LLM_METHOD_ALIASES == ("llm", "llm_only", "exectv2_llm_only")
    assert [active_method_name(alias) for alias in LLM_METHOD_ALIASES] == ["llm"] * 3
    assert retained_method_id("llm") == "exectv2_llm_only"
    with pytest.raises(ValueError):
        active_method_name("llm-only")


def test_exect_llm_public_runner_delegates_every_alias_to_one_canonical_projection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
        structured_one_call,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runner import (
        Exectv2PipelineConfiguration,
        Exectv2PipelineRunner,
    )

    calls: list[str] = []
    real = structured_one_call.run_llm_only_letter

    def spy(letter, producer):
        calls.append(letter.letter_id)
        return real(letter, producer)

    monkeypatch.setattr(structured_one_call, "run_llm_only_letter", spy)
    results = []
    for alias in ("llm", "llm_only", "exectv2_llm_only"):
        results.append(
            Exectv2PipelineRunner(
                Exectv2PipelineConfiguration(
                    method=alias, mode="replay", raw_output=_raw(), model="fixture/model"
                )
            ).run(_letter())
        )

    assert calls == ["LLM-VERTICAL-1"] * 3
    assert all(result.method == "llm" for result in results)
    assert all(result.result.row["method_id"] == "llm" for result in results)
    assert all(result.result.row["pipeline_family"] == "llm" for result in results)
    assert all(result.result.row["run_id"] == "llm" for result in results)
    assert all("saved_run_id" not in result.result.row for result in results)
    assert all("retained_evidence_id" not in result.result.row for result in results)


def test_exect_llm_split_rejects_forbidden_splits_before_consuming_input() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.split import run_split

    class MustNotBeConsumed:
        def __iter__(self):
            raise AssertionError("split validation must happen before processing")

    forbidden = (
        "test",
        "test60",
        "holdout",
        "locked_test",
        "locked-test",
        "aggregate_only",
        "aggregate-only",
        "full",
        "full200",
        "all",
        "development",
        "dev-140",
    )
    for split in forbidden:
        with pytest.raises(ValueError, match="inspectable development split"):
            run_split(MustNotBeConsumed(), method="llm", split=split, mode="replay")


def test_exect_llm_split_accepts_only_development_aliases_and_preserves_fresh_identity() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.split import run_split

    for split in ("dev", "dev140"):
        rows, metadata = run_split(
            [_letter()],
            method="llm_only",
            split=split,
            mode="replay",
            model="fixture/model",
            raw_outputs={_letter().letter_id: _raw()},
        )
        assert rows[0]["split"] == split
        assert rows[0]["method_id"] == "llm"
        assert rows[0]["pipeline_family"] == "llm"
        assert rows[0]["run_id"] == "llm"
        assert metadata["method_id"] == "llm"
        assert metadata["pipeline_family"] == "llm"
        assert metadata["run_id"] == "llm"
        assert "saved_run_id" not in rows[0]
        assert "retained_evidence_id" not in rows[0]
        assert "saved_run_id" not in metadata
        assert "retained_evidence_id" not in metadata


def test_exect_llm_prompt_only_and_replay_never_invoke_a_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
        structured_one_call,
    )

    def fail(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("prompt-only/replay must not call a model")

    monkeypatch.setattr(structured_one_call, "build_dspy_lm", fail)
    prompt_only = structured_one_call.produce_structured_letter(
        _letter(), model="fixture/model", mode="prompt-only"
    )
    replay = structured_one_call.produce_structured_letter(
        _letter(), model="fixture/model", mode="replay", raw_output=_raw()
    )
    assert prompt_only.mode == "prompt-only"
    assert prompt_only.raw_output == ""
    assert replay.mode == "replay"
    assert replay.raw_output == _raw()


def test_exect_llm_projection_keeps_raw_candidate_and_trace_ownership() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
        structured_one_call,
    )

    result = structured_one_call.run_llm_only_letter(
        _letter(),
        structured_one_call.produce_structured_letter(
            _letter(), raw_output=_raw(), model="openai/gpt-5.6-sol", mode="replay"
        ),
    )
    assert result.scorer_projection["view"] == "raw_candidate"
    assert all(event.stage_id.startswith("exect.llm.") for event in result.stage_events)
    assert all(event.owner and event.action for event in result.stage_events)
    assert result.stage_events[-2].stage_id == "exect.llm.raw_candidate"
    assert result.stage_events[-1].stage_id == "exect.llm.score"
    assert result.first_prediction_changing_owner == "model"
    assert not any("lens" in event.stage_id for event in result.stage_events)


def test_exect_llm_rejects_mismatched_producer_and_preserves_failure_layers() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
        structured_one_call,
    )

    producer = structured_one_call.produce_structured_letter(
        _letter(), raw_output="not json", model="fixture/model", mode="replay"
    )
    with pytest.raises(ValueError, match="producer letter_id"):
        structured_one_call.run_llm_only_letter(
            ExectLetter("OTHER", _letter().note_text), producer
        )
    assert producer.initial_parse_errors
    assert producer.parse_errors
    assert producer.format_retry_output == ""
    assert producer.projected_letter.mentions == ()


def test_exect_llm_operational_api_uses_the_canonical_runner_without_a_live_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from clinical_extraction.operational import exect
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
        structured_one_call,
    )

    calls: list[dict[str, Any]] = []
    real = structured_one_call.produce_structured_letter

    def replay_spy(letter: ExectLetter, **kwargs: Any):
        calls.append(kwargs)
        return real(letter, model=kwargs["model"], mode="replay", raw_output=_raw())

    monkeypatch.setattr(structured_one_call, "produce_structured_letter", replay_spy)
    output = exect.run_exect_notes(
        [InputNote(note_id="LLM-API-1", text=_letter().note_text)],
        RuntimeConfig(
            base_url="http://fixture.invalid/v1",
            api_key="fixture-key",
            model="fixture/model",
        ),
        method="exectv2_llm_only",
    )

    assert len(calls) == 1
    assert calls[0]["mode"] == "live"
    assert output[0]["pipeline"] == "llm"
    assert output[0]["method"] == "llm"
    assert output[0]["run_id"] == "llm"
    assert output[0]["scored_view"] == "raw_candidate"
    assert all(event["stage_id"].startswith("exect.llm.") for event in output[0]["trace"])


def test_exect_llm_independent_dev140_raw_lane_parity_is_pinned() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import load_letters_for_split
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.split import run_split

    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    source_rows = _baseline_rows()
    assert len(source_rows) == baseline["row_count"]
    letters = load_letters_for_split("dev")
    raw_outputs = {str(row["letter_id"]): str(row["raw_output"]) for row in source_rows}
    rows, _ = run_split(
        letters,
        method="llm",
        split="dev140",
        model="openai/gpt-5.6-sol",
        mode="replay",
        raw_outputs=raw_outputs,
    )
    by_id = {str(row["letter_id"]): row for row in rows}
    comparable = [
        {field: by_id[str(source["letter_id"])].get(field) for field in BASELINE_FIELDS}
        for source in source_rows
    ]
    expected = [{field: source.get(field) for field in BASELINE_FIELDS} for source in source_rows]
    for actual, source in zip(comparable, expected, strict=True):
        for field in BASELINE_FIELDS:
            if field in {
                "initial_parse_errors",
                "format_retry_output",
                "format_retry_notes",
                "predicted_mentions",
            }:
                continue
            assert actual[field] == source[field], field
        assert actual["mode"] if "mode" in actual else True
        assert [
            {key: value for key, value in mention.items() if key != "component_owner"}
            for mention in actual["predicted_mentions"]
        ] == source["predicted_mentions"]
    assert _fingerprint(expected) == baseline["normalized_sha256"]


def test_exect_llm_manifest_and_teaching_case_use_active_method_without_renaming_ids() -> None:
    manifest = stage_manifest.load_manifest("exectv2_llm_only")
    assert manifest.method == "llm"
    assert manifest.method_id == "exectv2_llm_only"
    assert "raw_candidate" in manifest.scored_representation
    case = build_exect_case()
    run = next(item for item in case.runs if item.manifest.method_id == "exectv2_llm_only")
    assert run.manifest.method == "llm"
    assert run.manifest.method_id == "exectv2_llm_only"
