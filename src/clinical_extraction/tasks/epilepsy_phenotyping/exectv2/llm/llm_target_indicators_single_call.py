"""Single-call ExECTv2 extractor for the ADR 0030 target indicators."""

from __future__ import annotations

import json
import re
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict

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
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    canonicalize_diagnosis_concept,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_all_entities import (
    MentionRecord,
    _mention_to_row,
    parse_extraction_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    _has_blocking_parse_issue,
    check_evidence,
    repair_attributes,
    write_jsonl,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first_essential_evaluation import (  # noqa: E501
    architecture_report,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.target_indicator_report import (  # noqa: E501
    TARGET_INDICATORS,
    build_target_indicator_report,
    render_target_indicator_markdown,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

PROMPT_VERSION = "exectv2_target_indicators_single_call_v0.4"
PIPELINE_FAMILY = "exectv2_target_indicators_single_call"
COMPONENT_OWNER = "llm_single_call_target_indicators"

Mode = Literal["live", "prompt-only"]


class ExtractionRecord(BaseModel):
    """Four-target extraction output."""

    model_config = ConfigDict(extra="ignore")

    mentions: list[MentionRecord] = []


class ExECTv2TargetIndicatorsSignature(dspy.Signature):
    """Extract the four ADR 0030 target indicators from one clinical letter."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter and four target-indicator instructions."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"mentions\": [{\"entity\": ..., \"text\": ..., "
            "\"attributes\": {...}, \"evidence\": ..., \"confidence\": ..., "
            "\"rationale\": ...}, ...]}"
        )
    )


class DspyTargetIndicatorsExtractor(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(ExECTv2TargetIndicatorsSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def build_prompt_input(letter: ExectLetter) -> str:
    """Build the one-call target-only prompt payload."""

    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": (
            "Read one epilepsy clinic letter and extract ONLY these four ExECTv2 "
            "target indicators: Diagnosis, SeizureFrequency, Prescription, and "
            "Investigations. Candidate generation and final selection happen in this "
            "single response. Deterministic code will later validate evidence, repair "
            "schema/format, normalize attributes, and project CUIs."
        ),
        "output_schema": {
            "entity": f"One of: {', '.join(TARGET_INDICATORS)}.",
            "text": (
                "Short phrase naming the clinical fact. For Diagnosis, use the "
                "normalized core clinical concept when the source includes certainty "
                "words such as probable/possible."
            ),
            "attributes": "String-to-string object; use only legal attributes below.",
            "evidence": (
                "Exact source substring supporting the mention and attributes. Evidence "
                "must appear verbatim in the letter."
            ),
            "confidence": "low | medium | high",
            "rationale": "One short sentence explaining the selection.",
        },
        "attribute_vocabulary": _target_attribute_vocabulary(),
        "indicator_policy": {
            "Diagnosis": [
                (
                    "Extract patient diagnoses: epilepsy, epilepsy syndromes, and "
                    "named epileptic seizure diagnoses."
                ),
                (
                    "Do not extract family history, education, driving advice, or "
                    "hypothetical risk as Diagnosis."
                ),
                (
                    "Split coordinated diagnosis phrases into atomic concepts when "
                    "each is explicitly present."
                ),
                (
                    "Use Certainty 5 for established, 4 for likely/probable, 3 for "
                    "possible/query/suspected."
                ),
                "Use Negation=Affirmed unless the diagnosis is explicitly negated.",
                (
                    "Use DiagCategory=Epilepsy for epilepsy/syndrome, "
                    "MultipleSeizures for plural seizure types, SingleSeizure for a "
                    "single seizure type."
                ),
            ],
            "SeizureFrequency": [
                (
                    "Extract each seizure type with current or stated frequency, "
                    "seizure-free state, or explicit frequency change."
                ),
                "Mention text is the seizure anchor only, not the full frequency clause.",
                (
                    "Use NumberOfSeizures=0 for seizure-free statements with a "
                    "duration, date, or since-anchor."
                ),
                "Use NumberOfTimePeriods=1 with TimePeriod for per-day/week/month/year cadence.",
                "Do not emit bare seizure words with no frequency/state attributes.",
            ],
            "Prescription": [
                "Extract current anti-seizure medication regimens and rescue medication.",
                (
                    "Do not extract stopped, previous, conditional future, or merely "
                    "discussed medications."
                ),
                "Use DrugName, DrugDose, DoseUnit, and Frequency when stated.",
                (
                    "Map once daily to Frequency=1, bd/twice daily to 2, "
                    "tds/three times daily to 3, PRN/rescue to As_Required."
                ),
            ],
            "Investigations": [
                "Extract EEG, MRI, CT, telemetry, and similar investigation statements.",
                "Mention text should be the test phrase, usually EEG, MRI, CT, telemetry, or scan.",
                "Set performed/result/type attributes when explicitly stated.",
                "Normal and abnormal results must be attached to the correct modality.",
            ],
        },
        "worked_examples": _worked_examples(),
        "global_rules": [
            "Return only the four target indicators; omit all other ExECT families.",
            "Evidence must be an exact source substring for every mention.",
            "For non-Diagnosis mentions, text should also be an exact source substring.",
            "Do not invent CUI or CUIPhrase values.",
            "Do not include empty-attribute SeizureFrequency mentions.",
            (
                "Be exhaustive for the target indicators. Clinic letters often contain "
                "more than one Diagnosis and more than one SeizureFrequency fact."
            ),
            (
                "Scan in this order before answering: diagnosis header/impression, "
                "current medication lines, seizure frequency/history paragraphs, "
                "investigation result paragraphs."
            ),
            (
                "Do not collapse target facts. If one sentence contains a diagnosis "
                "and a seizure-frequency state, emit both target mentions."
            ),
            (
                "Named seizure types with current/history frequency usually need both "
                "a Diagnosis mention and a SeizureFrequency mention."
            ),
            (
                "Emit every distinct SeizureFrequency state for the same anchor when "
                "the letter states multiple dates, windows, zero-since facts, or "
                "frequency-change facts."
            ),
            "If no target findings are present, return {\"mentions\": []}.",
            "Return exactly one JSON object. No markdown fences.",
        ],
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def to_predicted_letter(
    letter_id: str,
    mentions: Sequence[MentionRecord],
    *,
    note_text: str,
) -> tuple[PredictedLetter, list[str]]:
    """Validate entity/evidence and apply deterministic schema repair/projection."""

    warnings: list[str] = []
    entity_valid: list[MentionRecord] = []
    for mention in mentions:
        if mention.entity not in TARGET_INDICATORS:
            warnings.append(f"dropped_non_target_entity: {mention.entity!r}")
            continue
        if mention.entity == "SeizureFrequency" and not mention.attributes:
            warnings.append(f"dropped_empty_sf_attributes: {mention.text!r}")
            continue
        entity_valid.append(mention)

    evidence_valid, evidence_invalid, evidence_warnings = check_evidence(
        list(entity_valid),
        note_text=note_text,
    )
    warnings.extend(evidence_warnings)

    predicted_mentions: list[PredictedMention] = []
    for mention in evidence_valid:
        spec = ENTITY_REGISTRY[mention.entity]
        normalized_attrs, normalization_warnings = _normalize_target_attributes(
            mention.entity,
            {str(k): str(v) for k, v in dict(mention.attributes).items()},
        )
        warnings.extend(f"{mention.entity}: {warning}" for warning in normalization_warnings)
        attrs, attr_warnings = repair_attributes(
            normalized_attrs,
            spec=spec,
        )
        warnings.extend(f"{mention.entity}: {warning}" for warning in attr_warnings)
        text, text_warnings = _normalize_target_text(mention.entity, mention.text)
        warnings.extend(f"{mention.entity}: {warning}" for warning in text_warnings)
        predicted_mentions.append(
            PredictedMention(
                entity=mention.entity,
                text=text,
                attributes=attrs,
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
                    "attribute_warnings": warnings,
                },
            )
        ),
        warnings,
    )


def _normalize_target_attributes(
    entity: str,
    attrs: dict[str, str],
) -> tuple[dict[str, str], list[str]]:
    """Format-only normalization before scorer-facing schema repair."""

    normalized = dict(attrs)
    warnings: list[str] = []
    if entity == "Prescription":
        unit = normalized.get("DoseUnit", "").strip().lower()
        if unit in {"milligram", "milligrams", "mgs"}:
            normalized["DoseUnit"] = "mg"
            warnings.append("normalized_dose_unit: milligrams -> mg")
        elif unit in {"gram", "grams"}:
            normalized["DoseUnit"] = "g"
            warnings.append("normalized_dose_unit: grams -> g")
    if entity == "SeizureFrequency":
        period_raw = normalized.get("TimePeriod", "").strip().lower()
        if "last clinic" in period_raw:
            normalized.pop("TimePeriod", None)
            normalized.setdefault("TimeSince_or_TimeOfEvent", "Since")
            normalized.setdefault("PointInTime", "LastClinic")
            warnings.append("normalized_since_last_clinic_period")
        _split_range_attribute(
            normalized,
            source_key="NumberOfSeizures",
            lower_key="LowerNumberOfSeizures",
            upper_key="UpperNumberOfSeizures",
            warnings=warnings,
        )
        _split_range_attribute(
            normalized,
            source_key="NumberOfTimePeriods",
            lower_key="LowerNumberOfTimePeriods",
            upper_key="UpperNumberOfTimePeriods",
            warnings=warnings,
        )
        period = normalized.get("TimePeriod", "").strip().lower()
        period_map = {
            "day": "Day",
            "days": "Day",
            "week": "Week",
            "weeks": "Week",
            "month": "Month",
            "months": "Month",
            "year": "Year",
            "years": "Year",
        }
        if period in period_map:
            normalized["TimePeriod"] = period_map[period]
            if period != period_map[period]:
                warnings.append(f"normalized_time_period: {period} -> {period_map[period]}")
        if normalized.get("TimePeriod") == "Day":
            _convert_day_period_to_week(normalized, warnings)
    return normalized, warnings


def _normalize_target_text(entity: str, text: str) -> tuple[str, list[str]]:
    if entity != "Diagnosis":
        return text, []
    normalized = canonicalize_diagnosis_concept(text)
    if normalized and normalized != text:
        return normalized, [f"normalized_diagnosis_text: {text!r} -> {normalized!r}"]
    return text, []


def _convert_day_period_to_week(attrs: dict[str, str], warnings: list[str]) -> None:
    converted = False
    for key in (
        "NumberOfTimePeriods",
        "LowerNumberOfTimePeriods",
        "UpperNumberOfTimePeriods",
    ):
        if key not in attrs:
            continue
        raw = attrs[key]
        if not raw.isdigit():
            return
        days = int(raw)
        if days % 7 != 0:
            return
        attrs[key] = str(days // 7)
        converted = True
    if converted:
        attrs["TimePeriod"] = "Week"
        warnings.append("converted_day_period_to_week")


def _split_range_attribute(
    attrs: dict[str, str],
    *,
    source_key: str,
    lower_key: str,
    upper_key: str,
    warnings: list[str],
) -> None:
    raw = attrs.get(source_key, "")
    match = re.fullmatch(
        r"\s*(\d+(?:\.\d+)?)\s*(?:-|to|or|/)\s*(\d+(?:\.\d+)?)\s*",
        raw,
        flags=re.IGNORECASE,
    )
    if not match:
        return
    attrs.pop(source_key, None)
    attrs[lower_key] = _clean_number(match.group(1))
    attrs[upper_key] = _clean_number(match.group(2))
    warnings.append(
        f"split_range_attribute: {source_key} -> {lower_key}/{upper_key}"
    )


def _clean_number(value: str) -> str:
    return value[:-2] if value.endswith(".0") else value


def run_split(
    letters: Sequence[ExectLetter],
    *,
    split: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Mode,
    dspy_cache: bool = True,
    api_base: str | None = None,
    progress_every: int | None = None,
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
    resume: bool = False,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    program = DspyTargetIndicatorsExtractor()
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
    existing_rows, completed = read_completed(
        checkpoint_jsonl_path if resume else None,
        key="letter_id",
    )
    requested = set(order)
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
                "pipeline_family": PIPELINE_FAMILY,
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
                    if a.entity in TARGET_INDICATORS
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
    gold_letters, pred_letters = _letters_from_rows(rows)
    arch = architecture_report(
        name=PIPELINE_FAMILY,
        ownership="llm_first_with_deterministic_normalization_projection",
        gold_letters=gold_letters,
        pred_letters=pred_letters,
    )
    routed_like = {
        "pipeline_family": PIPELINE_FAMILY,
        "generated_on": "",
        "split": rows[0].get("split", ""),
        "stage": f"dev{len(rows)}",
        "row_count": len(rows),
        "candidates": [
            {
                "name": PIPELINE_FAMILY,
                "ownership": arch["ownership"],
                "routed_primary_recovery": {
                    "overall": arch["clinical_recovery"]["cui_projected_overall"],
                    "headline_scores": {
                        indicator: arch["clinical_recovery"][
                            "cui_projected_headline_scores"
                        ][indicator]
                        for indicator in TARGET_INDICATORS
                    },
                },
                "routed_primary_errors": {
                    "per_entity": arch["error_taxonomy"]["per_entity"],
                },
            }
        ],
    }
    return {
        "examples": len(rows),
        "call_failures": sum(bool(r.get("call_error")) for r in rows),
        "parse_failures": sum(_has_blocking_parse_issue(r.get("parse_errors")) for r in rows),
        "n_mentions_raw": sum(int(r.get("n_mentions_raw", 0)) for r in rows),
        "n_mentions_scored": sum(int(r.get("n_mentions_scored", 0)) for r in rows),
        "n_evidence_invalid": sum(int(r.get("n_evidence_invalid", 0)) for r in rows),
        "target_report": build_target_indicator_report(routed_like),
    }


def write_report(
    rows: Sequence[dict[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    summary = dict(metadata.get("summary") or summarize_rows(rows))
    target_report = summary["target_report"]
    lines = [
        "# ExECTv2 Target Indicators Single-Call Run",
        "",
        f"- JSONL: `{jsonl_path}`",
        f"- Prompt version: `{metadata.get('prompt_version', PROMPT_VERSION)}`",
        f"- Pipeline family: `{PIPELINE_FAMILY}`",
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
        f"- Mentions scored: {summary.get('n_mentions_scored', 0)}",
        f"- Evidence-invalid dropped: {summary.get('n_evidence_invalid', 0)}",
        "",
        render_target_indicator_markdown(target_report),
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def _letters_from_rows(
    rows: Sequence[dict[str, Any]],
) -> tuple[list[ExectLetter], list[PredictedLetter]]:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (  # noqa: PLC0415
        ExectAnnotation,
        load_letters_for_split,
    )

    split = str(rows[0].get("split", "dev")) if rows else "dev"
    note_by_id = {
        letter.letter_id: letter.note_text
        for letter in load_letters_for_split(split)
    }
    gold_letters = []
    pred_letters = []
    for row in rows:
        letter_id = str(row["letter_id"])
        gold_letters.append(
            ExectLetter(
                letter_id=letter_id,
                note_text=note_by_id.get(letter_id, ""),
                annotations=tuple(
                    ExectAnnotation(
                        entity=str(m["entity"]),
                        text=str(m.get("text", "")),
                        attributes={
                            str(k): str(v)
                            for k, v in dict(m.get("attributes", {})).items()
                        },
                    )
                    for m in row.get("gold_mentions", [])
                    if str(m.get("entity")) in TARGET_INDICATORS
                ),
            )
        )
        pred_letters.append(
            PredictedLetter(
                letter_id=str(row["letter_id"]),
                mentions=tuple(
                    PredictedMention(
                        entity=str(m["entity"]),
                        text=str(m.get("text", "")),
                        attributes={
                            str(k): str(v)
                            for k, v in dict(m.get("attributes", {})).items()
                        },
                        evidence=str(m.get("evidence", "")),
                        confidence=m.get("confidence"),
                        rationale=str(m.get("rationale", "")),
                        component_owner=COMPONENT_OWNER,
                    )
                    for m in row.get("predicted_mentions", [])
                    if str(m.get("entity")) in TARGET_INDICATORS
                ),
            )
        )
    return gold_letters, pred_letters


def _target_attribute_vocabulary() -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for entity in TARGET_INDICATORS:
        spec = ENTITY_REGISTRY[entity]
        attrs: dict[str, Any] = {}
        for attr in sorted(spec.legal_attributes):
            if attr in {"CUI", "CUIPhrase"}:
                attrs[attr] = "Do not emit; deterministic projection handles this."
            elif attr in spec.closed_vocab:
                attrs[attr] = sorted(spec.closed_vocab[attr])
            else:
                attrs[attr] = "string copied or normalized from the letter"
        out[entity] = attrs
    return out


def _worked_examples() -> list[dict[str, Any]]:
    return [
        {
            "letter_fragment": (
                "Diagnosis: probable focal epilepsy. She has focal seizures twice "
                "a month. Current medication is lamotrigine 100 mg bd. MRI was normal."
            ),
            "mentions": [
                {
                    "entity": "Diagnosis",
                    "text": "focal epilepsy",
                    "attributes": {
                        "DiagCategory": "Epilepsy",
                        "Certainty": "4",
                        "Negation": "Affirmed",
                    },
                    "evidence": "probable focal epilepsy",
                },
                {
                    "entity": "SeizureFrequency",
                    "text": "focal seizures",
                    "attributes": {
                        "NumberOfSeizures": "2",
                        "NumberOfTimePeriods": "1",
                        "TimePeriod": "Month",
                    },
                    "evidence": "focal seizures twice a month",
                },
                {
                    "entity": "Prescription",
                    "text": "lamotrigine 100 mg bd",
                    "attributes": {
                        "DrugName": "lamotrigine",
                        "DrugDose": "100",
                        "DoseUnit": "mg",
                        "Frequency": "2",
                    },
                    "evidence": "lamotrigine 100 mg bd",
                },
                {
                    "entity": "Investigations",
                    "text": "MRI",
                    "attributes": {"MRI_Performed": "Yes", "MRI_Results": "Normal"},
                    "evidence": "MRI was normal",
                },
            ],
        },
        {
            "letter_fragment": (
                "He previously tried carbamazepine. If attacks recur we may start "
                "levetiracetam. No EEG has been arranged."
            ),
            "mentions": [
                {
                    "entity": "Investigations",
                    "text": "EEG",
                    "attributes": {"EEG_Performed": "No"},
                    "evidence": "No EEG has been arranged",
                }
            ],
            "note": "Previous and conditional future medications are not current prescriptions.",
        },
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
        write_report(
            rows,
            {
                "prompt_version": PROMPT_VERSION,
                "split": split,
                "model": model,
                "mode": mode,
                "summary": summary,
            },
            report_path.with_name(f"{report_path.stem}_checkpoint{report_path.suffix}"),
            jsonl_path=jsonl_path,
        )
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
        file=sys.stderr,
        flush=True,
    )
