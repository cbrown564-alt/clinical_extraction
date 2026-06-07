"""LLM-only canonical-pipeline Gan 2026 seizure-frequency extraction experiments.

This is the "purest form" fully-LLM comparator named in the three-way
architecture comparison plan: a single-shot configuration that collapses
extract -> select -> normalize -> project -> render into one LLM call, with
the now-mature deterministic rule taxonomy (cluster-axis ambiguity,
seizure-free conflict, same-window additive frequency, and similar named
families) embedded as prompt instructions rather than pre/post processing.
It sits alongside, not in place of, `llm_only_direct_labeler` and
`llm_only_structured_events`.

Because this architecture produces one free-text decision rather than a
`CandidateSet` with source ids, it reports a distinct evidence
text-containment metric (does the LLM's free-text evidence string appear in
the source note) rather than the formal `CandidateSet` source-id validity
rate the deterministic/hybrid configurations support.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict, ValidationError

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
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_metadata import (
    build_run_metadata,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    repair_prediction_label_with_evidence,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.reports.base import (
    llm_model_metadata_lines,
    write_markdown_report,
)

PROMPT_VERSION = "gan2026_llm_only_canonical_pipeline_v0.1"
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_llm_only_canonical_pipeline_validation_gpt41mini_2026-06-07.jsonl"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_llm_only_canonical_pipeline_validation_gpt41mini_2026-06-07.md"
)


class CanonicalLlmDecisionRecord(BaseModel):
    """Single-shot note-to-label decision for the canonical fully-LLM pipeline."""

    model_config = ConfigDict(extra="forbid")

    final_label: str
    evidence: str
    answer_kind: Literal[
        "frequency",
        "seizure_free",
        "unknown",
        "no_reference",
        "unresolved_multiple",
    ]
    selected_seizure_type: str
    time_window: str
    applied_rule_families: list[str]
    confidence: Literal["low", "medium", "high"]
    rationale: str


class Gan2026CanonicalLlmExtractorSignature(dspy.Signature):
    """Read a clinical note and decide the patient's current seizure frequency.

    Provide a complete answer that adheres to the instructions below. 
    Return exactly one JSON object with these keys: final_label,
    evidence, answer_kind, selected_seizure_type, time_window,
    applied_rule_families, confidence, and rationale.
    """

    prompt_input_json: str = dspy.InputField(
        desc=(
            "JSON containing one clinical note, guidance on how to reason "
            "about tricky cases, and the fields your answer must contain."
        )
    )
    decision_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object. final_label must already be your "
            "complete, final answer in plain form, such as '2 per month', "
            "'2 to 3 per week', 'multiple per day', '1 cluster per week', "
            "'2 to 3 per cluster', 'seizure free for 6 month', 'unknown', or "
            "'no seizure frequency reference'."
        )
    )


class DspyCanonicalLlmExtractor(dspy.Module):
    """DSPy single-shot extractor that owns the full extract-to-render chain."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(Gan2026CanonicalLlmExtractorSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


# Named clinical-reasoning rule families from the deterministic/hybrid rule
# taxonomy (see CONTEXT.md), embedded as prompt instructions rather than
# pre/post processing — the defining trait of this "purest form" comparator.
_RULE_TAXONOMY_INSTRUCTIONS: list[str] = [
    (
        "cluster_axis_ambiguity: when a cluster statement could describe "
        "cluster cadence, events-per-cluster, cluster duration, or plain "
        "seizure frequency, and the intended axis is not clear from the note, "
        "do not guess a specific cluster rate; prefer unknown."
    ),
    (
        "seizure_free_conflict: do not select seizure-free when active-event "
        "evidence, scoped event types, breakthrough events, or other current "
        "seizure-burden facts remain unresolved; a concrete current frequency "
        "takes precedence over a seizure-free claim it conflicts with."
    ),
    (
        "same_window_additive_frequency: you may sum multiple concrete "
        "frequency-rate facts only when they explicitly share the same time "
        "window and compatible event scope; mixed-window, vague-plus-concrete, "
        "or event-scope-uncertain combinations must not be added together."
    ),
    (
        "denominator_window_mismatch: keep the stated count and the stated "
        "time-window denominator paired exactly as the source describes them; "
        "do not silently convert a multi-period count into a different "
        "denominator (for example, do not turn '6 over 3 months' into "
        "'2 per month' unless the note itself states the monthly rate)."
    ),
    (
        "medication_cadence_ambiguity: cadence language describing medication "
        "use, rescue dosing, or another non-event schedule is not seizure "
        "frequency; do not convert medication or treatment cadence into a "
        "seizure rate without reliable seizure-event evidence."
    ),
    (
        "cluster_cadence_as_event_rate: a clear current cluster cadence may "
        "be rendered as a simple seizure-frequency rate only when no "
        "events-per-cluster burden is stated; do not apply this when the "
        "cluster axis is ambiguous, the cadence describes medication, or "
        "per-cluster evidence conflicts."
    ),
    (
        "unknown_cadence_cluster_burden: when events-per-cluster burden is "
        "known but cluster recurrence cadence is not stated, prefer an "
        "explicit cluster-burden-with-unknown-cadence label (for example "
        "'2 to 3 per cluster') rather than inventing a cadence."
    ),
    (
        "concrete_frequency_precedence: a renderable concrete frequency-rate "
        "fact can override a contextual cluster framing when the cluster "
        "framing is incidental rather than itself the current clinical "
        "burden being described; it must not override an already-renderable "
        "cluster-burden operand or medication-use cadence."
    ),
    (
        "dominant_vague_current_burden: a vague but clearly current "
        "high-frequency burden (for example, events on most weekdays) may be "
        "selected over a lower-frequency contextual burden when both are "
        "derivable and the vague burden mechanically dominates; this is a "
        "selection preference, not additive arithmetic."
    ),
    (
        "seizure_free_proxy_evidence_overreach: do not render a seizure-free "
        "duration from proxy-improvement evidence such as no rescue "
        "medication, no injury, no admission, better control, or conditional "
        "future breakthrough-event planning; only explicit no-seizure or "
        "no-event assertions support a seizure-free label."
    ),
    (
        "conditional_only_trigger and relative_only_trend: events described "
        "only as conditional on a trigger (for example, only with missed "
        "medication) or only as a relative trend (for example, less frequent "
        "than before) without a countable current rate should usually "
        "resolve to unknown rather than an invented countable rate."
    ),
    (
        "multiple_current_primary_facts: when several distinct current "
        "seizure-burden facts compete and the rules above do not resolve "
        "which one is dominant, prefer unresolved_multiple or unknown over "
        "guessing a single rate."
    ),
]


def build_prompt_input(record: GanFrequencyRecord) -> str:
    """Build the LLM-only canonical-pipeline prompt payload, excluding gold labels."""

    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": "Determine a patient's current seizure frequency from one clinical note",
        "source_row_index": record.source_row_index,
        "instructions": [
            (
                "Read the full clinical note and decide what the "
                "patient's current seizure frequency is."
            ),
            (
                "Return final_label as one normalized string using count, "
                "range, or multiple over a day/week/month/year denominator; "
                "seizure-free duration; unknown; or no seizure frequency "
                "reference."
            ),
            (
                "Allowed frequency forms include 1 per day, 2 to 3 per month, "
                "multiple per week, 1 cluster per week, 2 to 3 per cluster, "
                "seizure free for 6 month, unknown, no seizure frequency "
                "reference."
            ),
            (
                "If multiple seizure events occur over the same period "
                "combine them into a single rate using the same time window (for example, "
                "2 tonic-clonic seizures and 3 focal seizures in the last month should"
                "combine into '5 per month')."
            ),
            (
                "If multiple unrelated seizure events are present, select the "
                "highest current seizure burden across unless "
                "the note gives an overall current count, in which case "
                "prefer the overall count."
            ),
            (
                "Plural daily seizures/events should map to multiple per day "
                "unless the note clearly states exactly one per day."
            ),
            (
                "Use unknown when seizures or seizure-like events are "
                "discussed but the current frequency cannot be converted to a "
                "normalized rate."
            ),
            (
                "Use no seizure frequency reference only when the note "
                "contains no usable seizure-frequency evidence."
            ),
            "Evidence must be an exact substring from the note when possible.",
            (
                "Each guidance note below starts with a short label. In "
                "applied_rule_families, list the labels (if any) that "
                "actually shaped how you read this particular note. Leave it "
                "empty if none did."
            ),
            "Return exactly one JSON object with no markdown.",
        ],
        "guidance_for_tricky_cases": {
            "how_to_use_this": (
                "Clinical notes describe seizure frequency in many different "
                "ways, and some are easy to misread. The notes below each "
                "name a situation that commonly trips people up and say what "
                "to do about it. Check whether any apply to this note before "
                "you settle on your final answer"
            ),
            "notes": _RULE_TAXONOMY_INSTRUCTIONS,
        },
        "allowed_decision_fields": [
            "final_label",
            "evidence",
            "answer_kind",
            "selected_seizure_type",
            "time_window",
            "applied_rule_families",
            "confidence",
            "rationale",
        ],
        "note_text": record.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def parse_decision_json(
    raw_output: str,
) -> tuple[CanonicalLlmDecisionRecord | None, list[str]]:
    errors: list[str] = []
    try:
        payload = _filter_decision_payload(
            repair_decision_payload(json.loads(_extract_json_object(raw_output)))
        )
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json: {exc.msg}"]

    payload = _coerce_applied_rule_families(payload)

    try:
        decision = CanonicalLlmDecisionRecord.model_validate(payload)
    except ValidationError as exc:
        return None, [f"schema_validation_error: {exc.errors()[0]['msg']}"]

    repaired_label = repair_prediction_label_with_evidence(
        decision.final_label,
        decision.evidence,
    )
    if repaired_label != decision.final_label:
        errors.append(f"final_label_repaired: {decision.final_label!r} -> {repaired_label!r}")
        decision = decision.model_copy(update={"final_label": repaired_label})

    try:
        label_to_frequency_record(decision.final_label)
    except ValueError as exc:
        errors.append(f"unscorable_final_label: {exc}")

    return decision, errors


def _coerce_applied_rule_families(payload: Any) -> Any:
    """Tolerate a missing or scalar `applied_rule_families` field from the model."""

    if not isinstance(payload, dict):
        return payload
    repaired = dict(payload)
    families = repaired.get("applied_rule_families")
    if families is None:
        repaired["applied_rule_families"] = []
    elif isinstance(families, str):
        repaired["applied_rule_families"] = [families] if families else []
    return repaired


def _filter_decision_payload(payload: Any) -> Any:
    """Keep shared adjudicator repair fields out of canonical-pipeline validation."""

    if not isinstance(payload, dict):
        return payload
    allowed = set(CanonicalLlmDecisionRecord.model_fields)
    return {key: value for key, value in payload.items() if key in allowed}


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
    reuse_raw_outputs: Mapping[int, str] | None = None,
    reuse_source: str | None = None,
    escalation_reason: str | None = None,
    progress_every: int | None = None,
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    reuse_raw_outputs = reuse_raw_outputs or {}
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
    program = DspyCanonicalLlmExtractor()
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
        prompt_input_json = build_prompt_input(record)
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
        evidence_text_contained = (
            evidence_is_substring(record.note_text, decision.evidence)
            if decision and decision.evidence
            else False
        )
        comparison = _compare_to_gold(record, decision) if decision else None
        rows.append(
            {
                "source_row_index": record.source_row_index,
                "split": split,
                "split_manifest": split_manifest,
                "prompt_version": PROMPT_VERSION,
                "prompt_input_json": prompt_input_json,
                "raw_output": raw_output,
                "reused_raw_output": reused_raw_output,
                "call_error": call_error,
                "parse_errors": parse_errors,
                "decision_record": decision.model_dump() if decision else None,
                "evidence_text_contained": evidence_text_contained,
                "reference": {
                    "gold_label": record.gold_label,
                    "gold_monthly_frequency": record.gold_monthly_frequency,
                    "row_ok": record.row_ok,
                },
                "comparison": comparison,
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
        "purist_accuracy_so_far": metadata["summary"]["purist_accuracy"],
        "pragmatic_accuracy_so_far": metadata["summary"]["pragmatic_accuracy"],
        "reused_raw_outputs": metadata["summary"]["reused_raw_outputs"],
    }
    print(json.dumps(progress, sort_keys=True), file=sys.stderr, flush=True)


def summarize_records(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    decision_rows = [row for row in rows if row.get("decision_record")]
    call_failures = sum(bool(row.get("call_error")) for row in rows)
    reused_raw_outputs = sum(bool(row.get("reused_raw_output")) for row in rows)
    parse_failures = sum(_has_blocking_parse_issue(row.get("parse_errors")) for row in rows)
    repair_notes = sum(_has_repair_note(row.get("parse_errors")) for row in rows)
    purist_correct = sum(bool((row.get("comparison") or {}).get("purist_correct")) for row in rows)
    pragmatic_correct = sum(
        bool((row.get("comparison") or {}).get("pragmatic_correct")) for row in rows
    )
    evidence_text_contained = sum(bool(row.get("evidence_text_contained")) for row in rows)
    applied_rule_families = Counter(
        family
        for row in rows
        for family in (row.get("decision_record") or {}).get("applied_rule_families") or []
    )
    final_labels = Counter(
        row["decision_record"]["final_label"] for row in rows if row.get("decision_record")
    )
    return {
        "examples": len(rows),
        "decision_records": len(decision_rows),
        "call_failures": call_failures,
        "reused_raw_outputs": reused_raw_outputs,
        "parse_or_validation_failures": parse_failures,
        "repair_notes": repair_notes,
        "evidence_text_contained": evidence_text_contained,
        "evidence_text_containment_rate": (
            round(evidence_text_contained / len(rows), 4) if rows else 0.0
        ),
        "purist_correct": purist_correct,
        "purist_accuracy": round(purist_correct / len(rows), 4) if rows else 0.0,
        "pragmatic_correct": pragmatic_correct,
        "pragmatic_accuracy": round(pragmatic_correct / len(rows), 4) if rows else 0.0,
        "final_labels": dict(sorted(final_labels.items())),
        "applied_rule_family_counts": dict(sorted(applied_rule_families.items())),
    }


def write_jsonl(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    write_jsonl_rows(rows, path)


def load_reusable_raw_outputs(path: Path) -> dict[int, str]:
    """Load reusable raw model outputs from a prior JSONL artifact."""

    return load_raw_outputs_by_source_index(path)


def write_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    summary = metadata["summary"]
    lines = [
        "# Gan 2026 LLM-Only Canonical-Pipeline Validation Run",
        "",
        f"Date: {metadata['date']}",
        "",
        "This is a validation development result on `gan2026_split_v1`. It is not a "
        "final holdout or benchmark result.",
        "",
        "## Experiment Unit",
        "",
        "Hypothesis: the 'purest form' fully-LLM comparator — a single DSPy call that "
        "collapses extract/select/normalize/project/render into one pass, with the "
        "now-mature deterministic/hybrid clinical-reasoning rule taxonomy embedded as "
        "prompt instructions rather than pre/post processing — can produce a directly "
        "scorable, fully rendered label without any deterministic normalization or "
        "projection stage downstream.",
        "",
        "Minimal change: add an `llm_only_canonical_pipeline` runner alongside (not "
        "replacing) `llm_only_direct_labeler` and `llm_only_structured_events`. No "
        "deterministic `CandidateSet` is built or consumed; final_label is the model's "
        "directly rendered answer.",
        "",
        f"Data surface: `{metadata['split']}` split, `{metadata['split_manifest']}`, "
        f"{summary['examples']} rows.",
        (
            f"Rare full-validation reason: {metadata['escalation_reason']}"
            if metadata.get("escalation_reason")
            else "Rare full-validation reason: not applicable for this run size."
        ),
        "Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as "
        "a side-car.",
        "",
        "## Model And Prompt Metadata",
        "",
        *llm_model_metadata_lines(
            metadata,
            jsonl_path,
            model_role=(
                "LLM-only canonical-pipeline single-shot extract/select/normalize/"
                "project/render extractor"
            ),
            deterministic_rule_configuration=(
                "none as pre/post processing; the deterministic/hybrid rule taxonomy "
                "is embedded as prompt instructions only, and deterministic code is "
                "limited to label repair, evidence text-containment checking, and "
                "scoring."
            ),
            summary=summary,
        ),
        "",
        "## Summary",
        "",
        f"- Decision records: {summary['decision_records']} / {summary['examples']}",
        f"- Call failures: {summary['call_failures']}",
        f"- Parse/schema/label issues: {summary['parse_or_validation_failures']}",
        f"- Deterministic repair notes: {summary['repair_notes']}",
        (
            "- Evidence text-containment (free-text evidence found verbatim in note, "
            f"the comparator-appropriate metric in place of `CandidateSet` source-id "
            f"validity rate): {summary['evidence_text_contained']} / {summary['examples']} "
            f"({summary['evidence_text_containment_rate']:.4f})"
        ),
        f"- Purist validation accuracy/micro F1 proxy: {summary['purist_accuracy']:.4f} "
        f"({summary['purist_correct']} / {summary['examples']})",
        f"- Pragmatic validation accuracy/micro F1 proxy: {summary['pragmatic_accuracy']:.4f} "
        f"({summary['pragmatic_correct']} / {summary['examples']})",
        "",
        "## Applied Rule-Taxonomy Families (Self-Reported)",
        "",
        "These counts reflect which embedded rule-taxonomy families the model itself "
        "reported as shaping its answer (`applied_rule_families`); they are a prompt-"
        "compliance signal, not a verified trace.",
        "",
    ]
    if summary["applied_rule_family_counts"]:
        for family, count in summary["applied_rule_family_counts"].items():
            lines.append(f"- `{family}`: {count}")
    else:
        lines.append("- (none reported)")
    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| Row | Final | Gold | Purist | Notes |",
            "| ---: | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        decision = row.get("decision_record") or {}
        comparison = row.get("comparison") or {}
        notes = "; ".join(row.get("parse_errors") or [])
        if row.get("call_error"):
            notes = f"{notes}; {row['call_error']}" if notes else str(row["call_error"])
        if not row.get("evidence_text_contained"):
            note = "evidence_not_text_contained"
            notes = f"{notes}; {note}" if notes else note
        lines.append(
            f"| {row['source_row_index']} | {decision.get('final_label', '')} | "
            f"{row['reference']['gold_label']} | "
            f"{'yes' if comparison.get('purist_correct') else 'no'} | {notes} |"
        )
    write_markdown_report(path, lines)


def _compare_to_gold(
    record: GanFrequencyRecord,
    decision: CanonicalLlmDecisionRecord,
) -> dict[str, Any]:
    try:
        predicted_record = label_to_frequency_record(decision.final_label)
    except ValueError:
        return {}
    gold_purist = str(map_purist(record.gold_monthly_frequency))
    predicted_purist = str(map_purist(predicted_record.monthly_frequency))
    gold_pragmatic = str(map_pragmatic(record.gold_monthly_frequency))
    predicted_pragmatic = str(map_pragmatic(predicted_record.monthly_frequency))
    return {
        "predicted_monthly_frequency": predicted_record.monthly_frequency,
        "gold_monthly_frequency": record.gold_monthly_frequency,
        "predicted_purist_category": predicted_purist,
        "gold_purist_category": gold_purist,
        "purist_correct": predicted_purist == gold_purist,
        "predicted_pragmatic_category": predicted_pragmatic,
        "gold_pragmatic_category": gold_pragmatic,
        "pragmatic_correct": predicted_pragmatic == gold_pragmatic,
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
    records: Sequence[GanFrequencyRecord],
    *,
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: str,
    api_base: str | None = None,
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
    )
