from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    temporal_sentinel_specialist,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.cli.llm_pipeline_cli import (
    pipeline_specs,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord


def test_temporal_sentinel_specialist_is_registered_on_shared_cli_surface() -> None:
    spec = pipeline_specs()["temporal_sentinel_specialist"]

    assert "temporal/sentinel" in spec.description
    assert spec.default_max_tokens == 2400
    assert spec.default_structured_event_jsonl_path is not None


def test_specialist_prompt_uses_hints_without_forbidden_labels() -> None:
    record = _record(
        960,
        (
            "Clinic Date: 12 June 2026\n"
            "She reports a very infrequent, short event a fortnight ago."
        ),
        gold_label="unknown",
        gold_monthly_frequency=1000.0,
    )
    prompt_input_json = temporal_sentinel_specialist.build_prompt_input(
        record,
        _boundary_structured_event_row(960),
    )
    payload = json.loads(prompt_input_json)
    payload_text = json.dumps(payload, ensure_ascii=False)

    assert "source_row_index" not in payload_text
    assert "gold_label" not in payload_text
    assert "gan2026_split_v1" not in payload_text
    assert "deterministic_top" not in payload_text
    assert payload["variant"] == "V9_temporal_sentinel_specialist"
    assert "last_event_only_boundary" in payload["specialist_profiles"]
    assert payload["required_output_schema"]["action"] == [
        "keep_original_structured_event_final",
        "replace_with_existing_event",
    ]
    assert "replace_with_recomputed_fact_from_selected_evidence" in (
        payload["disabled_actions_for_this_run"]
    )
    assert payload["specialist_hints"]["possible_profiles"][0]["profile"] == (
        "last_event_only_boundary"
    )
    selected_review = payload["specialist_hints"]["selected_event_review"][0]
    assert "selected_event_candidate_differs_from_original_final" in (
        selected_review["review_flags"]
    )
    assert "last_event_only_or_latest_event" in selected_review["review_flags"]


def test_disabled_recompute_action_is_rejected() -> None:
    parsed = temporal_sentinel_specialist.parse_specialist_decision_json(
        json.dumps(
            {
                "action": "replace_with_recomputed_fact_from_selected_evidence",
                "final_label": "unknown",
                "final_kind": "unknown",
                "selected_event_ids": ["e1"],
                "rejected_event_ids": [],
                "evidence": ["a very infrequent, short event a fortnight ago"],
                "contradiction_profile": ["temporal_sentinel:last_event_only_boundary"],
                "calculation_trace": "disabled recompute attempt",
                "clinical_rationale": "The event is isolated.",
                "uncertainty": "low",
                "tool_calls": [],
                "attribution": "llm_selected_tool_rendered",
            }
        ),
        _boundary_structured_event_row(961),
    )

    assert parsed.final_decision is None
    assert (
        "action_render_error: disabled_action:"
        "replace_with_recomputed_fact_from_selected_evidence"
    ) in parsed.parse_errors


def test_seizure_free_replacement_is_safety_gated_when_original_is_frequency() -> None:
    parsed = temporal_sentinel_specialist.parse_specialist_decision_json(
        json.dumps(
            {
                "action": "replace_with_existing_event",
                "final_label": "seizure free for multiple year",
                "final_kind": "seizure_free",
                "selected_event_ids": ["e2"],
                "rejected_event_ids": ["e1"],
                "evidence": ["no seizures since last year"],
                "contradiction_profile": ["temporal_sentinel:seizure_free_sentinel_boundary"],
                "calculation_trace": None,
                "clinical_rationale": "Unsafe seizure-free replacement.",
                "uncertainty": "low",
                "tool_calls": [],
                "attribution": "llm_selected_tool_rendered",
            }
        ),
        _seizure_free_candidate_row(962),
    )

    assert parsed.final_decision is not None
    assert parsed.final_decision.final_label == "1 per 2 week"
    assert "specialist_safety_gate_kept_original:seizure_free_replacement_disallowed" in (
        parsed.action_render_events
    )


def test_seizure_free_replacement_allows_seizure_free_label_with_mismatched_kind() -> None:
    row = _seizure_free_candidate_row(965)
    row["structured_record"]["selection"]["final_kind"] = "unknown"
    row["structured_record"]["selection"]["final_label"] = "seizure free for multiple year"

    parsed = temporal_sentinel_specialist.parse_specialist_decision_json(
        json.dumps(
            {
                "action": "replace_with_existing_event",
                "final_label": "seizure free for multiple year",
                "final_kind": "seizure_free",
                "selected_event_ids": ["e2"],
                "rejected_event_ids": ["e1"],
                "evidence": ["no seizures since last year"],
                "contradiction_profile": ["temporal_sentinel:seizure_free_sentinel_boundary"],
                "calculation_trace": None,
                "clinical_rationale": "The original label text is already seizure-free.",
                "uncertainty": "low",
                "tool_calls": [],
                "attribution": "llm_selected_tool_rendered",
            }
        ),
        row,
    )

    assert parsed.final_decision is not None
    assert parsed.final_decision.final_label == "seizure free for multiple year"
    assert "action_render_error: seizure_free_replacement_disallowed" not in (
        parsed.parse_errors
    )


def test_live_specialist_scores_selected_boundary_event(monkeypatch) -> None:
    def fake_model_call(
        prompt_input_json: str,
        *,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        del model, temperature, max_tokens
        assert "deterministic_top" not in prompt_input_json
        return json.dumps(
            {
                "action": "replace_with_existing_event",
                "final_label": "no seizure frequency reference",
                "final_kind": "no_reference",
                "selected_event_ids": ["e1"],
                "rejected_event_ids": [],
                "evidence": ["a very infrequent, short event a fortnight ago"],
                "contradiction_profile": ["temporal_sentinel:last_event_only_boundary"],
                "calculation_trace": "isolated last-event evidence is not a cadence",
                "clinical_rationale": (
                    "The selected event's own normalized candidate is a sentinel "
                    "boundary rather than a recurring frequency."
                ),
                "uncertainty": "low",
                "tool_calls": [],
                "attribution": "llm_selected_tool_rendered",
            }
        )

    monkeypatch.setattr(
        temporal_sentinel_specialist,
        "_run_model_call",
        fake_model_call,
    )

    rows, metadata = temporal_sentinel_specialist.run_split(
        [
            _record(
                963,
                "Clinic Date: 12 June 2026\na very infrequent, short event a fortnight ago",
                gold_label="unknown",
                gold_monthly_frequency=1000.0,
            )
        ],
        structured_event_rows=[_boundary_structured_event_row(963)],
        structured_event_source_path=Path("v0.jsonl"),
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=2400,
        mode="live",
        dspy_cache=True,
        api_base=None,
        escalation_reason=None,
        progress_every=None,
        checkpoint_jsonl_path=None,
        checkpoint_report_path=None,
    )

    row = rows[0]

    assert metadata["summary"]["model_calls_attempted"] == 1
    assert metadata["summary"]["wrong_to_correct_vs_v0"] == 1
    assert metadata["summary"]["correct_to_wrong_vs_v0"] == 0
    assert metadata["summary"]["temporal_sentinel_profiles"] == {
        "temporal_sentinel:last_event_only_boundary": 1
    }
    assert row["score_layers"]["final"]["final_label"] == (
        "no seizure frequency reference"
    )
    assert row["transition_vs_v0"]["purist_transition"] == "wrong_to_correct"
    assert row["decision_record"]["selected_event_ids"] == ["e1"]
    assert row["evidence_valid"] is True


def test_live_specialist_scores_recurring_cadence_replacement(monkeypatch) -> None:
    def fake_model_call(
        prompt_input_json: str,
        *,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        del model, temperature, max_tokens
        assert "recurring_cadence_preferred" in prompt_input_json
        return json.dumps(
            {
                "action": "replace_with_existing_event",
                "final_label": "1 per month",
                "final_kind": "frequency",
                "selected_event_ids": ["e2"],
                "rejected_event_ids": ["e1"],
                "evidence": ["typical pattern is a focal seizure monthly"],
                "contradiction_profile": ["temporal_sentinel:recurring_cadence_preferred"],
                "calculation_trace": "typical monthly cadence beats year-to-date total",
                "clinical_rationale": "The current cadence is the clearer standing burden.",
                "uncertainty": "low",
                "tool_calls": [],
                "attribution": "llm_selected_tool_rendered",
            }
        )

    monkeypatch.setattr(
        temporal_sentinel_specialist,
        "_run_model_call",
        fake_model_call,
    )

    rows, metadata = temporal_sentinel_specialist.run_split(
        [
            _record(
                964,
                (
                    "Clinic Date: 12 June 2026\n"
                    "only seven focal impaired-awareness seizures reported so far "
                    "this year; typical pattern is a focal seizure monthly"
                ),
                gold_label="1 per month",
                gold_monthly_frequency=1.0138888888888888,
            )
        ],
        structured_event_rows=[_cadence_structured_event_row(964)],
        structured_event_source_path=Path("v0.jsonl"),
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=2400,
        mode="live",
        dspy_cache=True,
        api_base=None,
        escalation_reason=None,
        progress_every=None,
        checkpoint_jsonl_path=None,
        checkpoint_report_path=None,
    )

    row = rows[0]

    assert metadata["summary"]["wrong_to_correct_vs_v0"] == 1
    assert row["score_layers"]["final"]["final_label"] == "1 per month"
    assert row["transition_vs_v0"]["purist_transition"] == "wrong_to_correct"


def test_duration_only_boundary_replacement_is_safety_gated() -> None:
    parsed = temporal_sentinel_specialist.parse_specialist_decision_json(
        json.dumps(
            {
                "action": "replace_with_existing_event",
                "final_label": "no seizure frequency reference",
                "final_kind": "no_reference",
                "selected_event_ids": ["e1"],
                "rejected_event_ids": [],
                "evidence": [
                    (
                        "This week he has had 3 or 4 focal impaired awareness "
                        "seizures, each lasting a few minutes"
                    )
                ],
                "contradiction_profile": [
                    "temporal_sentinel:duration_or_episode_length_boundary"
                ],
                "calculation_trace": "duration text is not a cadence",
                "clinical_rationale": "Unsafe duration-only demotion.",
                "uncertainty": "low",
                "tool_calls": [],
                "attribution": "llm_selected_tool_rendered",
            }
        ),
        _duration_only_structured_event_row(966),
    )

    assert parsed.final_decision is not None
    assert parsed.final_decision.final_label == "3 to 4 per week"
    assert (
        "specialist_safety_gate_kept_original:replacement_not_in_high_precision_gate"
        in parsed.action_render_events
    )


def _record(
    source_row_index: int,
    note_text: str,
    *,
    gold_label: str = "unknown",
    gold_monthly_frequency: float = 1000.0,
) -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=source_row_index,
        note_text=note_text,
        gold_label=gold_label,
        gold_reference="",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label=gold_label,
        gold_label_kind=FrequencyLabelKind.UNKNOWN,
        gold_yearly_bounds=None,
        gold_monthly_frequency=gold_monthly_frequency,
    )


def _boundary_structured_event_row(source_row_index: int) -> dict:
    return {
        "source_row_index": source_row_index,
        "structured_record": {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "raw_value": "a very infrequent, short event a fortnight ago",
                    "temporality": "recent",
                    "assertion_status": "asserted",
                    "applies_to": "seizures",
                    "evidence": "a very infrequent, short event a fortnight ago",
                    "time_window": "a fortnight ago",
                    "notes": "isolated last event",
                }
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": "frequency",
                "final_label": "1 per 2 week",
                "evidence": "a very infrequent, short event a fortnight ago",
                "confidence": "high",
                "rationale": "Original structured-event selection.",
            },
        },
        "normalized_events": [
            {
                "event_id": "e1",
                "normalized_label": "no seizure frequency reference",
                "semantic_kind": "no_reference",
                "monthly_frequency": 1000.0,
                "validation_errors": [],
            }
        ],
        "comparison": {
            "purist_correct": False,
            "pragmatic_correct": False,
        },
        "evidence_valid": True,
    }


def _cadence_structured_event_row(source_row_index: int) -> dict:
    return {
        "source_row_index": source_row_index,
        "structured_record": {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "raw_value": "seven seizures so far this year",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "applies_to": "focal seizures",
                    "evidence": (
                        "only seven focal impaired-awareness seizures reported so "
                        "far this year"
                    ),
                    "time_window": "so far this year",
                },
                {
                    "event_id": "e2",
                    "kind": "frequency_rate",
                    "raw_value": "focal seizure monthly",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "applies_to": "focal seizures",
                    "evidence": "typical pattern is a focal seizure monthly",
                    "time_window": "current pattern",
                },
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": "frequency",
                "final_label": "7 per 10 month",
                "evidence": (
                    "only seven focal impaired-awareness seizures reported so far "
                    "this year"
                ),
                "confidence": "high",
                "rationale": "Original structured-event selection.",
            },
        },
        "normalized_events": [
            {
                "event_id": "e1",
                "normalized_label": "7 per 10 month",
                "semantic_kind": "frequency",
                "monthly_frequency": 0.7097222222222223,
                "validation_errors": [],
            },
            {
                "event_id": "e2",
                "normalized_label": "1 per month",
                "semantic_kind": "frequency",
                "monthly_frequency": 1.0138888888888888,
                "validation_errors": [],
            },
        ],
        "comparison": {
            "purist_correct": False,
            "pragmatic_correct": True,
        },
        "evidence_valid": True,
    }


def _seizure_free_candidate_row(source_row_index: int) -> dict:
    row = _boundary_structured_event_row(source_row_index)
    row["structured_record"]["events"].append(
        {
            "event_id": "e2",
            "kind": "seizure_free",
            "raw_value": "no seizures since last year",
            "temporality": "current",
            "assertion_status": "asserted",
            "applies_to": "seizures",
            "evidence": "no seizures since last year",
            "time_window": "since last year",
        }
    )
    row["normalized_events"].append(
        {
            "event_id": "e2",
            "normalized_label": "seizure free for multiple year",
            "semantic_kind": "seizure_free",
            "monthly_frequency": 0.0,
            "validation_errors": [],
        }
    )
    return row


def _duration_only_structured_event_row(source_row_index: int) -> dict:
    return {
        "source_row_index": source_row_index,
        "structured_record": {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "raw_value": "3 or 4 focal impaired awareness seizures",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "applies_to": "focal impaired awareness seizures",
                    "evidence": (
                        "This week he has had 3 or 4 focal impaired awareness "
                        "seizures, each lasting a few minutes"
                    ),
                    "time_window": "this week",
                }
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": "frequency",
                "final_label": "3 to 4 per week",
                "evidence": (
                    "This week he has had 3 or 4 focal impaired awareness "
                    "seizures, each lasting a few minutes"
                ),
                "confidence": "high",
                "rationale": "Original structured-event selection.",
            },
        },
        "normalized_events": [
            {
                "event_id": "e1",
                "normalized_label": "no seizure frequency reference",
                "semantic_kind": "no_reference",
                "monthly_frequency": 1000.0,
                "validation_errors": [],
            }
        ],
        "comparison": {
            "purist_correct": True,
            "pragmatic_correct": True,
        },
        "evidence_valid": True,
    }
