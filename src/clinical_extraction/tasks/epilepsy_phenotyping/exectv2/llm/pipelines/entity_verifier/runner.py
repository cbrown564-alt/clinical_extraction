"""Shared run_split / report helpers for entity verifiers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy

from clinical_extraction.core.run_resume import merge_rows, pending_items, read_completed
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    project_cuis,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.mention_pipeline import (
    MentionRecord,
    check_evidence,
    parse_extraction_json,
    repair_attributes,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.config import (
    VerifierConfig,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.draft_io import (
    draft_mentions_by_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    write_jsonl,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.dspy_runner import (
    emit_run_checkpoint,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm


def make_dspy_module(config: VerifierConfig) -> dspy.Module:
    signature = config.dspy_signature

    class _DspyVerifier(dspy.Module):
        def __init__(self) -> None:
            super().__init__()
            self.predict = dspy.Predict(signature)

        def forward(self, prompt_input_json: str) -> dspy.Prediction:
            return self.predict(prompt_input_json=prompt_input_json)

    return _DspyVerifier()


def mention_to_row(mention: PredictedMention) -> dict[str, Any]:
    return {
        "entity": mention.entity,
        "text": mention.text,
        "attributes": dict(mention.attributes),
        "evidence": mention.evidence,
        "confidence": mention.confidence,
        "rationale": mention.rationale,
    }


def to_predicted_letter(
    config: VerifierConfig,
    letter_id: str,
    mentions: Sequence[MentionRecord],
    *,
    note_text: str,
) -> tuple[PredictedLetter, list[str]]:
    all_warnings: list[str] = []
    evidence_valid, evidence_invalid, ev_warnings = check_evidence(
        mentions, note_text=note_text
    )
    all_warnings.extend(ev_warnings)

    predicted_mentions: list[PredictedMention] = []
    spec = ENTITY_REGISTRY[config.entity_name]
    for mention in evidence_valid:
        attrs = dict(mention.attributes)
        for key in ("CUI", "CUIPhrase"):
            if key in attrs:
                attrs.pop(key)
                all_warnings.append(
                    f"{config.entity_name}: "
                    f"dropped_model_supplied_projection_attribute: {key!r}"
                )
        repaired_attrs, attr_warnings = repair_attributes(attrs, spec=spec)
        all_warnings.extend(
            f"{config.entity_name}: {warning}" for warning in attr_warnings
        )
        predicted_mentions.append(
            PredictedMention(
                entity=config.entity_name,
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


def reconstruct_gold_letters(
    rows: Sequence[dict[str, Any]],
    *,
    entity_name: str,
) -> list[ExectLetter]:
    return [
        ExectLetter(
            letter_id=row["letter_id"],
            note_text="",
            annotations=tuple(
                ExectAnnotation(
                    entity=entity_name,
                    text=str(m["text"]),
                    attributes={
                        str(k): str(v)
                        for k, v in dict(m.get("attributes") or {}).items()
                    },
                )
                for m in row.get("gold_mentions", [])
            ),
        )
        for row in rows
    ]


def reconstruct_pred_letters(
    rows: Sequence[dict[str, Any]],
    *,
    entity_name: str,
) -> list[ExectLetter]:
    letters: list[ExectLetter] = []
    for row in rows:
        pred = PredictedLetter(
            letter_id=row["letter_id"],
            mentions=tuple(
                PredictedMention(
                    entity=entity_name,
                    text=str(m["text"]),
                    attributes={
                        str(k): str(v)
                        for k, v in dict(m.get("attributes") or {}).items()
                    },
                    evidence=str(m.get("evidence", "")),
                    confidence=str(m.get("confidence", "medium")),
                    rationale=str(m.get("rationale", "")),
                )
                for m in row.get("predicted_mentions", [])
            ),
        )
        letters.append(to_exect_letter(pred))
    return letters


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
    timeline_context_by_letter: Mapping[str, str] | None = None,
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

    drafts = draft_mentions_by_letter(draft_rows, config)
    order = [letter.letter_id for letter in letters]
    requested = set(order)
    existing_rows, completed = read_completed(
        checkpoint_jsonl_path if resume else None, key="letter_id"
    )
    rows: list[dict[str, Any]] = [
        r for r in existing_rows if r.get("letter_id") in requested
    ]
    n_resumed = len(rows)
    todo = pending_items(letters, completed, key_of=lambda letter: letter.letter_id)

    for letter in todo:
        draft_mentions = drafts.get(letter.letter_id, [])
        timeline_context = (
            timeline_context_by_letter.get(letter.letter_id)
            if timeline_context_by_letter is not None
            else None
        )
        prompt_input_json = config.build_prompt_input(
            letter, draft_mentions, timeline_context=timeline_context
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
                "timeline_context_used": timeline_context is not None,
                "prompt_input_json": prompt_input_json,
                "raw_output": raw_output,
                "call_error": call_error,
                "parse_errors": parse_errors,
                "gate_warnings": gate_warnings,
                "n_draft_mentions": len(draft_mentions),
                "n_mentions_raw": len(mentions),
                "n_mentions_scored": len(predicted_letter.mentions),
                "n_evidence_invalid": len(mentions) - len(predicted_letter.mentions),
                "predicted_mentions": [
                    mention_to_row(m) for m in predicted_letter.mentions
                ],
                "gold_mentions": [
                    {"text": a.text, "attributes": dict(a.attributes)}
                    for a in letter.entities(config.entity_name)
                ],
            }
        )

        if progress_every and (len(rows) - n_resumed) % progress_every == 0:
            metadata = _run_metadata(
                config=config,
                split=split,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                mode=mode,
                n_letters=len(letters),
                n_resumed=n_resumed,
                rows=rows,
            )
            emit_run_checkpoint(
                rows,
                total=len(letters),
                jsonl_path=checkpoint_jsonl_path,
                report_path=checkpoint_report_path,
                metadata=metadata,
                summarize_rows=config.summarize_rows,
                write_jsonl=write_jsonl,
                write_report=lambda r, m, p, *, jsonl_path: write_report(
                    r, m, p, config=config, jsonl_path=jsonl_path
                ),
            )

    rows = merge_rows(rows, order, key="letter_id")
    metadata = _run_metadata(
        config=config,
        split=split,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        mode=mode,
        n_letters=len(letters),
        n_resumed=n_resumed,
        rows=rows,
    )
    return rows, metadata


def write_report(
    rows: Sequence[dict[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    config: VerifierConfig,
    jsonl_path: Path,
) -> None:
    summary = metadata.get("summary", {})
    clinical = summary.get("clinical_recovery", {}).get(config.clinical_recovery_key, {})
    source_near = summary.get("source_near", {})
    lines = [
        f"# {config.report_title}",
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
        f"- {config.draft_mentions_label}: {summary.get('n_draft_mentions', 0)}",
        f"- Mentions raw: {summary.get('n_mentions_raw', 0)}",
        f"- Mentions scored: {summary.get('n_mentions_scored', 0)}",
        f"- Evidence-invalid dropped: {summary.get('n_evidence_invalid', 0)}",
        f"- Evidence validity rate: {summary.get('evidence_validity_rate', 0):.4f}",
        "",
        f"## {config.clinical_recovery_section_title}",
        "",
        "| Target F1 | F1 | P | R | TP | FP | FN |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        (
            f"| 0.80 | {clinical.get('f1', 0):.3f} | "
            f"{clinical.get('precision', 0):.3f} | {clinical.get('recall', 0):.3f} | "
            f"{clinical.get('tp', 0)} | {clinical.get('fp', 0)} | "
            f"{clinical.get('fn', 0)} |"
        ),
    ]
    if config.include_source_near_in_report:
        lines.extend(
            [
                "",
                "## Source-Near Diagnostic",
                "",
                (
                    f"- Overlap F1={source_near.get('overlap', {}).get('f1', 0):.3f} "
                    f"R={source_near.get('overlap', {}).get('recall', 0):.3f}"
                ),
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _run_metadata(
    *,
    config: VerifierConfig,
    split: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: str,
    n_letters: int,
    n_resumed: int,
    rows: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    metadata = {
        "prompt_version": config.prompt_version,
        "pipeline_family": config.pipeline_family,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "mode": mode,
        "split": split,
        "n_letters": n_letters,
        "n_resumed": n_resumed,
        "dspy_version": getattr(dspy, "__version__", "unknown"),
    }
    metadata["summary"] = config.summarize_rows(rows)
    return metadata
