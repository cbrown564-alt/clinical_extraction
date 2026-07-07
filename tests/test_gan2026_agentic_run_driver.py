from __future__ import annotations

import json
from pathlib import Path

import pytest

# cross_model_structured_event_adjudicator must initialise before run_driver:
# run_driver reads its AGENT_IDS at import time while the adjudicator imports
# run_driver back, so importing run_driver first triggers a circular import.
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    cross_model_structured_event_adjudicator,  # noqa: F401  (import-order guard)
    llm_event_reasoner,
    tool_context_ablation,
    tool_self_consistency,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    runner as agentic_runner,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.run_driver import (
    AgenticSplitHooks,
    MatchedBudgetSplitContext,
    RegisteredAgenticStage,
    SplitRunParams,
    StructuredEventSplitContext,
    dispatch_registered_split,
    register_agentic_stage,
    registered_agentic_stages,
)
from tests.helpers.gan2026_agentic_run_driver_fixtures import (
    llm_reasoner_structured_event_row as _llm_reasoner_structured_event_row,
)
from tests.helpers.gan2026_agentic_run_driver_fixtures import (
    metadata_without_timestamps as _metadata_without_timestamps,
)
from tests.helpers.gan2026_agentic_run_driver_fixtures import (
    record as _record,
)


def test_runner_stage_is_registered() -> None:
    stages = registered_agentic_stages()

    assert "runner" in stages
    stage = stages["runner"]
    assert stage.dispatch_kind == "matched_budget"
    assert stage.module.endswith("runner")


def test_dispatch_runner_matches_direct_run_split(monkeypatch) -> None:
    def fake_model_call(
        prompt_input_json: str,
        *,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        del prompt_input_json, model, temperature, max_tokens
        return (
            '{"final_label":"2 per week","evidence":"2 seizures per week",'
            '"answer_kind":"frequency","selected_seizure_type":"seizure",'
            '"time_window":"current","confidence":"high",'
            '"rationale":"The note states 2 seizures per week."}'
        )

    monkeypatch.setattr(agentic_runner, "_run_model_call", fake_model_call)

    record = _record(
        1101,
        "Clinic Date: 12 June 2026\nShe has 2 seizures per week.",
        gold_label="2 per week",
        gold_monthly_frequency=8.666666666666666,
    )
    split_kwargs = {
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "model": "openai/gpt-4.1-mini",
        "temperature": 0.0,
        "max_tokens": 900,
        "mode": "live",
        "dspy_cache": True,
        "api_base": None,
        "escalation_reason": None,
        "progress_every": None,
        "checkpoint_jsonl_path": None,
        "checkpoint_report_path": None,
    }

    direct_rows, direct_metadata = agentic_runner.run_split([record], **split_kwargs)
    dispatched_rows, dispatched_metadata = dispatch_registered_split(
        agentic_runner.STAGE_ID,
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
            prompt_version=agentic_runner.PROMPT_VERSION,
            metadata_extra={
                "artifact_kind": "gan2026_agentic_matched_budget_trace",
                "pipeline_family": "agentic_matched_budget",
                "pipeline_version": "gan2026_agentic_phase6_live_v0",
                "claim_boundary": (
                    "validation-development matched-budget agentic trace; no holdout "
                    "use, no row-level test inspection, and no benchmark claim"
                ),
            },
            build_row=agentic_runner._build_row_trace,
            summarize_rows=agentic_runner.summarize_rows,
            write_report=agentic_runner.write_report,
        ),
        matched_budget_context=MatchedBudgetSplitContext(
            default_conditions=agentic_runner.DEFAULT_CONDITIONS,
            validate_conditions=agentic_runner._validate_conditions,
            default_budgets=agentic_runner._default_budgets,
        ),
    )

    assert direct_rows == dispatched_rows
    assert _metadata_without_timestamps(direct_metadata) == _metadata_without_timestamps(
        dispatched_metadata
    )


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


def test_llm_event_reasoner_stage_is_registered() -> None:
    stages = registered_agentic_stages()

    assert "llm_event_reasoner" in stages
    stage = stages["llm_event_reasoner"]
    assert stage.dispatch_kind == "structured_event"
    assert stage.module.endswith("llm_event_reasoner")


def test_dispatch_llm_event_reasoner_matches_direct_run_split(monkeypatch) -> None:
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

    record = _record(
        903,
        "Clinic Date: 12 June 2026\nPatient reports 2 seizures per week.",
        gold_label="2 per week",
        gold_monthly_frequency=8.69047619047619,
    )
    structured_event_rows = [
        _llm_reasoner_structured_event_row(
            903,
            final_label="1 per month",
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
        "max_tokens": 1600,
        "mode": "live",
        "dspy_cache": True,
        "api_base": None,
        "escalation_reason": None,
        "progress_every": None,
        "checkpoint_jsonl_path": None,
        "checkpoint_report_path": None,
    }

    direct_rows, direct_metadata = llm_event_reasoner.run_split(
        [record],
        **split_kwargs,
    )
    dispatched_rows, dispatched_metadata = dispatch_registered_split(
        llm_event_reasoner.STAGE_ID,
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
            prompt_version=llm_event_reasoner.PROMPT_VERSION,
            metadata_extra={
                "artifact_kind": "gan2026_llm_event_reasoner_trace",
                "pipeline_family": llm_event_reasoner.PIPELINE_FAMILY,
                "pipeline_version": llm_event_reasoner.PROMPT_VERSION,
                "structured_event_source_role": (
                    "pure structured-event V0 comparator and input substrate; not "
                    "a deterministic final-label floor"
                ),
                "claim_boundary": (
                    "validation-development Stage 1 scaffold; no holdout use, no "
                    "row-level test inspection, and no benchmark claim"
                ),
            },
            build_row=llm_event_reasoner._build_row,
            summarize_rows=llm_event_reasoner.summarize_rows,
            gate_interpretation=llm_event_reasoner.gate_interpretation,
            write_report=llm_event_reasoner.write_report,
            progress_fields=("final_purist_correct", "net_purist_gain_vs_v0"),
        ),
        structured_event_context=StructuredEventSplitContext(
            default_structured_event_jsonl_path=(
                llm_event_reasoner.DEFAULT_STRUCTURED_EVENT_JSONL_PATH
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


def test_tool_context_ablation_stage_is_registered() -> None:
    stages = registered_agentic_stages()

    assert "tool_context_ablation" in stages
    stage = stages["tool_context_ablation"]
    assert stage.dispatch_kind == "standard"
    assert stage.module.endswith("tool_context_ablation")


def test_dispatch_tool_context_ablation_matches_direct_run_split(monkeypatch) -> None:
    def fake_model_call(
        prompt_input_json: str,
        *,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        del model, temperature, max_tokens
        assert "deterministic_top" not in prompt_input_json
        return (
            '{"final_label":"2 per week","evidence":"2 seizures per week",'
            '"answer_kind":"frequency","selected_seizure_type":"seizure",'
            '"time_window":"current","confidence":"high",'
            '"rationale":"The note states 2 seizures per week."}'
        )

    monkeypatch.setattr(tool_context_ablation, "_run_model_call", fake_model_call)

    record = _record(
        201,
        "Clinic Date: 12 June 2026\nShe reports 2 seizures per week.",
        gold_label="2 per week",
        gold_monthly_frequency=8.690476190476192,
    )
    split_kwargs = {
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "model": "openai/gpt-4.1-mini",
        "temperature": 0.0,
        "max_tokens": 900,
        "mode": "live",
        "dspy_cache": True,
        "api_base": None,
        "progress_every": None,
        "checkpoint_jsonl_path": None,
        "checkpoint_report_path": None,
    }

    direct_rows, direct_metadata = tool_context_ablation.run_split(
        [record],
        **split_kwargs,
    )
    dispatched_rows, dispatched_metadata = dispatch_registered_split(
        tool_context_ablation.STAGE_ID,
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
            prompt_version=tool_context_ablation.PROMPT_VERSION,
            metadata_extra={
                "artifact_kind": "gan2026_agentic_tool_context_ablation",
                "pipeline_family": tool_context_ablation.PIPELINE_FAMILY,
                "pipeline_version": tool_context_ablation.PIPELINE_VERSION,
                "claim_boundary": (
                    "validation-development hard50 tool-context ablation; no holdout "
                    "use, no row-level test inspection, and no benchmark claim"
                ),
            },
            build_row=tool_context_ablation._build_row,
            summarize_rows=tool_context_ablation.summarize_rows,
            finalize_metadata=tool_context_ablation._finalize_metadata,
            write_report=tool_context_ablation.write_report,
            progress_fields=("call_failures", "parse_or_validation_failures"),
        ),
    )

    assert direct_rows == dispatched_rows
    assert _metadata_without_timestamps(direct_metadata) == _metadata_without_timestamps(
        dispatched_metadata
    )


def test_tool_self_consistency_stage_is_registered() -> None:
    stages = registered_agentic_stages()

    assert "tool_self_consistency" in stages
    stage = stages["tool_self_consistency"]
    assert stage.dispatch_kind == "standard"
    assert stage.module.endswith("tool_self_consistency")


def test_dispatch_tool_self_consistency_matches_direct_run_split(monkeypatch) -> None:
    labels_by_call_index = {
        1: "2 per week",
        2: "unknown",
        3: "2 per week",
        4: "2 per week",
    }

    def fake_model_call(
        prompt_input_json: str,
        *,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        del model, temperature, max_tokens
        call_index = int(json.loads(prompt_input_json)["call_index"])
        label = labels_by_call_index[call_index]
        return (
            f'{{"final_label":"{label}","evidence":"2 seizures per week",'
            '"answer_kind":"frequency","selected_seizure_type":"seizure",'
            '"time_window":"current","confidence":"high",'
            '"rationale":"The note states 2 seizures per week."}'
        )

    monkeypatch.setattr(tool_self_consistency, "_run_model_call", fake_model_call)

    record = _record(
        301,
        "Clinic Date: 12 June 2026\nShe reports 2 seizures per week.",
        gold_label="2 per week",
        gold_monthly_frequency=8.690476190476192,
    )
    reference_rows = [
        {
            "source_row_index": 301,
            "condition_traces": {
                "single_self_consistency_temperature": {
                    "final_label": "unknown",
                }
            },
        }
    ]
    split_kwargs = {
        "reference_rows": reference_rows,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "model": "openai/gpt-4.1-mini",
        "temperature": 0.0,
        "max_tokens": 900,
        "mode": "live",
        "dspy_cache": True,
        "api_base": None,
        "progress_every": None,
        "checkpoint_jsonl_path": None,
        "checkpoint_report_path": None,
    }

    direct_rows, direct_metadata = tool_self_consistency.run_split(
        [record],
        **split_kwargs,
    )
    dispatched_rows, dispatched_metadata = dispatch_registered_split(
        tool_self_consistency.STAGE_ID,
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
            prompt_version=tool_self_consistency.PROMPT_VERSION,
            metadata_extra={
                "artifact_kind": "gan2026_agentic_tool_self_consistency",
                "pipeline_family": "agentic_tool_self_consistency",
                "pipeline_version": "gan2026_agentic_e2_tool_self_consistency_v0",
                "claim_boundary": (
                    "validation-development hard50 four-call boundary-guide "
                    "self-consistency; no holdout use, no row-level test inspection, "
                    "and no benchmark claim"
                ),
            },
            build_row=tool_self_consistency._build_row,
            summarize_rows=tool_self_consistency.summarize_rows,
            gate_interpretation=tool_self_consistency.gate_interpretation,
            write_report=tool_self_consistency.write_report,
        ),
        structured_event_context=StructuredEventSplitContext(
            default_structured_event_jsonl_path=Path("."),
            row_kwargs={
                "reference_labels": tool_self_consistency._reference_labels(reference_rows)
            },
        ),
    )

    assert direct_rows == dispatched_rows
    assert _metadata_without_timestamps(direct_metadata) == _metadata_without_timestamps(
        dispatched_metadata
    )
