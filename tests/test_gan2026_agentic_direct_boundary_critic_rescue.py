from __future__ import annotations

import json

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    direct_boundary_critic_rescue,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord


def test_direct_boundary_critic_uses_guides_without_parser_context(monkeypatch) -> None:
    prompts: list[dict] = []

    def fake_model_call(
        prompt_input_json: str,
        *,
        call_role: str,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        del model, temperature, max_tokens
        prompts.append(json.loads(prompt_input_json))
        if call_role == "direct_no_tool_final_label":
            return json.dumps(_direct_payload(final_label="1 per month"))
        return json.dumps(
            _critic_payload(
                action="raise_current_burden",
                proposed_final_label="2 per week",
                evidence="She reports 2 seizures per week",
                higher_current_burden_evidence="She reports 2 seizures per week",
            )
        )

    monkeypatch.setattr(
        direct_boundary_critic_rescue,
        "_run_model_call",
        fake_model_call,
    )

    rows, metadata = direct_boundary_critic_rescue.run_split(
        [_record()],
        reference_rows=[_reference_row("unknown")],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=1200,
        mode="live",
        dspy_cache=True,
        api_base=None,
        progress_every=None,
        checkpoint_jsonl_path=None,
        checkpoint_report_path=None,
    )

    assert rows[0]["final_label"] == "2 per week"
    assert rows[0]["accepted_action"] == "raise_current_burden"
    assert metadata["summary"]["accepted_rescue_correct"] == 1
    assert metadata["summary"]["parser_context_disabled"] is True
    for prompt in prompts:
        assert "parser_result" not in prompt.get("tool_context", {})
    critic_prompt = prompts[1]
    assert set(critic_prompt["tool_context"]) == {
        "boundary_guides",
        "direct_answer",
        "tool_attribution_boundary",
    }
    guide_ids = {
        guide["guide_id"] for guide in critic_prompt["tool_context"]["boundary_guides"]
    }
    assert guide_ids == set(direct_boundary_critic_rescue.FIXED_BOUNDARY_GUIDE_IDS)


def test_boundary_demotion_override_is_blocked(monkeypatch) -> None:
    def fake_model_call(
        prompt_input_json: str,
        *,
        call_role: str,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        del prompt_input_json, model, temperature, max_tokens
        if call_role == "direct_no_tool_final_label":
            return json.dumps(_direct_payload(final_label="2 per week"))
        return json.dumps(
            _critic_payload(
                action="raise_current_burden",
                proposed_final_label="unknown",
                evidence="She reports 2 seizures per week",
                higher_current_burden_evidence="She reports 2 seizures per week",
            )
        )

    monkeypatch.setattr(
        direct_boundary_critic_rescue,
        "_run_model_call",
        fake_model_call,
    )

    rows, metadata = direct_boundary_critic_rescue.run_split(
        [_record()],
        reference_rows=[_reference_row("2 per week")],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=1200,
        mode="live",
        dspy_cache=True,
        api_base=None,
        progress_every=None,
        checkpoint_jsonl_path=None,
        checkpoint_report_path=None,
    )

    assert rows[0]["final_label"] == "2 per week"
    assert rows[0]["accepted_action"] == "fallback"
    assert rows[0]["action_policy"]["blocked_reason"] == "boundary_label_override_blocked"
    assert metadata["summary"]["accepted_boundary_demotions"] == 0


def test_restore_cluster_burden_requires_cluster_cadence_and_burden_evidence() -> None:
    direct = direct_boundary_critic_rescue.DirectDecisionRecord.model_validate(
        _direct_payload(final_label="1 per month")
    )
    critic = direct_boundary_critic_rescue.BoundaryCriticDecisionRecord.model_validate(
        _critic_payload(
            action="restore_cluster_burden",
            proposed_final_label="1 cluster per month, multiple per cluster",
            evidence="cluster days roughly once per month, usually five spells",
            cluster_cadence_evidence="cluster days roughly once per month",
            events_per_cluster_evidence="usually five spells",
        )
    )

    policy = direct_boundary_critic_rescue.apply_action_policy(
        _record(
            note_text=(
                "She reports cluster days roughly once per month, usually five spells."
            )
        ),
        direct,
        critic,
    )

    assert policy["final_label"] == "1 cluster per month, multiple per cluster"
    assert policy["accepted_action"] == "restore_cluster_burden"


def test_critic_shape_repair_accepts_boolean_and_numeric_audit_fields() -> None:
    raw_output = json.dumps(
        {
            "action": "keep",
            "proposed_final_label": None,
            "evidence": "She reports 2 seizures per week",
            "cluster_cadence_evidence": "",
            "events_per_cluster_evidence": "",
            "higher_current_burden_evidence": None,
            "boundary_demotion_hazard": False,
            "confidence": 0.95,
            "rationale": "The direct answer should be kept.",
        }
    )

    decision, errors = direct_boundary_critic_rescue.parse_critic_decision_json(
        raw_output
    )

    assert decision is not None
    assert decision.action == "keep"
    assert decision.confidence == "high"
    assert decision.boundary_demotion_hazard == "False"
    assert any(error.startswith("critic_field_shape_repaired:") for error in errors)


def test_gate_interpretation_enforces_panel_and_hard50_rules() -> None:
    panel_gate = direct_boundary_critic_rescue.gate_interpretation(
        {
            "accepted_rescue_correct": 4,
            "accepted_boundary_demotions": 0,
            "parse_or_validation_failures": 0,
        },
        surface="panel",
    )
    hard50_gate = direct_boundary_critic_rescue.gate_interpretation(
        {
            "wins_vs_reference": 5,
            "losses_vs_reference": 1,
            "changed_label_precision": 0.7,
            "parse_or_validation_failures": 0,
        },
        surface="hard50",
    )

    assert panel_gate["status"] == "pass_panel_gate"
    assert hard50_gate["status"] == "pass_hard50_gate"


def _record(
    source_row_index: int = 401,
    note_text: str = (
        "Clinic Date: 12 June 2026\n"
        "She reports 2 seizures per week and keeps a diary."
    ),
) -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=source_row_index,
        note_text=note_text,
        gold_label="2 per week",
        gold_reference="2 seizures per week",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label="2 per week",
        gold_label_kind=FrequencyLabelKind.FREQUENCY,
        gold_yearly_bounds=(104.0, 104.0),
        gold_monthly_frequency=8.690476190476192,
    )


def _reference_row(label: str, source_row_index: int = 401) -> dict:
    return {
        "source_row_index": source_row_index,
        "condition_traces": {
            "single_self_consistency_temperature": {
                "final_label": label,
            }
        },
    }


def _direct_payload(final_label: str) -> dict:
    return {
        "final_label": final_label,
        "evidence": "She reports 2 seizures per week",
        "answer_kind": "frequency",
        "selected_seizure_type": "seizures",
        "time_window": "current",
        "confidence": "high",
        "rationale": "The current frequency is stated in the note.",
    }


def _critic_payload(
    *,
    action: str,
    proposed_final_label: str | None,
    evidence: str,
    cluster_cadence_evidence: str | None = None,
    events_per_cluster_evidence: str | None = None,
    higher_current_burden_evidence: str | None = None,
) -> dict:
    return {
        "action": action,
        "proposed_final_label": proposed_final_label,
        "evidence": evidence,
        "cluster_cadence_evidence": cluster_cadence_evidence,
        "events_per_cluster_evidence": events_per_cluster_evidence,
        "higher_current_burden_evidence": higher_current_burden_evidence,
        "boundary_demotion_hazard": None,
        "confidence": "high",
        "rationale": "The critic found a conservative rescue action.",
    }
