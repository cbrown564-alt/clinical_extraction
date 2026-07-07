from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    represented_event_normalizer,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.cli.llm_pipeline_cli import (
    pipeline_specs,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord


def test_represented_event_normalizer_is_registered_on_shared_cli_surface() -> None:
    spec = pipeline_specs()["represented_event_normalizer"]

    assert "represented-event" in spec.description
    assert spec.default_max_tokens == 2200
    assert spec.default_structured_event_jsonl_path is not None


def test_normalizer_prompt_allows_recompute_without_forbidden_labels() -> None:
    record = _record(
        940,
        ("Clinic Date: 12 June 2026\nPatient reports two seizures per week, not one per month."),
        gold_label="2 per week",
        gold_monthly_frequency=8.69047619047619,
    )
    prompt_input_json = represented_event_normalizer.build_prompt_input(
        record,
        _structured_event_row(
            940,
            final_label="1 per month",
            final_kind="frequency",
            purist_correct=False,
            replacement_normalized_label="unknown",
        ),
    )
    payload = json.loads(prompt_input_json)
    payload_text = json.dumps(payload, ensure_ascii=False)

    assert "source_row_index" not in payload_text
    assert "gold_label" not in payload_text
    assert "gan2026_split_v1" not in payload_text
    assert "2 per week" not in payload_text
    assert "deterministic_top" not in payload_text
    assert payload["variant"] == "V8_represented_event_normalizer"
    assert (
        "replace_with_recomputed_fact_from_selected_evidence"
        in payload["required_output_schema"]["action"]
    )
    assert "replace_with_existing_event" not in payload["required_output_schema"]["action"]
    assert any("selected existing event" in instruction for instruction in payload["instructions"])


def test_recomputed_action_renders_model_label_from_existing_selected_event() -> None:
    parsed = represented_event_normalizer.parse_normalizer_decision_json(
        json.dumps(
            {
                "action": "replace_with_recomputed_fact_from_selected_evidence",
                "final_label": "two_per_week",
                "final_kind": "frequency",
                "selected_event_ids": ["e2"],
                "rejected_event_ids": ["e1"],
                "evidence": ["two seizures per week"],
                "contradiction_profile": ["represented_rate_denominator"],
                "calculation_trace": "two seizures per week -> 2 per week",
                "clinical_rationale": (
                    "The selected event evidence states the current weekly rate."
                ),
                "uncertainty": "low",
                "tool_calls": [],
                "attribution": "llm_selected_tool_rendered",
            }
        ),
        _structured_event_row(
            941,
            final_label="1 per month",
            final_kind="frequency",
            purist_correct=False,
            replacement_normalized_label="unknown",
        ),
    )

    assert parsed.raw_common_decision is not None
    assert parsed.raw_common_decision.final_label == "two_per_week"
    assert parsed.format_only_decision is not None
    assert parsed.format_only_decision.final_label == "2 per week"
    assert parsed.final_decision is not None
    assert parsed.final_decision.final_label == "2 per week"
    assert parsed.final_decision.selected_event_ids == ("e2",)
    assert parsed.final_decision.attribution == "llm_selected_format_repaired"
    assert (
        "normalizer_action_validated:replace_with_recomputed_fact_from_selected_evidence"
        in parsed.action_render_events
    )


def test_recomputed_action_requires_selected_existing_event() -> None:
    parsed = represented_event_normalizer.parse_normalizer_decision_json(
        json.dumps(
            {
                "action": "replace_with_recomputed_fact_from_selected_evidence",
                "final_label": "2 per week",
                "final_kind": "frequency",
                "selected_event_ids": ["missing_event"],
                "rejected_event_ids": ["e1"],
                "evidence": ["two seizures per week"],
                "contradiction_profile": ["represented_rate_denominator"],
                "calculation_trace": "two seizures per week -> 2 per week",
                "clinical_rationale": "The selected event evidence states a weekly rate.",
                "uncertainty": "low",
                "tool_calls": [],
                "attribution": "llm_selected_tool_rendered",
            }
        ),
        _structured_event_row(
            942,
            final_label="1 per month",
            final_kind="frequency",
            purist_correct=False,
            replacement_normalized_label="unknown",
        ),
    )

    assert parsed.final_decision is None
    assert any(
        error.startswith("action_render_error: recomputed_selected_event_missing")
        for error in parsed.parse_errors
    )


def test_existing_event_replacement_is_disabled_for_normalizer() -> None:
    parsed = represented_event_normalizer.parse_normalizer_decision_json(
        json.dumps(
            {
                "action": "replace_with_existing_event",
                "final_label": "unknown",
                "final_kind": "unknown",
                "selected_event_ids": ["e2"],
                "rejected_event_ids": ["e1"],
                "evidence": ["two seizures per week"],
                "contradiction_profile": ["represented_sentinel_boundary"],
                "calculation_trace": None,
                "clinical_rationale": "Use the existing normalized candidate.",
                "uncertainty": "low",
                "tool_calls": [],
                "attribution": "llm_selected_tool_rendered",
            }
        ),
        _structured_event_row(
            942,
            final_label="1 per month",
            final_kind="frequency",
            purist_correct=False,
            replacement_normalized_label="unknown",
        ),
    )

    assert parsed.final_decision is None
    assert (
        "action_render_error: replace_existing_disabled_for_represented_event_normalizer"
        in parsed.parse_errors
    )


def test_live_normalizer_scores_recomputed_action_against_v0(monkeypatch) -> None:
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
                "action": "replace_with_recomputed_fact_from_selected_evidence",
                "final_label": "two_per_week",
                "final_kind": "frequency",
                "selected_event_ids": ["e2"],
                "rejected_event_ids": ["e1"],
                "evidence": ["two seizures per week"],
                "contradiction_profile": ["represented_rate_denominator"],
                "calculation_trace": "two seizures per week -> 2 per week",
                "clinical_rationale": "The selected event gives the current burden.",
                "uncertainty": "low",
                "tool_calls": [],
                "attribution": "llm_selected_tool_rendered",
            }
        )

    monkeypatch.setattr(represented_event_normalizer, "_run_model_call", fake_model_call)

    rows, metadata = represented_event_normalizer.run_split(
        [
            _record(
                943,
                "Clinic Date: 12 June 2026\nPatient reports two seizures per week.",
                gold_label="2 per week",
                gold_monthly_frequency=8.69047619047619,
            )
        ],
        structured_event_rows=[
            _structured_event_row(
                943,
                final_label="1 per month",
                final_kind="frequency",
                purist_correct=False,
                replacement_normalized_label="unknown",
            )
        ],
        structured_event_source_path=Path("v0.jsonl"),
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=2200,
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
    assert metadata["summary"]["recomputed_fact_actions"] == 1
    assert metadata["summary"]["wrong_to_correct_vs_v0"] == 1
    assert row["score_layers"]["raw_model"]["final_label"] == "two_per_week"
    assert row["score_layers"]["format_only"]["final_label"] == "2 per week"
    assert row["score_layers"]["final"]["final_label"] == "2 per week"
    assert row["normalizer_decision_record"]["action"] == (
        "replace_with_recomputed_fact_from_selected_evidence"
    )
    assert row["transition_vs_v0"]["purist_transition"] == "wrong_to_correct"
    assert row["evidence_valid"] is True


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


def _structured_event_row(
    source_row_index: int,
    *,
    final_label: str,
    final_kind: str,
    purist_correct: bool,
    replacement_normalized_label: str,
) -> dict:
    return {
        "source_row_index": source_row_index,
        "structured_record": {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "raw_value": final_label,
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "applies_to": "seizures",
                    "evidence": "one seizure per month",
                    "time_window": "current",
                },
                {
                    "event_id": "e2",
                    "kind": "frequency_rate",
                    "raw_value": "two seizures per week",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "applies_to": "seizures",
                    "evidence": "two seizures per week",
                    "time_window": "current",
                },
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": final_kind,
                "final_label": final_label,
                "evidence": "one seizure per month",
                "confidence": "high",
                "rationale": "Original structured-event selection.",
            },
        },
        "normalized_events": [
            {
                "event_id": "e1",
                "normalized_label": final_label,
                "semantic_kind": final_kind,
                "monthly_frequency": 1.0138888888888888,
                "validation_errors": [],
            },
            {
                "event_id": "e2",
                "normalized_label": replacement_normalized_label,
                "semantic_kind": "unknown",
                "monthly_frequency": 1000.0,
                "validation_errors": [],
            },
        ],
        "comparison": {
            "purist_correct": purist_correct,
            "pragmatic_correct": purist_correct,
        },
        "evidence_valid": True,
    }
