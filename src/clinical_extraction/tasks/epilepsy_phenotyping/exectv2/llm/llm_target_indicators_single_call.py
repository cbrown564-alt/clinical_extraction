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

PROMPT_VERSION = "exectv2_target_indicators_single_call_v0.9"
PIPELINE_FAMILY = "exectv2_target_indicators_single_call"
COMPONENT_OWNER = "llm_single_call_target_indicators"
_DIAGNOSIS_ALLOWED_CORE = re.compile(
    r"\b(epilep|seizures?|jme|absence|absences|myoclonic|tonic|clonic|"
    r"convulsive|partial|focal|generalised|generalized|status|grand mal)\b",
    re.IGNORECASE,
)
_PLANNED_PRESCRIPTION_CONTEXT = re.compile(
    r"\b(?:to start|starts?|suggest(?:ed|s|ing)? adding|would suggest|"
    r"plan(?:ned)? to start|if attacks recur|target dose)\b",
    re.IGNORECASE,
)
_PLANNED_INVESTIGATION_CONTEXT = re.compile(
    r"\b(?:will arrange|will request|i will request|to arrange|to request|"
    r"further tests including|await(?:ing)?|planned)\b",
    re.IGNORECASE,
)
_ASYMMETRIC_DOSING = re.compile(
    r"(?P<first>\d+(?:\.\d+)?)\s*mg\b.{0,40}\b(?:mane|morning|am)\b"
    r".{0,80}?(?P<second>\d+(?:\.\d+)?)\s*mg\b.{0,40}\b(?:nocte|night|pm)\b",
    re.IGNORECASE | re.DOTALL,
)

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
                    "Every named epileptic seizure type in a diagnosis, history, "
                    "current-seizure, or frequency statement is also a Diagnosis "
                    "fact, even when you also emit SeizureFrequency."
                ),
                (
                    "Do not extract family history, education, driving advice, or "
                    "hypothetical risk as Diagnosis. Do not extract migraine, "
                    "headache, anxiety, depression, syncope, or learning difficulty "
                    "as Diagnosis."
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
                (
                    "For 'no seizures since <date/year/event>', emit a seizure-free "
                    "SeizureFrequency mention with NumberOfSeizures=0, "
                    "TimeSince_or_TimeOfEvent=Since, and YearDate/MonthDate or "
                    "PointInTime when stated."
                ),
                (
                    "For 'since last clinic' or similar clinic anchors, use "
                    "TimeSince_or_TimeOfEvent=Since and PointInTime=LastClinic."
                ),
                (
                    "For explicit change words such as increased, decreased, better, "
                    "worse, rare, infrequent, or clusters, emit a separate "
                    "SeizureFrequency mention carrying FrequencyChange or the "
                    "stated dated/windowed count."
                ),
                "Use NumberOfTimePeriods=1 with TimePeriod for per-day/week/month/year cadence.",
                (
                    "Do not collapse states: the same seizure anchor can have both "
                    "an active rate and a seizure-free/since-date fact."
                ),
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
                (
                    "Extract completed historical investigations when a result is "
                    "stated, for example a previous CT showing infarct is CT "
                    "performed with abnormal result."
                ),
                (
                    "Do not extract planned, requested, or future tests unless the "
                    "letter also gives a result."
                ),
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
            (
                "Before final JSON, explicitly check whether each named seizure "
                "type appears in both Diagnosis and SeizureFrequency when the "
                "letter gives both the clinical type and a frequency/state."
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
        if mention.entity == "Diagnosis" and not _is_allowed_diagnosis_core(text):
            warnings.append(f"Diagnosis: dropped_non_epilepsy_core: {text!r}")
            continue
        base_mention = PredictedMention(
            entity=mention.entity,
            text=text,
            attributes=attrs,
            evidence=mention.evidence,
            confidence=mention.confidence,
            rationale=mention.rationale,
            component_owner=COMPONENT_OWNER,
        )
        if mention.entity == "Prescription" and _is_planned_prescription(
            base_mention,
            note_text,
        ):
            warnings.append(f"Prescription: dropped_planned_prescription: {text!r}")
            continue
        if mention.entity == "Investigations" and _is_planned_investigation(
            base_mention,
            note_text,
        ):
            warnings.append(f"Investigations: dropped_planned_investigation: {text!r}")
            continue
        expanded_mentions, expansion_warnings = _expand_target_mention(base_mention)
        warnings.extend(f"{mention.entity}: {warning}" for warning in expansion_warnings)
        predicted_mentions.extend(expanded_mentions)
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


def _is_allowed_diagnosis_core(text: str) -> bool:
    return bool(_DIAGNOSIS_ALLOWED_CORE.search(text))


def _is_planned_prescription(mention: PredictedMention, note_text: str) -> bool:
    if mention.entity != "Prescription":
        return False
    context = _local_evidence_context(note_text, mention.evidence, before=96, after=24)
    return bool(_PLANNED_PRESCRIPTION_CONTEXT.search(context))


def _is_planned_investigation(mention: PredictedMention, note_text: str) -> bool:
    if mention.entity != "Investigations":
        return False
    attrs = mention.attributes
    has_result = any(
        attrs.get(key) in {"Normal", "Abnormal", "Unknown"}
        for key in ("EEG_Results", "MRI_Results", "CT_Results")
    )
    if has_result:
        return False
    context = _local_evidence_context(note_text, mention.evidence, before=96, after=24)
    return bool(_PLANNED_INVESTIGATION_CONTEXT.search(context))


def _local_evidence_context(
    note_text: str,
    evidence: str,
    *,
    before: int,
    after: int,
) -> str:
    if not note_text or not evidence:
        return evidence
    lowered_note = note_text.lower()
    lowered_evidence = evidence.lower()
    index = lowered_note.find(lowered_evidence)
    if index < 0:
        return evidence
    start = max(0, index - before)
    end = min(len(note_text), index + len(evidence) + after)
    return note_text[start:end]


def _expand_target_mention(
    mention: PredictedMention,
) -> tuple[list[PredictedMention], list[str]]:
    if mention.entity != "Prescription":
        return [mention], []
    expanded, warnings = _expand_asymmetric_prescription(mention)
    if expanded:
        return expanded, warnings
    return [mention], warnings


def _expand_asymmetric_prescription(
    mention: PredictedMention,
) -> tuple[list[PredictedMention], list[str]]:
    attrs = dict(mention.attributes)
    if attrs.get("DoseUnit") != "mg" or attrs.get("Frequency") != "1":
        return [], []
    match = _ASYMMETRIC_DOSING.search(mention.evidence)
    if not match:
        return [], []
    first = _clean_number(match.group("first"))
    second = _clean_number(match.group("second"))
    if first == second:
        return [], []
    first_attrs = {**attrs, "DrugDose": first, "Frequency": "1"}
    second_attrs = {**attrs, "DrugDose": second, "Frequency": "1"}
    return [
        mention.model_copy(update={"attributes": first_attrs}),
        mention.model_copy(update={"attributes": second_attrs}),
    ], [f"split_asymmetric_same_drug_dosing: {first}/{second} mg"]


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
        {
            "letter_fragment": (
                "Diagnosis: temporal lobe epilepsy with focal seizures with altered "
                "awareness and focal to bilateral convulsive seizures. She has focal "
                "seizures with altered awareness once every 2 weeks and has had no "
                "focal to bilateral convulsive seizures since December 2017."
            ),
            "mentions": [
                {
                    "entity": "Diagnosis",
                    "text": "temporal lobe epilepsy",
                    "attributes": {
                        "DiagCategory": "Epilepsy",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                    "evidence": "temporal lobe epilepsy",
                },
                {
                    "entity": "Diagnosis",
                    "text": "focal seizures with altered awareness",
                    "attributes": {
                        "DiagCategory": "MultipleSeizures",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                    "evidence": "focal seizures with altered awareness",
                },
                {
                    "entity": "Diagnosis",
                    "text": "focal to bilateral convulsive seizures",
                    "attributes": {
                        "DiagCategory": "MultipleSeizures",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                    "evidence": "focal to bilateral convulsive seizures",
                },
                {
                    "entity": "SeizureFrequency",
                    "text": "focal seizures with altered awareness",
                    "attributes": {
                        "NumberOfSeizures": "1",
                        "NumberOfTimePeriods": "2",
                        "TimePeriod": "Week",
                    },
                    "evidence": "focal seizures with altered awareness once every 2 weeks",
                },
                {
                    "entity": "SeizureFrequency",
                    "text": "focal to bilateral convulsive seizures",
                    "attributes": {
                        "NumberOfSeizures": "0",
                        "TimeSince_or_TimeOfEvent": "Since",
                        "MonthDate": "12",
                        "YearDate": "2017",
                    },
                    "evidence": "no focal to bilateral convulsive seizures since December 2017",
                },
            ],
            "note": (
                "Named seizure diagnoses and their frequency states are both target "
                "facts; zero-since statements are not active rates."
            ),
        },
        {
            "letter_fragment": (
                "There was a previous CT scan from 2017 showing a left hemisphere "
                "infarct. I will request an MRI of the brain and EEG."
            ),
            "mentions": [
                {
                    "entity": "Investigations",
                    "text": "CT scan",
                    "attributes": {
                        "CT_Performed": "Yes",
                        "CT_Results": "Abnormal",
                    },
                    "evidence": (
                        "previous CT scan from 2017 showing a left hemisphere infarct"
                    ),
                }
            ],
            "note": (
                "Completed historical CT with a result counts; requested future "
                "MRI/EEG does not."
            ),
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
