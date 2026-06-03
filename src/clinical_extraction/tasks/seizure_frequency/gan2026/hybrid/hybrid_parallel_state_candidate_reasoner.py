"""Hybrid parallel state/candidate reasoner for Gan 2026 validation smokes."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.replay_io import (
    load_raw_outputs_by_source_index,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.schema_repair import (
    repair_decision_payload,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.repair_modes import (
    repair_mode_layers,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_metadata import (
    build_run_metadata,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    repair_prediction_label,
    repair_prediction_label_format_preserving,
    repair_prediction_label_with_evidence,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.pipeline_v1 import (
    Gan2026PipelineV1,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.state_graph import (
    build_state_graph,
    project_graph_to_gan,
)

PROMPT_VERSION = "gan2026_hybrid_parallel_state_candidate_reasoner_v0"
PIPELINE_FAMILY = "hybrid_parallel_state_candidate_reasoner"
SCORE_LAYER_NAMES = (
    "deterministic_top_candidate",
    "state_graph_projection",
    "llm_candidate_selector_raw",
    "hybrid_adjudicator_raw",
    "hybrid_adjudicator_with_adapters",
    "adapter_only_sidecar_from_adjudicator_selection",
)
ANALYSIS_LAYER_NAMES = (
    "oracle_candidate_presence",
    "oracle_graph_representability",
)
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation25_gpt41mini_v0_2026-06-02.jsonl"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation25_gpt41mini_v0_2026-06-02.md"
)


class HybridLlmCandidate(BaseModel):
    """Independent LLM candidate emitted before final hybrid adjudication."""

    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    kind: Literal[
        "frequency_rate",
        "cluster_frequency",
        "seizure_free",
        "last_event_only",
        "unknown_frequency",
        "no_reference",
    ]
    applies_to: str | None = None
    evidence: str
    raw_value: str
    temporality: Literal["current", "recent", "historical", "future", "unclear"]
    assertion_status: Literal["asserted", "negated", "hypothetical", "uncertain"]
    normalized_label: str | None = None
    confidence: Literal["high", "medium", "low"]
    rationale: str = ""


class HybridLlmCandidateSelection(BaseModel):
    """LLM candidate selector's own raw top candidate."""

    model_config = ConfigDict(extra="forbid")

    selected_candidate_ids: list[str]
    final_label: str
    final_kind: Literal[
        "frequency",
        "seizure_free",
        "unknown",
        "no_reference",
        "unresolved_multiple",
    ]
    selected_evidence: str
    rationale: str = ""


class HybridLlmCandidatePacket(BaseModel):
    """Full independent LLM candidate selector output."""

    model_config = ConfigDict(extra="forbid")

    candidates: list[HybridLlmCandidate]
    selection: HybridLlmCandidateSelection


class HybridParallelAdjudicatorDecision(BaseModel):
    """Typed final hybrid adjudicator output."""

    model_config = ConfigDict(extra="forbid")

    final_label: str
    final_kind: Literal[
        "frequency",
        "seizure_free",
        "unknown",
        "no_reference",
        "unresolved_multiple",
    ]
    selected_source_ids: list[str]
    selected_source_types: list[
        Literal[
            "deterministic_candidate",
            "state_graph_node",
            "llm_candidate",
            "adjudicator_synthesis",
        ]
    ]
    selected_evidence: str
    confidence: Literal["high", "medium", "low"]
    rationale: str
    supporting_source_ids: list[str] = Field(default_factory=list)


class Gan2026HybridLlmCandidateSignature(dspy.Signature):
    """Extract independent LLM candidates for hybrid adjudication."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one Gan 2026 note and the LLM-candidate output schema."
    )
    llm_candidate_json: str = dspy.OutputField(
        desc="One strict JSON object with candidates and selection."
    )


class Gan2026HybridAdjudicatorSignature(dspy.Signature):
    """Adjudicate deterministic, graph, and LLM candidate sources."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing note text, deterministic candidates, graph nodes, and LLM candidates."
    )
    adjudicator_json: str = dspy.OutputField(
        desc="One strict JSON object with final_label and selected source provenance."
    )


class DspyHybridLlmCandidateSelector(dspy.Module):
    """DSPy wrapper for independent LLM candidate selection."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(Gan2026HybridLlmCandidateSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


class DspyHybridParallelAdjudicator(dspy.Module):
    """DSPy wrapper for final hybrid parallel adjudication."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(Gan2026HybridAdjudicatorSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def build_llm_candidate_prompt_input(record: GanFrequencyRecord) -> str:
    """Build the independent LLM-candidate selector prompt without gold labels."""

    payload = {
        "prompt_version": PROMPT_VERSION,
        "pipeline_family": PIPELINE_FAMILY,
        "task": "Gan 2026 hybrid independent LLM candidate selector",
        "source_row_index": record.source_row_index,
        "instructions": [
            "Read the full note and emit compact source-near seizure-frequency candidates.",
            "Do not use deterministic candidates or gold labels; this stage is independent.",
            (
                "Every candidate evidence value must be an exact substring copied from the note. "
                "Use no_reference only when the note has no seizure-frequency evidence."
            ),
            (
                "The selection should choose the current or recent clinical state that would be "
                "most relevant for Gan-compatible seizure-frequency scoring."
            ),
            "Return exactly one JSON object with top-level keys candidates and selection.",
        ],
        "candidate_schema": {
            "candidate_id": "stable string such as llm-1",
            "kind": [
                "frequency_rate",
                "cluster_frequency",
                "seizure_free",
                "last_event_only",
                "unknown_frequency",
                "no_reference",
            ],
            "applies_to": "seizure type or clinical target, or null",
            "evidence": "exact note substring",
            "raw_value": "source-near frequency/state phrase",
            "temporality": ["current", "recent", "historical", "future", "unclear"],
            "assertion_status": ["asserted", "negated", "hypothetical", "uncertain"],
            "normalized_label": "model-rendered Gan label, unknown, no-reference, or null",
            "confidence": ["high", "medium", "low"],
            "rationale": "short source-near reason",
        },
        "selection_schema": {
            "selected_candidate_ids": "list of candidate ids",
            "final_label": "raw model-selected Gan label",
            "final_kind": [
                "frequency",
                "seizure_free",
                "unknown",
                "no_reference",
                "unresolved_multiple",
            ],
            "selected_evidence": "exact evidence from one selected candidate",
            "rationale": "short clinical selection reason",
        },
        "note_text": record.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def build_adjudicator_prompt_input(component_inputs: Mapping[str, Any]) -> str:
    """Build the final hybrid adjudicator prompt from prepared component inputs."""

    payload = {
        "prompt_version": PROMPT_VERSION,
        "pipeline_family": PIPELINE_FAMILY,
        "task": "Gan 2026 hybrid parallel state/candidate adjudication",
        "source_row_index": component_inputs["source_row_index"],
        "instructions": [
            "Read the full note and all candidate tables.",
            (
                "Select the final clinical seizure-frequency state from deterministic candidates, "
                "state graph nodes, LLM candidates, or explicit adjudicator synthesis."
            ),
            (
                "Report selected_source_ids using prefixes det:, graph:, llm:, or synth:. "
                "Use synth: only when the final answer combines exact evidence not represented "
                "by a supplied row."
            ),
            (
                "Copy selected_evidence as an exact note substring. Do not include gold labels."
            ),
            "Return exactly one JSON object matching adjudicator_schema.",
        ],
        "adjudicator_schema": {
            "final_label": "raw Gan-compatible label, unknown, or no seizure frequency reference",
            "final_kind": [
                "frequency",
                "seizure_free",
                "unknown",
                "no_reference",
                "unresolved_multiple",
            ],
            "selected_source_ids": "list of det:/graph:/llm:/synth: ids",
            "selected_source_types": [
                "deterministic_candidate",
                "state_graph_node",
                "llm_candidate",
                "adjudicator_synthesis",
            ],
            "selected_evidence": "exact note substring supporting the final answer",
            "confidence": ["high", "medium", "low"],
            "rationale": "short source-near reason",
            "supporting_source_ids": "optional additional source ids",
        },
        "score_layers_to_report": [*SCORE_LAYER_NAMES, *ANALYSIS_LAYER_NAMES],
        "note_text": component_inputs["note_text"],
        "deterministic_top": component_inputs["deterministic_top"],
        "deterministic_candidates": component_inputs["deterministic_candidates"],
        "state_graph_projection": component_inputs["state_graph_projection"],
        "state_graph_nodes": component_inputs["state_graph_nodes"],
        "llm_candidates": component_inputs["llm_candidates"],
        "llm_candidate_selection": component_inputs["llm_candidate_selection"],
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def parse_llm_candidate_json(
    raw_output: str,
    *,
    note_text: str | None = None,
) -> tuple[HybridLlmCandidatePacket | None, list[str]]:
    """Parse and validate one independent LLM-candidate selector output."""

    try:
        payload = _repair_llm_candidate_payload(json.loads(_extract_json_object(raw_output)))
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json: {exc.msg}"]
    try:
        packet = HybridLlmCandidatePacket.model_validate(payload)
    except ValidationError as exc:
        return None, [f"schema_validation_error: {exc.errors()[0]['msg']}"]
    if note_text is not None:
        packet = _repair_llm_candidate_evidence_copy(packet, note_text)

    errors: list[str] = []
    candidate_ids = {candidate.candidate_id for candidate in packet.candidates}
    missing_ids = [
        candidate_id
        for candidate_id in packet.selection.selected_candidate_ids
        if candidate_id not in candidate_ids
    ]
    if missing_ids:
        errors.append(f"selection: unknown selected_candidate_ids {missing_ids!r}")
    selected_evidence_values = {
        candidate.evidence
        for candidate in packet.candidates
        if candidate.candidate_id in packet.selection.selected_candidate_ids
    }
    if packet.selection.selected_evidence not in selected_evidence_values:
        errors.append("evidence: selected evidence is not one selected candidate evidence value")
    if note_text is not None:
        invalid_ids = [
            candidate.candidate_id
            for candidate in packet.candidates
            if not evidence_is_substring(note_text, candidate.evidence)
        ]
        if invalid_ids:
            errors.append(f"evidence: invalid candidate evidence for {invalid_ids!r}")
        if not evidence_is_substring(note_text, packet.selection.selected_evidence):
            errors.append("evidence: invalid selected evidence")
    return packet, errors


def parse_adjudicator_json(
    raw_output: str,
    *,
    allowed_source_ids: set[str] | None = None,
    note_text: str | None = None,
) -> tuple[HybridParallelAdjudicatorDecision | None, list[str]]:
    """Parse and validate one final hybrid adjudicator output."""

    try:
        payload = _repair_adjudicator_payload(json.loads(_extract_json_object(raw_output)))
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json: {exc.msg}"]
    try:
        decision = HybridParallelAdjudicatorDecision.model_validate(payload)
    except ValidationError as exc:
        return None, [f"schema_validation_error: {exc.errors()[0]['msg']}"]

    errors: list[str] = []
    repaired_label = repair_prediction_label(decision.final_label)
    if repaired_label != decision.final_label:
        errors.append(f"final_label_repaired: {decision.final_label!r} -> {repaired_label!r}")
        decision = decision.model_copy(update={"final_label": repaired_label})
    try:
        label_to_frequency_record(decision.final_label)
    except ValueError as exc:
        errors.append(f"unscorable_final_label: {exc}")
    if allowed_source_ids is not None:
        decision, source_id_repairs = _canonicalize_decision_source_ids(
            decision,
            allowed_source_ids,
        )
        errors.extend(source_id_repairs)
        unknown = [
            source_id
            for source_id in [*decision.selected_source_ids, *decision.supporting_source_ids]
            if not source_id.startswith("synth:") and source_id not in allowed_source_ids
        ]
        if unknown:
            errors.append(f"selected_source_ids: unknown ids {unknown!r}")
    if len(decision.selected_source_types) != len(decision.selected_source_ids):
        decision = decision.model_copy(
            update={
                "selected_source_types": [
                    _source_type_from_id(source_id) for source_id in decision.selected_source_ids
                ]
            }
        )
        errors.append("selected_source_types_repaired_from_source_ids")
    if note_text is not None:
        decision = decision.model_copy(
            update={
                "selected_evidence": _repair_case_only_evidence_copy(
                    decision.selected_evidence,
                    note_text,
                )
            }
        )
    if note_text is not None and not evidence_is_substring(note_text, decision.selected_evidence):
        errors.append("evidence: invalid selected evidence")
    return decision, errors


def run_split(
    records: Sequence[GanFrequencyRecord],
    *,
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
    dspy_cache: bool = True,
    api_base: str | None = None,
    reuse_llm_candidate_outputs: Mapping[int, str] | None = None,
    reuse_adjudicator_outputs: Mapping[int, str] | None = None,
    reuse_source: str | None = None,
    escalation_reason: str | None = None,
    progress_every: int | None = None,
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run the hybrid parallel smoke over validation rows or prompt-only inputs."""

    reuse_llm_candidate_outputs = reuse_llm_candidate_outputs or {}
    reuse_adjudicator_outputs = reuse_adjudicator_outputs or {}
    metadata = _run_metadata(
        records,
        split=split,
        split_manifest=split_manifest,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        mode=mode,
        api_base=api_base,
    )
    metadata["dspy_cache"] = dspy_cache
    metadata["reuse_source"] = reuse_source
    metadata["escalation_reason"] = escalation_reason
    metadata["repair_mode_layers"] = repair_mode_layers(SCORE_LAYER_NAMES)
    llm_program = DspyHybridLlmCandidateSelector()
    adjudicator_program = DspyHybridParallelAdjudicator()
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

    rows: list[dict[str, Any]] = []
    for record in records:
        deterministic = _deterministic_components(record)
        graph = _graph_components(record)
        llm_candidate_prompt_input_json = build_llm_candidate_prompt_input(record)
        llm_candidate_raw_output = reuse_llm_candidate_outputs.get(record.source_row_index, "")
        adjudicator_raw_output = reuse_adjudicator_outputs.get(record.source_row_index, "")
        llm_candidate_call_error: str | None = None
        adjudicator_call_error: str | None = None
        reused_llm_candidate_output = llm_candidate_raw_output != ""
        reused_adjudicator_output = adjudicator_raw_output != ""
        if mode == "live" and not reused_llm_candidate_output:
            try:
                prediction = llm_program(prompt_input_json=llm_candidate_prompt_input_json)
                llm_candidate_raw_output = str(prediction.llm_candidate_json)
            except Exception as exc:  # pragma: no cover - exercised only with live APIs.
                llm_candidate_call_error = f"{type(exc).__name__}: {exc}"

        llm_packet, llm_candidate_parse_errors = (
            parse_llm_candidate_json(llm_candidate_raw_output, note_text=record.note_text)
            if llm_candidate_raw_output
            else (None, ["not_run"])
        )
        component_inputs = _component_inputs(record, deterministic, graph, llm_packet)
        adjudicator_prompt_input_json = build_adjudicator_prompt_input(component_inputs)
        if mode == "live" and not reused_adjudicator_output:
            try:
                prediction = adjudicator_program(prompt_input_json=adjudicator_prompt_input_json)
                adjudicator_raw_output = str(prediction.adjudicator_json)
            except Exception as exc:  # pragma: no cover - exercised only with live APIs.
                adjudicator_call_error = f"{type(exc).__name__}: {exc}"

        allowed_source_ids = _allowed_source_ids(component_inputs)
        decision, adjudicator_parse_errors = (
            parse_adjudicator_json(
                adjudicator_raw_output,
                allowed_source_ids=allowed_source_ids,
                note_text=record.note_text,
            )
            if adjudicator_raw_output
            else (None, ["not_run"])
        )
        score_layers = _score_layers(record, deterministic, graph, llm_packet, decision)
        analysis_layers = _analysis_layers(record, deterministic, graph)
        diagnostics = _diagnostics(record, component_inputs, llm_packet, decision)
        component_status = _component_status(
            deterministic=deterministic,
            graph=graph,
            llm_packet=llm_packet,
            decision=decision,
            llm_candidate_parse_errors=llm_candidate_parse_errors,
            adjudicator_parse_errors=adjudicator_parse_errors,
            diagnostics=diagnostics,
            llm_candidate_call_error=llm_candidate_call_error,
            adjudicator_call_error=adjudicator_call_error,
        )
        rows.append(
            {
                "source_row_index": record.source_row_index,
                "split": split,
                "split_manifest": split_manifest,
                "pipeline_family": PIPELINE_FAMILY,
                "pipeline_name": PROMPT_VERSION,
                "prompt_version": PROMPT_VERSION,
                "llm_candidate_prompt_input_json": llm_candidate_prompt_input_json,
                "adjudicator_prompt_input_json": adjudicator_prompt_input_json,
                "llm_candidate_raw_output": llm_candidate_raw_output,
                "adjudicator_raw_output": adjudicator_raw_output,
                "raw_output": adjudicator_raw_output,
                "reused_llm_candidate_output": reused_llm_candidate_output,
                "reused_adjudicator_output": reused_adjudicator_output,
                "call_error": adjudicator_call_error or llm_candidate_call_error,
                "llm_candidate_call_error": llm_candidate_call_error,
                "adjudicator_call_error": adjudicator_call_error,
                "llm_candidate_parse_errors": llm_candidate_parse_errors,
                "adjudicator_parse_errors": adjudicator_parse_errors,
                "parse_errors": [*llm_candidate_parse_errors, *adjudicator_parse_errors],
                "structured_llm_candidate_record": (
                    llm_packet.model_dump() if llm_packet else None
                ),
                "structured_adjudicator_record": decision.model_dump() if decision else None,
                "component_inputs": component_inputs,
                "component_status": component_status,
                "diagnostics": diagnostics,
                "score_layers": score_layers,
                "analysis_layers": analysis_layers,
                "repair_changes": _repair_changes(score_layers),
                "repair_mode_layers": repair_mode_layers(SCORE_LAYER_NAMES),
                "reference": {
                    "gold_label": record.gold_label,
                    "gold_normalized_label": record.gold_normalized_label,
                    "gold_label_kind": str(record.gold_label_kind),
                    "gold_monthly_frequency": record.gold_monthly_frequency,
                    "row_ok": record.row_ok,
                },
            }
        )
        if progress_every and len(rows) % progress_every == 0:
            _emit_progress_checkpoint(
                rows,
                metadata,
                total=len(records),
                jsonl_path=checkpoint_jsonl_path,
                report_path=checkpoint_report_path,
            )

    metadata["summary"] = summarize_records(rows)
    return rows, metadata


def summarize_records(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize hybrid parallel validation-smoke rows."""

    count = len(rows)
    component_failures = Counter(
        component
        for row in rows
        for component, status in (row.get("component_status") or {}).items()
        if status != "ok"
    )
    summary: dict[str, Any] = {
        "examples": count,
        "structured_llm_candidate_records": sum(
            bool(row.get("structured_llm_candidate_record")) for row in rows
        ),
        "structured_adjudicator_records": sum(
            bool(row.get("structured_adjudicator_record")) for row in rows
        ),
        "call_failures": sum(bool(row.get("call_error")) for row in rows),
        "reused_llm_candidate_outputs": sum(
            bool(row.get("reused_llm_candidate_output")) for row in rows
        ),
        "reused_adjudicator_outputs": sum(
            bool(row.get("reused_adjudicator_output")) for row in rows
        ),
        "parse_or_validation_failures": sum(_has_blocking_parse_issue(row) for row in rows),
        "selected_evidence_exact": sum(
            bool((row.get("diagnostics") or {}).get("selected_evidence_exact")) for row in rows
        ),
        "selected_source_ids_exist": sum(
            bool((row.get("diagnostics") or {}).get("selected_source_ids_exist")) for row in rows
        ),
        "candidate_recall_rescues": sum(
            bool((row.get("diagnostics") or {}).get("candidate_recall_rescue")) for row in rows
        ),
        "graph_representability_rescues": sum(
            bool((row.get("diagnostics") or {}).get("graph_representability_rescue"))
            for row in rows
        ),
        "deterministic_correct_regressions": sum(
            bool((row.get("diagnostics") or {}).get("deterministic_correct_regression"))
            for row in rows
        ),
        "graph_projection_regressions": sum(
            bool((row.get("diagnostics") or {}).get("graph_projection_regression"))
            for row in rows
        ),
        "adapter_changed_rows": sum(bool(row.get("repair_changes")) for row in rows),
        "component_failures": dict(sorted(component_failures.items())),
        "selected_source_provenance_counts": dict(_selected_source_type_counts(rows)),
    }
    for layer in SCORE_LAYER_NAMES:
        layer_summary = _layer_summary(rows, layer)
        for key, value in layer_summary.items():
            summary[f"{layer}_{key}"] = value
    summary.update(_adapter_deltas(rows))
    summary["validation25_smoke_outcome"] = _validation25_smoke_outcome(summary)
    return summary


def write_jsonl(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    write_jsonl_rows(rows, path)


def load_reusable_raw_outputs(path: Path) -> dict[int, str]:
    return load_raw_outputs_by_source_index(path)


def write_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    /,
    *,
    jsonl_path: Path,
) -> None:
    """Write a compact Markdown report for the hybrid validation25 smoke."""

    path.parent.mkdir(parents=True, exist_ok=True)
    summary = metadata.get("summary") or summarize_records(rows)
    lines = [
        "# Gan 2026 Hybrid Parallel State Candidate Reasoner",
        "",
        f"- JSONL: `{jsonl_path}`",
        f"- Pipeline family: `{PIPELINE_FAMILY}`",
        f"- Prompt version: `{metadata.get('prompt_version', PROMPT_VERSION)}`",
        f"- Split: `{metadata.get('split')}` / `{metadata.get('split_manifest')}`",
        f"- Rows: {summary.get('examples', 0)}",
        f"- Model: `{metadata.get('model')}`",
        f"- Mode: `{metadata.get('mode')}`",
        (
            "- Claim language: hybrid validation development result with deterministic "
            "candidate, state-graph, LLM-candidate, adjudicator, and adapter layers."
        ),
        f"- Smoke outcome: `{summary.get('validation25_smoke_outcome')}`",
        "",
        "## Smoke Summary",
        "",
        (
            f"- Structured LLM candidates: {summary.get('structured_llm_candidate_records', 0)}/"
            f"{summary.get('examples', 0)}"
        ),
        (
            f"- Structured adjudicator records: {summary.get('structured_adjudicator_records', 0)}/"
            f"{summary.get('examples', 0)}"
        ),
        f"- Parse/schema failures: {summary.get('parse_or_validation_failures', 0)}",
        (
            f"- Selected evidence exact: {summary.get('selected_evidence_exact', 0)}/"
            f"{summary.get('examples', 0)}"
        ),
        (
            f"- Selected source ids valid: {summary.get('selected_source_ids_exist', 0)}/"
            f"{summary.get('examples', 0)}"
        ),
        f"- candidate-recall rescue rows: {summary.get('candidate_recall_rescues', 0)}",
        (
            "- graph-representability rescue rows: "
            f"{summary.get('graph_representability_rescues', 0)}"
        ),
        (
            "- deterministic-correct regressions: "
            f"{summary.get('deterministic_correct_regressions', 0)}"
        ),
        f"- adapter-changed rows: {summary.get('adapter_changed_rows', 0)}",
        "",
        "## Score Layers",
        "",
    ]
    for layer in SCORE_LAYER_NAMES:
        lines.append(
            f"- `{layer}`: scorable {summary.get(f'{layer}_scorable', 0)}, "
            f"Purist {summary.get(f'{layer}_purist_correct', 0)}/{summary.get('examples', 0)} "
            f"({summary.get(f'{layer}_purist_accuracy', 0.0):.4f}), "
            f"Pragmatic {summary.get(f'{layer}_pragmatic_correct', 0)}/"
            f"{summary.get('examples', 0)} "
            f"({summary.get(f'{layer}_pragmatic_accuracy', 0.0):.4f})"
        )
    lines.extend(
        [
            "",
            "## Provenance",
            "",
            *[
                f"- `{source_type}`: {source_count}"
                for source_type, source_count in sorted(
                    (summary.get("selected_source_provenance_counts") or {}).items()
                )
            ],
            "",
            "## Row Review",
            "",
            *_row_review_lines(rows),
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def _deterministic_components(record: GanFrequencyRecord) -> dict[str, Any]:
    result = Gan2026PipelineV1().run(record)
    diagnostics = result.diagnostics
    return {
        "candidate_events": diagnostics["candidate_events"],
        "normalized_events": diagnostics["normalized_events"],
        "final_selection": diagnostics["final_selection"],
        "evidence_valid": diagnostics["evidence_valid"],
    }


def _graph_components(record: GanFrequencyRecord) -> dict[str, Any]:
    graph = build_state_graph(record.note_text, source_row_index=record.source_row_index)
    projection = project_graph_to_gan(graph)
    return {
        "graph": graph,
        "projection": projection.model_dump(mode="json"),
        "nodes": [_graph_node_row(node) for node in graph.nodes],
    }


def _component_inputs(
    record: GanFrequencyRecord,
    deterministic: Mapping[str, Any],
    graph: Mapping[str, Any],
    llm_packet: HybridLlmCandidatePacket | None,
) -> dict[str, Any]:
    return {
        "source_row_index": record.source_row_index,
        "note_text": record.note_text,
        "deterministic_top": deterministic["final_selection"],
        "deterministic_candidates": _deterministic_candidate_rows(deterministic),
        "state_graph_projection": graph["projection"],
        "state_graph_nodes": graph["nodes"],
        "llm_candidates": (
            [_llm_candidate_row(candidate) for candidate in llm_packet.candidates]
            if llm_packet
            else []
        ),
        "llm_candidate_selection": (
            llm_packet.selection.model_dump() if llm_packet else None
        ),
    }


def _llm_candidate_row(candidate: HybridLlmCandidate) -> dict[str, Any]:
    return {
        **candidate.model_dump(),
        "source_id": f"llm:{candidate.candidate_id}",
    }


def _deterministic_candidate_rows(deterministic: Mapping[str, Any]) -> list[dict[str, Any]]:
    normalized_by_id = {
        normalized["event_id"]: normalized for normalized in deterministic["normalized_events"]
    }
    rows = []
    for event in deterministic["candidate_events"]:
        normalized = normalized_by_id.get(event["event_id"], {})
        rows.append(
            {
                **event,
                "normalized_label": normalized.get("normalized_label"),
                "semantic_kind": normalized.get("semantic_kind"),
                "monthly_frequency": normalized.get("monthly_frequency"),
                "validation_errors": normalized.get("validation_errors", ()),
                "source_id": f"det:{event['event_id']}",
            }
        )
    return rows


def _graph_node_row(node: Any) -> dict[str, Any]:
    return {
        "node_id": node.node_id,
        "source_id": f"graph:{node.node_id}",
        "kind": node.kind.value,
        "normalized_label": node.normalized_label,
        "semantic_kind": node.semantic_kind.value,
        "monthly_frequency": node.monthly_frequency,
        "evidence": node.evidence.text,
        "assertion_status": node.assertion_status,
        "temporality": node.temporality,
        "certainty": node.certainty,
        "applies_to": node.applies_to,
        "rule_id": node.rule_id,
        "graph_errors": node.graph_errors,
    }


def _allowed_source_ids(component_inputs: Mapping[str, Any]) -> set[str]:
    source_ids = {
        row["source_id"] for row in component_inputs.get("deterministic_candidates") or []
    }
    source_ids.update(row["source_id"] for row in component_inputs.get("state_graph_nodes") or [])
    source_ids.update(
        row.get("source_id", f"llm:{row['candidate_id']}")
        for row in component_inputs.get("llm_candidates") or []
    )
    return source_ids


def _score_layers(
    record: GanFrequencyRecord,
    deterministic: Mapping[str, Any],
    graph: Mapping[str, Any],
    llm_packet: HybridLlmCandidatePacket | None,
    decision: HybridParallelAdjudicatorDecision | None,
) -> dict[str, dict[str, Any]]:
    deterministic_label = (deterministic["final_selection"] or {}).get("final_label")
    graph_label = (graph["projection"] or {}).get("final_label")
    llm_label = llm_packet.selection.final_label if llm_packet else None
    raw_adjudicator_label = decision.final_label if decision else None
    format_label = (
        repair_prediction_label_format_preserving(raw_adjudicator_label)
        if raw_adjudicator_label
        else None
    )
    adapted_label = (
        repair_prediction_label_with_evidence(format_label, decision.selected_evidence)
        if decision and format_label
        else None
    )
    return {
        "deterministic_top_candidate": _score_label(
            record,
            deterministic_label,
            repair_mode="deterministic_top_candidate",
        ),
        "state_graph_projection": _score_label(
            record,
            graph_label,
            repair_mode="state_graph_projection",
        ),
        "llm_candidate_selector_raw": _score_label(
            record,
            llm_label,
            repair_mode="llm_candidate_selector_raw",
        ),
        "hybrid_adjudicator_raw": _score_label(
            record,
            raw_adjudicator_label,
            repair_mode="hybrid_adjudicator_raw",
        ),
        "hybrid_adjudicator_with_adapters": _score_label(
            record,
            adapted_label,
            repair_mode="hybrid_adjudicator_with_adapters",
        ),
        "adapter_only_sidecar_from_adjudicator_selection": _score_label(
            record,
            adapted_label,
            repair_mode="adapter_only_sidecar_from_adjudicator_selection",
        ),
    }


def _analysis_layers(
    record: GanFrequencyRecord,
    deterministic: Mapping[str, Any],
    graph: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    return {
        "oracle_candidate_presence": {
            "present": _candidate_or_graph_has_gold(record, deterministic["normalized_events"]),
            "analysis_only": True,
        },
        "oracle_graph_representability": {
            "present": _candidate_or_graph_has_gold(record, graph["nodes"]),
            "analysis_only": True,
        },
    }


def _diagnostics(
    record: GanFrequencyRecord,
    component_inputs: Mapping[str, Any],
    llm_packet: HybridLlmCandidatePacket | None,
    decision: HybridParallelAdjudicatorDecision | None,
) -> dict[str, Any]:
    allowed_source_ids = _allowed_source_ids(component_inputs)
    selected_source_ids_exist = (
        decision is not None
        and all(
            source_id.startswith("synth:") or source_id in allowed_source_ids
            for source_id in [*decision.selected_source_ids, *decision.supporting_source_ids]
        )
    )
    selected_evidence_exact = (
        decision is not None and evidence_is_substring(record.note_text, decision.selected_evidence)
    )
    deterministic_correct = _layer_correct_from_label(
        record,
        (component_inputs["deterministic_top"] or {}).get("final_label"),
    )
    graph_correct = _layer_correct_from_label(
        record,
        (component_inputs["state_graph_projection"] or {}).get("final_label"),
    )
    adjudicator_correct = _layer_correct_from_label(
        record,
        decision.final_label if decision else None,
    )
    adapted_correct = _layer_correct_from_label(
        record,
        (
            repair_prediction_label_with_evidence(
                repair_prediction_label_format_preserving(decision.final_label),
                decision.selected_evidence,
            )
            if decision
            else None
        ),
    )
    llm_candidate_correct = _layer_correct_from_label(
        record,
        llm_packet.selection.final_label if llm_packet else None,
    )
    candidate_present = _candidate_or_graph_has_gold(
        record,
        component_inputs.get("deterministic_candidates") or [],
    )
    graph_present = _candidate_or_graph_has_gold(
        record,
        component_inputs.get("state_graph_nodes") or [],
    )
    return {
        "selected_source_ids_exist": selected_source_ids_exist,
        "selected_evidence_exact": selected_evidence_exact,
        "selected_source_provenance_counts": dict(
            Counter(decision.selected_source_types if decision else [])
        ),
        "llm_candidate_correct": llm_candidate_correct,
        "deterministic_correct": deterministic_correct,
        "graph_projection_correct": graph_correct,
        "adjudicator_raw_correct": adjudicator_correct,
        "adjudicator_adapted_correct": adapted_correct,
        "candidate_recall_rescue": (
            (not deterministic_correct)
            and adapted_correct
            and (llm_candidate_correct or graph_present)
        ),
        "graph_representability_rescue": (
            graph_present and not graph_correct and adapted_correct
        ),
        "deterministic_correct_regression": deterministic_correct and not adapted_correct,
        "graph_projection_regression": graph_correct and not adapted_correct,
        "oracle_candidate_presence": candidate_present,
        "oracle_graph_representability": graph_present,
    }


def _component_status(
    *,
    deterministic: Mapping[str, Any],
    graph: Mapping[str, Any],
    llm_packet: HybridLlmCandidatePacket | None,
    decision: HybridParallelAdjudicatorDecision | None,
    llm_candidate_parse_errors: Sequence[str],
    adjudicator_parse_errors: Sequence[str],
    diagnostics: Mapping[str, Any],
    llm_candidate_call_error: str | None,
    adjudicator_call_error: str | None,
) -> dict[str, str]:
    status = {
        "deterministic_top": "ok",
        "state_graph_projection": "ok",
        "llm_candidate_selector": "ok",
        "hybrid_adjudicator": "ok",
        "adapter_layer": "ok",
        "source_id_trace": "ok",
        "selected_evidence_exactness": "ok",
    }
    if not deterministic.get("final_selection"):
        status["deterministic_top"] = "fail"
    if not graph.get("projection"):
        status["state_graph_projection"] = "fail"
    if llm_candidate_call_error or _blocking_errors(llm_candidate_parse_errors) or not llm_packet:
        status["llm_candidate_selector"] = "fail"
    if adjudicator_call_error or _blocking_errors(adjudicator_parse_errors) or not decision:
        status["hybrid_adjudicator"] = "fail"
        status["adapter_layer"] = "fail"
    if not diagnostics.get("selected_source_ids_exist"):
        status["source_id_trace"] = "fail"
    if not diagnostics.get("selected_evidence_exact"):
        status["selected_evidence_exactness"] = "fail"
    return status


def _score_label(
    record: GanFrequencyRecord,
    label: str | None,
    *,
    repair_mode: str,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "final_label": label,
        "scorable": False,
        "repair_mode_metadata": repair_mode_layers((repair_mode,))[repair_mode],
    }
    if not label:
        result["error"] = "missing_final_label"
        return result
    try:
        predicted_record = label_to_frequency_record(label)
    except ValueError as exc:
        result["error"] = str(exc)
        return result
    gold_purist = str(map_purist(record.gold_monthly_frequency))
    predicted_purist = str(map_purist(predicted_record.monthly_frequency))
    gold_pragmatic = str(map_pragmatic(record.gold_monthly_frequency))
    predicted_pragmatic = str(map_pragmatic(predicted_record.monthly_frequency))
    result.update(
        {
            "scorable": True,
            "predicted_monthly_frequency": predicted_record.monthly_frequency,
            "gold_monthly_frequency": record.gold_monthly_frequency,
            "predicted_purist_category": predicted_purist,
            "gold_purist_category": gold_purist,
            "purist_correct": predicted_purist == gold_purist,
            "predicted_pragmatic_category": predicted_pragmatic,
            "gold_pragmatic_category": gold_pragmatic,
            "pragmatic_correct": predicted_pragmatic == gold_pragmatic,
        }
    )
    return result


def _layer_correct_from_label(record: GanFrequencyRecord, label: str | None) -> bool:
    return bool(_score_label(record, label, repair_mode="diagnostic").get("purist_correct"))


def _candidate_or_graph_has_gold(
    record: GanFrequencyRecord,
    rows: Sequence[Mapping[str, Any]],
) -> bool:
    gold_kind = record.gold_label_kind
    gold_freq = record.gold_monthly_frequency
    for row in rows:
        label = row.get("normalized_label") or row.get("final_label")
        if not label:
            continue
        try:
            parsed = label_to_frequency_record(str(label))
        except ValueError:
            continue
        if parsed.kind is gold_kind and parsed.monthly_frequency == gold_freq:
            return True
    return False


def _repair_changes(score_layers: Mapping[str, Mapping[str, Any]]) -> list[dict[str, str]]:
    changes: list[dict[str, str]] = []
    raw_label = score_layers["hybrid_adjudicator_raw"].get("final_label")
    for layer in (
        "hybrid_adjudicator_with_adapters",
        "adapter_only_sidecar_from_adjudicator_selection",
    ):
        current = score_layers[layer].get("final_label")
        if isinstance(raw_label, str) and isinstance(current, str) and current != raw_label:
            changes.append({"layer": layer, "before": raw_label, "after": current})
    return changes


def _layer_summary(rows: Sequence[Mapping[str, Any]], layer: str) -> dict[str, Any]:
    count = len(rows)
    layer_rows = [(row.get("score_layers") or {}).get(layer) or {} for row in rows]
    scorable = sum(bool(row.get("scorable")) for row in layer_rows)
    purist = sum(bool(row.get("purist_correct")) for row in layer_rows)
    pragmatic = sum(bool(row.get("pragmatic_correct")) for row in layer_rows)
    return {
        "scorable": scorable,
        "purist_correct": purist,
        "purist_accuracy": round(purist / count, 4) if count else 0.0,
        "pragmatic_correct": pragmatic,
        "pragmatic_accuracy": round(pragmatic / count, 4) if count else 0.0,
    }


def _adapter_deltas(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    raw_wrong_to_correct = 0
    raw_correct_to_wrong = 0
    for row in rows:
        layers = row.get("score_layers") or {}
        raw = layers.get("hybrid_adjudicator_raw") or {}
        adapted = layers.get("hybrid_adjudicator_with_adapters") or {}
        raw_correct = bool(raw.get("purist_correct"))
        adapted_correct = bool(adapted.get("purist_correct"))
        if not raw_correct and adapted_correct:
            raw_wrong_to_correct += 1
        if raw_correct and not adapted_correct:
            raw_correct_to_wrong += 1
    return {
        "adapter_raw_wrong_to_correct": raw_wrong_to_correct,
        "adapter_raw_correct_to_wrong": raw_correct_to_wrong,
    }


def _selected_source_type_counts(rows: Sequence[Mapping[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in rows:
        counts.update((row.get("diagnostics") or {}).get("selected_source_provenance_counts") or {})
    return counts


def _validation25_smoke_outcome(summary: Mapping[str, Any]) -> str:
    examples = int(summary.get("examples", 0))
    if examples == 0:
        return "reject"
    blocking = any(
        (
            int(summary.get("call_failures", 0)) > 0,
            int(summary.get("structured_adjudicator_records", 0)) < examples - 1,
            int(summary.get("selected_evidence_exact", 0)) < min(23, examples),
            int(summary.get("selected_source_ids_exist", 0)) < examples,
            int(summary.get("deterministic_correct_regressions", 0)) > 1,
        )
    )
    if blocking:
        return "reject"
    if (
        int(summary.get("candidate_recall_rescues", 0)) > 0
        or int(summary.get("graph_representability_rescues", 0)) > 0
    ):
        return "promote_to_50"
    return "revise"


def _row_review_lines(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    lines = []
    for row in rows:
        diagnostics = row.get("diagnostics") or {}
        if (
            not diagnostics.get("candidate_recall_rescue")
            and not diagnostics.get("graph_representability_rescue")
            and not diagnostics.get("deterministic_correct_regression")
        ):
            continue
        layers = row.get("score_layers") or {}
        det = layers.get("deterministic_top_candidate") or {}
        adapted = layers.get("hybrid_adjudicator_with_adapters") or {}
        lines.append(
            "- "
            f"{row.get('source_row_index')}: "
            f"gold `{((row.get('reference') or {}).get('gold_normalized_label'))}`; "
            f"deterministic `{det.get('final_label')}`; "
            f"adapted `{adapted.get('final_label')}`; "
            f"candidate-recall rescue `{diagnostics.get('candidate_recall_rescue')}`; "
            f"graph rescue `{diagnostics.get('graph_representability_rescue')}`; "
            f"deterministic regression `{diagnostics.get('deterministic_correct_regression')}`"
        )
    if not lines:
        return ["- No rescue or regression rows on this surface."]
    return lines


def _repair_llm_candidate_payload(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload
    repaired = dict(payload)
    candidates = repaired.get("candidates")
    if isinstance(candidates, list):
        repaired["candidates"] = [_repair_candidate_payload(candidate) for candidate in candidates]
    selection = repaired.get("selection")
    if isinstance(selection, dict):
        repaired["selection"] = _repair_candidate_selection_payload(selection)
    return repaired


def _repair_candidate_payload(candidate: Any) -> Any:
    if not isinstance(candidate, dict):
        return candidate
    repaired = repair_decision_payload(dict(candidate))
    if "candidate_id" not in repaired and "event_id" in repaired:
        repaired["candidate_id"] = repaired["event_id"]
    if "raw_value" not in repaired and "raw_phrase" in repaired:
        repaired["raw_value"] = repaired["raw_phrase"]
    if repaired.get("assertion_status") == "historical":
        repaired["assertion_status"] = "asserted"
    repaired.setdefault("raw_value", repaired.get("evidence", ""))
    repaired.setdefault("confidence", "medium")
    repaired.setdefault("rationale", "")
    return {key: value for key, value in repaired.items() if key in HybridLlmCandidate.model_fields}


def _repair_candidate_selection_payload(selection: Any) -> Any:
    repaired = dict(selection)
    repaired = repair_decision_payload(repaired)
    if "selected_candidate_ids" not in repaired and "selected_event_ids" in repaired:
        repaired["selected_candidate_ids"] = repaired["selected_event_ids"]
    if "selected_evidence" not in repaired and "evidence" in repaired:
        repaired["selected_evidence"] = repaired["evidence"]
    if "final_kind" not in repaired:
        repaired["final_kind"] = "unknown"
    repaired.setdefault("rationale", "")
    return {
        key: value
        for key, value in repaired.items()
        if key in HybridLlmCandidateSelection.model_fields
    }


def _repair_adjudicator_payload(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload
    repaired = repair_decision_payload(dict(payload))
    if "selected_source_ids" not in repaired and "selected_event_ids" in repaired:
        repaired["selected_source_ids"] = repaired["selected_event_ids"]
    if "selected_source_types" not in repaired:
        repaired["selected_source_types"] = [
            _source_type_from_id(source_id) for source_id in repaired.get("selected_source_ids", [])
        ]
    if "selected_evidence" not in repaired and "evidence" in repaired:
        repaired["selected_evidence"] = repaired["evidence"]
    if "final_kind" not in repaired:
        repaired["final_kind"] = "unknown"
    repaired.setdefault("confidence", repaired.get("uncertainty", "medium"))
    if repaired.get("confidence") == "low confidence":
        repaired["confidence"] = "low"
    if repaired.get("confidence") not in {"high", "medium", "low"}:
        repaired["confidence"] = "medium"
    repaired.setdefault("rationale", "")
    repaired.setdefault("supporting_source_ids", [])
    return {
        key: value
        for key, value in repaired.items()
        if key in HybridParallelAdjudicatorDecision.model_fields
    }


def _repair_llm_candidate_evidence_copy(
    packet: HybridLlmCandidatePacket,
    note_text: str,
) -> HybridLlmCandidatePacket:
    candidate_updates = []
    for candidate in packet.candidates:
        candidate_updates.append(
            candidate.model_copy(
                update={
                    "evidence": _repair_case_only_evidence_copy(candidate.evidence, note_text)
                }
            )
        )
    selection = packet.selection.model_copy(
        update={
            "selected_evidence": _repair_case_only_evidence_copy(
                packet.selection.selected_evidence,
                note_text,
            )
        }
    )
    return packet.model_copy(
        update={
            "candidates": candidate_updates,
            "selection": selection,
        }
    )


def _repair_case_only_evidence_copy(evidence: str, note_text: str) -> str:
    if evidence_is_substring(note_text, evidence):
        return evidence
    start = note_text.lower().find(evidence.lower())
    if start < 0:
        return evidence
    return note_text[start : start + len(evidence)]


def _source_type_from_id(source_id: str) -> str:
    if str(source_id).startswith("det:"):
        return "deterministic_candidate"
    if str(source_id).startswith("graph:"):
        return "state_graph_node"
    if str(source_id).startswith("llm:"):
        return "llm_candidate"
    return "adjudicator_synthesis"


def _canonicalize_decision_source_ids(
    decision: HybridParallelAdjudicatorDecision,
    allowed_source_ids: set[str],
) -> tuple[HybridParallelAdjudicatorDecision, list[str]]:
    selected_ids, selected_repairs = _canonicalize_source_id_list(
        decision.selected_source_ids,
        allowed_source_ids,
    )
    supporting_ids, supporting_repairs = _canonicalize_source_id_list(
        decision.supporting_source_ids,
        allowed_source_ids,
    )
    if not selected_repairs and not supporting_repairs:
        return decision, []
    return (
        decision.model_copy(
            update={
                "selected_source_ids": selected_ids,
                "supporting_source_ids": supporting_ids,
            }
        ),
        [*selected_repairs, *supporting_repairs],
    )


def _canonicalize_source_id_list(
    source_ids: Sequence[str],
    allowed_source_ids: set[str],
) -> tuple[list[str], list[str]]:
    canonical_ids: list[str] = []
    repairs: list[str] = []
    for source_id in source_ids:
        canonical = _canonicalize_source_id(str(source_id), allowed_source_ids)
        canonical_ids.append(canonical)
        if canonical != source_id:
            repairs.append(f"selected_source_ids_repaired: {source_id!r} -> {canonical!r}")
    return canonical_ids, repairs


def _canonicalize_source_id(source_id: str, allowed_source_ids: set[str]) -> str:
    if source_id in allowed_source_ids or source_id.startswith("synth:") or ":" in source_id:
        return source_id
    matches = [
        candidate
        for candidate in (f"det:{source_id}", f"graph:{source_id}", f"llm:{source_id}")
        if candidate in allowed_source_ids
    ]
    if len(matches) == 1:
        return matches[0]
    return source_id


def _has_blocking_parse_issue(row: Mapping[str, Any]) -> bool:
    return _blocking_errors(row.get("llm_candidate_parse_errors")) or _blocking_errors(
        row.get("adjudicator_parse_errors")
    )


def _blocking_errors(errors: Any) -> bool:
    return any(
        str(error).startswith(("invalid_json:", "schema_validation_error:", "not_run"))
        for error in errors or []
    )


def _extract_json_object(raw_output: str) -> str:
    text = raw_output.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if fenced:
        return fenced.group(1)
    first = text.find("{")
    last = text.rfind("}")
    if first != -1 and last != -1 and last > first:
        return text[first : last + 1]
    return text


def _run_metadata(
    records: Sequence[GanFrequencyRecord],
    *,
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: str,
    api_base: str | None,
) -> dict[str, Any]:
    return build_run_metadata(
        mode=mode,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        prompt_version=PROMPT_VERSION,
        dspy_version=getattr(dspy, "__version__", "unknown"),
        split=split,
        split_manifest=split_manifest,
        api_base=api_base,
        row_count=len(records),
        extra={
            "pipeline_name": PROMPT_VERSION,
            "pipeline_family": PIPELINE_FAMILY,
            "prompt_version": PROMPT_VERSION,
            "score_layers": [*SCORE_LAYER_NAMES, *ANALYSIS_LAYER_NAMES],
            "validation_smoke_stop_rule": {
                "call_success_minimum": "25/25",
                "structured_outputs_minimum": "24/25",
                "selected_evidence_exact_minimum": "23/25",
                "unknown_source_ids_maximum": "0 rows",
                "deterministic_correct_regressions_maximum": "1 row",
                "rescue_requirement": ">=1 candidate-recall or graph-representability rescue",
            },
        },
    )


def _emit_progress_checkpoint(
    rows: Sequence[Mapping[str, Any]],
    metadata: dict[str, Any],
    *,
    total: int,
    jsonl_path: Path | None,
    report_path: Path | None,
) -> None:
    metadata["summary"] = summarize_records(rows)
    if jsonl_path is not None:
        write_jsonl(rows, jsonl_path)
    if report_path is not None and jsonl_path is not None:
        write_report(rows, metadata, report_path, jsonl_path=jsonl_path)
    progress = {
        "processed": len(rows),
        "total": total,
        "call_failures": metadata["summary"]["call_failures"],
        "parse_or_validation_failures": metadata["summary"]["parse_or_validation_failures"],
        "hybrid_adjudicator_scorable": metadata["summary"][
            "hybrid_adjudicator_raw_scorable"
        ],
    }
    print(json.dumps(progress, sort_keys=True), file=sys.stderr, flush=True)
