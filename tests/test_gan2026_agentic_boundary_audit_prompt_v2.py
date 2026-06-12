from __future__ import annotations

import json

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    boundary_audit_prompt_v2,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord


def test_boundary_audit_prompt_uses_fixed_guides_without_parser_context(monkeypatch) -> None:
    prompts: list[dict] = []

    def fake_model_call(
        prompt_input_json: str,
        *,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        del model, temperature, max_tokens
        prompts.append(json.loads(prompt_input_json))
        return json.dumps(
            {
                "current_frequency_evidence": ["She reports 2 seizures per week"],
                "active_semiologies_and_burdens": ["seizures: 2 per week"],
                "cluster_cadence_and_burden": None,
                "boundary_hazards": [],
                "rejected_lower_burden_or_historical_alternatives": [],
                "final_label": "2 per week",
                "evidence": "She reports 2 seizures per week",
                "answer_kind": "frequency",
                "selected_seizure_type": "seizures",
                "time_window": "current",
                "confidence": "high",
                "rationale": "The current frequency is 2 seizures per week.",
            }
        )

    monkeypatch.setattr(boundary_audit_prompt_v2, "_run_model_call", fake_model_call)

    rows, metadata = boundary_audit_prompt_v2.run_split(
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

    assert rows[0]["decision_record"]["final_label"] == "2 per week"
    assert metadata["summary"]["purist_correct"] == 1
    assert metadata["summary"]["wins_vs_reference"] == 1
    assert metadata["summary"]["parser_context_disabled"] is True
    prompt = prompts[0]
    assert "parser_result" not in prompt["tool_context"]
    assert set(prompt["tool_context"]) == {
        "boundary_guides",
        "tool_attribution_boundary",
    }
    guide_ids = {
        guide["guide_id"] for guide in prompt["tool_context"]["boundary_guides"]
    }
    assert guide_ids == set(boundary_audit_prompt_v2.FIXED_BOUNDARY_GUIDE_IDS)


def test_boundary_audit_gate_rejects_sentinel_regression(monkeypatch) -> None:
    def fake_model_call(
        prompt_input_json: str,
        *,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        del prompt_input_json, model, temperature, max_tokens
        return json.dumps(
            {
                "current_frequency_evidence": [],
                "active_semiologies_and_burdens": [],
                "cluster_cadence_and_burden": None,
                "boundary_hazards": ["seizure-free wording"],
                "rejected_lower_burden_or_historical_alternatives": [],
                "final_label": "seizure free for multiple year",
                "evidence": "seizure free for years",
                "answer_kind": "seizure_free",
                "selected_seizure_type": None,
                "time_window": "current",
                "confidence": "medium",
                "rationale": "The note appears seizure-free.",
            }
        )

    monkeypatch.setattr(boundary_audit_prompt_v2, "_run_model_call", fake_model_call)

    rows, metadata = boundary_audit_prompt_v2.run_split(
        [_record(source_row_index=5534)],
        reference_rows=[_reference_row("2 per week", source_row_index=5534)],
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

    assert rows[0]["comparison"]["purist_correct"] is False
    assert metadata["summary"]["e2_loss_sentinel_regressions"] == 1
    assert metadata["gate"]["status"] == "reject_or_revise_before_hard50"


def test_audit_shape_repair_accepts_object_audit_items() -> None:
    raw_output = json.dumps(
        {
            "current_frequency_evidence": [
                {"text": "She reports 2 seizures per week"}
            ],
            "active_semiologies_and_burdens": [
                {"semiology": "seizures", "burden": "2 per week"}
            ],
            "cluster_cadence_and_burden": {"cadence": None, "burden": None},
            "boundary_hazards": [{"hazard": "none"}],
            "rejected_lower_burden_or_historical_alternatives": [],
            "final_label": "2 per week",
            "evidence": "She reports 2 seizures per week",
            "answer_kind": "frequency",
            "selected_seizure_type": "seizures",
            "time_window": "current",
            "confidence": "high",
            "rationale": "The current frequency is 2 seizures per week.",
        }
    )

    decision, errors = boundary_audit_prompt_v2.parse_audit_decision_json(raw_output)

    assert decision is not None
    assert decision.final_label == "2 per week"
    assert any(error.startswith("audit_field_shape_repaired:") for error in errors)
    assert isinstance(decision.active_semiologies_and_burdens[0], str)


def test_hard50_gate_uses_wins_losses_and_changed_precision() -> None:
    gate = boundary_audit_prompt_v2.gate_interpretation(
        {
            "wins_vs_reference": 5,
            "losses_vs_reference": 1,
            "changed_label_precision": 0.625,
            "parse_or_validation_failures": 0,
            "parser_context_disabled": True,
        },
        surface="hard50",
    )

    assert gate["status"] == "pass_hard50_gate"


def _record(source_row_index: int = 401) -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=source_row_index,
        note_text=(
            "Clinic Date: 12 June 2026\n"
            "She reports 2 seizures per week and keeps a diary."
        ),
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
