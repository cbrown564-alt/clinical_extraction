"""Diagnosis reconciler over verifier and decomposer candidate outputs."""

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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    canonicalize_concept,
    normalize_phrase,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_diagnosis_verifier as verifier_base,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    MentionRecord,
    _has_blocking_parse_issue,
    check_evidence,
    parse_extraction_json,
    repair_attributes,
    write_jsonl,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

PROMPT_VERSION = "exectv2_hybrid_diagnosis_reconciler_v0.2"
PIPELINE_FAMILY = "exectv2_hybrid_diagnosis_reconciler"
COMPONENT_OWNER = "hybrid_diagnosis_reconciler"


class ExECTv2DiagnosisReconcilerSignature(dspy.Signature):
    """Reconcile high-precision and high-recall Diagnosis candidates."""

    prompt_input_json: str = dspy.InputField(
        desc=(
            "JSON containing one letter, verifier candidates, decomposer "
            "candidates, spans, and rules."
        )
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"mentions\": [{\"text\": ..., "
            "\"attributes\": {...}, \"evidence\": ..., \"confidence\": ..., "
            "\"rationale\": ...}, ...]}"
        )
    )


class DspyDiagnosisReconciler(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(ExECTv2DiagnosisReconcilerSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def read_rows(path: Path | None) -> list[dict[str, Any]]:
    if path is None or not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def mentions_by_letter(rows: Sequence[Mapping[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        out[str(row["letter_id"])] = [
            {
                "text": str(m.get("text", "")),
                "attributes": dict(m.get("attributes") or {}),
                "evidence": str(m.get("evidence", "")),
                "confidence": str(m.get("confidence", "")),
                "rationale": str(m.get("rationale", "")),
            }
            for m in row.get("predicted_mentions", [])
            if m.get("entity", DIAGNOSIS.name) == DIAGNOSIS.name
        ]
    return out


def spans_by_letter(rows: Sequence[Mapping[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    return {
        str(row["letter_id"]): [dict(span) for span in row.get("diagnosis_spans", [])]
        for row in rows
    }


def build_prompt_input(
    letter: ExectLetter,
    verifier_mentions: Sequence[Mapping[str, Any]],
    decomposer_mentions: Sequence[Mapping[str, Any]],
    diagnosis_spans: Sequence[Mapping[str, Any]],
) -> str:
    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": (
            "Reconcile two Diagnosis candidate lists for one clinical letter. "
            "The verifier list is usually higher precision. The decomposer list "
            "is usually higher recall but over-emits seizure-type diagnoses. "
            "Return the final Diagnosis mentions only."
        ),
        "candidate_sources": {
            "verifier_mentions": list(verifier_mentions),
            "decomposer_mentions": list(decomposer_mentions),
            "diagnosis_candidate_spans": list(diagnosis_spans),
        },
        "candidate_concept_groups": candidate_concept_groups(
            verifier_mentions=verifier_mentions,
            decomposer_mentions=decomposer_mentions,
            diagnosis_spans=diagnosis_spans,
        ),
        "output_schema": {
            "mentions": [
                {
                    "text": "Clean core Diagnosis concept phrase owned by you.",
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
        "reconciliation_rules": _reconciliation_rules(),
        "attribute_vocabulary": verifier_base._attribute_vocabulary(),
        "clinical_rules": verifier_base._clinical_rules(),
        "worked_examples": verifier_base._worked_examples(),
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def candidate_concept_groups(
    *,
    verifier_mentions: Sequence[Mapping[str, Any]],
    decomposer_mentions: Sequence[Mapping[str, Any]],
    diagnosis_spans: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Group candidate evidence by the clinical decisions left after v0.1."""

    grouped: dict[str, list[dict[str, Any]]] = {
        group_id: []
        for group_id in (
            "generic_epilepsy",
            "focal_epilepsy_family",
            "tonic_clonic_family",
            "secondary_generalised_family",
            "structural_symptomatic_family",
            "other_seizure_type_family",
            "other_diagnosis",
        )
    }
    for source, mentions in (
        ("verifier", verifier_mentions),
        ("decomposer", decomposer_mentions),
    ):
        for index, mention in enumerate(mentions):
            text = str(mention.get("text", ""))
            evidence = str(mention.get("evidence", ""))
            candidate = _group_candidate(
                source=source,
                candidate_id=f"{source[0].upper()}{index}",
                text=text,
                evidence=evidence,
                attributes=dict(mention.get("attributes") or {}),
            )
            for group_id in _concept_group_ids(text, evidence):
                grouped[group_id].append(candidate)

    for index, span in enumerate(diagnosis_spans):
        hints = [str(hint) for hint in span.get("concept_hints", [])]
        evidence = str(span.get("evidence", ""))
        text = _span_group_text(hints, evidence)
        candidate = _group_candidate(
            source="span",
            candidate_id=str(span.get("span_id") or f"S{index}"),
            text=text,
            evidence=evidence,
            attributes={},
            span_role=str(span.get("span_role", "")),
            concept_hints=hints,
        )
        for group_id in _concept_group_ids(text, evidence):
            grouped[group_id].append(candidate)

    return [
        {
            "group_id": group_id,
            "decision_question": _group_decision_question(group_id),
            "candidates": candidates,
        }
        for group_id, candidates in grouped.items()
        if candidates
    ]


def _group_candidate(
    *,
    source: str,
    candidate_id: str,
    text: str,
    evidence: str,
    attributes: Mapping[str, Any],
    span_role: str | None = None,
    concept_hints: Sequence[str] = (),
) -> dict[str, Any]:
    candidate: dict[str, Any] = {
        "source": source,
        "candidate_id": candidate_id,
        "text": text,
        "canonical_text": canonicalize_concept(text),
        "certainty": str(attributes.get("Certainty", "")),
        "negation": str(attributes.get("Negation", "")),
        "evidence": evidence,
    }
    if span_role:
        candidate["span_role"] = span_role
    if concept_hints:
        candidate["concept_hints"] = list(concept_hints)
    return candidate


def _span_group_text(hints: Sequence[str], evidence: str) -> str:
    for hint in hints:
        if hint:
            return hint
    return evidence


def _concept_group_ids(text: str, evidence: str) -> tuple[str, ...]:
    haystack = normalize_phrase(f"{text} {evidence}")
    concept = canonicalize_concept(text)
    groups: list[str] = []
    if concept == "epilepsy":
        return ("generic_epilepsy",)
    if "epilepsy" in haystack and not any(
        term in haystack for term in ("focal", "generalised", "generalized")
    ):
        groups.append("generic_epilepsy")
    if "secondary generalised" in haystack or "secondary generalized" in haystack:
        groups.append("secondary_generalised_family")
    if "tonic clonic" in haystack or "tonic chronic" in haystack:
        groups.append("tonic_clonic_family")
    if "symptomatic" in haystack or "structural" in haystack:
        groups.append("structural_symptomatic_family")
    if any(
        phrase in haystack
        for phrase in (
            "focal epilepsy",
            "focal onset",
            "temporal lobe epilepsy",
            "probable focal",
            "temporal",
        )
    ):
        groups.append("focal_epilepsy_family")
    if any(
        term in haystack
        for term in (
            "focal seizures",
            "absence",
            "complex partial",
            "dyscognitive",
            "myoclonic",
            "convulsive seizure",
        )
    ):
        groups.append("other_seizure_type_family")
    return tuple(dict.fromkeys(groups or ["other_diagnosis"]))


def _group_decision_question(group_id: str) -> str:
    questions = {
        "generic_epilepsy": (
            "Is generic epilepsy directly asserted for the patient, historical/background, "
            "section context only, or reject?"
        ),
        "focal_epilepsy_family": "Which focal-family Diagnosis concepts are directly asserted?",
        "tonic_clonic_family": (
            "Which tonic-clonic concepts are diagnosis assertions rather than frequency-only facts?"
        ),
        "secondary_generalised_family": (
            "Which secondary-generalised concepts are directly asserted and should be preserved?"
        ),
        "structural_symptomatic_family": (
            "Is symptomatic or structural focal epilepsy directly asserted rather than inferred?"
        ),
        "other_seizure_type_family": (
            "Which named seizure-type concepts are true Diagnosis assertions?"
        ),
        "other_diagnosis": "Which remaining Diagnosis concepts are directly asserted?",
    }
    return questions[group_id]


def _reconciliation_rules() -> list[str]:
    return [
        (
            "Use verifier_mentions as the starting point. Add decomposer-only "
            "mentions only when the exact evidence independently asserts a "
            "Diagnosis concept, not merely a seizure-frequency line."
        ),
        (
            "Classify each candidate_concept_groups bucket before emitting final "
            "mentions. The groups are attention scaffolding, not predictions."
        ),
        (
            "For generic epilepsy, choose one of: patient-level established, "
            "historical/background, section context only, or reject. Emit generic "
            "epilepsy only for patient-level established evidence that explicitly "
            "contains the word epilepsy."
        ),
        (
            "Recover a specific epilepsy syndrome from decomposer candidates only "
            "when the span states epilepsy plus the type/syndrome, such as focal "
            "epilepsy, generalised epilepsy, temporal lobe epilepsy, structural "
            "focal epilepsy, JME, or intractable epilepsy."
        ),
        (
            "Be conservative with seizure-type-only decomposer candidates. Keep "
            "tonic clonic, absence, focal, dyscognitive, myoclonic, or complex "
            "partial seizure diagnoses only when the source asserts them as the "
            "patient's seizure diagnosis/type, not just an episode count, aura, "
            "symptom, family history, or non-epileptic event."
        ),
        (
            "Group tonic-clonic, generalised tonic-clonic, and tonic chronic spellings "
            "before choosing the normalized concept. Do not emit both a broad tonic "
            "clonic concept and a longer variant unless separate evidence requires it."
        ),
        (
            "Preserve secondary generalised seizure concepts when they are directly "
            "asserted; do not collapse them into tonic clonic seizures unless the "
            "source separately asserts tonic-clonic seizures."
        ),
        (
            "Do not infer symptomatic structural focal epilepsy from MRI, stroke, "
            "tumour, abscess, or lesion context alone. Emit it only when the evidence "
            "directly asserts symptomatic/structural epilepsy."
        ),
        (
            "If verifier and decomposer disagree on certainty, choose the certainty "
            "supported by hedging in the exact evidence: established/unqualified=5, "
            "probable/likely=4, possible/query/suspected=3."
        ),
        (
            "Drop decomposer-only mentions for dissociative seizures, febrile "
            "history, generic symptoms, medication side effects, and unlabelled "
            "events unless the source clearly asserts a scored epileptic Diagnosis."
        ),
    ]


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
    program = DspyDiagnosisReconciler()
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

    verifier_by_id = mentions_by_letter(verifier_rows)
    decomposer_by_id = mentions_by_letter(decomposer_rows)
    spans_by_id = spans_by_letter(decomposer_rows)
    order = [letter.letter_id for letter in letters]
    requested = set(order)
    existing_rows, completed = read_completed(
        checkpoint_jsonl_path if resume else None, key="letter_id"
    )
    rows: list[dict[str, Any]] = [r for r in existing_rows if r.get("letter_id") in requested]
    n_resumed = len(rows)
    todo = pending_items(letters, completed, key_of=lambda letter: letter.letter_id)

    for letter in todo:
        verifier_mentions = verifier_by_id.get(letter.letter_id, [])
        decomposer_mentions = decomposer_by_id.get(letter.letter_id, [])
        diagnosis_spans = spans_by_id.get(letter.letter_id, [])
        prompt_input_json = build_prompt_input(
            letter,
            verifier_mentions,
            decomposer_mentions,
            diagnosis_spans,
        )
        raw_output = ""
        call_error: str | None = None
        if mode == "live":
            try:
                prediction = program(prompt_input_json=prompt_input_json)
                raw_output = str(prediction.extraction_json)
            except Exception as exc:  # pragma: no cover
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
                "verifier_mentions": list(verifier_mentions),
                "decomposer_mentions": list(decomposer_mentions),
                "diagnosis_spans": list(diagnosis_spans),
                "prompt_input_json": prompt_input_json,
                "raw_output": raw_output,
                "call_error": call_error,
                "parse_errors": parse_errors,
                "gate_warnings": gate_warnings,
                "n_verifier_mentions": len(verifier_mentions),
                "n_decomposer_mentions": len(decomposer_mentions),
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
        summary.update(
            {
                "n_verifier_mentions": sum(int(r.get("n_verifier_mentions", 0)) for r in rows),
                "n_decomposer_mentions": sum(
                    int(r.get("n_decomposer_mentions", 0)) for r in rows
                ),
                "n_diagnosis_spans": sum(int(r.get("n_diagnosis_spans", 0)) for r in rows),
                "parse_failures": sum(
                    _has_blocking_parse_issue(r.get("parse_errors")) for r in rows
                ),
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
        "# ExECTv2 Diagnosis Decomposition Reconciler",
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
        f"- Verifier candidate mentions: {summary.get('n_verifier_mentions', 0)}",
        f"- Decomposer candidate mentions: {summary.get('n_decomposer_mentions', 0)}",
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
