"""Prescription/Investigations verifier prompt content and scoring."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict, ValidationError

from clinical_extraction.core.run_resume import merge_rows, pending_items, read_completed
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    project_cuis,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    ENTITY_REGISTRY,
    INVESTIGATIONS,
    PRESCRIPTION,
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
    MentionRecord,
    _coerce_payload,
    _extract_json_object,
    _has_blocking_parse_issue,
    check_evidence,
    repair_attributes,
    write_jsonl,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.config import (
    VerifierConfig,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.runner import (
    make_dspy_module,
    mention_to_row,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.prompts.entity_verifier.loader import (
    load_med_inv_clinical_rules,
    load_med_inv_worked_examples,
)

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    PHRASE_ONLY,
    benchmark_config_for,
    score_entity,
    score_investigations_components,
    score_prescription_components,
    semantic_config_for,
    source_near_diagnostic,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

PROMPT_VERSION = "exectv2_llm_med_inv_verifier_v0.1"
PIPELINE_FAMILY = "exectv2_llm_med_inv_verifier"
COMPONENT_OWNER = "llm_med_inv_verifier"
TARGET_ENTITIES: tuple[str, ...] = (PRESCRIPTION.name, INVESTIGATIONS.name)

TASK_TEXT = (
    "Review the clinical letter and draft Prescription/Investigations "
    "mentions from the single structured key-entity extractor. Return final "
    "Prescription and Investigations mentions only. You may keep, delete, "
    "edit, or add mentions, but every final mention must be supported by "
    "exact source evidence."
)

OUTPUT_SCHEMA = {
    "mentions": [
        {
            "entity": "Prescription | Investigations",
            "text": "Clean mention phrase owned by the verifier.",
            "attributes": {
                "Prescription": {
                    "DrugName": "normalized medication name",
                    "DrugDose": "dose number or range",
                    "DoseUnit": "mg | g",
                    "Frequency": "1 | 2 | 3 | As_Required",
                },
                "Investigations": {
                    "MRI_Performed": "Yes | No",
                    "MRI_Results": "Normal | Abnormal | Unknown",
                    "CT_Performed": "Yes | No",
                    "CT_Results": "Normal | Abnormal | Unknown",
                    "EEG_Performed": "Yes | No",
                    "EEG_Results": "Normal | Abnormal | Unknown",
                    "EEG_Type": "Standard | SleepDeprived | VideoTelemetry",
                },
            },
            "evidence": "Exact source substring supporting text and attributes.",
            "confidence": "low | medium | high",
            "rationale": "One brief sentence explaining the decision.",
        }
    ]
}


class MedInvMentionRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    entity: str = ""
    text: str
    attributes: dict[str, Any] = {}
    evidence: str
    confidence: Literal["low", "medium", "high"] = "medium"
    rationale: str = ""


class MedInvExtractionRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    mentions: list[MedInvMentionRecord] = []


class ExECTv2MedInvVerifierSignature(dspy.Signature):
    """Review one clinical letter and draft Prescription/Investigations mentions."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter, draft mentions, and rules."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"mentions\": [{\"entity\": ..., "
            "\"text\": ..., \"attributes\": {...}, \"evidence\": ..., "
            "\"confidence\": ..., \"rationale\": ...}, ...]}"
        )
    )


def _attribute_vocabulary() -> dict[str, Any]:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.prompt import (
        attribute_vocabulary,
    )

    return {entity: attribute_vocabulary(entity) for entity in TARGET_ENTITIES}


def _clinical_rules() -> list[str]:
    return load_med_inv_clinical_rules()


def _worked_examples() -> list[dict[str, Any]]:
    return load_med_inv_worked_examples()


def parse_med_inv_json(raw_output: str) -> tuple[MedInvExtractionRecord | None, list[str]]:
    try:
        payload = json.loads(_extract_json_object(raw_output))
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json: {exc.msg}"]
    payload, coerce_notes = _coerce_payload(payload)
    try:
        return MedInvExtractionRecord.model_validate(payload), list(coerce_notes)
    except ValidationError as exc:
        return None, [f"schema_validation_error: {exc.errors()[0]['msg']}"]


def to_predicted_letter(
    config: VerifierConfig,
    letter_id: str,
    mentions: Sequence[MedInvMentionRecord | MentionRecord],
    *,
    note_text: str,
) -> tuple[PredictedLetter, list[str]]:
    all_warnings: list[str] = []
    evidence_valid, evidence_invalid, ev_warnings = check_evidence(
        mentions, note_text=note_text
    )
    all_warnings.extend(ev_warnings)

    predicted_mentions: list[PredictedMention] = []
    for mention in evidence_valid:
        entity = getattr(mention, "entity", "") or _infer_entity(mention.attributes)
        if entity not in TARGET_ENTITIES:
            all_warnings.append(f"dropped_unsupported_entity: {entity!r}")
            continue
        attrs = dict(mention.attributes)
        for key in ("CUI", "CUIPhrase"):
            if key in attrs:
                attrs.pop(key)
                all_warnings.append(
                    f"{entity}: dropped_model_supplied_projection_attribute: {key!r}"
                )
        repaired_attrs, attr_warnings = repair_attributes(
            attrs,
            spec=ENTITY_REGISTRY[entity],
        )
        all_warnings.extend(f"{entity}: {warning}" for warning in attr_warnings)
        predicted_mentions.append(
            PredictedMention(
                entity=entity,
                text=mention.text,
                attributes=repaired_attrs,
                evidence=mention.evidence,
                confidence=mention.confidence,
                rationale=mention.rationale,
                component_owner=config.component_owner,
            )
        )

    return (
        project_cuis(
            PredictedLetter(
                letter_id=letter_id,
                mentions=tuple(predicted_mentions),
                diagnostics={
                    "prompt_version": config.prompt_version,
                    "pipeline_family": config.pipeline_family,
                    "n_evidence_invalid": len(evidence_invalid),
                    "attribute_warnings": all_warnings,
                },
            )
        ),
        all_warnings,
    )


def summarize_rows(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"examples": 0}
    gold_letters = _reconstruct_gold_letters(rows)
    pred_letters = _reconstruct_pred_letters(rows)
    prescription = score_prescription_components(gold_letters, pred_letters)
    investigations = score_investigations_components(gold_letters, pred_letters)
    source_near = source_near_diagnostic(
        gold_letters,
        pred_letters,
        list(TARGET_ENTITIES),
        semantic_config_for,
    )
    n_mentions_raw = sum(int(r.get("n_mentions_raw", 0)) for r in rows)
    n_evidence_invalid = sum(int(r.get("n_evidence_invalid", 0)) for r in rows)

    return {
        "examples": len(rows),
        "call_failures": sum(bool(r.get("call_error")) for r in rows),
        "parse_failures": sum(_has_blocking_parse_issue(r.get("parse_errors")) for r in rows),
        "n_draft_mentions": sum(int(r.get("n_draft_mentions", 0)) for r in rows),
        "n_mentions_raw": n_mentions_raw,
        "n_mentions_scored": sum(int(r.get("n_mentions_scored", 0)) for r in rows),
        "n_evidence_invalid": n_evidence_invalid,
        "evidence_validity_rate": (
            (n_mentions_raw - n_evidence_invalid) / n_mentions_raw if n_mentions_raw else 1.0
        ),
        "clinical_recovery": {
            PRESCRIPTION.name: prescription.clinical_headline.model_dump(),
            INVESTIGATIONS.name: investigations.clinical_headline.model_dump(),
            "target_headline_f1": 0.8,
        },
        "source_near": {
            entity: source_near.per_entity[entity].model_dump() for entity in TARGET_ENTITIES
        },
        "format_layers": {
            "phrase_only": {
                entity: score_entity(gold_letters, pred_letters, entity, PHRASE_ONLY)
                .per_item.model_dump()
                for entity in TARGET_ENTITIES
            },
            "semantic": {
                entity: score_entity(
                    gold_letters,
                    pred_letters,
                    entity,
                    semantic_config_for(entity),
                )
                .per_item.model_dump()
                for entity in TARGET_ENTITIES
            },
            "benchmark": {
                entity: score_entity(
                    gold_letters,
                    pred_letters,
                    entity,
                    benchmark_config_for(entity),
                )
                .per_item.model_dump()
                for entity in TARGET_ENTITIES
            },
        },
    }


def run_split(
    letters: Sequence[ExectLetter],
    *,
    config: VerifierConfig,
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
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    program = make_dspy_module(config)
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

    drafts = config.draft_mentions_by_letter(draft_rows)
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
        prompt_input_json = config.build_prompt_input(letter, draft_mentions)
        raw_output = ""
        call_error: str | None = None
        if mode == "live":
            try:
                prediction = program(prompt_input_json=prompt_input_json)
                raw_output = str(prediction.extraction_json)
            except Exception as exc:  # pragma: no cover
                call_error = f"{type(exc).__name__}: {exc}"

        extraction, parse_errors = (
            parse_med_inv_json(raw_output) if raw_output else (None, ["not_run"])
        )
        mentions = extraction.mentions if extraction else []
        predicted_letter, gate_warnings = to_predicted_letter(
            config,
            letter.letter_id,
            mentions,
            note_text=letter.note_text,
        )
        rows.append(
            {
                "letter_id": letter.letter_id,
                "split": split,
                "prompt_version": config.prompt_version,
                "pipeline_family": config.pipeline_family,
                "model": model,
                "mode": mode,
                "draft_mentions": list(draft_mentions),
                "prompt_input_json": prompt_input_json,
                "raw_output": raw_output,
                "call_error": call_error,
                "parse_errors": parse_errors,
                "gate_warnings": gate_warnings,
                "n_draft_mentions": len(draft_mentions),
                "n_mentions_raw": len(mentions),
                "n_mentions_scored": len(predicted_letter.mentions),
                "n_evidence_invalid": len(mentions) - len(predicted_letter.mentions),
                "predicted_mentions": [mention_to_row(m) for m in predicted_letter.mentions],
                "gold_mentions": [
                    {"entity": a.entity, "text": a.text, "attributes": dict(a.attributes)}
                    for a in letter.annotations
                    if a.entity in TARGET_ENTITIES
                ],
            }
        )

        if progress_every and (len(rows) - n_resumed) % progress_every == 0:
            _emit_checkpoint(
                config,
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
        "prompt_version": config.prompt_version,
        "pipeline_family": config.pipeline_family,
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


def write_report(
    rows: Sequence[dict[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    summary = metadata.get("summary", {})
    clinical = summary.get("clinical_recovery", {})
    lines = [
        "# ExECTv2 Prescription/Investigations Verifier",
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
        f"- Draft mentions: {summary.get('n_draft_mentions', 0)}",
        f"- Mentions raw: {summary.get('n_mentions_raw', 0)}",
        f"- Mentions scored: {summary.get('n_mentions_scored', 0)}",
        f"- Evidence-invalid dropped: {summary.get('n_evidence_invalid', 0)}",
        f"- Evidence validity rate: {summary.get('evidence_validity_rate', 0):.4f}",
        "",
        "## Clinical-Recovery Headlines",
        "",
        "| Entity | Target F1 | F1 | P | R | TP | FP | FN |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for entity in TARGET_ENTITIES:
        score = clinical.get(entity, {})
        lines.append(
            f"| {entity} | 0.80 | {score.get('f1', 0):.3f} | "
            f"{score.get('precision', 0):.3f} | {score.get('recall', 0):.3f} | "
            f"{score.get('tp', 0)} | {score.get('fp', 0)} | {score.get('fn', 0)} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _infer_entity(attributes: Mapping[str, Any]) -> str:
    keys = set(attributes)
    if keys & {"DrugName", "DrugDose", "DoseUnit", "Frequency"}:
        return PRESCRIPTION.name
    if any(key.startswith(("MRI_", "CT_", "EEG_")) for key in keys):
        return INVESTIGATIONS.name
    return ""


def _reconstruct_gold_letters(rows: Sequence[dict[str, Any]]) -> list[ExectLetter]:
    return [
        ExectLetter(
            letter_id=row["letter_id"],
            note_text="",
            annotations=tuple(
                ExectAnnotation(
                    entity=str(m["entity"]),
                    text=str(m["text"]),
                    attributes={str(k): str(v) for k, v in dict(m.get("attributes") or {}).items()},
                )
                for m in row.get("gold_mentions", [])
            ),
        )
        for row in rows
    ]


def _reconstruct_pred_letters(rows: Sequence[dict[str, Any]]) -> list[ExectLetter]:
    letters: list[ExectLetter] = []
    for row in rows:
        pred = PredictedLetter(
            letter_id=row["letter_id"],
            mentions=tuple(
                PredictedMention(
                    entity=str(m["entity"]),
                    text=str(m["text"]),
                    attributes={str(k): str(v) for k, v in dict(m.get("attributes") or {}).items()},
                    evidence=str(m.get("evidence", "")),
                    confidence=str(m.get("confidence", "medium")),
                    rationale=str(m.get("rationale", "")),
                )
                for m in row.get("predicted_mentions", [])
            ),
        )
        letters.append(to_exect_letter(pred))
    return letters


def _emit_checkpoint(
    config: VerifierConfig,
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
        "prompt_version": config.prompt_version,
        "pipeline_family": config.pipeline_family,
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
