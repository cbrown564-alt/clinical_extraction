"""Prompt-only matched-budget runner for Gan 2026 agentic Phase 6."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy

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
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_only_direct_labeler import (
    LlmOnlyDirectLabelerDecisionRecord,
    parse_decision_json,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm
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
    """Build matched-budget traces for agentic conditions."""

    del escalation_reason, progress_every, checkpoint_jsonl_path
    del checkpoint_report_path, candidate_set_jsonl_path
    if mode == "live":
        dspy.configure(
            lm=build_dspy_lm(
                model,
                temperature=temperature,
                max_tokens=max_tokens,
                cache=dspy_cache,
                api_base=api_base,
            )
        )
    budgets = _default_budgets(max_tokens=max_tokens)
    rows = [
        _build_row_trace(
            record,
            split=split,
            split_manifest=split_manifest,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            mode=mode,
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
            "pipeline_version": "gan2026_agentic_phase6_live_v0",
            "claim_boundary": (
                "validation-development matched-budget agentic trace; no holdout "
                "use, no row-level test inspection, and no benchmark claim"
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
    model_calls_attempted = 0
    call_failures = 0
    decision_records = 0
    parse_or_validation_failures = 0
    purist_correct = 0
    pragmatic_correct = 0
    for row in rows:
        if row.get("final_label") is not None:
            prediction_bearing_rows += 1
        for trace in dict(row.get("condition_traces") or {}).values():
            tool_smoke_calls += sum(
                1
                for tool_call in trace.get("tool_calls", [])
                if tool_call.get("status") == "contract_smoke"
            )
            for result in trace.get("model_call_results", []):
                model_calls_attempted += 1
                call_failures += int(result.get("call_error") is not None)
                decision_records += int(result.get("decision_record") is not None)
                parse_or_validation_failures += int(
                    _has_blocking_parse_issue(result.get("parse_errors"))
                )
                comparison = result.get("comparison") or {}
                purist_correct += int(bool(comparison.get("purist_correct")))
                pragmatic_correct += int(bool(comparison.get("pragmatic_correct")))
    return {
        "rows": len(rows),
        "conditions": list(DEFAULT_CONDITIONS),
        "tool_smoke_calls": tool_smoke_calls,
        "prediction_bearing_rows": prediction_bearing_rows,
        "model_calls_attempted": model_calls_attempted,
        "call_failures": call_failures,
        "decision_records": decision_records,
        "parse_or_validation_failures": parse_or_validation_failures,
        "purist_correct_call_level": purist_correct,
        "pragmatic_correct_call_level": pragmatic_correct,
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
        "# Gan 2026 Agentic Matched-Budget Trace",
        "",
        f"Date: {metadata.get('date', 'unknown')}",
        "",
        "This is a Phase 6 matched-budget agentic comparison surface.",
        "Prompt-only runs record plans and tool schemas; live runs add model outputs.",
        "Prompt-only mode remains a no-call contract smoke.",
        "",
        "## Summary",
        "",
        f"- Rows: {summary.get('rows', 0)}",
        f"- Conditions: {', '.join(summary.get('conditions', []))}",
        f"- Tool smoke calls: {summary.get('tool_smoke_calls', 0)}",
        f"- Prediction-bearing rows: {summary.get('prediction_bearing_rows', 0)}",
        f"- Model calls attempted: {summary.get('model_calls_attempted', 0)}",
        f"- Call failures: {summary.get('call_failures', 0)}",
        f"- Decision records: {summary.get('decision_records', 0)}",
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
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
    budgets: Mapping[ConditionName, AgentBudget],
) -> dict[str, Any]:
    parser_result = parse_seizure_frequency_candidates(record.note_text)
    guide_results = _boundary_guides_for_parser_result(parser_result.model_dump(mode="json"))
    condition_traces = {
        condition: _condition_trace(
            condition,
            record=record,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            mode=mode,
            budget=budgets[condition],
            parser_result=parser_result.model_dump(mode="json"),
            guide_results=guide_results,
        )
        for condition in DEFAULT_CONDITIONS
    }
    final_label = _select_row_final_label(condition_traces)
    return {
        "source_row_index": record.source_row_index,
        "split": split,
        "split_manifest": split_manifest,
        "artifact_mode": mode,
        "final_label": final_label,
        "attribution_layer": "raw_model" if final_label is not None else "no_prediction",
        "condition_traces": condition_traces,
    }


def _condition_trace(
    condition: ConditionName,
    *,
    record: GanFrequencyRecord,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
    budget: AgentBudget,
    parser_result: dict[str, Any],
    guide_results: list[dict[str, Any]],
) -> dict[str, Any]:
    model_call_plans = _model_call_plans(
        condition,
        model=model,
        temperature=temperature,
        note_text=record.note_text,
    )
    model_call_results = (
        []
        if mode == "prompt-only"
        else [
            _execute_model_call(
                plan,
                condition=condition,
                record=record,
                max_tokens=max_tokens,
                parser_result=parser_result,
                guide_results=guide_results,
            )
            for plan in model_call_plans
        ]
    )
    final_label = _select_trace_final_label(model_call_results)
    return {
        "condition": condition,
        "budget": budget.model_dump(mode="json"),
        "model_call_plans": model_call_plans,
        "model_call_results": model_call_results,
        "tool_calls": _tool_calls(condition, parser_result, guide_results),
        "aggregation": _aggregation_plan(condition),
        "final_label": final_label,
        "attribution_layer": "raw_model" if final_label is not None else "no_prediction",
        "trace_warnings": (
            ["prompt_only_no_prediction"] if mode == "prompt-only" else []
        ),
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
        samples = [
            {**base, "call_index": index, "call_role": "self_consistency_sample"}
            for index in range(1, 4)
        ]
        return [
            *samples,
            {**base, "call_index": 4, "call_role": "self_consistency_adjudicator"},
        ]
    if condition == "single_self_consistency_cross_model":
        samples = [
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
        return [
            *samples,
            {**base, "call_index": 4, "call_role": "cross_model_adjudicator"},
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


class AgenticDecisionSignature(dspy.Signature):
    """Extract one Gan 2026 seizure-frequency decision as strict JSON."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON prompt payload with task instructions, note text, and optional tool context."
    )
    decision_json: str = dspy.OutputField(
        desc=(
            "Strict JSON object with final_label, evidence, answer_kind, "
            "selected_seizure_type, time_window, confidence, and rationale."
        )
    )


class DspyAgenticDecisionCaller(dspy.Module):
    """Small DSPy wrapper used by the agentic runner for one planned call."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(AgenticDecisionSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def _execute_model_call(
    plan: Mapping[str, Any],
    *,
    condition: ConditionName,
    record: GanFrequencyRecord,
    max_tokens: int,
    parser_result: Mapping[str, Any],
    guide_results: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    prompt_input_json = _build_prompt_input(
        record,
        condition=condition,
        call_plan=plan,
        parser_result=parser_result,
        guide_results=guide_results,
    )
    raw_output = ""
    call_error: str | None = None
    try:
        raw_output = _run_model_call(
            prompt_input_json,
            model=str(plan["model"]),
            temperature=float(plan["temperature"]),
            max_tokens=max_tokens,
        )
    except Exception as exc:  # pragma: no cover - live transport only.
        call_error = f"{type(exc).__name__}: {exc}"

    decision, parse_errors = (
        parse_decision_json(raw_output) if raw_output else (None, ["not_run"])
    )
    comparison = _compare_to_gold(record, decision) if decision is not None else None
    return {
        "call_index": plan["call_index"],
        "call_role": plan["call_role"],
        "model": plan["model"],
        "temperature": plan["temperature"],
        "prompt_version": PROMPT_VERSION,
        "prompt_input_json": prompt_input_json,
        "raw_output": raw_output,
        "call_error": call_error,
        "parse_errors": parse_errors,
        "decision_record": decision.model_dump() if decision else None,
        "comparison": comparison,
        "attribution": "raw_model" if decision is not None else "no_prediction",
    }


def _run_model_call(
    prompt_input_json: str,
    *,
    model: str,
    temperature: float,
    max_tokens: int,
) -> str:
    del model, temperature, max_tokens
    prediction = DspyAgenticDecisionCaller()(prompt_input_json=prompt_input_json)
    return str(prediction.decision_json)


def _build_prompt_input(
    record: GanFrequencyRecord,
    *,
    condition: ConditionName,
    call_plan: Mapping[str, Any],
    parser_result: Mapping[str, Any],
    guide_results: Sequence[Mapping[str, Any]],
) -> str:
    import json

    payload: dict[str, Any] = {
        "prompt_version": PROMPT_VERSION,
        "task": "Gan 2026 seizure-frequency matched-budget agentic extraction",
        "condition": condition,
        "call_role": call_plan["call_role"],
        "source_row_index": record.source_row_index,
        "instructions": [
            "Read the clinical note and extract the current seizure-frequency answer.",
            (
                "Return exactly one strict JSON object with final_label, evidence, "
                "answer_kind, selected_seizure_type, time_window, confidence, and rationale."
            ),
            (
                "final_label must be a normalized Gan-style seizure-frequency label, "
                "seizure-free duration, unknown, or no seizure frequency reference."
            ),
            "Evidence should be copied as an exact source substring when possible.",
            (
                "Use unknown when seizure-frequency evidence exists but cannot be converted; "
                "use no seizure frequency reference only when no usable frequency evidence exists."
            ),
            (
                "Do not mention gold labels, split membership, row-level scoring, or benchmark "
                "answers. Make the clinical selection from the note and any supplied tool context."
            ),
        ],
        "allowed_answer_kind_values": [
            "frequency",
            "seizure_free",
            "unknown",
            "no_reference",
            "unresolved_multiple",
        ],
        "note_text": record.note_text,
    }
    if condition in {"single_agent_tools", "multi_agent_matched"}:
        payload["tool_context"] = {
            "parser_result": parser_result,
            "boundary_guides": list(guide_results),
            "tool_attribution_boundary": (
                "Parser candidates are deterministic-tool-owned. The model owns only "
                "the final clinical selection it explicitly makes from this context."
            ),
        }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _select_trace_final_label(results: Sequence[Mapping[str, Any]]) -> str | None:
    labels = [
        result["decision_record"]["final_label"]
        for result in results
        if result.get("decision_record")
    ]
    if not labels:
        return None
    return _majority_label(labels)


def _select_row_final_label(
    condition_traces: Mapping[ConditionName, Mapping[str, Any]]
) -> str | None:
    preferred_order: tuple[ConditionName, ...] = (
        "single_agent_tools",
        "single_self_consistency_temperature",
        "single_greedy",
        "single_self_consistency_cross_model",
        "multi_agent_matched",
    )
    for condition in preferred_order:
        label = condition_traces[condition].get("final_label")
        if label is not None:
            return str(label)
    return None


def _majority_label(labels: Sequence[str]) -> str:
    counts = {label: labels.count(label) for label in labels}
    return sorted(counts.items(), key=lambda item: (-item[1], labels.index(item[0])))[0][0]


def _compare_to_gold(
    record: GanFrequencyRecord,
    decision: LlmOnlyDirectLabelerDecisionRecord,
) -> dict[str, Any]:
    from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
        label_to_frequency_record,
    )

    predicted_record = label_to_frequency_record(decision.final_label)
    predicted_monthly = predicted_record.monthly_frequency
    return {
        "predicted_monthly_frequency": predicted_monthly,
        "gold_monthly_frequency": record.gold_monthly_frequency,
        "predicted_purist_category": str(map_purist(predicted_monthly)),
        "gold_purist_category": str(map_purist(record.gold_monthly_frequency)),
        "purist_correct": map_purist(predicted_monthly)
        == map_purist(record.gold_monthly_frequency),
        "predicted_pragmatic_category": str(map_pragmatic(predicted_monthly)),
        "gold_pragmatic_category": str(map_pragmatic(record.gold_monthly_frequency)),
        "pragmatic_correct": map_pragmatic(predicted_monthly)
        == map_pragmatic(record.gold_monthly_frequency),
    }


def _has_blocking_parse_issue(errors: Any) -> bool:
    return any(
        str(error).startswith(
            (
                "invalid_json:",
                "schema_validation_error:",
                "unscorable_final_label:",
                "not_run",
            )
        )
        for error in errors or []
    )
