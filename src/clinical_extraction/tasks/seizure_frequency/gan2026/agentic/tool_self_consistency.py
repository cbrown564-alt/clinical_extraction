"""E2 four-call boundary-guide tool self-consistency experiment."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.runner import (
    PROMPT_VERSION,
    _extract_raw_model_final_label,
    _normalized_label_vote,
    _run_model_call,
    _trace_attribution_layer,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.run_driver import (
    AgenticSplitHooks,
    RegisteredAgenticStage,
    SplitRunParams,
    StructuredEventSplitContext,
    dispatch_registered_split,
    register_agentic_stage,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.tool_context_ablation import (
    _boundary_guides_for_parser_result,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.tools import (
    parse_seizure_frequency_candidates,
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
    load_jsonl_rows,
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

CONDITION = "single_agent_tools_self_consistency_boundary_guide_only"
REFERENCE_CONDITION = "single_self_consistency_temperature"
STAGE_ID = "tool_self_consistency"

register_agentic_stage(
    RegisteredAgenticStage(
        stage_id=STAGE_ID,
        dispatch_kind="standard",
        module=__name__,
        description="E2 four-call boundary-guide tool self-consistency experiment",
    )
)


def run_split(
    records: Sequence[GanFrequencyRecord],
    *,
    reference_rows: Sequence[Mapping[str, Any]],
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
    reference_labels = _reference_labels(reference_rows)
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
            "artifact_kind": "gan2026_agentic_tool_self_consistency",
            "pipeline_family": "agentic_tool_self_consistency",
            "pipeline_version": "gan2026_agentic_e2_tool_self_consistency_v0",
            "claim_boundary": (
                "validation-development hard50 four-call boundary-guide "
                "self-consistency; no holdout use, no row-level test inspection, "
                "and no benchmark claim"
            ),
        },
        build_row=_build_row,
        summarize_rows=summarize_rows,
        gate_interpretation=gate_interpretation,
        write_report=write_report,
    )
    return dispatch_registered_split(
        STAGE_ID,
        records,
        params=params,
        hooks=hooks,
        structured_event_context=StructuredEventSplitContext(
            default_structured_event_jsonl_path=Path("."),
            row_kwargs={"reference_labels": reference_labels},
        ),
    )


def summarize_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    purist_correct = 0
    pragmatic_correct = 0
    wins = 0
    losses = 0
    call_failures = 0
    decision_records = 0
    parse_failures = 0
    for row in rows:
        trace = dict(row.get("condition_trace") or {})
        score = dict(trace.get("final_comparison") or {})
        reference_score = dict(row.get("reference_comparison") or {})
        purist_correct += int(bool(score.get("purist_correct")))
        pragmatic_correct += int(bool(score.get("pragmatic_correct")))
        wins += int(
            bool(score.get("purist_correct"))
            and not bool(reference_score.get("purist_correct"))
        )
        losses += int(
            bool(reference_score.get("purist_correct"))
            and not bool(score.get("purist_correct"))
        )
        for result in trace.get("model_call_results") or []:
            call_failures += int(result.get("call_error") is not None)
            decision_records += int(result.get("decision_record") is not None)
            parse_failures += int(_has_blocking_parse_issue(result.get("parse_errors")))
    return {
        "rows": len(rows),
        "condition": CONDITION,
        "reference_condition": REFERENCE_CONDITION,
        "model_calls_attempted": len(rows) * 4,
        "decision_records": decision_records,
        "call_failures": call_failures,
        "parse_or_validation_failures": parse_failures,
        "purist_correct": purist_correct,
        "pragmatic_correct": pragmatic_correct,
        "wins_vs_reference": wins,
        "losses_vs_reference": losses,
    }


def gate_interpretation(summary: Mapping[str, Any]) -> dict[str, Any]:
    wins = int(summary.get("wins_vs_reference", 0))
    losses = int(summary.get("losses_vs_reference", 0))
    if wins >= 5 and losses <= 2:
        status = "promote_to_boundary_safe_prompt"
        interpretation = (
            "Four-call boundary-guide self-consistency passed the hard50 gate; "
            "continue to E3."
        )
    else:
        status = "reject_tool_self_consistency"
        interpretation = (
            "Four-call boundary-guide self-consistency did not produce enough "
            "high-precision rescues versus self-consistency; stop the current "
            "tool-agent branch before E3/E4."
        )
    return {
        "status": status,
        "wins_vs_reference": wins,
        "losses_vs_reference": losses,
        "interpretation": interpretation,
    }


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
        "# Gan 2026 Agentic Hard50 Tool Self-Consistency",
        "",
        f"Date: {metadata.get('date', 'unknown')}",
        "",
        "## Experiment Unit",
        "",
        "- Work class: E2 four-call boundary-guide-only tool self-consistency.",
        f"- Rows: {summary.get('rows', 0)}",
        f"- Condition: `{CONDITION}`",
        f"- Reference condition: `{REFERENCE_CONDITION}`",
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
        f"- Purist: {summary.get('purist_correct', 0)}/{summary.get('rows', 0)}",
        f"- Pragmatic: {summary.get('pragmatic_correct', 0)}/{summary.get('rows', 0)}",
        f"- Wins vs reference: {summary.get('wins_vs_reference', 0)}",
        f"- Losses vs reference: {summary.get('losses_vs_reference', 0)}",
        "",
        "## Gate",
        "",
        f"- Status: `{gate.get('status')}`",
        f"- Interpretation: {gate.get('interpretation')}",
        "",
        "## Claim Boundary",
        "",
        str(metadata.get("claim_boundary", "")),
        "",
        "## Rows",
        "",
        "| Row | Final | Reference | Purist | Reference Purist | Vote counts | Parse notes |",
        "| ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        trace = dict(row.get("condition_trace") or {})
        comparison = dict(trace.get("final_comparison") or {})
        reference_comparison = dict(row.get("reference_comparison") or {})
        parse_notes = "; ".join(
            str(error)
            for result in trace.get("model_call_results") or []
            for error in result.get("parse_errors") or []
        )
        vote_counts = dict(trace.get("normalized_label_vote") or {}).get("vote_counts") or {}
        lines.append(
            f"| {row.get('source_row_index')} | `{trace.get('final_label')}` | "
            f"`{row.get('reference_label')}` | "
            f"{'yes' if comparison.get('purist_correct') else 'no'} | "
            f"{'yes' if reference_comparison.get('purist_correct') else 'no'} | "
            f"`{vote_counts}` | {parse_notes} |"
        )
    write_markdown_report(path, lines)


def write_jsonl(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    write_jsonl_rows(rows, path)


def _build_row(
    record: GanFrequencyRecord,
    *,
    reference_labels: Mapping[int, str] | None = None,
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
) -> dict[str, Any]:
    reference_label = (
        reference_labels.get(record.source_row_index) if reference_labels else None
    )
    parser_result = parse_seizure_frequency_candidates(record.note_text).model_dump(mode="json")
    guide_results = _boundary_guides_for_parser_result(parser_result)
    trace = _condition_trace(
        record,
        guide_results=guide_results,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        mode=mode,
    )
    return {
        "source_row_index": record.source_row_index,
        "split": split,
        "split_manifest": split_manifest,
        "artifact_mode": mode,
        "reference_condition": REFERENCE_CONDITION,
        "reference_label": reference_label,
        "reference_comparison": _compare_label_to_gold(record, reference_label),
        "condition_trace": trace,
    }


def _condition_trace(
    record: GanFrequencyRecord,
    *,
    guide_results: Sequence[Mapping[str, Any]],
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
) -> dict[str, Any]:
    plans = [
        {
            "call_index": index,
            "call_role": "tool_self_consistency_sample",
            "model": model,
            "temperature": temperature,
            "prompt_version": PROMPT_VERSION,
            "input_note_chars": len(record.note_text),
        }
        for index in range(1, 5)
    ]
    model_call_results = (
        []
        if mode == "prompt-only"
        else [
            _execute_model_call(
                plan,
                record=record,
                guide_results=guide_results,
                max_tokens=max_tokens,
            )
            for plan in plans
        ]
    )
    vote = _normalized_label_vote(model_call_results)
    final_label = vote["selected_label"]
    return {
        "condition": CONDITION,
        "model_call_plans": plans,
        "model_call_results": model_call_results,
        "tool_calls": [
            {
                "tool_name": "read_boundary_guide",
                "status": "context_included",
                "result": guide_result,
                "attribution": "split_neutral_guidance_retrieval",
            }
            for guide_result in guide_results
        ],
        "aggregation": {
            "method": "deterministic_normalized_label_vote",
            "aggregation_model_calls": 0,
        },
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
    record: GanFrequencyRecord,
    guide_results: Sequence[Mapping[str, Any]],
    max_tokens: int,
) -> dict[str, Any]:
    prompt_input_json = _build_prompt_input(
        record,
        call_index=int(plan["call_index"]),
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
    return {
        "call_index": plan["call_index"],
        "call_role": plan["call_role"],
        "model": plan["model"],
        "temperature": plan["temperature"],
        "prompt_version": PROMPT_VERSION,
        "prompt_input_json": prompt_input_json,
        "raw_output": raw_output,
        "raw_model_final_label": _extract_raw_model_final_label(raw_output)
        if raw_output
        else None,
        "call_error": call_error,
        "parse_errors": parse_errors,
        "decision_record": decision.model_dump() if decision else None,
        "comparison": _compare_to_gold(record, decision) if decision else None,
        "attribution": "raw_model" if decision is not None else "no_prediction",
    }


def _build_prompt_input(
    record: GanFrequencyRecord,
    *,
    call_index: int,
    guide_results: Sequence[Mapping[str, Any]],
) -> str:
    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": "Gan 2026 seizure-frequency four-call boundary-guide self-consistency",
        "condition": CONDITION,
        "call_role": "tool_self_consistency_sample",
        "call_index": call_index,
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
        "tool_context": {
            "boundary_guides": list(guide_results),
            "tool_attribution_boundary": (
                "Boundary guides are split-neutral retrieval context. The model owns "
                "the final clinical selection it makes from the full note."
            ),
        },
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


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


def _reference_labels(reference_rows: Sequence[Mapping[str, Any]]) -> dict[int, str]:
    labels: dict[int, str] = {}
    for row in reference_rows:
        source_row_index = row.get("source_row_index")
        if source_row_index is None:
            continue
        trace = dict(
            dict(row.get("condition_traces") or {}).get(REFERENCE_CONDITION) or {}
        )
        label = trace.get("final_label")
        if label is not None:
            labels[int(source_row_index)] = str(label)
    return labels


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


def _load_hard50_indices(path: Path) -> list[int]:
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
        description="Run E2 boundary-guide tool self-consistency on hard50."
    )
    parser.add_argument("--manifest-json", type=Path, required=True)
    parser.add_argument("--reference-jsonl", type=Path, required=True)
    parser.add_argument("--jsonl", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--split", choices=("validation", "train", "test"), default="validation")
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
    indices = _load_hard50_indices(args.manifest_json)
    records = _filter_records_by_source_indices(load_records_for_split(args.split), indices)
    manifest = load_split_manifest()
    split_manifest = str(manifest.get("manifest_version", "gan2026_split_v1"))
    rows, metadata = run_split(
        records,
        reference_rows=load_jsonl_rows(args.reference_jsonl),
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
    metadata["reference_jsonl_path"] = str(args.reference_jsonl)
    write_jsonl(rows, args.jsonl)
    write_report(rows, metadata, args.markdown, jsonl_path=args.jsonl)
    print(json.dumps(metadata["gate"], sort_keys=True))


if __name__ == "__main__":
    main()
