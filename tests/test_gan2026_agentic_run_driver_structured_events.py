from __future__ import annotations

import json
from pathlib import Path

# cross_model_structured_event_adjudicator must initialise before run_driver:
# run_driver reads its AGENT_IDS at import time while the adjudicator imports
# run_driver back, so importing run_driver first triggers a circular import.
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    cross_model_structured_event_adjudicator,  # noqa: F401  (import-order guard)
    event_completion_reasoner,
    llm_event_reasoner,
    represented_event_normalizer,
    structured_event_verifier,
    temporal_sentinel_specialist,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.run_driver import (
    AgenticSplitHooks,
    SplitRunParams,
    StructuredEventSplitContext,
    dispatch_registered_split,
    registered_agentic_stages,
)
from tests.helpers.gan2026_agentic_run_driver_fixtures import (
    completion_structured_event_row as _completion_structured_event_row,
)
from tests.helpers.gan2026_agentic_run_driver_fixtures import (
    metadata_without_timestamps as _metadata_without_timestamps,
)
from tests.helpers.gan2026_agentic_run_driver_fixtures import (
    record as _record,
)
from tests.helpers.gan2026_agentic_run_driver_fixtures import (
    structured_event_row as _structured_event_row,
)
from tests.helpers.gan2026_agentic_run_driver_fixtures import (
    temporal_sentinel_boundary_row as _temporal_sentinel_boundary_row,
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
        ("Clinic Date: 12 June 2026\nPatient has clusters about four times per month."),
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
