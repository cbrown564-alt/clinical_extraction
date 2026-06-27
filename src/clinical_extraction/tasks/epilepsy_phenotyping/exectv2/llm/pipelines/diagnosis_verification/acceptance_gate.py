"""Constrained accept/reject gate for ExECTv2 Diagnosis candidates.

The gate does not let the model render arbitrary final mentions. Deterministic
code builds normalized candidate mentions from upstream Diagnosis components;
the model only accepts or rejects each candidate ID.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy

from clinical_extraction.core.run_resume import merge_rows, pending_items, read_completed
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    project_cuis,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    ENTITY_REGISTRY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.diagnosis_verification import (
    reconciler as reconciler_base,
    verifier as verifier_base,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    MentionRecord,
    _has_blocking_parse_issue,
    check_evidence,
    repair_attributes,
    write_jsonl,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.json_parse import (
    extract_json_object,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

PROMPT_VERSION = "exectv2_hybrid_diagnosis_acceptance_gate_v0.1"
PIPELINE_FAMILY = "exectv2_hybrid_diagnosis_acceptance_gate"
COMPONENT_OWNER = "hybrid_diagnosis_acceptance_gate"


class ExECTv2DiagnosisAcceptanceGateSignature(dspy.Signature):
    """Accept or reject fixed Diagnosis candidate mentions."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one letter, fixed Diagnosis candidates, and gate rules."
    )
    decision_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"decisions\": [{\"candidate_id\": \"C0\", "
            "\"decision\": \"accept\", \"reason_code\": \"...\", "
            "\"rationale\": \"...\"}, ...]}"
        )
    )


class DspyDiagnosisAcceptanceGate(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(ExECTv2DiagnosisAcceptanceGateSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def read_rows(path: Path | None) -> list[dict[str, Any]]:
    if path is None or not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def build_candidate_pool(
    *,
    verifier_mentions: Sequence[Mapping[str, Any]],
    decomposer_mentions: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Build fixed Diagnosis candidates from upstream sources."""

    by_key: dict[tuple[str, tuple[tuple[str, str], ...], str], dict[str, Any]] = {}
    for source, mentions in (
        ("verifier", verifier_mentions),
        ("decomposer", decomposer_mentions),
    ):
        for mention in mentions:
            text = str(mention.get("text", ""))
            evidence = str(mention.get("evidence", ""))
            attrs = {
                str(k): str(v)
                for k, v in dict(mention.get("attributes") or {}).items()
                if v is not None and k not in {"CUI", "CUIPhrase"}
            }
            key = (text, tuple(sorted(attrs.items())), evidence)
            if key not in by_key:
                by_key[key] = {
                    "text": text,
                    "attributes": attrs,
                    "evidence": evidence,
                    "family": _candidate_family(text, evidence),
                    "sources": [],
                }
            if source not in by_key[key]["sources"]:
                by_key[key]["sources"].append(source)

    candidates: list[dict[str, Any]] = []
    for index, candidate in enumerate(
        sorted(
            by_key.values(),
            key=lambda item: (
                str(item["family"]),
                str(item["evidence"]),
                str(item["text"]),
                ",".join(item["sources"]),
            ),
        )
    ):
        candidate["sources"] = sorted(candidate["sources"])
        candidate["candidate_id"] = f"C{index}"
        candidates.append(candidate)
    return candidates


def build_prompt_input(
    letter: ExectLetter,
    candidates: Sequence[Mapping[str, Any]],
) -> str:
    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": (
            "Review fixed Diagnosis candidate mentions for one clinical letter. "
            "Return one accept/reject decision for every candidate_id. The model "
            "does not create new mentions; accepted candidates are rendered "
            "deterministically from the candidate list."
        ),
        "candidate_mentions": list(candidates),
        "output_schema": {
            "decisions": [
                {
                    "candidate_id": "C0",
                    "decision": "accept | reject",
                    "reason_code": (
                        "direct_assertion | section_context_only | "
                        "frequency_only_seizure_type | historical_background | "
                        "inferred_structural_cause | non_epileptic_event | duplicate"
                    ),
                    "rationale": "One brief sentence.",
                }
            ]
        },
        "acceptance_rules": _acceptance_rules(),
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def parse_decision_json(raw_output: str) -> tuple[dict[str, str], list[str]]:
    if not raw_output.strip():
        return {}, ["not_run"]
    try:
        payload = json.loads(extract_json_object(raw_output))
    except json.JSONDecodeError as exc:
        return {}, [f"json_decode: {exc}"]
    decisions = payload.get("decisions")
    if not isinstance(decisions, list):
        return {}, ["missing_decisions_list"]
    out: dict[str, str] = {}
    errors: list[str] = []
    for index, item in enumerate(decisions):
        if not isinstance(item, Mapping):
            errors.append(f"decision_{index}_not_object")
            continue
        candidate_id = item.get("candidate_id")
        decision = item.get("decision")
        if not isinstance(candidate_id, str) or not isinstance(decision, str):
            errors.append(f"decision_{index}_missing_fields")
            continue
        normalized = decision.strip().lower()
        if normalized not in {"accept", "reject"}:
            errors.append(f"decision_{index}_invalid_decision")
            continue
        out[candidate_id] = normalized
    return out, errors


def to_predicted_letter(
    letter_id: str,
    candidates: Sequence[Mapping[str, Any]],
    *,
    accepted_ids: set[str],
    note_text: str,
) -> tuple[PredictedLetter, list[str]]:
    records = [
        MentionRecord(
            text=str(candidate.get("text", "")),
            attributes=dict(candidate.get("attributes") or {}),
            evidence=str(candidate.get("evidence", "")),
            confidence="medium",
            rationale=(
                "Accepted fixed Diagnosis candidate from "
                f"{','.join(candidate.get('sources', []))}."
            ),
        )
        for candidate in candidates
        if str(candidate.get("candidate_id", "")) in accepted_ids
    ]
    evidence_valid, evidence_invalid, warnings = check_evidence(records, note_text=note_text)
    predicted_mentions: list[PredictedMention] = []
    spec = ENTITY_REGISTRY[DIAGNOSIS.name]
    for mention in evidence_valid:
        repaired_attrs, attr_warnings = repair_attributes(mention.attributes, spec=spec)
        warnings.extend(f"{DIAGNOSIS.name}: {warning}" for warning in attr_warnings)
        predicted_mentions.append(
            PredictedMention(
                entity=DIAGNOSIS.name,
                text=mention.text,
                attributes=repaired_attrs,
                evidence=mention.evidence,
                confidence=mention.confidence,
                rationale=mention.rationale,
                component_owner=COMPONENT_OWNER,
            )
        )

    return (
        project_cuis(
            PredictedLetter(
                letter_id=letter_id,
                mentions=tuple(predicted_mentions),
                diagnostics={
                    "prompt_version": PROMPT_VERSION,
                    "pipeline_family": PIPELINE_FAMILY,
                    "n_evidence_invalid": len(evidence_invalid),
                    "attribute_warnings": warnings,
                },
            )
        ),
        warnings,
    )


def run_split(
    letters: Sequence[ExectLetter],
    *,
    verifier_rows: Sequence[Mapping[str, Any]] = (),
    decomposer_rows: Sequence[Mapping[str, Any]] = (),
    split: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
    dspy_cache: bool = True,
    api_base: str | None = None,
    progress_every: int | None = None,
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
    resume: bool = False,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    program = DspyDiagnosisAcceptanceGate()
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

    verifier_by_id = reconciler_base.mentions_by_letter(verifier_rows)
    decomposer_by_id = reconciler_base.mentions_by_letter(decomposer_rows)
    order = [letter.letter_id for letter in letters]
    requested = set(order)
    existing_rows, completed = read_completed(
        checkpoint_jsonl_path if resume else None, key="letter_id"
    )
    rows: list[dict[str, Any]] = [r for r in existing_rows if r.get("letter_id") in requested]
    n_resumed = len(rows)
    todo = pending_items(letters, completed, key_of=lambda letter: letter.letter_id)

    for letter in todo:
        candidates = build_candidate_pool(
            verifier_mentions=verifier_by_id.get(letter.letter_id, []),
            decomposer_mentions=decomposer_by_id.get(letter.letter_id, []),
        )
        prompt_input_json = build_prompt_input(letter, candidates)
        raw_output = ""
        call_error: str | None = None
        if mode == "live":
            try:
                prediction = program(prompt_input_json=prompt_input_json)
                raw_output = str(prediction.decision_json)
            except Exception as exc:  # pragma: no cover
                call_error = f"{type(exc).__name__}: {exc}"
        decisions, parse_errors = parse_decision_json(raw_output)
        accepted_ids = {
            candidate_id for candidate_id, decision in decisions.items() if decision == "accept"
        }
        predicted_letter, gate_warnings = to_predicted_letter(
            letter.letter_id,
            candidates,
            accepted_ids=accepted_ids,
            note_text=letter.note_text,
        )
        rows.append(
            {
                "letter_id": letter.letter_id,
                "split": split,
                "prompt_version": PROMPT_VERSION,
                "pipeline_family": PIPELINE_FAMILY,
                "model": model,
                "mode": mode,
                "candidate_mentions": list(candidates),
                "prompt_input_json": prompt_input_json,
                "raw_output": raw_output,
                "call_error": call_error,
                "parse_errors": parse_errors,
                "gate_warnings": gate_warnings,
                "decisions": decisions,
                "n_candidates": len(candidates),
                "n_accepted": len(accepted_ids),
                "n_mentions_scored": len(predicted_letter.mentions),
                "n_evidence_invalid": len(accepted_ids) - len(predicted_letter.mentions),
                "predicted_mentions": [
                    verifier_base._mention_to_row(m) for m in predicted_letter.mentions
                ],
                "gold_mentions": [
                    {"text": a.text, "attributes": dict(a.attributes)}
                    for a in letter.entities(DIAGNOSIS.name)
                ],
            }
        )
        if progress_every and (len(rows) - n_resumed) % progress_every == 0:
            _emit_checkpoint(
                rows,
                total=len(letters),
                jsonl_path=checkpoint_jsonl_path,
                report_path=checkpoint_report_path,
                split=split,
                model=model,
                mode=mode,
            )

    rows = merge_rows(rows, order, key="letter_id")
    metadata = {
        "prompt_version": PROMPT_VERSION,
        "pipeline_family": PIPELINE_FAMILY,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "mode": mode,
        "split": split,
        "n_letters": len(letters),
        "n_resumed": n_resumed,
        "dspy_version": getattr(dspy, "__version__", "unknown"),
    }
    metadata["summary"] = summarize_rows(rows)
    return rows, metadata


def summarize_rows(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    summary = verifier_base.summarize_rows(rows)
    summary.update(
        {
            "n_candidates": sum(int(r.get("n_candidates", 0)) for r in rows),
            "n_accepted": sum(int(r.get("n_accepted", 0)) for r in rows),
            "parse_failures": sum(_has_blocking_parse_issue(r.get("parse_errors")) for r in rows),
        }
    )
    return summary


def write_report(
    rows: Sequence[dict[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    summary = metadata.get("summary", {})
    clinical = summary.get("clinical_recovery", {}).get("diagnosis", {})
    source_near = summary.get("source_near", {})
    lines = [
        "# ExECTv2 Diagnosis Candidate Acceptance Gate",
        "",
        f"- JSONL: `{jsonl_path}`",
        f"- Prompt version: `{metadata.get('prompt_version')}`",
        f"- Pipeline family: `{metadata.get('pipeline_family')}`",
        f"- Split: `{metadata.get('split')}`",
        f"- Model: `{metadata.get('model')}`",
        f"- Mode: `{metadata.get('mode')}`",
        f"- Letters: {metadata.get('n_letters')}",
        "",
        "## Gate Summary",
        "",
        f"- Call failures: {summary.get('call_failures', 0)}",
        f"- Parse/schema failures: {summary.get('parse_failures', 0)}",
        f"- Candidate mentions: {summary.get('n_candidates', 0)}",
        f"- Accepted candidates: {summary.get('n_accepted', 0)}",
        f"- Mentions scored: {summary.get('n_mentions_scored', 0)}",
        f"- Evidence-invalid dropped: {summary.get('n_evidence_invalid', 0)}",
        f"- Evidence validity rate: {summary.get('evidence_validity_rate', 0):.4f}",
        "",
        "## Diagnosis Clinical-Recovery Headline",
        "",
        "| Target F1 | F1 | P | R | TP | FP | FN |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        (
            f"| 0.80 | {clinical.get('f1', 0):.3f} | "
            f"{clinical.get('precision', 0):.3f} | {clinical.get('recall', 0):.3f} | "
            f"{clinical.get('tp', 0)} | {clinical.get('fp', 0)} | "
            f"{clinical.get('fn', 0)} |"
        ),
        "",
        "## Source-Near Diagnostic",
        "",
        (
            f"- Overlap F1={source_near.get('overlap', {}).get('f1', 0):.3f} "
            f"R={source_near.get('overlap', {}).get('recall', 0):.3f}"
        ),
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _candidate_family(text: str, evidence: str) -> str:
    groups = reconciler_base._concept_group_ids(text, evidence)
    priority = (
        "generic_epilepsy",
        "structural_symptomatic_family",
        "secondary_generalised_family",
        "tonic_clonic_family",
        "focal_epilepsy_family",
        "other_seizure_type_family",
        "other_diagnosis",
    )
    for group in priority:
        if group in groups:
            return group
    return "other_diagnosis"


def _acceptance_rules() -> list[str]:
    return [
        "Return one decision for every candidate_id. Do not omit candidates.",
        "Do not invent new Diagnosis mentions, new evidence, or edited text.",
        (
            "Accept when the candidate evidence directly asserts the candidate "
            "Diagnosis concept for the patient."
        ),
        (
            "Reject generic epilepsy when the evidence is section context only, "
            "historical/background, a clinic specialty, medication context, or an "
            "inference from EEG/MRI/seizure events."
        ),
        (
            "Reject frequency-only seizure type candidates when the evidence is only "
            "a seizure frequency/count line and not a diagnosis or seizure-type assertion."
        ),
        (
            "Reject symptomatic structural focal epilepsy when it is inferred from a "
            "lesion, stroke, abscess, or MRI finding rather than directly asserted."
        ),
        (
            "Accept focal epilepsy, secondary generalised seizures, and named seizure "
            "types when the letter directly states them as diagnosis/seizure-type facts."
        ),
        (
            "Reject dissociative, non-epileptic, psychogenic, febrile-history, symptom, "
            "aura, and side-effect candidates unless the evidence explicitly asserts an "
            "epileptic Diagnosis concept."
        ),
        "Return exactly one JSON object. No markdown code fences.",
    ]


def _emit_checkpoint(
    rows: Sequence[dict[str, Any]],
    *,
    total: int,
    jsonl_path: Path | None,
    report_path: Path | None,
    split: str,
    model: str,
    mode: str,
) -> None:
    if jsonl_path:
        write_jsonl(rows, jsonl_path)
    metadata = {
        "prompt_version": PROMPT_VERSION,
        "pipeline_family": PIPELINE_FAMILY,
        "model": model,
        "mode": mode,
        "split": split,
        "n_letters": total,
        "summary": summarize_rows(rows),
    }
    if report_path:
        write_report(rows, metadata, report_path, jsonl_path=jsonl_path or Path(""))
    summary = metadata["summary"]
    print(
        json.dumps(
            {
                "processed": len(rows),
                "total": total,
                "call_failures": summary.get("call_failures", 0),
                "parse_failures": summary.get("parse_failures", 0),
                "n_mentions_scored": summary.get("n_mentions_scored", 0),
            },
            sort_keys=True,
        ),
        flush=True,
    )
