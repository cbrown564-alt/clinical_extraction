"""Prompt-only matched-budget runner for Gan 2026 agentic Phase 6."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.contracts import (
    AgentBudget,
    ConditionName,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.tools import (
    parse_seizure_frequency_candidates,
    read_boundary_guide,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_metadata import (
    build_run_metadata,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.reports.base import (
    write_markdown_report,
)

DEFAULT_CONDITIONS: tuple[ConditionName, ...] = (
    "single_greedy",
    "single_self_consistency_temperature",
    "single_self_consistency_cross_model",
    "single_agent_tools",
    "multi_agent_matched",
)

DEFAULT_JSONL_PATH = Path("experiments/gan2026_agentic_matched_budget_validation.jsonl")
DEFAULT_REPORT_PATH = Path("experiments/gan2026_agentic_matched_budget_validation.md")
PROMPT_VERSION = "gan2026_agentic_matched_budget_prompt_v0"


def run_split(
    records: Sequence[GanFrequencyRecord],
    *,
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
    dspy_cache: bool,
    api_base: str | None,
    escalation_reason: str | None,
    progress_every: int | None,
    checkpoint_jsonl_path: Path | None,
    checkpoint_report_path: Path | None,
    candidate_set_jsonl_path: Path | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Build no-call traces for matched-budget agentic conditions.

    Live model execution is intentionally not implemented in this first Phase 6
    slice. The prompt-only mode validates budgets, trace shape, and tool schemas
    before any prediction-bearing calls are allowed.
    """

    del escalation_reason, progress_every, checkpoint_jsonl_path
    del checkpoint_report_path, candidate_set_jsonl_path
    if mode != "prompt-only":
        raise NotImplementedError(
            "agentic_matched_budget currently supports only prompt-only no-call traces"
        )

    budgets = _default_budgets(max_tokens=max_tokens)
    rows = [
        _build_row_trace(
            record,
            split=split,
            split_manifest=split_manifest,
            model=model,
            temperature=temperature,
            budgets=budgets,
        )
        for record in records
    ]
    metadata = build_run_metadata(
        mode=mode,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        prompt_version=PROMPT_VERSION,
        dspy_version="none",
        split=split,
        split_manifest=split_manifest,
        api_base=api_base,
        row_count=len(records),
    )
    metadata.update(
        {
            "artifact_kind": "gan2026_agentic_matched_budget_trace",
            "pipeline_family": "agentic_matched_budget",
            "pipeline_version": "gan2026_agentic_phase6_prompt_only_v0",
            "claim_boundary": (
                "validation-development prompt-only/no-call contract smoke; "
                "no prediction-bearing model outputs and no benchmark claim"
            ),
            "dspy_cache": dspy_cache,
            "conditions": list(DEFAULT_CONDITIONS),
            "matched_budget": {
                condition: budget.model_dump(mode="json")
                for condition, budget in budgets.items()
            },
        }
    )
    metadata["summary"] = summarize_rows(rows)
    return rows, metadata


def summarize_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    tool_smoke_calls = 0
    prediction_bearing_rows = 0
    for row in rows:
        if row.get("final_label") is not None:
            prediction_bearing_rows += 1
        for trace in dict(row.get("condition_traces") or {}).values():
            tool_smoke_calls += sum(
                1
                for tool_call in trace.get("tool_calls", [])
                if tool_call.get("status") == "contract_smoke"
            )
    return {
        "rows": len(rows),
        "conditions": list(DEFAULT_CONDITIONS),
        "tool_smoke_calls": tool_smoke_calls,
        "prediction_bearing_rows": prediction_bearing_rows,
    }


def write_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    summary = dict(metadata.get("summary") or {})
    lines = [
        "# Gan 2026 Agentic Matched-Budget Prompt-Only Trace",
        "",
        f"Date: {metadata.get('date', 'unknown')}",
        "",
        "This is a no-call contract smoke for the Phase 6 agentic comparison surface.",
        "It records prompt plans, matched budgets, and tool trace schemas only.",
        "",
        "## Summary",
        "",
        f"- Rows: {summary.get('rows', 0)}",
        f"- Conditions: {', '.join(summary.get('conditions', []))}",
        f"- Tool smoke calls: {summary.get('tool_smoke_calls', 0)}",
        f"- Prediction-bearing rows: {summary.get('prediction_bearing_rows', 0)}",
        f"- JSONL artifact: `{jsonl_path}`",
        "",
        "## Claim Boundary",
        "",
        str(metadata.get("claim_boundary", "")),
        "",
        "## Condition Budgets",
        "",
        "| Condition | Model calls | Tool calls | Tool output tokens | Aggregation calls |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for condition, budget in dict(metadata.get("matched_budget") or {}).items():
        lines.append(
            f"| {condition} | {budget['model_calls_per_row']} | "
            f"{budget['max_tool_calls_per_row']} | "
            f"{budget['max_tool_output_tokens_per_row']} | "
            f"{budget['aggregation_budget_model_calls']} |"
        )
    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| Row | Tool smoke calls | Attribution |",
            "| ---: | ---: | --- |",
        ]
    )
    for row in rows:
        traces = dict(row.get("condition_traces") or {})
        tool_calls = sum(len(trace.get("tool_calls", [])) for trace in traces.values())
        attribution = sorted({trace.get("attribution_layer", "") for trace in traces.values()})
        lines.append(
            f"| {row.get('source_row_index')} | {tool_calls} | {', '.join(attribution)} |"
        )
    write_markdown_report(path, lines)


def _build_row_trace(
    record: GanFrequencyRecord,
    *,
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    budgets: Mapping[ConditionName, AgentBudget],
) -> dict[str, Any]:
    parser_result = parse_seizure_frequency_candidates(record.note_text)
    guide_results = _boundary_guides_for_parser_result(parser_result.model_dump(mode="json"))
    return {
        "source_row_index": record.source_row_index,
        "split": split,
        "split_manifest": split_manifest,
        "artifact_mode": "prompt-only",
        "final_label": None,
        "attribution_layer": "no_prediction",
        "condition_traces": {
            condition: _condition_trace(
                condition,
                record=record,
                model=model,
                temperature=temperature,
                budget=budgets[condition],
                parser_result=parser_result.model_dump(mode="json"),
                guide_results=guide_results,
            )
            for condition in DEFAULT_CONDITIONS
        },
    }


def _condition_trace(
    condition: ConditionName,
    *,
    record: GanFrequencyRecord,
    model: str,
    temperature: float,
    budget: AgentBudget,
    parser_result: dict[str, Any],
    guide_results: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "condition": condition,
        "budget": budget.model_dump(mode="json"),
        "model_call_plans": _model_call_plans(
            condition,
            model=model,
            temperature=temperature,
            note_text=record.note_text,
        ),
        "tool_calls": _tool_calls(condition, parser_result, guide_results),
        "aggregation": _aggregation_plan(condition),
        "final_label": None,
        "attribution_layer": "no_prediction",
        "trace_warnings": ["prompt_only_no_prediction"],
    }


def _model_call_plans(
    condition: ConditionName,
    *,
    model: str,
    temperature: float,
    note_text: str,
) -> list[dict[str, Any]]:
    base = {
        "model": model,
        "temperature": temperature,
        "prompt_version": PROMPT_VERSION,
        "input_note_chars": len(note_text),
    }
    if condition == "single_greedy":
        return [{**base, "call_index": 1, "call_role": "direct_extractor"}]
    if condition == "single_self_consistency_temperature":
        return [
            {**base, "call_index": index, "call_role": "self_consistency_sample"}
            for index in range(1, 5)
        ]
    if condition == "single_self_consistency_cross_model":
        return [
            {
                **base,
                "call_index": index,
                "call_role": "cross_model_sample",
                "model": model_name,
            }
            for index, model_name in enumerate(
                ("openai/gpt-4.1-mini", "deepseek/deepseek-chat", "qwen/qwen3-35b"),
                start=1,
            )
        ]
    if condition == "single_agent_tools":
        return [{**base, "call_index": 1, "call_role": "agent_loop"}]
    if condition == "multi_agent_matched":
        return [
            {**base, "call_index": 1, "call_role": "extractor_agent"},
            {**base, "call_index": 2, "call_role": "boundary_agent"},
            {**base, "call_index": 3, "call_role": "adjudicator_agent"},
            {**base, "call_index": 4, "call_role": "coordinator_agent"},
        ]
    raise ValueError(f"Unknown condition: {condition}")


def _tool_calls(
    condition: ConditionName,
    parser_result: dict[str, Any],
    guide_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if condition not in {"single_agent_tools", "multi_agent_matched"}:
        return []
    calls = [
        {
            "tool_name": "parse_seizure_frequency_candidates",
            "status": "contract_smoke",
            "result": parser_result,
            "attribution": "deterministic_tool_candidate_discovery",
        }
    ]
    calls.extend(
        {
            "tool_name": "read_boundary_guide",
            "status": "contract_smoke",
            "result": guide_result,
            "attribution": "split_neutral_guidance_retrieval",
        }
        for guide_result in guide_results
    )
    return calls


def _aggregation_plan(condition: ConditionName) -> dict[str, Any]:
    if condition == "single_greedy":
        return {"method": "none_single_output", "aggregation_model_calls": 0}
    if condition in {
        "single_self_consistency_temperature",
        "single_self_consistency_cross_model",
    }:
        return {
            "method": "deterministic_normalized_label_vote",
            "aggregation_model_calls": 0,
        }
    return {
        "method": "budget_matched_adjudication_or_deterministic_vote",
        "aggregation_model_calls": 1,
    }


def _boundary_guides_for_parser_result(parser_result: Mapping[str, Any]) -> list[dict[str, Any]]:
    guide_ids = {"unknown_frequency_vs_no_reference"}
    candidate_kinds = {
        candidate.get("candidate_kind")
        for candidate in parser_result.get("candidates", [])
    }
    if "cluster_frequency" in candidate_kinds:
        guide_ids.add("cluster_frequency_vs_incidental_clustering")
    if "seizure_free" in candidate_kinds:
        guide_ids.add("seizure_free_event_conflict")
    return [
        read_boundary_guide(guide_id).model_dump(mode="json")
        for guide_id in sorted(guide_ids)
    ]


def _default_budgets(*, max_tokens: int) -> dict[ConditionName, AgentBudget]:
    shared_multi_call = AgentBudget(
        model_calls_per_row=4,
        prompt_token_budget=2_500,
        max_completion_tokens_per_call=max_tokens,
        max_tool_calls_per_row=3,
        max_tool_output_tokens_per_row=700,
        aggregation_budget_model_calls=1,
    )
    return {
        "single_greedy": AgentBudget(
            model_calls_per_row=1,
            prompt_token_budget=2_500,
            max_completion_tokens_per_call=max_tokens,
            max_tool_calls_per_row=0,
            max_tool_output_tokens_per_row=0,
            aggregation_budget_model_calls=0,
        ),
        "single_self_consistency_temperature": shared_multi_call,
        "single_self_consistency_cross_model": shared_multi_call,
        "single_agent_tools": shared_multi_call,
        "multi_agent_matched": shared_multi_call,
    }
