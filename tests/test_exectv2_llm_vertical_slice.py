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


def _file_sha256(path: Path) -> str:
    content = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(content).hexdigest()


def _normalise_empty_layer(value: Any) -> Any:
    return None if value in ("", []) else value


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


def test_exect_llm_public_split_requires_explicit_valid_mode_before_iteration() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.split import run_split

    class MustNotBeConsumed:
        def __iter__(self):
            raise AssertionError("mode validation must happen before input iteration")

    for mode in (None, "no-call", "unknown", "live/replay"):
        kwargs: dict[str, Any] = {"method": "llm", "split": "dev"}
        if mode is not None:
            kwargs["mode"] = mode
        with pytest.raises(ValueError, match="live, prompt-only, or replay"):
            run_split(MustNotBeConsumed(), **kwargs)


def test_exect_llm_modes_reject_mixed_provenance_and_preflight_replay_ids(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
        structured_one_call,
    )

    with pytest.raises(ValueError, match="live mode does not accept raw_outputs"):
        structured_one_call.produce_structured_letter(
            _letter(), mode="live", raw_output=_raw(), model="fixture/model"
        )
    prompt_fixture = structured_one_call.produce_structured_letter(
        _letter(), mode="prompt-only", raw_output=_raw(), model="fixture/model"
    )
    assert prompt_fixture.mode == "prompt-only"
    assert prompt_fixture.raw_output == _raw()

    calls = 0

    def fail_producer(*_args: Any, **_kwargs: Any) -> Any:
        nonlocal calls
        calls += 1
        raise AssertionError("incomplete replay must fail before processing")

    monkeypatch.setattr(structured_one_call, "produce_structured_letter", fail_producer)
    with pytest.raises(ValueError, match="complete raw_outputs"):
        structured_one_call.run_split(
            [_letter(), ExectLetter("LLM-VERTICAL-2", _letter().note_text)],
            split="dev",
            model="fixture/model",
            temperature=0,
            max_tokens=900,
            mode="replay",
            raw_outputs={_letter().letter_id: _raw()},
            projection="llm",
        )
    assert calls == 0

    with pytest.raises(ValueError, match="prompt-only mode does not accept raw_outputs"):
        structured_one_call.run_split(
            [_letter()],
            split="dev",
            model="fixture/model",
            temperature=0,
            max_tokens=900,
            mode="prompt-only",
            raw_outputs={_letter().letter_id: _raw()},
            projection="llm",
        )


def test_exect_llm_split_records_unambiguous_per_mode_call_counts() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
        structured_one_call,
    )

    letters = [
        ExectLetter("LLM-MODE-1", _letter().note_text),
        ExectLetter("LLM-MODE-2", _letter().note_text),
    ]
    calls = 0

    class Program:
        def __call__(self, **_kwargs: Any) -> Any:
            nonlocal calls
            calls += 1
            return type("Prediction", (), {"extraction_json": _raw()})()

    live_rows, live_metadata = structured_one_call.run_split(
        letters,
        split="dev",
        model="fixture/model",
        temperature=0,
        max_tokens=900,
        mode="live",
        program=Program(),
        projection="llm",
    )
    assert calls == 2
    assert live_metadata["mode"] == "live"
    assert all(row["mode"] == "live" for row in live_rows)

    prompt_rows, prompt_metadata = structured_one_call.run_split(
        letters,
        split="dev",
        model="fixture/model",
        temperature=0,
        max_tokens=900,
        mode="prompt-only",
        projection="llm",
    )
    assert calls == 2
    assert prompt_metadata["mode"] == "prompt-only"
    assert all(row["mode"] == "prompt-only" for row in prompt_rows)

    replay_rows, replay_metadata = structured_one_call.run_split(
        letters,
        split="dev",
        model="fixture/model",
        temperature=0,
        max_tokens=900,
        mode="replay",
        raw_outputs={letter.letter_id: _raw() for letter in letters},
        projection="llm",
    )
    assert calls == 2
    assert replay_metadata["mode"] == "replay"
    assert all(row["mode"] == "replay" for row in replay_rows)


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


def test_exect_llm_operational_api_marks_blocking_parse_output_as_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from clinical_extraction.operational import exect
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
        structured_one_call,
    )

    real = structured_one_call.produce_structured_letter

    def malformed_spy(letter: ExectLetter, **kwargs: Any):
        return real(letter, model=kwargs["model"], mode="replay", raw_output="not json")

    monkeypatch.setattr(structured_one_call, "produce_structured_letter", malformed_spy)
    output = exect.run_exect_notes(
        [InputNote(note_id="LLM-API-BAD", text=_letter().note_text)],
        RuntimeConfig(
            base_url="http://fixture.invalid/v1",
            api_key="fixture",
            model="fixture/model",
        ),
        method="llm",
    )

    assert output[0]["status"] == "error"
    assert output[0]["error"]["type"] == "model_or_parse_failure"
    assert "invalid_json:" in output[0]["error"]["message"]


def test_exect_llm_operational_live_contract_reuses_one_program_and_preserves_route_cache(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from clinical_extraction.operational import exect
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
        structured_one_call,
    )

    seen: dict[str, Any] = {"build": [], "configure": [], "programs": 0, "calls": 0}

    def build(model: str, **kwargs: Any) -> object:
        seen["build"].append((model, kwargs))
        return object()

    def configure(**kwargs: Any) -> None:
        seen["configure"].append(kwargs)

    class Program:
        def __init__(self) -> None:
            seen["programs"] += 1

        def __call__(self, **_kwargs: Any) -> Any:
            seen["calls"] += 1
            return type("Prediction", (), {"extraction_json": _raw()})()

    monkeypatch.setattr(structured_one_call, "build_dspy_lm", build)
    monkeypatch.setattr(structured_one_call.dspy, "configure", configure)
    monkeypatch.setattr(structured_one_call, "DspyKeyEntitiesStructuredExtractor", Program)

    output = exect.run_exect_notes(
        [
            InputNote(note_id="LLM-LIVE-1", text=_letter().note_text),
            InputNote(note_id="LLM-LIVE-2", text=_letter().note_text),
        ],
        RuntimeConfig(
            base_url="http://fixture.invalid/v1",
            api_key="fixture",
            model="fixture/model",
        ),
        method="llm",
    )

    assert seen["programs"] == 1
    assert seen["calls"] == 2
    assert len(seen["build"]) == 1
    assert seen["build"][0][1]["cache"] is False
    assert seen["build"][0][1]["api_base"] == "http://fixture.invalid/v1"
    assert len(seen["configure"]) == 1
    assert all(item["status"] == "ok" for item in output)
    assert all(item["route"] == "http://fixture.invalid/v1" for item in output)


def test_exect_llm_split_delegates_checkpoint_resume_and_skips_completed_ids(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    import dspy

    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.split import run_split

    letters = [
        ExectLetter("LLM-RESUME-1", _letter().note_text),
        ExectLetter("LLM-RESUME-2", _letter().note_text),
    ]
    counts = {"build": 0, "programs": 0, "calls": 0}

    def build(_model: str, **_kwargs: Any) -> object:
        counts["build"] += 1
        return object()

    class Program:
        def __init__(self) -> None:
            counts["programs"] += 1

        def __call__(self, **_kwargs: Any) -> Any:
            counts["calls"] += 1
            return type("Prediction", (), {"extraction_json": _raw()})()

    monkeypatch.setattr(dspy, "configure", lambda **_kwargs: None)
    checkpoint = tmp_path / "rows.jsonl"
    report = tmp_path / "report.json"
    first_rows, first_meta = run_split(
        letters,
        method="llm",
        split="dev",
        model="fixture/model",
        mode="live",
        progress_every=1,
        checkpoint_jsonl_path=checkpoint,
        checkpoint_report_path=report,
        model_builder=build,
        program_factory=Program,
    )
    assert len(first_rows) == 2
    assert first_meta["n_resumed"] == 0
    assert counts == {"build": 1, "programs": 1, "calls": 2}

    second_rows, second_meta = run_split(
        letters,
        method="llm",
        split="dev",
        model="fixture/model",
        mode="live",
        resume=True,
        checkpoint_jsonl_path=checkpoint,
        checkpoint_report_path=report,
        model_builder=build,
        program_factory=Program,
    )
    assert second_rows == first_rows
    assert second_meta["n_resumed"] == 2
    assert counts == {"build": 1, "programs": 1, "calls": 2}


def test_exect_llm_resume_rejects_foreign_run_provenance_before_provider_setup(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    import dspy

    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.split import run_split

    letters = [ExectLetter("LLM-FOREIGN-1", _letter().note_text)]
    checkpoint = tmp_path / "rows.jsonl"
    report = tmp_path / "report.json"
    counts = {"build": 0, "calls": 0}

    def build(_model: str, **_kwargs: Any) -> object:
        counts["build"] += 1
        return object()

    monkeypatch.setattr(dspy, "configure", lambda **_kwargs: None)

    run_split(
        letters,
        method="llm",
        split="dev",
        model="fixture/model",
        mode="replay",
        progress_every=1,
        checkpoint_jsonl_path=checkpoint,
        checkpoint_report_path=report,
        raw_outputs={letters[0].letter_id: _raw()},
    )
    with pytest.raises(ValueError, match="mismatched run_(fingerprint|provenance)"):
        run_split(
            letters,
            method="llm_with_rules",
            split="dev",
            model="fixture/model",
            mode="live",
            resume=True,
            checkpoint_jsonl_path=checkpoint,
            checkpoint_report_path=report,
            model_builder=build,
        )
    assert counts["build"] == 0


def test_exect_llm_resume_binds_checkpoint_to_exact_replay_content(
    tmp_path: Path,
) -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.split import run_split

    letter = ExectLetter("LLM-REPLAY-CONTENT-1", _letter().note_text)
    checkpoint = tmp_path / "rows.jsonl"
    report = tmp_path / "report.json"
    run_split(
        [letter],
        method="llm",
        split="dev",
        model="fixture/model",
        mode="replay",
        progress_every=1,
        checkpoint_jsonl_path=checkpoint,
        checkpoint_report_path=report,
        raw_outputs={letter.letter_id: _raw()},
    )

    changed_raw = json.dumps({"clinical_events": []}, separators=(",", ":"))
    with pytest.raises(ValueError, match="mismatched run_(fingerprint|provenance)"):
        run_split(
            [letter],
            method="llm",
            split="dev",
            model="fixture/model",
            mode="replay",
            resume=True,
            checkpoint_jsonl_path=checkpoint,
            checkpoint_report_path=report,
            raw_outputs={letter.letter_id: changed_raw},
        )


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("duplicate", "duplicate letter_id"),
        ("foreign", "foreign to the requested split"),
        ("missing_fingerprint", "mismatched run_fingerprint"),
        ("malformed", "checkpoint is malformed"),
    ],
)
def test_exect_llm_resume_rejects_malformed_or_extra_checkpoint_rows(
    mutation: str,
    message: str,
    tmp_path: Path,
) -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.split import run_split

    letter = ExectLetter(f"LLM-CHECKPOINT-{mutation}", _letter().note_text)
    checkpoint = tmp_path / "rows.jsonl"
    report = tmp_path / "report.json"
    run_split(
        [letter],
        method="llm",
        split="dev",
        model="fixture/model",
        mode="replay",
        progress_every=1,
        checkpoint_jsonl_path=checkpoint,
        checkpoint_report_path=report,
        raw_outputs={letter.letter_id: _raw()},
    )
    if mutation == "malformed":
        checkpoint.write_text("not-json\n", encoding="utf-8")
    else:
        rows = [json.loads(line) for line in checkpoint.read_text(encoding="utf-8").splitlines()]
        if mutation == "duplicate":
            rows.append(dict(rows[0]))
        elif mutation == "foreign":
            rows[0]["letter_id"] = "FOREIGN-CHECKPOINT-ROW"
        else:
            rows[0].pop("run_fingerprint")
        checkpoint.write_text(
            "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
            encoding="utf-8",
        )

    with pytest.raises(ValueError, match=message):
        run_split(
            [letter],
            method="llm",
            split="dev",
            model="fixture/model",
            mode="replay",
            resume=True,
            checkpoint_jsonl_path=checkpoint,
            checkpoint_report_path=report,
            raw_outputs={letter.letter_id: _raw()},
        )


def test_exect_llm_independent_dev140_raw_lane_parity_is_pinned() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import load_letters_for_split
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.split import run_split

    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    source_rows = _baseline_rows()
    assert _file_sha256(RAW_ARTIFACT) == baseline["source_artifact_sha256"]
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


def test_exect_llm_full_dev140_baseline_hashes_actual_output_and_trace() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import load_letters_for_split
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
        structured_one_call,
    )

    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    source_rows = _baseline_rows()
    assert _file_sha256(RAW_ARTIFACT) == baseline["source_artifact_sha256"]
    raw_outputs = {str(row["letter_id"]): str(row["raw_output"]) for row in source_rows}
    letters = load_letters_for_split("dev")
    assert len(letters) == baseline["row_count"]
    excluded = {
        "active_method",
        "method_id",
        "pipeline_family",
        "run_id",
        "source_method_id",
        "source_pipeline_family",
        "scored_view",
        "route",
        "dspy_cache",
        "producer_row",
        "prediction",
        "stage_events",
        "scorer_projection",
        "first_prediction_changing_owner",
        "first_failure",
    }

    full: list[dict[str, Any]] = []
    active_rows: list[dict[str, Any]] = []
    for letter, source in zip(letters, source_rows, strict=True):
        producer_result = structured_one_call.produce_structured_letter(
            letter,
            model="openai/gpt-5.6-sol",
            mode="prompt-only",
            raw_output=raw_outputs[letter.letter_id],
            split="dev140",
        )
        result = structured_one_call.run_llm_only_letter(letter, producer_result)
        actual = result.row
        producer = dict(producer_result.row)
        for field in BASELINE_FIELDS:
            actual_value = producer.get(field)
            source_value = source.get(field)
            if field in {"initial_parse_errors", "format_retry_output", "format_retry_notes"}:
                actual_value = _normalise_empty_layer(actual_value)
                source_value = _normalise_empty_layer(source_value)
            if field == "predicted_mentions":
                actual_value = [
                    {key: value for key, value in mention.items() if key != "component_owner"}
                    for mention in actual_value
                ]
            assert actual_value == source_value, f"producer parity: {field}"

        assert actual["mode"] == "prompt-only"
        assert actual["route"] == ""
        assert actual["active_method"] == "llm"
        assert actual["method_id"] == "llm"
        assert actual["pipeline_family"] == "llm"
        assert actual["run_id"] == "llm"
        assert actual["source_method_id"] == "exectv2_llm_only"
        assert actual["source_pipeline_family"] == source["pipeline_family"]
        assert actual["scored_view"] == "raw_candidate"
        assert actual["scorer_projection"]["view"] == "raw_candidate"
        assert all(event["owner"] and event["action"] for event in actual["stage_events"])
        assert actual["first_prediction_changing_owner"] == "model"
        assert actual["first_failure"] is None
        active_rows.append(actual)
        full.append(
            {
                "letter_id": actual["letter_id"],
                "producer_row": {
                    key: value for key, value in actual.items() if key not in excluded
                },
                "prediction": result.prediction.model_dump(mode="json"),
                "stages": [event.to_dict() for event in result.stage_events],
                "scorer": result.scorer_projection,
                "first_owner": result.first_prediction_changing_owner,
                "first_failure": result.first_failure,
            }
        )

    assert len(active_rows) == baseline["row_count"]
    assert _fingerprint(full) == (
        "ad58b6bfb288c1dc6b34022180c065d9ae394f15b7316c7f1f04fb48085a3462"
    )


def test_exect_llm_manifest_and_teaching_case_use_active_method_without_renaming_ids() -> None:
    manifest = stage_manifest.load_manifest("exectv2_llm_only")
    assert manifest.method == "llm"
    assert manifest.method_id == "exectv2_llm_only"
    assert "raw_candidate" in manifest.scored_representation
    case = build_exect_case()
    run = next(item for item in case.runs if item.manifest.method_id == "exectv2_llm_only")
    assert run.manifest.method == "llm"
    assert run.manifest.method_id == "exectv2_llm_only"
