"""DSPy modules and run harnesses for Gan 2026 seizure-frequency experiments."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_raw_outputs_by_source_index,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_metadata import (
    build_run_metadata,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.hybrid.hybrid_adjudicator_parser import (
    AdjudicatorDecisionRecord,
    parse_decision_json,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm
from clinical_extraction.tasks.seizure_frequency.gan2026.pipeline_v1 import Gan2026PipelineV1
from clinical_extraction.tasks.seizure_frequency.gan2026.reports.hybrid_adjudicator_report import (
    write_adjudicator_report,
    write_hybrid_rules_candidates_llm_adjudicator_report,
)

PROMPT_VERSION = "gan2026_final_selection_adjudicator_v0.5_conservative"
DEFAULT_DEVSET_PATH = Path("experiments/gan2026_v1_prompt_adjudicator_devset_2026-05-31.jsonl")
DEFAULT_ADJUDICATOR_JSONL_PATH = Path(
    "experiments/gan2026_v1_dspy_adjudicator_devset_gpt41mini_2026-05-31.jsonl"
)
DEFAULT_ADJUDICATOR_REPORT_PATH = Path(
    "experiments/gan2026_v1_dspy_adjudicator_devset_gpt41mini_2026-05-31.md"
)
DEFAULT_HYBRID_RULES_CANDIDATES_LLM_ADJUDICATOR_JSONL_PATH = Path(
    "experiments/"
    "gan2026_hybrid_rules_candidates_llm_adjudicator_validation25_gpt41mini_v02_"
    "2026-06-01.jsonl"
)
DEFAULT_HYBRID_RULES_CANDIDATES_LLM_ADJUDICATOR_REPORT_PATH = Path(
    "experiments/"
    "gan2026_hybrid_rules_candidates_llm_adjudicator_validation25_gpt41mini_v02_"
    "2026-06-01.md"
)

BOUNDARY_FINAL_LABELS = frozenset({"unknown", "no seizure frequency reference"})
CandidateRevision = Literal["frozen_v1", "cluster_diary_candidate_recall"]
DEFAULT_CANDIDATE_REVISION: CandidateRevision = "frozen_v1"


class SeizureEventExtractor:
    """Extract all seizure-frequency events from a clinical note."""

    def __call__(self, note_text: str) -> list[dict[str, str]]:
        raise NotImplementedError


class ClinicalReasoner:
    """Select or aggregate extracted events into one benchmark-facing answer."""

    def __call__(self, note_text: str, events: list[dict[str, str]]) -> dict[str, str]:
        raise NotImplementedError


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


def build_hybrid_rules_candidates_llm_adjudicator_prompt_input(
    record: Any,
    diagnostics: Mapping[str, Any],
) -> str:
    """Build a split-wide hybrid prompt without gold labels or V1 scores."""

    candidate_events = _hybrid_rules_candidates_llm_adjudicator_candidate_events(diagnostics)
    deterministic_final = diagnostics.get("final_selection") or {}
    payload = {
        "prompt_version": PROMPT_VERSION,
        "architecture": "gan2026_hybrid_rules_candidates_llm_adjudicator",
        "claim_type": "hybrid_llm_adjudicator",
        "candidate_revision": diagnostics.get("candidate_revision", DEFAULT_CANDIDATE_REVISION),
        "task": "Gan 2026 seizure-frequency candidate adjudication",
        "source_row_index": record.source_row_index,
        "instructions": [
            "Read the full note first, then adjudicate the deterministic candidate set.",
            (
                "The deterministic generator is a high-recall retrieval layer, not the final "
                "answer, but it is the fallback whenever your override is not directly "
                "supported by candidate evidence."
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
                "Conservative v0.2 policy: change the deterministic top candidate only when "
                "you can name selected_event_ids whose evidence is an exact note substring "
                "and whose normalized_label directly supports final_label."
            ),
            (
                "Do not demote a deterministic frequency or seizure-free answer to unknown "
                "or no seizure frequency reference unless every current/recent candidate is "
                "rejected with evidence-specific rationale."
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


def run_adjudicator_devset(
    examples: Sequence[Mapping[str, Any]],
    *,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
    api_base: str | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    metadata = _run_metadata(
        examples,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        mode=mode,
        api_base=api_base,
    )
    program = DspyFinalSelectionAdjudicator()
    if mode == "live":
        dspy.configure(
            lm=build_dspy_lm(
                model,
                temperature=temperature,
                max_tokens=max_tokens,
                cache=False,
                api_base=api_base,
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
                    "baseline_prediction_label": example["reference"]["baseline_prediction_label"],
                    "baseline_prediction_category": example["reference"][
                        "baseline_prediction_category"
                    ],
                },
                "comparison": comparison,
            }
        )

    metadata["summary"] = summarize_adjudicator_records(records)
    return records, metadata


def run_hybrid_rules_candidates_llm_adjudicator_split(
    records: Sequence[Any],
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
    candidate_revision: CandidateRevision = DEFAULT_CANDIDATE_REVISION,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run the hybrid rules-candidates LLM-adjudicator pipeline over Gan records."""

    reuse_raw_outputs = reuse_raw_outputs or {}
    metadata = _run_metadata(
        [{"split": split, "split_manifest": split_manifest} for _ in records],
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        mode=mode,
        api_base=api_base,
    )
    metadata["architecture"] = "hybrid_rules_candidates_llm_adjudicator"
    metadata["claim_type"] = "hybrid_llm_adjudicator"
    metadata["dspy_cache"] = dspy_cache
    metadata["reuse_source"] = reuse_source
    metadata["escalation_reason"] = escalation_reason
    metadata["candidate_revision"] = candidate_revision
    pipeline = Gan2026PipelineV1()
    program = DspyFinalSelectionAdjudicator()
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

    output_rows: list[dict[str, Any]] = []
    for record in records:
        deterministic_result = pipeline.run(record)
        diagnostics = apply_hybrid_candidate_revision(
            deterministic_result.diagnostics,
            note_text=record.note_text,
            candidate_revision=candidate_revision,
        )
        prompt_input_json = build_hybrid_rules_candidates_llm_adjudicator_prompt_input(
            record,
            diagnostics,
        )
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
        conservative_gate = _conservative_adjudicator_gate(record, diagnostics, decision)
        conservative_score = _compare_label_to_record(
            record,
            str(conservative_gate["final_label"]),
        )
        candidate_recall = _candidate_recall(record, diagnostics)
        output_rows.append(
            {
                "source_row_index": record.source_row_index,
                "split": split,
                "split_manifest": split_manifest,
                "architecture": metadata["architecture"],
                "claim_type": metadata["claim_type"],
                "candidate_revision": candidate_revision,
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
                    "raw_adjudicator": adjudicator_score,
                    "conservative_adjudicator": conservative_score,
                    "adjudicator": conservative_score,
                },
                "conservative_gate": conservative_gate,
                "reference": {
                    "gold_label": record.gold_label,
                    "gold_label_kind": str(record.gold_label_kind),
                    "gold_monthly_frequency": record.gold_monthly_frequency,
                    "row_ok": record.row_ok,
                },
            }
        )
        if progress_every and len(output_rows) % progress_every == 0:
            _emit_hybrid_candidate_adjudicator_checkpoint(
                output_rows,
                metadata,
                total=len(records),
                jsonl_path=checkpoint_jsonl_path,
                report_path=checkpoint_report_path,
            )

    metadata["summary"] = summarize_hybrid_rules_candidates_llm_adjudicator_records(output_rows)
    return output_rows, metadata


def summarize_hybrid_rules_candidates_llm_adjudicator_records(
    records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
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
    changed = sum(_hybrid_candidate_adjudicator_changed_final_label(record) for record in records)
    raw_changed = sum(
        _hybrid_candidate_adjudicator_changed_final_label(record, "raw_adjudicator")
        for record in records
    )
    improved = sum(
        _hybrid_candidate_adjudicator_changed_correctness(
            record,
            from_correct=False,
            to_correct=True,
        )
        for record in records
    )
    regressed = sum(
        _hybrid_candidate_adjudicator_changed_correctness(
            record,
            from_correct=True,
            to_correct=False,
        )
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
        "raw_changed_final_labels": raw_changed,
        "deterministic_wrong_to_adjudicator_correct": improved,
        "deterministic_correct_to_adjudicator_wrong": regressed,
        "deterministic_fallbacks": sum(
            bool((record.get("conservative_gate") or {}).get("used_deterministic_fallback"))
            for record in records
        ),
        "overreach_gate_counts": dict(
            sorted(
                Counter(
                    gate
                    for record in records
                    for gate in (record.get("conservative_gate") or {}).get("fired_gates", [])
                ).items()
            )
        ),
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
    write_jsonl_rows(records, path)


def write_hybrid_rules_candidates_llm_adjudicator_jsonl(
    records: Sequence[Mapping[str, Any]],
    path: Path,
) -> None:
    write_adjudicator_jsonl(records, path)


def load_hybrid_rules_candidates_llm_adjudicator_raw_outputs(path: Path) -> dict[int, str]:
    return load_raw_outputs_by_source_index(path)


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


def _hybrid_rules_candidates_llm_adjudicator_candidate_events(
    diagnostics: Mapping[str, Any],
) -> list[dict[str, Any]]:
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


def apply_hybrid_candidate_revision(
    diagnostics: Mapping[str, Any],
    *,
    note_text: str,
    candidate_revision: CandidateRevision = DEFAULT_CANDIDATE_REVISION,
) -> dict[str, Any]:
    """Apply opt-in hybrid candidate recall revisions outside frozen deterministic V1."""

    revised = dict(diagnostics)
    revised["candidate_revision"] = candidate_revision
    if candidate_revision == "frozen_v1":
        return revised
    if candidate_revision != "cluster_diary_candidate_recall":
        raise ValueError(f"Unknown hybrid candidate revision: {candidate_revision}")

    candidate_events = [dict(event) for event in diagnostics.get("candidate_events", [])]
    normalized_events = [dict(event) for event in diagnostics.get("normalized_events", [])]
    existing_labels = {
        str(event.get("normalized_label"))
        for event in normalized_events
        if event.get("normalized_label") is not None
    }
    existing_evidence = {
        str(event.get("evidence")).lower()
        for event in candidate_events
        if event.get("evidence") is not None
    }
    additions = _cluster_diary_candidate_recall_events(
        note_text,
        start_index=len(candidate_events) + 1,
        existing_labels=existing_labels,
        existing_evidence=existing_evidence,
    )
    if not additions:
        revised["candidate_events"] = candidate_events
        revised["normalized_events"] = normalized_events
        return revised

    for candidate, normalized in additions:
        candidate_events.append(candidate)
        normalized_events.append(normalized)
    revised["candidate_events"] = candidate_events
    revised["normalized_events"] = normalized_events
    revised["candidate_revision_additions"] = len(additions)
    revised["candidate_revision_rule_ids"] = [
        candidate["rule_id"] for candidate, _normalized in additions
    ]
    return revised


def _cluster_diary_candidate_recall_events(
    note_text: str,
    *,
    start_index: int,
    existing_labels: set[str],
    existing_evidence: set[str],
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    additions: list[tuple[dict[str, Any], dict[str, Any]]] = []
    next_index = start_index
    for label, evidence, kind, rule_id, match_groups in _cluster_diary_revision_candidates(
        note_text
    ):
        evidence_key = evidence.lower()
        if label in existing_labels and evidence_key in existing_evidence:
            continue
        event_id = f"event_{next_index}"
        next_index += 1
        candidate = _revision_candidate_event(
            event_id=event_id,
            kind=kind,
            label=label,
            evidence=evidence,
            note_text=note_text,
            rule_id=rule_id,
            match_groups=match_groups,
        )
        normalized = _revision_normalized_event(event_id, label)
        additions.append((candidate, normalized))
        existing_labels.add(str(normalized["normalized_label"]))
        existing_evidence.add(evidence_key)
    return additions


def _cluster_diary_revision_candidates(
    note_text: str,
) -> list[tuple[str, str, str, str, dict[str, str | None]]]:
    candidates: list[tuple[str, str, str, str, dict[str, str | None]]] = []
    candidates.extend(_dual_axis_cluster_candidates(note_text))
    candidates.extend(_distributed_diary_candidates(note_text))
    return candidates


def _dual_axis_cluster_candidates(
    note_text: str,
) -> list[tuple[str, str, str, str, dict[str, str | None]]]:
    pattern = re.compile(
        r"\b(?P<count>\d+|multiple)\s+clusters?\s+per\s+"
        r"(?:(?P<denominator>\d+)\s+)?(?P<unit>day|week|month|year)s?,\s+"
        r"(?P<per_cluster>\d+(?:\s+to\s+\d+)?|multiple)\s+per\s+cluster\b",
        re.IGNORECASE,
    )
    results = []
    for match in pattern.finditer(note_text):
        denominator = match.group("denominator")
        period = f"{denominator} {match.group('unit')}" if denominator else match.group("unit")
        label = (
            f"{match.group('count')} cluster per {period}, "
            f"{match.group('per_cluster')} per cluster"
        ).lower()
        results.append(
            (
                label,
                match.group(0),
                "cluster_frequency",
                "hybrid.cluster_diary_candidate_recall.dual_axis_cluster_literal",
                match.groupdict(),
            )
        )
    return results


def _distributed_diary_candidates(
    note_text: str,
) -> list[tuple[str, str, str, str, dict[str, str | None]]]:
    results: list[tuple[str, str, str, str, dict[str, str | None]]] = []
    month_counts = re.compile(
        r"\b(?P<evidence>(?:(?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December)\s+\d+,\s*){2,}"
        r"(?:January|February|March|April|May|June|July|August|September|October|"
        r"November|December)\s+\d+)\b",
        re.IGNORECASE,
    )
    for match in month_counts.finditer(note_text):
        counts = [
            int(value)
            for value in re.findall(
                r"\b(?:January|February|March|April|May|June|July|August|"
                r"September|October|November|December)\s+(\d+)\b",
                match.group("evidence"),
                flags=re.IGNORECASE,
            )
        ]
        if not counts:
            continue
        total = sum(counts)
        months = len(counts)
        label = _average_or_period_rate_label(total, months, "month")
        results.append(
            (
                label,
                match.group("evidence"),
                "frequency_rate",
                "hybrid.cluster_diary_candidate_recall.month_count_average",
                {"total": str(total), "months": str(months)},
            )
        )

    recent_period = re.compile(
        r"\b(?P<evidence>(?P<count>\d+)\s+in\s+the\s+last\s+(?P<denominator>\d+)\s+"
        r"(?P<unit>day|week|month|year)s?)\b",
        re.IGNORECASE,
    )
    for match in recent_period.finditer(note_text):
        label = (
            f"{match.group('count')} per {match.group('denominator')} "
            f"{match.group('unit').lower()}"
        )
        results.append(
            (
                label,
                match.group("evidence"),
                "frequency_rate",
                "hybrid.cluster_diary_candidate_recall.last_period_count",
                match.groupdict(),
            )
        )

    across_months = re.compile(
        r"\b(?P<evidence>(?P<count>\d+)\s+seizures?\s+across\s+"
        r"(?P<months>(?:January|February|March|April|May|June|July|August|September|"
        r"October|November|December)(?:,\s*|,\s*and\s+|\s+and\s+)"
        r"(?:January|February|March|April|May|June|July|August|September|October|"
        r"November|December)(?:(?:,\s*|,\s*and\s+|\s+and\s+)"
        r"(?:January|February|March|April|May|June|July|August|September|October|"
        r"November|December))*)\b)",
        re.IGNORECASE,
    )
    for match in across_months.finditer(note_text):
        month_count = len(
            re.findall(
                r"\b(?:January|February|March|April|May|June|July|August|September|"
                r"October|November|December)\b",
                match.group("months"),
                flags=re.IGNORECASE,
            )
        )
        if month_count <= 0:
            continue
        label = _average_or_period_rate_label(int(match.group("count")), month_count, "month")
        results.append(
            (
                label,
                match.group("evidence"),
                "frequency_rate",
                "hybrid.cluster_diary_candidate_recall.count_across_named_months",
                {"count": match.group("count"), "months": str(month_count)},
            )
        )
    return results


def _average_or_period_rate_label(total: int, denominator: int, unit: str) -> str:
    if denominator > 0 and total % denominator == 0:
        return f"{total // denominator} per {unit}"
    return f"{total} per {denominator} {unit}"


def _revision_candidate_event(
    *,
    event_id: str,
    kind: str,
    label: str,
    evidence: str,
    note_text: str,
    rule_id: str,
    match_groups: Mapping[str, str | None],
) -> dict[str, Any]:
    start_char = note_text.find(evidence)
    end_char = start_char + len(evidence) if start_char >= 0 else None
    return {
        "event_id": event_id,
        "kind": kind,
        "raw_value": label,
        "evidence": evidence,
        "start_char": start_char if start_char >= 0 else None,
        "end_char": end_char,
        "rule_id": rule_id,
        "rule_group": "hybrid_candidate_recall",
        "portability": "seizure_frequency",
        "match_groups": dict(match_groups),
    }


def _revision_normalized_event(event_id: str, label: str) -> dict[str, Any]:
    try:
        record = label_to_frequency_record(label)
        return {
            "event_id": event_id,
            "normalized_label": record.normalized_label,
            "semantic_kind": str(record.kind),
            "monthly_frequency": record.monthly_frequency,
            "validation_errors": [],
        }
    except ValueError as exc:
        unknown = label_to_frequency_record("unknown")
        return {
            "event_id": event_id,
            "normalized_label": "unknown",
            "semantic_kind": str(unknown.kind),
            "monthly_frequency": unknown.monthly_frequency,
            "validation_errors": [str(exc)],
        }


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


def _conservative_adjudicator_gate(
    record: Any,
    diagnostics: Mapping[str, Any],
    decision: AdjudicatorDecisionRecord | None,
) -> dict[str, Any]:
    deterministic_final = diagnostics.get("final_selection") or {}
    deterministic_label = str(deterministic_final.get("final_label", "unknown"))
    if decision is None:
        return _fallback_gate_payload(
            deterministic_label,
            fallback_reason="no_parseable_adjudicator_decision",
            fired_gates=("adjudicator_output_missing_or_invalid",),
        )

    candidate_by_id = {
        str(event.get("event_id")): event for event in diagnostics.get("candidate_events", [])
    }
    normalized_by_id = {
        str(event.get("event_id")): event for event in diagnostics.get("normalized_events", [])
    }
    selected_ids = tuple(str(event_id) for event_id in decision.selected_event_ids)
    selected_set = set(selected_ids)
    accepted_set = {str(event_id) for event_id in decision.accepted_event_ids}
    fired_gates: list[str] = []

    if not selected_set.issubset(candidate_by_id):
        fired_gates.append("candidate_membership_overreach")
    if not selected_set.issubset(accepted_set):
        fired_gates.append("accepted_subset_overreach")
    if decision.final_label not in BOUNDARY_FINAL_LABELS and not selected_ids:
        fired_gates.append("unsupported_empty_selection_overreach")
    if decision.final_label in BOUNDARY_FINAL_LABELS:
        deterministic_kind = str(deterministic_final.get("final_kind", ""))
        deterministic_selected = deterministic_final.get("selected_event_ids") or []
        if deterministic_kind in {"frequency", "seizure_free"} and deterministic_selected:
            fired_gates.append("unsupported_boundary_demotion_overreach")
    elif selected_ids:
        selected_labels = {
            normalized_by_id.get(event_id, {}).get("normalized_label") for event_id in selected_ids
        }
        if decision.final_label not in selected_labels:
            fired_gates.append("label_support_overreach")

    note_text = str(getattr(record, "note_text", ""))
    for event_id in selected_ids:
        evidence = candidate_by_id.get(event_id, {}).get("evidence")
        if isinstance(evidence, str) and evidence and evidence in note_text:
            continue
        fired_gates.append("evidence_substring_overreach")
        break

    if fired_gates:
        return _fallback_gate_payload(
            deterministic_label,
            fallback_reason="conservative_overreach_gate",
            fired_gates=tuple(fired_gates),
            raw_adjudicator_final_label=decision.final_label,
        )
    return {
        "policy_version": "hybrid_adjudicator_conservative_v0.2",
        "final_label": decision.final_label,
        "used_deterministic_fallback": False,
        "fallback_reason": None,
        "fired_gates": [],
        "raw_adjudicator_final_label": decision.final_label,
        "deterministic_final_label": deterministic_label,
    }


def _fallback_gate_payload(
    deterministic_label: str,
    *,
    fallback_reason: str,
    fired_gates: Sequence[str],
    raw_adjudicator_final_label: str | None = None,
) -> dict[str, Any]:
    return {
        "policy_version": "hybrid_adjudicator_conservative_v0.2",
        "final_label": deterministic_label,
        "used_deterministic_fallback": True,
        "fallback_reason": fallback_reason,
        "fired_gates": list(fired_gates),
        "raw_adjudicator_final_label": raw_adjudicator_final_label,
        "deterministic_final_label": deterministic_label,
    }


def _hybrid_candidate_adjudicator_changed_final_label(
    record: Mapping[str, Any],
    adjudicator_score_name: str = "adjudicator",
) -> bool:
    scores = record.get("scores") or {}
    deterministic = scores.get("deterministic_top") or {}
    adjudicator = scores.get(adjudicator_score_name) or {}
    return bool(adjudicator) and deterministic.get("final_label") != adjudicator.get("final_label")


def _hybrid_candidate_adjudicator_changed_correctness(
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


def _emit_hybrid_candidate_adjudicator_checkpoint(
    records: Sequence[Mapping[str, Any]],
    metadata: dict[str, Any],
    *,
    total: int,
    jsonl_path: Path | None,
    report_path: Path | None,
) -> None:
    metadata["summary"] = summarize_hybrid_rules_candidates_llm_adjudicator_records(records)
    if jsonl_path is not None:
        write_hybrid_rules_candidates_llm_adjudicator_jsonl(records, jsonl_path)
    if report_path is not None and jsonl_path is not None:
        write_hybrid_rules_candidates_llm_adjudicator_report(
            records,
            metadata,
            report_path,
            jsonl_path=jsonl_path,
        )
    progress = {
        "processed": len(records),
        "total": total,
        "adjudicator_purist_accuracy_so_far": metadata["summary"]["adjudicator_purist_accuracy"],
        "candidate_purist_recall_rate_so_far": metadata["summary"]["candidate_purist_recall_rate"],
        "reused_raw_outputs": metadata["summary"]["reused_raw_outputs"],
    }
    print(json.dumps(progress, sort_keys=True), file=sys.stderr, flush=True)


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


def _run_metadata(
    examples: Sequence[Mapping[str, Any]],
    *,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: str,
    api_base: str | None = None,
) -> dict[str, Any]:
    split = sorted({str(example["split"]) for example in examples})
    split_manifest = sorted({str(example["split_manifest"]) for example in examples})
    return build_run_metadata(
        mode=mode,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        prompt_version=PROMPT_VERSION,
        dspy_version=getattr(dspy, "__version__", "unknown"),
        split=", ".join(split),
        split_manifest=", ".join(split_manifest),
        api_base=api_base,
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
