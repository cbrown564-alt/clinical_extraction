from __future__ import annotations

import json
from pathlib import Path

import pytest

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    cross_model_challenge_adjudicator,
    llm_event_reasoner,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.run_driver import (
    AgenticSplitHooks,
    CrossModelSplitContext,
    RegisteredAgenticStage,
    SplitRunParams,
    dispatch_registered_split,
    register_agentic_stage,
    registered_agentic_stages,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord


def test_cross_model_challenge_stage_is_registered() -> None:
    stages = registered_agentic_stages()

    assert "cross_model_challenge_adjudicator" in stages
    stage = stages["cross_model_challenge_adjudicator"]
    assert stage.dispatch_kind == "cross_model_structured_event"
    assert stage.module.endswith("cross_model_challenge_adjudicator")


def test_register_agentic_stage_rejects_conflicting_reregistration() -> None:
    stage = RegisteredAgenticStage(
        stage_id="fixture_conflict_stage",
        dispatch_kind="standard",
        module="tests.fixture",
        description="fixture",
    )
    register_agentic_stage(stage)

    with pytest.raises(ValueError, match="already registered"):
        register_agentic_stage(
            RegisteredAgenticStage(
                stage_id="fixture_conflict_stage",
                dispatch_kind="structured_event",
                module="tests.other",
            )
        )


def test_dispatch_unknown_stage_raises_key_error() -> None:
    params = SplitRunParams(
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=2000,
        mode="prompt-only",
        dspy_cache=True,
        api_base=None,
    )
    hooks = AgenticSplitHooks(
        prompt_version="fixture",
        metadata_extra={},
        build_row=lambda record, **kwargs: {"source_row_index": record.source_row_index},
        summarize_rows=lambda rows: {"rows": len(rows)},
    )

    with pytest.raises(KeyError, match="unknown agentic stage"):
        dispatch_registered_split(
            "definitely_not_a_registered_stage",
            [],
            params=params,
            hooks=hooks,
        )


def test_dispatch_cross_model_matches_direct_run_split(monkeypatch) -> None:
    gpt_evidence = "only seven focal seizures reported so far this year"
    peer_evidence = "typical pattern is a focal seizure monthly"
    note_text = f"{gpt_evidence}; {peer_evidence}."
    record = _record(
        982,
        note_text,
        gold_label="1 per month",
        gold_monthly_frequency=1.0138888888888888,
    )
    structured_event_rows = [
        _agent_row(
            982,
            label="7 per 10 month",
            kind="frequency",
            evidence=gpt_evidence,
            purist_correct=False,
        )
    ]
    agent_rows_by_id = {
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
    }

    def fake_model_call(
        prompt_input_json: str,
        *,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        del model, temperature, max_tokens
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

    split_kwargs = {
        "structured_event_rows": structured_event_rows,
        "structured_event_source_path": Path("gpt.jsonl"),
        "agent_rows_by_id": agent_rows_by_id,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "model": "openai/gpt-4.1-mini",
        "temperature": 0.0,
        "max_tokens": 2000,
        "mode": "live",
        "dspy_cache": True,
        "api_base": None,
        "escalation_reason": None,
        "progress_every": None,
        "checkpoint_jsonl_path": None,
        "checkpoint_report_path": None,
    }

    direct_rows, direct_metadata = cross_model_challenge_adjudicator.run_split(
        [record],
        **split_kwargs,
    )
    dispatched_rows, dispatched_metadata = dispatch_registered_split(
        cross_model_challenge_adjudicator.STAGE_ID,
        [record],
        params=SplitRunParams(
            split=split_kwargs["split"],
            split_manifest=split_kwargs["split_manifest"],
            model=split_kwargs["model"],
            temperature=split_kwargs["temperature"],
            max_tokens=split_kwargs["max_tokens"],
            mode=split_kwargs["mode"],
            dspy_cache=split_kwargs["dspy_cache"],
            api_base=split_kwargs["api_base"],
        ),
        hooks=AgenticSplitHooks(
            prompt_version=cross_model_challenge_adjudicator.PROMPT_VERSION,
            metadata_extra={
                "artifact_kind": "gan2026_cross_model_challenge_adjudicator_trace",
                "pipeline_family": cross_model_challenge_adjudicator.PIPELINE_FAMILY,
                "pipeline_version": cross_model_challenge_adjudicator.PROMPT_VERSION,
                "structured_event_source_role": (
                    "GPT, Qwen, and DeepSeek saved LLM structured-event finals are "
                    "peer candidates. Deterministic top labels are not shown or used."
                ),
                "claim_boundary": (
                    "validation-development V11 open cross-model challenge "
                    "adjudicator; no holdout use, no row-level test inspection, and "
                    "no benchmark claim"
                ),
                "safety_policy": cross_model_challenge_adjudicator._safety_policy_label("none"),
            },
            build_row=cross_model_challenge_adjudicator._build_row,
            summarize_rows=cross_model_challenge_adjudicator.summarize_rows,
            gate_interpretation=llm_event_reasoner.gate_interpretation,
            write_report=cross_model_challenge_adjudicator.write_report,
            progress_fields=("final_purist_correct", "net_purist_gain_vs_v0"),
        ),
        cross_model_context=CrossModelSplitContext(
            gpt_structured_event_source_path=Path("gpt.jsonl"),
            agent_source_paths={
                "gpt": Path("gpt.jsonl"),
                "qwen": cross_model_challenge_adjudicator.DEFAULT_QWEN_STRUCTURED_EVENT_JSONL_PATH,
                "deepseek": (
                    cross_model_challenge_adjudicator.DEFAULT_DEEPSEEK_STRUCTURED_EVENT_JSONL_PATH
                ),
            },
            gpt_structured_event_rows=structured_event_rows,
            agent_rows_by_id=agent_rows_by_id,
            row_kwargs={"safety_policy": "none"},
        ),
    )

    assert direct_rows == dispatched_rows
    assert _metadata_without_timestamps(direct_metadata) == _metadata_without_timestamps(
        dispatched_metadata
    )


def _metadata_without_timestamps(metadata: dict) -> dict:
    filtered = dict(metadata)
    filtered.pop("created_at_utc", None)
    filtered.pop("date", None)
    return filtered


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
                "monthly_frequency": 1.0138888888888888
                if label == "1 per month"
                else 1000.0,
                "validation_errors": [],
            }
        ],
        "comparison": {
            "purist_correct": purist_correct,
            "pragmatic_correct": purist_correct,
        },
        "evidence_valid": True,
    }
