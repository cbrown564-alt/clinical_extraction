from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    event_completion_reasoner,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.cli.llm_pipeline_cli import (
    pipeline_specs,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord


def test_event_completion_reasoner_is_registered_on_shared_cli_surface() -> None:
    spec = pipeline_specs()["event_completion_reasoner"]

    assert "event-completion" in spec.description
    assert spec.default_max_tokens == 2200
    assert spec.default_structured_event_jsonl_path is not None


def test_event_completion_prompt_has_raw_excerpt_without_forbidden_labels() -> None:
    record = _record(
        930,
        (
            "Clinic Date: 12 June 2026\n"
            "Patient has clusters about four times per month, with several "
            "events per cluster."
        ),
        gold_label="4 cluster per month, multiple per cluster",
        gold_monthly_frequency=1000.0,
    )
    prompt_input_json = event_completion_reasoner.build_prompt_input(
        record,
        _structured_event_row(
            930,
            final_label="unknown",
            final_kind="unknown",
            purist_correct=False,
        ),
    )
    payload = json.loads(prompt_input_json)
    payload_text = json.dumps(payload, ensure_ascii=False)

    assert "source_row_index" not in payload_text
    assert "gold_label" not in payload_text
    assert "gan2026_split_v1" not in payload_text
    assert "4 cluster per month" not in payload_text
    assert "deterministic_top" not in payload_text
    assert payload["variant"] == "V7_event_completion_reasoner"
    assert "create_completed_event_final" in payload["required_output_schema"]["action"]
    assert "Patient has clusters about four times per month" in payload["raw_note_excerpt"]
    assert any(
        "Only create a completed event" in instruction for instruction in payload["instructions"]
    )


def test_keep_action_renders_original_structured_event_final() -> None:
    parsed = event_completion_reasoner.parse_completion_decision_json(
        json.dumps(
            {
                "action": "keep_original_structured_event_final",
                "final_label": "4 per day",
                "final_kind": "frequency",
                "selected_event_ids": ["completed_event_1"],
                "rejected_event_ids": [],
                "evidence": ["four per day"],
                "boundary_profile": [],
                "calculation_trace": None,
                "rationale": "The original answer is sufficient.",
                "uncertainty": "low",
                "tool_calls": [],
                "attribution": "llm_selected_tool_rendered",
                "completed_event": {
                    "create_action_event_id": "completed_event_1",
                    "event_id": None,
                    "keep_action_value": "unknown",
                    "kind": None,
                    "raw_value": None,
                    "evidence": None,
                    "rationale": None,
                },
            }
        ),
        _structured_event_row(
            931,
            final_label="unknown",
            final_kind="unknown",
            purist_correct=True,
        ),
    )

    assert parsed.raw_decision is not None
    assert parsed.raw_decision.final_label == "4 per day"
    assert parsed.final_decision is not None
    assert parsed.final_decision.final_label == "unknown"
    assert parsed.final_decision.selected_event_ids == ("e1",)
    assert parsed.final_decision.attribution == "llm_original_structured_event_kept"
    assert "decision_field_shape_repaired:completed_event_ignored_for_keep" in (parsed.parse_errors)
    assert "decision_field_shape_repaired:clinical_rationale_alias" in (parsed.parse_errors)
    assert "completion_action_rendered:keep_original_structured_event_final" in (
        parsed.action_render_events
    )


def test_live_completion_scores_created_event_final(monkeypatch) -> None:
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
                "action": "create_completed_event_final",
                "final_label": "multiple per month",
                "final_kind": "unresolved_multiple",
                "selected_event_ids": ["completed_event_1"],
                "rejected_event_ids": ["e1"],
                "evidence": ["clusters about four times per month"],
                "boundary_profile": ["event_completion:cluster_axis"],
                "calculation_trace": "cluster cadence is about 4/month",
                "clinical_rationale": (
                    "The raw note contains a cluster cadence omitted from the event table."
                ),
                "uncertainty": "medium",
                "tool_calls": [],
                "attribution": "llm_selected_tool_rendered",
                "completed_event": {
                    "event_id": "completed_event_1",
                    "kind": "cluster_frequency",
                    "raw_value": "clusters about four times per month",
                    "evidence": "clusters about four times per month",
                    "rationale": "Omitted cluster cadence.",
                },
            }
        )

    monkeypatch.setattr(event_completion_reasoner, "_run_model_call", fake_model_call)

    rows, metadata = event_completion_reasoner.run_split(
        [
            _record(
                932,
                ("Clinic Date: 12 June 2026\nPatient has clusters about four times per month."),
                gold_label="multiple per month",
                gold_monthly_frequency=1000.0,
            )
        ],
        structured_event_rows=[
            _structured_event_row(
                932,
                final_label="unknown",
                final_kind="unknown",
                purist_correct=False,
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
    assert metadata["summary"]["completed_event_actions"] == 1
    assert metadata["summary"]["wrong_to_correct_vs_v0"] == 1
    assert row["score_layers"]["final"]["final_label"] == "multiple per month"
    assert row["decision_record"]["selected_event_ids"] == ["completed_event_1"]
    assert row["completed_event_record"]["kind"] == "cluster_frequency"
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
                    "kind": "unknown_frequency",
                    "raw_value": "unclear frequency",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "applies_to": "seizures",
                    "evidence": "unclear frequency",
                    "time_window": "current",
                }
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": final_kind,
                "final_label": final_label,
                "evidence": "unclear frequency",
                "confidence": "medium",
                "rationale": "Original structured-event selection.",
            },
        },
        "normalized_events": [
            {
                "event_id": "e1",
                "normalized_label": final_label,
                "semantic_kind": final_kind,
                "monthly_frequency": 1000.0,
                "validation_errors": [],
            }
        ],
        "comparison": {
            "purist_correct": purist_correct,
            "pragmatic_correct": purist_correct,
        },
        "evidence_valid": True,
    }
