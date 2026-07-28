from __future__ import annotations

import json

import pytest

from scripts.gan2026_v05_dev750_panel import (
    ConditionSpec,
    classify_first_failure,
    summarize_condition_rows,
    validate_reuse_rows,
)


def _row(
    index: int,
    *,
    prompt_input: dict[str, object] | None = None,
    prompt_version: str = "gan2026_hybrid_structured_events_v0.5",
    raw_label: str = "2 per month",
    final_label: str = "2 per month",
    purist_correct: bool = True,
    pragmatic_correct: bool = True,
    evidence_valid: bool = True,
) -> dict[str, object]:
    prompt = prompt_input or {"note_text": f"note {index}"}
    return {
        "source_row_index": index,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "prompt_version": prompt_version,
        "prompt_input_json": json.dumps(prompt, sort_keys=True),
        "raw_output": json.dumps({"selection": {"final_label": raw_label}}),
        "structured_record": {
            "selection": {
                "final_label": final_label,
                "evidence": f"note {index}",
                "selected_event_ids": ["e1"],
            },
            "events": [
                {
                    "event_id": "e1",
                    "evidence": f"note {index}",
                    "kind": "frequency",
                }
            ],
        },
        "parse_errors": [],
        "call_error": None,
        "evidence_valid": evidence_valid,
        "comparison": {
            "purist_correct": purist_correct,
            "pragmatic_correct": pragmatic_correct,
        },
        "row_trace": {
            "schema_version": "gan2026.row_trace.v1",
            "method": "llm_with_rules",
            "model_prediction": {
                "record": {
                    "selection": {
                        "final_label": raw_label,
                        "evidence": f"note {index}",
                    }
                }
            },
            "format_repair": {"events": []},
            "deterministic_semantic": {"events": []},
        },
    }


def _condition() -> ConditionSpec:
    return ConditionSpec(
        slug="gpt41mini",
        model="openai/gpt-4.1-mini",
        execution_group="hosted_openai",
        transport="DSPy/LiteLLM OpenAI chat",
        temperature=0.0,
        cli_temperature=0.0,
        max_tokens=10_000,
        reuse_candidate=None,
        resume_candidate=None,
    )


def test_validate_reuse_rows_accepts_exact_complete_identity() -> None:
    rows = [_row(10), _row(20)]
    prompts = {10: {"note_text": "note 10"}, 20: {"note_text": "note 20"}}

    result = validate_reuse_rows(
        rows,
        expected_indices={10, 20},
        expected_prompt_inputs=prompts,
        require_complete=True,
    )

    assert result == {
        "rows": 2,
        "unique_source_rows": 2,
        "prompt_payload_matches": 2,
        "raw_outputs": 2,
    }


def test_validate_reuse_rows_rejects_prompt_payload_drift() -> None:
    rows = [_row(10, prompt_input={"note_text": "different"})]

    with pytest.raises(ValueError, match="prompt payload"):
        validate_reuse_rows(
            rows,
            expected_indices={10},
            expected_prompt_inputs={10: {"note_text": "note 10"}},
            require_complete=True,
        )


def test_validate_reuse_rows_allows_only_manifest_subset_for_resume() -> None:
    rows = [_row(10)]

    result = validate_reuse_rows(
        rows,
        expected_indices={10, 20},
        expected_prompt_inputs={10: {"note_text": "note 10"}},
        require_complete=False,
    )

    assert result["rows"] == 1
    with pytest.raises(ValueError, match="complete manifest"):
        validate_reuse_rows(
            rows,
            expected_indices={10, 20},
            expected_prompt_inputs={10: {"note_text": "note 10"}},
            require_complete=True,
        )


def test_summarize_condition_rows_pins_score_layers_and_transitions() -> None:
    rows = [
        _row(
            10,
            raw_label="unknown",
            final_label="2 per month",
            purist_correct=True,
            pragmatic_correct=True,
        ),
        _row(
            20,
            raw_label="2 per month",
            final_label="unknown",
            purist_correct=False,
            pragmatic_correct=False,
            evidence_valid=False,
        ),
    ]
    rows[1]["row_trace"]["model_prediction"]["record"]["selection"]["evidence"] = (
        "not in source"
    )

    summary, attribution = summarize_condition_rows(
        rows,
        condition=_condition(),
        expected_indices={10, 20},
        gold_monthly={10: 2.0, 20: 2.0},
        rules_correct={10: False, 20: True},
        artifact_sha256="abc",
    )

    assert summary["complete"] is True
    assert summary["model_boundary_purist_correct"] == 1
    assert summary["final_purist_correct"] == 1
    assert summary["deterministic_wrong_to_correct"] == 1
    assert summary["deterministic_correct_to_wrong"] == 1
    assert summary["rules_correct_regressions"] == 1
    assert summary["exact_selected_evidence"] == 1
    assert len(attribution) == 2
    assert attribution[0]["score_layer_transition"] == "wrong_to_correct"
    assert attribution[1]["first_failure_owner"] == "evidence_selection"


def test_classify_first_failure_keeps_transport_and_schema_distinct() -> None:
    assert (
        classify_first_failure(
            call_error="timeout",
            parse_errors=[],
            evidence_valid=False,
            model_correct=False,
            final_correct=False,
        )
        == "model_transport"
    )
    assert (
        classify_first_failure(
            call_error=None,
            parse_errors=["schema_validation_error: missing selection"],
            evidence_valid=False,
            model_correct=False,
            final_correct=False,
        )
        == "format_or_schema"
    )
