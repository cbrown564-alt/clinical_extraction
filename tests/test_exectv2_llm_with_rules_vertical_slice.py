"""Contract tests for the active ExECT LLM-with-rules vertical slice."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

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


def _letter(letter_id: str = "HYBRID-VERTICAL-1") -> ExectLetter:
    return ExectLetter(
        letter_id=letter_id,
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
                    "mentions": [{"entity": "Investigations", "text": "MRI", "attributes": {}}],
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


def _clinical_mention(mention: Any) -> dict[str, Any]:
    value = mention.model_dump(mode="json") if hasattr(mention, "model_dump") else mention
    return {
        field: value.get(field)
        for field in ("entity", "text", "evidence", "attributes", "confidence")
    }


def test_hybrid_identity_and_cli_aliases_are_active() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.cli_specs import get_cli_specs
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.naming import (
        LLM_WITH_RULES_METHOD_ALIASES,
        active_method_name,
        retained_method_id,
    )

    assert LLM_WITH_RULES_METHOD_ALIASES == (
        "llm_with_rules",
        "exectv2_llm_with_rules",
    )
    assert [active_method_name(alias) for alias in LLM_WITH_RULES_METHOD_ALIASES] == [
        "llm_with_rules",
        "llm_with_rules",
    ]
    assert retained_method_id("llm_with_rules") == "exectv2_llm_with_rules"
    assert set(LLM_WITH_RULES_METHOD_ALIASES) <= set(get_cli_specs())


def test_hybrid_public_runner_uses_canonical_projection_and_fresh_identity() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runner import (
        Exectv2PipelineConfiguration,
        Exectv2PipelineRunner,
    )

    result = Exectv2PipelineRunner(
        Exectv2PipelineConfiguration(
            method="llm_with_rules",
            mode="replay",
            raw_output=_raw(),
            model="fixture/model",
        )
    ).run(_letter())

    assert result.method == "llm_with_rules"
    assert result.result.row["active_method"] == "llm_with_rules"
    assert result.result.row["method_id"] == "llm_with_rules"
    assert result.result.row["source_method_id"] == "exectv2_llm_with_rules"
    assert result.result.row["scored_view"] == "clinical_headline"
    assert result.result.row["policy"] == {
        "diagnosis_policy_variant": "default",
        "prescription_policy_variant": "default",
        "sf_projection_ablation": "combined",
    }
    assert result.result.stage_events[-1].stage_id == "exect.hybrid.score"


def test_hybrid_runtime_trace_agrees_with_manifest_and_records_noops() -> None:
    from clinical_extraction.architecture.stage_manifest import load_manifest
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runner import (
        Exectv2PipelineConfiguration,
        Exectv2PipelineRunner,
    )

    result = Exectv2PipelineRunner(
        Exectv2PipelineConfiguration(
            method="llm_with_rules",
            mode="replay",
            raw_output=_raw(),
            model="fixture/model",
        )
    ).run(_letter())
    manifest = load_manifest("exectv2_llm_with_rules")
    events = result.result.stage_events
    assert [event.stage_id for event in events] == [stage.stage_id for stage in manifest.stages]
    assert [event.action for event in events] == [
        "build_four_family_prompt",
        "one_model_or_replay_call",
        "parse_schema_and_optional_format_retry",
        "flatten_model_events",
        "repair_attributes_and_enforce_evidence",
        "project_seizure_frequency_state",
        "suppress_unsupported_unknown_state",
        "register_raw_and_scored_findings",
        "apply_named_family_lens",
        "apply_named_family_lens",
        "apply_named_family_lens",
        "apply_named_family_lens",
        "require_exact_source_evidence",
        "materialize_scoring_views",
        "defer_gold_comparison_to_scorer",
    ]
    assert [event.changed for event in events] == [
        True,
        True,
        False,
        True,
        False,
        True,
        False,
        True,
        True,
        True,
        True,
        True,
        False,
        True,
        False,
    ]
    for event, stage in zip(events, manifest.stages, strict=True):
        assert event.owner == stage.owner
        assert event.effect_class == stage.effect_class
        assert event.rule_category == stage.rule_category
        assert event.action == stage.runtime_action


def test_hybrid_split_replay_projects_rows_without_a_second_producer_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
        structured_one_call,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.split import run_split

    calls = 0
    real = structured_one_call.produce_structured_letter

    def spy(letter: ExectLetter, **kwargs: Any):
        nonlocal calls
        calls += 1
        return real(letter, **kwargs)

    monkeypatch.setattr(structured_one_call, "produce_structured_letter", spy)
    letters = [_letter("HYBRID-SPLIT-1"), _letter("HYBRID-SPLIT-2")]
    rows, metadata = run_split(
        letters,
        method="llm_with_rules",
        split="dev",
        model="fixture/model",
        mode="replay",
        raw_outputs={letter.letter_id: _raw() for letter in letters},
    )

    assert calls == len(letters)
    assert [row["letter_id"] for row in rows] == [letter.letter_id for letter in letters]
    assert all(row["method_id"] == "llm_with_rules" for row in rows)
    assert all(row["source_method_id"] == "exectv2_llm_with_rules" for row in rows)
    assert all(row["pipeline_family"] == "llm_with_rules" for row in rows)
    assert all(
        row["source_pipeline_family"] == "exectv2_hybrid_key_family_event_ledger"
        for row in rows
    )
    assert all(row["scored_view"] == "clinical_headline" for row in rows)
    assert metadata["active_method"] == "llm_with_rules"
    assert metadata["method_id"] == "llm_with_rules"
    assert metadata["scored_view"] == "clinical_headline"


def test_hybrid_dev140_replay_matches_independent_prechange_oracle() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
        load_letters_for_split,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
        structured_one_call,
    )

    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    source_rows = [
        json.loads(line) for line in RAW_ARTIFACT.read_text(encoding="utf-8").splitlines()
    ]
    assert baseline["migration_baseline_commit"] == "4d2b04c5354d9317a263d5fb0b44f1a0da4766e7"
    assert baseline["oracle_commit"] == baseline["migration_baseline_commit"]
    assert baseline["source_commit"] == "7c9d8b5d"
    assert _file_sha256(RAW_ARTIFACT) == baseline["source_artifact_sha256"]
    assert len(source_rows) == baseline["row_count"] == 140
    raw_outputs = {str(row["letter_id"]): str(row["raw_output"]) for row in source_rows}
    letters = load_letters_for_split("dev")
    assert len(letters) == len(source_rows)

    parity: list[dict[str, Any]] = []
    for letter, source in zip(letters, source_rows, strict=True):
        producer = structured_one_call.produce_structured_letter(
            letter,
            model="openai/gpt-5.6-sol",
            mode="prompt-only",
            raw_output=raw_outputs[letter.letter_id],
            split="dev140",
        )
        result = structured_one_call.run_llm_with_rules_letter(letter, producer)
        for field in BASELINE_FIELDS:
            actual_value = producer.row.get(field)
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
        assert result.producer is producer
        assert result.row["active_method"] == "llm_with_rules"
        assert result.row["source_method_id"] == "exectv2_llm_with_rules"
        assert result.row["source_pipeline_family"] == source["pipeline_family"]
        for field in (
            "model",
            "mode",
            "split",
            "prompt_version",
            "prompt_profile",
            "raw_output",
            "initial_parse_errors",
            "parse_errors",
            "format_retry_output",
            "format_retry_notes",
            "call_error",
        ):
            assert result.row[field] == producer.row[field], f"final provenance: {field}"
        assert result.row["producer_row"] == producer.row
        assert result.row["prediction"] == result.prediction.model_dump(mode="json")
        assert result.row["scorer_projection"] == result.scorer_projection
        assert result.row["first_prediction_changing_owner"] == (
            result.first_prediction_changing_owner
        )
        assert result.row["first_failure"] == result.first_failure
        assert result.row["stage_events"] == [
            event.to_dict() for event in result.stage_events
        ]
        assert [
            (event.stage_id, event.owner, event.action)
            for event in result.stage_events
            if event.owner != "model"
        ] == [
            (
                str(stage["stage_id"]),
                str(stage["owner"]),
                str(stage["runtime_action"]),
            )
            for stage in json.loads(
                Path(
                    "src/clinical_extraction/architecture/manifests/"
                    "exectv2_llm_with_rules.json"
                ).read_text(encoding="utf-8")
            )["stages"]
            if stage["owner"] != "model"
        ]
        parity.append(
            {
                "letter_id": letter.letter_id,
                "producer": dict(producer.row),
                "prediction": [
                    _clinical_mention(mention) for mention in result.prediction.mentions
                ],
                "scorer": {
                    "view": result.scorer_projection["view"],
                    "n_mentions": len(result.prediction.mentions),
                },
                "first_owner": result.first_prediction_changing_owner,
                "first_failure": result.first_failure,
            }
        )

    assert _fingerprint(parity) == baseline["independent_prechange_oracle_sha256"]


def test_hybrid_operational_api_delegates_to_the_public_runner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from clinical_extraction.operational import exect
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runner import (
        Exectv2PipelineRunner,
    )

    calls: list[str] = []
    real_run = Exectv2PipelineRunner.run

    def replay_run(self: Exectv2PipelineRunner, letter: ExectLetter):
        calls.append(self.config.method)
        return real_run(
            Exectv2PipelineRunner(
                self.config.__class__(
                    **{
                        **self.config.__dict__,
                        "mode": "replay",
                        "raw_output": _raw(),
                    }
                )
            ),
            letter,
        )

    monkeypatch.setattr(Exectv2PipelineRunner, "run", replay_run)
    output = exect.run_exect_notes(
        [InputNote("HYBRID-API-1", _letter().note_text)],
        RuntimeConfig(
            base_url="http://fixture.invalid/v1",
            api_key="fixture-key",
            model="fixture/model",
        ),
        method="llm_with_rules",
    )

    assert calls == ["llm_with_rules"]
    assert output[0]["status"] == "ok"
    assert output[0]["pipeline"] == "llm_with_rules"
    assert output[0]["method"] == "llm_with_rules"
    assert output[0]["run_id"] == "llm_with_rules"
    assert output[0]["scored_view"] == "clinical_headline"
    assert output[0]["trace"][-1]["stage_id"] == "exect.hybrid.score"


@pytest.mark.parametrize(
    "raw_output",
    ["not json", '{"clinical_events":[{"family":"diagnosis"}]}'],
)
def test_hybrid_operational_api_fails_closed_on_malformed_model_output(
    monkeypatch: pytest.MonkeyPatch,
    raw_output: str,
) -> None:
    from clinical_extraction.operational import exect
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runner import (
        Exectv2PipelineConfiguration,
        Exectv2PipelineRunner,
    )

    real_run = Exectv2PipelineRunner.run

    def replay_malformed(self: Exectv2PipelineRunner, letter: ExectLetter):
        return real_run(
            Exectv2PipelineRunner(
                self.config.__class__(
                    **{
                        **self.config.__dict__,
                        "mode": "replay",
                        "raw_output": raw_output,
                    }
                )
            ),
            letter,
        )

    monkeypatch.setattr(Exectv2PipelineRunner, "run", replay_malformed)
    public_result = Exectv2PipelineRunner(
        Exectv2PipelineConfiguration(
            method="llm_with_rules",
            mode="replay",
            raw_output=raw_output,
            model="fixture/model",
        )
    ).run(_letter()).result
    assert public_result.row["parse_errors"]
    assert public_result.row["producer_row"]["parse_errors"]
    assert public_result.row["first_failure"]
    assert public_result.prediction.mentions == ()

    output = exect.run_exect_notes(
        [InputNote("HYBRID-API-MALFORMED", _letter().note_text)],
        RuntimeConfig(
            base_url="http://fixture.invalid/v1",
            api_key="fixture-key",
            model="fixture/model",
        ),
        method="llm_with_rules",
    )

    assert output[0]["status"] == "error"
    assert output[0]["error"]["type"] == "model_or_parse_failure"
    assert any(
        marker in output[0]["error"]["message"]
        for marker in ("invalid_json:", "schema_validation_error:")
    )
    assert output[0]["trace"][-1]["stage_id"] == "exect.hybrid.fail_closed"
    assert not any(
        mention["entity"] == "Diagnosis"
        for mention in output[0].get("prediction", {}).get("mentions", [])
    )
