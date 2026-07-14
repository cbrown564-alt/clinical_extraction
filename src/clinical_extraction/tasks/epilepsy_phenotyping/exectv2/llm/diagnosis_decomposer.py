"""Decompose Diagnosis headings and narrative spans for model review."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.mention_pipeline import (
    MentionRecord,
    check_evidence,
    has_blocking_parse_issue,
    parse_extraction_json,
    raw_output_from_adapter_parse_error,
    repair_attributes,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.replay_rows import (
    reconstruct_gold_letters,
    reconstruct_pred_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    PHRASE_ONLY,
    benchmark_config_for,
    score_concept_identity,
    score_entity,
    semantic_config_for,
    source_near_diagnostic,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows as write_jsonl,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

from .prompts.diagnosis_decomposer import loader as prompt_loader

PROMPT_VERSION = "exectv2_hybrid_diagnosis_decomposer_v0.1"
PIPELINE_FAMILY = "exectv2_hybrid_diagnosis_decomposer"
COMPONENT_OWNER = "hybrid_diagnosis_decomposer"
PromptProfile = Literal["full", "qwen_compact"]

_HEADING_RE = re.compile(
    r"\b(diagnosis|impression|epilepsy|classification|syndrome)\b",
    re.IGNORECASE,
)
_SEIZURE_TYPE_RE = re.compile(
    r"\b("
    r"tonic(?:-| )clonic|tonic(?:-| )chronic|focal(?: onset)?|generalised|"
    r"generalized|absence|absences|myoclonic|dyscognitive|complex partial|"
    r"bilateral convulsive|secondary generalised|febrile|dissociative|"
    r"seizures?|epilepsy|JME|juvenile myoclonic"
    r")\b",
    re.IGNORECASE,
)
_NEGATIVE_CONTEXT_RE = re.compile(
    r"\b(no history of|family history|denies|not epileptic|non[- ]epileptic)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class DiagnosisSpan:
    """One exact source span for decomposed Diagnosis review."""

    span_id: str
    evidence: str
    span_role: str
    concept_hints: tuple[str, ...]
    start: int
    end: int

    def as_payload(self) -> dict[str, Any]:
        return {
            "span_id": self.span_id,
            "evidence": self.evidence,
            "span_role": self.span_role,
            "concept_hints": list(self.concept_hints),
        }


class ExECTv2DiagnosisDecomposerSignature(dspy.Signature):
    """Review decomposed Diagnosis candidate spans from one clinical letter."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter, draft Diagnosis mentions, spans, and rules."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            'One strict JSON object: {"mentions": [{"text": ..., '
            '"attributes": {...}, "evidence": ..., "confidence": ..., '
            '"rationale": ...}, ...]}'
        )
    )


class DspyDiagnosisDecomposer(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(ExECTv2DiagnosisDecomposerSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def draft_mentions_by_letter(rows: Sequence[Mapping[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    drafts: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        drafts[str(row["letter_id"])] = [
            {
                "text": str(mention.get("text", "")),
                "attributes": dict(mention.get("attributes") or {}),
                "evidence": str(mention.get("evidence", "")),
                "confidence": str(mention.get("confidence", "")),
                "rationale": str(mention.get("rationale", "")),
            }
            for mention in row.get("predicted_mentions", [])
            if mention.get("entity") == DIAGNOSIS.name
        ]
    return drafts


def read_draft_rows(path: Path | None) -> list[dict[str, Any]]:
    if path is None or not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _attribute_vocabulary() -> dict[str, Any]:
    spec = ENTITY_REGISTRY[DIAGNOSIS.name]
    vocabulary: dict[str, Any] = {}
    for attribute in sorted(spec.legal_attributes):
        if attribute in {"CUI", "CUIPhrase"}:
            vocabulary[attribute] = "Do not emit this; deterministic projection fills it later."
        elif attribute in spec.closed_vocab:
            vocabulary[attribute] = sorted(spec.closed_vocab[attribute])
        else:
            vocabulary[attribute] = "string copied or normalized from the letter."
    return vocabulary


def _mention_to_row(mention: PredictedMention) -> dict[str, Any]:
    return {
        "entity": mention.entity,
        "text": mention.text,
        "attributes": dict(mention.attributes),
        "evidence": mention.evidence,
        "confidence": mention.confidence,
        "rationale": mention.rationale,
    }


def diagnosis_spans_for_letter(
    letter: ExectLetter,
    draft_mentions: Sequence[Mapping[str, Any]] = (),
    *,
    max_spans: int = 30,
) -> list[DiagnosisSpan]:
    text = letter.note_text
    spans: list[DiagnosisSpan] = []
    seen: set[str] = set()

    def add(evidence: str, role: str, start: int | None = None, end: int | None = None) -> None:
        clean = evidence.strip()
        if not clean or clean not in text or _NEGATIVE_CONTEXT_RE.search(clean):
            return
        key = re.sub(r"\s+", " ", clean.lower())
        if key in seen:
            return
        if start is None or end is None:
            start = text.index(clean)
            end = start + len(clean)
        seen.add(key)
        spans.append(
            DiagnosisSpan(
                span_id=f"D{len(spans)}",
                evidence=clean,
                span_role=role,
                concept_hints=tuple(_concept_hints(clean)),
                start=start,
                end=end,
            )
        )

    for draft in draft_mentions:
        evidence = str(draft.get("evidence", "")).strip()
        if evidence:
            add(evidence, "draft-diagnosis")

    for sentence, start, end in _sentence_spans(text):
        role = ""
        if _HEADING_RE.search(sentence):
            role = "diagnosis-heading"
        elif _SEIZURE_TYPE_RE.search(sentence):
            role = "narrative-seizure-type"
        if role:
            add(sentence, role, start, end)

    return spans[:max_spans]


def build_prompt_input(
    letter: ExectLetter,
    draft_mentions: Sequence[Mapping[str, Any]],
    diagnosis_spans: Sequence[DiagnosisSpan] | None = None,
    *,
    prompt_profile: PromptProfile = "full",
) -> str:
    spans = (
        list(diagnosis_spans)
        if diagnosis_spans is not None
        else diagnosis_spans_for_letter(letter, draft_mentions)
    )
    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": (
            "Review the clinical letter, the draft Diagnosis mentions, and the "
            "decomposed diagnosis spans. Return final Diagnosis mentions only. "
            "Use the spans as a checklist for separate clinical assertions; "
            "keep, split, merge, reject, or add mentions based on exact evidence."
        ),
        "decomposition_contract": {
            "diagnosis-heading": (
                "First extract explicit generic epilepsy, syndrome, category, "
                "certainty, and negation assertions from headings/impressions."
            ),
            "narrative-seizure-type": (
                "Then extract named seizure-type diagnoses only when the span "
                "asserts the patient has that seizure type, not mere symptoms or "
                "family history."
            ),
            "reconcile": (
                "Do not deduplicate independently supported assertions. Do split "
                "multi-concept spans: explicit epilepsy plus focal/generalised/"
                "structural/JME concepts should become separate mentions."
            ),
        },
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
        "draft_diagnosis_mentions": list(draft_mentions),
        "diagnosis_candidate_spans": [span.as_payload() for span in spans],
        "attribute_vocabulary": _attribute_vocabulary(),
        "clinical_rules": _clinical_rules(),
        "worked_examples": prompt_loader.load_worked_examples(),
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    if prompt_profile == "qwen_compact":
        payload["output_contract_reminder"] = [
            "Return only one JSON object with exactly the top-level key 'mentions'.",
            "Do not return a top-level list.",
            "Do not use Python dict syntax or single quotes.",
            "Do not include analysis, scratchpad text, or a second corrected object.",
        ]
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _clinical_rules() -> list[str]:
    return [
        (
            "Treat the candidate spans as a clinical checklist, not as predictions. "
            "A span can yield zero, one, or several Diagnosis mentions."
        ),
        (
            "For every diagnosis-heading span, explicitly ask: does this contain "
            "the word epilepsy? If yes, usually emit a generic epilepsy mention "
            "with the certainty supported by that span."
        ),
        (
            "For every diagnosis-heading span, separately ask whether it contains "
            "a specific syndrome or type: focal epilepsy, generalised epilepsy, "
            "temporal lobe epilepsy, structural/symptomatic focal epilepsy, JME, "
            "or intractable epilepsy."
        ),
        (
            "For every narrative-seizure-type span, emit named seizure diagnoses "
            "only for asserted patient seizure types. Reject medication effects, "
            "family history, non-epileptic/dissociative events, and generic "
            "symptoms unless the source asserts an epileptic diagnosis."
        ),
    ] + prompt_loader.load_clinical_rules()


def _sentence_spans(text: str) -> list[tuple[str, int, int]]:
    spans: list[tuple[str, int, int]] = []
    for match in re.finditer(r"[^.!?\n\r]+(?:[.!?]+|$)", text):
        start, _ = match.span()
        raw = match.group(0)
        leading = len(raw) - len(raw.lstrip())
        trailing = len(raw.rstrip())
        clean = raw.strip()
        if clean:
            spans.append((clean, start + leading, start + trailing))
    return spans


def _concept_hints(evidence: str) -> list[str]:
    lower = evidence.lower()
    hints: list[str] = []
    for pattern, hint in [
        (r"\bepilepsy\b", "epilepsy"),
        (r"\bfocal epilepsy\b|\bprobable focal\b|\bfocal onset epilepsy\b", "focal epilepsy"),
        (r"\bgeneralised epilepsy\b|\bgeneralized epilepsy\b", "generalised epilepsy"),
        (r"\btemporal lobe\b", "temporal lobe epilepsy"),
        (r"\bjuvenile myoclonic\b|\bjme\b", "juvenile myoclonic epilepsy"),
        (r"\bstructural\b|\bsymptomatic\b", "symptomatic structural focal epilepsy"),
        (r"\bintractable epilepsy\b", "intractable epilepsy"),
        (r"tonic(?:-| )?(?:clonic|chronic)", "tonic clonic seizures"),
        (r"\bfocal seizures?\b", "focal seizures"),
        (r"\babsence seizures?\b|\babsences\b", "absence seizures"),
        (r"\bmyoclonic jerks\b", "myoclonic jerks"),
        (r"\bdyscognitive seizures?\b", "dyscognitive seizures"),
        (r"\bcomplex partial seizures?\b", "complex partial seizures"),
        (r"\bbilateral convulsive seizure", "bilateral convulsive seizure"),
    ]:
        if re.search(pattern, lower) and hint not in hints:
            hints.append(hint)
    return hints


def to_predicted_letter(
    letter_id: str,
    mentions: list[MentionRecord],
    *,
    note_text: str,
) -> tuple[PredictedLetter, list[str]]:
    all_warnings: list[str] = []
    evidence_valid, evidence_invalid, ev_warnings = check_evidence(mentions, note_text=note_text)
    all_warnings.extend(ev_warnings)

    predicted_mentions: list[PredictedMention] = []
    spec = ENTITY_REGISTRY[DIAGNOSIS.name]
    for mention in evidence_valid:
        attrs = dict(mention.attributes)
        for key in ("CUI", "CUIPhrase"):
            if key in attrs:
                attrs.pop(key)
                all_warnings.append(
                    f"{DIAGNOSIS.name}: dropped_model_supplied_projection_attribute: {key!r}"
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
    draft_rows: Sequence[Mapping[str, Any]] = (),
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
    prompt_profile: PromptProfile = "full",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    program = DspyDiagnosisDecomposer()
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

    drafts = draft_mentions_by_letter(draft_rows)
    order = [letter.letter_id for letter in letters]
    requested = set(order)
    existing_rows, completed = read_completed(
        checkpoint_jsonl_path if resume else None, key="letter_id"
    )
    rows: list[dict[str, Any]] = [r for r in existing_rows if r.get("letter_id") in requested]
    n_resumed = len(rows)
    todo = pending_items(letters, completed, key_of=lambda letter: letter.letter_id)

    for letter in todo:
        draft_mentions = drafts.get(letter.letter_id, [])
        diagnosis_spans = diagnosis_spans_for_letter(letter, draft_mentions)
        prompt_input_json = build_prompt_input(
            letter,
            draft_mentions,
            diagnosis_spans,
            prompt_profile=prompt_profile,
        )
        raw_output = ""
        call_error: str | None = None
        adapter_repair_notes: list[str] = []
        if mode == "live":
            try:
                prediction = program(prompt_input_json=prompt_input_json)
                raw_output = str(prediction.extraction_json)
            except Exception as exc:  # pragma: no cover
                call_error = f"{type(exc).__name__}: {exc}"
                recovered = raw_output_from_adapter_parse_error(call_error)
                if recovered:
                    raw_output = recovered
                    call_error = None
                    adapter_repair_notes.append(
                        "adapter_output_field_repaired: extraction_json_missing"
                    )

        extraction, parse_errors = (
            parse_extraction_json(raw_output) if raw_output else (None, ["not_run"])
        )
        parse_errors = [*adapter_repair_notes, *parse_errors]
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
                "prompt_profile": prompt_profile,
                "pipeline_family": PIPELINE_FAMILY,
                "model": model,
                "mode": mode,
                "draft_mentions": list(draft_mentions),
                "diagnosis_spans": [span.as_payload() for span in diagnosis_spans],
                "prompt_input_json": prompt_input_json,
                "raw_output": raw_output,
                "call_error": call_error,
                "parse_errors": parse_errors,
                "gate_warnings": gate_warnings,
                "n_draft_mentions": len(draft_mentions),
                "n_diagnosis_spans": len(diagnosis_spans),
                "n_mentions_raw": len(mentions),
                "n_mentions_scored": len(predicted_letter.mentions),
                "n_evidence_invalid": len(mentions) - len(predicted_letter.mentions),
                "predicted_mentions": [_mention_to_row(m) for m in predicted_letter.mentions],
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
        "prompt_profile": prompt_profile,
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
    n = len(rows)
    if n == 0:
        return {"examples": 0}
    n_mentions_raw = sum(int(row.get("n_mentions_raw", 0)) for row in rows)
    n_evidence_invalid = sum(int(row.get("n_evidence_invalid", 0)) for row in rows)
    gold_letters = reconstruct_gold_letters(rows, entity_name=DIAGNOSIS.name)
    pred_letters = reconstruct_pred_letters(rows, entity_name=DIAGNOSIS.name)

    phrase = score_entity(gold_letters, pred_letters, DIAGNOSIS.name, PHRASE_ONLY)
    semantic = score_entity(
        gold_letters,
        pred_letters,
        DIAGNOSIS.name,
        semantic_config_for(DIAGNOSIS.name),
    )
    benchmark = score_entity(
        gold_letters,
        pred_letters,
        DIAGNOSIS.name,
        benchmark_config_for(DIAGNOSIS.name),
    )
    source_near = source_near_diagnostic(
        gold_letters,
        pred_letters,
        [DIAGNOSIS.name],
        semantic_config_for,
    ).per_entity[DIAGNOSIS.name]
    clinical = score_concept_identity(
        gold_letters,
        pred_letters,
        DIAGNOSIS.name,
    ).concept_assertion

    return {
        "examples": n,
        "call_failures": sum(bool(row.get("call_error")) for row in rows),
        "parse_failures": sum(has_blocking_parse_issue(row.get("parse_errors")) for row in rows),
        "n_draft_mentions": sum(int(row.get("n_draft_mentions", 0)) for row in rows),
        "n_diagnosis_spans": sum(int(row.get("n_diagnosis_spans", 0)) for row in rows),
        "n_mentions_raw": n_mentions_raw,
        "n_mentions_scored": sum(int(row.get("n_mentions_scored", 0)) for row in rows),
        "n_evidence_invalid": n_evidence_invalid,
        "evidence_validity_rate": (
            round((n_mentions_raw - n_evidence_invalid) / n_mentions_raw, 4)
            if n_mentions_raw
            else 1.0
        ),
        "scores": {
            "phrase_only": _entity_score_to_dict(phrase),
            "semantic": _entity_score_to_dict(semantic),
            "benchmark": _entity_score_to_dict(benchmark),
        },
        "source_near": {
            "overlap": _prf1_to_dict(source_near.overlap),
            "attribute_agreement_tp": source_near.attribute_agreement_tp,
            "attribute_agreement_total": source_near.attribute_agreement_total,
            "attribute_agreement_rate": round(source_near.attribute_agreement_rate, 4),
        },
        "clinical_recovery": {
            "target_headline_f1": 0.80,
            "diagnosis": _prf1_to_dict(clinical),
        },
    }


def _entity_score_to_dict(score: Any) -> dict[str, Any]:
    return {
        "per_item": _prf1_to_dict(score.per_item),
        "per_letter": _prf1_to_dict(score.per_letter),
    }


def _prf1_to_dict(score: Any) -> dict[str, Any]:
    return {
        "precision": round(score.precision, 4),
        "recall": round(score.recall, 4),
        "f1": round(score.f1, 4),
        "tp": score.tp,
        "fp": score.fp,
        "fn": score.fn,
    }


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
        "# ExECTv2 Diagnosis Heading/Narrative Decomposer",
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
        f"- Draft Diagnosis mentions: {summary.get('n_draft_mentions', 0)}",
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
    summary_value = metadata["summary"]
    summary = summary_value if isinstance(summary_value, Mapping) else {}
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
