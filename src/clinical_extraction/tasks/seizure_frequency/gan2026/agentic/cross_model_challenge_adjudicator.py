"""Open peer-challenge adjudicator over saved Gan structured-event agents.

This V11 candidate keeps the V10 renderer/scorer contract but changes the
coordinator task. Instead of preferring GPT with a high-precision safety gate,
the model must adjudicate disagreements directly and choose the clinically best
saved structured-event final from GPT, Qwen, or DeepSeek. Deterministic code
still cannot synthesize labels or fall back to deterministic top.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    cross_model_structured_event_adjudicator as base,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    llm_event_reasoner,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_metadata import (
    build_run_metadata,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm
from clinical_extraction.tasks.seizure_frequency.gan2026.reports.base import (
    write_markdown_report,
)

PROMPT_VERSION = "gan2026_cross_model_challenge_adjudicator_v0_1"
PIPELINE_FAMILY = "cross_model_challenge_adjudicator"
DEFAULT_STRUCTURED_EVENT_JSONL_PATH = base.DEFAULT_STRUCTURED_EVENT_JSONL_PATH
DEFAULT_QWEN_STRUCTURED_EVENT_JSONL_PATH = base.DEFAULT_QWEN_STRUCTURED_EVENT_JSONL_PATH
DEFAULT_DEEPSEEK_STRUCTURED_EVENT_JSONL_PATH = (
    base.DEFAULT_DEEPSEEK_STRUCTURED_EVENT_JSONL_PATH
)
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_cross_model_challenge_adjudicator_validation.jsonl"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_cross_model_challenge_adjudicator_validation.md"
)
DEFAULT_GATED_JSONL_PATH = Path(
    "experiments/gan2026_cross_model_challenge_gated_adjudicator_validation.jsonl"
)
DEFAULT_GATED_REPORT_PATH = Path(
    "experiments/gan2026_cross_model_challenge_gated_adjudicator_validation.md"
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
    escalation_reason: str | None,
    progress_every: int | None,
    checkpoint_jsonl_path: Path | None,
    checkpoint_report_path: Path | None,
    candidate_set_jsonl_path: Path | None = None,
    structured_event_jsonl_path: Path | None = None,
    structured_event_rows: Sequence[Mapping[str, Any]] | None = None,
    structured_event_source_path: Path | None = None,
    agent_rows_by_id: Mapping[str, Sequence[Mapping[str, Any]]] | None = None,
    safety_policy: Literal["none", "high_precision"] = "none",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run or prompt-smoke the open cross-model peer challenge coordinator."""

    del escalation_reason, candidate_set_jsonl_path
    source_path = (
        structured_event_source_path
        or structured_event_jsonl_path
        or DEFAULT_STRUCTURED_EVENT_JSONL_PATH
    )
    agent_sources = {
        "gpt": source_path,
        "qwen": DEFAULT_QWEN_STRUCTURED_EVENT_JSONL_PATH,
        "deepseek": DEFAULT_DEEPSEEK_STRUCTURED_EVENT_JSONL_PATH,
    }
    if structured_event_rows is None:
        structured_event_rows = load_jsonl_rows(source_path)
    loaded_agent_rows = base._load_agent_rows(
        gpt_rows=structured_event_rows,
        agent_sources=agent_sources,
        agent_rows_by_id=agent_rows_by_id,
    )
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

    rows_by_agent = {
        agent_id: llm_event_reasoner._rows_by_source_index(rows)
        for agent_id, rows in loaded_agent_rows.items()
    }
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
            "artifact_kind": "gan2026_cross_model_challenge_adjudicator_trace",
            "pipeline_family": PIPELINE_FAMILY,
            "pipeline_version": PROMPT_VERSION,
            "agent_source_paths": {
                agent_id: str(path) for agent_id, path in agent_sources.items()
            },
            "structured_event_source_role": (
                "GPT, Qwen, and DeepSeek saved LLM structured-event finals are "
                "peer candidates. Deterministic top labels are not shown or used."
            ),
            "claim_boundary": (
                "validation-development V11 open cross-model challenge "
                "adjudicator; no holdout use, no row-level test inspection, and "
                "no benchmark claim"
            ),
            "safety_policy": _safety_policy_label(safety_policy),
            "dspy_cache": dspy_cache,
        }
    )

    rows: list[dict[str, Any]] = []
    for record in records:
        rows.append(
            _build_row(
                record,
                agent_rows={
                    agent_id: rows_by_agent.get(agent_id, {}).get(
                        record.source_row_index
                    )
                    for agent_id in base.AGENT_IDS
                },
                split=split,
                split_manifest=split_manifest,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                mode=mode,
                safety_policy=safety_policy,
            )
        )
        if progress_every and len(rows) % progress_every == 0:
            _emit_progress_checkpoint(
                rows,
                metadata,
                total=len(records),
                jsonl_path=checkpoint_jsonl_path,
                report_path=checkpoint_report_path,
            )

    metadata["summary"] = summarize_rows(rows)
    metadata["gate"] = llm_event_reasoner.gate_interpretation(metadata["summary"])
    return rows, metadata


def build_prompt_input(
    record: GanFrequencyRecord,
    agent_rows: Mapping[str, Mapping[str, Any] | None],
) -> str:
    """Build a split-neutral, disagreement-focused peer challenge payload."""

    agent_inputs = [
        base._agent_prompt_summary(agent_id, agent_rows.get(agent_id))
        for agent_id in base.AGENT_IDS
    ]
    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": "Gan 2026 open peer challenge over structured-event finals",
        "variant": "V11_cross_model_challenge_adjudicator",
        "instructions": [
            (
                "Choose the clinically best saved structured-event final among "
                "GPT, Qwen, and DeepSeek. The three agents are peers for this "
                "task; do not default to GPT because it is listed first."
            ),
            (
                "The final answer will be rendered from the selected agent's "
                "original_final.final_label. Do not invent, recompute, average, "
                "or create a new label."
            ),
            (
                "Use only the agent event tables, original finals, rationales, "
                "exact evidence contexts, adjudicator hints, and note excerpt. "
                "Do not use row IDs, split membership, gold labels, scoring "
                "metadata, deterministic rules, or deterministic top labels."
            ),
            (
                "Actively challenge each agent's final answer: ask whether its "
                "selected event is current versus historical, countable versus "
                "last-event-only, frequency versus duration, seizure-free versus "
                "conflicting active seizures, cluster cadence versus events per "
                "cluster, and highest active semiology versus lower burden."
            ),
            (
                "Exact label majority is only weak evidence. Prefer the agent "
                "whose selected event and evidence best answer the current "
                "seizure-frequency question."
            ),
            (
                "When selecting a peer, final_label must copy that peer's "
                "original_final.final_label exactly and selected_event_ids should "
                "copy that peer's original_final.selected_event_ids."
            ),
            (
                "For keep_gpt_final, selected_agent_id must be gpt. For "
                "select_qwen_final, selected_agent_id must be qwen. For "
                "select_deepseek_final, selected_agent_id must be deepseek."
            ),
            "Evidence entries should be exact substrings from the note when possible.",
            (
                "final_kind, uncertainty, attribution, action, and selected_agent_id "
                "must each be one string, not an array of options."
            ),
        ],
        "required_output_schema": {
            "action": list(base.PROMPT_ACTION_VALUES),
            "selected_agent_id": list(base.AGENT_IDS),
            "final_label": "copy of selected agent original_final.final_label",
            "final_kind": [
                "frequency",
                "seizure_free",
                "unknown",
                "no_reference",
                "unresolved_multiple",
            ],
            "selected_event_ids": "selected event IDs from the chosen agent",
            "rejected_agent_ids": "agent IDs explicitly rejected",
            "evidence": "list of exact evidence substrings supporting the choice",
            "comparison_profile": "list of disagreement profiles driving the choice",
            "calculation_trace": "short arithmetic or boundary trace, or null",
            "clinical_rationale": "brief rationale for why this agent wins",
            "uncertainty": "one string: low | medium | high",
            "attribution": (
                "one string: llm_selected_tool_rendered | "
                "llm_selected_format_repaired | llm_original_structured_event_kept"
            ),
        },
        "agent_inputs": agent_inputs,
        "agreement_features": base._agreement_features(agent_inputs),
        "adjudicator_hints": base._adjudicator_hints(agent_rows),
        "raw_evidence_contexts": base._combined_evidence_contexts(
            record.note_text,
            agent_rows,
        ),
        "raw_note_excerpt": record.note_text[:6000],
        "excerpt_truncated": len(record.note_text) > 6000,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def summarize_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    summary = base.summarize_rows(rows)
    policies = sorted(
        {
            str(row.get("safety_policy"))
            for row in rows
            if row.get("safety_policy") is not None
        }
    )
    summary["safety_policy"] = policies[0] if len(policies) == 1 else policies
    return summary


def write_jsonl(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    base.write_jsonl(rows, path)


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
        "# Gan 2026 Cross-Model Challenge Adjudicator",
        "",
        f"Date: {metadata.get('date', 'unknown')}",
        "",
        "This is a validation-development V11 open peer-challenge artifact.",
        "The model chooses among saved GPT, Qwen, and DeepSeek structured-event finals.",
        "",
        "## Experiment Unit",
        "",
        "- Work class: V11 open cross-model peer challenge.",
        f"- Rows: {summary.get('rows', 0)}",
        "- Split: `validation`, manifest `gan2026_split_v1`.",
        f"- Mode: `{metadata.get('mode')}`",
        f"- Model: `{metadata.get('model')}`",
        f"- Prompt version: `{metadata.get('prompt_version')}`",
        f"- Safety policy: `{metadata.get('safety_policy')}`",
        f"- JSONL artifact: `{jsonl_path}`",
        "",
        "## Summary",
        "",
        f"- Prediction-bearing rows: {summary.get('prediction_bearing_rows', 0)}",
        f"- Model calls attempted: {summary.get('model_calls_attempted', 0)}",
        f"- Call failures: {summary.get('call_failures', 0)}",
        f"- Parse/schema/label failures: {summary.get('parse_or_validation_failures', 0)}",
        f"- Action-render fallbacks: {summary.get('action_render_fallbacks', 0)}",
        f"- Exact evidence substrings: {summary.get('evidence_exact_substrings', 0)}",
        f"- GPT V0 Purist: {summary.get('v0_purist_correct', 0)}/{summary.get('rows', 0)}",
        (
            f"- Raw declared Purist: {summary.get('raw_model_purist_correct', 0)}/"
            f"{summary.get('rows', 0)}"
        ),
        f"- Final Purist: {summary.get('final_purist_correct', 0)}/{summary.get('rows', 0)}",
        f"- Net Purist gain vs GPT V0: {summary.get('net_purist_gain_vs_v0', 0)}",
        (
            "- Changed-label precision vs GPT V0: "
            f"{summary.get('changed_label_precision_vs_v0')}"
        ),
        f"- Selected agents: `{summary.get('selected_agent_counts', {})}`",
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
        "| Row | Selected | GPT | Raw | Final | Transition | Evidence exact | Notes |",
        "| ---: | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        layers = dict(row.get("score_layers") or {})
        decision = dict(row.get("cross_model_decision_record") or {})
        notes = "; ".join(str(error) for error in row.get("parse_errors") or [])
        if row.get("call_error"):
            notes = f"{notes}; {row['call_error']}" if notes else str(row["call_error"])
        lines.append(
            f"| {row.get('source_row_index')} | "
            f"`{decision.get('selected_agent_id')}` | "
            f"`{dict(row.get('v0_reference') or {}).get('final_label')}` | "
            f"`{dict(layers.get('raw_model') or {}).get('final_label')}` | "
            f"`{dict(layers.get('final') or {}).get('final_label')}` | "
            f"`{dict(row.get('transition_vs_v0') or {}).get('purist_transition')}` | "
            f"{'yes' if row.get('evidence_valid') else 'no'} | {notes} |"
        )
    write_markdown_report(path, lines)


class CrossModelChallengeSignature(dspy.Signature):
    """Adjudicate saved cross-model structured-event finals and emit JSON."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON payload with sanitized GPT, Qwen, and DeepSeek structured-event rows."
    )
    decision_json: str = dspy.OutputField(
        desc="Strict JSON object matching CrossModelAdjudicatorDecision."
    )


class DspyCrossModelChallengeCaller(dspy.Module):
    """DSPy caller for V11 cross-model challenge adjudication."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(CrossModelChallengeSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def _build_row(
    record: GanFrequencyRecord,
    *,
    agent_rows: Mapping[str, Mapping[str, Any] | None],
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
    safety_policy: Literal["none", "high_precision"],
) -> dict[str, Any]:
    prompt_input_json = build_prompt_input(record, agent_rows)
    raw_output = ""
    call_error: str | None = None
    model_call_attempted = False
    if mode == "live":
        model_call_attempted = True
        try:
            raw_output = _run_model_call(
                prompt_input_json,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as exc:  # pragma: no cover - live transport only.
            call_error = f"{type(exc).__name__}: {exc}"
    parsed = (
        base.parse_cross_model_decision_json(
            raw_output,
            agent_rows=agent_rows,
            note_text=record.note_text,
            safety_policy=safety_policy,
        )
        if raw_output
        else base.ParsedCrossModelDecision(
            raw_decision=None,
            raw_common_decision=None,
            format_only_decision=None,
            final_decision=None,
            parse_errors=["not_run"],
        )
    )
    final_decision = parsed.final_decision
    gpt_reference = llm_event_reasoner._v0_reference(agent_rows.get("gpt"))
    score_layers = {
        "raw_model": llm_event_reasoner._score_layer(
            record,
            parsed.raw_common_decision,
        ),
        "format_only": llm_event_reasoner._score_layer(
            record,
            parsed.format_only_decision,
        ),
        "final": llm_event_reasoner._score_layer(record, final_decision),
    }
    evidence_valid = llm_event_reasoner._decision_evidence_valid(
        record.note_text,
        final_decision,
    )
    return {
        "source_row_index": record.source_row_index,
        "split": split,
        "split_manifest": split_manifest,
        "artifact_mode": mode,
        "pipeline_family": PIPELINE_FAMILY,
        "prompt_version": PROMPT_VERSION,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "safety_policy": _safety_policy_label(safety_policy),
        "agent_inputs_available": {
            agent_id: agent_rows.get(agent_id) is not None for agent_id in base.AGENT_IDS
        },
        "agent_references": {
            agent_id: base._agent_reference(agent_rows.get(agent_id))
            for agent_id in base.AGENT_IDS
        },
        "v0_reference": gpt_reference,
        "model_call_attempted": model_call_attempted,
        "prompt_input_json": prompt_input_json,
        "raw_output": raw_output,
        "call_error": call_error,
        "parse_errors": parsed.parse_errors,
        "format_repair_events": parsed.format_repair_events,
        "action_render_events": parsed.action_render_events,
        "cross_model_decision_record": (
            parsed.raw_decision.model_dump(mode="json") if parsed.raw_decision else None
        ),
        "raw_decision_record": (
            parsed.raw_common_decision.model_dump(mode="json")
            if parsed.raw_common_decision
            else None
        ),
        "format_only_decision_record": (
            parsed.format_only_decision.model_dump(mode="json")
            if parsed.format_only_decision
            else None
        ),
        "decision_record": final_decision.model_dump(mode="json") if final_decision else None,
        "evidence_valid": evidence_valid,
        "score_layers": score_layers,
        "transition_vs_v0": llm_event_reasoner._transition_vs_v0(
            v0_reference=gpt_reference,
            final_layer=score_layers["final"],
        ),
        "reference": {
            "gold_label": record.gold_label,
            "gold_monthly_frequency": record.gold_monthly_frequency,
            "row_ok": record.row_ok,
        },
        "trace_warnings": (
            ["prompt_only_no_prediction"] if mode == "prompt-only" else []
        )
        + [
            f"missing_{agent_id}_structured_event_row"
            for agent_id in base.AGENT_IDS
            if agent_rows.get(agent_id) is None
        ],
    }


def _run_model_call(
    prompt_input_json: str,
    *,
    model: str,
    temperature: float,
    max_tokens: int,
) -> str:
    del model, temperature, max_tokens
    prediction = DspyCrossModelChallengeCaller()(prompt_input_json=prompt_input_json)
    return str(prediction.decision_json)


def _safety_policy_label(safety_policy: Literal["none", "high_precision"]) -> str:
    if safety_policy == "high_precision":
        return "high_precision_peer_gate"
    return "none_model_owned_agent_selection"


def _emit_progress_checkpoint(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    *,
    total: int,
    jsonl_path: Path | None,
    report_path: Path | None,
) -> None:
    summary = summarize_rows(rows)
    print(
        json.dumps(
            {
                "pipeline": PIPELINE_FAMILY,
                "completed": len(rows),
                "total": total,
                "final_purist_correct": summary.get("final_purist_correct"),
                "net_purist_gain_vs_v0": summary.get("net_purist_gain_vs_v0"),
            },
            sort_keys=True,
        )
    )
    if jsonl_path is not None:
        write_jsonl(rows, jsonl_path)
    if report_path is not None:
        checkpoint_metadata = dict(metadata)
        checkpoint_metadata["summary"] = summary
        checkpoint_metadata["gate"] = llm_event_reasoner.gate_interpretation(summary)
        write_report(rows, checkpoint_metadata, report_path, jsonl_path=jsonl_path or Path(""))
