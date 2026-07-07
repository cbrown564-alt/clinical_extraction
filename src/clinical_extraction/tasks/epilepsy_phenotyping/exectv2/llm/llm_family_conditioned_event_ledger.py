"""Family-conditioned event-ledger extractor for the ExECTv2 key families.

This module carries forward the single design that survived the all-family
prompt experiments: one shared structured-event schema and one source-near
candidate ledger, conditioned by a target family profile. Each call extracts
one family only, which keeps the prompt narrow while preserving a common
architecture for Prescription, Diagnosis, SeizureFrequency, and Investigations.
"""

from __future__ import annotations

import json
import re
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    _has_blocking_parse_issue,
    check_evidence,
    repair_attributes,
    write_jsonl,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    PHRASE_ONLY,
    benchmark_config_for,
    score_concept_identity,
    score_entity,
    score_frequency_state,
    score_investigations_components,
    score_prescription_components,
    semantic_config_for,
    source_near_diagnostic,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

PROMPT_VERSION = "exectv2_hybrid_family_conditioned_event_ledger_v0.3"
PIPELINE_FAMILY = "exectv2_hybrid_family_conditioned_event_ledger"
COMPONENT_OWNER = "hybrid_family_conditioned_event_ledger"

KEY_ENTITY_NAMES: tuple[str, ...] = (
    PRESCRIPTION.name,
    DIAGNOSIS.name,
    SEIZURE_FREQUENCY.name,
    INVESTIGATIONS.name,
)

TargetFamily = Literal["Prescription", "Diagnosis", "SeizureFrequency", "Investigations"]

ENTITY_TO_EVENT_FAMILY: dict[str, str] = {
    PRESCRIPTION.name: "medication",
    DIAGNOSIS.name: "diagnosis",
    SEIZURE_FREQUENCY.name: "seizure_frequency",
    INVESTIGATIONS.name: "investigation",
}
EVENT_FAMILY_TO_ENTITY = {value: key for key, value in ENTITY_TO_EVENT_FAMILY.items()}

IDEAL_HEADLINE_F1_TARGET = 0.80
CURRENT_COMPARATOR_HEADLINE_F1: dict[str, float] = {
    PRESCRIPTION.name: 0.817,
    DIAGNOSIS.name: 0.658,
    SEIZURE_FREQUENCY.name: 0.782,
    INVESTIGATIONS.name: 0.872,
}


@dataclass(frozen=True)
class FamilyProfile:
    entity: str
    event_family: str
    task: str
    mention_text_policy: str
    attribute_policy: list[str]
    lane_policy: list[str]
    worked_examples: list[dict[str, Any]]

    def as_prompt_payload(self) -> dict[str, Any]:
        return {
            "entity": self.entity,
            "event_family": self.event_family,
            "task": self.task,
            "mention_text_policy": self.mention_text_policy,
            "attribute_policy": self.attribute_policy,
            "lane_policy": self.lane_policy,
            "worked_examples": self.worked_examples,
        }


class ExECTv2FamilyConditionedEventLedgerSignature(dspy.Signature):
    """Read one clinical letter and return target-family clinical events.

    Return exactly one JSON object with a 'clinical_events' list. No markdown.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter and a target family profile."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            'One strict JSON object: {"clinical_events": [{"family": ..., '
            '"anchor_text": ..., "evidence": ..., "event_state": {...}, '
            '"mentions": [{"entity": ..., "text": ..., "attributes": {...}}], '
            '"confidence": ..., "rationale": ...}, ...]}'
        )
    )


class DspyFamilyConditionedEventLedgerExtractor(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(ExECTv2FamilyConditionedEventLedgerSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def build_prompt_input(letter: ExectLetter, target_family: str) -> str:
    """Build a prompt payload for one target family using the shared event schema."""

    profile = family_profile(target_family)
    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": (
            "Read the clinical letter once. Use the candidate_evidence_ledger as "
            "attention scaffolding, then build source-near clinical events for the "
            "target family only. Return no mentions for other families."
        ),
        "architecture": {
            "name": "single family-conditioned event ledger",
            "inspiration": (
                "Gan structured-events discipline: source-near candidate evidence, "
                "typed event lanes, exact evidence, then final mention renderings."
            ),
            "component_ownership": (
                "The candidate ledger proposes possible evidence spans only. The "
                "model owns keep, reject, split, merge, and final rendered mentions. "
                "A later validation layer checks exact evidence, cleans illegal "
                "attributes, and attaches finite ontology codes."
            ),
        },
        "target_family": profile.entity,
        "target_event_family": profile.event_family,
        "family_profile": profile.as_prompt_payload(),
        "output_schema": _output_schema(profile),
        "candidate_evidence_ledger": _target_candidate_ledger(letter, profile),
        "decision_procedure": _target_decision_procedure(profile),
        "event_lane_guide": {
            profile.event_family: structured._event_lane_guide()[profile.event_family],
        },
        "attribute_vocabulary": {profile.entity: _attribute_vocabulary(profile.entity)},
        "clinical_rules": _shared_clinical_rules(profile),
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def family_profile(target_family: str) -> FamilyProfile:
    normalized = normalize_target_family(target_family)
    return FAMILY_PROFILES[normalized]


def normalize_target_family(target_family: str) -> TargetFamily:
    if target_family in FAMILY_PROFILES:
        return target_family  # type: ignore[return-value]
    if target_family in EVENT_FAMILY_TO_ENTITY:
        return EVENT_FAMILY_TO_ENTITY[target_family]  # type: ignore[return-value]
    lowered = target_family.strip().lower()
    for entity, event_family in ENTITY_TO_EVENT_FAMILY.items():
        if lowered in {entity.lower(), event_family.lower()}:
            return entity  # type: ignore[return-value]
    raise ValueError(f"Unknown target family: {target_family!r}")


def _output_schema(profile: FamilyProfile) -> dict[str, Any]:
    return {
        "clinical_events": [
            {
                "family": profile.event_family,
                "anchor_text": "Short exact source substring naming the event.",
                "evidence": "Exact source substring supporting every rendered mention.",
                "event_state": {
                    "decision_lane": "One lane from event_lane_guide.",
                    "state": "Compact source-near facts before mention rendering.",
                },
                "mentions": [
                    {
                        "entity": profile.entity,
                        "text": "Exact source substring for the final mention.",
                        "attributes": {
                            "use_only": f"legal {profile.entity} attributes listed below"
                        },
                    }
                ],
                "confidence": "low | medium | high",
                "rationale": "One short sentence naming why the evidence was kept.",
            }
        ]
    }


def _target_candidate_ledger(
    letter: ExectLetter,
    profile: FamilyProfile,
) -> list[dict[str, Any]]:
    return [
        row
        for row in structured.candidate_evidence_ledger_for_letter(letter)
        if row.get("family") == profile.event_family
    ]


def _target_decision_procedure(profile: FamilyProfile) -> list[str]:
    return [
        step.replace("the four key families", f"the {profile.entity} family").replace(
            "for medication, diagnosis, seizure frequency, and investigations",
            f"for {profile.event_family}",
        )
        for step in structured._decision_procedure()
    ] + [
        (
            f"Final mentions must all have entity={profile.entity!r}. If an event "
            "belongs to another family, keep it only as context in event_state and "
            "return no mention for it."
        )
    ]


def _attribute_vocabulary(entity_name: str) -> dict[str, Any]:
    spec = ENTITY_REGISTRY[entity_name]
    attrs: dict[str, Any] = {}
    for attr in sorted(spec.legal_attributes):
        if attr in {"CUI", "CUIPhrase"}:
            attrs[attr] = "Do not emit this; the validation layer fills it later."
        elif attr in spec.closed_vocab:
            attrs[attr] = sorted(spec.closed_vocab[attr])
        else:
            attrs[attr] = "string copied or normalized from the letter."
    return attrs


def _shared_clinical_rules(profile: FamilyProfile) -> list[str]:
    return (
        [
            "Candidate ledger rows are not predictions; reject unsupported candidates.",
            "Every final evidence value must be an exact substring of the letter.",
            "Every final mention text must be an exact substring of its evidence.",
            f"Return only {profile.entity} mentions.",
            "Do not emit CUI or CUIPhrase; ontology projection is handled after validation.",
            'If no target-family findings are present, return {"clinical_events": []}.',
            "Return exactly one JSON object. No markdown code fences.",
        ]
        + profile.attribute_policy
        + profile.lane_policy
    )


FAMILY_PROFILES: dict[str, FamilyProfile] = {
    PRESCRIPTION.name: FamilyProfile(
        entity=PRESCRIPTION.name,
        event_family="medication",
        task="Extract current anti-seizure medication regimens.",
        mention_text_policy=(
            "Use the compact medication regimen span when dose or frequency is stated; "
            "use the bare medication name when that is the only source text."
        ),
        attribute_policy=[
            (
                "Prescription attributes should include DrugName, DrugDose, DoseUnit, "
                "and Frequency when the source states them."
            ),
            (
                "Frequency values are 1, 2, 3, or As_Required. Map once daily to 1, "
                "twice daily or bd to 2, three times daily or tds to 3, and rescue "
                "or PRN use to As_Required."
            ),
            (
                "Previous trials, stopped medication, future options, and titration "
                "targets are not current regimens."
            ),
        ],
        lane_policy=[
            "Medication decision lane current_regimen keeps ordinary active treatment.",
            "Medication decision lane rescue_regimen keeps as-required rescue treatment.",
            "Medication decision lane future_or_historical_medication usually returns no mention.",
        ],
        worked_examples=[
            {
                "note_fragment": "Current treatment is lamotrigine 200 mg twice daily.",
                "correct_event": {
                    "family": "medication",
                    "anchor_text": "lamotrigine",
                    "evidence": "Current treatment is lamotrigine 200 mg twice daily.",
                    "event_state": {"decision_lane": "current_regimen"},
                    "mentions": [
                        {
                            "entity": "Prescription",
                            "text": "lamotrigine 200 mg twice daily",
                            "attributes": {
                                "DrugName": "lamotrigine",
                                "DrugDose": "200",
                                "DoseUnit": "mg",
                                "Frequency": "2",
                            },
                        }
                    ],
                    "confidence": "high",
                    "rationale": "The sentence states an active medication regimen.",
                },
            },
            {
                "note_fragment": "We may increase levetiracetam if seizures recur.",
                "correct_event": {
                    "family": "medication",
                    "anchor_text": "levetiracetam",
                    "evidence": "We may increase levetiracetam if seizures recur.",
                    "event_state": {"decision_lane": "future_or_historical_medication"},
                    "mentions": [],
                    "confidence": "high",
                    "rationale": "The source describes a conditional future plan.",
                },
            },
        ],
    ),
    DIAGNOSIS.name: FamilyProfile(
        entity=DIAGNOSIS.name,
        event_family="diagnosis",
        task="Extract patient-level epilepsy diagnoses and named epileptic seizure diagnoses.",
        mention_text_policy=(
            "Render the clean core clinical concept span. Put hedging in Certainty, "
            "and do not include section headers or explanatory context in text."
        ),
        attribute_policy=[
            "Every Diagnosis mention must include Certainty and Negation.",
            "Use Certainty=5 for established or unqualified diagnoses.",
            "Use Certainty=4 for probable or likely diagnoses.",
            "Use Certainty=3 for possible, query, or suspected diagnoses.",
            "Use Negation=Affirmed unless the source explicitly negates the diagnosis.",
            "Use DiagCategory=Epilepsy for epilepsy syndromes and named epileptic seizure types.",
            (
                "Use DiagCategory=MultipleSeizures for plural seizure-type diagnoses "
                "such as focal seizures or tonic clonic seizures."
            ),
            (
                "Use DiagCategory=SingleSeizure for singular seizure-type diagnoses "
                "such as a single focal seizure."
            ),
        ],
        lane_policy=[
            "Diagnosis decision lane diagnosis_assertion keeps patient-level diagnosis statements.",
            (
                "Diagnosis decision lane diagnosis_context_only rejects family history, "
                "education, and risk discussion."
            ),
            (
                "Diagnosis decision lane symptom_or_nonepileptic rejects blackouts, "
                "collapse, anxiety, and dissociative events unless explicitly epileptic."
            ),
            "A problem-list or Diagnosis header is not enough without an asserted concept.",
            (
                "Split compound Diagnosis lines into atomic concepts when the exact "
                "source contains each concept. Do not return one long combined line "
                "when it contains multiple diagnoses."
            ),
            (
                "For text like epilepsy probable focal where focal epilepsy is not "
                "an exact source phrase, return epilepsy rather than the whole header."
            ),
        ],
        worked_examples=[
            {
                "note_fragment": "Diagnosis: probable temporal lobe epilepsy.",
                "correct_event": {
                    "family": "diagnosis",
                    "anchor_text": "temporal lobe epilepsy",
                    "evidence": "Diagnosis: probable temporal lobe epilepsy.",
                    "event_state": {"decision_lane": "diagnosis_assertion"},
                    "mentions": [
                        {
                            "entity": "Diagnosis",
                            "text": "temporal lobe epilepsy",
                            "attributes": {
                                "DiagCategory": "Epilepsy",
                                "Certainty": "4",
                                "Negation": "Affirmed",
                            },
                        }
                    ],
                    "confidence": "high",
                    "rationale": "The source asserts a probable epilepsy syndrome.",
                },
            },
            {
                "note_fragment": "Family history includes epilepsy.",
                "correct_event": {
                    "family": "diagnosis",
                    "anchor_text": "epilepsy",
                    "evidence": "Family history includes epilepsy.",
                    "event_state": {"decision_lane": "diagnosis_context_only"},
                    "mentions": [],
                    "confidence": "high",
                    "rationale": "The diagnosis belongs to family history, not the patient.",
                },
            },
        ],
    ),
    SEIZURE_FREQUENCY.name: FamilyProfile(
        entity=SEIZURE_FREQUENCY.name,
        event_family="seizure_frequency",
        task=(
            "Extract seizure frequency, seizure-free, last-event, count, cadence, "
            "and change states."
        ),
        mention_text_policy=(
            "Use only the seizure anchor as mention text, such as seizures, focal "
            "seizures, or generalised tonic clonic seizure. Put counts, dates, "
            "ranges, intervals, and change state in attributes."
        ),
        attribute_policy=[
            "Never emit a SeizureFrequency mention with empty attributes.",
            (
                "For seizure-free or last-event anchors, use NumberOfSeizures=0 "
                "plus the date, duration, or point-in-time attributes supported by evidence."
            ),
            (
                "For ranges, use LowerNumberOfSeizures and UpperNumberOfSeizures "
                "or LowerNumberOfTimePeriods and UpperNumberOfTimePeriods."
            ),
            "Map several to NumberOfSeizures=3 only when the evidence states several seizures.",
            (
                "Use FrequencyChange only for explicit improved, worse, increased, "
                "decreased, frequent, infrequent, same, or controlled seizure frequency."
            ),
            (
                "Use month numbers for MonthDate: January=1, February=2, March=3, "
                "April=4, May=5, June=6, July=7, August=8, September=9, "
                "October=10, November=11, December=12."
            ),
            (
                "Add TimeSince_or_TimeOfEvent=During for dated counts such as "
                "2 seizures 2014, and Since for last seizure or last event anchors."
            ),
            (
                "For since last clinic or since the last clinic appointment, add "
                "TimeSince_or_TimeOfEvent=Since and PointInTime=LastClinic."
            ),
        ],
        lane_policy=[
            "Seizure-frequency decision lane active_rate keeps counts or current cadence.",
            (
                "Seizure-frequency decision lane seizure_free_anchor keeps "
                "no-further-seizure and last-event states."
            ),
            (
                "Seizure-frequency decision lane qualitative_change keeps explicit "
                "frequency change wording."
            ),
            (
                "Reject diagnosis-only, family-history-only, unlabelled events, "
                "and bare seizure types without frequency state."
            ),
            (
                "Reject seizure-free wording when it has no duration, date, surgery, "
                "drug-change, last-clinic, or last-event anchor."
            ),
            (
                "Extract structured section lines and later narrative frequency "
                "sentences as separate events when both state different frequencies."
            ),
            (
                "Do not include the count, interval, or date in SeizureFrequency "
                "mention text; those details belong only in attributes."
            ),
        ],
        worked_examples=[
            {
                "note_fragment": "She has focal seizures every 3 to 4 weeks.",
                "correct_event": {
                    "family": "seizure_frequency",
                    "anchor_text": "focal seizures",
                    "evidence": "She has focal seizures every 3 to 4 weeks.",
                    "event_state": {"decision_lane": "active_rate"},
                    "mentions": [
                        {
                            "entity": "SeizureFrequency",
                            "text": "focal seizures every 3 to 4 weeks",
                            "attributes": {
                                "NumberOfSeizures": "1",
                                "LowerNumberOfTimePeriods": "3",
                                "UpperNumberOfTimePeriods": "4",
                                "TimePeriod": "Week",
                            },
                        }
                    ],
                    "confidence": "high",
                    "rationale": "The source states a named seizure cadence.",
                },
            },
            {
                "note_fragment": "Her last seizure was in September 2017.",
                "correct_event": {
                    "family": "seizure_frequency",
                    "anchor_text": "last seizure",
                    "evidence": "Her last seizure was in September 2017.",
                    "event_state": {"decision_lane": "seizure_free_anchor"},
                    "mentions": [
                        {
                            "entity": "SeizureFrequency",
                            "text": "last seizure was in September 2017",
                            "attributes": {
                                "NumberOfSeizures": "0",
                                "TimeSince_or_TimeOfEvent": "Since",
                                "MonthDate": "September",
                                "YearDate": "2017",
                            },
                        }
                    ],
                    "confidence": "high",
                    "rationale": "The source gives a last-event anchor.",
                },
            },
        ],
    ),
    INVESTIGATIONS.name: FamilyProfile(
        entity=INVESTIGATIONS.name,
        event_family="investigation",
        task="Extract completed EEG, MRI, CT, and telemetry investigations with status or result.",
        mention_text_policy=(
            "Use the modality or compact result-bearing span. Planned repeats and "
            "bare modality references usually produce no final mention."
        ),
        attribute_policy=[
            (
                "Use MRI_Performed, CT_Performed, or EEG_Performed when the source "
                "states a modality was done or not done."
            ),
            (
                "Use MRI_Results, CT_Results, or EEG_Results only when the source "
                "states normal, abnormal, unknown, captured, showed, revealed, "
                "or similar result wording."
            ),
            (
                "Treat temporal slowing, spike and wave, spikes, sharp waves, "
                "and captured seizures as Abnormal EEG results."
            ),
            "Use EEG_Type=SleepDeprived only for sleep-deprived EEG.",
            "Use EEG_Type=VideoTelemetry only for video EEG, VEEG, telemetry, or video telemetry.",
            (
                "Do not default a plain EEG to Standard unless the source clearly "
                "distinguishes a routine standard EEG."
            ),
            (
                "Future planned, requested, repeat, or follow-up investigations "
                "should return no mention unless the same evidence also gives a "
                "completed result."
            ),
        ],
        lane_policy=[
            (
                "Investigation decision lane performed_investigation keeps completed "
                "or resulted investigations."
            ),
            (
                "Investigation decision lane not_performed keeps explicit no MRI, "
                "no CT, or no EEG statements."
            ),
            "Investigation decision lane planned_investigation usually returns no mention.",
            "Reject bare modality references without status or result.",
            (
                "Previous investigations with normal or abnormal results are still "
                "completed investigations; do not reject them merely because they "
                "are historical."
            ),
        ],
        worked_examples=[
            {
                "note_fragment": "MRI brain was normal.",
                "correct_event": {
                    "family": "investigation",
                    "anchor_text": "MRI",
                    "evidence": "MRI brain was normal.",
                    "event_state": {"decision_lane": "performed_investigation"},
                    "mentions": [
                        {
                            "entity": "Investigations",
                            "text": "MRI brain was normal",
                            "attributes": {
                                "MRI_Performed": "Yes",
                                "MRI_Results": "Normal",
                            },
                        }
                    ],
                    "confidence": "high",
                    "rationale": "The source gives a completed MRI result.",
                },
            },
            {
                "note_fragment": "I will request a repeat MRI scan next year.",
                "correct_event": {
                    "family": "investigation",
                    "anchor_text": "MRI",
                    "evidence": "I will request a repeat MRI scan next year.",
                    "event_state": {"decision_lane": "planned_investigation"},
                    "mentions": [],
                    "confidence": "high",
                    "rationale": "The source describes a future request.",
                },
            },
        ],
    ),
}


_MONTH_NUMBERS = {
    "january": "1",
    "february": "2",
    "march": "3",
    "april": "4",
    "may": "5",
    "june": "6",
    "july": "7",
    "august": "8",
    "september": "9",
    "october": "10",
    "november": "11",
    "december": "12",
}

_SF_TEMPORAL_ANCHOR_ATTRS = {
    "NumberOfTimePeriods",
    "LowerNumberOfTimePeriods",
    "UpperNumberOfTimePeriods",
    "TimePeriod",
    "TimeSince_or_TimeOfEvent",
    "PointInTime",
    "DayDate",
    "MonthDate",
    "YearDate",
    "AgeLower",
    "AgeUpper",
    "AgeUnit",
}


def to_predicted_letter(
    letter_id: str,
    mentions: list[structured.MentionForEvidence],
    *,
    note_text: str,
    target_family: str,
) -> tuple[PredictedLetter, list[str]]:
    profile = family_profile(target_family)
    warnings: list[str] = []
    target_mentions: list[structured.MentionForEvidence] = []
    for mention in _normalize_family_mentions(profile, mentions):
        if mention.entity != profile.entity:
            warnings.append(
                f"dropped_non_target_entity: target={profile.entity!r} entity={mention.entity!r}"
            )
            continue
        target_mentions.append(mention)

    evidence_valid, evidence_invalid, evidence_warnings = check_evidence(
        target_mentions,
        note_text=note_text,
    )
    warnings.extend(evidence_warnings)

    predicted_mentions: list[PredictedMention] = []
    for mention in evidence_valid:
        spec = ENTITY_REGISTRY[profile.entity]
        attrs = dict(mention.attributes)
        for projection_key in ("CUI", "CUIPhrase"):
            if projection_key in attrs:
                attrs.pop(projection_key)
                warnings.append(
                    f"{profile.entity}: dropped_model_supplied_projection_attribute: "
                    f"{projection_key!r}"
                )
        attrs = _repair_family_attributes(profile.entity, mention, attrs, warnings)
        repaired_attrs, attr_warnings = repair_attributes(attrs, spec=spec)
        warnings.extend(f"{profile.entity}: {warning}" for warning in attr_warnings)
        predicted_mentions.append(
            PredictedMention(
                entity=profile.entity,
                text=mention.text,
                attributes=repaired_attrs,
                evidence=mention.evidence,
                confidence=mention.confidence,
                rationale=mention.rationale,
                component_owner=COMPONENT_OWNER,
            )
        )

    predicted_mentions = structured._apply_render_safety_gates(predicted_mentions, warnings)
    predicted_mentions = _apply_family_safety_gates(profile.entity, predicted_mentions, warnings)
    pred = PredictedLetter(
        letter_id=letter_id,
        mentions=tuple(predicted_mentions),
        diagnostics={
            "prompt_version": PROMPT_VERSION,
            "pipeline_family": PIPELINE_FAMILY,
            "target_family": profile.entity,
            "n_evidence_invalid": len(evidence_invalid),
            "attribute_warnings": warnings,
        },
    )
    return project_cuis(pred), warnings


def _normalize_family_mentions(
    profile: FamilyProfile,
    mentions: Sequence[structured.MentionForEvidence],
) -> list[structured.MentionForEvidence]:
    if profile.entity not in {DIAGNOSIS.name, SEIZURE_FREQUENCY.name}:
        return list(mentions)

    normalized: list[structured.MentionForEvidence] = []
    for mention in mentions:
        if mention.entity != profile.entity:
            normalized.append(mention)
            continue
        if profile.entity == SEIZURE_FREQUENCY.name:
            anchor = _sf_anchor_text(f"{mention.text} {mention.evidence}")
            if anchor and anchor.lower() != mention.text.lower():
                normalized.append(mention.model_copy(update={"text": anchor}))
                continue
        lower = mention.text.lower()
        if (
            "epilepsy" in lower
            and any(token in lower for token in ("probable focal", "unclassified"))
            and lower.strip() != "epilepsy"
        ):
            match = re.search(r"\bepilepsy\b", mention.text, re.IGNORECASE)
            if match:
                attrs = dict(mention.attributes)
                attrs["Certainty"] = "5"
                normalized.append(
                    mention.model_copy(update={"text": match.group(0), "attributes": attrs})
                )
                continue
        normalized.append(mention)
    return normalized


def _sf_anchor_text(text: str) -> str:
    patterns = [
        r"\bfocal\s+seizures?\s+with\s+altered\s+awareness\b",
        r"\bfocal\s+impaired\s+awareness\s+seizures?\b",
        r"\bfocal\s+to\s+bilateral\s+convulsive\s+seizures?\b",
        r"\bfocal\s+to\s+bilateral\s+seizures?\b",
        r"\bsecondary\s+generalised\s+seizures?\b",
        r"\bsecondary\s+generalized\s+seizures?\b",
        r"\bgeneralised\s+tonic[- ](?:clonic|chronic)\s+seizures?\b",
        r"\bgeneralized\s+tonic[- ](?:clonic|chronic)\s+seizures?\b",
        r"\btonic[- ](?:clonic|chronic)\s+seizures?\b",
        r"\babsence[- ]like\s+seizures?\b",
        r"\babsence\s+seizures?\b",
        r"\babsences?\b",
        r"\bcomplex\s+partial\s+seizures?\b",
        r"\bpartial\s+motor\s+seizures?\b",
        r"\bfocal\s+motor\s+seizures?\b",
        r"\bdyscognitive\s+seizures?\b",
        r"\bmyoclonic\s+seizures?\b",
        r"\bmyoclonic\s+jerks?\b",
        r"\bfocal\s+seizures?\b",
        r"\bseizure\s+clusters?\b",
        r"\bseizure[- ]free\b",
        r"\bseizures?\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return ""


def _repair_family_attributes(
    entity: str,
    mention: structured.MentionForEvidence,
    attrs: dict[str, str],
    warnings: list[str],
) -> dict[str, str]:
    repaired = dict(attrs)
    evidence = f"{mention.evidence} {mention.text}".lower()
    if entity == DIAGNOSIS.name:
        _repair_diagnosis_attributes(evidence, repaired, warnings)
    elif entity == SEIZURE_FREQUENCY.name:
        _repair_sf_attributes(evidence, repaired, warnings)
    elif entity == INVESTIGATIONS.name:
        _repair_investigation_attributes(evidence, repaired, warnings)
    return repaired


def _repair_diagnosis_attributes(
    evidence: str,
    attrs: dict[str, str],
    warnings: list[str],
) -> None:
    if "DiagCategory" not in attrs:
        return
    if re.search(r"\bseizures\b", evidence):
        if attrs["DiagCategory"] != "MultipleSeizures":
            attrs["DiagCategory"] = "MultipleSeizures"
            warnings.append("Diagnosis: repaired_diag_category_plural_seizure_type")
    elif re.search(r"\bseizure\b", evidence) and "epilepsy" not in evidence:
        if attrs["DiagCategory"] != "SingleSeizure":
            attrs["DiagCategory"] = "SingleSeizure"
            warnings.append("Diagnosis: repaired_diag_category_singular_seizure_type")


def _repair_sf_attributes(
    evidence: str,
    attrs: dict[str, str],
    warnings: list[str],
) -> None:
    month = attrs.get("MonthDate", "").strip().lower()
    if month in _MONTH_NUMBERS:
        attrs["MonthDate"] = _MONTH_NUMBERS[month]
        warnings.append("SeizureFrequency: normalized_month_name_to_number")

    if attrs.get("TimePeriod") and not any(
        attrs.get(key)
        for key in (
            "NumberOfTimePeriods",
            "LowerNumberOfTimePeriods",
            "UpperNumberOfTimePeriods",
        )
    ):
        if re.search(r"\b(per|every|each)\b", evidence):
            attrs["NumberOfTimePeriods"] = "1"
            warnings.append("SeizureFrequency: added_default_period_count")

    if attrs.get("TimePeriod") and re.search(r"\b(per|every|each)\b", evidence):
        if not re.search(r"\blast (?:event|seizure|clinic)", evidence):
            for key in ("YearDate", "TimeSince_or_TimeOfEvent"):
                if attrs.pop(key, None) is not None:
                    warnings.append(f"SeizureFrequency: removed_cadence_{key}")

    if re.search(r"\bsince (?:the )?last clinic", evidence):
        attrs.setdefault("TimeSince_or_TimeOfEvent", "Since")
        attrs.setdefault("PointInTime", "LastClinic")
        warnings.append("SeizureFrequency: added_last_clinic_anchor")

    if re.search(r"\blast (?:event|seizure)\b", evidence):
        attrs.setdefault("TimeSince_or_TimeOfEvent", "Since")
        attrs.setdefault("NumberOfSeizures", "0")
        warnings.append("SeizureFrequency: added_last_event_anchor")
    elif attrs.get("YearDate") and re.search(r"\bseizures?\b", evidence):
        attrs.setdefault("TimeSince_or_TimeOfEvent", "During")
        warnings.append("SeizureFrequency: added_dated_count_anchor")


def _repair_investigation_attributes(
    evidence: str,
    attrs: dict[str, str],
    warnings: list[str],
) -> None:
    for modality in ("MRI", "CT", "EEG"):
        performed_key = f"{modality}_Performed"
        result_key = f"{modality}_Results"
        if attrs.get(performed_key) != "Yes" or attrs.get(result_key):
            continue
        if "normal" in evidence and not re.search(r"\babnormal\b", evidence):
            attrs[result_key] = "Normal"
            warnings.append(f"Investigations: inferred_{modality.lower()}_normal_result")
        elif modality == "EEG" and re.search(
            r"\b(abnormal|slowing|spike|wave|sharp|captur(?:ed|ing))\b",
            evidence,
        ):
            attrs[result_key] = "Abnormal"
            warnings.append("Investigations: inferred_eeg_abnormal_result")
        elif modality in {"MRI", "CT"} and re.search(r"\b(abnormal|lesion|sclerosis)\b", evidence):
            attrs[result_key] = "Abnormal"
            warnings.append(f"Investigations: inferred_{modality.lower()}_abnormal_result")


def _apply_family_safety_gates(
    entity: str,
    mentions: list[PredictedMention],
    warnings: list[str],
) -> list[PredictedMention]:
    if entity != SEIZURE_FREQUENCY.name:
        return mentions
    kept: list[PredictedMention] = []
    for mention in mentions:
        lower = f"{mention.text} {mention.evidence}".lower()
        if re.search(
            r"\b(not had any other episode which may resemble|"
            r"no events which resemble|not had any events which resemble)\b",
            lower,
        ):
            warnings.append(
                f"SeizureFrequency: dropped_negated_resemblance_statement: {mention.text!r}"
            )
            continue
        if (
            "seizure free" in lower
            and str(mention.attributes.get("NumberOfSeizures", "")).strip() == "0"
            and not any(
                mention.attributes.get(key)
                for key in _SF_TEMPORAL_ANCHOR_ATTRS - {"TimeSince_or_TimeOfEvent"}
            )
        ):
            warnings.append(
                f"SeizureFrequency: dropped_bare_seizure_free_without_anchor: {mention.text!r}"
            )
            continue
        kept.append(mention)
    return kept


def run_split(
    letters: Sequence[ExectLetter],
    *,
    target_family: str,
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
    profile = family_profile(target_family)
    program = DspyFamilyConditionedEventLedgerExtractor()
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
    requested = set(order)
    existing_rows, completed = read_completed(
        checkpoint_jsonl_path if resume else None,
        key="letter_id",
    )
    rows: list[dict[str, Any]] = [r for r in existing_rows if r.get("letter_id") in requested]
    n_resumed = len(rows)
    todo = pending_items(letters, completed, key_of=lambda letter: letter.letter_id)

    for letter in todo:
        prompt_input_json = build_prompt_input(letter, profile.entity)
        raw_output = ""
        call_error: str | None = None
        if mode == "live":
            try:
                prediction = program(prompt_input_json=prompt_input_json)
                raw_output = str(prediction.extraction_json)
            except Exception as exc:  # pragma: no cover
                call_error = f"{type(exc).__name__}: {exc}"

        record, parse_errors = (
            structured.parse_structured_events_json(raw_output)
            if raw_output
            else (None, ["not_run"])
        )
        mentions = structured.flatten_events(record) if record else []
        predicted_letter, gate_warnings = to_predicted_letter(
            letter.letter_id,
            mentions,
            note_text=letter.note_text,
            target_family=profile.entity,
        )

        rows.append(
            {
                "letter_id": letter.letter_id,
                "split": split,
                "target_family": profile.entity,
                "prompt_version": PROMPT_VERSION,
                "pipeline_family": PIPELINE_FAMILY,
                "model": model,
                "mode": mode,
                "prompt_input_json": prompt_input_json,
                "raw_output": raw_output,
                "call_error": call_error,
                "parse_errors": parse_errors,
                "gate_warnings": gate_warnings,
                "n_events_raw": len(record.clinical_events) if record else 0,
                "n_mentions_raw": len(mentions),
                "n_mentions_scored": len(predicted_letter.mentions),
                "n_evidence_invalid": len(mentions) - len(predicted_letter.mentions),
                "structured_events": [
                    event.model_dump() for event in (record.clinical_events if record else [])
                ],
                "predicted_mentions": [_mention_to_row(m) for m in predicted_letter.mentions],
                "gold_mentions": [
                    {"entity": a.entity, "text": a.text, "attributes": dict(a.attributes)}
                    for a in letter.entities(profile.entity)
                ],
            }
        )

        if progress_every and (len(rows) - n_resumed) % progress_every == 0:
            _emit_checkpoint(
                rows,
                profile=profile,
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
        "target_family": profile.entity,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "mode": mode,
        "split": split,
        "n_letters": len(letters),
        "n_resumed": n_resumed,
        "dspy_version": getattr(dspy, "__version__", "unknown"),
    }
    metadata["summary"] = summarize_rows(rows, target_family=profile.entity)
    return rows, metadata


def summarize_rows(
    rows: Sequence[dict[str, Any]],
    *,
    target_family: str | None = None,
) -> dict[str, Any]:
    if not rows:
        return {"examples": 0}
    entity = normalize_target_family(target_family or str(rows[0]["target_family"]))
    n_mentions_raw = sum(int(r.get("n_mentions_raw", 0)) for r in rows)
    n_evidence_invalid = sum(int(r.get("n_evidence_invalid", 0)) for r in rows)
    gold_letters = _reconstruct_letters(rows, key="gold_mentions", target_family=entity)
    pred_letters = _reconstruct_letters(rows, key="predicted_mentions", target_family=entity)
    headline = _headline_score(entity, gold_letters, pred_letters)
    source_near = source_near_diagnostic(
        gold_letters,
        pred_letters,
        [entity],
        semantic_config_for,
    )

    return {
        "examples": len(rows),
        "target_family": entity,
        "call_failures": sum(bool(r.get("call_error")) for r in rows),
        "parse_failures": sum(_has_blocking_parse_issue(r.get("parse_errors")) for r in rows),
        "n_events_raw": sum(int(r.get("n_events_raw", 0)) for r in rows),
        "n_mentions_raw": n_mentions_raw,
        "n_mentions_scored": sum(int(r.get("n_mentions_scored", 0)) for r in rows),
        "n_evidence_invalid": n_evidence_invalid,
        "evidence_validity_rate": (
            round((n_mentions_raw - n_evidence_invalid) / n_mentions_raw, 4)
            if n_mentions_raw
            else 1.0
        ),
        "clinical_recovery": {
            "headline": _prf1_to_dict(headline),
            "ideal_f1_target": IDEAL_HEADLINE_F1_TARGET,
            "current_comparator_f1": CURRENT_COMPARATOR_HEADLINE_F1[entity],
        },
        "format_layers": {
            "phrase_only": score_entity(
                gold_letters, pred_letters, entity, PHRASE_ONLY
            ).per_item.model_dump(),
            "semantic": score_entity(
                gold_letters,
                pred_letters,
                entity,
                semantic_config_for(entity),
            ).per_item.model_dump(),
            "benchmark": score_entity(
                gold_letters,
                pred_letters,
                entity,
                benchmark_config_for(entity),
            ).per_item.model_dump(),
        },
        "source_near": source_near.per_entity[entity].model_dump(),
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
    clinical = summary.get("clinical_recovery", {})
    headline = clinical.get("headline", {})
    lines = [
        "# ExECTv2 Family-Conditioned Event Ledger",
        "",
        f"- JSONL: `{jsonl_path}`",
        f"- Prompt version: `{metadata.get('prompt_version', PROMPT_VERSION)}`",
        f"- Pipeline family: `{metadata.get('pipeline_family', PIPELINE_FAMILY)}`",
        f"- Target family: `{metadata.get('target_family') or summary.get('target_family')}`",
        f"- Split: `{metadata.get('split')}`",
        f"- Model: `{metadata.get('model')}`",
        f"- Mode: `{metadata.get('mode')}`",
        f"- Letters: {summary.get('examples', 0)}",
        "",
        "## Gate Summary",
        "",
        f"- Call failures: {summary.get('call_failures', 0)}",
        f"- Parse/schema failures: {summary.get('parse_failures', 0)}",
        f"- Clinical events raw: {summary.get('n_events_raw', 0)}",
        f"- Mentions raw: {summary.get('n_mentions_raw', 0)}",
        f"- Mentions scored: {summary.get('n_mentions_scored', 0)}",
        f"- Evidence-invalid dropped: {summary.get('n_evidence_invalid', 0)}",
        f"- Evidence validity rate: {summary.get('evidence_validity_rate', 0.0):.4f}",
        "",
        "## Clinical Recovery",
        "",
        "| Metric | F1 | Precision | Recall | TP | FP | FN |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        (
            f"| target headline | {headline.get('f1', 0):.3f} | "
            f"{headline.get('precision', 0):.3f} | {headline.get('recall', 0):.3f} | "
            f"{headline.get('tp', 0)} | {headline.get('fp', 0)} | {headline.get('fn', 0)} |"
        ),
        "",
        f"- Ideal target F1: {clinical.get('ideal_f1_target', IDEAL_HEADLINE_F1_TARGET):.3f}",
        f"- Current comparator F1: {clinical.get('current_comparator_f1', 0.0):.3f}",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def _headline_score(
    entity: str,
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
) -> Any:
    if entity == PRESCRIPTION.name:
        return score_prescription_components(gold_letters, pred_letters).clinical_headline
    if entity == DIAGNOSIS.name:
        return score_concept_identity(gold_letters, pred_letters, DIAGNOSIS.name).concept_assertion
    if entity == SEIZURE_FREQUENCY.name:
        return score_frequency_state(gold_letters, pred_letters).clinical_headline
    if entity == INVESTIGATIONS.name:
        return score_investigations_components(gold_letters, pred_letters).clinical_headline
    raise ValueError(f"Unsupported target family: {entity!r}")


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


def _reconstruct_letters(
    rows: Sequence[dict[str, Any]],
    *,
    key: str,
    target_family: str,
) -> list[ExectLetter]:
    letters: list[ExectLetter] = []
    for row in rows:
        annotations = tuple(
            ExectAnnotation(
                entity=str(m["entity"]),
                text=str(m["text"]),
                attributes={str(k): str(v) for k, v in dict(m.get("attributes") or {}).items()},
            )
            for m in (row.get(key) or [])
            if str(m.get("entity")) == target_family
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


def _emit_checkpoint(
    rows: Sequence[dict[str, Any]],
    *,
    profile: FamilyProfile,
    total: int,
    jsonl_path: Path | None,
    report_path: Path | None,
    split: str,
    model: str,
    mode: str,
) -> None:
    summary = summarize_rows(rows, target_family=profile.entity)
    if jsonl_path is not None:
        write_jsonl(rows, jsonl_path)
    if report_path is not None and jsonl_path is not None:
        write_report(
            rows,
            {
                "prompt_version": PROMPT_VERSION,
                "pipeline_family": PIPELINE_FAMILY,
                "target_family": profile.entity,
                "split": split,
                "model": model,
                "mode": mode,
                "summary": summary,
            },
            _checkpoint_report_path(report_path),
            jsonl_path=jsonl_path,
        )
    progress = {
        "processed": len(rows),
        "total": total,
        "target_family": profile.entity,
        "call_failures": summary.get("call_failures", 0),
        "parse_failures": summary.get("parse_failures", 0),
        "n_mentions_scored": summary.get("n_mentions_scored", 0),
    }
    print(json.dumps(progress, sort_keys=True), file=sys.stderr, flush=True)


def _checkpoint_report_path(path: Path) -> Path:
    if path.stem.endswith("_checkpoint"):
        return path
    return path.with_name(f"{path.stem}_checkpoint{path.suffix}")
