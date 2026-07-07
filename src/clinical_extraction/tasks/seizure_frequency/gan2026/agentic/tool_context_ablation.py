"""One-call tool-context ablation for Gan 2026 agentic hard slices."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.run_driver import (
    AgenticSplitHooks,
    RegisteredAgenticStage,
    SplitRunParams,
    dispatch_registered_split,
    register_agentic_stage,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.runner import (
    PROMPT_VERSION,
    _extract_raw_model_final_label,
    _normalized_label_vote,
    _run_model_call,
    _trace_attribution_layer,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.tools import (
    parse_seizure_frequency_candidates,
    read_boundary_guide,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    load_records_for_split,
    load_split_manifest,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import (
    map_pragmatic,
    map_purist,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_only_direct_labeler import (
    LlmOnlyDirectLabelerDecisionRecord,
    parse_decision_json,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.reports.base import (
    write_markdown_report,
)

TOOL_CONTEXT_CONDITIONS: tuple[str, ...] = (
    "direct_no_tool_context",
    "direct_parser_only",
    "direct_boundary_guide_only",
    "direct_parser_plus_boundary_guide",
)
PIPELINE_FAMILY = "agentic_tool_context_ablation"
PIPELINE_VERSION = "gan2026_agentic_e1_tool_context_ablation_v0"
STAGE_ID = "tool_context_ablation"

register_agentic_stage(
    RegisteredAgenticStage(
        stage_id=STAGE_ID,
        dispatch_kind="standard",
        module=__name__,
        description="E1 one-call tool-context ablation over fixed hard slices",
    )
)


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
    progress_every: int | None,
    checkpoint_jsonl_path: Path | None,
    checkpoint_report_path: Path | None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run the E1 one-call context ablation over a fixed record surface."""

    params = SplitRunParams(
        split=split,
        split_manifest=split_manifest,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        mode=mode,
        dspy_cache=dspy_cache,
        api_base=api_base,
        progress_every=progress_every,
        checkpoint_jsonl_path=checkpoint_jsonl_path,
        checkpoint_report_path=checkpoint_report_path,
    )
    hooks = AgenticSplitHooks(
        prompt_version=PROMPT_VERSION,
        metadata_extra={
            "artifact_kind": "gan2026_agentic_tool_context_ablation",
            "pipeline_family": PIPELINE_FAMILY,
            "pipeline_version": PIPELINE_VERSION,
            "claim_boundary": (
                "validation-development hard50 tool-context ablation; no holdout "
                "use, no row-level test inspection, and no benchmark claim"
            ),
        },
        build_row=_build_row,
        summarize_rows=summarize_rows,
        finalize_metadata=_finalize_metadata,
        write_report=write_report,
        progress_fields=("call_failures", "parse_or_validation_failures"),
    )
    return dispatch_registered_split(STAGE_ID, records, params=params, hooks=hooks)


def summarize_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    call_failures = 0
    decision_records = 0
    parse_or_validation_failures = 0
    for row in rows:
        for trace in dict(row.get("condition_traces") or {}).values():
            for result in trace.get("model_call_results") or []:
                call_failures += int(result.get("call_error") is not None)
                decision_records += int(result.get("decision_record") is not None)
                parse_or_validation_failures += int(
                    _has_blocking_parse_issue(result.get("parse_errors"))
                )
    return {
        "rows": len(rows),
        "conditions": list(TOOL_CONTEXT_CONDITIONS),
        "model_calls_attempted": len(rows) * len(TOOL_CONTEXT_CONDITIONS),
        "call_failures": call_failures,
        "decision_records": decision_records,
        "parse_or_validation_failures": parse_or_validation_failures,
    }


def condition_summaries(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    summaries: dict[str, dict[str, Any]] = {}
    no_tool_correct_by_row = _correct_by_row(rows, "direct_no_tool_context")
    for condition in TOOL_CONTEXT_CONDITIONS:
        purist_correct = 0
        pragmatic_correct = 0
        call_failures = 0
        parse_failures = 0
        final_labels = Counter()
        for row in rows:
            trace = dict(row.get("condition_traces", {}).get(condition) or {})
            score = dict(trace.get("final_comparison") or {})
            purist_correct += int(bool(score.get("purist_correct")))
            pragmatic_correct += int(bool(score.get("pragmatic_correct")))
            final_label = trace.get("final_label")
            if final_label is not None:
                final_labels[str(final_label)] += 1
            for result in trace.get("model_call_results") or []:
                call_failures += int(result.get("call_error") is not None)
                parse_failures += int(_has_blocking_parse_issue(result.get("parse_errors")))
        correct_by_row = _correct_by_row(rows, condition)
        wins = sum(
            int(not no_tool_correct_by_row[index] and correct)
            for index, correct in correct_by_row.items()
        )
        losses = sum(
            int(no_tool_correct_by_row[index] and not correct)
            for index, correct in correct_by_row.items()
        )
        summaries[condition] = {
            "rows": len(rows),
            "purist_correct": purist_correct,
            "pragmatic_correct": pragmatic_correct,
            "purist_accuracy": round(purist_correct / len(rows), 4) if rows else 0.0,
            "pragmatic_accuracy": (round(pragmatic_correct / len(rows), 4) if rows else 0.0),
            "wins_vs_no_tool": wins,
            "losses_vs_no_tool": losses,
            "call_failures": call_failures,
            "parse_or_validation_failures": parse_failures,
            "final_labels": dict(sorted(final_labels.items())),
        }
    return summaries


def gate_interpretation(condition_summary: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    no_tool = dict(condition_summary.get("direct_no_tool_context") or {})
    no_tool_score = int(no_tool.get("purist_correct", 0))
    context_conditions = [
        "direct_parser_only",
        "direct_boundary_guide_only",
        "direct_parser_plus_boundary_guide",
    ]
    non_harmful = [
        condition
        for condition in context_conditions
        if int(condition_summary[condition]["purist_correct"]) >= no_tool_score
    ]
    harmful = [
        condition
        for condition in context_conditions
        if int(condition_summary[condition]["purist_correct"]) < no_tool_score
    ]
    if len(harmful) == len(context_conditions):
        status = "reject_dynamic_tool_context"
        interpretation = (
            "Every tool-context variant underperformed the no-tool one-call condition on hard50."
        )
    elif non_harmful:
        status = "revise_with_non_harmful_context"
        interpretation = (
            "At least one tool-context variant was neutral or better than no-tool; "
            "use only the non-harmful context in E2/E3."
        )
    else:
        status = "diagnostic"
        interpretation = "Tool-context gate was inconclusive."
    return {
        "status": status,
        "no_tool_purist_correct": no_tool_score,
        "non_harmful_contexts": non_harmful,
        "harmful_contexts": harmful,
        "interpretation": interpretation,
    }


def _finalize_metadata(
    rows: Sequence[Mapping[str, Any]],
    metadata: dict[str, Any],
) -> None:
    metadata["condition_summaries"] = condition_summaries(rows)
    metadata["gate"] = gate_interpretation(metadata["condition_summaries"])


def write_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    summary = dict(metadata.get("summary") or {})
    gate = dict(metadata.get("gate") or {})
    lines = [
        "# Gan 2026 Agentic Hard50 Tool-Context Ablation",
        "",
        f"Date: {metadata.get('date', 'unknown')}",
        "",
        "## Experiment Unit",
        "",
        "- Work class: E1 validation hard-slice one-call tool-context ablation.",
        f"- Rows: {summary.get('rows', 0)}",
        "- Split: `validation`, manifest `gan2026_split_v1`.",
        "- Surface: fixed validation hard50 manifest.",
        f"- Mode: `{metadata.get('mode')}`",
        f"- Model: `{metadata.get('model')}`",
        f"- Prompt version: `{metadata.get('prompt_version')}`",
        f"- JSONL artifact: `{jsonl_path}`",
        "",
        "## Summary",
        "",
        f"- Model calls attempted: {summary.get('model_calls_attempted', 0)}",
        f"- Decision records: {summary.get('decision_records', 0)}",
        f"- Call failures: {summary.get('call_failures', 0)}",
        f"- Parse/schema/label failures: {summary.get('parse_or_validation_failures', 0)}",
        "",
        "## Condition Summary",
        "",
        (
            "| Condition | Purist | Pragmatic | Wins vs no-tool | Losses vs no-tool | "
            "Call failures | Parse failures |"
        ),
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for condition, condition_summary in dict(metadata.get("condition_summaries") or {}).items():
        lines.append(
            f"| `{condition}` | {condition_summary['purist_correct']}/"
            f"{condition_summary['rows']} | {condition_summary['pragmatic_correct']}/"
            f"{condition_summary['rows']} | {condition_summary['wins_vs_no_tool']} | "
            f"{condition_summary['losses_vs_no_tool']} | "
            f"{condition_summary['call_failures']} | "
            f"{condition_summary['parse_or_validation_failures']} |"
        )
    lines.extend(
        [
            "",
            "## Gate",
            "",
            f"- Status: `{gate.get('status')}`",
            f"- Non-harmful contexts: `{', '.join(gate.get('non_harmful_contexts') or [])}`",
            f"- Harmful contexts: `{', '.join(gate.get('harmful_contexts') or [])}`",
            f"- Interpretation: {gate.get('interpretation')}",
            "",
            "## Claim Boundary",
            "",
            str(metadata.get("claim_boundary", "")),
            "",
            "## Rows",
            "",
            "| Row | Condition | Final | Purist | Parse notes |",
            "| ---: | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        for condition, trace in dict(row.get("condition_traces") or {}).items():
            comparison = dict(trace.get("final_comparison") or {})
            parse_notes = "; ".join(
                str(error)
                for result in trace.get("model_call_results") or []
                for error in result.get("parse_errors") or []
            )
            lines.append(
                f"| {row.get('source_row_index')} | `{condition}` | "
                f"`{trace.get('final_label')}` | "
                f"{'yes' if comparison.get('purist_correct') else 'no'} | "
                f"{parse_notes} |"
            )
    write_markdown_report(path, lines)


def write_jsonl(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    write_jsonl_rows(rows, path)


def _build_row(
    record: GanFrequencyRecord,
    *,
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
) -> dict[str, Any]:
    parser_result = parse_seizure_frequency_candidates(record.note_text).model_dump(mode="json")
    guide_results = _boundary_guides_for_parser_result(parser_result)
    condition_traces = {
        condition: _condition_trace(
            condition,
            record=record,
            parser_result=parser_result,
            guide_results=guide_results,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            mode=mode,
        )
        for condition in TOOL_CONTEXT_CONDITIONS
    }
    return {
        "source_row_index": record.source_row_index,
        "split": split,
        "split_manifest": split_manifest,
        "artifact_mode": mode,
        "condition_traces": condition_traces,
    }


def _condition_trace(
    condition: str,
    *,
    record: GanFrequencyRecord,
    parser_result: Mapping[str, Any],
    guide_results: Sequence[Mapping[str, Any]],
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
) -> dict[str, Any]:
    call_plan = {
        "call_index": 1,
        "call_role": "direct_context_ablation",
        "model": model,
        "temperature": temperature,
        "prompt_version": PROMPT_VERSION,
        "input_note_chars": len(record.note_text),
    }
    model_call_results = (
        []
        if mode == "prompt-only"
        else [
            _execute_model_call(
                call_plan,
                condition=condition,
                record=record,
                parser_result=parser_result,
                guide_results=guide_results,
                max_tokens=max_tokens,
            )
        ]
    )
    vote = _normalized_label_vote(model_call_results)
    final_label = vote["selected_label"]
    return {
        "condition": condition,
        "model_call_plans": [call_plan],
        "model_call_results": model_call_results,
        "tool_calls": _tool_calls(condition, parser_result, guide_results),
        "aggregation": {"method": "none_single_output", "aggregation_model_calls": 0},
        "final_label": final_label,
        "final_comparison": _compare_label_to_gold(record, final_label)
        if final_label is not None
        else None,
        "attribution_layer": _trace_attribution_layer(
            final_label=final_label,
            model_call_results=model_call_results,
        ),
        "normalized_label_vote": vote,
        "trace_warnings": ["prompt_only_no_prediction"] if mode == "prompt-only" else [],
    }


def _execute_model_call(
    plan: Mapping[str, Any],
    *,
    condition: str,
    record: GanFrequencyRecord,
    parser_result: Mapping[str, Any],
    guide_results: Sequence[Mapping[str, Any]],
    max_tokens: int,
) -> dict[str, Any]:
    prompt_input_json = build_prompt_input(
        record,
        condition=condition,
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
    decision, parse_errors = parse_decision_json(raw_output) if raw_output else (None, ["not_run"])
    return {
        "call_index": plan["call_index"],
        "call_role": plan["call_role"],
        "model": plan["model"],
        "temperature": plan["temperature"],
        "prompt_version": PROMPT_VERSION,
        "prompt_input_json": prompt_input_json,
        "raw_output": raw_output,
        "raw_model_final_label": _extract_raw_model_final_label(raw_output) if raw_output else None,
        "call_error": call_error,
        "parse_errors": parse_errors,
        "decision_record": decision.model_dump() if decision else None,
        "comparison": _compare_to_gold(record, decision) if decision else None,
        "attribution": "raw_model" if decision is not None else "no_prediction",
    }


def build_prompt_input(
    record: GanFrequencyRecord,
    *,
    condition: str,
    parser_result: Mapping[str, Any],
    guide_results: Sequence[Mapping[str, Any]],
) -> str:
    payload: dict[str, Any] = {
        "prompt_version": PROMPT_VERSION,
        "task": "Gan 2026 seizure-frequency one-call tool-context ablation",
        "condition": condition,
        "call_role": "direct_context_ablation",
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
            (
                "Write frequency labels with spaces, not underscores: use "
                "'multiple per day' instead of 'multiple_per_day' and '2 per year' "
                "instead of 'twice_per_year'."
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
    tool_context: dict[str, Any] = {}
    if condition in {"direct_parser_only", "direct_parser_plus_boundary_guide"}:
        tool_context["parser_result"] = parser_result
    if condition in {"direct_boundary_guide_only", "direct_parser_plus_boundary_guide"}:
        tool_context["boundary_guides"] = list(guide_results)
    if tool_context:
        tool_context["tool_attribution_boundary"] = (
            "Parser candidates are deterministic-tool-owned. The model owns only "
            "the final clinical selection it explicitly makes from this context."
        )
        payload["tool_context"] = tool_context
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _tool_calls(
    condition: str,
    parser_result: Mapping[str, Any],
    guide_results: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    if condition in {"direct_parser_only", "direct_parser_plus_boundary_guide"}:
        calls.append(
            {
                "tool_name": "parse_seizure_frequency_candidates",
                "status": "context_included",
                "result": parser_result,
                "attribution": "deterministic_tool_candidate_discovery",
            }
        )
    if condition in {"direct_boundary_guide_only", "direct_parser_plus_boundary_guide"}:
        calls.extend(
            {
                "tool_name": "read_boundary_guide",
                "status": "context_included",
                "result": guide_result,
                "attribution": "split_neutral_guidance_retrieval",
            }
            for guide_result in guide_results
        )
    return calls


def _boundary_guides_for_parser_result(parser_result: Mapping[str, Any]) -> list[dict[str, Any]]:
    guide_ids = {"unknown_frequency_vs_no_reference"}
    candidate_kinds = {
        candidate.get("candidate_kind") for candidate in parser_result.get("candidates", [])
    }
    if "cluster_frequency" in candidate_kinds:
        guide_ids.add("cluster_frequency_vs_incidental_clustering")
    if "seizure_free" in candidate_kinds:
        guide_ids.add("seizure_free_event_conflict")
    return [read_boundary_guide(guide_id).model_dump(mode="json") for guide_id in sorted(guide_ids)]


def _compare_to_gold(
    record: GanFrequencyRecord,
    decision: LlmOnlyDirectLabelerDecisionRecord,
) -> dict[str, Any]:
    return _compare_label_to_gold(record, decision.final_label)


def _compare_label_to_gold(
    record: GanFrequencyRecord,
    label: str | None,
) -> dict[str, Any]:
    if label is None:
        return {
            "predicted_monthly_frequency": None,
            "gold_monthly_frequency": record.gold_monthly_frequency,
            "predicted_purist_category": None,
            "gold_purist_category": str(map_purist(record.gold_monthly_frequency)),
            "purist_correct": False,
            "predicted_pragmatic_category": None,
            "gold_pragmatic_category": str(map_pragmatic(record.gold_monthly_frequency)),
            "pragmatic_correct": False,
        }
    predicted_record = label_to_frequency_record(str(label))
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


def _correct_by_row(
    rows: Sequence[Mapping[str, Any]],
    condition: str,
) -> dict[int, bool]:
    return {
        int(row["source_row_index"]): bool(
            dict(
                dict(row.get("condition_traces", {})).get(condition, {}).get("final_comparison")
                or {}
            ).get("purist_correct")
        )
        for row in rows
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


def _load_hard50_records(path: Path) -> list[int]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [int(index) for index in payload["source_row_indices"]]


def _filter_records_by_source_indices(
    records: Sequence[GanFrequencyRecord],
    source_row_indices: Sequence[int],
) -> list[GanFrequencyRecord]:
    by_index = {record.source_row_index: record for record in records}
    missing = [index for index in source_row_indices if index not in by_index]
    if missing:
        raise ValueError(f"source_row_index values not present in split: {missing[:10]}")
    return [by_index[index] for index in source_row_indices]


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Run E1 one-call tool-context ablation on a fixed hard slice."
    )
    parser.add_argument("--manifest-json", type=Path, required=True)
    parser.add_argument("--jsonl", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--split", default="validation", choices=("validation", "train", "test"))
    parser.add_argument("--model", default="openai/gpt-4.1-mini")
    parser.add_argument("--api-base", default=None)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=900)
    parser.add_argument("--mode", choices=("live", "prompt-only"), default="live")
    parser.add_argument("--disable-dspy-cache", action="store_true")
    parser.add_argument("--progress-every", type=int, default=5)
    parser.add_argument("--overwrite-existing", action="store_true")
    args = parser.parse_args(argv)
    if not args.overwrite_existing:
        existing = [path for path in (args.jsonl, args.markdown) if path.exists()]
        if existing:
            parser.error(
                "output artifact already exists; use --overwrite-existing to replace: "
                + ", ".join(str(path) for path in existing)
            )
    requested = _load_hard50_records(args.manifest_json)
    records = _filter_records_by_source_indices(
        load_records_for_split(args.split),
        requested,
    )
    manifest = load_split_manifest()
    split_manifest = str(manifest.get("manifest_version", "gan2026_split_v1"))
    rows, metadata = run_split(
        records,
        split=args.split,
        split_manifest=split_manifest,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        mode=args.mode,
        dspy_cache=not args.disable_dspy_cache,
        api_base=args.api_base,
        progress_every=args.progress_every if args.progress_every > 0 else None,
        checkpoint_jsonl_path=args.jsonl,
        checkpoint_report_path=args.markdown,
    )
    metadata["hard50_manifest_path"] = str(args.manifest_json)
    write_jsonl(rows, args.jsonl)
    write_report(rows, metadata, args.markdown, jsonl_path=args.jsonl)
    print(json.dumps(metadata["gate"], sort_keys=True))


if __name__ == "__main__":
    main()
