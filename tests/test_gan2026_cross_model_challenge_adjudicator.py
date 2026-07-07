from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    cross_model_challenge_adjudicator,
    cross_model_structured_event_adjudicator,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.cli.llm_pipeline_cli import (
    pipeline_specs,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord


def test_cross_model_challenge_adjudicator_is_registered() -> None:
    spec = pipeline_specs()["cross_model_challenge_adjudicator"]

    assert "open cross-model challenge" in spec.description
    assert spec.default_max_tokens == 2000
    assert spec.default_structured_event_jsonl_path is not None


def test_cross_model_challenge_gated_adjudicator_is_registered() -> None:
    spec = pipeline_specs()["cross_model_challenge_gated_adjudicator"]

    assert "high-precision peer-selection gate" in spec.description
    assert spec.default_jsonl_path.name == (
        "gan2026_cross_model_challenge_gated_adjudicator_validation.jsonl"
    )
    assert spec.default_max_tokens == 2000
    assert spec.default_structured_event_jsonl_path is not None


def test_challenge_prompt_is_peer_focused_and_excludes_forbidden_context() -> None:
    record = _record(
        980,
        "Clinic Date: 12 June 2026\nThe typical pattern is one focal seizure monthly.",
        gold_label="1 per month",
        gold_monthly_frequency=1.0138888888888888,
    )
    prompt_input_json = cross_model_challenge_adjudicator.build_prompt_input(
        record,
        {
            "gpt": _agent_row(
                980,
                label="7 per 10 month",
                kind="frequency",
                evidence="seven focal seizures reported so far this year",
            ),
            "qwen": _agent_row(
                980,
                label="1 per month",
                kind="frequency",
                evidence="one focal seizure monthly",
            ),
            "deepseek": _agent_row(
                980,
                label="1 per month",
                kind="frequency",
                evidence="one focal seizure monthly",
            ),
        },
    )
    payload = json.loads(prompt_input_json)
    payload_text = json.dumps(payload, ensure_ascii=False)

    assert "source_row_index" not in payload_text
    assert "gold_label" not in payload_text
    assert "gan2026_split_v1" not in payload_text
    assert "deterministic_top" not in payload_text
    assert payload["variant"] == "V11_cross_model_challenge_adjudicator"
    assert "do not default to GPT" in " ".join(payload["instructions"])
    assert "Prefer GPT unless" not in " ".join(payload["instructions"])


def test_challenge_parse_allows_peer_selection_outside_v10_gate() -> None:
    note_text = "No seizure frequency is documented; no events since February."
    parsed = cross_model_structured_event_adjudicator.parse_cross_model_decision_json(
        json.dumps(
            {
                "action": "select_deepseek_final",
                "selected_agent_id": "deepseek",
                "final_label": "seizure free for 8 month",
                "final_kind": "seizure_free",
                "selected_event_ids": ["e1"],
                "rejected_agent_ids": ["gpt", "qwen"],
                "evidence": ["no events since February"],
                "comparison_profile": ["peer_challenge_seizure_free"],
                "calculation_trace": None,
                "clinical_rationale": "DeepSeek selected sustained seizure freedom.",
                "uncertainty": "medium",
                "attribution": "llm_selected_tool_rendered",
            }
        ),
        agent_rows={
            "gpt": _agent_row(
                981,
                label="no seizure frequency reference",
                kind="no_reference",
                evidence="No seizure frequency is documented",
            ),
            "qwen": _agent_row(
                981,
                label="unknown",
                kind="unknown",
                evidence="No seizure frequency is documented",
            ),
            "deepseek": _agent_row(
                981,
                label="seizure free for 8 month",
                kind="seizure_free",
                evidence="no events since February",
            ),
        },
        note_text=note_text,
        safety_policy="none",
    )

    assert parsed.final_decision is not None
    assert parsed.final_decision.final_label == "seizure free for 8 month"
    assert "rendered_selected_agent_final:deepseek" in parsed.action_render_events
    assert not any(
        event.startswith("peer_selection_safety_gate_kept_gpt")
        for event in parsed.action_render_events
    )


def test_challenge_parser_repairs_escaped_list_item_quotes() -> None:
    note_text = "He reports a current seizure frequency of 17 per month."
    raw_output = (
        "{\n"
        '  "selected_agent_id": "deepseek",\n'
        '  "selected_event_ids": ["e1"],\n'
        '  "final_label": "17 per month",\n'
        '  "final_kind": "frequency",\n'
        '  "uncertainty": "low",\n'
        '  "clinical_rationale": "DeepSeek cites the exact current frequency.",\n'
        '  "evidence": [\n'
        '    \\"He reports a current seizure frequency of 17 per month\\"\n'
        "  ],\n"
        '  "comparison_profile": [],\n'
        '  "rejected_agent_ids": "gpt,qwen",\n'
        '  "attribution": "llm_selected_tool_rendered",\n'
        '  "calculation_trace": null\n'
        "}"
    )

    parsed = cross_model_structured_event_adjudicator.parse_cross_model_decision_json(
        raw_output,
        agent_rows={
            "gpt": _agent_row(
                983,
                label="17 per month",
                kind="frequency",
                evidence=note_text,
            ),
            "qwen": _agent_row(
                983,
                label="17 per month",
                kind="frequency",
                evidence=note_text,
            ),
            "deepseek": _agent_row(
                983,
                label="17 per month",
                kind="frequency",
                evidence=note_text,
            ),
        },
        note_text=note_text,
        safety_policy="none",
    )

    assert parsed.final_decision is not None
    assert parsed.final_decision.final_label == "17 per month"
    assert "json_dialect_repaired: escaped_list_item_quotes" in parsed.parse_errors


def test_live_challenge_adjudicator_scores_peer_rescue(monkeypatch) -> None:
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
        assert "do not default to GPT" in prompt_input_json
        return json.dumps(
            {
                "action": "select_qwen_final",
                "selected_agent_id": "qwen",
                "final_label": "1 per month",
                "final_kind": "frequency",
                "selected_event_ids": ["e1"],
                "rejected_agent_ids": ["gpt", "deepseek"],
                "evidence": [peer_evidence],
                "comparison_profile": ["peer_challenge_recurring_cadence"],
                "calculation_trace": "monthly cadence is explicitly stated",
                "clinical_rationale": "Qwen selected the explicit current cadence.",
                "uncertainty": "low",
                "attribution": "llm_selected_tool_rendered",
            }
        )

    monkeypatch.setattr(
        cross_model_challenge_adjudicator,
        "_run_model_call",
        fake_model_call,
    )

    rows, metadata = cross_model_challenge_adjudicator.run_split(
        [
            _record(
                982,
                note_text,
                gold_label="1 per month",
                gold_monthly_frequency=1.0138888888888888,
            )
        ],
        structured_event_rows=[
            _agent_row(
                982,
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
                    982,
                    label="1 per month",
                    kind="frequency",
                    evidence=peer_evidence,
                    purist_correct=True,
                )
            ],
            "deepseek": [
                _agent_row(
                    982,
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
        max_tokens=2000,
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


def test_gated_challenge_variant_records_high_precision_policy(monkeypatch) -> None:
    note_text = "No seizure frequency is documented; no events since February."

    def fake_model_call(
        prompt_input_json: str,
        *,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        del model, temperature, max_tokens
        assert "do not default to GPT" in prompt_input_json
        return json.dumps(
            {
                "action": "select_deepseek_final",
                "selected_agent_id": "deepseek",
                "final_label": "seizure free for 8 month",
                "final_kind": "seizure_free",
                "selected_event_ids": ["e1"],
                "rejected_agent_ids": ["gpt", "qwen"],
                "evidence": ["no events since February"],
                "comparison_profile": ["peer_challenge_seizure_free"],
                "calculation_trace": None,
                "clinical_rationale": "DeepSeek selected sustained seizure freedom.",
                "uncertainty": "medium",
                "attribution": "llm_selected_tool_rendered",
            }
        )

    monkeypatch.setattr(
        cross_model_challenge_adjudicator,
        "_run_model_call",
        fake_model_call,
    )

    rows, metadata = cross_model_challenge_adjudicator.run_split(
        [
            _record(
                984,
                note_text,
                gold_label="no seizure frequency reference",
                gold_monthly_frequency=1000.0,
            )
        ],
        structured_event_rows=[
            _agent_row(
                984,
                label="no seizure frequency reference",
                kind="no_reference",
                evidence="No seizure frequency is documented",
                purist_correct=True,
            )
        ],
        structured_event_source_path=Path("gpt.jsonl"),
        agent_rows_by_id={
            "qwen": [
                _agent_row(
                    984,
                    label="unknown",
                    kind="unknown",
                    evidence="No seizure frequency is documented",
                    purist_correct=True,
                )
            ],
            "deepseek": [
                _agent_row(
                    984,
                    label="seizure free for 8 month",
                    kind="seizure_free",
                    evidence="no events since February",
                    purist_correct=False,
                )
            ],
        },
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=2000,
        mode="live",
        dspy_cache=True,
        api_base=None,
        escalation_reason=None,
        progress_every=None,
        checkpoint_jsonl_path=None,
        checkpoint_report_path=None,
        safety_policy="high_precision",
    )

    assert metadata["safety_policy"] == "high_precision_peer_gate"
    assert metadata["summary"]["safety_policy"] == "high_precision_peer_gate"
    assert rows[0]["decision_record"]["final_label"] == "no seizure frequency reference"
    assert (
        "peer_selection_safety_gate_kept_gpt:peer_selection_not_in_high_precision_gate"
        in rows[0]["action_render_events"]
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
                    "kind": "frequency_rate" if kind == "frequency" else kind,
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
