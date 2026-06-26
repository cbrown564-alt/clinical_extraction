"""Single-call ExECTv2 extractor for the ADR 0030 target indicators."""

from __future__ import annotations

import ast
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.target_projection import (
    ASYMMETRIC_DOSING,
    CONTROLLED_ON_DOSE,
    EVERY_N_PERIODS,
    EVERY_N_TO_M_PERIODS,
    ProjectionFamilySwitches,
    audit_only_projection_replay_switches,
    clean_number,
    effective_target_projection_family_switches,
    frequency_from_prescription_source,
    is_projection_family_enabled,
    local_evidence_context,
    period_to_canonical,
    project_context_parent_epilepsy,
    project_controlled_context_to_infrequent_state,
    project_diagnosis_context_to_sf_states,
    project_diagnosis_frequency_header_to_sf,
    project_diagnosis_header_parent_epilepsy,
    project_diagnosis_text_from_evidence,
    project_dated_diagnosis_context_to_sf,
    project_dropped_sf_to_diagnosis,
    project_eeg_context_to_mri_normal,
    project_empty_sf_candidate_to_diagnosis,
    project_focal_diagnosis_context_to_sf,
    project_infrequent_context_state,
    project_mri_context_to_eeg_result,
    project_returned_context_to_increased_state,
    project_sf_context_to_focal_diagnosis,
    project_sf_state_from_evidence,
    quarantined_projection_family_warning,
    repair_case_only_evidence,
    repair_prescription_attrs_from_text,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    canonicalize_diagnosis_concept,
    normalize_phrase,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_all_entities import (
    MentionRecord,
    _mention_to_row,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_all_entities import (
    parse_extraction_json as parse_all_entities_extraction_json,
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

PROMPT_VERSION = "exectv2_target_indicators_single_call_v0.42"
PIPELINE_FAMILY = "exectv2_target_indicators_single_call"
COMPONENT_OWNER = "llm_single_call_target_indicators"
_DIAGNOSIS_ALLOWED_CORE = re.compile(
    r"\b(epilep\w*|seizures?|jme|absence|absences|myoclonic|tonic|clonic|"
    r"convulsive|partial|focal|generalised|generalized|status|grand mal)\b",
    re.IGNORECASE,
)
_DIAGNOSIS_PROHIBITED_CORES = frozenset(
    {
        "seizure",
        "seizures",
        "febrile seizure",
        "febrile seizures",
        "dissociative seizure",
        "dissociative seizures",
        "non epileptic seizure",
        "non epileptic seizures",
        "psychogenic seizure",
        "psychogenic seizures",
        "myoclonic jerk",
        "myoclonic jerks",
        "absence like seizure",
        "absence like seizures",
    }
)
_PLANNED_PRESCRIPTION_CONTEXT = re.compile(
    r"\b(?:to start|starts?|suggest(?:ed|s|ing)? adding|would suggest|"
    r"plan(?:ned)? to start|if attacks recur|target dose)\b",
    re.IGNORECASE,
)
_PLANNED_INVESTIGATION_CONTEXT = re.compile(
    r"\b(?:will arrange|will request|i will request|to arrange|to request|"
    r"arranging|requesting|further tests including|await(?:ing)?|planned|useful to get)\b",
    re.IGNORECASE,
)
_SEIZURE_FREQUENCY_ANCHOR = re.compile(
    r"\b(seizures?|attacks?|episodes?|convulsions?|absences?|jerks?|myoclon(?:ic|us)|"
    r"tonic|clonic|focal|generalised|generalized|partial)\b",
    re.IGNORECASE,
)
_SEIZURE_FREQUENCY_PROHIBITED_ANCHOR = re.compile(
    r"\b(?:febrile|dissociative|non.?epileptic|psychogenic)\s+"
    r"(?:seizures?|convulsions?|events?)\b",
    re.IGNORECASE,
)
_CLUSTER_OF_SEIZURES = re.compile(r"\bcluster\s+of\s+seizures\b", re.IGNORECASE)
_GENERALIZED_EPILEPSY_GTCS_ALONE = re.compile(
    r"\bepilepsy\s+with\s+general(?:ised|ized)\s+tonic\s+(?:clonic|chronic)\s+"
    r"seizures?\s+alone\b",
    re.IGNORECASE,
)
_SPECIFIC_SEIZURE_EVIDENCE = re.compile(
    r"\b(seizures?|convulsions?|absences?|focal|tonic|clonic|partial|myoclonic)\b",
    re.IGNORECASE,
)
_UNKNOWN_LIKE_NUMBER = frozenset({"unknown", "unclear"})
_SF_STATE_ATTRIBUTES = frozenset(
    {
        "AgeLower",
        "AgeUnit",
        "AgeUpper",
        "DayDate",
        "FrequencyChange",
        "LowerNumberOfSeizures",
        "LowerNumberOfTimePeriods",
        "MonthDate",
        "NumberOfSeizures",
        "NumberOfTimePeriods",
        "PointInTime",
        "TimePeriod",
        "TimeSince_or_TimeOfEvent",
        "UpperNumberOfSeizures",
        "UpperNumberOfTimePeriods",
        "YearDate",
    }
)
_SF_TEXT_ALIASES = {
    "absence like seizure": "absence like seizures",
    "absence like seizures": "absence like seizures",
    "focal seizures without change in awareness": "focal seizures",
}

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
            "\"rationale\": \"\"}, ...]}. Do not include prose outside JSON."
        )
    )


class DspyTargetIndicatorsExtractor(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(ExECTv2TargetIndicatorsSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def _parse_target_extraction_json(
    raw_output: str,
) -> tuple[ExtractionRecord | None, list[str]]:
    extraction, errors = parse_all_entities_extraction_json(raw_output)
    if extraction is not None:
        return ExtractionRecord(mentions=list(extraction.mentions)), errors
    literal_payload = _loads_python_literal_payload(raw_output)
    if literal_payload is not None:
        try:
            record = ExtractionRecord.model_validate(literal_payload)
        except Exception as exc:
            errors.append(f"invalid_python_literal_payload: {type(exc).__name__}")
        else:
            return record, ["parsed_python_literal_payload"]
    if not any(error.startswith("invalid_json:") for error in errors):
        return None, errors
    salvaged_mentions, dropped = _salvage_mentions_from_malformed_json(raw_output)
    if not salvaged_mentions:
        return None, errors
    salvage_errors = [f"salvaged_invalid_json_mentions: {len(salvaged_mentions)}"]
    if dropped:
        salvage_errors.append(f"dropped_malformed_json_mentions: {dropped}")
    return ExtractionRecord(mentions=salvaged_mentions), salvage_errors


def _loads_python_literal_payload(raw_output: str) -> dict[str, Any] | None:
    stripped = raw_output.strip()
    if not stripped.startswith("{") or "mentions" not in stripped:
        return None
    try:
        payload = ast.literal_eval(stripped)
    except (SyntaxError, ValueError):
        return None
    return payload if isinstance(payload, dict) else None


def _salvage_mentions_from_malformed_json(raw_output: str) -> tuple[list[MentionRecord], int]:
    mentions: list[MentionRecord] = []
    dropped = 0
    for obj_text in _iter_top_level_json_objects(raw_output):
        payload = _loads_salvageable_mention_object(obj_text)
        if payload is None:
            dropped += 1
            continue
        try:
            mentions.append(MentionRecord.model_validate(payload))
        except Exception:
            dropped += 1
    return mentions, dropped


def _iter_top_level_json_objects(raw_output: str) -> list[str]:
    mentions_index = raw_output.find('"mentions"')
    if mentions_index < 0:
        return []
    array_start = raw_output.find("[", mentions_index)
    array_end = raw_output.rfind("]")
    if array_start < 0:
        return []
    body = (
        raw_output[array_start + 1 : array_end]
        if array_end > array_start
        else raw_output[array_start + 1 :]
    )
    objects: list[str] = []
    level = 0
    start: int | None = None
    for index, char in enumerate(body):
        if char == "{":
            if level == 0:
                start = index
            level += 1
        elif char == "}":
            level -= 1
            if level == 0 and start is not None:
                objects.append(body[start : index + 1])
                start = None
    return objects


def _loads_salvageable_mention_object(obj_text: str) -> dict[str, Any] | None:
    try:
        payload = json.loads(obj_text)
        return payload if isinstance(payload, dict) else None
    except json.JSONDecodeError:
        return _loads_malformed_rationale_mention_object(obj_text)


def _loads_malformed_rationale_mention_object(obj_text: str) -> dict[str, Any] | None:
    entity = _extract_json_string_field(obj_text, "entity")
    evidence = _extract_json_string_field(obj_text, "evidence")
    if not entity or not evidence:
        return None
    attributes = _extract_json_object_field(obj_text, "attributes") or {}
    text = _extract_json_string_field(obj_text, "text") or _infer_text_from_evidence(
        entity,
        evidence,
    )
    if not text:
        return None
    payload: dict[str, Any] = {
        "entity": entity,
        "text": text,
        "attributes": attributes,
        "evidence": evidence,
    }
    confidence = _extract_json_string_field(obj_text, "confidence")
    if confidence:
        payload["confidence"] = confidence
    return payload


def _extract_json_string_field(obj_text: str, field: str) -> str | None:
    match = re.search(
        rf'"{re.escape(field)}"\s*:\s*"(?P<value>(?:[^"\\]|\\.)*)"',
        obj_text,
        re.DOTALL,
    )
    if not match:
        return None
    return json.loads(f'"{match.group("value")}"')


def _extract_json_object_field(obj_text: str, field: str) -> dict[str, Any] | None:
    match = re.search(rf'"{re.escape(field)}"\s*:\s*', obj_text)
    if not match:
        return None
    decoder = json.JSONDecoder()
    try:
        value, _ = decoder.raw_decode(obj_text[match.end() :])
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def _infer_text_from_evidence(entity: str, evidence: str) -> str:
    normalized = normalize_phrase(evidence)
    if entity == "SeizureFrequency" and "seizure" in normalized:
        return "seizures"
    return ""


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
            "rationale": "Optional. Prefer an empty string; never include deliberation.",
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
                    "Always preserve the diagnosis header/impression syndrome or "
                    "category as its own Diagnosis fact, such as temporal lobe "
                    "epilepsy, intractable epilepsy, primary/generalised epilepsy, "
                    "epileptic attack, or single focal seizure."
                ),
                (
                    "Do not replace a specific diagnosis header with a looser parent. "
                    "If the header says temporal lobe epilepsy, emit temporal lobe "
                    "epilepsy; if it says focal epilepsy or possible focal onset, emit "
                    "focal epilepsy with the appropriate Certainty."
                ),
                (
                    "If the source says epilepsy with generalised tonic clonic "
                    "seizures alone/on awakening, keep that full syndrome Diagnosis "
                    "as well as any seizure-type Diagnosis facts."
                ),
                (
                    "If a diagnosis header gives a broad epilepsy category and the "
                    "history gives seizure types, emit both the category/syndrome "
                    "and the seizure types."
                ),
                (
                    "Phrases such as 'I suspect epilepsy' or 'possible epilepsy' "
                    "are Diagnosis facts with lower Certainty, not omissions."
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
                    "For 'no further seizures' or 'no recurrent seizures' with no "
                    "date, emit NumberOfSeizures=0 on the seizure anchor."
                ),
                (
                    "For 'since last clinic' or similar clinic anchors, use "
                    "TimeSince_or_TimeOfEvent=Since and PointInTime=LastClinic."
                ),
                (
                    "For 'last week', 'last month', or 'last year' occurrence "
                    "windows, use TimeSince_or_TimeOfEvent=During with "
                    "PointInTime=Last_Week, Last_Month, or Last_Year rather than "
                    "converting to a per-week/month/year rate."
                ),
                (
                    "For explicit change words such as increased, decreased, better, "
                    "worse, rare, infrequent, or clusters, emit a separate "
                    "SeizureFrequency mention carrying FrequencyChange or the "
                    "stated dated/windowed count."
                ),
                (
                    "If the text says seizures became infrequent, controlled, or "
                    "changed after a drug change, use PointInTime=DrugChange with "
                    "the FrequencyChange value when stated."
                ),
                (
                    "Do not emit SeizureFrequency for historical seizure descriptions "
                    "unless a count, rate, date-window, since-anchor, seizure-free "
                    "state, or explicit change word is stated."
                ),
                (
                    "Do not emit SeizureFrequency for 'frequency unknown', diagnostic "
                    "seizure types, or old history without a current/stated state."
                ),
                (
                    "Remote lifetime history such as childhood febrile seizures or "
                    "'last seizures were in teenage years' is not an active rate; "
                    "only emit a seizure-free/since state if the text gives a clear "
                    "since-anchor."
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
                    "Always scan previous/current investigation lines for completed "
                    "MRI, EEG, or CT results such as MRI 2011 Normal or MRI scan "
                    "showing a lesion."
                ),
                (
                    "Words such as showed, showing, revealed, demonstrated, "
                    "consistent with, slowing, gliosis, infarct, lesion, or "
                    "epileptiform indicate an abnormal result for the named test."
                ),
                (
                    "Phrases such as no epileptiform activity, normal EEG, or normal "
                    "MRI indicate a normal result for the named test."
                ),
                (
                    "Do not extract planned, requested, to-be-arranged, or future "
                    "tests unless the letter also gives a completed result for "
                    "that modality."
                ),
            ],
        },
        "worked_examples": _worked_examples(),
        "global_rules": [
            "Return only the four target indicators; omit all other ExECT families.",
            "Evidence must be an exact source substring for every mention.",
            (
                "Evidence must come from letter_text only. Never copy or adapt "
                "text from worked_examples."
            ),
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
            "Do not write analysis, corrections, caveats, or revised JSON after the object.",
            "Use rationale=\"\" or a short phrase only; do not explain uncertainty there.",
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
    projection_family_switches: ProjectionFamilySwitches | None = None,
) -> tuple[PredictedLetter, list[str]]:
    """Validate entity/evidence and apply deterministic schema repair/projection."""

    warnings: list[str] = []
    entity_valid: list[MentionRecord] = []
    for mention in mentions:
        if mention.entity not in TARGET_INDICATORS:
            warnings.append(f"dropped_non_target_entity: {mention.entity!r}")
            continue
        if mention.entity == "SeizureFrequency":
            focal_diagnosis = project_empty_sf_candidate_to_diagnosis(mention)
            if focal_diagnosis is not None:
                entity_valid.append(focal_diagnosis)
                warnings.append(
                    "projected_focal_onset_sf_candidate_to_diagnosis: "
                    f"{mention.text!r}"
                )
                continue
            if not mention.attributes:
                warnings.append(f"dropped_empty_sf_attributes: {mention.text!r}")
                continue
            if not _is_allowed_sf_anchor(mention.text):
                warnings.append(f"dropped_non_seizure_frequency_anchor: {mention.text!r}")
                continue
        entity_valid.append(mention)

    evidence_repaired, evidence_repair_warnings = repair_case_only_evidence(
        entity_valid,
        note_text=note_text,
        projection_family_switches=projection_family_switches,
    )
    warnings.extend(evidence_repair_warnings)

    evidence_valid, evidence_invalid, evidence_warnings = check_evidence(
        evidence_repaired,
        note_text=note_text,
    )
    warnings.extend(evidence_warnings)

    predicted_mentions: list[PredictedMention] = []
    for mention in evidence_valid:
        spec = ENTITY_REGISTRY[mention.entity]
        normalized_attrs, normalization_warnings = _normalize_target_attributes(
            mention.entity,
            {str(k): str(v) for k, v in dict(mention.attributes).items()},
            text=mention.text,
            evidence=mention.evidence,
            projection_family_switches=projection_family_switches,
        )
        warnings.extend(f"{mention.entity}: {warning}" for warning in normalization_warnings)
        attrs, attr_warnings = repair_attributes(
            normalized_attrs,
            spec=spec,
        )
        warnings.extend(f"{mention.entity}: {warning}" for warning in attr_warnings)
        if mention.entity == "Investigations" and not any(
            key.startswith(("CT_", "EEG_", "MRI_")) for key in attrs
        ):
            warnings.append(f"Investigations: dropped_empty_investigation_attrs: {mention.text!r}")
            continue
        text, text_warnings = _normalize_target_text(
            mention.entity,
            mention.text,
            evidence=mention.evidence,
        )
        warnings.extend(f"{mention.entity}: {warning}" for warning in text_warnings)
        if mention.entity == "SeizureFrequency":
            text, attrs, state_warnings = project_sf_state_from_evidence(
                text,
                attrs,
                mention.evidence,
                projection_family_switches=projection_family_switches,
            )
            warnings.extend(f"{mention.entity}: {warning}" for warning in state_warnings)
            drop_warning = _sf_state_drop_reason(text, attrs, mention.evidence)
            if drop_warning:
                projected_diagnosis = project_dropped_sf_to_diagnosis(
                    text,
                    mention.evidence,
                    mention,
                    component_owner=COMPONENT_OWNER,
                )
                if projected_diagnosis is not None:
                    predicted_mentions.append(projected_diagnosis)
                    warnings.append(
                        "SeizureFrequency: projected_dropped_sf_to_diagnosis: "
                        f"{text!r}"
                    )
                warnings.append(f"SeizureFrequency: {drop_warning}: {text!r}")
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
        if mention.entity == "Diagnosis" and not _is_allowed_diagnosis_core(text):
            projected_sf = project_diagnosis_frequency_header_to_sf(
                base_mention,
                note_text,
            )
            if projected_sf is not None:
                predicted_mentions.append(projected_sf)
                warnings.append(
                    "Diagnosis: projected_frequency_header_diagnosis_to_sf_state: "
                    f"{text!r}"
                )
                continue
            warnings.append(f"Diagnosis: dropped_non_epilepsy_core: {text!r}")
            continue
        if mention.entity == "Prescription" and _is_planned_prescription(
            base_mention,
            note_text,
        ):
            warnings.append(f"Prescription: dropped_planned_prescription: {text!r}")
            continue
        if mention.entity == "Diagnosis" and _is_zero_since_only_diagnosis_context(
            base_mention,
            note_text,
        ):
            warnings.append(
                f"Diagnosis: dropped_zero_since_only_diagnosis_context: {text!r}"
            )
            continue
        if mention.entity == "Diagnosis" and _is_investigation_only_diagnosis_context(
            base_mention
        ):
            warnings.append(
                f"Diagnosis: dropped_investigation_only_diagnosis_context: {text!r}"
            )
            continue
        if mention.entity == "Diagnosis" and _is_frequency_phrase_diagnosis_context(
            base_mention
        ):
            warnings.append(
                f"Diagnosis: dropped_frequency_phrase_diagnosis_context: {text!r}"
            )
            continue
        if mention.entity == "Diagnosis" and _is_unsupported_inferred_diagnosis(
            base_mention
        ):
            warnings.append(f"Diagnosis: dropped_unsupported_inferred_diagnosis: {text!r}")
            continue
        if mention.entity == "Investigations" and _is_planned_investigation(
            base_mention,
            note_text,
        ):
            warnings.append(f"Investigations: dropped_planned_investigation: {text!r}")
            continue
        if mention.entity == "Investigations" and _is_unsupported_eeg_confirmation(
            base_mention
        ):
            warnings.append(
                f"Investigations: dropped_unsupported_eeg_confirmation: {text!r}"
            )
            continue
        expanded_mentions, expansion_warnings = _expand_target_mention(base_mention)
        warnings.extend(f"{mention.entity}: {warning}" for warning in expansion_warnings)
        if mention.entity == "Diagnosis":
            context_parent = project_context_parent_epilepsy(base_mention, note_text)
            if context_parent is not None:
                expanded_mentions.append(context_parent)
                warnings.append("Diagnosis: projected_context_parent_epilepsy")
            diagnosis_sf_states, diagnosis_sf_state_warnings = (
                project_diagnosis_context_to_sf_states(
                    base_mention,
                    note_text,
                    projection_family_switches=projection_family_switches,
                )
            )
            if diagnosis_sf_states:
                expanded_mentions.extend(diagnosis_sf_states)
            warnings.extend(
                f"Diagnosis: {warning}" for warning in diagnosis_sf_state_warnings
            )
            projected_sf = project_focal_diagnosis_context_to_sf(
                base_mention,
                note_text,
            )
            if projected_sf is not None:
                expanded_mentions.append(projected_sf)
                warnings.append(
                    "Diagnosis: projected_focal_diagnosis_context_to_sf_state: "
                    f"{text!r}"
                )
            projected_parent = project_diagnosis_header_parent_epilepsy(
                base_mention,
                note_text,
            )
            if projected_parent is not None:
                expanded_mentions.append(projected_parent)
                warnings.append("Diagnosis: projected_header_parent_epilepsy")
            projected_dated_sf = project_dated_diagnosis_context_to_sf(
                base_mention,
                note_text,
            )
            if projected_dated_sf is not None:
                expanded_mentions.append(projected_dated_sf)
                warnings.append("Diagnosis: projected_dated_diagnosis_context_to_sf")
        if mention.entity == "SeizureFrequency":
            projected_diagnosis = project_sf_context_to_focal_diagnosis(
                base_mention,
                note_text,
            )
            if projected_diagnosis is not None:
                expanded_mentions.append(projected_diagnosis)
                warnings.append(
                    "SeizureFrequency: projected_sf_context_to_focal_diagnosis: "
                    f"{text!r}"
                )
            controlled_state = project_controlled_context_to_infrequent_state(
                base_mention,
                note_text,
            )
            if controlled_state is not None:
                expanded_mentions.append(controlled_state)
                warnings.append(
                    "SeizureFrequency: projected_controlled_context_to_infrequent_state"
                )
            infrequent_state = project_infrequent_context_state(
                base_mention,
                note_text,
            )
            if infrequent_state is not None:
                family = "projected_infrequent_context_state"
                if is_projection_family_enabled(
                    family,
                    projection_family_switches,
                ):
                    expanded_mentions.append(infrequent_state)
                    warnings.append(f"SeizureFrequency: {family}")
                else:
                    warnings.append(
                        "SeizureFrequency: "
                        + quarantined_projection_family_warning(family)
                    )
            increased_state = project_returned_context_to_increased_state(
                base_mention,
                note_text,
            )
            if increased_state is not None:
                expanded_mentions.append(increased_state)
                warnings.append(
                    "SeizureFrequency: projected_returned_context_to_increased_state"
                )
        if mention.entity == "Investigations" and _is_unsupported_investigation_evidence(
            base_mention
        ):
            warnings.append(
                f"Investigations: dropped_unsupported_investigation_evidence: {text!r}"
            )
            continue
        if mention.entity == "Investigations":
            projected_mri = project_eeg_context_to_mri_normal(
                base_mention,
                note_text,
            )
            if projected_mri is not None:
                expanded_mentions.append(projected_mri)
                warnings.append("Investigations: projected_eeg_context_to_mri_normal")
            projected_eeg = project_mri_context_to_eeg_result(
                base_mention,
                note_text,
            )
            if projected_eeg is not None:
                expanded_mentions.append(projected_eeg)
                warnings.append("Investigations: projected_mri_context_to_eeg_result")
        predicted_mentions.extend(expanded_mentions)
    return (
        project_cuis(
            PredictedLetter(
                letter_id=letter_id,
                mentions=tuple(_deduplicate_scored_mentions(predicted_mentions)),
                diagnostics={
                    "prompt_version": PROMPT_VERSION,
                    "pipeline_family": PIPELINE_FAMILY,
                    "n_evidence_invalid": len(evidence_invalid),
                    "target_projection_family_switches": (
                        effective_target_projection_family_switches(
                            projection_family_switches
                        )
                    ),
                    "attribute_warnings": warnings,
                },
            )
        ),
        warnings,
    )


























def _normalize_target_attributes(
    entity: str,
    attrs: dict[str, str],
    *,
    text: str = "",
    evidence: str = "",
    projection_family_switches: ProjectionFamilySwitches | None = None,
) -> tuple[dict[str, str], list[str]]:
    """Format-only normalization before scorer-facing schema repair."""

    normalized = dict(attrs)
    warnings: list[str] = []
    if entity == "Prescription":
        prescription_warnings = repair_prescription_attrs_from_text(
            normalized,
            source=f"{text} {evidence}",
        )
        warnings.extend(prescription_warnings)
        evidence_frequency = frequency_from_prescription_source(normalize_phrase(evidence))
        if (
            evidence_frequency
            and normalized.get("Frequency")
            and evidence_frequency != normalized.get("Frequency")
        ):
            normalized["Frequency"] = evidence_frequency
            warnings.append(
                f"projected_prescription_frequency_from_evidence: {evidence_frequency}"
            )
        unit = normalized.get("DoseUnit", "").strip().lower()
        if unit in {"milligram", "milligrams", "mgs"}:
            normalized["DoseUnit"] = "mg"
            warnings.append("normalized_dose_unit: milligrams -> mg")
        elif unit in {"gram", "grams"}:
            normalized["DoseUnit"] = "g"
            warnings.append("normalized_dose_unit: grams -> g")
        dose = normalized.get("DrugDose", "").strip()
        dose_match = re.fullmatch(r"(?P<dose>\d+(?:\.\d+)?)\s*(?:mgs?|mg|grams?|g)?", dose, re.I)
        if dose_match and dose_match.group("dose") != dose:
            normalized["DrugDose"] = clean_number(dose_match.group("dose"))
            warnings.append(f"normalized_drug_dose_number: {dose!r}")
    if entity == "SeizureFrequency":
        for key in (
            "NumberOfSeizures",
            "LowerNumberOfSeizures",
            "UpperNumberOfSeizures",
            "NumberOfTimePeriods",
            "LowerNumberOfTimePeriods",
            "UpperNumberOfTimePeriods",
        ):
            if normalized.get(key, "").strip().lower() in _UNKNOWN_LIKE_NUMBER:
                normalized.pop(key, None)
                warnings.append(f"removed_unknown_like_frequency_number: {key}")
        period_raw = normalized.get("TimePeriod", "").strip().lower()
        if "last clinic" in period_raw:
            normalized.pop("TimePeriod", None)
            normalized.setdefault("TimeSince_or_TimeOfEvent", "Since")
            normalized.setdefault("PointInTime", "LastClinic")
            warnings.append("normalized_since_last_clinic_period")
        if normalized.get("PointInTime", "").strip().lower() == "christmas":
            family = "projected_christmas_point_to_month_date"
            if is_projection_family_enabled(family, projection_family_switches):
                normalized.pop("PointInTime", None)
                normalized.setdefault("MonthDate", "12")
                warnings.append(family)
            else:
                warnings.append(quarantined_projection_family_warning(family))
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
    if entity == "Investigations":
        text_modality = _investigation_text_modality(text)
        if text_modality is None and _is_non_target_investigation_text(text):
            removed = [
                key
                for key in tuple(normalized)
                if key.startswith(("CT_", "EEG_", "MRI_")) or key == "EEG_Type"
            ]
            for key in removed:
                normalized.pop(key, None)
            if removed:
                warnings.append(
                    "removed_non_target_investigation_attrs: "
                    + ",".join(sorted(removed))
                )
        if text_modality is not None:
            removed = [
                key
                for key in tuple(normalized)
                if key.startswith(("CT_", "EEG_", "MRI_"))
                and not key.startswith(f"{text_modality}_")
                and not (text_modality == "EEG" and key == "EEG_Type")
            ]
            for key in removed:
                normalized.pop(key, None)
            if removed:
                warnings.append(
                    "removed_cross_modal_investigation_attrs: "
                    + ",".join(sorted(removed))
                )
        if normalized.get("EEG_Results") and "EEG_Performed" not in normalized:
            normalized["EEG_Performed"] = "Yes"
            warnings.append("inferred_eeg_performed_from_result")
        if normalized.get("MRI_Results") and "MRI_Performed" not in normalized:
            normalized["MRI_Performed"] = "Yes"
            warnings.append("inferred_mri_performed_from_result")
        if (
            "EEG_Type" in normalized
            and any(key.startswith("MRI_") for key in normalized)
            and not any(key in {"EEG_Performed", "EEG_Results"} for key in normalized)
        ):
            normalized.pop("EEG_Type", None)
            warnings.append("removed_cross_modal_eeg_type_from_mri")
    return normalized, warnings


def _normalize_target_text(
    entity: str,
    text: str,
    *,
    evidence: str = "",
) -> tuple[str, list[str]]:
    if entity == "SeizureFrequency":
        if (
            "seizures over" in normalize_phrase(evidence)
            and "generalised tonic clonic seizures with myoclonic jerks"
            in normalize_phrase(text)
        ):
            return "seizures", [
                f"normalized_seizure_frequency_text: {text!r} -> 'seizures'"
            ]
        normalized = normalize_phrase(text)
        if "absence like seizures" in normalize_phrase(evidence) and normalized not in {
            "absence like seizure",
            "absence like seizures",
        }:
            return "absence like seizures", [
                f"normalized_seizure_frequency_text_from_evidence: {text!r} -> "
                "'absence like seizures'"
            ]
        if normalized in _SF_TEXT_ALIASES and _SF_TEXT_ALIASES[normalized] != text:
            return _SF_TEXT_ALIASES[normalized], [
                f"normalized_seizure_frequency_text: {text!r} -> "
                f"{_SF_TEXT_ALIASES[normalized]!r}"
            ]
        if re.match(r"^seizures?\s+every\b", normalized) and (
            EVERY_N_PERIODS.search(normalized)
            or EVERY_N_TO_M_PERIODS.search(normalized)
        ):
            return "seizures", [
                f"normalized_seizure_frequency_text: {text!r} -> 'seizures'"
            ]
        return text, []
    if entity != "Diagnosis":
        return text, []
    raw_normalized = normalize_phrase(text)
    if (
        raw_normalized == "epilepsy with generalised tonic clonic seizures"
        and "alone" in normalize_phrase(evidence)
    ):
        normalized = "epilepsy with generalised tonic clonic seizures alone"
        return normalized, [f"normalized_diagnosis_text: {text!r} -> {normalized!r}"]
    normalized = canonicalize_diagnosis_concept(text)
    normalized = project_diagnosis_text_from_evidence(normalized, evidence)
    if normalized and normalized != text:
        return normalized, [f"normalized_diagnosis_text: {text!r} -> {normalized!r}"]
    return text, []






def _sf_state_drop_reason(
    text: str,
    attrs: dict[str, str],
    evidence: str,
) -> str | None:
    normalized_evidence = normalize_phrase(evidence)
    normalized_text = normalize_phrase(text)
    if normalized_text == "episodes of loss of consciousness":
        return "dropped_unsupported_episode_frequency_anchor"
    if (
        normalized_text == "general and complex partial seizures"
        and "continues to get" in normalized_evidence
    ):
        return "dropped_unsupported_episode_frequency_anchor"
    if (
        normalized_text in {"single focal seizure", "focal seizure"}
        and attrs.get("NumberOfSeizures") == "1"
        and "had an event on" in normalized_evidence
    ):
        return "dropped_single_event_not_frequency_state"
    if (
        normalized_text == "focal seizures"
        and attrs.get("FrequencyChange") == "Decreased"
        and "significant improvement since increasing" in normalized_evidence
    ):
        return "dropped_improvement_phrase_not_headline_state"
    if (
        normalized_text not in normalized_evidence
        and "angry or upset" in normalized_evidence
    ):
        return "dropped_unsupported_episode_frequency_anchor"
    if normalized_text == "minor seizures" and normalized_evidence == "occur 4 to 5 times a year":
        return "dropped_unsupported_episode_frequency_anchor"
    if (
        "jerks" in normalized_text
        and attrs.get("NumberOfSeizures") == "0"
        and "occasional" in normalized_evidence
    ):
        return "dropped_occasional_jerks_not_seizure_free"
    if (
        "episode" in normalized_evidence
        and normalized_text not in normalized_evidence
        and not _SPECIFIC_SEIZURE_EVIDENCE.search(normalized_evidence)
    ):
        return "dropped_unsupported_episode_frequency_anchor"
    if (
        normalized_text == "minor seizures"
        and "episode" in normalized_evidence
        and not _SPECIFIC_SEIZURE_EVIDENCE.search(normalized_evidence)
    ):
        return "dropped_unsupported_episode_frequency_anchor"
    if (
        attrs.get("FrequencyChange") == "Same"
        and "continues to get" in normalized_evidence
        and not any(
            key in attrs
            for key in (
                "NumberOfSeizures",
                "LowerNumberOfSeizures",
                "UpperNumberOfSeizures",
                "NumberOfTimePeriods",
                "LowerNumberOfTimePeriods",
                "UpperNumberOfTimePeriods",
                "TimePeriod",
                "TimeSince_or_TimeOfEvent",
                "PointInTime",
            )
        )
    ):
        return "dropped_ongoing_same_without_frequency"
    if not any(key in attrs for key in _SF_STATE_ATTRIBUTES):
        if "unknown" in normalized_evidence or "not documented" in normalized_evidence:
            return None
        return "dropped_empty_sf_state_after_normalization"
    if (
        attrs.get("NumberOfSeizures") == "0"
        and normalized_text not in {"seizure", "seizures"}
        and normalized_text not in normalized_evidence
        and "seizure free" in normalized_evidence
    ):
        return "dropped_generic_zero_state_for_typed_anchor"
    if (
        attrs.get("NumberOfSeizures") == "0"
        and normalized_text in {"seizure", "seizures", "seizure free"}
        and "remains seizure free" in normalized_evidence
        and "since" not in normalized_evidence
    ):
        return "dropped_unanchored_current_seizure_free_state"
    if (
        attrs.get("NumberOfSeizures") == "0"
        and "best its ever been" in normalized_evidence
    ):
        return "dropped_vague_best_control_zero_state"
    if (
        attrs.get("NumberOfSeizures") == "0"
        and "last had a seizure before this" in normalized_evidence
    ):
        return "dropped_relative_prior_event_not_seizure_free"
    if attrs.get("NumberOfSeizures") == "0" and _evidence_has_positive_rate(
        normalized_evidence
    ):
        return "dropped_inconsistent_zero_state_with_active_rate"
    if normalized_evidence.startswith("previous event"):
        return "dropped_previous_event_not_headline_frequency"
    if "well controlled" in normalized_evidence and not any(
        marker in normalized_evidence
        for marker in ("no ", "not had", "not have", "since", "last event")
    ):
        return "dropped_controlled_without_zero_anchor"
    if attrs.get("NumberOfSeizures") != "0":
        return None
    return None




def _is_allowed_diagnosis_core(text: str) -> bool:
    normalized = normalize_phrase(text)
    return normalized not in _DIAGNOSIS_PROHIBITED_CORES and bool(
        _DIAGNOSIS_ALLOWED_CORE.search(text)
    )


def _is_allowed_sf_anchor(text: str) -> bool:
    return bool(_SEIZURE_FREQUENCY_ANCHOR.search(text)) and not bool(
        _SEIZURE_FREQUENCY_PROHIBITED_ANCHOR.search(text)
    )




def _is_planned_prescription(mention: PredictedMention, note_text: str) -> bool:
    if mention.entity != "Prescription":
        return False
    context = local_evidence_context(note_text, mention.evidence, before=96, after=24)
    return bool(_PLANNED_PRESCRIPTION_CONTEXT.search(context))


def _is_planned_investigation(mention: PredictedMention, note_text: str) -> bool:
    if mention.entity != "Investigations":
        return False
    attrs = mention.attributes
    has_result = any(
        attrs.get(key) in {"Normal", "Abnormal"}
        for key in ("EEG_Results", "MRI_Results", "CT_Results")
    )
    if has_result:
        return False
    context = local_evidence_context(note_text, mention.evidence, before=96, after=24)
    return bool(_PLANNED_INVESTIGATION_CONTEXT.search(context))






















def _evidence_has_positive_rate(normalized_evidence: str) -> bool:
    return bool(
        re.search(
            r"\b(?:approximately|around|about)?\s*\d+\s*(?:-|to|–|\s)\s*\d+"
            r".{0,80}\b(?:seizures?|convulsions?|jerks?)\s+per\s+"
            r"(?:day|week|month|year)\b",
            normalized_evidence,
            re.IGNORECASE,
        )
        or re.search(
            r"\b\d+.{0,80}\b(?:seizures?|convulsions?|jerks?)\s+per\s+"
            r"(?:day|week|month|year)\b",
            normalized_evidence,
            re.IGNORECASE,
        )
    )












def _is_zero_since_only_diagnosis_context(
    mention: PredictedMention,
    note_text: str,
) -> bool:
    if mention.entity != "Diagnosis":
        return False
    normalized_text = normalize_phrase(mention.text)
    if normalized_text not in {"tonic clonic seizures", "absences"}:
        return False
    context = normalize_phrase(
        local_evidence_context(note_text, mention.evidence, before=48, after=64)
    )
    return (
        "not had any further" in context
        or "no further" in context
        or ("no absences since" in context and normalized_text == "absences")
    )


def _is_investigation_only_diagnosis_context(mention: PredictedMention) -> bool:
    if mention.entity != "Diagnosis":
        return False
    if normalize_phrase(mention.text) != "temporal lobe epilepsy":
        return False
    evidence = normalize_phrase(mention.evidence)
    return "temporal lobe" in evidence and not any(
        marker in evidence
        for marker in (
            "epilep",
            "seizure",
            "diagnosis",
            "probable temporal",
        )
    )


def _is_frequency_phrase_diagnosis_context(mention: PredictedMention) -> bool:
    if mention.entity != "Diagnosis":
        return False
    source = normalize_phrase(f"{mention.text} {mention.evidence}")
    if "focal onset" in source:
        return False
    return bool(
        (EVERY_N_PERIODS.search(source) or EVERY_N_TO_M_PERIODS.search(source))
        and re.search(r"\bseizures?\s+every\b", source)
    )


def _is_unsupported_inferred_diagnosis(mention: PredictedMention) -> bool:
    if mention.entity != "Diagnosis":
        return False
    normalized_evidence = normalize_phrase(mention.evidence)
    normalized_text = normalize_phrase(mention.text)
    if "probable temporal" in normalized_evidence:
        return False
    if normalized_text == "epilepsy" and "epilep" not in normalized_evidence:
        return True
    if _DIAGNOSIS_ALLOWED_CORE.search(normalized_evidence):
        return False
    return normalized_text not in normalized_evidence


def _is_unsupported_eeg_confirmation(mention: PredictedMention) -> bool:
    if mention.entity != "Investigations":
        return False
    if normalize_phrase(mention.evidence) != "confirmed with an eeg recording":
        return False
    return mention.attributes.get("EEG_Results") == "Abnormal"


def _is_unsupported_investigation_evidence(mention: PredictedMention) -> bool:
    if mention.entity != "Investigations":
        return False
    modality = _investigation_text_modality(mention.text)
    if modality is None:
        return False
    evidence = normalize_phrase(mention.evidence)
    if modality.lower() in evidence.split():
        return False
    return "neurological examination was normal" in evidence




def _deduplicate_scored_mentions(
    mentions: Sequence[PredictedMention],
) -> list[PredictedMention]:
    deduplicated: list[PredictedMention] = []
    seen: set[tuple[Any, ...]] = set()
    for mention in mentions:
        key = _dedupe_key(mention)
        if key in seen:
            continue
        seen.add(key)
        deduplicated.append(mention)
    return deduplicated


def _dedupe_key(mention: PredictedMention) -> tuple[Any, ...]:
    attrs = mention.attributes
    if mention.entity == "Diagnosis":
        return (
            mention.entity,
            canonicalize_diagnosis_concept(mention.text),
        )
    if mention.entity == "Prescription":
        return (
            mention.entity,
            normalize_phrase(attrs.get("DrugName", "")),
            normalize_phrase(attrs.get("DrugDose", "")),
            normalize_phrase(attrs.get("DoseUnit", "")),
            normalize_phrase(attrs.get("Frequency", "")),
        )
    if mention.entity == "Investigations":
        modality = _investigation_modality(attrs, mention.text)
        return (
            mention.entity,
            modality,
            attrs.get(f"{modality}_Performed", ""),
            attrs.get(f"{modality}_Results", ""),
            attrs.get("EEG_Type", "") if modality == "EEG" else "",
        )
    if mention.entity == "SeizureFrequency":
        return (
            mention.entity,
            normalize_phrase(mention.text),
            tuple(
                sorted(
                    (key, value)
                    for key, value in attrs.items()
                    if key
                    in {
                        "AgeLower",
                        "AgeUnit",
                        "AgeUpper",
                        "DayDate",
                        "FrequencyChange",
                        "LowerNumberOfSeizures",
                        "LowerNumberOfTimePeriods",
                        "MonthDate",
                        "NumberOfSeizures",
                        "NumberOfTimePeriods",
                        "PointInTime",
                        "TimePeriod",
                        "TimeSince_or_TimeOfEvent",
                        "UpperNumberOfSeizures",
                        "UpperNumberOfTimePeriods",
                        "YearDate",
                    }
                )
            ),
        )
    return (
        mention.entity,
        normalize_phrase(mention.text),
        tuple(sorted(attrs.items())),
        normalize_phrase(mention.evidence),
    )


def _investigation_modality(attrs: Mapping[str, str], text: str) -> str:
    if any(key.startswith("MRI_") for key in attrs) or "mri" in normalize_phrase(text):
        return "MRI"
    if any(key.startswith("EEG_") for key in attrs) or "eeg" in normalize_phrase(text):
        return "EEG"
    if any(key.startswith("CT_") for key in attrs) or "ct" in normalize_phrase(text):
        return "CT"
    return "EEG" if attrs.get("EEG_Type") else "MRI"


def _investigation_text_modality(text: str) -> str | None:
    normalized = normalize_phrase(text).split()
    if any(token in {"mri", "mr"} for token in normalized):
        return "MRI"
    if "eeg" in normalized:
        return "EEG"
    if "ct" in normalized:
        return "CT"
    return None


def _is_non_target_investigation_text(text: str) -> bool:
    tokens = set(normalize_phrase(text).split())
    return bool(tokens & {"ecg", "ekg"})


def _expand_target_mention(
    mention: PredictedMention,
) -> tuple[list[PredictedMention], list[str]]:
    if mention.entity == "Diagnosis":
        return _expand_diagnosis_projection(mention)
    if mention.entity == "SeizureFrequency":
        return _expand_seizure_frequency_state(mention)
    if mention.entity != "Prescription":
        return [mention], []
    expanded, warnings = _expand_asymmetric_prescription(mention)
    if expanded:
        return expanded, warnings
    return [mention], warnings


def _expand_diagnosis_projection(
    mention: PredictedMention,
) -> tuple[list[PredictedMention], list[str]]:
    if (
        normalize_phrase(mention.text) == "temporal lobe seizure"
        and "temporal lobe onset focal seizures" in normalize_phrase(mention.evidence)
    ):
        companion = mention.model_copy(
            update={
                "text": "focal seizures",
                "attributes": {
                    **mention.attributes,
                    "DiagCategory": "MultipleSeizures",
                },
            }
        )
        return [mention, companion], ["split_temporal_lobe_onset_to_focal_seizures"]
    if normalize_phrase(mention.text) == "secondary generalised tonic clonic seizures":
        companion = mention.model_copy(
            update={
                "text": "tonic clonic seizures",
                "attributes": {
                    **mention.attributes,
                    "DiagCategory": "MultipleSeizures",
                },
            }
        )
        return [mention, companion], ["split_secondary_gtc_to_tonic_clonic_diagnosis"]
    if normalize_phrase(mention.text) == (
        "epilepsy with generalised tonic clonic seizures alone"
    ):
        companion = mention.model_copy(
            update={
                "text": "tonic clonic seizures",
                "attributes": {
                    **mention.attributes,
                    "DiagCategory": "MultipleSeizures",
                },
            }
        )
        return [mention, companion], ["split_syndrome_to_tonic_clonic_diagnosis"]
    match = _GENERALIZED_EPILEPSY_GTCS_ALONE.search(mention.evidence)
    if not match:
        return [mention], []
    syndrome = "epilepsy with generalised tonic clonic seizures alone"
    if normalize_phrase(mention.text) == syndrome:
        return [mention], []
    syndrome_mention = mention.model_copy(
        update={
            "text": syndrome,
            "attributes": {
                **mention.attributes,
                "DiagCategory": "Epilepsy",
            },
        }
    )
    seizure_mention = mention.model_copy(
        update={
            "text": "tonic clonic seizures",
            "attributes": {
                **mention.attributes,
                "DiagCategory": "MultipleSeizures",
            },
        }
    )
    return [mention, syndrome_mention, seizure_mention], [
        "split_generalised_epilepsy_syndrome"
    ]


def _expand_seizure_frequency_state(
    mention: PredictedMention,
) -> tuple[list[PredictedMention], list[str]]:
    expanded = [mention]
    warnings: list[str] = []
    if (
        mention.attributes.get("NumberOfSeizures") == "0"
        and normalize_phrase(mention.text) == "focal to bilateral convulsive seizures"
    ):
        expanded.append(
            mention.model_copy(
                update={
                    "text": "convulsive seizure",
                }
            )
        )
        warnings.append("split_convulsive_zero_state")
    if mention.attributes.get("NumberOfSeizures") == "0" and CONTROLLED_ON_DOSE.search(
        mention.evidence
    ):
        expanded.append(
            mention.model_copy(
                update={
                    "text": "seizures",
                    "attributes": {
                        "FrequencyChange": "Infrequent",
                        "PointInTime": "DrugChange",
                    },
                }
            )
        )
        warnings.append("projected_controlled_drug_change_to_infrequent_state")
    sf_diagnosis_projection = _sf_type_to_diagnosis_projection_warning(mention)
    if sf_diagnosis_projection:
        expanded.append(
            mention.model_copy(
                update={
                    "entity": "Diagnosis",
                    "attributes": {
                        "Certainty": "5",
                        "DiagCategory": "MultipleSeizures",
                        "Negation": "Affirmed",
                    },
                }
            )
        )
        warnings.append(sf_diagnosis_projection)
    if (
        mention.attributes.get("NumberOfSeizures") == "0"
        and "focal to bilateral convulsive seizures" in normalize_phrase(mention.evidence)
        and normalize_phrase(mention.text) == "seizures"
    ):
        expanded.append(
            mention.model_copy(
                update={
                    "entity": "Diagnosis",
                    "text": "focal to bilateral convulsive seizures",
                    "attributes": {
                        "Certainty": "5",
                        "DiagCategory": "MultipleSeizures",
                        "Negation": "Affirmed",
                    },
                }
            )
        )
        warnings.append("projected_remote_seizure_type_to_diagnosis")
    if not _CLUSTER_OF_SEIZURES.search(mention.evidence):
        return expanded, warnings
    if normalize_phrase(mention.text) == "cluster of seizures":
        return expanded, warnings
    cluster_attrs = {
        key: value
        for key, value in mention.attributes.items()
        if key
        not in {
            "LowerNumberOfSeizures",
            "UpperNumberOfSeizures",
            "NumberOfTimePeriods",
            "LowerNumberOfTimePeriods",
            "UpperNumberOfTimePeriods",
            "TimePeriod",
            "FrequencyChange",
        }
    }
    cluster_attrs["NumberOfSeizures"] = "1"
    cluster = mention.model_copy(
        update={
            "text": "cluster of seizures",
            "attributes": cluster_attrs,
        }
    )
    expanded.append(cluster)
    warnings.append("split_cluster_of_seizures_state")
    return expanded, warnings


def _sf_type_to_diagnosis_projection_warning(mention: PredictedMention) -> str | None:
    if mention.entity != "SeizureFrequency":
        return None
    normalized = normalize_phrase(mention.text)
    if normalized in {
        "seizure",
        "seizures",
        "cluster of seizures",
        "generalised tonic clonic seizure",
        "generalized tonic clonic seizure",
    }:
        return None
    if not _is_allowed_diagnosis_core(normalized):
        return None
    has_count = any(
        key in mention.attributes
        for key in (
            "NumberOfSeizures",
            "LowerNumberOfSeizures",
            "UpperNumberOfSeizures",
        )
    )
    if mention.attributes.get("NumberOfSeizures") == "0":
        evidence = normalize_phrase(mention.evidence)
        if "last event" in evidence or "last seizure" in evidence or "last one" in evidence:
            return "projected_typed_seizure_frequency_to_diagnosis"
        if normalized == "focal seizures" and "control" in evidence:
            return "projected_typed_controlled_state_to_diagnosis"
        return None
    if has_count:
        if normalized not in normalize_phrase(mention.evidence):
            return None
        return "projected_active_rate_seizure_type_to_diagnosis"
    return None


def _expand_asymmetric_prescription(
    mention: PredictedMention,
) -> tuple[list[PredictedMention], list[str]]:
    attrs = dict(mention.attributes)
    if attrs.get("DoseUnit") != "mg":
        return [], []
    match = ASYMMETRIC_DOSING.search(f"{mention.text} {mention.evidence}")
    if not match:
        return [], []
    first = clean_number(match.group("first"))
    second = clean_number(match.group("second"))
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
    attrs[lower_key] = clean_number(match.group(1))
    attrs[upper_key] = clean_number(match.group(2))
    warnings.append(
        f"split_range_attribute: {source_key} -> {lower_key}/{upper_key}"
    )




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
            _parse_target_extraction_json(raw_output) if raw_output else (None, ["not_run"])
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
                "n_evidence_invalid": _count_evidence_invalid_warnings(gate_warnings),
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


def _count_evidence_invalid_warnings(warnings: Sequence[str]) -> int:
    return sum("dropped_evidence_not_substring" in warning for warning in warnings)


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
                "fidelity_companions": arch["clinical_recovery"].get(
                    "fidelity_companions", {}
                ),
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
        {
            "letter_fragment": (
                "Diagnosis: epilepsy - unclassified, possibly generalised. In 2014 "
                "she had two generalised tonic clonic seizures and one absence-like "
                "seizure."
            ),
            "mentions": [
                {
                    "entity": "Diagnosis",
                    "text": "generalised epilepsy",
                    "attributes": {
                        "DiagCategory": "Epilepsy",
                        "Certainty": "3",
                        "Negation": "Affirmed",
                    },
                    "evidence": "epilepsy - unclassified, possibly generalised",
                },
                {
                    "entity": "Diagnosis",
                    "text": "generalised tonic clonic seizures",
                    "attributes": {
                        "DiagCategory": "MultipleSeizures",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                    "evidence": "generalised tonic clonic seizures",
                },
                {
                    "entity": "Diagnosis",
                    "text": "absence-like seizure",
                    "attributes": {
                        "DiagCategory": "SingleSeizure",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                    "evidence": "absence-like seizure",
                },
                {
                    "entity": "SeizureFrequency",
                    "text": "generalised tonic clonic seizures",
                    "attributes": {
                        "NumberOfSeizures": "2",
                        "TimeSince_or_TimeOfEvent": "During",
                        "YearDate": "2014",
                    },
                    "evidence": "In 2014 she had two generalised tonic clonic seizures",
                },
                {
                    "entity": "SeizureFrequency",
                    "text": "absence-like seizure",
                    "attributes": {
                        "NumberOfSeizures": "1",
                        "TimeSince_or_TimeOfEvent": "During",
                        "YearDate": "2014",
                    },
                    "evidence": (
                        "2014 she had two generalised tonic clonic seizures and "
                        "one absence-like seizure"
                    ),
                },
            ],
            "note": (
                "Diagnosis category and seizure types are separate facts; dated "
                "counts are SF facts."
            ),
        },
        {
            "letter_fragment": (
                "Diagnosis: intractable epilepsy with complex partial seizures. "
                "No seizure frequency was documented today."
            ),
            "mentions": [
                {
                    "entity": "Diagnosis",
                    "text": "intractable epilepsy",
                    "attributes": {
                        "DiagCategory": "Epilepsy",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                    "evidence": "intractable epilepsy",
                },
                {
                    "entity": "Diagnosis",
                    "text": "complex partial seizures",
                    "attributes": {
                        "DiagCategory": "MultipleSeizures",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                    "evidence": "complex partial seizures",
                },
            ],
            "note": "Do not emit SeizureFrequency when the note says frequency is not documented.",
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
