"""ExECTv2 LLM-only all-entity single-pass extractor.

One DSPy call per letter emits mentions for all nine ExECTv2 entity types. The
LLM owns the clinical interpretation; deterministic code only validates JSON,
repairs neutral schema mismatches, checks evidence exactness, and scores.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict

from clinical_extraction.core.run_resume import merge_rows, pending_items, read_completed
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    project_cuis,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    ALL_ENTITIES,
    ENTITY_REGISTRY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    _coerce_payload,
    _has_blocking_parse_issue,
    check_evidence,
    repair_attributes,
    write_jsonl,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.json_parse import (
    extract_json_object,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    PHRASE_ONLY,
    benchmark_config_for,
    score_overall,
    semantic_config_for,
    source_near_diagnostic,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

PROMPT_VERSION = "exectv2_llm_only_all_entities_v0.1"
ENTITY_NAMES: tuple[str, ...] = tuple(spec.name for spec in ALL_ENTITIES)

PUBLISHED_PER_ENTITY_ITEM_F1: dict[str, float] = {
    "BirthHistory": 0.97,
    "Diagnosis": 0.85,
    "EpilepsyCause": 0.90,
    "Investigations": 0.95,
    "Onset": 0.96,
    "PatientHistory": 0.78,
    "Prescription": 0.87,
    "SeizureFrequency": 0.66,
    "WhenDiagnosed": 0.91,
}
PUBLISHED_OVERALL = {"per_item": 0.87, "per_letter": 0.90}
TEXT_TARGET_GUIDANCE: dict[str, str] = {
    "BirthHistory": "Compact birth-history phrase, such as premature birth or term birth.",
    "Diagnosis": "Compact diagnostic phrase, not a whole explanatory clause.",
    "EpilepsyCause": "Compact cause, aetiology, syndrome, or risk-factor phrase.",
    "Investigations": "Test phrase such as EEG, MRI, CT, or telemetry; put result in attributes.",
    "Onset": "Phrase naming the condition or seizures whose onset is being dated.",
    "PatientHistory": "Compact clinical concept phrase, not the full historical sentence.",
    "Prescription": (
        "Medication concept/name only where possible; put dose/frequency in attributes."
    ),
    "SeizureFrequency": "Seizure-type anchor only; put count, period, and timing in attributes.",
    "WhenDiagnosed": "Phrase naming the condition whose diagnosis date/age is being stated.",
}


class MentionRecord(BaseModel):
    """One entity mention emitted by the LLM."""

    model_config = ConfigDict(extra="ignore")

    entity: str
    text: str
    attributes: dict[str, Any] = {}
    evidence: str
    confidence: Literal["low", "medium", "high"] = "medium"
    rationale: str = ""


class ExtractionRecord(BaseModel):
    """Full all-entity LLM output for one letter."""

    model_config = ConfigDict(extra="ignore")

    mentions: list[MentionRecord] = []


class ExECTv2AllEntitiesSignature(dspy.Signature):
    """Read one clinical letter and list all requested clinical findings.

    Return exactly one JSON object with a 'mentions' list. No markdown wrapper.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter and task instructions."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            'One strict JSON object: {"mentions": [{"entity": ..., "text": ..., '
            '"attributes": {...}, "evidence": ..., "confidence": ..., '
            '"rationale": ...}, ...]}'
        )
    )


class DspyAllEntitiesExtractor(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(ExECTv2AllEntitiesSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def build_prompt_input(letter: ExectLetter) -> str:
    """Build the all-entity prompt payload from the entity registry."""

    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": (
            "Read the clinical letter and list every mention of the requested "
            "clinical finding types. Return one JSON object with a 'mentions' list."
        ),
        "output_schema": {
            "entity": f"One of: {', '.join(ENTITY_NAMES)}.",
            "text": (
                "The entity-specific short phrase in the letter naming the finding. "
                "Use the text_target guidance below. It must be an exact substring "
                "of the letter."
            ),
            "attributes": (
                "A string-to-string object containing only attributes legal for that "
                "entity and explicitly supported by the letter."
            ),
            "evidence": (
                "The exact clause or sentence from the letter that supports the "
                "entity mention and attributes. Must be copied verbatim."
            ),
            "confidence": (
                "'high': unambiguous finding and attributes. 'medium': finding is "
                "clear but one attribute is vague or approximate. 'low': competing "
                "or ambiguous statements remain."
            ),
            "rationale": "One brief sentence explaining the evidence used.",
        },
        "text_target": _text_target_guidance(),
        "entity_definitions": _entity_definitions(),
        "attribute_vocabulary": _attribute_vocabulary(),
        "worked_examples": _worked_examples(),
        "clinical_rules": [
            "Only emit entities that are explicitly stated in the letter.",
            "Both text and evidence must be exact substrings of the letter.",
            "Do not invent CUI values. If a CUI is not explicitly available, omit it.",
            (
                "For SeizureFrequency, do not emit Certainty or Negation; use only "
                "frequency attributes such as counts, periods, dates, point in time, "
                "or frequency change."
            ),
            (
                "For SeizureFrequency, text is the seizure-type anchor, not the "
                "frequency expression or full sentence."
            ),
            (
                "For prescriptions, text is usually the medication name; dose and "
                "dose frequency belong in attributes."
            ),
            (
                "For non-frequency history counts without a time frame, choose "
                "PatientHistory or Diagnosis as appropriate, not SeizureFrequency."
            ),
            (
                "For investigations, keep the text as the surface test phrase such "
                "as EEG, MRI, or CT, and put normal/abnormal/performed information in "
                "attributes."
            ),
            'If no requested findings are present, return {"mentions": []}.',
            "Return exactly one JSON object. No markdown code fences.",
        ],
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _entity_definitions() -> dict[str, str]:
    return {
        "BirthHistory": "Birth history such as premature or term birth.",
        "Diagnosis": "A diagnosis or diagnostic category, including epilepsy or seizure disorder.",
        "EpilepsyCause": "A stated cause, aetiology, risk factor, or syndrome cause of epilepsy.",
        "Investigations": "EEG, MRI, CT, telemetry, or similar investigation statements.",
        "Onset": "Age, date, or time period when seizures or epilepsy began.",
        "PatientHistory": (
            "Clinical history events such as seizure types, attacks, surgery, or past episodes."
        ),
        "Prescription": "Anti-seizure medication name, dose, or dosing frequency.",
        "SeizureFrequency": (
            "How often a seizure type occurs, including seizure-free duration or frequency change."
        ),
        "WhenDiagnosed": "Age, date, or time period when epilepsy or the condition was diagnosed.",
    }


def _text_target_guidance() -> dict[str, str]:
    return dict(TEXT_TARGET_GUIDANCE)


def _attribute_vocabulary() -> dict[str, dict[str, Any]]:
    vocab: dict[str, dict[str, Any]] = {}
    for spec in ALL_ENTITIES:
        attrs: dict[str, Any] = {}
        for attr in sorted(spec.legal_attributes):
            if attr == "CUIPhrase":
                attrs[attr] = "Clean phrase if explicitly available; otherwise omit."
            elif attr == "CUI":
                attrs[attr] = "UMLS CUI if explicitly available; do not guess."
            elif attr in spec.closed_vocab:
                attrs[attr] = sorted(spec.closed_vocab[attr])
            else:
                attrs[attr] = "string value copied or normalized from the letter."
        vocab[spec.name] = attrs
    return vocab


def _worked_examples() -> list[dict[str, Any]]:
    return [
        {
            "note_fragment": "She has focal epilepsy with 2 focal seizures per month.",
            "correct": [
                {
                    "entity": "Diagnosis",
                    "text": "focal epilepsy",
                    "attributes": {
                        "DiagCategory": "Epilepsy",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                    "evidence": "focal epilepsy",
                    "confidence": "high",
                    "rationale": "The diagnosis is directly stated.",
                },
                {
                    "entity": "SeizureFrequency",
                    "text": "focal seizures",
                    "attributes": {
                        "NumberOfSeizures": "2",
                        "NumberOfTimePeriods": "1",
                        "TimePeriod": "Month",
                    },
                    "evidence": "2 focal seizures per month",
                    "confidence": "high",
                    "rationale": "The seizure type occurs twice per month.",
                },
            ],
        },
        {
            "note_fragment": "Her EEG was abnormal and MRI was normal.",
            "correct": [
                {
                    "entity": "Investigations",
                    "text": "EEG",
                    "attributes": {"EEG_Performed": "Yes", "EEG_Results": "Abnormal"},
                    "evidence": "EEG was abnormal",
                    "confidence": "high",
                    "rationale": "The EEG result is abnormal.",
                },
                {
                    "entity": "Investigations",
                    "text": "MRI",
                    "attributes": {"MRI_Performed": "Yes", "MRI_Results": "Normal"},
                    "evidence": "MRI was normal",
                    "confidence": "high",
                    "rationale": "The MRI result is normal.",
                },
            ],
        },
        {
            "note_fragment": "He takes lamotrigine 200mg twice a day.",
            "correct": {
                "entity": "Prescription",
                "text": "lamotrigine",
                "attributes": {
                    "DrugName": "Lamotrigine",
                    "DrugDose": "200",
                    "DoseUnit": "mg",
                    "Frequency": "2",
                },
                "evidence": "lamotrigine 200mg twice a day",
                "confidence": "high",
                "rationale": "The medication, dose, unit, and frequency are stated.",
            },
        },
    ]


def parse_extraction_json(raw_output: str) -> tuple[ExtractionRecord | None, list[str]]:
    try:
        payload = json.loads(extract_json_object(raw_output))
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json: {exc.msg}"]

    payload, coerce_notes = _coerce_payload(payload)
    try:
        record = ExtractionRecord.model_validate(payload)
    except Exception as exc:
        return None, [f"schema_validation_error: {exc}"]
    return record, list(coerce_notes)


def to_predicted_letter(
    letter_id: str,
    mentions: list[MentionRecord],
    *,
    note_text: str,
) -> tuple[PredictedLetter, list[str]]:
    """Gate entity names, evidence, and attributes; return scorer-compatible output."""

    all_warnings: list[str] = []
    entity_valid: list[MentionRecord] = []
    for mention in mentions:
        if mention.entity not in ENTITY_REGISTRY:
            all_warnings.append(f"dropped_unknown_entity: {mention.entity!r}")
            continue
        entity_valid.append(mention)

    evidence_valid, evidence_invalid, ev_warnings = check_evidence(
        entity_valid, note_text=note_text
    )
    all_warnings.extend(ev_warnings)

    predicted_mentions: list[PredictedMention] = []
    for mention in evidence_valid:
        spec = ENTITY_REGISTRY[mention.entity]
        repaired_attrs, attr_warnings = repair_attributes(dict(mention.attributes), spec=spec)
        all_warnings.extend(f"{mention.entity}: {warning}" for warning in attr_warnings)
        predicted_mentions.append(
            PredictedMention(
                entity=mention.entity,
                text=mention.text,
                attributes=repaired_attrs,
                evidence=mention.evidence,
                confidence=mention.confidence,
                rationale=mention.rationale,
                component_owner="llm_only_all_entities",
            )
        )

    return (
        project_cuis(
            PredictedLetter(
                letter_id=letter_id,
                mentions=tuple(predicted_mentions),
                diagnostics={
                    "prompt_version": PROMPT_VERSION,
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
    program = DspyAllEntitiesExtractor()
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
        prompt_input_json = build_prompt_input(letter)
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
                "model": model,
                "mode": mode,
                "prompt_input_json": prompt_input_json,
                "raw_output": raw_output,
                "call_error": call_error,
                "parse_errors": parse_errors,
                "gate_warnings": gate_warnings,
                "n_mentions_raw": len(mentions),
                "n_mentions_scored": len(predicted_letter.mentions),
                "n_evidence_invalid": len(mentions) - len(predicted_letter.mentions),
                "predicted_mentions": [_mention_to_row(m) for m in predicted_letter.mentions],
                "gold_mentions": [
                    {"entity": a.entity, "text": a.text, "attributes": dict(a.attributes)}
                    for a in letter.annotations
                    if a.entity in ENTITY_REGISTRY
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

    n_mentions_raw = sum(int(r.get("n_mentions_raw", 0)) for r in rows)
    n_evidence_invalid = sum(int(r.get("n_evidence_invalid", 0)) for r in rows)
    gold_letters = _reconstruct_letters(rows, key="gold_mentions")
    pred_letters = _reconstruct_letters(rows, key="predicted_mentions")

    benchmark = score_overall(gold_letters, pred_letters, ENTITY_NAMES, benchmark_config_for)
    semantic = score_overall(gold_letters, pred_letters, ENTITY_NAMES, semantic_config_for)
    phrase = score_overall(gold_letters, pred_letters, ENTITY_NAMES, lambda _e: PHRASE_ONLY)
    source_near = source_near_diagnostic(
        gold_letters,
        pred_letters,
        ENTITY_NAMES,
        semantic_config_for,
    )

    return {
        "examples": n,
        "call_failures": sum(bool(r.get("call_error")) for r in rows),
        "parse_failures": sum(_has_blocking_parse_issue(r.get("parse_errors")) for r in rows),
        "n_mentions_raw": n_mentions_raw,
        "n_mentions_scored": sum(int(r.get("n_mentions_scored", 0)) for r in rows),
        "n_evidence_invalid": n_evidence_invalid,
        "evidence_validity_rate": (
            round((n_mentions_raw - n_evidence_invalid) / n_mentions_raw, 4)
            if n_mentions_raw
            else 1.0
        ),
        "scores": {
            "phrase_only": _overall_to_dict(phrase),
            "semantic": _overall_to_dict(semantic),
            "benchmark": _overall_to_dict(benchmark),
        },
        "diagnostic_ladder": {
            "source_near": _source_near_to_dict(source_near),
        },
        "published_targets": {
            "overall": PUBLISHED_OVERALL,
            "per_entity_per_item": PUBLISHED_PER_ENTITY_ITEM_F1,
        },
    }


def _overall_to_dict(score: Any) -> dict[str, Any]:
    return {
        "per_item": _prf1_to_dict(score.per_item),
        "per_letter": _prf1_to_dict(score.per_letter),
        "per_entity": {
            entity: {
                "per_item": _prf1_to_dict(entity_score.per_item),
                "per_letter": _prf1_to_dict(entity_score.per_letter),
                "published_per_item_target": PUBLISHED_PER_ENTITY_ITEM_F1.get(entity),
            }
            for entity, entity_score in score.per_entity.items()
        },
    }


def _source_near_to_dict(diagnostic: Any) -> dict[str, Any]:
    return {
        "overall": {
            "overlap": _prf1_to_dict(diagnostic.overall.overlap),
            "attribute_agreement_tp": diagnostic.overall.attribute_agreement_tp,
            "attribute_agreement_total": diagnostic.overall.attribute_agreement_total,
            "attribute_agreement_rate": round(diagnostic.overall.attribute_agreement_rate, 4),
        },
        "per_entity": {
            entity: {
                "overlap": _prf1_to_dict(entity_score.overlap),
                "attribute_agreement_tp": entity_score.attribute_agreement_tp,
                "attribute_agreement_total": entity_score.attribute_agreement_total,
                "attribute_agreement_rate": round(entity_score.attribute_agreement_rate, 4),
            }
            for entity, entity_score in diagnostic.per_entity.items()
        },
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


def _mention_to_row(mention: PredictedMention) -> dict[str, Any]:
    return {
        "entity": mention.entity,
        "text": mention.text,
        "attributes": dict(mention.attributes),
        "evidence": mention.evidence,
        "confidence": mention.confidence,
        "rationale": mention.rationale,
    }


def _reconstruct_letters(rows: Sequence[dict[str, Any]], *, key: str) -> list[ExectLetter]:
    letters: list[ExectLetter] = []
    for row in rows:
        annotations = tuple(
            ExectAnnotation(
                entity=str(m["entity"]),
                text=str(m["text"]),
                attributes={str(k): str(v) for k, v in dict(m.get("attributes") or {}).items()},
            )
            for m in (row.get(key) or [])
        )
        if key == "predicted_mentions":
            pred = PredictedLetter(
                letter_id=row["letter_id"],
                mentions=tuple(
                    PredictedMention(
                        entity=a.entity,
                        text=a.text,
                        attributes=dict(a.attributes),
                        evidence="",
                    )
                    for a in annotations
                ),
            )
            letters.append(to_exect_letter(pred))
        else:
            letters.append(
                ExectLetter(
                    letter_id=row["letter_id"],
                    note_text="",
                    annotations=annotations,
                )
            )
    return letters


def write_report(
    rows: Sequence[dict[str, Any]],
    metadata: dict[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    summary = metadata.get("summary") or summarize_rows(rows)
    is_checkpoint = bool(metadata.get("is_checkpoint"))
    total_letters = int(metadata.get("total_letters") or metadata.get("n_letters") or 0)
    lines = [
        "# ExECTv2 LLM-Only All Entities",
        "",
    ]
    if is_checkpoint:
        processed = summary.get("examples", len(rows))
        total = total_letters or processed
        lines.extend(
            [
                f"CHECKPOINT ONLY: processed {processed} / {total} letters",
                "",
            ]
        )
    lines.extend(
        [
            f"- JSONL: `{jsonl_path}`",
            f"- Prompt version: `{metadata.get('prompt_version', PROMPT_VERSION)}`",
            f"- Split: `{metadata.get('split')}`",
            f"- Model: `{metadata.get('model')}`",
            f"- Mode: `{metadata.get('mode')}`",
            f"- Letters: {summary.get('examples', 0)}",
            "",
            "## Gate Summary",
            "",
            f"- Call failures: {summary.get('call_failures', 0)}",
            f"- Parse/schema failures: {summary.get('parse_failures', 0)}",
            f"- Mentions raw: {summary.get('n_mentions_raw', 0)}",
            f"- Mentions scored (evidence-valid): {summary.get('n_mentions_scored', 0)}",
            f"- Evidence-invalid dropped: {summary.get('n_evidence_invalid', 0)}",
            f"- Evidence validity rate: {summary.get('evidence_validity_rate', 0.0):.4f}",
            "",
            "## Overall Scores",
            "",
        ]
    )
    for config_name in ("semantic", "benchmark", "phrase_only"):
        scores = summary.get("scores", {}).get(config_name, {})
        lines.extend(_score_lines(config_name, scores))
    lines.extend(_diagnostic_ladder_lines(summary.get("diagnostic_ladder", {})))
    lines.extend(["", "## Per-Entity Semantic F1", ""])
    semantic_entities = summary.get("scores", {}).get("semantic", {}).get("per_entity", {})
    lines.append("| Entity | Published item F1 | Item F1 | Letter F1 |")
    lines.append("| --- | ---: | ---: | ---: |")
    for entity in ENTITY_NAMES:
        entry = semantic_entities.get(entity, {})
        pi = entry.get("per_item", {})
        pl = entry.get("per_letter", {})
        target = entry.get("published_per_item_target")
        lines.append(f"| {entity} | {target:.2f} | {pi.get('f1', 0):.3f} | {pl.get('f1', 0):.3f} |")
    path.write_text("\n".join(lines), encoding="utf-8")


def _diagnostic_ladder_lines(diagnostic_ladder: dict[str, Any]) -> list[str]:
    source_near = diagnostic_ladder.get("source_near", {})
    overall = source_near.get("overall", {})
    overlap = overall.get("overlap", {})
    lines = [
        "",
        "## Diagnostic Scoring Ladder",
        "",
        "| Layer | Item F1 | TP | FP | FN | Attribute agreement |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
        (
            f"| source_near | {overlap.get('f1', 0):.3f} | "
            f"{overlap.get('tp', 0)} | {overlap.get('fp', 0)} | "
            f"{overlap.get('fn', 0)} | "
            f"{overall.get('attribute_agreement_rate', 0):.3f} "
            f"({overall.get('attribute_agreement_tp', 0)}/"
            f"{overall.get('attribute_agreement_total', 0)}) |"
        ),
        "",
        "| Entity | Source-near F1 | Overlap TP | Attribute agreement |",
        "| --- | ---: | ---: | ---: |",
    ]
    for entity in ENTITY_NAMES:
        entry = source_near.get("per_entity", {}).get(entity, {})
        entity_overlap = entry.get("overlap", {})
        lines.append(
            f"| {entity} | {entity_overlap.get('f1', 0):.3f} | "
            f"{entity_overlap.get('tp', 0)} | "
            f"{entry.get('attribute_agreement_rate', 0):.3f} "
            f"({entry.get('attribute_agreement_tp', 0)}/"
            f"{entry.get('attribute_agreement_total', 0)}) |"
        )
    return lines


def _score_lines(config_name: str, scores: dict[str, Any]) -> list[str]:
    pi = scores.get("per_item", {})
    pl = scores.get("per_letter", {})
    return [
        f"### {config_name}",
        "",
        f"- per-item: P={pi.get('precision', 0):.3f} "
        f"R={pi.get('recall', 0):.3f} "
        f"F1={pi.get('f1', 0):.3f} "
        f"(TP={pi.get('tp', 0)} FP={pi.get('fp', 0)} FN={pi.get('fn', 0)})",
        f"- per-letter: P={pl.get('precision', 0):.3f} "
        f"R={pl.get('recall', 0):.3f} "
        f"F1={pl.get('f1', 0):.3f} "
        f"(TP={pl.get('tp', 0)} FP={pl.get('fp', 0)} FN={pl.get('fn', 0)})",
        "",
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
    summary = summarize_rows(rows)
    if jsonl_path is not None:
        write_jsonl(rows, jsonl_path)
    if report_path is not None and jsonl_path is not None:
        checkpoint_report_path = _checkpoint_report_path(report_path)
        write_report(
            rows,
            {
                "prompt_version": PROMPT_VERSION,
                "split": split,
                "model": model,
                "mode": mode,
                "summary": summary,
                "is_checkpoint": True,
                "total_letters": total,
            },
            checkpoint_report_path,
            jsonl_path=jsonl_path,
        )
    progress = {
        "processed": len(rows),
        "total": total,
        "call_failures": summary.get("call_failures", 0),
        "parse_failures": summary.get("parse_failures", 0),
        "n_mentions_scored": summary.get("n_mentions_scored", 0),
    }
    print(json.dumps(progress, sort_keys=True), file=sys.stderr, flush=True)


def _checkpoint_report_path(path: Path) -> Path:
    if path.stem.endswith("_checkpoint"):
        return path
    return path.with_name(f"{path.stem}_checkpoint{path.suffix}")
