from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    cross_model_structured_event_adjudicator,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord


def test_cross_model_prompt_excludes_forbidden_scoring_context() -> None:
    record = _record(
        970,
        "Clinic Date: 12 June 2026\nHe now has a focal seizure about once monthly.",
        gold_label="1 per month",
        gold_monthly_frequency=1.0138888888888888,
    )
    prompt_input_json = cross_model_structured_event_adjudicator.build_prompt_input(
        record,
        {
            "gpt": _agent_row(
                970,
                label="unknown",
                kind="unknown",
                evidence="He now has a focal seizure about once monthly.",
            ),
            "qwen": _agent_row(
                970,
                label="1 per month",
                kind="frequency",
                evidence="He now has a focal seizure about once monthly.",
            ),
            "deepseek": _agent_row(
                970,
                label="unknown",
                kind="unknown",
                evidence="He now has a focal seizure about once monthly.",
            ),
        },
    )
    payload = json.loads(prompt_input_json)
    payload_text = json.dumps(payload, ensure_ascii=False)

    assert "source_row_index" not in payload_text
    assert "gold_label" not in payload_text
    assert "gan2026_split_v1" not in payload_text
    assert "deterministic_top" not in payload_text
    assert payload["variant"] == "V10_cross_model_structured_event_adjudicator"
    assert payload["required_output_schema"]["action"] == [
        "keep_gpt_final",
        "select_qwen_final",
        "select_deepseek_final",
    ]
    assert payload["agreement_features"]["peer_disagreement_with_gpt"] == ["qwen"]


def test_parse_cross_model_decision_renders_selected_qwen_final() -> None:
    gpt_evidence = "only seven focal seizures reported so far this year"
    peer_evidence = "typical pattern is a focal seizure monthly"
    note_text = f"{gpt_evidence}; {peer_evidence}."
    parsed = cross_model_structured_event_adjudicator.parse_cross_model_decision_json(
        json.dumps(
            {
                "action": "select_qwen_final",
                "selected_agent_id": "qwen",
                "final_label": "1 per month",
                "final_kind": "frequency",
                "selected_event_ids": ["e1"],
                "rejected_agent_ids": ["gpt", "deepseek"],
                "evidence": [peer_evidence],
                "comparison_profile": ["peer_recurring_cadence_beats_gpt_unknown"],
                "calculation_trace": "monthly cadence is explicitly stated",
                "clinical_rationale": "Qwen selected the explicit current cadence.",
                "uncertainty": "low",
                "attribution": "llm_selected_tool_rendered",
            }
        ),
        agent_rows={
            "gpt": _agent_row(
                971,
                label="7 per 10 month",
                kind="frequency",
                evidence=gpt_evidence,
            ),
            "qwen": _agent_row(
                971,
                label="1 per month",
                kind="frequency",
                evidence=peer_evidence,
            ),
            "deepseek": _agent_row(
                971,
                label="1 per month",
                kind="frequency",
                evidence=peer_evidence,
            ),
        },
        note_text=note_text,
    )

    assert parsed.final_decision is not None
    assert parsed.final_decision.final_label == "1 per month"
    assert parsed.final_decision.selected_event_ids == ("qwen:e1",)
    assert parsed.final_decision.evidence == (peer_evidence,)
    assert "rendered_selected_agent_final:qwen" in parsed.action_render_events


def test_missing_action_is_inferred_from_selected_agent_id() -> None:
    gpt_evidence = "only seven focal seizures reported so far this year"
    peer_evidence = "typical pattern is a focal seizure monthly"
    note_text = f"{gpt_evidence}; {peer_evidence}."
    parsed = cross_model_structured_event_adjudicator.parse_cross_model_decision_json(
        json.dumps(
            {
                "selected_agent_id": "Qwen peer",
                "final_label": "1 per month",
                "final_kind": "frequency",
                "selected_event_ids": ["e1"],
                "rejected_agent_ids": "gpt, deepseek",
                "evidence": [peer_evidence],
                "comparison_profile": [],
                "calculation_trace": None,
                "clinical_rationale": "Qwen selected the explicit cadence.",
                "uncertainty": "low",
            }
        ),
        agent_rows={
            "gpt": _agent_row(
                974,
                label="7 per 10 month",
                kind="frequency",
                evidence=gpt_evidence,
            ),
            "qwen": _agent_row(
                974,
                label="1 per month",
                kind="frequency",
                evidence=peer_evidence,
            ),
            "deepseek": _agent_row(
                974,
                label="1 per month",
                kind="frequency",
                evidence=peer_evidence,
            ),
        },
        note_text=note_text,
    )

    assert parsed.raw_decision is not None
    assert parsed.raw_decision.action == "select_qwen_final"
    assert parsed.raw_decision.selected_agent_id == "qwen"
    assert parsed.raw_decision.rejected_agent_ids == ("gpt", "deepseek")
    assert parsed.raw_decision.attribution == "llm_selected_tool_rendered"
    assert parsed.final_decision is not None
    assert parsed.final_decision.final_label == "1 per month"
    assert "decision_enum_shape_repaired:action" in parsed.parse_errors


def test_peer_selection_outside_recurring_cadence_gate_keeps_gpt() -> None:
    note_text = "No seizure frequency is documented; no events since February."
    parsed = cross_model_structured_event_adjudicator.parse_cross_model_decision_json(
        json.dumps(
            {
                "action": "select_deepseek_final",
                "selected_agent_id": "deepseek",
                "final_label": "seizure free for 8 month",
                "final_kind": "seizure_free",
                "selected_event_ids": ["e1"],
                "rejected_agent_ids": ["gpt"],
                "evidence": ["no events since February"],
                "comparison_profile": ["peer_seizure_free_over_boundary"],
                "calculation_trace": None,
                "clinical_rationale": "DeepSeek selected seizure freedom.",
                "uncertainty": "low",
                "attribution": "llm_selected_tool_rendered",
            }
        ),
        agent_rows={
            "gpt": _agent_row(
                975,
                label="no seizure frequency reference",
                kind="no_reference",
                evidence="No seizure frequency is documented",
            ),
            "qwen": _agent_row(
                975,
                label="seizure free for 8 month",
                kind="seizure_free",
                evidence="no events since February",
            ),
            "deepseek": _agent_row(
                975,
                label="seizure free for 8 month",
                kind="seizure_free",
                evidence="no events since February",
            ),
        },
        note_text=note_text,
    )

    assert parsed.final_decision is not None
    assert parsed.final_decision.final_label == "no seizure frequency reference"
    assert (
        "peer_selection_safety_gate_kept_gpt:peer_selection_not_in_high_precision_gate"
        in parsed.action_render_events
    )


def test_boundary_peer_rescue_is_allowed_for_isolated_numeric_gpt_label() -> None:
    gpt_evidence = "a very infrequent, short event a fortnight ago"
    note_text = f"She reports {gpt_evidence}."
    parsed = cross_model_structured_event_adjudicator.parse_cross_model_decision_json(
        json.dumps(
            {
                "action": "select_qwen_final",
                "selected_agent_id": "qwen",
                "final_label": "no seizure frequency reference",
                "final_kind": "no_reference",
                "selected_event_ids": ["e1"],
                "rejected_agent_ids": ["gpt", "deepseek"],
                "evidence": [gpt_evidence],
                "comparison_profile": ["boundary_peer_rescue"],
                "calculation_trace": "isolated last-event evidence is not a cadence",
                "clinical_rationale": "Qwen preserved the boundary state.",
                "uncertainty": "low",
                "attribution": "llm_selected_tool_rendered",
            }
        ),
        agent_rows={
            "gpt": _agent_row(
                976,
                label="1 per 2 week",
                kind="frequency",
                evidence=gpt_evidence,
            ),
            "qwen": _agent_row(
                976,
                label="no seizure frequency reference",
                kind="no_reference",
                evidence=gpt_evidence,
            ),
            "deepseek": _agent_row(
                976,
                label="1 per 2 week",
                kind="frequency",
                evidence=gpt_evidence,
            ),
        },
        note_text=note_text,
    )

    assert parsed.final_decision is not None
    assert parsed.final_decision.final_label == "no seizure frequency reference"
    assert "rendered_selected_agent_final:qwen" in parsed.action_render_events
    assert not any(
        event.startswith("peer_selection_safety_gate_kept_gpt")
        for event in parsed.action_render_events
    )


def test_action_agent_mismatch_falls_back_to_gpt_final() -> None:
    note_text = "He now has a focal seizure about once monthly."
    parsed = cross_model_structured_event_adjudicator.parse_cross_model_decision_json(
        json.dumps(
            {
                "action": "select_qwen_final",
                "selected_agent_id": "deepseek",
                "final_label": "1 per month",
                "final_kind": "frequency",
                "selected_event_ids": ["e1"],
                "rejected_agent_ids": ["gpt"],
                "evidence": [note_text],
                "comparison_profile": ["inconsistent_action"],
                "calculation_trace": None,
                "clinical_rationale": "Malformed selector output.",
                "uncertainty": "medium",
                "attribution": "llm_selected_tool_rendered",
            }
        ),
        agent_rows={
            "gpt": _agent_row(
                972,
                label="unknown",
                kind="unknown",
                evidence=note_text,
            ),
            "qwen": _agent_row(
                972,
                label="1 per month",
                kind="frequency",
                evidence=note_text,
            ),
            "deepseek": _agent_row(
                972,
                label="1 per month",
                kind="frequency",
                evidence=note_text,
            ),
        },
        note_text=note_text,
    )

    assert parsed.final_decision is not None
    assert parsed.final_decision.final_label == "unknown"
    assert "action_render_error:action_agent_mismatch" in parsed.parse_errors
    assert "action_render_fallback_kept_gpt:action_agent_mismatch" in parsed.action_render_events


def test_live_cross_model_adjudicator_scores_qwen_rescue(monkeypatch) -> None:
    gpt_evidence = "only seven focal seizures reported so far this year"
    peer_evidence = "typical pattern is a focal seizure monthly"
    note_text = f"{gpt_evidence}; {peer_evidence}."

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
                "action": "select_qwen_final",
                "selected_agent_id": "qwen",
                "final_label": "1 per month",
                "final_kind": "frequency",
                "selected_event_ids": ["e1"],
                "rejected_agent_ids": ["gpt", "deepseek"],
                "evidence": [peer_evidence],
                "comparison_profile": ["peer_recurring_cadence_beats_gpt_unknown"],
                "calculation_trace": "monthly cadence is explicitly stated",
                "clinical_rationale": "Qwen selected the explicit current cadence.",
                "uncertainty": "low",
                "attribution": "llm_selected_tool_rendered",
            }
        )

    monkeypatch.setattr(
        cross_model_structured_event_adjudicator,
        "_run_model_call",
        fake_model_call,
    )

    rows, metadata = cross_model_structured_event_adjudicator.run_split(
        [
            _record(
                973,
                note_text,
                gold_label="1 per month",
                gold_monthly_frequency=1.0138888888888888,
            )
        ],
        structured_event_rows=[
            _agent_row(
                973,
                label="7 per 10 month",
                kind="frequency",
                evidence=gpt_evidence,
                purist_correct=False,
            )
        ],
        structured_event_source_path=Path("gpt.jsonl"),
        agent_rows_by_id={
            "qwen": [
                _agent_row(
                    973,
                    label="1 per month",
                    kind="frequency",
                    evidence=peer_evidence,
                    purist_correct=True,
                )
            ],
            "deepseek": [
                _agent_row(
                    973,
                    label="1 per month",
                    kind="frequency",
                    evidence=peer_evidence,
                    purist_correct=True,
                )
            ],
        },
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
    assert metadata["summary"]["wrong_to_correct_vs_v0"] == 1
    assert metadata["summary"]["correct_to_wrong_vs_v0"] == 0
    assert metadata["summary"]["selected_agent_counts"] == {"qwen": 1}
    assert row["score_layers"]["final"]["final_label"] == "1 per month"
    assert row["transition_vs_v0"]["purist_transition"] == "wrong_to_correct"
    assert row["decision_record"]["selected_event_ids"] == ["qwen:e1"]
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


def _agent_row(
    source_row_index: int,
    *,
    label: str,
    kind: str,
    evidence: str,
    purist_correct: bool = False,
) -> dict:
    return {
        "source_row_index": source_row_index,
        "prompt_version": "fixture_structured_events",
        "structured_record": {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate" if kind == "frequency" else "unknown_frequency",
                    "raw_value": label,
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "applies_to": "seizures",
                    "evidence": evidence,
                    "time_window": "current",
                    "notes": "fixture event",
                }
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": kind,
                "final_label": label,
                "evidence": evidence,
                "confidence": "high",
                "rationale": f"Fixture selected {label}.",
            },
        },
        "normalized_events": [
            {
                "event_id": "e1",
                "normalized_label": label,
                "semantic_kind": kind,
                "monthly_frequency": 1.0138888888888888 if label == "1 per month" else 1000.0,
                "validation_errors": [],
            }
        ],
        "comparison": {
            "purist_correct": purist_correct,
            "pragmatic_correct": purist_correct,
        },
        "evidence_valid": True,
    }
