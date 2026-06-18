"""Diagnosis-focused verifier over the v0.5 structured key-entity draft.

This is the first targeted multi-prompt comparison after the single structured
schema path plateaued on Diagnosis. The LLM owns the revised Diagnosis mentions:
deterministic code only validates JSON shape, exact evidence, legal attributes,
and benchmark-facing CUI projection.
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
    score_concept_identity,
    score_entity,
    semantic_config_for,
    source_near_diagnostic,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

PROMPT_VERSION = "exectv2_llm_diagnosis_verifier_v0.3"
PIPELINE_FAMILY = "exectv2_llm_diagnosis_verifier"
COMPONENT_OWNER = "llm_diagnosis_verifier"


class ExECTv2DiagnosisVerifierSignature(dspy.Signature):
    """Review one clinical letter and a draft Diagnosis list.

    Return exactly one JSON object with a 'mentions' list. No markdown wrapper.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter, draft Diagnosis mentions, and rules."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"mentions\": [{\"text\": ..., "
            "\"attributes\": {...}, \"evidence\": ..., \"confidence\": ..., "
            "\"rationale\": ...}, ...]}"
        )
    )


class DspyDiagnosisVerifier(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(ExECTv2DiagnosisVerifierSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def draft_mentions_by_letter(rows: Sequence[Mapping[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    drafts: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        letter_id = str(row["letter_id"])
        drafts[letter_id] = [
            {
                "text": str(m.get("text", "")),
                "attributes": dict(m.get("attributes") or {}),
                "evidence": str(m.get("evidence", "")),
                "confidence": str(m.get("confidence", "")),
                "rationale": str(m.get("rationale", "")),
            }
            for m in row.get("predicted_mentions", [])
            if m.get("entity") == DIAGNOSIS.name
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
            "Review the clinical letter and the draft Diagnosis mentions from the "
            "single structured key-entity extractor. Return the final Diagnosis "
            "mentions only. You may keep, delete, edit, or add mentions, but every "
            "final mention must be supported by exact source evidence."
        ),
        "output_schema": {
            "mentions": [
                {
                    "text": "Clean core Diagnosis concept phrase owned by the verifier.",
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
        "attribute_vocabulary": _attribute_vocabulary(),
        "clinical_rules": _clinical_rules(),
        "worked_examples": _worked_examples(),
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _attribute_vocabulary() -> dict[str, Any]:
    spec = ENTITY_REGISTRY[DIAGNOSIS.name]
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
        "Return only Diagnosis mentions. Do not emit Prescription, SF, or Investigations.",
        "Every final evidence value must be an exact substring of the letter.",
        (
            "Diagnosis text may be a normalized core clinical concept phrase even "
            "when the source expresses it with hedging, punctuation, abbreviation, "
            "or discontinuous wording. The evidence must still be exact."
        ),
        "Do not emit CUI or CUIPhrase; projection is a separate deterministic layer.",
        (
            "Render only the core clinical concept span in text. Strip section labels, "
            "dashes, hedging words, 'single' in simple single-seizure phrases, "
            "and explanatory context. Do not strip 'alone' from an epilepsy-with-"
            "generalised-tonic-clonic-seizures-alone syndrome."
        ),
        (
            "Use Certainty='4' for probable or likely diagnoses; Certainty='3' for "
            "possible, suspected, query, or differential diagnoses; Certainty='5' "
            "only for established or unqualified statements."
        ),
        (
            "Prefer the most specific epilepsy syndrome stated in the source, such "
            "as focal epilepsy, temporal lobe epilepsy, focal onset epilepsy, "
            "symptomatic structural focal epilepsy, intractable epilepsy, "
            "primary/generalised epilepsy, juvenile myoclonic epilepsy, or JME."
        ),
        (
            "When the source says 'Epilepsy - unclassified, possibly generalised', "
            "emit 'generalised epilepsy' with Certainty='3'. Do not emit generic "
            "'epilepsy' with Certainty='3' for that phrase."
        ),
        (
            "Use the exact abbreviation as text when the source says JME; do not "
            "write 'possible JME' as text."
        ),
        (
            "For discontinuous syndrome wording, render the normalized concept: "
            "'epilepsy - probable focal' -> 'focal epilepsy'; 'probable temporal' "
            "in an epilepsy diagnosis context -> 'temporal lobe epilepsy'."
        ),
        (
            "Keep named seizure types when they are asserted as seizure diagnoses: "
            "focal seizures, focal seizures with altered awareness, focal to bilateral "
            "convulsive seizures, tonic clonic seizures, secondary generalised "
            "tonic clonic seizures, complex partial seizures, absence seizures, "
            "and bilateral convulsive seizure."
        ),
        (
            "Do not drop true named seizure types just because they occur in a "
            "seizure-type/frequency line; if the line names the seizure type, include "
            "the Diagnosis mention as well as any SF handled elsewhere."
        ),
        (
            "Do not deduplicate separately supported diagnosis assertions. If both "
            "a Diagnosis line and a seizure-type/frequency line independently assert "
            "tonic clonic seizures, return two Diagnosis mentions with their own "
            "exact evidence strings."
        ),
        (
            "Use normalized seizure-type text for scoring-facing Diagnosis mentions: "
            "'generalised tonic clonic seizures' -> 'tonic clonic seizures'; "
            "'single focal seizure' -> 'focal seizure'. Use plural "
            "'tonic clonic seizures' for recurring, plural, or frequency-context "
            "tonic-clonic events."
        ),
        (
            "If the source states an epilepsy-with-generalised-tonic-clonic-"
            "seizures-alone syndrome, preserve the full syndrome as a Diagnosis "
            "text mention, add the generic 'epilepsy' concept only when the word "
            "epilepsy is explicit in that evidence, and add tonic-clonic seizure "
            "type mentions for each separately supported tonic-clonic assertion."
        ),
        (
            "For source phrases such as 'I think these are in keeping with temporal "
            "lobe onset focal seizures', emit seizure-type diagnoses such as "
            "'temporal lobe seizure' and 'focal seizures' with Certainty='4'; do "
            "not convert them into 'temporal lobe epilepsy'."
        ),
        (
            "A bare adjective such as 'general seizures' is not a named seizure "
            "type. If a phrase says 'general and complex partial seizures', keep "
            "the named 'complex partial seizures' and do not emit 'general seizures'."
        ),
        "Never write 'tonic chronic'; preserve tonic clonic or tonic-clonic.",
        "Never use attribute labels such as 'MultipleSeizures' as mention text.",
        (
            "Do not emit isolated symptoms or aura features as Diagnosis, including "
            "myoclonic jerks, jerks, flashing lights, odd sensations, altered "
            "awareness alone, dizziness, blackouts, collapse, or anxiety."
        ),
        (
            "Myoclonic jerks are not a Diagnosis mention by themselves, even when "
            "frequent. If the source also says possible JME, emit JME with "
            "Certainty='3' and omit myoclonic jerks."
        ),
        (
            "Do not emit dissociative, non-epileptic, or psychogenic events as an "
            "epileptic Diagnosis unless the evidence explicitly states they are "
            "epileptic seizures."
        ),
        "If the letter has no requested Diagnosis mentions, return {\"mentions\": []}.",
        "Return exactly one JSON object. No markdown code fences.",
    ]


def _worked_examples() -> list[dict[str, Any]]:
    return [
        {
            "note_fragment": "Diagnosis: focal epilepsy-Probable temporal",
            "draft": [{"text": "focal epilepsy probable temporal"}],
            "correct": [
                {
                    "text": "focal epilepsy",
                    "attributes": {
                        "DiagCategory": "Epilepsy",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                    "evidence": "focal epilepsy",
                    "confidence": "high",
                    "rationale": "Focal epilepsy is explicitly stated.",
                },
                {
                    "text": "temporal lobe epilepsy",
                    "attributes": {
                        "DiagCategory": "Epilepsy",
                        "Certainty": "4",
                        "Negation": "Affirmed",
                    },
                    "evidence": "Probable temporal",
                    "confidence": "medium",
                    "rationale": "Probable temporal diagnosis is stated with uncertainty.",
                },
            ],
        },
        {
            "note_fragment": "Diagnosis: epilepsy - probable focal.",
            "draft": [{"text": "epilepsy - probable focal"}],
            "correct": [
                {
                    "text": "focal epilepsy",
                    "attributes": {
                        "DiagCategory": "Epilepsy",
                        "Certainty": "4",
                        "Negation": "Affirmed",
                    },
                    "evidence": "epilepsy - probable focal",
                    "confidence": "medium",
                    "rationale": "Discontinuous probable focal epilepsy is normalized.",
                }
            ],
        },
        {
            "note_fragment": "Seizure type: generalised tonic clonic seizures.",
            "draft": [],
            "correct": [
                {
                    "text": "tonic clonic seizures",
                    "attributes": {
                        "DiagCategory": "MultipleSeizures",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                    "evidence": "generalised tonic clonic seizures",
                    "confidence": "high",
                    "rationale": "The named seizure type is asserted and normalized.",
                }
            ],
        },
        {
            "note_fragment": (
                "Diagnosis: epilepsy with generalised tonic clonic seizures alone. "
                "Seizure type and frequency: Generalised tonic clonic seizures: "
                "six per year."
            ),
            "draft": [{"text": "tonic clonic seizures"}],
            "correct": [
                {
                    "text": "epilepsy",
                    "attributes": {
                        "DiagCategory": "Epilepsy",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                    "evidence": "epilepsy with generalised tonic clonic seizures alone",
                    "confidence": "high",
                    "rationale": "The source explicitly states epilepsy.",
                },
                {
                    "text": "generalised tonic clonic seizures alone",
                    "attributes": {
                        "DiagCategory": "Epilepsy",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                    "evidence": "epilepsy with generalised tonic clonic seizures alone",
                    "confidence": "high",
                    "rationale": "The syndrome includes the clinically meaningful alone qualifier.",
                },
                {
                    "text": "tonic clonic seizures",
                    "attributes": {
                        "DiagCategory": "MultipleSeizures",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                    "evidence": "generalised tonic clonic seizures",
                    "confidence": "high",
                    "rationale": "The named seizure type is present in the diagnosis line.",
                },
                {
                    "text": "tonic clonic seizures",
                    "attributes": {
                        "DiagCategory": "MultipleSeizures",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                    "evidence": "Generalised tonic clonic seizures: six per year",
                    "confidence": "high",
                    "rationale": (
                        "A separate frequency line independently asserts the "
                        "same seizure type."
                    ),
                },
            ],
        },
        {
            "note_fragment": (
                "Diagnosis: Epilepsy - unclassified, possibly generalised. "
                "Seizure type and frequency: 2 generalised tonic clonic seizures."
            ),
            "draft": [{"text": "epilepsy", "attributes": {"Certainty": "3"}}],
            "correct": [
                {
                    "text": "generalised epilepsy",
                    "attributes": {
                        "DiagCategory": "Epilepsy",
                        "Certainty": "3",
                        "Negation": "Affirmed",
                    },
                    "evidence": "Epilepsy - unclassified, possibly generalised",
                    "confidence": "medium",
                    "rationale": "Possibly generalised is the uncertain specific syndrome.",
                },
                {
                    "text": "tonic clonic seizures",
                    "attributes": {
                        "DiagCategory": "MultipleSeizures",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                    "evidence": "2 generalised tonic clonic seizures",
                    "confidence": "high",
                    "rationale": "The named seizure type is asserted in a seizure-type line.",
                },
            ],
        },
        {
            "note_fragment": (
                "I think these are in keeping with temporal lobe onset focal "
                "seizures. She continues to get general and complex partial seizures."
            ),
            "draft": [{"text": "temporal lobe epilepsy"}, {"text": "general seizures"}],
            "correct": [
                {
                    "text": "temporal lobe seizure",
                    "attributes": {
                        "DiagCategory": "MultipleSeizures",
                        "Certainty": "4",
                        "Negation": "Affirmed",
                    },
                    "evidence": "in keeping with temporal lobe onset focal seizures",
                    "confidence": "medium",
                    "rationale": (
                        "The source states a probable seizure type, not "
                        "epilepsy syndrome."
                    ),
                },
                {
                    "text": "focal seizures",
                    "attributes": {
                        "DiagCategory": "MultipleSeizures",
                        "Certainty": "4",
                        "Negation": "Affirmed",
                    },
                    "evidence": "in keeping with temporal lobe onset focal seizures",
                    "confidence": "medium",
                    "rationale": "The same phrase also asserts focal seizures with uncertainty.",
                },
                {
                    "text": "complex partial seizures",
                    "attributes": {
                        "DiagCategory": "MultipleSeizures",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                    "evidence": "complex partial seizures",
                    "confidence": "high",
                    "rationale": "Complex partial seizures are a named seizure type.",
                },
            ],
        },
        {
            "note_fragment": "Diagnosis: possible JME.",
            "draft": [{"text": "possible JME"}],
            "correct": [
                {
                    "text": "JME",
                    "attributes": {
                        "DiagCategory": "Epilepsy",
                        "Certainty": "3",
                        "Negation": "Affirmed",
                    },
                    "evidence": "possible JME",
                    "confidence": "medium",
                    "rationale": "Possible maps to Certainty 3; JME is the core span.",
                }
            ],
        },
        {
            "note_fragment": "Unwitnessed blackouts and anxiety, no epileptic seizures.",
            "draft": [{"text": "Unwitnessed blackouts"}, {"text": "anxiety"}],
            "correct": [],
        },
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
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    program = DspyDiagnosisVerifier()
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
    n = len(rows)
    if n == 0:
        return {"examples": 0}
    n_mentions_raw = sum(int(r.get("n_mentions_raw", 0)) for r in rows)
    n_evidence_invalid = sum(int(r.get("n_evidence_invalid", 0)) for r in rows)
    gold_letters = _reconstruct_gold_letters(rows)
    pred_letters = _reconstruct_pred_letters(rows)

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
        "call_failures": sum(bool(r.get("call_error")) for r in rows),
        "parse_failures": sum(_has_blocking_parse_issue(r.get("parse_errors")) for r in rows),
        "n_draft_mentions": sum(int(r.get("n_draft_mentions", 0)) for r in rows),
        "n_mentions_raw": n_mentions_raw,
        "n_mentions_scored": sum(int(r.get("n_mentions_scored", 0)) for r in rows),
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
    clinical = summary.get("clinical_recovery", {}).get("diagnosis", {})
    source = summary.get("source_near", {})
    overlap = source.get("overlap", {})
    lines = ["# ExECTv2 Diagnosis Verifier", ""]
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
            f"- Draft Diagnosis mentions: {summary.get('n_draft_mentions', 0)}",
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
                f"{clinical.get('precision', 0):.3f} | "
                f"{clinical.get('recall', 0):.3f} | {clinical.get('tp', 0)} | "
                f"{clinical.get('fp', 0)} | {clinical.get('fn', 0)} |"
            ),
            "",
            "## Source-Near Diagnostic",
            "",
            (
                f"- Overlap F1={overlap.get('f1', 0):.3f} "
                f"R={overlap.get('recall', 0):.3f} "
                f"(TP={overlap.get('tp', 0)} FP={overlap.get('fp', 0)} "
                f"FN={overlap.get('fn', 0)})"
            ),
            (
                f"- Attribute agreement: {source.get('attribute_agreement_rate', 0):.3f} "
                f"({source.get('attribute_agreement_tp', 0)}/"
                f"{source.get('attribute_agreement_total', 0)})"
            ),
            "",
            "## Format Layers",
            "",
            "| Layer | Item F1 | Item P | Item R | Letter F1 | TP | FP | FN |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for name in ("phrase_only", "semantic", "benchmark"):
        score = summary.get("scores", {}).get(name, {})
        item = score.get("per_item", {})
        letter = score.get("per_letter", {})
        lines.append(
            f"| {name} | {item.get('f1', 0):.3f} | "
            f"{item.get('precision', 0):.3f} | {item.get('recall', 0):.3f} | "
            f"{letter.get('f1', 0):.3f} | {item.get('tp', 0)} | "
            f"{item.get('fp', 0)} | {item.get('fn', 0)} |"
        )
    path.write_text("\n".join(lines), encoding="utf-8")


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
                    entity=DIAGNOSIS.name,
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
                    entity=DIAGNOSIS.name,
                    text=str(m["text"]),
                    attributes={
                        str(k): str(v) for k, v in dict(m.get("attributes") or {}).items()
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
    if jsonl_path is not None:
        write_jsonl(rows, jsonl_path)
    if report_path is not None:
        metadata = {
            "prompt_version": PROMPT_VERSION,
            "pipeline_family": PIPELINE_FAMILY,
            "split": split,
            "model": model,
            "mode": mode,
            "is_checkpoint": True,
            "total_letters": total,
            "summary": summarize_rows(rows),
        }
        write_report(rows, metadata, report_path, jsonl_path=jsonl_path or Path(""))
    print(
        json.dumps(
            {
                "processed": len(rows),
                "total": total,
                "call_failures": sum(bool(r.get("call_error")) for r in rows),
                "parse_failures": sum(
                    _has_blocking_parse_issue(r.get("parse_errors")) for r in rows
                ),
                "n_mentions_scored": sum(int(r.get("n_mentions_scored", 0)) for r in rows),
            },
            sort_keys=True,
        ),
        flush=True,
    )
