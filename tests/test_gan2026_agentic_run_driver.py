from __future__ import annotations

import json
from pathlib import Path

import pytest

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    cross_model_challenge_adjudicator,
    cross_model_structured_event_adjudicator,
    event_completion_reasoner,
    llm_event_reasoner,
    represented_event_normalizer,
    runner as agentic_runner,
    targeted_boundary_router,
    temporal_sentinel_specialist,
    tool_context_ablation,
    tool_self_consistency,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    structured_event_verifier,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.run_driver import (
    AgenticSplitHooks,
    CrossModelSplitContext,
    MatchedBudgetSplitContext,
    RegisteredAgenticStage,
    SplitRunParams,
    StructuredEventSplitContext,
    dispatch_registered_split,
    register_agentic_stage,
    registered_agentic_stages,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord


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


def test_represented_event_normalizer_stage_is_registered() -> None:
    stages = registered_agentic_stages()

    assert "represented_event_normalizer" in stages
    stage = stages["represented_event_normalizer"]
    assert stage.dispatch_kind == "structured_event"
    assert stage.module.endswith("represented_event_normalizer")


def test_event_completion_reasoner_stage_is_registered() -> None:
    stages = registered_agentic_stages()

    assert "event_completion_reasoner" in stages
    stage = stages["event_completion_reasoner"]
    assert stage.dispatch_kind == "structured_event"
    assert stage.module.endswith("event_completion_reasoner")


def test_dispatch_structured_event_matches_direct_run_split(monkeypatch) -> None:
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
                "action": "replace_with_recomputed_fact_from_selected_evidence",
                "final_label": "two_per_week",
                "final_kind": "frequency",
                "selected_event_ids": ["e2"],
                "rejected_event_ids": ["e1"],
                "evidence": ["two seizures per week"],
                "contradiction_profile": ["represented_rate_denominator"],
                "calculation_trace": "two seizures per week -> 2 per week",
                "clinical_rationale": "The selected event gives the current burden.",
                "uncertainty": "low",
                "tool_calls": [],
                "attribution": "llm_selected_tool_rendered",
            }
        )

    monkeypatch.setattr(represented_event_normalizer, "_run_model_call", fake_model_call)

    record = _record(
        943,
        "Clinic Date: 12 June 2026\nPatient reports two seizures per week.",
        gold_label="2 per week",
        gold_monthly_frequency=8.69047619047619,
    )
    structured_event_rows = [
        _structured_event_row(
            943,
            final_label="1 per month",
            final_kind="frequency",
            purist_correct=False,
            replacement_normalized_label="unknown",
        )
    ]
    split_kwargs = {
        "structured_event_rows": structured_event_rows,
        "structured_event_source_path": Path("v0.jsonl"),
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "model": "openai/gpt-4.1-mini",
        "temperature": 0.0,
        "max_tokens": 2200,
        "mode": "live",
        "dspy_cache": True,
        "api_base": None,
        "escalation_reason": None,
        "progress_every": None,
        "checkpoint_jsonl_path": None,
        "checkpoint_report_path": None,
    }

    direct_rows, direct_metadata = represented_event_normalizer.run_split(
        [record],
        **split_kwargs,
    )
    dispatched_rows, dispatched_metadata = dispatch_registered_split(
        represented_event_normalizer.STAGE_ID,
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
            prompt_version=represented_event_normalizer.PROMPT_VERSION,
            metadata_extra={
                "artifact_kind": "gan2026_represented_event_normalizer_trace",
                "pipeline_family": represented_event_normalizer.PIPELINE_FAMILY,
                "pipeline_version": represented_event_normalizer.PROMPT_VERSION,
                "structured_event_source_role": (
                    "pure structured-event V0 comparator and represented-event "
                    "normalization substrate; the model owns any recomputed label"
                ),
                "claim_boundary": (
                    "validation-development V8 represented-event normalizer; no "
                    "holdout use, no row-level test inspection, and no benchmark claim"
                ),
            },
            build_row=represented_event_normalizer._build_row,
            summarize_rows=represented_event_normalizer.summarize_rows,
            gate_interpretation=structured_event_verifier.gate_interpretation,
            write_report=represented_event_normalizer.write_report,
            progress_fields=("final_purist_correct", "net_purist_gain_vs_v0"),
        ),
        structured_event_context=StructuredEventSplitContext(
            default_structured_event_jsonl_path=(
                represented_event_normalizer.DEFAULT_STRUCTURED_EVENT_JSONL_PATH
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


def test_temporal_sentinel_specialist_stage_is_registered() -> None:
    stages = registered_agentic_stages()

    assert "temporal_sentinel_specialist" in stages
    stage = stages["temporal_sentinel_specialist"]
    assert stage.dispatch_kind == "structured_event"
    assert stage.module.endswith("temporal_sentinel_specialist")


def test_dispatch_temporal_sentinel_matches_direct_run_split(monkeypatch) -> None:
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
                "final_label": "no seizure frequency reference",
                "final_kind": "no_reference",
                "selected_event_ids": ["e1"],
                "rejected_event_ids": [],
                "evidence": ["a very infrequent, short event a fortnight ago"],
                "contradiction_profile": ["temporal_sentinel:last_event_only_boundary"],
                "calculation_trace": "isolated last-event evidence is not a cadence",
                "clinical_rationale": (
                    "The selected event's own normalized candidate is a sentinel "
                    "boundary rather than a recurring frequency."
                ),
                "uncertainty": "low",
                "tool_calls": [],
                "attribution": "llm_selected_tool_rendered",
            }
        )

    monkeypatch.setattr(temporal_sentinel_specialist, "_run_model_call", fake_model_call)

    record = _record(
        963,
        "Clinic Date: 12 June 2026\na very infrequent, short event a fortnight ago",
        gold_label="unknown",
        gold_monthly_frequency=1000.0,
    )
    structured_event_rows = [_temporal_sentinel_boundary_row(963)]
    split_kwargs = {
        "structured_event_rows": structured_event_rows,
        "structured_event_source_path": Path("v0.jsonl"),
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "model": "openai/gpt-4.1-mini",
        "temperature": 0.0,
        "max_tokens": 2400,
        "mode": "live",
        "dspy_cache": True,
        "api_base": None,
        "escalation_reason": None,
        "progress_every": None,
        "checkpoint_jsonl_path": None,
        "checkpoint_report_path": None,
    }

    direct_rows, direct_metadata = temporal_sentinel_specialist.run_split(
        [record],
        **split_kwargs,
    )
    dispatched_rows, dispatched_metadata = dispatch_registered_split(
        temporal_sentinel_specialist.STAGE_ID,
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
            prompt_version=temporal_sentinel_specialist.PROMPT_VERSION,
            metadata_extra={
                "artifact_kind": "gan2026_temporal_sentinel_specialist_trace",
                "pipeline_family": temporal_sentinel_specialist.PIPELINE_FAMILY,
                "pipeline_version": (
                    f"{temporal_sentinel_specialist.PROMPT_VERSION}+"
                    f"{temporal_sentinel_specialist.SAFETY_GATE_VERSION}"
                ),
                "safety_gate_version": temporal_sentinel_specialist.SAFETY_GATE_VERSION,
                "structured_event_source_role": (
                    "pure structured-event V0 comparator and temporal/sentinel "
                    "specialist substrate; the specialist action owns any selected "
                    "replacement event"
                ),
                "claim_boundary": (
                    "validation-development V9 temporal/sentinel specialist; no "
                    "holdout use, no row-level test inspection, and no benchmark claim"
                ),
            },
            build_row=temporal_sentinel_specialist._build_row,
            summarize_rows=temporal_sentinel_specialist.summarize_rows,
            gate_interpretation=structured_event_verifier.gate_interpretation,
            write_report=temporal_sentinel_specialist.write_report,
            progress_fields=("final_purist_correct", "net_purist_gain_vs_v0"),
        ),
        structured_event_context=StructuredEventSplitContext(
            default_structured_event_jsonl_path=(
                temporal_sentinel_specialist.DEFAULT_STRUCTURED_EVENT_JSONL_PATH
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


def test_dispatch_event_completion_matches_direct_run_split(monkeypatch) -> None:
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

    record = _record(
        932,
        (
            "Clinic Date: 12 June 2026\n"
            "Patient has clusters about four times per month."
        ),
        gold_label="multiple per month",
        gold_monthly_frequency=1000.0,
    )
    structured_event_rows = [
        _completion_structured_event_row(
            932,
            final_label="unknown",
            final_kind="unknown",
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
        "max_tokens": 2200,
        "mode": "live",
        "dspy_cache": True,
        "api_base": None,
        "escalation_reason": None,
        "progress_every": None,
        "checkpoint_jsonl_path": None,
        "checkpoint_report_path": None,
    }

    direct_rows, direct_metadata = event_completion_reasoner.run_split(
        [record],
        **split_kwargs,
    )
    dispatched_rows, dispatched_metadata = dispatch_registered_split(
        event_completion_reasoner.STAGE_ID,
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
            prompt_version=event_completion_reasoner.PROMPT_VERSION,
            metadata_extra={
                "artifact_kind": "gan2026_event_completion_reasoner_trace",
                "pipeline_family": event_completion_reasoner.PIPELINE_FAMILY,
                "pipeline_version": event_completion_reasoner.PROMPT_VERSION,
                "structured_event_source_role": (
                    "pure structured-event V0 comparator and completion substrate; "
                    "the model owns any created completed event"
                ),
                "claim_boundary": (
                    "validation-development V7 event-completion scaffold; no holdout "
                    "use, no row-level test inspection, and no benchmark claim"
                ),
            },
            build_row=event_completion_reasoner._build_row,
            summarize_rows=event_completion_reasoner.summarize_rows,
            gate_interpretation=structured_event_verifier.gate_interpretation,
            write_report=event_completion_reasoner.write_report,
            progress_fields=("final_purist_correct", "net_purist_gain_vs_v0"),
        ),
        structured_event_context=StructuredEventSplitContext(
            default_structured_event_jsonl_path=(
                event_completion_reasoner.DEFAULT_STRUCTURED_EVENT_JSONL_PATH
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


def _llm_reasoner_structured_event_row(
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


def _router_structured_event_row(
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
                    "raw_value": "two recent occasions (July and September)",
                    "temporality": "recent",
                    "assertion_status": "asserted",
                    "applies_to": "seizures",
                    "evidence": (
                        "brief collapses have occurred on two recent occasions "
                        "(July and September)"
                    ),
                    "time_window": "recent",
                },
                {
                    "event_id": "e2",
                    "kind": "unknown_frequency",
                    "raw_value": "spells are uncommon when meals are regular",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "applies_to": "spells",
                    "evidence": "spells are uncommon when meals are regular",
                    "time_window": "current",
                },
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": final_kind,
                "final_label": final_label,
                "evidence": (
                    "brief collapses have occurred on two recent occasions "
                    "(July and September)"
                ),
                "confidence": "high",
                "rationale": "Original structured-event selection.",
            },
        },
        "normalized_events": [
            {
                "event_id": "e1",
                "normalized_label": final_label,
                "semantic_kind": final_kind,
                "monthly_frequency": 0.6666666667,
                "validation_errors": [],
            },
            {
                "event_id": "e2",
                "normalized_label": "unknown",
                "semantic_kind": "unknown",
                "monthly_frequency": 1000.0,
                "validation_errors": [],
            },
        ],
        "comparison": {
            "purist_correct": purist_correct,
            "pragmatic_correct": purist_correct,
        },
        "evidence_valid": True,
    }


def _structured_event_row(
    source_row_index: int,
    *,
    final_label: str,
    final_kind: str,
    purist_correct: bool,
    replacement_normalized_label: str,
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
                    "raw_value": "two seizures per week",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "applies_to": "seizures",
                    "evidence": "two seizures per week",
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
                "normalized_label": replacement_normalized_label,
                "semantic_kind": "unknown",
                "monthly_frequency": 1000.0,
                "validation_errors": [],
            },
        ],
        "comparison": {
            "purist_correct": purist_correct,
            "pragmatic_correct": purist_correct,
        },
        "evidence_valid": True,
    }


def _temporal_sentinel_boundary_row(source_row_index: int) -> dict:
    return {
        "source_row_index": source_row_index,
        "structured_record": {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "raw_value": "a very infrequent, short event a fortnight ago",
                    "temporality": "recent",
                    "assertion_status": "asserted",
                    "applies_to": "seizures",
                    "evidence": "a very infrequent, short event a fortnight ago",
                    "time_window": "a fortnight ago",
                    "notes": "isolated last event",
                }
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": "frequency",
                "final_label": "1 per 2 week",
                "evidence": "a very infrequent, short event a fortnight ago",
                "confidence": "high",
                "rationale": "Original structured-event selection.",
            },
        },
        "normalized_events": [
            {
                "event_id": "e1",
                "normalized_label": "no seizure frequency reference",
                "semantic_kind": "no_reference",
                "monthly_frequency": 1000.0,
                "validation_errors": [],
            }
        ],
        "comparison": {
            "purist_correct": False,
            "pragmatic_correct": False,
        },
        "evidence_valid": True,
    }


def _completion_structured_event_row(
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
