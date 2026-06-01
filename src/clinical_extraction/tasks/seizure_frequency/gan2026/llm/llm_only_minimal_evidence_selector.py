"""LLM-only minimal evidence selector for Gan 2026 seizure-frequency extraction."""

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
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_raw_outputs_by_source_index,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_metadata import (
    build_run_metadata,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    repair_prediction_label_clean_scorer_facing,
    repair_prediction_label_format_preserving,
    repair_prediction_label_with_evidence,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.reports.minimal_evidence_report import (
    write_report,
)

PROMPT_VERSION = "gan2026_llm_only_minimal_evidence_selector_v2"
PROMPT_POLICY_TAXONOMY: list[dict[str, str]] = [
    {
        "policy_id": "mes_v2.schema.shallow_json_object",
        "controlled_variable": "minimal_schema_shape",
        "portability": "general",
        "status": "active",
        "description": "Prompt requires a shallow answer plus supporting_facts JSON object.",
    },
    {
        "policy_id": "mes_v2.evidence.exact_answer_substring",
        "controlled_variable": "answer_evidence_substring_policy",
        "portability": "seizure_frequency",
        "status": "active",
        "description": "Prompt requires answer.evidence to be copied from the note.",
    },
    {
        "policy_id": "mes_v2.answer.source_near_text",
        "controlled_variable": "source_near_answer_policy",
        "portability": "seizure_frequency",
        "status": "active",
        "description": "Prompt asks for source-near answer text; normalization is downstream.",
    },
]
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_llm_only_minimal_evidence_selector_validation25_v2_2026-06-01.jsonl"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_llm_only_minimal_evidence_selector_validation25_v2_2026-06-01.md"
)


MinimalAnswerState = Literal[
    "frequency",
    "cluster_frequency",
    "seizure_free",
    "unknown_frequency",
    "no_frequency_reference",
    "last_event_only",
    "non_seizure_or_proxy",
]


class MinimalAnswerRecord(BaseModel):
    """Minimal prediction-bearing answer emitted by the model."""

    model_config = ConfigDict(extra="forbid")

    state: MinimalAnswerState
    answer_text: str
    evidence: str
    confidence: Literal["low", "medium", "high"] | None = None
    reason: str | None = None


class MinimalSupportingFactRecord(BaseModel):
    """Optional source-near fact supporting or competing with the answer."""

    model_config = ConfigDict(extra="forbid")

    fact_id: str
    role: Literal["selected", "competing", "context", "rejected"]
    state: MinimalAnswerState | Literal["cluster_context"]
    fact_text: str
    evidence: str


class MinimalEvidenceExtractionRecord(BaseModel):
    """Full minimal evidence-selector record returned by the LLM."""

    model_config = ConfigDict(extra="forbid")

    answer: MinimalAnswerRecord
    supporting_facts: list[MinimalSupportingFactRecord]


class Gan2026MinimalEvidenceSelectorSignature(dspy.Signature):
    """Select the Gan seizure-frequency answer using a minimal evidence contract."""

    prompt_input_json: str = dspy.InputField(
        desc=(
            "JSON containing one clinical note and minimal schema instructions. It omits "
            "gold labels, deterministic candidates, and rich claim-table selector state."
        )
    )
    minimal_evidence_selector_json: str = dspy.OutputField(
        desc="One strict JSON object with answer and supporting_facts."
    )


class DspyMinimalEvidenceSelector(dspy.Module):
    """DSPy program for the minimal evidence selector."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(Gan2026MinimalEvidenceSelectorSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def build_prompt_input(record: GanFrequencyRecord) -> str:
    """Build the minimal evidence-selector prompt payload, excluding gold labels."""

    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": "Gan 2026 minimal evidence selector for seizure frequency",
        "source_row_index": record.source_row_index,
        "prompt_policy_taxonomy": PROMPT_POLICY_TAXONOMY,
        "instructions": [
            "Read the full clinical note.",
            (
                "Return exactly one strict JSON object with top-level keys answer "
                "and supporting_facts."
            ),
            "Do not return markdown, Python dict syntax, comments, or any extra top-level keys.",
            "Do not create a nested final_query object.",
            (
                "Use answer.state to describe the selected answer family: frequency, "
                "cluster_frequency, seizure_free, unknown_frequency, no_frequency_reference, "
                "last_event_only, or non_seizure_or_proxy."
            ),
            (
                "Use answer.answer_text for the source-near selected frequency or boundary "
                "answer. It can be natural source wording such as <= four per day, no seizures "
                "for six months, unknown, or no seizure frequency reference."
            ),
            "Every evidence value must be an exact substring from the note when possible.",
            (
                "If there are competing or contextual seizure-frequency facts, include a few "
                "supporting_facts rows. Keep this short. Use an empty list only when no "
                "supporting fact can be copied cleanly."
            ),
            (
                "Use no_frequency_reference only when the note contains no usable "
                "seizure-frequency evidence. Use unknown_frequency when seizure evidence exists "
                "but current frequency cannot be converted."
            ),
            (
                "Prefer the current or recent seizure-frequency answer over historical, "
                "hypothetical, medication, rescue-medication, or proxy-only statements."
            ),
        ],
        "answer_schema": {
            "state": [
                "frequency",
                "cluster_frequency",
                "seizure_free",
                "unknown_frequency",
                "no_frequency_reference",
                "last_event_only",
                "non_seizure_or_proxy",
            ],
            "answer_text": "source-near selected answer text",
            "evidence": "exact note substring supporting the selected answer",
            "confidence": ["low", "medium", "high", None],
            "reason": "optional brief reason, or null",
        },
        "supporting_fact_schema": {
            "fact_id": "stable string such as f1",
            "role": ["selected", "competing", "context", "rejected"],
            "state": [
                "frequency",
                "cluster_frequency",
                "seizure_free",
                "unknown_frequency",
                "no_frequency_reference",
                "last_event_only",
                "non_seizure_or_proxy",
                "cluster_context",
            ],
            "fact_text": "source-near fact text",
            "evidence": "exact note substring supporting this fact",
        },
        "note_text": record.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def parse_minimal_evidence_selector_json(
    raw_output: str,
) -> tuple[MinimalEvidenceExtractionRecord | None, list[str], dict[str, Any]]:
    """Parse one raw minimal evidence-selector output."""

    diagnostics: dict[str, Any] = {
        "raw_json_valid": False,
        "schema_valid": False,
        "repair_applied": False,
        "repair_policy": None,
        "extra_fields_seen": [],
    }
    try:
        raw_payload = json.loads(_extract_json_object(raw_output))
        diagnostics["raw_json_valid"] = True
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json: {exc.msg}"], diagnostics

    payload, repair_notes = _repair_minimal_payload(raw_payload)
    if repair_notes:
        diagnostics["repair_applied"] = True
        diagnostics["repair_policy"] = "minimal_alias_shape_repair_v0"
    if isinstance(raw_payload, dict):
        diagnostics["extra_fields_seen"] = sorted(
            key for key in raw_payload if key not in {"answer", "supporting_facts"}
        )

    try:
        extraction = MinimalEvidenceExtractionRecord.model_validate(payload)
    except ValidationError as exc:
        errors = [*repair_notes, f"schema_validation_error: {exc.errors()[0]['msg']}"]
        return None, errors, diagnostics

    diagnostics["schema_valid"] = True
    errors = [*repair_notes]
    if extraction.answer.state == "no_frequency_reference" and extraction.supporting_facts:
        errors.append("contract_warning: no_frequency_reference has supporting facts")
    return extraction, errors, diagnostics


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
    program = DspyMinimalEvidenceSelector()
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
                raw_output = str(prediction.minimal_evidence_selector_json)
            except Exception as exc:  # pragma: no cover - exercised only with live APIs.
                call_error = f"{type(exc).__name__}: {exc}"

        if raw_output:
            extraction, parse_errors, contract_diagnostics = parse_minimal_evidence_selector_json(
                raw_output
            )
        else:
            extraction, parse_errors, contract_diagnostics = (
                None,
                ["not_run"],
                _empty_contract_diagnostics(),
            )
        evidence_summary = _evidence_summary(record.note_text, extraction)
        score_layers = _score_layers(record, extraction)
        derived_diagnostics = _derived_diagnostics(extraction, score_layers)
        repair_changes = _repair_changes(score_layers)
        rows.append(
            {
                "source_row_index": record.source_row_index,
                "split": split,
                "split_manifest": split_manifest,
                "pipeline_name": PROMPT_VERSION,
                "prompt_version": PROMPT_VERSION,
                "prompt_input_json": prompt_input_json,
                "raw_output": raw_output,
                "reused_raw_output": reused_raw_output,
                "call_error": call_error,
                "parse_errors": parse_errors,
                "minimal_record": extraction.model_dump() if extraction else None,
                "contract_diagnostics": contract_diagnostics,
                "evidence_summary": evidence_summary,
                "derived_diagnostics": derived_diagnostics,
                "score_layers": score_layers,
                "repair_changes": repair_changes,
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
    count = len(rows)
    raw = _layer_summary(rows, "raw")
    strict = _layer_summary(rows, "strict_format")
    clean = _layer_summary(rows, "clean_scorer_facing")
    states = Counter(
        (row.get("minimal_record") or {}).get("answer", {}).get("state")
        for row in rows
        if row.get("minimal_record")
    )
    return {
        "examples": count,
        "minimal_records": sum(bool(row.get("minimal_record")) for row in rows),
        "call_failures": sum(bool(row.get("call_error")) for row in rows),
        "reused_raw_outputs": sum(bool(row.get("reused_raw_output")) for row in rows),
        "invalid_json_failures": sum(
            any(str(error).startswith("invalid_json:") for error in row.get("parse_errors") or [])
            for row in rows
        ),
        "schema_failures": sum(
            any(
                str(error).startswith("schema_validation_error:")
                for error in row.get("parse_errors") or []
            )
            for row in rows
        ),
        "parse_or_validation_failures": sum(
            _has_blocking_parse_issue(row.get("parse_errors")) for row in rows
        ),
        "answer_evidence_valid": sum(
            bool((row.get("evidence_summary") or {}).get("answer_evidence_valid"))
            for row in rows
        ),
        "supporting_fact_evidence_valid": sum(
            int((row.get("evidence_summary") or {}).get("supporting_fact_evidence_valid", 0))
            for row in rows
        ),
        "supporting_fact_evidence_total": sum(
            int((row.get("evidence_summary") or {}).get("supporting_fact_evidence_total", 0))
            for row in rows
        ),
        "raw_scorable": raw["scorable"],
        "raw_purist_correct": raw["purist_correct"],
        "raw_purist_accuracy": raw["purist_accuracy"],
        "raw_pragmatic_correct": raw["pragmatic_correct"],
        "raw_pragmatic_accuracy": raw["pragmatic_accuracy"],
        "strict_format_scorable": strict["scorable"],
        "strict_format_purist_correct": strict["purist_correct"],
        "strict_format_purist_accuracy": strict["purist_accuracy"],
        "strict_format_pragmatic_correct": strict["pragmatic_correct"],
        "strict_format_pragmatic_accuracy": strict["pragmatic_accuracy"],
        "clean_scorer_facing_scorable": clean["scorable"],
        "clean_scorer_facing_purist_correct": clean["purist_correct"],
        "clean_scorer_facing_purist_accuracy": clean["purist_accuracy"],
        "clean_scorer_facing_pragmatic_correct": clean["pragmatic_correct"],
        "clean_scorer_facing_pragmatic_accuracy": clean["pragmatic_accuracy"],
        "repair_changed_rows": sum(bool(row.get("repair_changes")) for row in rows),
        "answer_states": dict(sorted((str(key), value) for key, value in states.items())),
    }


def write_jsonl(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    write_jsonl_rows(rows, path)


def load_reusable_raw_outputs(path: Path) -> dict[int, str]:
    return load_raw_outputs_by_source_index(path)


def _score_layers(
    record: GanFrequencyRecord,
    extraction: MinimalEvidenceExtractionRecord | None,
) -> dict[str, dict[str, Any]]:
    raw_label = _raw_answer_label(extraction)
    strict_label = repair_prediction_label_format_preserving(raw_label) if raw_label else None
    clean_label = _selected_evidence_repaired_label(record, extraction, raw_label)
    return {
        "raw": _score_label(record, raw_label),
        "strict_format": _score_label(record, strict_label),
        "clean_scorer_facing": _score_label(record, clean_label),
    }


def _raw_answer_label(extraction: MinimalEvidenceExtractionRecord | None) -> str | None:
    if extraction is None:
        return None
    state = extraction.answer.state
    if state in {"unknown_frequency", "last_event_only", "non_seizure_or_proxy"}:
        return "unknown"
    if state == "no_frequency_reference":
        return "no seizure frequency reference"
    return extraction.answer.answer_text


def _selected_evidence_repaired_label(
    record: GanFrequencyRecord,
    extraction: MinimalEvidenceExtractionRecord | None,
    raw_label: str | None,
) -> str | None:
    if raw_label is None:
        return None
    if extraction is None:
        return repair_prediction_label_clean_scorer_facing(raw_label)
    return repair_prediction_label_with_evidence(
        raw_label,
        extraction.answer.evidence,
        context_text=record.note_text,
    )


def _score_label(record: GanFrequencyRecord, label: str | None) -> dict[str, Any]:
    result: dict[str, Any] = {"final_label": label, "scorable": False}
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


def _evidence_summary(
    note_text: str,
    extraction: MinimalEvidenceExtractionRecord | None,
) -> dict[str, Any]:
    if extraction is None:
        return {
            "answer_evidence_valid": False,
            "answer_evidence": None,
            "supporting_fact_evidence_valid": 0,
            "supporting_fact_evidence_total": 0,
            "supporting_fact_evidence_invalid": [],
        }
    invalid_facts = []
    fact_valid_count = 0
    for fact in extraction.supporting_facts:
        if evidence_is_substring(note_text, fact.evidence):
            fact_valid_count += 1
        else:
            invalid_facts.append({"fact_id": fact.fact_id, "evidence": fact.evidence})
    return {
        "answer_evidence_valid": evidence_is_substring(note_text, extraction.answer.evidence),
        "answer_evidence": extraction.answer.evidence,
        "supporting_fact_evidence_valid": fact_valid_count,
        "supporting_fact_evidence_total": len(extraction.supporting_facts),
        "supporting_fact_evidence_invalid": invalid_facts,
    }


def _derived_diagnostics(
    extraction: MinimalEvidenceExtractionRecord | None,
    score_layers: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    if extraction is None:
        return {
            "derived_state": None,
            "normalization": None,
            "review_projection": None,
        }
    selected_fact_ids = [
        fact.fact_id for fact in extraction.supporting_facts if fact.role == "selected"
    ]
    boundary_state = _derive_boundary_state(extraction.answer.state)
    cluster_axis = _derive_cluster_axis(extraction)
    clean = score_layers["clean_scorer_facing"]
    normalization = {
        "raw_selected_frequency": extraction.answer.answer_text,
        "final_label": clean.get("final_label"),
        "semantic_kind": _semantic_kind_for_state(extraction.answer.state),
        "monthly_frequency": clean.get("predicted_monthly_frequency"),
        "normalization_policy": "selected_evidence_repair_after_minimal_answer_v2",
    }
    return {
        "derived_state": {
            "boundary_state": boundary_state,
            "cluster_axis": cluster_axis,
            "selected_fact_ids": selected_fact_ids,
        },
        "normalization": normalization,
        "review_projection": {
            "claims": [
                {
                    "claim_id": fact.fact_id,
                    "claim_type": _claim_type_for_fact_state(fact.state),
                    "evidence": fact.evidence,
                    "raw_frequency": fact.fact_text,
                    "derived_from": "minimal_supporting_fact",
                }
                for fact in extraction.supporting_facts
            ],
            "final_query": {
                "selected_claim_ids": selected_fact_ids,
                "answer_kind": normalization["semantic_kind"],
                "cluster_axis": cluster_axis,
                "boundary_state": boundary_state,
                "raw_selected_frequency": extraction.answer.answer_text,
                "final_label": normalization["final_label"],
                "evidence": extraction.answer.evidence,
                "derived_from": "minimal_answer",
            },
        },
    }


def _repair_minimal_payload(payload: Any) -> tuple[Any, list[str]]:
    if not isinstance(payload, dict):
        return payload, []
    repaired = dict(payload)
    notes: list[str] = []
    final_selector = repaired.pop("final_selector", None)
    if "answer" not in repaired and isinstance(final_selector, dict):
        repaired["answer"] = final_selector
        notes.append("schema_repair: final_selector mapped to answer")
    if "supporting_facts" not in repaired and isinstance(repaired.get("claims"), list):
        repaired["supporting_facts"] = [
            _fact_from_claim(claim)
            for claim in repaired.get("claims", [])
            if isinstance(claim, dict)
        ]
        notes.append("schema_repair: claims mapped to supporting_facts")
    if "supporting_facts" not in repaired:
        repaired["supporting_facts"] = []
    answer = repaired.get("answer")
    if isinstance(answer, dict):
        repaired["answer"] = _repair_answer_payload(answer, notes)
    facts = repaired.get("supporting_facts")
    if isinstance(facts, list):
        repaired["supporting_facts"] = [
            _repair_fact_payload(fact, index, notes) if isinstance(fact, dict) else fact
            for index, fact in enumerate(facts, start=1)
        ]
    repaired = {
        key: value for key, value in repaired.items() if key in {"answer", "supporting_facts"}
    }
    return repaired, notes


def _repair_answer_payload(answer: Mapping[str, Any], notes: list[str]) -> dict[str, Any]:
    repaired = dict(answer)
    if "state" not in repaired and "answer_kind" in repaired:
        repaired["state"] = _state_from_answer_kind(repaired["answer_kind"])
        notes.append("schema_repair: answer_kind mapped to answer.state")
    if "answer_text" not in repaired:
        for alias in ("raw_selected_frequency", "normalized_rate", "final_label"):
            if isinstance(repaired.get(alias), str):
                repaired["answer_text"] = repaired[alias]
                notes.append(f"schema_repair: {alias} mapped to answer.answer_text")
                break
    if "evidence" not in repaired and isinstance(repaired.get("reasoning"), str):
        repaired["evidence"] = repaired["reasoning"]
        notes.append("schema_repair: reasoning mapped to answer.evidence")
    if "reason" not in repaired and isinstance(repaired.get("rationale"), str):
        repaired["reason"] = repaired["rationale"]
        notes.append("schema_repair: rationale mapped to answer.reason")
    if "reason" not in repaired and isinstance(repaired.get("reasoning"), str):
        repaired["reason"] = repaired["reasoning"]
        notes.append("schema_repair: reasoning mapped to answer.reason")
    if "confidence" in repaired:
        repaired["confidence"] = _unwrap_singleton(repaired["confidence"])
    if "state" in repaired:
        repaired["state"] = _state_alias(_unwrap_singleton(repaired["state"]))
    return {
        key: value
        for key, value in repaired.items()
        if key in {"state", "answer_text", "evidence", "confidence", "reason"}
    }


def _repair_fact_payload(
    fact: Mapping[str, Any],
    index: int,
    notes: list[str],
) -> dict[str, Any]:
    repaired = dict(fact)
    if "fact_id" not in repaired and "claim_id" in repaired:
        repaired["fact_id"] = repaired["claim_id"]
        notes.append("schema_repair: claim_id mapped to fact_id")
    if "fact_id" not in repaired:
        repaired["fact_id"] = f"f{index}"
        notes.append("schema_repair: missing fact_id filled")
    if "role" not in repaired:
        repaired["role"] = "context"
    if repaired.get("role") == "cluster_context":
        repaired["role"] = "context"
        notes.append("schema_repair: cluster_context role mapped to context")
    if "state" not in repaired and "claim_type" in repaired:
        repaired["state"] = _state_from_claim_type(repaired["claim_type"])
        notes.append("schema_repair: claim_type mapped to fact.state")
    if "fact_text" not in repaired:
        for alias in ("raw_frequency", "final_label", "text"):
            if isinstance(repaired.get(alias), str):
                repaired["fact_text"] = repaired[alias]
                notes.append(f"schema_repair: {alias} mapped to fact_text")
                break
    if "fact_text" not in repaired and isinstance(repaired.get("evidence"), str):
        repaired["fact_text"] = repaired["evidence"]
        notes.append("schema_repair: evidence copied to fact_text")
    if "evidence" not in repaired and isinstance(repaired.get("fact_text"), str):
        repaired["evidence"] = repaired["fact_text"]
        notes.append("schema_repair: fact_text copied to evidence")
    if "state" in repaired:
        repaired["state"] = _state_alias(_unwrap_singleton(repaired["state"]))
    return {
        key: value
        for key, value in repaired.items()
        if key in {"fact_id", "role", "state", "fact_text", "evidence"}
    }


def _fact_from_claim(claim: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "fact_id": claim.get("claim_id"),
        "role": "context",
        "state": _state_from_claim_type(claim.get("claim_type")),
        "fact_text": claim.get("raw_frequency") or claim.get("evidence"),
        "evidence": claim.get("evidence"),
    }


def _state_from_answer_kind(value: Any) -> Any:
    mapping = {
        "frequency": "frequency",
        "cluster_frequency": "cluster_frequency",
        "seizure_free": "seizure_free",
        "unknown": "unknown_frequency",
        "unknown_frequency": "unknown_frequency",
        "no_reference": "no_frequency_reference",
        "no_frequency_reference": "no_frequency_reference",
        "non_seizure_event": "non_seizure_or_proxy",
    }
    return mapping.get(str(value), value)


def _state_from_claim_type(value: Any) -> Any:
    mapping = {
        "frequency": "frequency",
        "cluster_frequency": "cluster_frequency",
        "seizure_free": "seizure_free",
        "last_event_only": "last_event_only",
        "unknown_frequency": "unknown_frequency",
        "no_reference": "no_frequency_reference",
        "non_seizure_event": "non_seizure_or_proxy",
    }
    return mapping.get(str(value), value)


def _state_alias(value: Any) -> Any:
    aliases = {
        "unknown": "unknown_frequency",
        "no_reference": "no_frequency_reference",
        "no seizure frequency reference": "no_frequency_reference",
        "non_seizure_event": "non_seizure_or_proxy",
    }
    if isinstance(value, str):
        return aliases.get(value, value)
    return value


def _derive_boundary_state(state: str) -> str:
    return {
        "frequency": "ordinary_frequency",
        "cluster_frequency": "ordinary_frequency",
        "seizure_free": "seizure_free_interval",
        "unknown_frequency": "unknown_frequency",
        "no_frequency_reference": "no_frequency_reference",
        "last_event_only": "last_event_only",
        "non_seizure_or_proxy": "non_epileptic_or_proxy",
    }[state]


def _derive_cluster_axis(extraction: MinimalEvidenceExtractionRecord) -> str:
    text = " ".join(
        [extraction.answer.answer_text, extraction.answer.evidence]
        + [fact.fact_text for fact in extraction.supporting_facts]
    ).lower()
    if extraction.answer.state == "cluster_frequency":
        if "per cluster" in text:
            return "cadence_and_burden"
        return "cadence_only"
    if "cluster" in text:
        return "vague_cluster"
    return "none"


def _semantic_kind_for_state(state: str) -> str:
    return {
        "frequency": "frequency",
        "cluster_frequency": "frequency",
        "seizure_free": "seizure_free",
        "unknown_frequency": "unknown",
        "no_frequency_reference": "no_reference",
        "last_event_only": "unknown",
        "non_seizure_or_proxy": "unknown",
    }[state]


def _claim_type_for_fact_state(state: str) -> str:
    return {
        "frequency": "frequency",
        "cluster_frequency": "cluster_frequency",
        "seizure_free": "seizure_free",
        "unknown_frequency": "unknown_frequency",
        "no_frequency_reference": "no_reference",
        "last_event_only": "last_event_only",
        "non_seizure_or_proxy": "non_seizure_event",
        "cluster_context": "cluster_frequency",
    }[state]


def _repair_changes(score_layers: Mapping[str, Mapping[str, Any]]) -> list[dict[str, str]]:
    changes: list[dict[str, str]] = []
    previous = score_layers["raw"].get("final_label")
    for layer in ["strict_format", "clean_scorer_facing"]:
        current = score_layers[layer].get("final_label")
        if isinstance(previous, str) and isinstance(current, str) and current != previous:
            changes.append({"layer": layer, "before": previous, "after": current})
        previous = current
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


def _empty_contract_diagnostics() -> dict[str, Any]:
    return {
        "raw_json_valid": False,
        "schema_valid": False,
        "repair_applied": False,
        "repair_policy": None,
        "extra_fields_seen": [],
    }


def _has_blocking_parse_issue(errors: Any) -> bool:
    return any(
        str(error).startswith(
            (
                "invalid_json:",
                "schema_validation_error:",
                "not_run",
            )
        )
        for error in errors or []
    )


def _unwrap_singleton(value: Any) -> Any:
    if isinstance(value, list) and len(value) == 1:
        return value[0]
    return value


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
        "raw_scorable": metadata["summary"]["raw_scorable"],
        "clean_purist_accuracy_so_far": metadata["summary"]["clean_scorer_facing_purist_accuracy"],
        "reused_raw_outputs": metadata["summary"]["reused_raw_outputs"],
    }
    print(json.dumps(progress, sort_keys=True), file=sys.stderr, flush=True)


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
        extra={
            "pipeline_name": PROMPT_VERSION,
            "prompt_policy_ids": [policy["policy_id"] for policy in PROMPT_POLICY_TAXONOMY],
            "schema_contract": "minimal_source_near_answer_plus_selected_evidence_repair_v2",
        },
    )
