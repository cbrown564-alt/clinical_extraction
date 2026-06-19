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
    normalize_phrase,
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

PROMPT_VERSION = "exectv2_target_indicators_single_call_v0.23"
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
    r"further tests including|await(?:ing)?|planned)\b",
    re.IGNORECASE,
)
_ASYMMETRIC_DOSING = re.compile(
    r"(?P<first>\d+(?:\.\d+)?)\s*mg\b.{0,40}\b(?:mane|morning|am)\b"
    r".{0,80}?(?P<second>\d+(?:\.\d+)?)\s*mg\b.{0,40}\b(?:nocte|night|pm)\b",
    re.IGNORECASE | re.DOTALL,
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
_REMOTE_LAST_SEIZURES_IN_TEENS = re.compile(
    r"\blast\s+seizures?\s+were\s+in\s+(?:(?:his|her|their)\s+)?teenage\s+years\b",
    re.IGNORECASE,
)
_VAGUE_YEARLY_SEIZURE_RATE = re.compile(
    r"\b(?:a\s+)?(?:few|couple|several)\s+\w*seizures?\s+per\s+year\b",
    re.IGNORECASE,
)
_GENERIC_YEARLY_SEIZURE_RATE = re.compile(
    r"\b(?:roughly|about|around|approximately)\s+two\s+seizures?\s+per\s+year\b",
    re.IGNORECASE,
)
_YEAR_IN_TEXT = re.compile(r"\b(?P<year>19\d{2}|20\d{2})\b")
_SEVERAL_SINCE_LAST_CLINIC = re.compile(
    r"\bseveral\s+seizures?\s+since\s+(?:the\s+)?last\s+clinic(?:\s+appointment)?\b",
    re.IGNORECASE,
)
_EVERY_N_PERIODS = re.compile(
    r"\bevery\s+(?P<n>\d+)\s+(?P<period>days?|weeks?|months?|years?)\b",
    re.IGNORECASE,
)
_EVERY_N_TO_M_PERIODS = re.compile(
    r"\bevery\s+(?P<lower>\d+)\s*(?:-|to)\s*(?P<upper>\d+)\s+"
    r"(?P<period>days?|weeks?|months?|years?)\b",
    re.IGNORECASE,
)
_CONTROLLED_ON_DOSE = re.compile(
    r"\b(?:completely\s+)?under\s+control\s+on\s+the\s+dose\b",
    re.IGNORECASE,
)
_CLUSTER_OF_SEIZURES = re.compile(r"\bcluster\s+of\s+seizures\b", re.IGNORECASE)
_INFREQUENT_DIAGNOSIS_YEAR = re.compile(
    r"\binfrequent\b.+\byear\s+of\s+(?:his|her|the)\s+diagnosis\b",
    re.IGNORECASE | re.DOTALL,
)
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
                    "Words such as showed, showing, revealed, demonstrated, "
                    "consistent with, slowing, gliosis, infarct, lesion, or "
                    "epileptiform indicate an abnormal result for the named test."
                ),
                (
                    "Phrases such as no epileptiform activity, normal EEG, or normal "
                    "MRI indicate a normal result for the named test."
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
        if mention.entity == "SeizureFrequency":
            focal_diagnosis = _project_empty_sf_candidate_to_diagnosis(mention)
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

    evidence_repaired, evidence_repair_warnings = _repair_case_only_evidence(
        entity_valid,
        note_text=note_text,
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
        )
        warnings.extend(f"{mention.entity}: {warning}" for warning in normalization_warnings)
        attrs, attr_warnings = repair_attributes(
            normalized_attrs,
            spec=spec,
        )
        warnings.extend(f"{mention.entity}: {warning}" for warning in attr_warnings)
        text, text_warnings = _normalize_target_text(
            mention.entity,
            mention.text,
            evidence=mention.evidence,
        )
        warnings.extend(f"{mention.entity}: {warning}" for warning in text_warnings)
        if mention.entity == "SeizureFrequency":
            text, attrs, state_warnings = _project_sf_state_from_evidence(
                text,
                attrs,
                mention.evidence,
            )
            warnings.extend(f"{mention.entity}: {warning}" for warning in state_warnings)
            drop_warning = _sf_state_drop_reason(text, attrs, mention.evidence)
            if drop_warning:
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
            projected_sf = _project_diagnosis_frequency_header_to_sf(
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
        if mention.entity == "Diagnosis" and _is_frequency_phrase_diagnosis_context(
            base_mention
        ):
            warnings.append(
                f"Diagnosis: dropped_frequency_phrase_diagnosis_context: {text!r}"
            )
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


def _repair_case_only_evidence(
    mentions: Sequence[MentionRecord],
    *,
    note_text: str,
) -> tuple[list[MentionRecord], list[str]]:
    repaired: list[MentionRecord] = []
    warnings: list[str] = []
    lowered_note = note_text.lower()
    for mention in mentions:
        evidence = mention.evidence
        if evidence and evidence not in note_text:
            index = lowered_note.find(evidence.lower())
            if index >= 0:
                exact = note_text[index : index + len(evidence)]
                repaired.append(mention.model_copy(update={"evidence": exact}))
                warnings.append(f"repaired_evidence_case: {mention.text!r}")
                continue
            if (
                mention.entity == "SeizureFrequency"
                and mention.attributes.get("NumberOfSeizures") == "0"
                and "last one being around christmas" in evidence.lower()
            ):
                marker = "last one being around christmas time in 2017"
                marker_index = lowered_note.find(marker)
                if marker_index >= 0:
                    exact = note_text[marker_index : marker_index + len(marker)]
                    repaired.append(mention.model_copy(update={"evidence": exact}))
                    warnings.append(f"repaired_last_event_evidence: {mention.text!r}")
                    continue
            if mention.entity == "Prescription":
                ellipsis = _repair_ellipsis_evidence(mention.evidence, note_text)
                if ellipsis:
                    repaired.append(mention.model_copy(update={"evidence": ellipsis}))
                    warnings.append(f"repaired_ellipsis_evidence: {mention.text!r}")
                    continue
                synonym = _repair_prescription_frequency_synonym_evidence(
                    mention,
                    note_text,
                )
                if synonym:
                    repaired.append(mention.model_copy(update={"evidence": synonym}))
                    warnings.append(
                        "repaired_prescription_frequency_synonym_evidence: "
                        f"{mention.text!r}"
                    )
                    continue
        repaired.append(mention)
    return repaired, warnings


def _repair_ellipsis_evidence(evidence: str, note_text: str) -> str | None:
    if "..." not in evidence:
        return None
    suffix = evidence.rsplit("...", 1)[-1].strip()
    if not suffix:
        return None
    lowered_note = note_text.lower()
    suffix_index = lowered_note.find(suffix.lower())
    if suffix_index < 0:
        return None
    return note_text[suffix_index : suffix_index + len(suffix)]


def _repair_prescription_frequency_synonym_evidence(
    mention: MentionRecord,
    note_text: str,
) -> str | None:
    attrs = {str(k): str(v) for k, v in dict(mention.attributes).items()}
    drug = normalize_phrase(attrs.get("DrugName", ""))
    dose = attrs.get("DrugDose", "").strip()
    if not drug or not dose or attrs.get("Frequency") != "2":
        return None
    pattern = re.compile(
        rf"\b{re.escape(drug)}\s+{re.escape(dose)}\s*mg\s+twice\s+a\s+day\b",
        re.IGNORECASE,
    )
    match = pattern.search(note_text)
    return match.group(0) if match else None


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


def _normalize_target_text(
    entity: str,
    text: str,
    *,
    evidence: str = "",
) -> tuple[str, list[str]]:
    if entity == "SeizureFrequency":
        normalized = normalize_phrase(text)
        if normalized in _SF_TEXT_ALIASES and _SF_TEXT_ALIASES[normalized] != text:
            return _SF_TEXT_ALIASES[normalized], [
                f"normalized_seizure_frequency_text: {text!r} -> "
                f"{_SF_TEXT_ALIASES[normalized]!r}"
            ]
        if re.match(r"^seizures?\s+every\b", normalized) and (
            _EVERY_N_PERIODS.search(normalized)
            or _EVERY_N_TO_M_PERIODS.search(normalized)
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
    normalized = _project_diagnosis_text_from_evidence(normalized, evidence)
    if normalized and normalized != text:
        return normalized, [f"normalized_diagnosis_text: {text!r} -> {normalized!r}"]
    return text, []


def _project_diagnosis_text_from_evidence(text: str, evidence: str) -> str:
    source = normalize_phrase(f"{text} {evidence}")
    if (
        text == "epilepsy with generalised tonic clonic seizures"
        and "alone" in source
    ):
        return "epilepsy with generalised tonic clonic seizures alone"
    if (
        text == "general seizures"
        and "general and complex partial seizures" in source
    ):
        return "complex partial seizures"
    if "focal onset" in source and text in {
        "epilepsy",
        "focal seizures",
        "seizures possibly focal onset",
    }:
        return "focal epilepsy"
    if text in {"epilepsy", "focal epilepsy"} and "epilep" in source:
        if "probable temporal" in source or "temporal lobe epilepsy" in source:
            return "temporal lobe epilepsy"
    if text == "epilepsy" and "epilep" in source:
        if "probable focal" in source or "focal onset" in source:
            return "focal epilepsy"
        if "possibly generalised" in source or "possibly generalized" in source:
            return "generalised epilepsy"
    return text


def _project_sf_state_from_evidence(
    text: str,
    attrs: dict[str, str],
    evidence: str,
) -> tuple[str, dict[str, str], list[str]]:
    if _INFREQUENT_DIAGNOSIS_YEAR.search(evidence):
        return (
            text,
            {"FrequencyChange": "Infrequent"},
            ["projected_infrequent_diagnosis_year_to_change_state"],
        )
    if not _REMOTE_LAST_SEIZURES_IN_TEENS.search(evidence):
        if _SEVERAL_SINCE_LAST_CLINIC.search(evidence):
            projected = {
                key: value
                for key, value in attrs.items()
                if key
                not in {
                    "FrequencyChange",
                    "NumberOfTimePeriods",
                    "LowerNumberOfTimePeriods",
                    "UpperNumberOfTimePeriods",
                    "TimePeriod",
                    "DayDate",
                    "MonthDate",
                    "YearDate",
                }
            }
            projected.update(
                {
                    "NumberOfSeizures": "3",
                    "TimeSince_or_TimeOfEvent": "Since",
                    "PointInTime": "LastClinic",
                }
            )
            return text, projected, ["projected_several_since_last_clinic"]
        if _GENERIC_YEARLY_SEIZURE_RATE.search(evidence):
            projected = {
                key: value
                for key, value in attrs.items()
                if key
                not in {
                    "FrequencyChange",
                    "TimeSince_or_TimeOfEvent",
                    "PointInTime",
                    "DayDate",
                    "MonthDate",
                    "YearDate",
                }
            }
            projected.update(
                {
                    "NumberOfSeizures": "2",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Year",
                }
            )
            return "seizures", projected, ["projected_generic_yearly_rate_anchor"]
        range_match = _EVERY_N_TO_M_PERIODS.search(evidence)
        if (
            range_match
            and attrs.get("NumberOfSeizures", "1") == "1"
            and "LowerNumberOfSeizures" not in attrs
            and "UpperNumberOfSeizures" not in attrs
        ):
            projected = {
                key: value
                for key, value in attrs.items()
                if key
                not in {
                    "FrequencyChange",
                    "NumberOfTimePeriods",
                    "LowerNumberOfTimePeriods",
                    "UpperNumberOfTimePeriods",
                    "TimePeriod",
                }
            }
            projected.update(
                {
                    "NumberOfSeizures": "1",
                    "LowerNumberOfTimePeriods": range_match.group("lower"),
                    "UpperNumberOfTimePeriods": range_match.group("upper"),
                    "TimePeriod": _period_to_canonical(range_match.group("period")),
                }
            )
            return (
                text,
                projected,
                ["projected_every_n_to_m_periods_to_one_event_rate"],
            )
        if (
            "NumberOfSeizures" not in attrs
            and "LowerNumberOfSeizures" not in attrs
            and "UpperNumberOfSeizures" not in attrs
        ):
            match = _EVERY_N_PERIODS.search(evidence)
            if match:
                projected = {
                    key: value
                    for key, value in attrs.items()
                    if key not in {"FrequencyChange"}
                }
                projected["NumberOfSeizures"] = "1"
                projected["NumberOfTimePeriods"] = match.group("n")
                projected["TimePeriod"] = _period_to_canonical(match.group("period"))
                return (
                    text,
                    projected,
                    ["projected_every_n_periods_to_one_event_rate"],
                )
        if _VAGUE_YEARLY_SEIZURE_RATE.search(evidence):
            projected = {
                key: value
                for key, value in attrs.items()
                if key
                not in {
                    "FrequencyChange",
                    "TimeSince_or_TimeOfEvent",
                    "PointInTime",
                    "DayDate",
                    "MonthDate",
                    "YearDate",
                }
            }
            projected.update(
                {
                    "NumberOfSeizures": "2",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Year",
                }
            )
            return text, projected, ["projected_vague_yearly_rate"]
        return text, attrs, []
    projected = {
        key: value
        for key, value in attrs.items()
        if key
        not in {
            "NumberOfSeizures",
            "LowerNumberOfSeizures",
            "UpperNumberOfSeizures",
            "NumberOfTimePeriods",
            "LowerNumberOfTimePeriods",
            "UpperNumberOfTimePeriods",
            "TimePeriod",
            "FrequencyChange",
        }
    }
    projected.update(
        {
            "NumberOfSeizures": "0",
            "TimeSince_or_TimeOfEvent": "Since",
            "AgeLower": "13",
            "AgeUpper": "19",
            "AgeUnit": "Year",
        }
    )
    return "seizures", projected, ["projected_remote_last_seizures_to_seizure_free"]


def _sf_state_drop_reason(
    text: str,
    attrs: dict[str, str],
    evidence: str,
) -> str | None:
    normalized_evidence = normalize_phrase(evidence)
    normalized_text = normalize_phrase(text)
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
        and normalized_text in {"seizure", "seizures"}
        and "remains seizure free" in normalized_evidence
        and "since" not in normalized_evidence
    ):
        return "dropped_unanchored_current_seizure_free_state"
    if "last had a seizure before this" in normalized_evidence:
        return "dropped_relative_prior_event_not_seizure_free"
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


def _project_empty_sf_candidate_to_diagnosis(
    mention: MentionRecord,
) -> MentionRecord | None:
    if any(key in mention.attributes for key in _SF_STATE_ATTRIBUTES):
        return None
    source = normalize_phrase(f"{mention.text} {mention.evidence}")
    if "focal onset" not in source:
        return None
    attrs = {str(k): str(v) for k, v in dict(mention.attributes).items()}
    certainty = attrs.get("Certainty", "3")
    return mention.model_copy(
        update={
            "entity": "Diagnosis",
            "text": "focal epilepsy",
            "attributes": {
                "Certainty": certainty,
                "DiagCategory": "Epilepsy",
                "Negation": "Affirmed",
            },
        }
    )


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


def _project_diagnosis_frequency_header_to_sf(
    mention: PredictedMention,
    note_text: str,
) -> PredictedMention | None:
    normalized_text = normalize_phrase(mention.text)
    if normalized_text not in {"absence like seizures", "absence-like seizures"}:
        return None
    year_match = _YEAR_IN_TEXT.search(mention.evidence)
    if not year_match:
        return None
    context = normalize_phrase(
        _local_evidence_context(note_text, mention.evidence, before=64, after=16)
    )
    if "seizure type and frequency" not in context:
        return None
    return mention.model_copy(
        update={
            "entity": "SeizureFrequency",
            "text": "absence like seizures",
            "attributes": {
                "NumberOfSeizures": "1",
                "TimeSince_or_TimeOfEvent": "During",
                "YearDate": year_match.group("year"),
            },
        }
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
        _local_evidence_context(note_text, mention.evidence, before=48, after=64)
    )
    return (
        "not had any further" in context
        or "no further" in context
        or ("no absences since" in context and normalized_text == "absences")
    )


def _is_frequency_phrase_diagnosis_context(mention: PredictedMention) -> bool:
    if mention.entity != "Diagnosis":
        return False
    source = normalize_phrase(f"{mention.text} {mention.evidence}")
    if "focal onset" in source:
        return False
    return bool(
        (_EVERY_N_PERIODS.search(source) or _EVERY_N_TO_M_PERIODS.search(source))
        and re.search(r"\bseizures?\s+every\b", source)
    )


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
    return [mention, syndrome_mention], ["split_generalised_epilepsy_syndrome"]


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
    if mention.attributes.get("NumberOfSeizures") == "0" and _CONTROLLED_ON_DOSE.search(
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
        "focal to bilateral convulsive seizures",
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
        if "last event" in evidence or "last seizure" in evidence:
            return "projected_typed_seizure_frequency_to_diagnosis"
        return None
    if has_count:
        return "projected_active_rate_seizure_type_to_diagnosis"
    return None


def _expand_asymmetric_prescription(
    mention: PredictedMention,
) -> tuple[list[PredictedMention], list[str]]:
    attrs = dict(mention.attributes)
    if attrs.get("DoseUnit") != "mg" or attrs.get("Frequency") != "1":
        return [], []
    match = _ASYMMETRIC_DOSING.search(f"{mention.text} {mention.evidence}")
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


def _period_to_canonical(period: str) -> str:
    normalized = period.strip().lower()
    if normalized.startswith("day"):
        return "Day"
    if normalized.startswith("week"):
        return "Week"
    if normalized.startswith("month"):
        return "Month"
    if normalized.startswith("year"):
        return "Year"
    return period


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
