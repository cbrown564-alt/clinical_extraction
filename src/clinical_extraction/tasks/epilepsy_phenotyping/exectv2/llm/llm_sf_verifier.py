"""SeizureFrequency-focused verifier over the v0.5 structured key-entity draft."""

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
    score_frequency_state,
    semantic_config_for,
    source_near_diagnostic,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

PROMPT_VERSION = "exectv2_llm_sf_verifier_v0.1"
PIPELINE_FAMILY = "exectv2_llm_sf_verifier"
COMPONENT_OWNER = "llm_sf_verifier"


class ExECTv2SFVerifierSignature(dspy.Signature):
    """Review one clinical letter and a draft SeizureFrequency list."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter, draft SF mentions, and rules."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"mentions\": [{\"text\": ..., "
            "\"attributes\": {...}, \"evidence\": ..., \"confidence\": ..., "
            "\"rationale\": ...}, ...]}"
        )
    )


class DspySFVerifier(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(ExECTv2SFVerifierSignature)

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
            if m.get("entity") == SEIZURE_FREQUENCY.name
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
            "Review the clinical letter and draft SeizureFrequency mentions from "
            "the single structured key-entity extractor. Return the final "
            "SeizureFrequency mentions only. You may keep, delete, edit, or add "
            "mentions, but every final mention must be supported by exact source "
            "evidence."
        ),
        "output_schema": {
            "mentions": [
                {
                    "text": "Clean seizure/event type anchor phrase owned by the verifier.",
                    "attributes": {
                        "NumberOfSeizures": "string count, including 0 for seizure-free",
                        "LowerNumberOfSeizures": "lower bound count",
                        "UpperNumberOfSeizures": "upper bound count",
                        "NumberOfTimePeriods": "period count",
                        "LowerNumberOfTimePeriods": "lower bound period count",
                        "UpperNumberOfTimePeriods": "upper bound period count",
                        "TimePeriod": "Day | Week | Month | Year",
                        "TimeSince_or_TimeOfEvent": "Since | During",
                        "FrequencyChange": (
                            "Decreased | Frequent | Increased | Infrequent | Same"
                        ),
                        "PointInTime": (
                            "Birthday | DrugChange | LastClinic | Last_Month | "
                            "Last_Week | Last_Year | Surgery"
                        ),
                        "DayDate": "day number",
                        "MonthDate": "month number",
                        "YearDate": "year number",
                        "AgeLower": "lower age",
                        "AgeUpper": "upper age",
                        "AgeUnit": "Year | Month",
                    },
                    "evidence": "Exact source substring supporting text and attributes.",
                    "confidence": "low | medium | high",
                    "rationale": "One brief sentence explaining the decision.",
                }
            ]
        },
        "draft_seizure_frequency_mentions": list(draft_mentions),
        "attribute_vocabulary": _attribute_vocabulary(),
        "clinical_rules": _clinical_rules(),
        "worked_examples": _worked_examples(),
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _attribute_vocabulary() -> dict[str, Any]:
    spec = ENTITY_REGISTRY[SEIZURE_FREQUENCY.name]
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
        "Return only SeizureFrequency mentions. Do not emit Diagnosis or Prescription.",
        "Every final evidence value must be an exact substring of the letter.",
        (
            "Text may be a normalized clean seizure/event type anchor phrase even "
            "when the source has a typo. Evidence must remain exact. Example: "
            "source 'tonic chronic seizures' may have text 'tonic clonic seizures'."
        ),
        "Do not emit CUI or CUIPhrase; projection is a deterministic layer.",
        (
            "Clinical headline scoring cares about seizure/event type plus state: "
            "active-rate when a nonzero count/range is present, seizure-free when "
            "NumberOfSeizures is 0, and unknown when only FrequencyChange is present."
        ),
        (
            "Do not turn an active historical count into seizure-free just because "
            "the patient currently remains seizure free. Keep the historical active "
            "count and omit current seizure-free unless the source separately gives "
            "a seizure-free duration or point-in-time target annotated by the scheme."
        ),
        (
            "For 'several' use NumberOfSeizures='3'; for 'a few' use "
            "NumberOfSeizures='2'."
        ),
        (
            "For every 3 to 4 weeks, render one seizure per 3-4 Week period: "
            "NumberOfSeizures='1', LowerNumberOfTimePeriods='3', "
            "UpperNumberOfTimePeriods='4', TimePeriod='Week'."
        ),
        (
            "Do not deduplicate separately supported SF mentions. If a seizure-type "
            "line and a later narrative repeat the same frequency statement, return "
            "both mentions with separate evidence."
        ),
        (
            "Do not emit SF for a single diagnostic event without ongoing frequency "
            "context, such as 'single focal seizure'."
        ),
        (
            "Do not emit SF for generic episodes, dizzy spells, or aura descriptions "
            "unless a named seizure type and frequency state are explicitly stated."
        ),
        (
            "When the letter says focal seizures are completely under control after "
            "a drug change, render focal seizures with NumberOfSeizures='0' and "
            "PointInTime='DrugChange'."
        ),
        (
            "When the letter says seizures are significantly improved after a drug "
            "change without a count, render generic seizures with "
            "FrequencyChange='Infrequent' and PointInTime='DrugChange'."
        ),
        (
            "When a last-event phrase names focal to bilateral convulsive seizures, "
            "also render the component convulsive seizure seizure-free state if the "
            "letter explicitly supports it."
        ),
        "Return exactly one JSON object. No markdown code fences.",
    ]


def _worked_examples() -> list[dict[str, Any]]:
    return [
        {
            "note_fragment": (
                "Seizure type and frequency: seizures every 3 to 4 weeks. "
                "She has seizures every 3 to 4 weeks."
            ),
            "draft": [{"text": "seizures"}],
            "correct": [
                {
                    "text": "seizures",
                    "attributes": {
                        "NumberOfSeizures": "1",
                        "LowerNumberOfTimePeriods": "3",
                        "UpperNumberOfTimePeriods": "4",
                        "TimePeriod": "Week",
                    },
                    "evidence": "seizures every 3 to 4 weeks",
                    "confidence": "high",
                    "rationale": "The seizure-type line states the rate.",
                },
                {
                    "text": "seizures",
                    "attributes": {
                        "NumberOfSeizures": "1",
                        "LowerNumberOfTimePeriods": "3",
                        "UpperNumberOfTimePeriods": "4",
                        "TimePeriod": "Week",
                    },
                    "evidence": "She has seizures every 3 to 4 weeks",
                    "confidence": "high",
                    "rationale": "The narrative repeats the same independent rate.",
                },
            ],
        },
        {
            "note_fragment": (
                "He had 2 generalised tonic clonic seizures in 2014. "
                "He remains seizure free and is now driving."
            ),
            "draft": [{"text": "seizure free"}],
            "correct": [
                {
                    "text": "generalised tonic clonic seizures",
                    "attributes": {
                        "NumberOfSeizures": "2",
                        "TimeSince_or_TimeOfEvent": "During",
                        "YearDate": "2014",
                    },
                    "evidence": "2 generalised tonic clonic seizures in 2014",
                    "confidence": "high",
                    "rationale": "The historical count is the frequency fact.",
                }
            ],
        },
        {
            "note_fragment": (
                "I think that the focal seizures are completely under control on "
                "lamotrigine 200 mg twice a day."
            ),
            "draft": [{"text": "focal seizures", "attributes": {"FrequencyChange": "Decreased"}}],
            "correct": [
                {
                    "text": "focal seizures",
                    "attributes": {
                        "NumberOfSeizures": "0",
                        "PointInTime": "DrugChange",
                    },
                    "evidence": "focal seizures are completely under control",
                    "confidence": "medium",
                    "rationale": (
                        "Completely under control after medication change is "
                        "seizure-free."
                    ),
                }
            ],
        },
        {
            "note_fragment": (
                "This history is consistent with a single focal seizure secondary "
                "to a known stroke."
            ),
            "draft": [{"text": "single focal seizure"}],
            "correct": [],
        },
        {
            "note_fragment": (
                "She had approximately 3-4 generalised tonic chronic seizures per "
                "week from May to August. She also had very frequent myoclonic jerks."
            ),
            "draft": [{"text": "generalised tonic chronic seizures"}],
            "correct": [
                {
                    "text": "generalised tonic clonic seizures",
                    "attributes": {
                        "LowerNumberOfSeizures": "3",
                        "UpperNumberOfSeizures": "4",
                        "NumberOfTimePeriods": "1",
                        "TimePeriod": "Week",
                        "TimeSince_or_TimeOfEvent": "During",
                    },
                    "evidence": (
                        "3-4 generalised tonic chronic seizures per week from May "
                        "to August"
                    ),
                    "confidence": "high",
                    "rationale": "The source typo chronic is normalized to clonic.",
                },
                {
                    "text": "myoclonic jerks",
                    "attributes": {"FrequencyChange": "Frequent"},
                    "evidence": "very frequent myoclonic jerks",
                    "confidence": "high",
                    "rationale": "Very frequent is a frequency-change state.",
                },
            ],
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
    spec = ENTITY_REGISTRY[SEIZURE_FREQUENCY.name]
    for mention in evidence_valid:
        attrs = dict(mention.attributes)
        for key in ("CUI", "CUIPhrase"):
            if key in attrs:
                attrs.pop(key)
                all_warnings.append(
                    f"{SEIZURE_FREQUENCY.name}: "
                    f"dropped_model_supplied_projection_attribute: {key!r}"
                )
        repaired_attrs, attr_warnings = repair_attributes(attrs, spec=spec)
        all_warnings.extend(f"{SEIZURE_FREQUENCY.name}: {warning}" for warning in attr_warnings)
        predicted_mentions.append(
            PredictedMention(
                entity=SEIZURE_FREQUENCY.name,
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
    program = DspySFVerifier()
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
                    for a in letter.entities(SEIZURE_FREQUENCY.name)
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
    phrase = score_entity(
        gold_letters,
        pred_letters,
        SEIZURE_FREQUENCY.name,
        PHRASE_ONLY,
    )
    semantic = score_entity(
        gold_letters,
        pred_letters,
        SEIZURE_FREQUENCY.name,
        semantic_config_for(SEIZURE_FREQUENCY.name),
    )
    benchmark = score_entity(
        gold_letters,
        pred_letters,
        SEIZURE_FREQUENCY.name,
        benchmark_config_for(SEIZURE_FREQUENCY.name),
    )
    source_near = source_near_diagnostic(
        gold_letters,
        pred_letters,
        [SEIZURE_FREQUENCY.name],
        semantic_config_for,
    ).per_entity[SEIZURE_FREQUENCY.name]
    frequency = score_frequency_state(gold_letters, pred_letters)
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
        "phrase_only": phrase.model_dump(),
        "semantic": semantic.model_dump(),
        "benchmark": benchmark.model_dump(),
        "source_near": source_near.model_dump(),
        "clinical_recovery": {
            "seizure_frequency": frequency.clinical_headline.model_dump(),
            "active_rate": frequency.active_rate.model_dump(),
            "seizure_free": frequency.seizure_free.model_dump(),
            "unknown": frequency.unknown.model_dump(),
            "target_headline_f1": 0.8,
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
    clinical = summary.get("clinical_recovery", {}).get("seizure_frequency", {})
    source_near = summary.get("source_near", {})
    lines = [
        "# ExECTv2 SeizureFrequency Verifier",
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
        f"- Draft SF mentions: {summary.get('n_draft_mentions', 0)}",
        f"- Mentions raw: {summary.get('n_mentions_raw', 0)}",
        f"- Mentions scored: {summary.get('n_mentions_scored', 0)}",
        f"- Evidence-invalid dropped: {summary.get('n_evidence_invalid', 0)}",
        f"- Evidence validity rate: {summary.get('evidence_validity_rate', 0):.4f}",
        "",
        "## SeizureFrequency Clinical-Recovery Headline",
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
                    entity=SEIZURE_FREQUENCY.name,
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
                    entity=SEIZURE_FREQUENCY.name,
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
