"""Run orchestration, scoring summaries, and report/metadata assembly.

Pure relocation from ``llm_only_key_entities_structured``. No logic changes.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy

from clinical_extraction.core.local_structured_output import (
    FormatOnlyJsonRetry,
    assess_structured_output,
    build_format_only_retry_input,
    validate_format_retry,
)
from clinical_extraction.core.run_resume import merge_rows, pending_items, read_completed
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.mention_pipeline import (
    has_blocking_parse_issue,
    is_terminal_provider_error,
    raw_output_from_adapter_parse_error,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    PHRASE_ONLY,
    benchmark_config_for,
    score_concept_identity,
    score_frequency_state,
    score_investigations_components,
    score_overall,
    score_prescription_components,
    semantic_config_for,
    source_near_diagnostic,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

from .constants import (
    KEY_ENTITY_ITEM_F1_TARGET,
    KEY_ENTITY_NAMES,
    PIPELINE_FAMILY,
    PROMPT_VERSION,
    PUBLISHED_PER_ENTITY_ITEM_F1,
    PromptProfile,
    prompt_version_for,
)
from .parsing import (
    flatten_events,
    parse_structured_events_json,
)
from .projection import (
    to_predicted_letter,
)
from .prompt_builders import (
    build_prompt_input,
)
from .records import format_retry_schema_for
from .signatures import (
    DspyKeyEntitiesStructuredExtractor,
)

_is_terminal_provider_error = is_terminal_provider_error


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
    api_key: str | None = None,
    timeout: int | None = None,
    progress_every: int | None = None,
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
    resume: bool = False,
    prompt_profile: PromptProfile = "full",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Compatibility facade; the one-call producer lives in orchestration."""

    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.contracts import (
        StructuredMethodConfig,
    )

    from ....orchestration import structured_one_call

    return structured_one_call.run_split(
        letters,
        split=split,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        mode=mode,
        dspy_cache=dspy_cache,
        api_base=api_base,
        api_key=api_key,
        timeout=timeout,
        progress_every=progress_every,
        checkpoint_jsonl_path=checkpoint_jsonl_path,
        checkpoint_report_path=checkpoint_report_path,
        resume=resume,
        config=StructuredMethodConfig.selected(prompt_profile=prompt_profile),
        model_builder=build_dspy_lm,
        program_factory=DspyKeyEntitiesStructuredExtractor,
        format_retry_factory=FormatOnlyJsonRetry,
    )


def _legacy_run_split(
    letters: Sequence[ExectLetter],
    *,
    split: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
    dspy_cache: bool = True,
    api_base: str | None = None,
    api_key: str | None = None,
    timeout: int | None = None,
    progress_every: int | None = None,
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
    resume: bool = False,
    prompt_profile: PromptProfile = "full",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    program = DspyKeyEntitiesStructuredExtractor()
    format_retry_program = FormatOnlyJsonRetry()
    if mode == "live":
        dspy.configure(
            lm=build_dspy_lm(
                model,
                temperature=temperature,
                max_tokens=max_tokens,
                cache=dspy_cache,
                api_base=api_base,
                api_key=api_key,
                timeout=timeout,
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
    prompt_version = prompt_version_for(prompt_profile)

    for letter in todo:
        prompt_input_json = build_prompt_input(letter, prompt_profile=prompt_profile)
        raw_output = ""
        call_error: str | None = None
        adapter_repair_notes: list[str] = []
        if mode == "live":
            try:
                prediction = program(prompt_input_json=prompt_input_json)
                raw_output = str(prediction.extraction_json)
            except Exception as exc:  # pragma: no cover
                call_error = f"{type(exc).__name__}: {exc}"
                if _is_terminal_provider_error(call_error):
                    raise RuntimeError(
                        "Terminal model-provider error; stopping before recording "
                        "placeholder rows: " + call_error
                    ) from exc
                recovered = raw_output_from_adapter_parse_error(call_error)
                if recovered:
                    raw_output = recovered
                    call_error = None
                    adapter_repair_notes.append(
                        "adapter_output_field_repaired: extraction_json_missing"
                    )

        record, parse_errors = (
            parse_structured_events_json(raw_output, prompt_version=prompt_version)
            if raw_output
            else (None, ["not_run"])
        )
        initial_parse_errors = list(parse_errors)
        assessment = assess_structured_output(
            raw_output, initial_parse_errors, call_error=call_error
        )
        format_retry_output = ""
        format_retry_notes: list[str] = []
        if mode == "live" and model.startswith("ollama_chat/") and assessment.retry_eligible:
            try:
                retry_prediction = format_retry_program(
                    retry_input_json=build_format_only_retry_input(
                        malformed_output=raw_output,
                        schema=format_retry_schema_for(prompt_version),
                    )
                )
                format_retry_output = str(retry_prediction.repaired_json)
                retry_validation = validate_format_retry(
                    raw_output, initial_parse_errors, format_retry_output
                )
                retry_record, retry_parse_errors = parse_structured_events_json(
                    format_retry_output, prompt_version=prompt_version
                )
                format_retry_notes = list(retry_validation.notes)
                if retry_validation.accepted and retry_record is not None:
                    record = retry_record
                    parse_errors = [*retry_parse_errors, *format_retry_notes]
                elif retry_validation.accepted:
                    format_retry_notes = ["format_retry_rejected: schema_validation"]
                    parse_errors = [*initial_parse_errors, *format_retry_notes]
                else:
                    parse_errors = [*initial_parse_errors, *format_retry_notes]
            except Exception as exc:  # pragma: no cover - live provider behavior.
                format_retry_notes = [
                    f"format_retry_rejected: provider_error:{type(exc).__name__}"
                ]
                parse_errors = [*initial_parse_errors, *format_retry_notes]
        parse_errors = [*adapter_repair_notes, *parse_errors]
        mentions = flatten_events(record) if record else []
        predicted_letter, gate_warnings = to_predicted_letter(
            letter.letter_id,
            mentions,
            note_text=letter.note_text,
            prompt_version=prompt_version,
        )

        rows.append(
            {
                "letter_id": letter.letter_id,
                "split": split,
                "prompt_version": prompt_version,
                "prompt_profile": prompt_profile,
                "pipeline_family": PIPELINE_FAMILY,
                "model": model,
                "mode": mode,
                "prompt_input_json": prompt_input_json,
                "raw_output": raw_output,
                "call_error": call_error,
                "initial_parse_errors": initial_parse_errors,
                "parse_errors": parse_errors,
                "structured_output_failure_codes": list(assessment.failure_codes),
                "format_retry_output": format_retry_output,
                "format_retry_notes": format_retry_notes,
                "gate_warnings": gate_warnings,
                "n_events_raw": len(record.clinical_events) if record else 0,
                "n_mentions_raw": len(mentions),
                "n_mentions_scored": len(predicted_letter.mentions),
                "n_evidence_invalid": len(mentions) - len(predicted_letter.mentions),
                "structured_events": [
                    event.model_dump() for event in (record.clinical_events if record else [])
                ],
                "patient_history": [
                    item.model_dump() for item in (record.patient_history if record else [])
                ],
                "medication_history": [
                    item.model_dump() for item in (record.medication_history if record else [])
                ],
                "predicted_mentions": [_mention_to_row(m) for m in predicted_letter.mentions],
                "gold_mentions": [
                    {"entity": a.entity, "text": a.text, "attributes": dict(a.attributes)}
                    for a in letter.annotations
                    if a.entity in KEY_ENTITY_NAMES
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
                prompt_version=prompt_version,
                prompt_profile=prompt_profile,
            )

    rows = merge_rows(rows, order, key="letter_id")
    metadata = {
        "prompt_version": prompt_version,
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

    n_mentions_raw = sum(int(r.get("n_mentions_raw", 0)) for r in rows)
    n_evidence_invalid = sum(int(r.get("n_evidence_invalid", 0)) for r in rows)
    n_patient_history = sum(len(r.get("patient_history", [])) for r in rows)
    n_medication_history = sum(len(r.get("medication_history", [])) for r in rows)
    gold_letters = _reconstruct_letters(rows, key="gold_mentions")
    pred_letters = _reconstruct_letters(rows, key="predicted_mentions")

    benchmark = score_overall(gold_letters, pred_letters, KEY_ENTITY_NAMES, benchmark_config_for)
    semantic = score_overall(gold_letters, pred_letters, KEY_ENTITY_NAMES, semantic_config_for)
    phrase = score_overall(gold_letters, pred_letters, KEY_ENTITY_NAMES, lambda _e: PHRASE_ONLY)
    source_near = source_near_diagnostic(
        gold_letters,
        pred_letters,
        KEY_ENTITY_NAMES,
        semantic_config_for,
    )
    clinical_recovery = _key_clinical_recovery_to_dict(gold_letters, pred_letters)

    return {
        "examples": n,
        "call_failures": sum(bool(r.get("call_error")) for r in rows),
        "parse_failures": sum(has_blocking_parse_issue(r.get("parse_errors")) for r in rows),
        "initial_parse_failures": sum(
            has_blocking_parse_issue(r.get("initial_parse_errors")) for r in rows
        ),
        "format_retries_applied": sum(
            "format_retry_applied" in (r.get("format_retry_notes") or []) for r in rows
        ),
        "format_retries_rejected": sum(
            any(
                str(note).startswith("format_retry_rejected:")
                for note in (r.get("format_retry_notes") or [])
            )
            for r in rows
        ),
        "n_events_raw": sum(int(r.get("n_events_raw", 0)) for r in rows),
        "n_mentions_raw": n_mentions_raw,
        "n_patient_history": n_patient_history,
        "n_medication_history": n_medication_history,
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
        "clinical_recovery": clinical_recovery,
        "diagnostic_ladder": {"source_near": _source_near_to_dict(source_near)},
        "target": {
            "key_entity_item_f1": KEY_ENTITY_ITEM_F1_TARGET,
            "published_per_entity_item_f1": PUBLISHED_PER_ENTITY_ITEM_F1,
        },
    }


def write_jsonl(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (  # noqa: E501
        write_jsonl_rows,
    )

    write_jsonl_rows(rows, path)


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
    lines = ["# ExECTv2 Key Entities Structured Events", ""]
    if is_checkpoint:
        processed = summary.get("examples", len(rows))
        total = total_letters or processed
        lines.extend([f"CHECKPOINT ONLY: processed {processed} / {total} letters", ""])
    lines.extend(
        [
            f"- JSONL: `{jsonl_path}`",
            f"- Prompt version: `{metadata.get('prompt_version', PROMPT_VERSION)}`",
            f"- Pipeline family: `{metadata.get('pipeline_family', PIPELINE_FAMILY)}`",
            f"- Split: `{metadata.get('split')}`",
            f"- Model: `{metadata.get('model')}`",
            f"- Mode: `{metadata.get('mode')}`",
            f"- Letters: {summary.get('examples', 0)}",
            "",
            "## Gate Summary",
            "",
            f"- Call failures: {summary.get('call_failures', 0)}",
            f"- Parse/schema failures: {summary.get('parse_failures', 0)}",
            f"- Initial parse/schema failures: {summary.get('initial_parse_failures', 0)}",
            f"- Format retries applied: {summary.get('format_retries_applied', 0)}",
            f"- Format retries rejected: {summary.get('format_retries_rejected', 0)}",
            f"- Clinical events raw: {summary.get('n_events_raw', 0)}",
            f"- Mentions raw: {summary.get('n_mentions_raw', 0)}",
            f"- Patient-history sink entries: {summary.get('n_patient_history', 0)}",
            f"- Medication-history sink entries: {summary.get('n_medication_history', 0)}",
            f"- Mentions scored: {summary.get('n_mentions_scored', 0)}",
            f"- Evidence-invalid dropped: {summary.get('n_evidence_invalid', 0)}",
            f"- Evidence validity rate: {summary.get('evidence_validity_rate', 0.0):.4f}",
            "",
            "## Overall Scores",
            "",
        ]
    )
    for config_name in ("semantic", "benchmark", "phrase_only"):
        lines.extend(_score_lines(config_name, summary.get("scores", {}).get(config_name, {})))
    lines.extend(_clinical_recovery_lines(summary.get("clinical_recovery", {})))
    lines.extend(_diagnostic_ladder_lines(summary.get("diagnostic_ladder", {})))
    lines.extend(["", "## Per-Entity Semantic F1", ""])
    lines.append("| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |")
    lines.append("| --- | ---: | ---: | ---: | ---: |")
    semantic_entities = summary.get("scores", {}).get("semantic", {}).get("per_entity", {})
    for entity in KEY_ENTITY_NAMES:
        entry = semantic_entities.get(entity, {})
        item = entry.get("per_item", {})
        letter = entry.get("per_letter", {})
        published = PUBLISHED_PER_ENTITY_ITEM_F1.get(entity, 0.0)
        lines.append(
            f"| {entity} | {KEY_ENTITY_ITEM_F1_TARGET:.2f} | {published:.2f} | "
            f"{item.get('f1', 0):.3f} | {letter.get('f1', 0):.3f} |"
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def _overall_to_dict(score: Any) -> dict[str, Any]:
    return {
        "per_item": _prf1_to_dict(score.per_item),
        "per_letter": _prf1_to_dict(score.per_letter),
        "per_entity": {
            entity: {
                "per_item": _prf1_to_dict(entity_score.per_item),
                "per_letter": _prf1_to_dict(entity_score.per_letter),
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


def _key_clinical_recovery_to_dict(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
) -> dict[str, Any]:
    scores = {
        PRESCRIPTION.name: score_prescription_components(
            gold_letters,
            pred_letters,
        ).clinical_headline,
        DIAGNOSIS.name: score_concept_identity(
            gold_letters,
            pred_letters,
            DIAGNOSIS.name,
        ).concept_negation,
        SEIZURE_FREQUENCY.name: score_frequency_state(
            gold_letters,
            pred_letters,
        ).clinical_headline,
        INVESTIGATIONS.name: score_investigations_components(
            gold_letters,
            pred_letters,
        ).clinical_headline,
    }
    precision_tp = sum(
        int(getattr(score, "precision_tp", getattr(score, "tp", 0))) for score in scores.values()
    )
    recall_tp = sum(
        int(getattr(score, "recall_tp", getattr(score, "tp", 0))) for score in scores.values()
    )
    pred_count = sum(
        int(getattr(score, "pred_count", getattr(score, "tp", 0) + getattr(score, "fp", 0)))
        for score in scores.values()
    )
    gold_count = sum(
        int(getattr(score, "gold_count", getattr(score, "tp", 0) + getattr(score, "fn", 0)))
        for score in scores.values()
    )
    precision = precision_tp / pred_count if pred_count else 0.0
    recall = recall_tp / gold_count if gold_count else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "target_headline_f1": KEY_ENTITY_ITEM_F1_TARGET,
        "overall": {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "tp": recall_tp,
            "fp": max(0, pred_count - precision_tp),
            "fn": max(0, gold_count - recall_tp),
        },
        "diagnosis_component": "concept_negation",
        "per_entity": {entity: _prf1_to_dict(score) for entity, score in scores.items()},
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
                ExectLetter(letter_id=row["letter_id"], note_text="", annotations=annotations)
            )
    return letters


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


def _clinical_recovery_lines(scores: dict[str, Any]) -> list[str]:
    per_entity = scores.get("per_entity", {})
    overall = scores.get("overall", {})
    target = float(scores.get("target_headline_f1", KEY_ENTITY_ITEM_F1_TARGET))
    lines = [
        "",
        "## Key Clinical-Recovery Headlines",
        "",
        (
            f"- Canonical overall (`clinical_headline`, Diagnosis="
            f"`{scores.get('diagnosis_component', 'concept_negation')}`): "
            f"F1={overall.get('f1', 0):.3f} "
            f"P={overall.get('precision', 0):.3f} "
            f"R={overall.get('recall', 0):.3f}"
        ),
        "",
        "| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for entity in KEY_ENTITY_NAMES:
        entry = per_entity.get(entity, {})
        lines.append(
            f"| {entity} | {target:.2f} | "
            f"{entry.get('f1', 0):.3f} | "
            f"{entry.get('precision', 0):.3f} | "
            f"{entry.get('recall', 0):.3f} | "
            f"{entry.get('tp', 0)} | {entry.get('fp', 0)} | {entry.get('fn', 0)} |"
        )
    return lines


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
    for entity in KEY_ENTITY_NAMES:
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


def _emit_checkpoint(
    rows: Sequence[dict[str, Any]],
    *,
    total: int,
    jsonl_path: Path | None,
    report_path: Path | None,
    split: str,
    model: str,
    mode: str,
    prompt_version: str = PROMPT_VERSION,
    prompt_profile: PromptProfile = "full",
) -> None:
    summary = summarize_rows(rows)
    if jsonl_path is not None:
        write_jsonl(rows, jsonl_path)
    if report_path is not None and jsonl_path is not None:
        checkpoint_report_path = _checkpoint_report_path(report_path)
        write_report(
            rows,
            {
                "prompt_version": prompt_version,
                "prompt_profile": prompt_profile,
                "pipeline_family": PIPELINE_FAMILY,
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
