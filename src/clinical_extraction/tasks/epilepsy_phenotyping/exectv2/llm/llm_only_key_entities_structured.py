"""Single-prompt structured-event extractor for the four key ExECTv2 families.

This module tests the architectural extreme the per-entity work deliberately
left open: one model call reads the letter directly and emits a shared
event-style schema for medication, diagnosis, seizure frequency, and
investigations. The LLM owns clinical event selection; deterministic code only
validates shape, checks evidence, strips illegal attributes, projects CUIs, and
scores the flattened rendered mentions.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict

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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    _extract_json_object,
    _has_blocking_parse_issue,
    check_evidence,
    repair_attributes,
    write_jsonl,
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

PROMPT_VERSION = "exectv2_llm_only_key_entities_structured_v0.3"
PIPELINE_FAMILY = "exectv2_llm_only_key_entities_structured"
COMPONENT_OWNER = "llm_only_key_entities_structured"

KEY_ENTITY_NAMES: tuple[str, ...] = (
    PRESCRIPTION.name,
    DIAGNOSIS.name,
    SEIZURE_FREQUENCY.name,
    INVESTIGATIONS.name,
)

KEY_ENTITY_ITEM_F1_TARGET = 0.80
PUBLISHED_PER_ENTITY_ITEM_F1: dict[str, float] = {
    "Prescription": 0.87,
    "Diagnosis": 0.85,
    "SeizureFrequency": 0.66,
    "Investigations": 0.95,
}

EventFamily = Literal["medication", "diagnosis", "seizure_frequency", "investigation"]


class RenderedMentionRecord(BaseModel):
    """One scorer-facing mention rendered from a structured clinical event."""

    model_config = ConfigDict(extra="ignore")

    entity: str
    text: str
    attributes: dict[str, Any] = {}


class StructuredClinicalEvent(BaseModel):
    """One source-near clinical event with one or more scorer-facing renderings."""

    model_config = ConfigDict(extra="ignore")

    family: EventFamily
    anchor_text: str
    evidence: str
    event_state: dict[str, Any] = {}
    mentions: list[RenderedMentionRecord] = []
    confidence: Literal["low", "medium", "high"] = "medium"
    rationale: str = ""


class StructuredExtractionRecord(BaseModel):
    """Structured output for one letter."""

    model_config = ConfigDict(extra="ignore")

    clinical_events: list[StructuredClinicalEvent] = []


class MentionForEvidence(BaseModel):
    """Minimal mention shape accepted by the shared evidence gate."""

    text: str
    attributes: dict[str, str] = {}
    evidence: str
    confidence: Literal["low", "medium", "high"] = "medium"
    rationale: str = ""
    entity: str = ""


class ExECTv2KeyEntitiesStructuredSignature(dspy.Signature):
    """Read one clinical letter and produce structured clinical events.

    Return exactly one JSON object with a 'clinical_events' list. No markdown.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter and task instructions."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"clinical_events\": [{\"family\": ..., "
            "\"anchor_text\": ..., \"evidence\": ..., \"event_state\": {...}, "
            "\"mentions\": [{\"entity\": ..., \"text\": ..., \"attributes\": {...}}], "
            "\"confidence\": ..., \"rationale\": ...}, ...]}"
        )
    )


class DspyKeyEntitiesStructuredExtractor(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(ExECTv2KeyEntitiesStructuredSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def build_prompt_input(letter: ExectLetter) -> str:
    """Build the single-prompt structured-event payload."""

    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": (
            "Read the clinical letter once. Build a compact list of clinical events "
            "for medication, diagnosis, seizure frequency, and investigations. Each "
            "event may render one or more entity mentions when the same clinical fact "
            "validly belongs to more than one requested family."
        ),
        "output_schema": {
            "clinical_events": [
                {
                    "family": "medication | diagnosis | seizure_frequency | investigation",
                    "anchor_text": (
                        "Short exact substring naming the clinical event. Use the "
                        "family guidance below."
                    ),
                    "evidence": (
                        "Exact clause or sentence copied from the letter that supports "
                        "the event and all rendered mentions."
                    ),
                    "event_state": (
                        "Source-near state for clinical reasoning, such as medication "
                        "dose/frequency, diagnostic assertion, seizure rate, or test "
                        "result. Values must be strings."
                    ),
                    "mentions": [
                        {
                            "entity": (
                                "One of Prescription, Diagnosis, SeizureFrequency, "
                                "Investigations."
                            ),
                            "text": "Short exact substring used for scoring this entity.",
                            "attributes": "Only attributes legal for that entity.",
                        }
                    ],
                    "confidence": "low | medium | high",
                    "rationale": "One brief sentence explaining the event.",
                }
            ]
        },
        "family_guidance": _family_guidance(),
        "attribute_vocabulary": _attribute_vocabulary(),
        "worked_examples": _worked_examples(),
        "clinical_rules": [
            "Use one event per medication, diagnostic concept, seizure-rate statement, or test.",
            "Both anchor_text and evidence must be exact substrings of the letter.",
            "Every rendered mention text must be an exact substring of the letter.",
            (
                "Named seizure types can render both Diagnosis and SeizureFrequency "
                "when the letter states both the type and a rate or seizure-free state."
            ),
            (
                "Do not force a single entity if the same fact belongs to more than "
                "one requested family; render each valid entity separately."
            ),
            (
                "For diagnosis, split compound seizure clauses into atomic diagnostic "
                "concepts when the letter names more than one seizure type."
            ),
            (
                "Every Diagnosis mention must include Certainty and Negation. Use "
                "Certainty='5' and Negation='Affirmed' for directly stated diagnoses "
                "or seizure types unless the letter explicitly says otherwise."
            ),
            (
                "For Diagnosis certainty, preserve diagnostic hedging: use "
                "Certainty='4' for probable or likely diagnoses, Certainty='3' for "
                "possible, suspected, query, or differential diagnoses, and "
                "Certainty='5' only for established or unqualified statements."
            ),
            (
                "For Diagnosis concepts, prefer the most specific epilepsy syndrome "
                "or seizure type stated in the letter, such as focal epilepsy, "
                "temporal lobe epilepsy, primary generalised epilepsy, or JME; do not "
                "collapse these to generic 'epilepsy' when the specific phrase is "
                "present."
            ),
            (
                "Do not render vague symptoms, blackout/loss-of-consciousness "
                "descriptions, anxiety, or non-epileptic events as Diagnosis unless "
                "the same phrase is explicitly asserted as an epileptic seizure, "
                "epilepsy diagnosis, or named seizure type."
            ),
            (
                "For diagnosis, use DiagCategory='Epilepsy' for epilepsy syndromes or "
                "diagnoses, 'SingleSeizure' for one named seizure type, and "
                "'MultipleSeizures' only when the mention represents multiple seizure "
                "types or recurrent seizures as a category."
            ),
            (
                "For seizure frequency, mention text is only the seizure-type anchor; "
                "do not include counts, dates, or the words 'seizure frequency' in text. "
                "event_state and attributes carry counts, periods, dates, and changes."
            ),
            (
                "For SeizureFrequency anchors, use the generic seizure phrase when "
                "the count refers to seizures generally; use a named seizure type only "
                "when the count explicitly belongs to that type."
            ),
            (
                "For seizure-frequency ranges, never write values like '2 to 3', "
                "'2-4', or '3 or 4' in NumberOfSeizures. Use LowerNumberOfSeizures "
                "and UpperNumberOfSeizures instead."
            ),
            (
                "For interval rates such as 'one every 3 to 4 weeks', set "
                "NumberOfSeizures='1', LowerNumberOfTimePeriods='3', "
                "UpperNumberOfTimePeriods='4', and TimePeriod='Week'. Do not convert "
                "the interval into 3 to 4 seizures."
            ),
            (
                "For cluster statements, keep the cluster as the clinical event when "
                "the note counts clusters, for example text 'cluster of seizures' with "
                "NumberOfSeizures='1' and the stated date or time frame."
            ),
            (
                "For frequency-change statements without an exact count, render a "
                "SeizureFrequency mention with FrequencyChange only, such as "
                "Frequent, Infrequent, Increased, Decreased, or Same."
            ),
            (
                "For dated counts such as '2 to 3 in March', use Lower/Upper count "
                "fields plus MonthDate or YearDate and TimeSince_or_TimeOfEvent='During'; "
                "do not invent TimePeriod='Month' unless the note says per month."
            ),
            (
                "For 'since last clinic', use TimeSince_or_TimeOfEvent='Since' and "
                "PointInTime='LastClinic'; do not put 'since last clinic' in TimePeriod."
            ),
            (
                "For last-event or seizure-free statements, use NumberOfSeizures='0' "
                "with TimeSince_or_TimeOfEvent='Since' and the stated MonthDate, "
                "YearDate, or PointInTime. Do not convert last-event dates into an "
                "annual recurring rate."
            ),
            (
                "For seizure-free statements, anchor text to the underlying seizure "
                "phrase when it is present in the same sentence, such as 'seizures' or "
                "'focal seizures'; otherwise use the exact seizure-free phrase."
            ),
            (
                "For medication, mention text is the medication name where possible; "
                "dose and frequency belong in attributes."
            ),
            (
                "For medication list entries that contain a compact regimen, render "
                "text as the exact medication item span including dose and frequency "
                "when those words are part of the same short line, for example "
                "'Topiramate 100 mg BD'."
            ),
            (
                "For investigations, use one event per modality such as EEG, MRI, or "
                "CT; put performed, result, and EEG type in attributes."
            ),
            (
                "Do not render future planned, requested, repeat, or follow-up "
                "investigations as performed tests. Only render completed tests or "
                "tests with a stated result."
            ),
            (
                "Do not render a bare modality-only investigation when the note gives "
                "no completion/result statement, and do not add a duplicate modality-only "
                "mention when a result-bearing mention for the same modality is already "
                "rendered."
            ),
            (
                "For investigation text, use the shortest exact modality phrase: "
                "'MRI scan' if those words occur together, otherwise 'MRI'; likewise "
                "'EEG' or 'CT'. Do not include dates or results in text."
            ),
            (
                "Only include EEG_Type when the letter explicitly says sleep-deprived "
                "EEG or video telemetry. Do not default a plain EEG to Standard."
            ),
            "Do not invent CUI values. If a CUI is not explicitly available, omit it.",
            "If no requested findings are present, return {\"clinical_events\": []}.",
            "Return exactly one JSON object. No markdown code fences.",
        ],
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _family_guidance() -> dict[str, str]:
    return {
        "medication": (
            "Anti-seizure medication events. Render Prescription mentions with "
            "DrugName, DrugDose, DoseUnit, and Frequency when stated. The rendered "
            "text should preserve the medication item's annotation-facing span: "
            "full compact regimen when present in a medication list, bare drug name "
            "when that is all the note states."
        ),
        "diagnosis": (
            "Diagnostic concepts such as epilepsy, focal epilepsy, seizure disorder, "
            "or named seizure types. Render atomic Diagnosis mentions with "
            "DiagCategory, Certainty, and Negation. Preserve uncertainty words and "
            "avoid vague symptoms or non-epileptic differentials unless they are "
            "explicitly asserted as epileptic diagnoses."
        ),
        "seizure_frequency": (
            "How often a seizure type occurs, including seizure-free duration, "
            "ranges, interval cadence, cluster counts, dated counts, and frequency "
            "change. Preserve the stated seizure anchor and temporal frame instead "
            "of converting it into a guessed rate."
        ),
        "investigation": (
            "EEG, MRI, CT, telemetry, and related investigation statements. Render "
            "Investigations with performed/result/type attributes only for completed "
            "or resulted tests, not planned repeats or bare modality references."
        ),
    }


def _attribute_vocabulary() -> dict[str, dict[str, Any]]:
    vocab: dict[str, dict[str, Any]] = {}
    for entity_name in KEY_ENTITY_NAMES:
        spec = ENTITY_REGISTRY[entity_name]
        attrs: dict[str, Any] = {}
        for attr in sorted(spec.legal_attributes):
            if attr == "CUI":
                attrs[attr] = "UMLS CUI only if explicitly available; otherwise omit."
            elif attr == "CUIPhrase":
                attrs[attr] = "Clean phrase only if explicitly available; otherwise omit."
            elif attr in spec.closed_vocab:
                attrs[attr] = sorted(spec.closed_vocab[attr])
            else:
                attrs[attr] = "string copied or normalized from the letter."
        vocab[entity_name] = attrs
    return vocab


def _worked_examples() -> list[dict[str, Any]]:
    return [
        {
            "note_fragment": "She has focal epilepsy with 2 focal seizures per month.",
            "correct_event": {
                "family": "seizure_frequency",
                "anchor_text": "focal seizures",
                "evidence": "focal epilepsy with 2 focal seizures per month",
                "event_state": {
                    "diagnosis": "focal epilepsy",
                    "seizure_type": "focal seizures",
                    "rate": "2 per 1 Month",
                },
                "mentions": [
                    {
                        "entity": "Diagnosis",
                        "text": "focal epilepsy",
                        "attributes": {
                            "DiagCategory": "Epilepsy",
                            "Certainty": "5",
                            "Negation": "Affirmed",
                        },
                    },
                    {
                        "entity": "Diagnosis",
                        "text": "focal seizures",
                        "attributes": {
                            "DiagCategory": "MultipleSeizures",
                            "Certainty": "5",
                            "Negation": "Affirmed",
                        },
                    },
                    {
                        "entity": "SeizureFrequency",
                        "text": "focal seizures",
                        "attributes": {
                            "LowerNumberOfSeizures": "2",
                            "UpperNumberOfSeizures": "3",
                            "MonthDate": "3",
                            "TimeSince_or_TimeOfEvent": "During",
                        },
                    },
                ],
                "confidence": "high",
                "rationale": "The diagnosis and dated seizure count are directly stated.",
            },
        },
        {
            "note_fragment": (
                "Since her last clinic appointment she has had four secondary "
                "generalised seizures."
            ),
            "correct_event": {
                "family": "seizure_frequency",
                "anchor_text": "secondary generalised seizures",
                "evidence": (
                    "Since her last clinic appointment she has had four secondary "
                    "generalised seizures."
                ),
                "event_state": {
                    "seizure_type": "secondary generalised seizures",
                    "count": "4",
                    "frame": "since last clinic",
                },
                "mentions": [
                    {
                        "entity": "Diagnosis",
                        "text": "secondary generalised seizures",
                        "attributes": {
                            "DiagCategory": "SingleSeizure",
                            "Certainty": "5",
                            "Negation": "Affirmed",
                        },
                    },
                    {
                        "entity": "SeizureFrequency",
                        "text": "secondary generalised seizures",
                        "attributes": {
                            "NumberOfSeizures": "4",
                            "TimeSince_or_TimeOfEvent": "Since",
                            "PointInTime": "LastClinic",
                        },
                    },
                ],
                "confidence": "high",
                "rationale": "The count is tied to the period since last clinic.",
            },
        },
        {
            "note_fragment": "She has been seizure-free since July 2016.",
            "correct_event": {
                "family": "seizure_frequency",
                "anchor_text": "seizure-free",
                "evidence": "seizure-free since July 2016",
                "event_state": {"state": "seizure-free", "since": "July 2016"},
                "mentions": [
                    {
                        "entity": "SeizureFrequency",
                        "text": "seizure-free",
                        "attributes": {
                            "NumberOfSeizures": "0",
                            "MonthDate": "7",
                            "YearDate": "2016",
                            "TimeSince_or_TimeOfEvent": "Since",
                        },
                    }
                ],
                "confidence": "high",
                "rationale": "The note states seizure-free since a month and year.",
            },
        },
        {
            "note_fragment": "She has seizures every 3 to 4 weeks.",
            "correct_event": {
                "family": "seizure_frequency",
                "anchor_text": "seizures",
                "evidence": "seizures every 3 to 4 weeks",
                "event_state": {
                    "seizure_type": "seizures",
                    "rate": "1 per 3 to 4 Week",
                },
                "mentions": [
                    {
                        "entity": "SeizureFrequency",
                        "text": "seizures",
                        "attributes": {
                            "NumberOfSeizures": "1",
                            "LowerNumberOfTimePeriods": "3",
                            "UpperNumberOfTimePeriods": "4",
                            "TimePeriod": "Week",
                        },
                    }
                ],
                "confidence": "high",
                "rationale": "The count is one seizure over a 3 to 4 week interval.",
            },
        },
        {
            "note_fragment": "She had a cluster of seizures in August 2017.",
            "correct_event": {
                "family": "seizure_frequency",
                "anchor_text": "cluster of seizures",
                "evidence": "cluster of seizures in August 2017",
                "event_state": {"event": "cluster", "date": "August 2017"},
                "mentions": [
                    {
                        "entity": "SeizureFrequency",
                        "text": "cluster of seizures",
                        "attributes": {
                            "NumberOfSeizures": "1",
                            "MonthDate": "8",
                            "YearDate": "2017",
                            "TimeSince_or_TimeOfEvent": "During",
                        },
                    }
                ],
                "confidence": "high",
                "rationale": "The note counts one cluster rather than individual seizures.",
            },
        },
        {
            "note_fragment": "Since changing medication her focal seizures are infrequent.",
            "correct_event": {
                "family": "seizure_frequency",
                "anchor_text": "focal seizures",
                "evidence": "focal seizures are infrequent",
                "event_state": {"change": "infrequent", "anchor": "DrugChange"},
                "mentions": [
                    {
                        "entity": "SeizureFrequency",
                        "text": "focal seizures",
                        "attributes": {
                            "FrequencyChange": "Infrequent",
                            "PointInTime": "DrugChange",
                        },
                    }
                ],
                "confidence": "high",
                "rationale": "The statement gives frequency change without an exact count.",
            },
        },
        {
            "note_fragment": "She has 2 focal seizures per month.",
            "correct_event": {
                "family": "seizure_frequency",
                "anchor_text": "focal seizures",
                "evidence": "2 focal seizures per month",
                "event_state": {"seizure_type": "focal seizures", "rate": "2 per 1 Month"},
                "mentions": [
                    {
                        "entity": "Diagnosis",
                        "text": "focal seizures",
                        "attributes": {
                            "DiagCategory": "SingleSeizure",
                            "Certainty": "5",
                            "Negation": "Affirmed",
                        },
                    },
                    {
                        "entity": "SeizureFrequency",
                        "text": "focal seizures",
                        "attributes": {
                            "NumberOfSeizures": "2",
                            "NumberOfTimePeriods": "1",
                            "TimePeriod": "Month",
                        },
                    },
                ],
                "confidence": "high",
                "rationale": "The diagnosis and seizure rate are directly stated.",
            },
        },
        {
            "note_fragment": "Current treatment is lamotrigine 200 mg twice daily.",
            "correct_event": {
                "family": "medication",
                "anchor_text": "lamotrigine",
                "evidence": "lamotrigine 200 mg twice daily",
                "event_state": {
                    "drug": "lamotrigine",
                    "dose": "200 mg",
                    "frequency": "twice daily",
                },
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
                "rationale": "Medication, dose, and frequency are stated.",
            },
        },
        {
            "note_fragment": "Diagnosis: probable temporal lobe epilepsy.",
            "correct_event": {
                "family": "diagnosis",
                "anchor_text": "temporal lobe epilepsy",
                "evidence": "probable temporal lobe epilepsy",
                "event_state": {
                    "diagnosis": "temporal lobe epilepsy",
                    "certainty": "probable",
                },
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
                "rationale": "Probable maps to Certainty 4 while preserving the specific syndrome.",
            },
        },
        {
            "note_fragment": (
                "She has anxiety and unwitnessed blackouts, but no diagnosis of epilepsy."
            ),
            "correct_event": {
                "family": "diagnosis",
                "anchor_text": "no diagnosis of epilepsy",
                "evidence": "no diagnosis of epilepsy",
                "event_state": {"diagnosis": "epilepsy", "negation": "negated"},
                "mentions": [
                    {
                        "entity": "Diagnosis",
                        "text": "epilepsy",
                        "attributes": {
                            "DiagCategory": "Epilepsy",
                            "Certainty": "5",
                            "Negation": "Negated",
                        },
                    }
                ],
                "confidence": "high",
                "rationale": (
                    "Anxiety and blackouts are not rendered as Diagnosis; "
                    "epilepsy is negated."
                ),
            },
        },
        {
            "note_fragment": "MRI brain was normal; sleep-deprived EEG showed sharp waves.",
            "correct_event": [
                {
                    "family": "investigation",
                    "anchor_text": "MRI",
                    "evidence": "MRI brain was normal",
                    "event_state": {"modality": "MRI", "result": "Normal"},
                    "mentions": [
                        {
                            "entity": "Investigations",
                            "text": "MRI",
                            "attributes": {"MRI_Performed": "Yes", "MRI_Results": "Normal"},
                        }
                    ],
                    "confidence": "high",
                    "rationale": "MRI result is normal.",
                },
                {
                    "family": "investigation",
                    "anchor_text": "sleep-deprived EEG",
                    "evidence": "sleep-deprived EEG showed sharp waves",
                    "event_state": {
                        "modality": "EEG",
                        "type": "SleepDeprived",
                        "result": "Abnormal",
                    },
                    "mentions": [
                        {
                            "entity": "Investigations",
                            "text": "sleep-deprived EEG",
                            "attributes": {
                                "EEG_Performed": "Yes",
                                "EEG_Type": "SleepDeprived",
                                "EEG_Results": "Abnormal",
                            },
                        }
                    ],
                    "confidence": "high",
                    "rationale": "Sleep-deprived EEG showed sharp waves.",
                },
            ],
        },
        {
            "note_fragment": "EEG 2012 generalised spike and wave.",
            "correct_event": {
                "family": "investigation",
                "anchor_text": "EEG",
                "evidence": "EEG 2012 generalised spike and wave",
                "event_state": {"modality": "EEG", "result": "Abnormal"},
                "mentions": [
                    {
                        "entity": "Investigations",
                        "text": "EEG",
                        "attributes": {"EEG_Performed": "Yes", "EEG_Results": "Abnormal"},
                    }
                ],
                "confidence": "high",
                "rationale": "The plain EEG is abnormal; no EEG_Type is stated.",
            },
        },
        {
            "note_fragment": "I will request a repeat MRI scan next year.",
            "correct_event": {
                "family": "investigation",
                "anchor_text": "MRI scan",
                "evidence": "I will request a repeat MRI scan next year.",
                "event_state": {"planned": "repeat MRI"},
                "mentions": [],
                "confidence": "high",
                "rationale": "A planned repeat MRI is not a completed investigation mention.",
            },
        },
    ]


def parse_structured_events_json(
    raw_output: str,
) -> tuple[StructuredExtractionRecord | None, list[str]]:
    try:
        payload = json.loads(_extract_json_object(raw_output))
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json: {exc.msg}"]

    payload, coerce_notes = _coerce_structured_payload(payload)
    try:
        record = StructuredExtractionRecord.model_validate(payload)
    except Exception as exc:
        return None, [f"schema_validation_error: {exc}"]
    return record, list(coerce_notes)


def _coerce_structured_payload(payload: Any) -> tuple[Any, list[str]]:
    """Coerce event and mention state values to strings and preserve diagnostics."""

    notes: list[str] = []
    if not isinstance(payload, dict):
        return payload, notes
    events = payload.get("clinical_events")
    if events is None and isinstance(payload.get("mentions"), list):
        events = [_legacy_mention_to_event(m) for m in payload["mentions"]]
        notes.append("coerced_legacy_mentions_to_events")
    if not isinstance(events, list):
        return payload, notes

    coerced_events: list[Any] = []
    for event_index, event in enumerate(events):
        if not isinstance(event, dict):
            coerced_events.append(event)
            continue
        event = dict(event)
        event["event_state"] = _stringify_mapping(
            event.get("event_state") or {},
            notes=notes,
            prefix=f"event[{event_index}].event_state",
        )
        mentions = event.get("mentions")
        if isinstance(mentions, list):
            coerced_mentions: list[Any] = []
            for mention_index, mention in enumerate(mentions):
                if not isinstance(mention, dict):
                    coerced_mentions.append(mention)
                    continue
                mention = dict(mention)
                mention["attributes"] = _stringify_mapping(
                    mention.get("attributes") or {},
                    notes=notes,
                    prefix=f"event[{event_index}].mentions[{mention_index}].attributes",
                )
                coerced_mentions.append(mention)
            event["mentions"] = coerced_mentions
        coerced_events.append(event)
    return {**payload, "clinical_events": coerced_events}, notes


def _legacy_mention_to_event(mention: Any) -> dict[str, Any]:
    entity = str(mention.get("entity", "")) if isinstance(mention, dict) else ""
    family = {
        "Prescription": "medication",
        "Diagnosis": "diagnosis",
        "SeizureFrequency": "seizure_frequency",
        "Investigations": "investigation",
    }.get(entity, "diagnosis")
    if not isinstance(mention, dict):
        mention = {}
    return {
        "family": family,
        "anchor_text": str(mention.get("text") or ""),
        "evidence": str(mention.get("evidence") or ""),
        "event_state": {},
        "mentions": [mention],
        "confidence": mention.get("confidence") or "medium",
        "rationale": mention.get("rationale") or "",
    }


def _stringify_mapping(mapping: Any, *, notes: list[str], prefix: str) -> dict[str, str]:
    if not isinstance(mapping, dict):
        return {}
    coerced: dict[str, str] = {}
    for key, value in mapping.items():
        if value is None:
            continue
        str_value = str(value)
        if str_value != value:
            notes.append(f"coerced_attribute_value: {prefix}.{key!s} {value!r} -> {str_value!r}")
        coerced[str(key)] = str_value
    return coerced


def flatten_events(record: StructuredExtractionRecord) -> list[MentionForEvidence]:
    mentions: list[MentionForEvidence] = []
    for event in record.clinical_events:
        for mention in event.mentions:
            mentions.append(
                MentionForEvidence(
                    entity=mention.entity,
                    text=mention.text,
                    attributes={str(k): str(v) for k, v in mention.attributes.items()},
                    evidence=event.evidence,
                    confidence=event.confidence,
                    rationale=event.rationale,
                )
            )
    return mentions


def to_predicted_letter(
    letter_id: str,
    mentions: list[MentionForEvidence],
    *,
    note_text: str,
) -> tuple[PredictedLetter, list[str]]:
    all_warnings: list[str] = []
    entity_valid: list[MentionForEvidence] = []
    for mention in mentions:
        if mention.entity not in KEY_ENTITY_NAMES:
            all_warnings.append(f"dropped_out_of_scope_entity: {mention.entity!r}")
            continue
        entity_valid.append(mention)

    evidence_valid, evidence_invalid, ev_warnings = check_evidence(
        entity_valid, note_text=note_text
    )
    all_warnings.extend(ev_warnings)

    predicted_mentions: list[PredictedMention] = []
    for mention in evidence_valid:
        spec = ENTITY_REGISTRY[mention.entity]
        attrs, projection_warnings = _strip_model_supplied_projection_attrs(
            dict(mention.attributes)
        )
        all_warnings.extend(f"{mention.entity}: {warning}" for warning in projection_warnings)
        repaired_attrs, attr_warnings = repair_attributes(attrs, spec=spec)
        all_warnings.extend(f"{mention.entity}: {warning}" for warning in attr_warnings)
        predicted_mentions.append(
            PredictedMention(
                entity=mention.entity,
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


def _strip_model_supplied_projection_attrs(
    attrs: dict[str, str],
) -> tuple[dict[str, str], list[str]]:
    stripped = dict(attrs)
    warnings: list[str] = []
    for key in ("CUI", "CUIPhrase"):
        if key in stripped:
            stripped.pop(key)
            warnings.append(f"dropped_model_supplied_projection_attribute: {key!r}")
    return stripped, warnings


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
    progress_every: int | None = None,
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
    resume: bool = False,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    program = DspyKeyEntitiesStructuredExtractor()
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
        checkpoint_jsonl_path if resume else None, key="letter_id"
    )
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

        record, parse_errors = (
            parse_structured_events_json(raw_output) if raw_output else (None, ["not_run"])
        )
        mentions = flatten_events(record) if record else []
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
            f"- Clinical events raw: {summary.get('n_events_raw', 0)}",
            f"- Mentions raw: {summary.get('n_mentions_raw', 0)}",
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
        ).concept_assertion,
        SEIZURE_FREQUENCY.name: score_frequency_state(
            gold_letters,
            pred_letters,
        ).clinical_headline,
        INVESTIGATIONS.name: score_investigations_components(
            gold_letters,
            pred_letters,
        ).clinical_headline,
    }
    return {
        "target_headline_f1": KEY_ENTITY_ITEM_F1_TARGET,
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
    target = float(scores.get("target_headline_f1", KEY_ENTITY_ITEM_F1_TARGET))
    lines = [
        "",
        "## Key Clinical-Recovery Headlines",
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
) -> None:
    summary = summarize_rows(rows)
    if jsonl_path is not None:
        write_jsonl(rows, jsonl_path)
    if report_path is not None and jsonl_path is not None:
        checkpoint_report_path = _checkpoint_report_path(report_path)
        write_report(
            rows,
            {
                "prompt_version": PROMPT_VERSION,
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
