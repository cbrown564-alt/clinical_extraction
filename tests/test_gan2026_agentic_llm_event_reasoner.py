from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    llm_event_reasoner,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord


def test_prompt_input_uses_structured_events_without_forbidden_labels() -> None:
    record = _record(
        901,
        "Clinic Date: 12 June 2026\nPatient reports one seizure per month.",
        gold_label="9 per year",
        gold_monthly_frequency=0.75,
    )
    prompt_input_json = llm_event_reasoner.build_prompt_input(
        record,
        _structured_event_row(
            901,
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
    assert payload["structured_event_input"]["original_final"]["final_label"] == "1 per month"
    assert payload["structured_event_input"]["event_table"][0]["event_id"] == "e1"
    assert payload["structured_event_input"]["event_table"][0]["normalized_candidate"] == {
        "normalized_label": "1 per month",
        "semantic_kind": "frequency",
        "monthly_frequency": 1.0138888888888888,
        "validation_errors": [],
    }
    assert any(
        "final_label must be a valid Gan label only" in instruction
        for instruction in payload["instructions"]
    )
    assert any(
        "Counts over vague intervals" in instruction for instruction in payload["instructions"]
    )
    assert any(
        "Keep original_final.final_label" in instruction for instruction in payload["instructions"]
    )
    assert any("Preserve cluster labels" in instruction for instruction in payload["instructions"])
    assert any(
        "Absence-since evidence is renderable as seizure_free" in instruction
        for instruction in payload["instructions"]
    )
    assert "one string: low | medium | high" == payload["required_output_schema"]["uncertainty"]
    assert "one string:" in payload["required_output_schema"]["attribution"]
    assert payload["raw_evidence_contexts"][0]["event_id"] == "e1"
    assert "one seizure per month" in payload["raw_evidence_contexts"][0]["context"]


def test_parse_reasoned_decision_preserves_raw_and_format_only_layers() -> None:
    parsed = llm_event_reasoner.parse_reasoned_decision_json(
        json.dumps(
            {
                "final_label": "two_per_week",
                "final_kind": "frequency",
                "selected_event_ids": ["e1"],
                "rejected_event_ids": ["e2"],
                "evidence": ["2 seizures per week"],
                "boundary_profile": ["freq_category_shift"],
                "calculation_trace": "2 / week",
                "clinical_rationale": "The selected event states a current weekly rate.",
                "uncertainty": "low",
                "tool_calls": [],
                "attribution": "llm_selected_tool_rendered",
            }
        )
    )

    assert parsed.raw_decision is not None
    assert parsed.raw_decision.final_label == "two_per_week"
    assert parsed.format_only_decision is not None
    assert parsed.format_only_decision.final_label == "2 per week"
    assert parsed.final_decision is not None
    assert parsed.final_decision.final_label == "2 per week"
    assert parsed.final_decision.attribution == "llm_selected_format_repaired"
    assert parsed.format_repair_events[0]["rule_id"] == (
        "benchmark_repair.underscore_label_separators"
    )
    assert any(error.startswith("final_label_format_repaired:") for error in parsed.parse_errors)


def test_parse_reasoned_decision_repairs_single_enum_arrays() -> None:
    parsed = llm_event_reasoner.parse_reasoned_decision_json(
        json.dumps(
            {
                "final_label": "4 per day",
                "final_kind": "frequency",
                "selected_event_ids": ["e1"],
                "rejected_event_ids": ["e2"],
                "evidence": ["overall frequency is four seizures per day"],
                "boundary_profile": [],
                "calculation_trace": None,
                "clinical_rationale": "The selected event states a current daily rate.",
                "uncertainty": ["low"],
                "tool_calls": [],
                "attribution": [
                    "llm_selected_tool_rendered",
                    "llm_selected_format_repaired",
                    "llm_original_structured_event_kept",
                ],
            }
        )
    )

    assert parsed.raw_decision is not None
    assert parsed.raw_decision.final_label == "4 per day"
    assert parsed.raw_decision.uncertainty == "low"
    assert parsed.raw_decision.attribution == "llm_selected_tool_rendered"
    assert parsed.final_decision is not None
    assert parsed.final_decision.final_label == "4 per day"
    assert "decision_enum_shape_repaired:uncertainty" in parsed.parse_errors
    assert "decision_enum_shape_repaired:attribution" in parsed.parse_errors
    assert parsed.format_repair_events == []


def test_prompt_only_run_consumes_structured_event_artifact_without_predictions() -> None:
    rows, metadata = llm_event_reasoner.run_split(
        [
            _record(
                902,
                "Clinic Date: 12 June 2026\nPatient reports one seizure per month.",
                gold_label="1 per month",
                gold_monthly_frequency=1.0138888888888888,
            )
        ],
        structured_event_rows=[
            _structured_event_row(
                902,
                final_label="1 per month",
                final_kind="frequency",
                purist_correct=True,
            )
        ],
        structured_event_source_path=Path("v0.jsonl"),
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=1600,
        mode="prompt-only",
        dspy_cache=True,
        api_base=None,
        escalation_reason=None,
        progress_every=None,
        checkpoint_jsonl_path=None,
        checkpoint_report_path=None,
    )

    assert metadata["artifact_kind"] == "gan2026_llm_event_reasoner_trace"
    assert metadata["summary"]["rows"] == 1
    assert metadata["summary"]["prediction_bearing_rows"] == 0
    assert metadata["summary"]["v0_purist_correct"] == 1
    assert metadata["summary"]["parse_or_validation_failures"] == 0
    assert metadata["summary"]["correct_to_wrong_vs_v0"] == 0
    assert metadata["summary"]["changed_labels_vs_v0"] == 0
    assert metadata["gate"]["status"] == "prompt_only_no_prediction"
    assert rows[0]["v0_reference"]["final_label"] == "1 per month"
    assert rows[0]["score_layers"]["raw_model"]["comparison"]["purist_correct"] is False
    assert rows[0]["transition_vs_v0"]["purist_transition"] == "unscored"
    assert rows[0]["trace_warnings"] == ["prompt_only_no_prediction"]


def test_live_run_scores_raw_format_and_final_layers_against_v0(monkeypatch) -> None:
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
                "final_label": "two_per_week",
                "final_kind": "frequency",
                "selected_event_ids": ["e1"],
                "rejected_event_ids": [],
                "evidence": ["2 seizures per week"],
                "boundary_profile": ["freq_category_shift"],
                "calculation_trace": "2 / week",
                "clinical_rationale": "The event table has a current weekly rate.",
                "uncertainty": "low",
                "tool_calls": [],
                "attribution": "llm_selected_tool_rendered",
            }
        )

    monkeypatch.setattr(llm_event_reasoner, "_run_model_call", fake_model_call)

    rows, metadata = llm_event_reasoner.run_split(
        [
            _record(
                903,
                "Clinic Date: 12 June 2026\nPatient reports 2 seizures per week.",
                gold_label="2 per week",
                gold_monthly_frequency=8.69047619047619,
            )
        ],
        structured_event_rows=[
            _structured_event_row(
                903,
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
        max_tokens=1600,
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
    assert row["score_layers"]["raw_model"]["final_label"] == "two_per_week"
    assert row["score_layers"]["format_only"]["final_label"] == "2 per week"
    assert row["score_layers"]["final"]["final_label"] == "2 per week"
    assert row["transition_vs_v0"]["purist_transition"] == "wrong_to_correct"
    assert row["decision_record"]["attribution"] == "llm_selected_format_repaired"
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
                }
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
            }
        ],
        "comparison": {
            "purist_correct": purist_correct,
            "pragmatic_correct": purist_correct,
        },
        "evidence_valid": True,
    }
