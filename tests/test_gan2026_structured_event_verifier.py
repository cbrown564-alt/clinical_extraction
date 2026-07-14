from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    structured_event_verifier,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord


def test_verifier_prompt_uses_action_contract_without_forbidden_labels() -> None:
    record = _record(
        910,
        "Clinic Date: 12 June 2026\nPatient reports one seizure per month.",
        gold_label="9 per year",
        gold_monthly_frequency=0.75,
    )
    prompt_input_json = structured_event_verifier.build_prompt_input(
        record,
        _structured_event_row(
            910,
            final_label="1 per month",
            final_kind="frequency",
            purist_correct=False,
        ),
    )
    payload = json.loads(prompt_input_json)
    payload_text = json.dumps(payload, ensure_ascii=False)

    assert "source_row_index" not in payload_text
    assert "gold_label" not in payload_text
    assert "gan2026_split_v1" not in payload_text
    assert "9 per year" not in payload_text
    assert "deterministic_top" not in payload_text
    assert payload["variant"] == "V4_verifier_first_structured_event_correction"
    assert payload["structured_event_input"]["original_final"]["final_label"] == "1 per month"
    assert "keep_original_structured_event_final" in payload["required_output_schema"]["action"]
    assert "replace_with_existing_event" in payload["required_output_schema"]["action"]
    assert any(
        "Only override original_final when" in instruction
        for instruction in payload["instructions"]
    )
    assert any(
        "The action owns the final rendered label" in instruction
        for instruction in payload["instructions"]
    )


def test_keep_original_action_renders_original_structured_event_final() -> None:
    parsed = structured_event_verifier.parse_verifier_decision_json(
        json.dumps(
            {
                "action": "keep_original_structured_event_final",
                "final_label": "two_per_week",
                "final_kind": "frequency",
                "selected_event_ids": ["e2"],
                "rejected_event_ids": [],
                "evidence": ["2 seizures per week"],
                "contradiction_profile": [],
                "calculation_trace": None,
                "clinical_rationale": "The original answer remains supported.",
                "uncertainty": "low",
                "tool_calls": [],
                "attribution": "llm_selected_tool_rendered",
            }
        ),
        _structured_event_row(
            911,
            final_label="1 per month",
            final_kind="frequency",
            purist_correct=True,
        ),
    )

    assert parsed.raw_common_decision is not None
    assert parsed.raw_common_decision.final_label == "two_per_week"
    assert parsed.final_decision is not None
    assert parsed.final_decision.final_label == "1 per month"
    assert parsed.final_decision.selected_event_ids == ("e1",)
    assert parsed.final_decision.attribution == "llm_original_structured_event_kept"
    assert "verifier_action_rendered:keep_original_structured_event_final" in (
        parsed.action_render_events
    )


def test_replace_existing_event_action_renders_selected_normalized_candidate() -> None:
    parsed = structured_event_verifier.parse_verifier_decision_json(
        json.dumps(
            {
                "action": "replace_with_existing_event",
                "final_label": "two_per_week",
                "final_kind": "frequency",
                "selected_event_ids": ["e2"],
                "rejected_event_ids": ["e1"],
                "evidence": ["2 seizures per week"],
                "contradiction_profile": ["higher_current_burden"],
                "calculation_trace": "selected normalized event e2",
                "clinical_rationale": "The selected event has a higher current burden.",
                "uncertainty": "low",
                "tool_calls": [],
                "attribution": "llm_selected_tool_rendered",
            }
        ),
        _structured_event_row(
            912,
            final_label="1 per month",
            final_kind="frequency",
            purist_correct=False,
        ),
    )

    assert parsed.raw_common_decision is not None
    assert parsed.raw_common_decision.final_label == "two_per_week"
    assert parsed.format_only_decision is not None
    assert parsed.format_only_decision.final_label == "2 per week"
    assert parsed.final_decision is not None
    assert parsed.final_decision.final_label == "2 per week"
    assert parsed.final_decision.selected_event_ids == ("e2",)
    assert parsed.final_decision.evidence == ("2 seizures per week",)
    assert parsed.final_decision.boundary_profile == ("higher_current_burden",)
    assert "verifier_action_rendered:replace_with_existing_event:e2" in (
        parsed.action_render_events
    )


def test_live_run_scores_action_rendered_final_layer_against_v0(monkeypatch) -> None:
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
                "final_label": "two_per_week",
                "final_kind": "frequency",
                "selected_event_ids": ["e2"],
                "rejected_event_ids": ["e1"],
                "evidence": ["2 seizures per week"],
                "contradiction_profile": ["higher_current_burden"],
                "calculation_trace": "selected normalized event e2",
                "clinical_rationale": "The current weekly event supersedes the monthly final.",
                "uncertainty": "low",
                "tool_calls": [],
                "attribution": "llm_selected_tool_rendered",
            }
        )

    monkeypatch.setattr(structured_event_verifier, "_run_model_call", fake_model_call)

    rows, metadata = structured_event_verifier.run_split(
        [
            _record(
                913,
                "Clinic Date: 12 June 2026\nPatient reports 2 seizures per week.",
                gold_label="2 per week",
                gold_monthly_frequency=8.69047619047619,
            )
        ],
        structured_event_rows=[
            _structured_event_row(
                913,
                final_label="1 per month",
                final_kind="frequency",
                purist_correct=False,
            )
        ],
        structured_event_source_path=Path("v0.jsonl"),
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=1800,
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
    assert metadata["summary"]["raw_model_purist_correct"] == 0
    assert metadata["summary"]["format_only_purist_correct"] == 1
    assert metadata["summary"]["final_purist_correct"] == 1
    assert metadata["summary"]["wrong_to_correct_vs_v0"] == 1
    assert metadata["summary"]["verifier_actions"] == {"replace_with_existing_event": 1}
    assert row["score_layers"]["raw_model"]["final_label"] == "two_per_week"
    assert row["score_layers"]["format_only"]["final_label"] == "2 per week"
    assert row["score_layers"]["final"]["final_label"] == "2 per week"
    assert row["verifier_decision_record"]["action"] == "replace_with_existing_event"
    assert row["transition_vs_v0"]["purist_transition"] == "wrong_to_correct"
    assert row["decision_record"]["attribution"] == "llm_selected_tool_rendered"
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
                    "raw_value": "2 per week",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "applies_to": "seizures",
                    "evidence": "2 seizures per week",
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
                "normalized_label": "2 per week",
                "semantic_kind": "frequency",
                "monthly_frequency": 8.69047619047619,
                "validation_errors": [],
            },
        ],
        "comparison": {
            "purist_correct": purist_correct,
            "pragmatic_correct": purist_correct,
        },
        "evidence_valid": True,
    }
