from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    cross_model_challenge_adjudicator,
    cross_model_structured_event_adjudicator,
    llm_event_reasoner,
    structured_event_verifier,
    targeted_boundary_router,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.run_driver import (
    AgenticSplitHooks,
    CrossModelSplitContext,
    SplitRunParams,
    StructuredEventSplitContext,
    dispatch_registered_split,
    registered_agentic_stages,
)
from tests.helpers.gan2026_agentic_run_driver_fixtures import (
    agent_row as _agent_row,
)
from tests.helpers.gan2026_agentic_run_driver_fixtures import (
    metadata_without_timestamps as _metadata_without_timestamps,
)
from tests.helpers.gan2026_agentic_run_driver_fixtures import (
    record as _record,
)
from tests.helpers.gan2026_agentic_run_driver_fixtures import (
    router_structured_event_row as _router_structured_event_row,
)


def test_targeted_boundary_router_stage_is_registered() -> None:
    stages = registered_agentic_stages()

    assert "targeted_boundary_router" in stages
    stage = stages["targeted_boundary_router"]
    assert stage.dispatch_kind == "structured_event"
    assert stage.module.endswith("targeted_boundary_router")


def test_dispatch_targeted_boundary_router_matches_direct_run_split(monkeypatch) -> None:
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
                "final_label": "unknown",
                "final_kind": "unknown",
                "selected_event_ids": ["e2"],
                "rejected_event_ids": ["e1"],
                "evidence": ["spells are uncommon when meals are regular"],
                "contradiction_profile": ["router:sentinel_boundary"],
                "calculation_trace": "anchored count is not a recurring cadence",
                "clinical_rationale": (
                    "The numeric count is anchored to named occasions, while e2 "
                    "states an unquantified current pattern."
                ),
                "uncertainty": "low",
                "tool_calls": [],
                "attribution": "llm_selected_tool_rendered",
            }
        )

    monkeypatch.setattr(targeted_boundary_router, "_run_model_call", fake_model_call)

    record = _record(
        921,
        "Clinic Date: 12 June 2026\nspells are uncommon when meals are regular.",
        gold_label="unknown",
        gold_monthly_frequency=1000.0,
    )
    structured_event_rows = [
        _router_structured_event_row(
            921,
            final_label="2 per 3 month",
            final_kind="frequency",
            purist_correct=False,
        )
    ]
    split_kwargs = {
        "structured_event_rows": structured_event_rows,
        "structured_event_source_path": Path("v0.jsonl"),
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

    direct_rows, direct_metadata = targeted_boundary_router.run_split(
        [record],
        **split_kwargs,
    )
    dispatched_rows, dispatched_metadata = dispatch_registered_split(
        targeted_boundary_router.STAGE_ID,
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
            prompt_version=targeted_boundary_router.PROMPT_VERSION,
            metadata_extra={
                "artifact_kind": "gan2026_targeted_boundary_router_trace",
                "pipeline_family": targeted_boundary_router.PIPELINE_FAMILY,
                "pipeline_version": targeted_boundary_router.PROMPT_VERSION,
                "structured_event_source_role": (
                    "pure structured-event V0 comparator and router substrate; "
                    "the router action owns any selected replacement event"
                ),
                "claim_boundary": (
                    "validation-development V3 targeted router scaffold; no holdout "
                    "use, no row-level test inspection, and no benchmark claim"
                ),
            },
            build_row=targeted_boundary_router._build_row,
            summarize_rows=targeted_boundary_router.summarize_rows,
            gate_interpretation=structured_event_verifier.gate_interpretation,
            write_report=targeted_boundary_router.write_report,
            progress_fields=("final_purist_correct", "net_purist_gain_vs_v0"),
        ),
        structured_event_context=StructuredEventSplitContext(
            default_structured_event_jsonl_path=(
                targeted_boundary_router.DEFAULT_STRUCTURED_EVENT_JSONL_PATH
            ),
            structured_event_rows=structured_event_rows,
            structured_event_source_path=Path("v0.jsonl"),
            rows_by_source_index=llm_event_reasoner._rows_by_source_index,
        ),
    )

    assert direct_rows == dispatched_rows
    assert _metadata_without_timestamps(direct_metadata) == _metadata_without_timestamps(
        dispatched_metadata
    )


def test_cross_model_structured_event_adjudicator_stage_is_registered() -> None:
    stages = registered_agentic_stages()

    assert "cross_model_structured_event_adjudicator" in stages
    stage = stages["cross_model_structured_event_adjudicator"]
    assert stage.dispatch_kind == "cross_model_structured_event"
    assert stage.module.endswith("cross_model_structured_event_adjudicator")


def test_dispatch_cross_model_structured_event_adjudicator_matches_direct_run_split(
    monkeypatch,
) -> None:
    gpt_evidence = "only seven focal seizures reported so far this year"
    peer_evidence = "typical pattern is a focal seizure monthly"
    note_text = f"{gpt_evidence}; {peer_evidence}."
    record = _record(
        973,
        note_text,
        gold_label="1 per month",
        gold_monthly_frequency=1.0138888888888888,
    )
    structured_event_rows = [
        _agent_row(
            973,
            label="7 per 10 month",
            kind="frequency",
            evidence=gpt_evidence,
            purist_correct=False,
        )
    ]
    agent_rows_by_id = {
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
    }

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

    split_kwargs = {
        "structured_event_rows": structured_event_rows,
        "structured_event_source_path": Path("gpt.jsonl"),
        "agent_rows_by_id": agent_rows_by_id,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "model": "openai/gpt-4.1-mini",
        "temperature": 0.0,
        "max_tokens": 1800,
        "mode": "live",
        "dspy_cache": True,
        "api_base": None,
        "escalation_reason": None,
        "progress_every": None,
        "checkpoint_jsonl_path": None,
        "checkpoint_report_path": None,
    }

    direct_rows, direct_metadata = cross_model_structured_event_adjudicator.run_split(
        [record],
        **split_kwargs,
    )
    dispatched_rows, dispatched_metadata = dispatch_registered_split(
        cross_model_structured_event_adjudicator.STAGE_ID,
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
            prompt_version=cross_model_structured_event_adjudicator.PROMPT_VERSION,
            metadata_extra={
                "artifact_kind": "gan2026_cross_model_structured_event_adjudicator_trace",
                "pipeline_family": cross_model_structured_event_adjudicator.PIPELINE_FAMILY,
                "pipeline_version": (
                    f"{cross_model_structured_event_adjudicator.PROMPT_VERSION}+"
                    f"{cross_model_structured_event_adjudicator.SAFETY_GATE_VERSION}"
                ),
                "safety_gate_version": (
                    cross_model_structured_event_adjudicator.SAFETY_GATE_VERSION
                ),
                "structured_event_source_role": (
                    "GPT is the LLM structured-event fallback; Qwen and DeepSeek are "
                    "peer LLM structured-event candidates. Deterministic top labels "
                    "are not provided to the model or used as fallback."
                ),
                "claim_boundary": (
                    "validation-development V10 cross-model structured-event "
                    "adjudicator; no holdout use, no row-level test inspection, and "
                    "no benchmark claim"
                ),
            },
            build_row=cross_model_structured_event_adjudicator._build_row,
            summarize_rows=cross_model_structured_event_adjudicator.summarize_rows,
            gate_interpretation=llm_event_reasoner.gate_interpretation,
            write_report=cross_model_structured_event_adjudicator.write_report,
            progress_fields=("final_purist_correct", "net_purist_gain_vs_v0"),
        ),
        cross_model_context=CrossModelSplitContext(
            gpt_structured_event_source_path=Path("gpt.jsonl"),
            agent_source_paths={
                "gpt": Path("gpt.jsonl"),
                "qwen": (
                    cross_model_structured_event_adjudicator.DEFAULT_QWEN_STRUCTURED_EVENT_JSONL_PATH
                ),
                "deepseek": (
                    cross_model_structured_event_adjudicator.DEFAULT_DEEPSEEK_STRUCTURED_EVENT_JSONL_PATH
                ),
            },
            gpt_structured_event_rows=structured_event_rows,
            agent_rows_by_id=agent_rows_by_id,
        ),
    )

    assert direct_rows == dispatched_rows
    assert _metadata_without_timestamps(direct_metadata) == _metadata_without_timestamps(
        dispatched_metadata
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


