"""Investigations-focused verifier over the v0.5 structured key-entity draft."""

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
    ENTITY_REGISTRY,
    INVESTIGATIONS,
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
    _has_blocking_parse_issue,
    check_evidence,
    parse_extraction_json,
    repair_attributes,
    write_jsonl,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    PHRASE_ONLY,
    benchmark_config_for,
    score_entity,
    score_investigations_components,
    semantic_config_for,
    source_near_diagnostic,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

PROMPT_VERSION = "exectv2_llm_investigations_verifier_v0.1"
PIPELINE_FAMILY = "exectv2_llm_investigations_verifier"
COMPONENT_OWNER = "llm_investigations_verifier"


class ExECTv2InvestigationsVerifierSignature(dspy.Signature):
    """Review one clinical letter and draft Investigations mentions."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter, draft Investigations mentions, and rules."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"mentions\": [{\"text\": ..., "
            "\"attributes\": {...}, \"evidence\": ..., \"confidence\": ..., "
            "\"rationale\": ...}, ...]}"
        )
    )


class DspyInvestigationsVerifier(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(ExECTv2InvestigationsVerifierSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def draft_mentions_by_letter(rows: Sequence[Mapping[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    drafts: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        drafts[str(row["letter_id"])] = [
            {
                "text": str(m.get("text", "")),
                "attributes": dict(m.get("attributes") or {}),
                "evidence": str(m.get("evidence", "")),
                "confidence": str(m.get("confidence", "")),
                "rationale": str(m.get("rationale", "")),
            }
            for m in row.get("predicted_mentions", [])
            if m.get("entity") == INVESTIGATIONS.name
        ]
    return drafts


def read_draft_rows(path: Path | None) -> list[dict[str, Any]]:
    if path is None or not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def build_prompt_input(letter: ExectLetter, draft_mentions: Sequence[Mapping[str, Any]]) -> str:
    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": (
            "Review the clinical letter and draft Investigations mentions from "
            "the single structured key-entity extractor. Return final "
            "Investigations mentions only. You may keep, delete, edit, or add "
            "mentions, but every final mention must be supported by exact source "
            "evidence."
        ),
        "output_schema": {
            "mentions": [
                {
                    "text": "Clean investigation phrase owned by the verifier.",
                    "attributes": {
                        "MRI_Performed": "Yes | No",
                        "MRI_Results": "Normal | Abnormal | Unknown",
                        "CT_Performed": "Yes | No",
                        "CT_Results": "Normal | Abnormal | Unknown",
                        "EEG_Performed": "Yes | No",
                        "EEG_Results": "Normal | Abnormal | Unknown",
                        "EEG_Type": "Standard | SleepDeprived | VideoTelemetry",
                    },
                    "evidence": "Exact source substring supporting text and attributes.",
                    "confidence": "low | medium | high",
                    "rationale": "One brief sentence explaining the decision.",
                }
            ]
        },
        "draft_investigations_mentions": list(draft_mentions),
        "attribute_vocabulary": _attribute_vocabulary(),
        "clinical_rules": _clinical_rules(),
        "worked_examples": _worked_examples(),
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _attribute_vocabulary() -> dict[str, Any]:
    spec = ENTITY_REGISTRY[INVESTIGATIONS.name]
    attrs: dict[str, Any] = {}
    for attr in sorted(spec.legal_attributes):
        if attr in {"CUI", "CUIPhrase"}:
            attrs[attr] = "Do not emit this; deterministic projection fills it later."
        elif attr in spec.closed_vocab:
            attrs[attr] = sorted(spec.closed_vocab[attr])
        else:
            attrs[attr] = "string copied or normalized from the letter."
    return attrs


def _clinical_rules() -> list[str]:
    return [
        "Return only Investigations mentions. Do not emit Prescription, Diagnosis, or SF.",
        "Every final evidence value must be an exact substring of the letter.",
        "Do not emit CUI or CUIPhrase; projection is a deterministic layer.",
        (
            "The clinical headline is one key per modality: MRI, CT, or EEG, with "
            "performed status plus result and EEG type when supported."
        ),
        (
            "Emit completed historical tests. Omit planned, requested, arranged, "
            "future, or recommended tests unless a separate completed test is also "
            "stated."
        ),
        (
            "Do not return modality-only mentions for planned tests such as 'I will "
            "arrange an MRI', 'request EEG', or 'organise CT'."
        ),
        (
            "When a completed test has an explicit result, include the result. "
            "Normal/unremarkable/no abnormality/no epileptiform correlate -> Normal. "
            "Spike and wave, epileptiform discharges, slowing, gliosis, lesion, "
            "atrophy, cortical or white matter changes, abnormality -> Abnormal."
        ),
        (
            "If the letter says a completed test was done but gives no result, "
            "emit Performed='Yes' without a result only when the source gives no "
            "result words nearby."
        ),
        (
            "For 'no MRI', 'never had MRI', or 'MRI not performed', emit "
            "MRI_Performed='No'. Use the same rule for CT and EEG."
        ),
        (
            "For video EEG, VEEG, video-telemetry, or telemetry, set "
            "EEG_Type='VideoTelemetry'. For sleep-deprived EEG, set "
            "EEG_Type='SleepDeprived'. Otherwise omit EEG_Type unless the source "
            "supports Standard."
        ),
        (
            "Do not merge different modalities into one mention unless the same "
            "source span explicitly states both and each has its own attributes."
        ),
        "Return exactly one JSON object. No markdown code fences.",
    ]


def _worked_examples() -> list[dict[str, Any]]:
    return [
        {
            "note_fragment": "I will arrange an MRI scan of the brain and an EEG.",
            "draft": [{"text": "MRI scan"}, {"text": "EEG"}],
            "correct": [],
        },
        {
            "note_fragment": "MRI 2016 showed left-sided gliosis. EEG was normal.",
            "draft": [],
            "correct": [
                {
                    "text": "MRI 2016 showed left-sided gliosis",
                    "attributes": {"MRI_Performed": "Yes", "MRI_Results": "Abnormal"},
                    "evidence": "MRI 2016 showed left-sided gliosis",
                    "confidence": "high",
                    "rationale": "Gliosis is an abnormal MRI result.",
                },
                {
                    "text": "EEG was normal",
                    "attributes": {"EEG_Performed": "Yes", "EEG_Results": "Normal"},
                    "evidence": "EEG was normal",
                    "confidence": "high",
                    "rationale": "The EEG result is explicitly normal.",
                },
            ],
        },
        {
            "note_fragment": "EEG showed generalised spike and wave. MRI was normal.",
            "draft": [{"text": "EEG"}, {"text": "MRI"}],
            "correct": [
                {
                    "text": "EEG showed generalised spike and wave",
                    "attributes": {"EEG_Performed": "Yes", "EEG_Results": "Abnormal"},
                    "evidence": "EEG showed generalised spike and wave",
                    "confidence": "high",
                    "rationale": "Spike and wave is an abnormal EEG result.",
                },
                {
                    "text": "MRI was normal",
                    "attributes": {"MRI_Performed": "Yes", "MRI_Results": "Normal"},
                    "evidence": "MRI was normal",
                    "confidence": "high",
                    "rationale": "The MRI result is explicitly normal.",
                },
            ],
        },
        {
            "note_fragment": "Video EEG captured events with no epileptiform correlate.",
            "draft": [],
            "correct": [
                {
                    "text": "Video EEG captured events with no epileptiform correlate",
                    "attributes": {
                        "EEG_Performed": "Yes",
                        "EEG_Results": "Normal",
                        "EEG_Type": "VideoTelemetry",
                    },
                    "evidence": "Video EEG captured events with no epileptiform correlate",
                    "confidence": "medium",
                    "rationale": (
                        "Video EEG is completed telemetry with no epileptiform "
                        "correlate."
                    ),
                }
            ],
        },
        {
            "note_fragment": "She has never had an MRI brain scan.",
            "draft": [],
            "correct": [
                {
                    "text": "never had an MRI brain scan",
                    "attributes": {"MRI_Performed": "No"},
                    "evidence": "never had an MRI brain scan",
                    "confidence": "medium",
                    "rationale": "The source explicitly says MRI was not performed.",
                }
            ],
        },
    ]


def to_predicted_letter(
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
    spec = ENTITY_REGISTRY[INVESTIGATIONS.name]
    for mention in evidence_valid:
        attrs = dict(mention.attributes)
        for key in ("CUI", "CUIPhrase"):
            if key in attrs:
                attrs.pop(key)
                all_warnings.append(
                    f"{INVESTIGATIONS.name}: "
                    f"dropped_model_supplied_projection_attribute: {key!r}"
                )
        repaired_attrs, attr_warnings = repair_attributes(attrs, spec=spec)
        all_warnings.extend(f"{INVESTIGATIONS.name}: {warning}" for warning in attr_warnings)
        predicted_mentions.append(
            PredictedMention(
                entity=INVESTIGATIONS.name,
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
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    program = DspyInvestigationsVerifier()
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
        prompt_input_json = build_prompt_input(letter, draft_mentions)
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
                "predicted_mentions": [_mention_to_row(m) for m in predicted_letter.mentions],
                "gold_mentions": [
                    {"text": a.text, "attributes": dict(a.attributes)}
                    for a in letter.entities(INVESTIGATIONS.name)
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
    if not rows:
        return {"examples": 0}
    gold_letters = _reconstruct_gold_letters(rows)
    pred_letters = _reconstruct_pred_letters(rows)
    investigations = score_investigations_components(gold_letters, pred_letters)
    source_near = source_near_diagnostic(
        gold_letters,
        pred_letters,
        [INVESTIGATIONS.name],
        semantic_config_for,
    ).per_entity[INVESTIGATIONS.name]
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
            "investigations": investigations.clinical_headline.model_dump(),
            "target_headline_f1": 0.8,
        },
        "source_near": source_near.model_dump(),
        "format_layers": {
            "phrase_only": score_entity(
                gold_letters,
                pred_letters,
                INVESTIGATIONS.name,
                PHRASE_ONLY,
            ).per_item.model_dump(),
            "semantic": score_entity(
                gold_letters,
                pred_letters,
                INVESTIGATIONS.name,
                semantic_config_for(INVESTIGATIONS.name),
            ).per_item.model_dump(),
            "benchmark": score_entity(
                gold_letters,
                pred_letters,
                INVESTIGATIONS.name,
                benchmark_config_for(INVESTIGATIONS.name),
            ).per_item.model_dump(),
        },
    }


def write_report(
    rows: Sequence[dict[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    summary = metadata.get("summary", {})
    clinical = summary.get("clinical_recovery", {}).get("investigations", {})
    lines = [
        "# ExECTv2 Investigations Verifier",
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
        f"- Draft Investigations mentions: {summary.get('n_draft_mentions', 0)}",
        f"- Mentions raw: {summary.get('n_mentions_raw', 0)}",
        f"- Mentions scored: {summary.get('n_mentions_scored', 0)}",
        f"- Evidence-invalid dropped: {summary.get('n_evidence_invalid', 0)}",
        f"- Evidence validity rate: {summary.get('evidence_validity_rate', 0):.4f}",
        "",
        "## Investigations Clinical-Recovery Headline",
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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _mention_to_row(mention: PredictedMention) -> dict[str, Any]:
    return {
        "entity": mention.entity,
        "text": mention.text,
        "attributes": dict(mention.attributes),
        "evidence": mention.evidence,
        "confidence": mention.confidence,
        "rationale": mention.rationale,
    }


def _reconstruct_gold_letters(rows: Sequence[dict[str, Any]]) -> list[ExectLetter]:
    return [
        ExectLetter(
            letter_id=row["letter_id"],
            note_text="",
            annotations=tuple(
                ExectAnnotation(
                    entity=INVESTIGATIONS.name,
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
                    entity=INVESTIGATIONS.name,
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
