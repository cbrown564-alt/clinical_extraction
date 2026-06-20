"""Diagnosis enumeration recall pass.

Predeclaration:
``docs/experiments/exectv2/predeclarations/
exectv2_diagnosis_enumeration_recall_pass_predeclaration_2026-06-18.md``

The dev140 candidate_miss ledger shows Diagnosis is a candidate-generation
recall gap (gold 346 vs predicted 166 concepts; 75% of misses are seizure-type /
semiology phrasing) that no projection or semantic layer recovers. This pass
exhaustively enumerates every seizure-type, semiology, and epilepsy-syndrome
mention in a letter as a Diagnosis candidate, deliberately without
de-duplicating against SeizureFrequency or collapsing repeated mentions.

Ownership: clean ``llm_first``. The LLM does candidate generation, reasoning,
and selection; deterministic code only validates evidence, repairs schema, and
projects CUI/certainty/format. No deterministic concept editing is performed,
per the predeclaration's stop rules.
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_diagnosis_decomposer as decomposer,
    llm_diagnosis_verifier as verifier_base,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    MentionRecord,
    check_evidence,
    parse_extraction_json,
    repair_attributes,
    write_jsonl,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

PROMPT_VERSION = "exectv2_llm_diagnosis_enumeration_v0.1"
PIPELINE_FAMILY = "exectv2_llm_diagnosis_enumeration"
COMPONENT_OWNER = "llm_first"


class ExECTv2DiagnosisEnumerationSignature(dspy.Signature):
    """Enumerate every Diagnosis concept asserted in one clinical letter."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter, candidate spans, and enumeration rules."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"mentions\": [{\"text\": ..., "
            "\"attributes\": {...}, \"evidence\": ..., \"confidence\": ..., "
            "\"rationale\": ...}, ...]}"
        )
    )


class DspyDiagnosisEnumeration(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(ExECTv2DiagnosisEnumerationSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def build_prompt_input(
    letter: ExectLetter,
    diagnosis_spans: Sequence[decomposer.DiagnosisSpan] | None = None,
) -> str:
    spans = (
        list(diagnosis_spans)
        if diagnosis_spans is not None
        else decomposer.diagnosis_spans_for_letter(letter, ())
    )
    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": (
            "Enumerate EVERY Diagnosis concept the letter asserts the patient "
            "has. Diagnosis covers named epilepsy syndromes/categories AND every "
            "named seizure type the patient experiences (these are the gold "
            "Diagnosis concepts in this benchmark). Be exhaustive: under-listing "
            "is the dominant error. Return one mention per distinct asserted "
            "concept, with exact source evidence."
        ),
        "enumeration_contract": {
            "seizure_types_are_diagnoses": (
                "Treat each named seizure type the patient has as a separate "
                "Diagnosis: focal seizures, focal motor seizures, tonic-clonic "
                "seizures, generalised tonic-clonic seizures, secondary "
                "generalised seizures, complex/simple partial seizures, absence "
                "seizures, myoclonic seizures, focal to bilateral convulsive "
                "seizures, seizures with altered awareness, etc."
            ),
            "syndromes_and_categories": (
                "Also emit explicit epilepsy/syndrome/category assertions: "
                "epilepsy, focal epilepsy, generalised epilepsy, temporal lobe "
                "epilepsy, juvenile myoclonic epilepsy, symptomatic/structural "
                "focal epilepsy, intractable epilepsy."
            ),
            "do_not_deduplicate": (
                "Do NOT drop a seizure-type Diagnosis because the same phrase "
                "also describes seizure frequency. Do NOT merge an explicit "
                "epilepsy assertion with a co-located seizure type; emit both. "
                "If the letter asserts the same concept in two distinct "
                "statements, emit it for each independently supported statement."
            ),
            "stay_grounded": (
                "Only emit concepts the source asserts the patient has. Reject "
                "family history, explicitly negated diagnoses, non-epileptic / "
                "dissociative events, medication or symptom descriptions that are "
                "not asserted seizure-type or epilepsy diagnoses. Every mention "
                "must carry exact source-substring evidence."
            ),
        },
        "output_schema": {
            "mentions": [
                {
                    "text": "Clean core Diagnosis concept phrase.",
                    "attributes": {
                        "DiagCategory": "Epilepsy | MultipleSeizures | SingleSeizure",
                        "Certainty": "1 | 2 | 3 | 4 | 5",
                        "Negation": "Affirmed | Negated",
                    },
                    "evidence": "Exact source substring supporting text and attributes.",
                    "confidence": "low | medium | high",
                    "rationale": "One brief sentence explaining the decision.",
                }
            ]
        },
        "diagnosis_candidate_spans": [span.as_payload() for span in spans],
        "attribute_vocabulary": verifier_base._attribute_vocabulary(),
        "clinical_rules": _clinical_rules(),
        "worked_examples": verifier_base._worked_examples(),
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _clinical_rules() -> list[str]:
    return [
        (
            "Recall is the objective. The most common failure on this task is "
            "listing only one or two diagnoses when the letter asserts several "
            "named seizure types. Re-read for every seizure type."
        ),
        (
            "Each named seizure type the patient is described as having is a "
            "separate Diagnosis mention, even when the same phrase carries "
            "frequency or count information."
        ),
        (
            "For each diagnosis-heading or impression span, ask separately: does "
            "it assert generic epilepsy? a specific syndrome (focal, generalised, "
            "temporal lobe, JME, symptomatic/structural focal, intractable)? Emit "
            "each asserted concept."
        ),
        (
            "Do not invent concepts absent from the text, and do not emit a "
            "mention whose evidence is not an exact source substring."
        ),
    ] + verifier_base._clinical_rules()


def to_predicted_letter(
    letter_id: str,
    mentions: list[MentionRecord],
    *,
    note_text: str,
) -> tuple[PredictedLetter, list[str]]:
    all_warnings: list[str] = []
    evidence_valid, evidence_invalid, ev_warnings = check_evidence(
        mentions, note_text=note_text
    )
    all_warnings.extend(ev_warnings)

    predicted_mentions: list[PredictedMention] = []
    spec = ENTITY_REGISTRY[DIAGNOSIS.name]
    for mention in evidence_valid:
        attrs = dict(mention.attributes)
        for key in ("CUI", "CUIPhrase"):
            if key in attrs:
                attrs.pop(key)
                all_warnings.append(
                    f"{DIAGNOSIS.name}: "
                    f"dropped_model_supplied_projection_attribute: {key!r}"
                )
        repaired_attrs, attr_warnings = repair_attributes(attrs, spec=spec)
        all_warnings.extend(f"{DIAGNOSIS.name}: {warning}" for warning in attr_warnings)
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
                    "attribute_warnings": all_warnings,
                },
            )
        ),
        all_warnings,
    )


def run_split(
    letters: Sequence[ExectLetter],
    *,
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
    program = DspyDiagnosisEnumeration()
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

    order = [letter.letter_id for letter in letters]
    requested = set(order)
    existing_rows, completed = read_completed(
        checkpoint_jsonl_path if resume else None, key="letter_id"
    )
    rows: list[dict[str, Any]] = [r for r in existing_rows if r.get("letter_id") in requested]
    n_resumed = len(rows)
    todo = pending_items(letters, completed, key_of=lambda letter: letter.letter_id)

    for letter in todo:
        diagnosis_spans = decomposer.diagnosis_spans_for_letter(letter, ())
        prompt_input_json = build_prompt_input(letter, diagnosis_spans)
        raw_output = ""
        call_error: str | None = None
        if mode == "live":
            try:
                prediction = program(prompt_input_json=prompt_input_json)
                raw_output = str(prediction.extraction_json)
            except Exception as exc:  # pragma: no cover - network/runtime guard
                call_error = f"{type(exc).__name__}: {exc}"

        extraction, parse_errors = (
            parse_extraction_json(raw_output) if raw_output else (None, ["not_run"])
        )
        mentions = extraction.mentions if extraction else []
        predicted_letter, gate_warnings = to_predicted_letter(
            letter.letter_id,
            mentions,
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
                "diagnosis_spans": [span.as_payload() for span in diagnosis_spans],
                "prompt_input_json": prompt_input_json,
                "raw_output": raw_output,
                "call_error": call_error,
                "parse_errors": parse_errors,
                "gate_warnings": gate_warnings,
                "n_diagnosis_spans": len(diagnosis_spans),
                "n_mentions_raw": len(mentions),
                "n_mentions_scored": len(predicted_letter.mentions),
                "n_evidence_invalid": len(mentions) - len(predicted_letter.mentions),
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
        "component_owner": COMPONENT_OWNER,
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
    if rows:
        summary["n_diagnosis_spans"] = sum(int(r.get("n_diagnosis_spans", 0)) for r in rows)
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
        "# ExECTv2 Diagnosis Enumeration Recall Pass",
        "",
        f"- JSONL: `{jsonl_path}`",
        f"- Prompt version: `{metadata.get('prompt_version')}`",
        f"- Pipeline family: `{metadata.get('pipeline_family')}`",
        f"- Component owner: `{metadata.get('component_owner', COMPONENT_OWNER)}`",
        f"- Split: `{metadata.get('split')}`",
        f"- Model: `{metadata.get('model')}`",
        f"- Mode: `{metadata.get('mode')}`",
        f"- Letters: {metadata.get('n_letters')}",
        "",
        "## Gate Summary",
        "",
        f"- Call failures: {summary.get('call_failures', 0)}",
        f"- Parse/schema failures: {summary.get('parse_failures', 0)}",
        f"- Diagnosis spans: {summary.get('n_diagnosis_spans', 0)}",
        f"- Mentions raw: {summary.get('n_mentions_raw', 0)}",
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
        "component_owner": COMPONENT_OWNER,
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
