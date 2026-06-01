"""DSPy modules and run harnesses for Gan 2026 seizure-frequency experiments."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    label_to_frequency_record,
    repair_prediction_label,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.pipeline_v1 import Gan2026PipelineV1
from clinical_extraction.tasks.seizure_frequency.gan2026.schema_repair import (
    repair_decision_payload,
)

PROMPT_VERSION = "gan2026_final_selection_adjudicator_v0.4"
DEFAULT_DEVSET_PATH = Path(
    "experiments/gan2026_v1_prompt_adjudicator_devset_2026-05-31.jsonl"
)
DEFAULT_ADJUDICATOR_JSONL_PATH = Path(
    "experiments/gan2026_v1_dspy_adjudicator_devset_gpt41mini_2026-05-31.jsonl"
)
DEFAULT_ADJUDICATOR_REPORT_PATH = Path(
    "experiments/gan2026_v1_dspy_adjudicator_devset_gpt41mini_2026-05-31.md"
)
DEFAULT_ARCH2_JSONL_PATH = Path(
    "experiments/gan2026_arch2_validation25_gpt41mini_v01_2026-06-01.jsonl"
)
DEFAULT_ARCH2_REPORT_PATH = Path(
    "experiments/gan2026_arch2_validation25_gpt41mini_v01_2026-06-01.md"
)


class SeizureEventExtractor:
    """Extract all seizure-frequency events from a clinical note."""

    def __call__(self, note_text: str) -> list[dict[str, str]]:
        raise NotImplementedError


class ClinicalReasoner:
    """Select or aggregate extracted events into one benchmark-facing answer."""

    def __call__(self, note_text: str, events: list[dict[str, str]]) -> dict[str, str]:
        raise NotImplementedError


class AdjudicatorDecisionRecord(BaseModel):
    """Traceable final-selection decision emitted by the DSPy adjudicator."""

    model_config = ConfigDict(extra="forbid")

    assertion_status: Literal[
        "asserted",
        "negated",
        "historical",
        "hypothetical",
        "unclear",
        "mixed",
    ]
    temporality: Literal["current", "recent", "historical", "future", "unclear", "mixed"]
    seizure_or_event_target: str
    window: str
    normalized_rate: str
    uncertainty: Literal["low", "medium", "high"]
    accepted_event_ids: list[str] = Field(default_factory=list)
    rejected_event_ids: list[str] = Field(default_factory=list)
    selected_event_ids: list[str] = Field(default_factory=list)
    final_label: str
    rationale: str


class Gan2026FinalSelectionAdjudicatorSignature(dspy.Signature):
    """Adjudicate deterministic candidate diagnostics into one Gan-compatible final label.

    Return exactly one JSON object with these keys: assertion_status, temporality,
    seizure_or_event_target, window, normalized_rate, uncertainty, accepted_event_ids,
    rejected_event_ids, selected_event_ids, final_label, and rationale.
    """

    prompt_input_json: str = dspy.InputField(
        desc=(
            "JSON containing note_text, candidate_events, normalized_events, "
            "deterministic_final_selection, and the development question. It intentionally "
            "omits the gold label."
        )
    )
    decision_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object. final_label must be a Gan-compatible label copied from a "
            "candidate normalized_label, or unknown/no seizure frequency reference when evidence "
            "does not support a current seizure-frequency answer."
        )
    )


class DspyFinalSelectionAdjudicator(dspy.Module):
    """DSPy final-selection adjudicator over deterministic V1 diagnostics."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(Gan2026FinalSelectionAdjudicatorSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def load_devset(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def build_prompt_input(example: Mapping[str, Any]) -> str:
    """Build the exact adjudicator input, excluding gold/reference fields."""

    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": "Gan 2026 seizure-frequency final-selection adjudication",
        "instructions": [
            "Review the full note first, then audit every candidate diagnostic against it.",
            (
                "A candidate is acceptable only if its evidence is a real seizure-frequency "
                "statement in the note, not a heading, section label, medication instruction, "
                "problem-list phrase, questionnaire field, or isolated words split across lines."
            ),
            (
                "Reject generic event phrases such as brief events or daily events unless the "
                "note context clearly says they are the patient's epileptic seizures in the "
                "current assessment window."
            ),
            (
                "If the note says plural seizures/events occur daily or several/multiple times "
                "per day, use a Gan-compatible multiple-rate label such as multiple per day "
                "rather than forcing the candidate's 1 per day label."
            ),
            (
                "Reject candidates created from line-break joins or headings such as daily "
                "Seizure when the note's real frequency sentence supports another candidate."
            ),
            (
                "When multiple seizure types are current, choose the highest current burden "
                "across types. Do not reject an unresolved-multiple label merely because a "
                "lower numeric label is more specific."
            ),
            (
                "Use unknown, not seizure-free, when events still occur under triggers, "
                "provocation, poor sleep, or visual stimuli, or when seizure freedom applies "
                "only to one semiology while other seizure-like events remain."
            ),
            (
                "Treat a single recent breakthrough after a seizure-free interval as the "
                "current benchmark rate when a broader cyclic or trigger pattern is only "
                "suspected, anticipatory, or not clearly counted as seizures."
            ),
            (
                "Use only these assertion_status values: asserted, negated, historical, "
                "hypothetical, unclear, mixed."
            ),
            "Use only these uncertainty values: low, medium, high.",
            "Write normalized_rate as text, not a number.",
            (
                "Prefer current or recent asserted seizure-frequency evidence over historical, "
                "negated, future, hypothetical, or non-seizure evidence."
            ),
            (
                "Do not choose a higher numeric rate merely because it is higher; first decide "
                "whether it is the current seizure-frequency target."
            ),
            (
                "When explicit current frequency evidence and seizure-free/no-event assertions "
                "conflict, reject no-red-flags/no-status/no-generalised-convulsion statements "
                "as seizure-free only if they do not deny all seizure types."
            ),
            (
                "Populate accepted_event_ids and rejected_event_ids after reviewing each "
                "candidate. selected_event_ids must be a subset of accepted_event_ids."
            ),
            (
                "If the candidates do not support a current seizure-frequency answer, return "
                "unknown or no seizure frequency reference."
            ),
            (
                "Use selected_event_ids from candidate_events. Use an empty list only when "
                "selecting unknown/no-reference without a supporting event."
            ),
            "Return exactly one JSON object with no markdown.",
        ],
        "allowed_decision_fields": [
            "assertion_status",
            "temporality",
            "seizure_or_event_target",
            "window",
            "normalized_rate",
            "uncertainty",
            "accepted_event_ids",
            "rejected_event_ids",
            "selected_event_ids",
            "final_label",
            "rationale",
        ],
        "example_id": example["example_id"],
        "source_row_index": example["source_row_index"],
        "development_question": example["adjudicator_target"]["development_question"],
        "note_text": example["input"].get("note_text", ""),
        "candidate_events": example["input"]["candidate_events"],
        "normalized_events": example["input"]["normalized_events"],
        "deterministic_final_selection": example["input"]["deterministic_final_selection"],
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def build_architecture2_prompt_input(
    record: Any,
    diagnostics: Mapping[str, Any],
) -> str:
    """Build a split-wide Architecture 2 prompt without gold labels or V1 scores."""

    candidate_events = _architecture2_candidate_events(diagnostics)
    deterministic_final = diagnostics.get("final_selection") or {}
    payload = {
        "prompt_version": PROMPT_VERSION,
        "architecture": "gan2026_architecture_2_deterministic_candidates_llm_adjudicator",
        "claim_type": "hybrid_llm_adjudicator",
        "task": "Gan 2026 seizure-frequency candidate adjudication",
        "source_row_index": record.source_row_index,
        "instructions": [
            "Read the full note first, then adjudicate the deterministic candidate set.",
            (
                "The deterministic generator is a high-recall retrieval layer, not the final "
                "answer. Do not rubber-stamp candidate order."
            ),
            (
                "Candidates are listed in stable event-id order, without deterministic scores. "
                "Choose a candidate only if its evidence supports the current/recent Gan "
                "seizure-frequency answer."
            ),
            (
                "Reject headings, medication instructions, rescue-medication frequency, "
                "caregiver concern, falls, collapses, non-epileptic-like events, and proxy "
                "statements unless the note explicitly ties them to definite epileptic seizure "
                "burden."
            ),
            (
                "Prefer current or recent asserted seizure-frequency evidence over historical, "
                "negated, future, hypothetical, or unsupported evidence."
            ),
            (
                "If several active seizure semiologies have current frequencies, select the "
                "highest current burden unless the note gives an overall count."
            ),
            (
                "Use unknown when seizures are discussed but the current frequency cannot be "
                "converted from the candidate evidence."
            ),
            (
                "Use no seizure frequency reference only when the note contains no usable "
                "seizure-frequency evidence."
            ),
            (
                "Use final_label copied from one candidate normalized_label whenever a "
                "candidate supports the answer. Use unknown or no seizure frequency reference "
                "only when no candidate supports a current frequency answer."
            ),
            (
                "Populate accepted_event_ids and rejected_event_ids after reviewing each "
                "candidate. selected_event_ids must be a subset of accepted_event_ids unless "
                "you select unknown/no-reference without a supporting event."
            ),
            "Return exactly one JSON object with no markdown.",
        ],
        "allowed_decision_fields": [
            "assertion_status",
            "temporality",
            "seizure_or_event_target",
            "window",
            "normalized_rate",
            "uncertainty",
            "accepted_event_ids",
            "rejected_event_ids",
            "selected_event_ids",
            "final_label",
            "rationale",
        ],
        "note_text": record.note_text,
        "candidate_events": candidate_events,
        "deterministic_top_candidate": {
            "final_label": deterministic_final.get("final_label"),
            "selected_event_ids": deterministic_final.get("selected_event_ids", []),
            "evidence": deterministic_final.get("evidence"),
        },
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def parse_decision_json(raw_output: str) -> tuple[AdjudicatorDecisionRecord | None, list[str]]:
    errors: list[str] = []
    try:
        payload = repair_decision_payload(json.loads(_extract_json_object(raw_output)))
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json: {exc.msg}"]

    try:
        decision = AdjudicatorDecisionRecord.model_validate(payload)
    except ValidationError as exc:
        return None, [f"schema_validation_error: {exc.errors()[0]['msg']}"]

    repaired_label = repair_prediction_label(decision.final_label)
    if repaired_label != decision.final_label:
        errors.append(
            f"final_label_repaired: {decision.final_label!r} -> {repaired_label!r}"
        )
        decision = decision.model_copy(update={"final_label": repaired_label})

    try:
        label_to_frequency_record(decision.final_label)
    except ValueError as exc:
        errors.append(f"unscorable_final_label: {exc}")

    return decision, errors


def run_adjudicator_devset(
    examples: Sequence[Mapping[str, Any]],
    *,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    metadata = _run_metadata(
        examples,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        mode=mode,
    )
    program = DspyFinalSelectionAdjudicator()
    if mode == "live":
        dspy.configure(
            lm=dspy.LM(
                model,
                temperature=temperature,
                max_tokens=max_tokens,
                cache=False,
                num_retries=2,
            )
        )

    records: list[dict[str, Any]] = []
    for example in examples:
        prompt_input_json = build_prompt_input(example)
        raw_output = ""
        call_error: str | None = None
        if mode == "live":
            try:
                prediction = program(prompt_input_json=prompt_input_json)
                raw_output = str(prediction.decision_json)
            except Exception as exc:  # pragma: no cover - exercised only with live APIs.
                call_error = f"{type(exc).__name__}: {exc}"

        decision, parse_errors = (
            parse_decision_json(raw_output) if raw_output else (None, ["not_run"])
        )
        comparison = _compare_to_reference(example, decision) if decision else None
        records.append(
            {
                "example_id": example["example_id"],
                "source_row_index": example["source_row_index"],
                "split": example["split"],
                "split_manifest": example["split_manifest"],
                "lesson_type": example["lesson_type"],
                "ablation_condition": example["ablation_condition"],
                "prompt_version": PROMPT_VERSION,
                "prompt_input_json": prompt_input_json,
                "raw_output": raw_output,
                "call_error": call_error,
                "parse_errors": parse_errors,
                "decision_record": decision.model_dump() if decision else None,
                "reference": {
                    "gold_label": example["reference"]["gold_label"],
                    "gold_category": example["reference"]["gold_category"],
                    "baseline_prediction_label": example["reference"][
                        "baseline_prediction_label"
                    ],
                    "baseline_prediction_category": example["reference"][
                        "baseline_prediction_category"
                    ],
                },
                "comparison": comparison,
            }
        )

    metadata["summary"] = summarize_adjudicator_records(records)
    return records, metadata


def run_architecture2_split(
    records: Sequence[Any],
    *,
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
    reuse_raw_outputs: Mapping[int, str] | None = None,
    reuse_source: str | None = None,
    escalation_reason: str | None = None,
    progress_every: int | None = None,
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run Architecture 2 over ordinary Gan split records."""

    reuse_raw_outputs = reuse_raw_outputs or {}
    metadata = _run_metadata(
        [{"split": split, "split_manifest": split_manifest} for _ in records],
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        mode=mode,
    )
    metadata["architecture"] = "architecture_2_deterministic_candidates_llm_adjudicator"
    metadata["claim_type"] = "hybrid_llm_adjudicator"
    metadata["reuse_source"] = reuse_source
    metadata["escalation_reason"] = escalation_reason
    pipeline = Gan2026PipelineV1()
    program = DspyFinalSelectionAdjudicator()
    if mode == "live":
        dspy.configure(
            lm=dspy.LM(
                model,
                temperature=temperature,
                max_tokens=max_tokens,
                cache=True,
                num_retries=2,
            )
        )

    output_rows: list[dict[str, Any]] = []
    for record in records:
        deterministic_result = pipeline.run(record)
        diagnostics = deterministic_result.diagnostics
        prompt_input_json = build_architecture2_prompt_input(record, diagnostics)
        raw_output = reuse_raw_outputs.get(record.source_row_index, "")
        call_error: str | None = None
        reused_raw_output = raw_output != ""
        if mode == "live" and not reused_raw_output:
            try:
                prediction = program(prompt_input_json=prompt_input_json)
                raw_output = str(prediction.decision_json)
            except Exception as exc:  # pragma: no cover - exercised only with live APIs.
                call_error = f"{type(exc).__name__}: {exc}"

        decision, parse_errors = (
            parse_decision_json(raw_output) if raw_output else (None, ["not_run"])
        )
        deterministic_score = _compare_label_to_record(
            record,
            str(diagnostics["final_selection"]["final_label"]),
        )
        adjudicator_score = (
            _compare_label_to_record(record, decision.final_label) if decision else None
        )
        candidate_recall = _candidate_recall(record, diagnostics)
        output_rows.append(
            {
                "source_row_index": record.source_row_index,
                "split": split,
                "split_manifest": split_manifest,
                "architecture": metadata["architecture"],
                "claim_type": metadata["claim_type"],
                "prompt_version": PROMPT_VERSION,
                "prompt_input_json": prompt_input_json,
                "raw_output": raw_output,
                "reused_raw_output": reused_raw_output,
                "call_error": call_error,
                "parse_errors": parse_errors,
                "decision_record": decision.model_dump() if decision else None,
                "deterministic_diagnostics": {
                    "candidate_events": diagnostics.get("candidate_events", []),
                    "normalized_events": diagnostics.get("normalized_events", []),
                    "final_selection": diagnostics.get("final_selection"),
                    "evidence_valid": diagnostics.get("evidence_valid"),
                },
                "candidate_recall": candidate_recall,
                "scores": {
                    "deterministic_top": deterministic_score,
                    "adjudicator": adjudicator_score,
                },
                "reference": {
                    "gold_label": record.gold_label,
                    "gold_label_kind": str(record.gold_label_kind),
                    "gold_monthly_frequency": record.gold_monthly_frequency,
                    "row_ok": record.row_ok,
                },
            }
        )
        if progress_every and len(output_rows) % progress_every == 0:
            _emit_arch2_checkpoint(
                output_rows,
                metadata,
                total=len(records),
                jsonl_path=checkpoint_jsonl_path,
                report_path=checkpoint_report_path,
            )

    metadata["summary"] = summarize_architecture2_records(output_rows)
    return output_rows, metadata


def summarize_architecture2_records(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    count = len(records)
    decisions = [record for record in records if record.get("decision_record")]
    parse_failures = sum(
        _has_blocking_parse_issue(record.get("parse_errors")) for record in records
    )
    call_failures = sum(bool(record.get("call_error")) for record in records)
    candidate_purist_recall = sum(
        bool((record.get("candidate_recall") or {}).get("purist_category_recalled"))
        for record in records
    )
    deterministic_purist = sum(
        bool(((record.get("scores") or {}).get("deterministic_top") or {}).get("purist_correct"))
        for record in records
    )
    deterministic_pragmatic = sum(
        bool(((record.get("scores") or {}).get("deterministic_top") or {}).get("pragmatic_correct"))
        for record in records
    )
    adjudicator_purist = sum(
        bool(((record.get("scores") or {}).get("adjudicator") or {}).get("purist_correct"))
        for record in records
    )
    adjudicator_pragmatic = sum(
        bool(((record.get("scores") or {}).get("adjudicator") or {}).get("pragmatic_correct"))
        for record in records
    )
    changed = sum(_arch2_changed_final_label(record) for record in records)
    improved = sum(
        _arch2_changed_correctness(record, from_correct=False, to_correct=True)
        for record in records
    )
    regressed = sum(
        _arch2_changed_correctness(record, from_correct=True, to_correct=False)
        for record in records
    )
    return {
        "examples": count,
        "decision_records": len(decisions),
        "call_failures": call_failures,
        "parse_or_validation_failures": parse_failures,
        "reused_raw_outputs": sum(bool(record.get("reused_raw_output")) for record in records),
        "candidate_purist_recall": candidate_purist_recall,
        "candidate_purist_recall_rate": round(candidate_purist_recall / count, 4) if count else 0.0,
        "deterministic_purist_correct": deterministic_purist,
        "deterministic_purist_accuracy": round(deterministic_purist / count, 4) if count else 0.0,
        "deterministic_pragmatic_correct": deterministic_pragmatic,
        "deterministic_pragmatic_accuracy": (
            round(deterministic_pragmatic / count, 4) if count else 0.0
        ),
        "adjudicator_purist_correct": adjudicator_purist,
        "adjudicator_purist_accuracy": round(adjudicator_purist / count, 4) if count else 0.0,
        "adjudicator_pragmatic_correct": adjudicator_pragmatic,
        "adjudicator_pragmatic_accuracy": round(adjudicator_pragmatic / count, 4) if count else 0.0,
        "changed_final_labels": changed,
        "deterministic_wrong_to_adjudicator_correct": improved,
        "deterministic_correct_to_adjudicator_wrong": regressed,
    }


def summarize_adjudicator_records(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    live_records = [record for record in records if record.get("decision_record")]
    parse_failures = sum(
        _has_blocking_parse_issue(record.get("parse_errors")) for record in records
    )
    repair_notes = sum(_has_repair_note(record.get("parse_errors")) for record in records)
    call_failures = sum(bool(record.get("call_error")) for record in records)
    purist_correct = sum(
        bool((record.get("comparison") or {}).get("purist_correct")) for record in records
    )
    pragmatic_correct = sum(
        bool((record.get("comparison") or {}).get("pragmatic_correct")) for record in records
    )
    final_labels = Counter(
        record["decision_record"]["final_label"]
        for record in records
        if record.get("decision_record")
    )
    return {
        "examples": len(records),
        "decision_records": len(live_records),
        "call_failures": call_failures,
        "parse_or_validation_failures": parse_failures,
        "repair_notes": repair_notes,
        "purist_correct": purist_correct,
        "purist_accuracy": round(purist_correct / len(records), 4) if records else 0.0,
        "pragmatic_correct": pragmatic_correct,
        "pragmatic_accuracy": round(pragmatic_correct / len(records), 4) if records else 0.0,
        "final_labels": dict(sorted(final_labels.items())),
    }


def write_adjudicator_jsonl(records: Sequence[Mapping[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def write_architecture2_jsonl(records: Sequence[Mapping[str, Any]], path: Path) -> None:
    write_adjudicator_jsonl(records, path)


def load_architecture2_raw_outputs(path: Path) -> dict[int, str]:
    reusable: dict[int, str] = {}
    if not path.exists():
        return reusable
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        source_row_index = row.get("source_row_index")
        raw_output = row.get("raw_output")
        if isinstance(source_row_index, int) and isinstance(raw_output, str) and raw_output:
            reusable[source_row_index] = raw_output
    return reusable


def write_architecture2_report(
    records: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    summary = metadata["summary"]
    lines = [
        "# Gan 2026 Architecture 2 Candidate Adjudicator",
        "",
        f"Date: {metadata['date']}",
        "",
        "This is a validation development artifact unless the split is explicitly `test` "
        "and the candidate was frozen before evaluation. It is not a benchmark claim.",
        "",
        "## Experiment Unit",
        "",
        "Hypothesis: deterministic V1 can serve as a high-recall candidate generator, "
        "while an LLM adjudicator makes the prediction-bearing semantic selection.",
        "",
        "Prediction-bearing component: LLM final-selection adjudicator over unscored "
        "deterministic candidate evidence. Deterministic code generates candidate labels, "
        "validates output shape, applies existing label repair, and scores.",
        "",
        f"Data surface: `{metadata['split']}` split, `{metadata['split_manifest']}`, "
        f"{summary['examples']} rows.",
        (
            f"Escalation reason: {metadata['escalation_reason']}"
            if metadata.get("escalation_reason")
            else "Escalation reason: not applicable for this run size."
        ),
        "",
        "## Model And Prompt Metadata",
        "",
        f"- Architecture: `{metadata['architecture']}`",
        f"- Claim type: `{metadata['claim_type']}`",
        f"- DSPy version: `{metadata['dspy_version']}`",
        f"- Runtime model display/API identifier: `{metadata['model']}`",
        "- Provider/execution: hosted OpenAI via DSPy/LiteLLM",
        "- Model role: final-selection adjudicator",
        f"- Prompt/program version: `{metadata['prompt_version']}`",
        f"- Temperature: `{metadata['temperature']}`",
        f"- Max tokens: `{metadata['max_tokens']}`",
        f"- Mode: `{metadata['mode']}`",
        f"- Reused raw model outputs: `{summary['reused_raw_outputs']}`",
        f"- Reuse source: `{metadata.get('reuse_source') or 'none'}`",
        "- Deterministic rule configuration: frozen V1 candidate generator before LLM "
        "adjudication.",
        f"- Git commit: `{metadata['git_commit']}`",
        f"- Working tree note: `{metadata['working_tree_note']}`",
        f"- JSONL artifact: `{jsonl_path}`",
        "",
        "## Summary",
        "",
        f"- Decision records: {summary['decision_records']} / {summary['examples']}",
        f"- Call failures: {summary['call_failures']}",
        f"- Parse/schema/label issues: {summary['parse_or_validation_failures']}",
        f"- Candidate-set Purist recall proxy: {summary['candidate_purist_recall_rate']:.4f} "
        f"({summary['candidate_purist_recall']} / {summary['examples']})",
        f"- Deterministic top Purist: {summary['deterministic_purist_accuracy']:.4f} "
        f"({summary['deterministic_purist_correct']} / {summary['examples']})",
        f"- Deterministic top Pragmatic: {summary['deterministic_pragmatic_accuracy']:.4f} "
        f"({summary['deterministic_pragmatic_correct']} / {summary['examples']})",
        f"- Adjudicator Purist: {summary['adjudicator_purist_accuracy']:.4f} "
        f"({summary['adjudicator_purist_correct']} / {summary['examples']})",
        f"- Adjudicator Pragmatic: {summary['adjudicator_pragmatic_accuracy']:.4f} "
        f"({summary['adjudicator_pragmatic_correct']} / {summary['examples']})",
        f"- Changed final labels: {summary['changed_final_labels']}",
        "- Deterministic-wrong to adjudicator-correct: "
        f"{summary['deterministic_wrong_to_adjudicator_correct']}",
        "- Deterministic-correct to adjudicator-wrong: "
        f"{summary['deterministic_correct_to_adjudicator_wrong']}",
        "",
        "## Rows",
        "",
        "| Row | Candidate recall | Deterministic | Adjudicator | Gold | "
        "Det Purist | Adj Purist | Notes |",
        "| ---: | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for record in records:
        deterministic = ((record.get("scores") or {}).get("deterministic_top") or {})
        adjudicator = ((record.get("scores") or {}).get("adjudicator") or {})
        recall = (record.get("candidate_recall") or {}).get("purist_category_recalled")
        notes = "; ".join(str(error) for error in record.get("parse_errors") or [])
        if record.get("call_error"):
            notes = f"{notes}; {record['call_error']}" if notes else str(record["call_error"])
        lines.append(
            f"| {record['source_row_index']} | {_yes_no(recall)} | "
            f"{deterministic.get('final_label', '')} | "
            f"{adjudicator.get('final_label', '') if adjudicator else ''} | "
            f"{record['reference']['gold_label']} | "
            f"{_yes_no(deterministic.get('purist_correct'))} | "
            f"{_yes_no(adjudicator.get('purist_correct')) if adjudicator else ''} | "
            f"{notes} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_adjudicator_report(
    records: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
    devset_path: Path,
) -> None:
    summary = metadata["summary"]
    lines = [
        "# Gan 2026 DSPy Final-Selection Adjudicator Dev-Set Run",
        "",
        f"Date: {metadata['date']}",
        "",
        "This is a validation-only prompt/adjudicator development run over the 16-example "
        "dev set mined from validation ablations. It is not a benchmark result and does "
        "not inspect locked test-row failures.",
        "",
        "## Experiment Unit",
        "",
        "Hypothesis: a DSPy final-selection adjudicator can use deterministic V1 candidate "
        "diagnostics to reject unsupported high-priority candidates while preserving "
        "necessary deterministic evidence.",
        "",
        "Minimal change: add the adjudicator program and run harness only. Deterministic "
        "candidate extraction, normalization, scoring, split policy, and repair rules are "
        "unchanged.",
        "",
        f"Data surface: `{metadata['split']}` split, `{metadata['split_manifest']}`, "
        f"{summary['examples']} examples from `{devset_path}`.",
        "Scorer policy: compare final labels to carried gold labels with Gan-compatible "
        "Purist categories first, Pragmatic categories as a side-car.",
        "",
        "## Model And Prompt Metadata",
        "",
        f"- DSPy version: `{metadata['dspy_version']}`",
        f"- Runtime model display/API identifier: `{metadata['model']}`",
        "- Provider/execution: hosted OpenAI via DSPy/LiteLLM",
        "- Model role: final-selection adjudicator",
        f"- Prompt/program version: `{metadata['prompt_version']}`",
        f"- Temperature: `{metadata['temperature']}`",
        f"- Max tokens: `{metadata['max_tokens']}`",
        f"- Mode: `{metadata['mode']}`",
        "- Optimizer: none",
        "- Deterministic rule configuration: frozen V1 diagnostics from the dev-set JSONL",
        f"- Git commit: `{metadata['git_commit']}`",
        f"- Working tree note: `{metadata['working_tree_note']}`",
        f"- JSONL artifact: `{jsonl_path}`",
        "",
        "## Summary",
        "",
        f"- Decision records: {summary['decision_records']} / {summary['examples']}",
        f"- Call failures: {summary['call_failures']}",
        f"- Parse/schema/label issues: {summary['parse_or_validation_failures']}",
        f"- Deterministic repair notes: {summary['repair_notes']}",
        f"- Purist dev-set accuracy: {summary['purist_accuracy']:.4f} "
        f"({summary['purist_correct']} / {summary['examples']})",
        f"- Pragmatic dev-set accuracy: {summary['pragmatic_accuracy']:.4f} "
        f"({summary['pragmatic_correct']} / {summary['examples']})",
        "",
        "## Rows",
        "",
        "| Row | Lesson | Condition | Final | Gold | Purist | Notes |",
        "| ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for record in records:
        decision = record.get("decision_record") or {}
        comparison = record.get("comparison") or {}
        notes = "; ".join(record.get("parse_errors") or [])
        if record.get("call_error"):
            notes = f"{notes}; {record['call_error']}" if notes else str(record["call_error"])
        lines.append(
            f"| {record['source_row_index']} | {record['lesson_type']} | "
            f"{record['ablation_condition']} | {decision.get('final_label', '')} | "
            f"{record['reference']['gold_label']} | "
            f"{'yes' if comparison.get('purist_correct') else 'no'} | {notes} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            _interpret_run(summary),
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _compare_to_reference(
    example: Mapping[str, Any],
    decision: AdjudicatorDecisionRecord,
) -> dict[str, Any]:
    gold_record = label_to_frequency_record(example["reference"]["gold_label"])
    predicted_record = label_to_frequency_record(decision.final_label)
    gold_purist = str(map_purist(gold_record.monthly_frequency))
    predicted_purist = str(map_purist(predicted_record.monthly_frequency))
    gold_pragmatic = str(map_pragmatic(gold_record.monthly_frequency))
    predicted_pragmatic = str(map_pragmatic(predicted_record.monthly_frequency))
    return {
        "predicted_monthly_frequency": predicted_record.monthly_frequency,
        "gold_monthly_frequency": gold_record.monthly_frequency,
        "predicted_purist_category": predicted_purist,
        "gold_purist_category": gold_purist,
        "purist_correct": predicted_purist == gold_purist,
        "predicted_pragmatic_category": predicted_pragmatic,
        "gold_pragmatic_category": gold_pragmatic,
        "pragmatic_correct": predicted_pragmatic == gold_pragmatic,
    }


def _architecture2_candidate_events(diagnostics: Mapping[str, Any]) -> list[dict[str, Any]]:
    normalized_by_id = {
        event.get("event_id"): event for event in diagnostics.get("normalized_events", [])
    }
    events: list[dict[str, Any]] = []
    for event in sorted(
        diagnostics.get("candidate_events", []),
        key=lambda item: str(item.get("event_id", "")),
    ):
        normalized = normalized_by_id.get(event.get("event_id"), {})
        events.append(
            {
                "event_id": event.get("event_id"),
                "kind": event.get("kind"),
                "raw_value": event.get("raw_value"),
                "evidence": event.get("evidence"),
                "rule_id": event.get("rule_id"),
                "rule_group": event.get("rule_group"),
                "portability": event.get("portability"),
                "normalized_label": normalized.get("normalized_label"),
                "semantic_kind": normalized.get("semantic_kind"),
                "validation_errors": normalized.get("validation_errors", []),
            }
        )
    return events


def _compare_label_to_record(record: Any, label: str) -> dict[str, Any]:
    result: dict[str, Any] = {"final_label": label, "scorable": False}
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


def _candidate_recall(record: Any, diagnostics: Mapping[str, Any]) -> dict[str, Any]:
    gold_purist = str(map_purist(record.gold_monthly_frequency))
    recalled_labels: list[str] = []
    for event in diagnostics.get("normalized_events", []):
        label = event.get("normalized_label")
        if not isinstance(label, str):
            continue
        try:
            candidate_record = label_to_frequency_record(label)
        except ValueError:
            continue
        if str(map_purist(candidate_record.monthly_frequency)) == gold_purist:
            recalled_labels.append(label)
    return {
        "gold_purist_category": gold_purist,
        "purist_category_recalled": bool(recalled_labels),
        "recalled_labels": recalled_labels,
        "candidate_count": len(diagnostics.get("normalized_events", [])),
    }


def _arch2_changed_final_label(record: Mapping[str, Any]) -> bool:
    scores = record.get("scores") or {}
    deterministic = scores.get("deterministic_top") or {}
    adjudicator = scores.get("adjudicator") or {}
    return bool(adjudicator) and deterministic.get("final_label") != adjudicator.get("final_label")


def _arch2_changed_correctness(
    record: Mapping[str, Any],
    *,
    from_correct: bool,
    to_correct: bool,
) -> bool:
    scores = record.get("scores") or {}
    deterministic = scores.get("deterministic_top") or {}
    adjudicator = scores.get("adjudicator") or {}
    return (
        bool(adjudicator)
        and deterministic.get("purist_correct") is from_correct
        and adjudicator.get("purist_correct") is to_correct
    )


def _emit_arch2_checkpoint(
    records: Sequence[Mapping[str, Any]],
    metadata: dict[str, Any],
    *,
    total: int,
    jsonl_path: Path | None,
    report_path: Path | None,
) -> None:
    metadata["summary"] = summarize_architecture2_records(records)
    if jsonl_path is not None:
        write_architecture2_jsonl(records, jsonl_path)
    if report_path is not None and jsonl_path is not None:
        write_architecture2_report(records, metadata, report_path, jsonl_path=jsonl_path)
    progress = {
        "processed": len(records),
        "total": total,
        "adjudicator_purist_accuracy_so_far": metadata["summary"][
            "adjudicator_purist_accuracy"
        ],
        "candidate_purist_recall_rate_so_far": metadata["summary"][
            "candidate_purist_recall_rate"
        ],
        "reused_raw_outputs": metadata["summary"]["reused_raw_outputs"],
    }
    print(json.dumps(progress, sort_keys=True), file=sys.stderr, flush=True)


def _yes_no(value: Any) -> str:
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return ""


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


def _has_repair_note(errors: Any) -> bool:
    return any(str(error).startswith("final_label_repaired:") for error in errors or [])


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
    examples: Sequence[Mapping[str, Any]],
    *,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: str,
) -> dict[str, Any]:
    split = sorted({str(example["split"]) for example in examples})
    split_manifest = sorted({str(example["split_manifest"]) for example in examples})
    return {
        "date": datetime.now(UTC).date().isoformat(),
        "created_at_utc": datetime.now(UTC).isoformat(),
        "mode": mode,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "prompt_version": PROMPT_VERSION,
        "dspy_version": getattr(dspy, "__version__", "unknown"),
        "split": ", ".join(split),
        "split_manifest": ", ".join(split_manifest),
        "git_commit": _git_output(["git", "rev-parse", "--short", "HEAD"]),
        "working_tree_note": _working_tree_note(),
        "python": sys.version.split()[0],
    }


def _working_tree_note() -> str:
    status = _git_output(["git", "status", "--short"])
    return "clean" if status == "" else "dirty/uncommitted local changes"


def _git_output(args: Sequence[str]) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _interpret_run(summary: Mapping[str, Any]) -> str:
    if summary["decision_records"] == 0:
        return (
            "The run exported prompt inputs but did not execute live model calls. Use the JSONL "
            "artifact to inspect prompt payloads before running a live comparison."
        )
    if summary["parse_or_validation_failures"]:
        return (
            "The first priority is output robustness: repair the prompt/schema contract before "
            "drawing quality conclusions from the dev-set labels."
        )
    if summary["purist_accuracy"] < 0.5:
        return (
            "The first live adjudicator is diagnostic rather than promotable; inspect row-level "
            "rationales before any broader validation pass."
        )
    return (
        "The dev-set behavior is interpretable enough to inspect row-level successes and "
        "failures before deciding whether to revise the prompt or run a broader validation pass."
    )


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Run the Gan 2026 DSPy final-selection adjudicator dev-set experiment."
    )
    parser.add_argument("--devset", type=Path, default=DEFAULT_DEVSET_PATH)
    parser.add_argument("--jsonl", type=Path, default=DEFAULT_ADJUDICATOR_JSONL_PATH)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_ADJUDICATOR_REPORT_PATH)
    parser.add_argument("--model", default="openai/gpt-4.1-mini")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=900)
    parser.add_argument("--mode", choices=("live", "prompt-only"), default="live")
    args = parser.parse_args(argv)

    examples = load_devset(args.devset)
    records, metadata = run_adjudicator_devset(
        examples,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        mode=args.mode,
    )
    write_adjudicator_jsonl(records, args.jsonl)
    write_adjudicator_report(
        records,
        metadata,
        args.markdown,
        jsonl_path=args.jsonl,
        devset_path=args.devset,
    )
    print(json.dumps(metadata["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
