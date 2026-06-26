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
import re
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict

from clinical_extraction.core.evidence import evidence_is_substring
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    standard_dictionary as sd,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.json_parse import extract_json_object
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.mention_pipeline import (
    check_evidence, raw_output_from_adapter_parse_error, repair_attributes,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    _has_blocking_parse_issue, write_jsonl,
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
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.schema_repair import (
    parse_json_payload_with_schema_repair,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.prompts.key_entities.loader import (
    load_worked_examples,
)

PROMPT_VERSION = "exectv2_hybrid_key_family_event_ledger_v0.9.24"
QWEN_COMPACT_PROMPT_VERSION = "exectv2_hybrid_key_family_event_ledger_v0.9.24_qwen_compact"
PIPELINE_FAMILY = "exectv2_hybrid_key_family_event_ledger"
COMPONENT_OWNER = "hybrid_key_family_event_ledger"

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
ALLOWED_EVENT_FAMILIES = {"medication", "diagnosis", "seizure_frequency", "investigation"}
PromptProfile = Literal["full", "qwen_compact"]

_MEDICATION_RE = re.compile(
    r"\b("
    r"lamotrigine|lamictal|levetiracetam|keppra|brivaracetam|sodium valproate|"
    r"valproate|eplim|carbamazepine|tegretol|topiramate|clobazam|clonazepam|"
    r"midazolam|lacosamide|vimpat|zonisamide|phenobarbital|phenytoin|"
    r"oxcarbazepine|gabapentin|pregabalin|perampanel|eslicarbazepine"
    r")\b",
    re.IGNORECASE,
)
_INVESTIGATION_RE = re.compile(
    r"\b(MRI|CT|EEG|VEEG|video\s+EEG|video[- ]telemetry|telemetry)\b",
    re.IGNORECASE,
)
_DIAGNOSIS_RE = re.compile(
    r"\b("
    r"epilepsy|seizure disorder|focal epilepsy|temporal lobe epilepsy|"
    r"generalised epilepsy|generalized epilepsy|JME|juvenile myoclonic epilepsy|"
    r"tonic[- ]clonic seizures?|tonic[- ]chronic seizures?|"
    r"generalised tonic[- ]clonic seizures?|generalized tonic[- ]clonic seizures?|"
    r"focal seizures?|focal to bilateral(?: convulsive)? seizures?|"
    r"absence(?:-like)? seizures?|complex partial seizures?|dyscognitive seizures?|"
    r"myoclonic seizures?"
    r")\b",
    re.IGNORECASE,
)
_SEIZURE_STATE_RE = re.compile(
    r"\b("
    r"seizures?|seizure[- ]free|last event|last seizure|no further|no more|"
    r"not had|per|every|daily|weekly|monthly|yearly|few|several|cluster|"
    r"returned|frequent|infrequent|controlled|under control|increased|decreased"
    r")\b",
    re.IGNORECASE,
)


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
            "\"confidence\": ..., \"rationale\": \"\"}, ...]}. Rationale may be "
            "an empty string; do not include analysis or first-person reasoning."
        )
    )


class DspyKeyEntitiesStructuredExtractor(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(ExECTv2KeyEntitiesStructuredSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def prompt_version_for(profile: PromptProfile = "full") -> str:
    return QWEN_COMPACT_PROMPT_VERSION if profile == "qwen_compact" else PROMPT_VERSION


def build_prompt_input(letter: ExectLetter, *, prompt_profile: PromptProfile = "full") -> str:
    """Build the single-prompt structured-event payload."""

    if prompt_profile == "qwen_compact":
        return _build_qwen_compact_prompt_input(letter)

    payload = {
        "prompt_version": prompt_version_for(prompt_profile),
        "task": (
            "Read the clinical letter once. Use the candidate_evidence_ledger as "
            "attention scaffolding, then build a compact list of source-near "
            "clinical events for medication, diagnosis, seizure frequency, and "
            "investigations. Each event may render one or more entity mentions when "
            "the same clinical fact validly belongs to more than one requested family."
        ),
        "architecture": {
            "name": "single hybrid key-family event ledger",
            "inspiration": (
                "Gan structured-events discipline: source-near candidate evidence, "
                "typed state lanes, exact evidence, then final mention renderings."
            ),
            "component_ownership": (
                "The deterministic ledger proposes possible evidence spans only. "
                "The model owns keep/reject/split/merge decisions and final rendered "
                "mentions. Deterministic code later validates evidence, strips illegal "
                "attributes, attaches finite ontology codes, and evaluates outputs."
            ),
        },
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
        "decision_procedure": _decision_procedure(),
        "candidate_evidence_ledger": candidate_evidence_ledger_for_letter(letter),
        "event_lane_guide": _event_lane_guide(),
        "family_guidance": _family_guidance(),
        "attribute_vocabulary": _attribute_vocabulary(),
        "worked_examples": _worked_examples(),
        "clinical_rules": [
            (
                "First classify each candidate_evidence_ledger item into an event "
                "lane: current_regimen, rescue_regimen, future_or_historical_medication, "
                "diagnosis_assertion, diagnosis_context_only, active_rate, "
                "seizure_free_anchor, qualitative_change, performed_investigation, "
                "planned_investigation, or reject."
            ),
            (
                "Candidate ledger rows are not predictions. Keep, reject, split, "
                "merge, or add events based only on the full letter and exact evidence."
            ),
            (
                "Return only final clinical_events. Do not return candidate IDs unless "
                "you copy them into event_state as trace strings."
            ),
            (
                "Write each rationale as one short final-justification sentence. "
                "Do not show step-by-step reasoning, self-questioning, alternative "
                "options, or quoted prompt rules inside rationale."
            ),
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
                "temporal lobe epilepsy, primary generalised epilepsy, or JME. "
                "When the letter explicitly states both a generic epilepsy diagnosis "
                "and a specific syndrome or seizure type, render both as separate "
                "Diagnosis mentions; do not collapse one into the other."
            ),
            (
                "When a Diagnosis heading or impression states an epilepsy subtype "
                "using the word epilepsy, such as 'Temporal lobe epilepsy' or "
                "'Symptomatic structural focal epilepsy', render the subtype and also "
                "render generic 'epilepsy' only when the source itself explicitly uses "
                "the word epilepsy as a diagnosis. Do not add generic epilepsy from "
                "family history, clinic names, medication labels, or weak context."
            ),
            (
                "Do not add a generic epilepsy companion to a specific epilepsy "
                "subtype unless the source separately asserts generic epilepsy as its "
                "own diagnosis or context says the patient has/has known epilepsy. "
                "For example, 'Diagnosis: symptomatic structural focal epilepsy' "
                "renders only 'symptomatic structural focal epilepsy'."
            ),
            (
                "When narrative says 'intractable epilepsy', keep the modifier in "
                "the Diagnosis text; do not shorten it to generic 'epilepsy'."
            ),
            (
                "In phrases like 'general and complex partial seizures', do not emit "
                "'general seizures'; render 'complex partial seizures' unless another "
                "explicit named generalised seizure type is present."
            ),
            (
                "Onset-history phrases such as 'epilepsy started at age 4' are not "
                "a separate Diagnosis mention when the same letter already provides "
                "the current diagnosis or named seizure types."
            ),
            (
                "For Diagnosis mention text, render only the core clinical concept "
                "span. Do not include section labels, dashes, hedging words "
                "('probable', 'possible', 'query'), qualifiers like 'single' or "
                "'alone', or surrounding explanation in the mention text; put "
                "uncertainty in Certainty instead."
            ),
            (
                "Do not render bare modifiers such as 'focal', 'generalised', "
                "'probable focal', or 'possibly generalised' as Diagnosis mentions. "
                "When such wording appears in a Diagnosis heading modifying "
                "epilepsy, render the implied concept, for example 'focal epilepsy' "
                "or 'generalised epilepsy'."
            ),
            (
                "When a Diagnosis heading combines an established epilepsy type "
                "with a probable anatomical qualifier, render two concepts with "
                "separate certainty: for example 'focal epilepsy-Probable temporal' "
                "means text 'focal epilepsy' with Certainty='5' and text "
                "'temporal lobe epilepsy' with Certainty='4'."
            ),
            (
                "When a Diagnosis heading states established epilepsy before a dash "
                "and an uncertain subtype after the dash, keep the generic epilepsy "
                "diagnosis at Certainty='5' and apply the lower certainty only to "
                "the subtype; for example 'Epilepsy - unclassified, possibly "
                "generalised' renders 'epilepsy' Certainty='5' and 'generalised "
                "epilepsy' Certainty='3'."
            ),
            (
                "For abbreviated syndromes, use the exact abbreviation as mention "
                "text when that is the source span, for example text 'JME' or 'jme' "
                "with Certainty from probable/possible context."
            ),
            (
                "Do not render vague symptoms, blackout/loss-of-consciousness "
                "descriptions, anxiety, or non-epileptic events as Diagnosis unless "
                "the same phrase is explicitly asserted as an epileptic seizure, "
                "epilepsy diagnosis, or named seizure type."
            ),
            (
                "Do not render negated resemblance statements as Diagnosis or "
                "SeizureFrequency. Phrases such as 'no events which resemble "
                "absences, myoclonus or focal seizures' are explicit absence of "
                "those events, not affirmed diagnoses or seizure-frequency states."
            ),
            (
                "Do not render isolated symptoms or aura features as Diagnosis, "
                "including myoclonic jerks, jerks, flashing lights, odd sensations, "
                "altered awareness by itself, or dizziness, unless the phrase is part "
                "of a named seizure type such as 'focal seizures with altered awareness'."
            ),
            (
                "For tonic-clonic seizure wording, preserve 'tonic clonic' or "
                "'tonic-clonic'. Never write 'tonic chronic'."
            ),
            (
                "For Diagnosis headings like 'generalised tonic clonic seizures with "
                "myoclonic jerks, possible JME', render the plural tonic-clonic "
                "seizure type as Diagnosis and render JME with lower certainty; do "
                "not render isolated 'myoclonic jerks' as a Diagnosis mention."
            ),
            (
                "For composite Diagnosis headings such as 'complex partial seizures "
                "with secondary generalised tonic clonic seizures', split the heading "
                "into separate Diagnosis mentions for the named seizure types instead "
                "of returning the whole clause as one text span."
            ),
            (
                "A problem-list or Diagnosis header is not enough by itself: still "
                "exclude anxiety, dissociative/non-epileptic events, blackouts, "
                "collapse, and loss of consciousness from the requested Diagnosis "
                "family unless the phrase is explicitly asserted as epileptic."
            ),
            (
                "For diagnosis, use DiagCategory='Epilepsy' for epilepsy syndromes or "
                "diagnoses. Use DiagCategory='SingleSeizure' for one singular named "
                "seizure event such as 'focal seizure'. Use "
                "DiagCategory='MultipleSeizures' for plural named seizure types such "
                "as 'focal seizures' or 'generalised tonic clonic seizures', and for "
                "phrases that represent multiple seizure types or recurrent seizures "
                "as a category."
            ),
            (
                "Keep plural seizure-type wording plural in Diagnosis text. Source "
                "phrases such as 'absence like seizures' or 'absence-like seizures' "
                "render as plural Diagnosis text with DiagCategory='MultipleSeizures', "
                "not singular 'absence like seizure'."
            ),
            (
                "For seizure frequency, mention text is only the seizure-type anchor; "
                "do not include counts, dates, or the words 'seizure frequency' in text. "
                "event_state and attributes carry counts, periods, dates, and changes."
            ),
            (
                "Never emit a SeizureFrequency mention with empty attributes, only "
                "Negation, or only CUI/CUIPhrase. A valid SeizureFrequency mention "
                "must include a frequency-state attribute such as NumberOfSeizures, "
                "LowerNumberOfSeizures, FrequencyChange, TimeSince_or_TimeOfEvent, "
                "PointInTime, DayDate, MonthDate, YearDate, AgeLower, or AgeUpper."
            ),
            (
                "For SeizureFrequency anchors, use the generic seizure phrase when "
                "the count refers to seizures generally; use a named seizure type only "
                "when the count explicitly belongs to that type."
            ),
            (
                "SF recall: Seizure type and frequency headings are high-value "
                "evidence. If a heading says 'seizures every 3 to 4 weeks', "
                "'several seizures since last clinic', '2 generalised tonic clonic "
                "seizures 2014', or a named seizure type plus a date, render a "
                "SeizureFrequency mention for that anchor even when the count is "
                "approximate or dated. Do not replace a heading frequency with a "
                "later vague narrative estimate unless the later statement is an "
                "explicit newer quantified correction."
            ),
            (
                "When a seizure-frequency heading names a plural seizure type "
                "followed only by a year or date, treat it as one dated occurrence "
                "of that named type unless another count is attached to that same "
                "type. For example, 'absence like seizures 2014' has "
                "NumberOfSeizures='1', YearDate='2014', and "
                "TimeSince_or_TimeOfEvent='During'."
            ),
            (
                "SF state choice: statements that seizures have returned or have "
                "been experienced since a triggering event are active seizure states, "
                "not unknown states. Use active-rate attributes when a count, cadence, "
                "date, or since-frame is present; use unknown only when the letter "
                "names current seizures but gives no count, cadence, change, or "
                "seizure-free time frame."
            ),
            (
                "For named seizure types, preserve clinically meaningful modifiers "
                "that are part of the exact phrase, including 'with altered awareness', "
                "'focal to bilateral', lobe qualifiers, convulsive, tonic clonic, "
                "absence-like, and myoclonic."
            ),
            (
                "When a named seizure-frequency row says 'focal seizures with altered "
                "awareness approximately 1 per fortnight', keep the full named anchor "
                "'focal seizures with altered awareness' rather than shortening it to "
                "'focal seizures'."
            ),
            (
                "Do not render SeizureFrequency for generic events, blackouts, "
                "collapse, anxiety attacks, or dissociative/non-epileptic events "
                "unless the same phrase is explicitly asserted as epileptic seizures."
            ),
            (
                "SF precision: reject generic spell anchors such as 'events', "
                "'episodes', 'episodes of loss of consciousness', 'minor seizures', "
                "and 'jerks' when the letter describes uncertain attacks, dizziness, "
                "loss of consciousness, shaking, or light-triggered jerks without "
                "explicitly asserting that the anchor itself is an epileptic seizure "
                "type."
            ),
            (
                "Do not render childhood febrile seizures, family-history seizures, "
                "risk discussion, or old previous-event context as current "
                "SeizureFrequency unless the sentence explicitly gives the patient's "
                "current frequency state."
            ),
            (
                "SF precision: do not render risk or counselling statements such as "
                "'risk of further seizures', 'at risk of further seizures', or "
                "'even though he has only had one seizure' as SeizureFrequency."
            ),
            (
                "SF precision: do not render non-epileptic or diagnostically vague "
                "episode descriptions as SeizureFrequency, even when they include a "
                "cadence, such as 'episodes around twice a week of an unusual thought'."
            ),
            (
                "SF precision: do not render old or contextual minor-seizure episode "
                "phrases such as 'the episodes occur 4 to 5 times a year' unless the "
                "sentence explicitly asserts a current scorable epileptic seizure type."
            ),
            (
                "Onset-history statements such as 'seizures since the age of 13' are "
                "not SeizureFrequency by themselves. Use them only as a seizure-free "
                "since-age anchor when the same sentence says the last seizures were "
                "in a past age range such as the teenage years."
            ),
            (
                "For seizure-frequency ranges, never write values like '2 to 3', "
                "'2-4', or '3 or 4' in NumberOfSeizures. Use LowerNumberOfSeizures "
                "and UpperNumberOfSeizures instead."
            ),
            (
                "For approximate count words without exact numbers, use conservative "
                "integer counts only when the letter clearly describes seizures: "
                "'couple'='2', 'few'='2', and 'several'='3'."
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
                "Phrases like 'last seizure', 'last event', or 'has had none since' "
                "mean seizure-free since that anchor for the named seizure type; do "
                "not render them as one seizure during that date or as an active "
                "current-rate statement."
            ),
            (
                "Do not infer seizure-free from phrases like 'last seizure coincided "
                "with missing medication' or 'previous seizure was a year ago' unless "
                "the source also gives a clear no-further/since frame for the same "
                "seizure type."
            ),
            (
                "For seizure-free statements, anchor text to the underlying seizure "
                "phrase when it is present in the same sentence, such as 'seizures' or "
                "'focal seizures'; otherwise use the exact seizure-free phrase."
            ),
            (
                "SF precision: do not render safety-advice, conditional, or "
                "instructional statements as SeizureFrequency. Phrases such as 'if "
                "you have a seizure', 'in the event of a seizure', 'advised what to do "
                "if seizures occur', or general SUDEP/driving advice describe guidance, "
                "not a current rate."
            ),
            (
                "SF precision: do not emit a bare seizure-free or 'well controlled' "
                "SeizureFrequency mention unless it is tied to a seizure type, a count, "
                "or a temporal anchor (since/last/date). A standalone 'seizure free' "
                "with no seizure type and no time frame is not a scorable SF state."
            ),
            (
                "Phrases such as 'remains seizure free and is now driving' or "
                "'seizures were well controlled on medication' are not enough for a "
                "SeizureFrequency mention unless they name the seizure type and give "
                "a since/date/drug-change frame."
            ),
            (
                "SF precision: do not use an anaphoric anchor such as 'these seizures', "
                "'such episodes', or 'the events' as the SeizureFrequency text. Use the "
                "specific named seizure type stated earlier in the same context, or the "
                "generic 'seizures' when the count refers to seizures in general."
            ),
            (
                "SF precision: when a sentence names two seizure types joined by 'and' "
                "with a single shared count, render the count against the seizure type "
                "it actually belongs to, not a merged 'X and Y' anchor; only split into "
                "two SF mentions if the letter gives each type its own count or state."
            ),
            (
                "SF precision: emit at most one SeizureFrequency mention per distinct "
                "rate statement. Do not emit both a generic 'seizures' mention and a "
                "named-type mention for the same single count in the same clause."
            ),
            (
                "For medication, mention text is the medication name where possible; "
                "dose and frequency belong in attributes."
            ),
            (
                "Medication decision lane: current ordinary regimens and rescue "
                "as-required regimens render Prescription mentions; previous trials, "
                "stopped drugs, future starts, titration targets, options, and "
                "if-further-seizures plans are usually rejected."
            ),
            (
                "Medication current-list split dosing: if a current regimen gives "
                "unequal time-of-day doses such as 'Epilim 300 mg mane and 600 mg "
                "nocte' or 'Lamictal 100 mg in the morning, 175 mg in the afternoon', "
                "render separate Prescription mentions with Frequency='1'. Do not "
                "mark these current scheduled doses as As_Required."
            ),
            (
                "Medication plan boundary: future starts, requested dose increases, "
                "taper targets, or if-further-seizures instructions are not current "
                "Prescription mentions unless a separate current/taking/on-medication "
                "statement supports them."
            ),
            (
                "Medication frequency completion: when the selected current regimen "
                "says 'twice a day', 'twice daily', or 'bd', include Frequency='2'; "
                "when it says once daily, mane, nocte, morning, or evening, include "
                "Frequency='1'."
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
                "ECG is not an ExECTv2 target investigation. Never map ECG to EEG, "
                "MRI, or CT, and do not emit an Investigations mention from ECG-only "
                "evidence."
            ),
            (
                "Investigation decision lane: completed historical tests and tests "
                "with results render Investigations mentions; planned/requested/repeat "
                "tests without a completed result are rejected."
            ),
            (
                "Do not render future planned, requested, repeat, or follow-up "
                "investigations as performed tests. Only render completed tests or "
                "tests with a stated result."
            ),
            (
                "Investigation pending-test cues are decisive: if the test sentence "
                "contains 'will', 'arrange', 'request', 'await'/'awaiting', "
                "'appointment', 'suggest', 'recommend', 'should update', 'chase', 'up "
                "to date', 'not yet performed/received', or 'planned', treat it as a "
                "pending test and do not emit an Investigations mention for it unless a "
                "separate completed result for the same modality is also stated."
            ),
            (
                "Never emit an Investigations mention whose only support is a pending "
                "cue with Performed='No' or an unknown result; a requested or awaited "
                "test is not a completed historical test."
            ),
            (
                "Do not render a bare modality-only investigation when the note gives "
                "no completion/result statement, and do not add a duplicate modality-only "
                "mention when a result-bearing mention for the same modality is already "
                "rendered."
            ),
            (
                "Phrases such as 'EEG did show temporal slowing', 'EEG has shown "
                "spike and wave', or 'MRI does show signal change' are completed "
                "abnormal investigation results."
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
            (
                "Every rendered mention object must include both entity and text. "
                "Do not emit projection-only companion mentions such as objects with "
                "only CUI/CUIPhrase attributes; omit CUI and CUIPhrase unless they "
                "are explicitly available in the source."
            ),
            "Do not invent CUI values. If a CUI is not explicitly available, omit it.",
            "If no requested findings are present, return {\"clinical_events\": []}.",
            "Return exactly one JSON object. No markdown code fences.",
        ],
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _build_qwen_compact_prompt_input(letter: ExectLetter) -> str:
    """Build a shorter Qwen-oriented event-frame prompt.

    The full v0.9 prompt is intentionally comprehensive, but local Qwen has
    shown diagnosis-enumeration and SF-state drift on dev25. This profile keeps
    the same output contract while reducing prompt bulk and emphasizing one
    event frame per clinically supported fact.
    """

    payload = {
        "prompt_version": prompt_version_for("qwen_compact"),
        "prompt_profile": "qwen_compact",
        "task": (
            "Read the letter once and emit source-near clinical event frames for "
            "Prescription, Diagnosis, SeizureFrequency, and Investigations. The "
            "candidate ledger is attention scaffolding only; final keep/reject/"
            "split decisions are yours."
        ),
        "output_schema": {
            "clinical_events": [
                {
                    "family": "medication | diagnosis | seizure_frequency | investigation",
                    "anchor_text": "short exact source substring",
                    "evidence": "exact source clause/sentence supporting every mention",
                    "event_state": "strings only; lane/state/count/dose/result details",
                    "mentions": [
                        {
                            "entity": (
                                "Prescription | Diagnosis | SeizureFrequency | "
                                "Investigations"
                            ),
                            "text": "short source-near scoring text",
                            "attributes": "legal attributes only; omit CUI/CUIPhrase",
                        }
                    ],
                    "confidence": "low | medium | high",
                    "rationale": "empty string or <= 8 words; no analysis",
                }
            ]
        },
        "candidate_evidence_ledger": candidate_evidence_ledger_for_letter(letter, max_items=64),
        "high_priority_evidence_ledger": high_priority_evidence_ledger_for_letter(letter),
        "event_lane_guide": _event_lane_guide(),
        "attribute_vocabulary": _attribute_vocabulary(),
        "rules": [
            (
                "Return exactly one JSON object with clinical_events; no markdown, "
                "no analysis transcript, no first-person reasoning, no quoted "
                "prompt rules."
            ),
            (
                "Set rationale to an empty string unless a short phrase is needed. "
                "Never write deliberation such as 'I will', 'let us', 'however', "
                "or alternatives inside JSON strings."
            ),
            (
                "Each event must be source-near: evidence must be copied exactly "
                "from the letter and must support all rendered mentions."
            ),
            (
                "Use high_priority_evidence_ledger rows as verified attention "
                "cues for target facts previous Qwen runs often missed. They are "
                "not predictions: check the evidence in the letter, choose the "
                "right family/state, and emit the fact only if the source supports it."
            ),
            (
                "Medication: render only current ordinary regimens and as-required "
                "rescue regimens. Reject previous/stopped drugs, allergy trials, "
                "future starts, target doses, if-further-seizures plans, and "
                "requested dose increases."
            ),
            (
                "Medication split rule: if one current medication line lists "
                "unequal daily doses such as '750mg mane, 500 mg nocte' or "
                "'100 mg in the morning, 175 mg in the afternoon', render one "
                "Prescription mention per dose with Frequency='1'. A single "
                "'800mg bd' regimen has Frequency='2'."
            ),
            (
                "Diagnosis: enumerate every explicit patient diagnosis concept in "
                "Diagnosis/problem/impression statements. If generic epilepsy and "
                "a specific type/syndrome are both stated, render both separately."
            ),
            (
                "Do not add generic epilepsy as a companion to a specific epilepsy "
                "subtype unless the letter separately asserts the patient has "
                "epilepsy. Keep modifiers in diagnoses such as 'intractable "
                "epilepsy'."
            ),
            (
                "Diagnosis certainty: Certainty='5' for stated/known/diagnosed; "
                "'4' for probable/likely; '3' for possible/query. Always include "
                "Negation='Affirmed' unless the diagnosis itself is negated."
            ),
            (
                "Diagnosis boundaries: do not render vague symptoms, bare 'events', "
                "blackouts, dissociative/non-epileptic attacks, family history, "
                "education/SUDEP advice, or negated resemblance statements. Do not "
                "render myoclonic jerks unless the phrase is an explicit named "
                "epileptic seizure diagnosis."
            ),
            (
                "Diagnosis text: do not render bare modifiers such as 'focal' or "
                "'possibly generalised'. If a Diagnosis heading says epilepsy is "
                "probable focal or possibly generalised, render 'focal epilepsy' or "
                "'generalised epilepsy' with the hedging in Certainty."
            ),
            (
                "Do not render non-epilepsy causes or contextual labels as Diagnosis, "
                "including brain tumours, nonepileptic events, and risk-counselling "
                "phrases such as convulsive seizures causing injury."
            ),
            (
                "Diagnosis categories: epilepsy syndromes/types use DiagCategory="
                "'Epilepsy'; one singular seizure event uses 'SingleSeizure'; "
                "plural named seizure types such as focal seizures or generalised "
                "tonic clonic seizures use 'MultipleSeizures'. Never write "
                "'tonic chronic'; use the source concept tonic clonic."
            ),
            (
                "If Diagnosis text ends with plural 'seizures' or names a plural "
                "seizure type, DiagCategory must be 'MultipleSeizures', not "
                "'Epilepsy'."
            ),
            (
                "For named seizure types, words such as 'without change in "
                "awareness' describe the seizure semiology, not diagnostic "
                "uncertainty. Use Certainty='5' unless the source says probable, "
                "possible, query, or similar hedging."
            ),
            (
                "SeizureFrequency: render only statements of current/historical "
                "frequency state: active count/rate, seizure-free/last-event anchor, "
                "unknown frequency, or qualitative change. Diagnosis-only mentions "
                "are not SF."
            ),
            (
                "SeizureFrequency anchor: use the specific seizure phrase named in "
                "the evidence; use generic 'seizures' only when the count/state is "
                "generic. Do not use bare 'events', 'these seizures', or a count "
                "phrase such as '2 to 3' as text."
            ),
            (
                "For SeizureFrequency active-rate mentions, text must be the "
                "seizure type or generic 'seizures', while attributes carry the "
                "count/date/cadence. Example: evidence '2 to 3 focal seizures in "
                "March' uses text='focal seizures', LowerNumberOfSeizures='2', "
                "UpperNumberOfSeizures='3', MonthDate='3'."
            ),
            (
                "Use numeric date attributes: January=1, February=2, March=3, "
                "April=4, May=5, June=6, July=7, August=8, September=9, "
                "October=10, November=11, December=12. Do not write MonthDate as "
                "a month name."
            ),
            (
                "Approximate count mapping for this benchmark surface: "
                "'several' means NumberOfSeizures='3'; 'a few' means "
                "NumberOfSeizures='2'."
            ),
            (
                "SeizureFrequency attributes: never emit an SF mention with empty "
                "attributes. Use NumberOfSeizures/TimePeriod for rates, "
                "NumberOfSeizures='0' plus Since/LastClinic/date for seizure-free "
                "or last-event statements, and Frequency='unknown' only when the "
                "letter explicitly says frequency is unknown."
            ),
            (
                "SeizureFrequency headings are high-value evidence. Keep heading "
                "counts such as 'several seizures since last clinic' unless a later "
                "statement is an explicit newer quantified correction."
            ),
            (
                "SeizureFrequency precision: reject risk/counselling statements, "
                "diagnostically vague episodes, loss-of-consciousness spells, and "
                "non-epileptic events even when they include a cadence."
            ),
            (
                "If a seizure-frequency heading names a plural seizure type followed "
                "only by a year or date, render one dated occurrence for that type: "
                "NumberOfSeizures='1', YearDate='2014', "
                "TimeSince_or_TimeOfEvent='During'."
            ),
            (
                "Investigations: render completed historical MRI/CT/EEG/telemetry "
                "or explicit no-test statements. Reject planned/requested/repeat/"
                "awaited tests unless a separate completed result is stated. Do not "
                "default plain EEG to EEG_Type='Standard'."
            ),
            (
                "Investigations attributes: do not default unrelated modalities to "
                "No. An EEG result should not include MRI_Performed='No' or "
                "CT_Performed='No'; a planned MR brain/EEG should emit no mention."
            ),
            (
                "Every rendered mention object must include both entity and text. "
                "Never emit projection-only CUI/CUIPhrase companion objects."
            ),
            (
                "Exhaustiveness pass before final JSON: reread Diagnosis, "
                "Impression, Seizure type and frequency, Current medication, "
                "and Investigations sections. Add every explicitly stated target "
                "fact as a model mention; do not rely on any later dictionary or "
                "residual repair to add missed target facts."
            ),
            (
                "Diagnosis residual concepts to emit when stated: secondary "
                "generalised seizures, generalised epilepsy, focal epilepsy, "
                "focal seizures with altered awareness, focal motor seizures, "
                "temporal/frontal/parietal/occipital lobe epilepsy or seizures, "
                "status epilepticus, drug refractory epilepsy, and nocturnal "
                "seizures. These are target diagnoses when they describe the "
                "patient, not projection companions."
            ),
            (
                "Named seizure types are usually both Diagnosis and "
                "SeizureFrequency when the same source clause names the type and "
                "gives a count/rate/date. Emit a Diagnosis mention for the seizure "
                "type with DiagCategory='MultipleSeizures', then emit the separate "
                "SeizureFrequency mention with the count/rate attributes."
            ),
            (
                "Never render anatomical qualifiers as bare modifiers: 'probable "
                "temporal' means 'temporal lobe epilepsy' or 'temporal lobe "
                "seizures' with Certainty='4'; 'focal onset' means 'focal "
                "seizures' when the seizure type is being diagnosed."
            ),
            (
                "SeizureFrequency residual facts to emit when stated: dated "
                "seizure-type headings such as '2 generalised tonic clonic "
                "seizures 2014', seizure-free clauses such as 'remains seizure "
                "free', interval rates such as 'every 3 to 4 weeks', clusters "
                "with counts, and qualitative changes such as returned/increased "
                "seizures."
            ),
            (
                "Investigation residual facts to emit when completed: MRI/CT/EEG "
                "clauses with normal or abnormal results, including terse forms "
                "such as 'MRI-normal', 'CT scan ... infarct', 'EEG ... slowing', "
                "or telemetry/video EEG results. Planned or awaited tests still "
                "emit no mention."
            ),
            (
                "Prescription residual facts to emit when current: brand names "
                "and short regimen lines such as Epilim/Episenta/Sodium Valproate, "
                "Keppra/Levetiracetam, Tegretol/Carbamazepine, Clobazam PRN or "
                "night doses, and bracketed regimen fragments like '200mg BD'."
            ),
            "Do not invent CUI values; omit CUI and CUIPhrase.",
            "If no requested findings are present, return {\"clinical_events\": []}.",
        ],
        "worked_examples": _qwen_compact_examples(),
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _qwen_compact_examples() -> list[dict[str, Any]]:
    return [
        {
            "note_fragment": "Diagnosis: focal epilepsy-Probable temporal",
            "correct_event": {
                "family": "diagnosis",
                "anchor_text": "focal epilepsy-Probable temporal",
                "evidence": "Diagnosis: focal epilepsy-Probable temporal",
                "event_state": {
                    "diagnosis": "focal epilepsy",
                    "probable_anatomical_qualifier": "temporal lobe epilepsy",
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
                        "text": "temporal lobe epilepsy",
                        "attributes": {
                            "DiagCategory": "Epilepsy",
                            "Certainty": "4",
                            "Negation": "Affirmed",
                        },
                    },
                ],
                "confidence": "high",
                "rationale": (
                    "The heading states focal epilepsy and a probable temporal "
                    "qualifier."
                ),
            },
        },
        {
            "note_fragment": "Diagnosis: epilepsy - probable focal",
            "correct_event": {
                "family": "diagnosis",
                "anchor_text": "epilepsy - probable focal",
                "evidence": "Diagnosis: epilepsy - probable focal",
                "event_state": {"lane": "diagnosis_assertion"},
                "mentions": [
                    {
                        "entity": "Diagnosis",
                        "text": "epilepsy",
                        "attributes": {
                            "DiagCategory": "Epilepsy",
                            "Certainty": "5",
                            "Negation": "Affirmed",
                        },
                    },
                    {
                        "entity": "Diagnosis",
                        "text": "focal epilepsy",
                        "attributes": {
                            "DiagCategory": "Epilepsy",
                            "Certainty": "4",
                            "Negation": "Affirmed",
                        },
                    },
                ],
                "confidence": "high",
                "rationale": "Both the generic diagnosis and probable focal type are stated.",
            },
        },
        {
            "note_fragment": "She has generalised tonic clonic seizures with myoclonic jerks.",
            "correct_event": {
                "family": "diagnosis",
                "anchor_text": "generalised tonic clonic seizures",
                "evidence": "generalised tonic clonic seizures with myoclonic jerks",
                "event_state": {"lane": "diagnosis_assertion"},
                "mentions": [
                    {
                        "entity": "Diagnosis",
                        "text": "generalised tonic clonic seizures",
                        "attributes": {
                            "DiagCategory": "MultipleSeizures",
                            "Certainty": "5",
                            "Negation": "Affirmed",
                        },
                    }
                ],
                "confidence": "high",
                "rationale": (
                    "Myoclonic jerks are contextual symptoms, not a separate "
                    "diagnosis here."
                ),
            },
        },
        {
            "note_fragment": (
                "Diagnosis: focal epilepsy-Probable temporal. In March she had 2 to 3 "
                "of her focal seizures. Since last clinic she has had four secondary "
                "generalised seizures."
            ),
            "correct_event": {
                "family": "diagnosis",
                "anchor_text": (
                    "focal epilepsy-Probable temporal; focal seizures; "
                    "secondary generalised seizures"
                ),
                "evidence": (
                    "Diagnosis: focal epilepsy-Probable temporal. In March she had 2 to 3 "
                    "of her focal seizures. Since last clinic she has had four secondary "
                    "generalised seizures."
                ),
                "event_state": {"lane": "diagnosis_and_seizure_types"},
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
                        "text": "temporal lobe epilepsy",
                        "attributes": {
                            "DiagCategory": "Epilepsy",
                            "Certainty": "4",
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
                        "entity": "Diagnosis",
                        "text": "secondary generalised seizures",
                        "attributes": {
                            "DiagCategory": "MultipleSeizures",
                            "Certainty": "5",
                            "Negation": "Affirmed",
                        },
                    },
                ],
                "confidence": "high",
                "rationale": (
                    "The diagnosis line gives focal and probable temporal epilepsy; "
                    "the frequency clauses name focal and secondary generalised "
                    "seizure types."
                ),
            },
        },
        {
            "note_fragment": "Diagnosis: symptomatic structural focal epilepsy.",
            "correct_event": {
                "family": "diagnosis",
                "anchor_text": "symptomatic structural focal epilepsy",
                "evidence": "Diagnosis: symptomatic structural focal epilepsy.",
                "event_state": {"lane": "diagnosis_assertion"},
                "mentions": [
                    {
                        "entity": "Diagnosis",
                        "text": "symptomatic structural focal epilepsy",
                        "attributes": {
                            "DiagCategory": "Epilepsy",
                            "Certainty": "5",
                            "Negation": "Affirmed",
                        },
                    }
                ],
                "confidence": "high",
                "rationale": "The heading states one specific epilepsy subtype.",
            },
        },
        {
            "note_fragment": "I reviewed this lady with intractable epilepsy in clinic today.",
            "correct_event": {
                "family": "diagnosis",
                "anchor_text": "intractable epilepsy",
                "evidence": "intractable epilepsy",
                "event_state": {"lane": "diagnosis_assertion"},
                "mentions": [
                    {
                        "entity": "Diagnosis",
                        "text": "intractable epilepsy",
                        "attributes": {
                            "DiagCategory": "Epilepsy",
                            "Certainty": "5",
                            "Negation": "Affirmed",
                        },
                    }
                ],
                "confidence": "high",
                "rationale": "The modifier is part of the stated diagnosis.",
            },
        },
        {
            "note_fragment": (
                "Despite this she continues to get general and complex partial seizures."
            ),
            "correct_event": {
                "family": "diagnosis",
                "anchor_text": "complex partial seizures",
                "evidence": "general and complex partial seizures",
                "event_state": {"lane": "diagnosis_assertion"},
                "mentions": [
                    {
                        "entity": "Diagnosis",
                        "text": "complex partial seizures",
                        "attributes": {
                            "DiagCategory": "MultipleSeizures",
                            "Certainty": "5",
                            "Negation": "Affirmed",
                        },
                    }
                ],
                "confidence": "high",
                "rationale": "General is a modifier here, not a separate seizure type.",
            },
        },
        {
            "note_fragment": "Current medication: levetiracetam 750mg mane, 500 mg nocte.",
            "correct_event": {
                "family": "medication",
                "anchor_text": "levetiracetam",
                "evidence": "levetiracetam 750mg mane, 500 mg nocte",
                "event_state": {"lane": "current_regimen"},
                "mentions": [
                    {
                        "entity": "Prescription",
                        "text": "levetiracetam 750mg mane",
                        "attributes": {
                            "DrugName": "levetiracetam",
                            "DrugDose": "750",
                            "DoseUnit": "mg",
                            "Frequency": "1",
                        },
                    },
                    {
                        "entity": "Prescription",
                        "text": "levetiracetam 500 mg nocte",
                        "attributes": {
                            "DrugName": "levetiracetam",
                            "DrugDose": "500",
                            "DoseUnit": "mg",
                            "Frequency": "1",
                        },
                    },
                ],
                "confidence": "high",
                "rationale": "The current regimen states two separate once-daily doses.",
            },
        },
        {
            "note_fragment": (
                "Seizure type and frequency: Uncertain, several seizures since the "
                "last clinic appointment."
            ),
            "correct_event": {
                "family": "seizure_frequency",
                "anchor_text": "several seizures",
                "evidence": "several seizures since the last clinic appointment",
                "event_state": {"lane": "active_rate", "frame": "LastClinic"},
                "mentions": [
                    {
                        "entity": "SeizureFrequency",
                        "text": "seizures",
                        "attributes": {
                            "NumberOfSeizures": "3",
                            "TimeSince_or_TimeOfEvent": "Since",
                            "PointInTime": "LastClinic",
                        },
                    }
                ],
                "confidence": "medium",
                "rationale": "The heading gives an approximate count since last clinic.",
            },
        },
        {
            "note_fragment": "Seizure type and frequency: absence like seizures 2014.",
            "correct_event": {
                "family": "seizure_frequency",
                "anchor_text": "absence like seizures",
                "evidence": "absence like seizures 2014",
                "event_state": {"lane": "active_rate", "date": "2014"},
                "mentions": [
                    {
                        "entity": "SeizureFrequency",
                        "text": "absence like seizures",
                        "attributes": {
                            "NumberOfSeizures": "1",
                            "YearDate": "2014",
                            "TimeSince_or_TimeOfEvent": "During",
                        },
                    }
                ],
                "confidence": "high",
                "rationale": "A plural seizure type plus year is one dated occurrence.",
            },
        },
        {
            "note_fragment": (
                "Focal to bilateral convulsive seizures, last event around Christmas 2017."
            ),
            "correct_event": {
                "family": "seizure_frequency",
                "anchor_text": "Focal to bilateral convulsive seizures",
                "evidence": (
                    "Focal to bilateral convulsive seizures, last event around Christmas 2017."
                ),
                "event_state": {"lane": "seizure_free_anchor"},
                "mentions": [
                    {
                        "entity": "SeizureFrequency",
                        "text": "Focal to bilateral convulsive seizures",
                        "attributes": {
                            "NumberOfSeizures": "0",
                            "TimeSince_or_TimeOfEvent": "Since",
                            "MonthDate": "12",
                            "YearDate": "2017",
                        },
                    }
                ],
                "confidence": "high",
                "rationale": "A last-event date means seizure-free since that event.",
            },
        },
        {
            "note_fragment": (
                "I explained that even though he has only had one seizure he is at risk "
                "of further seizures."
            ),
            "correct_event": {
                "family": "seizure_frequency",
                "anchor_text": "further seizures",
                "evidence": "at risk of further seizures",
                "event_state": {"lane": "reject", "reason": "risk_counselling"},
                "mentions": [],
                "confidence": "high",
                "rationale": "Risk counselling is not a seizure-frequency state.",
            },
        },
        {
            "note_fragment": (
                "She has been getting episodes around twice a week of an unusual thought."
            ),
            "correct_event": {
                "family": "seizure_frequency",
                "anchor_text": "episodes",
                "evidence": "episodes around twice a week of an unusual thought",
                "event_state": {"lane": "reject", "reason": "vague_episode"},
                "mentions": [],
                "confidence": "high",
                "rationale": "The cadence belongs to vague episodes, not a scorable seizure type.",
            },
        },
        {
            "note_fragment": "An EEG in 2016 did show focal slowing.",
            "correct_event": {
                "family": "investigation",
                "anchor_text": "EEG",
                "evidence": "An EEG in 2016 did show focal slowing.",
                "event_state": {"lane": "performed_investigation"},
                "mentions": [
                    {
                        "entity": "Investigations",
                        "text": "EEG",
                        "attributes": {
                            "EEG_Performed": "Yes",
                            "EEG_Results": "Abnormal",
                        },
                    }
                ],
                "confidence": "high",
                "rationale": "The EEG was completed and abnormal; no other modality is negated.",
            },
        },
        {
            "note_fragment": "We are awaiting an EEG appointment.",
            "correct_event": {
                "family": "investigation",
                "anchor_text": "EEG",
                "evidence": "awaiting an EEG appointment",
                "event_state": {"lane": "planned_investigation"},
                "mentions": [],
                "confidence": "high",
                "rationale": "An awaited EEG is pending, not completed.",
            },
        },
    ]


def high_priority_evidence_ledger_for_letter(letter: ExectLetter) -> list[dict[str, Any]]:
    """Source-bound cue rows for facts Qwen must select itself.

    The rows intentionally avoid scorer-ready attributes. They tell the model
    where high-yield evidence lives, while the model still owns the final
    keep/reject, family, text, and attribute rendering.
    """

    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()

    def add(*, family: str, evidence: str, anchor_hint: str, lane_hint: str) -> None:
        clean = " ".join(evidence.strip().split())
        if not clean or clean not in letter.note_text:
            return
        key = (family, clean.lower(), anchor_hint.lower())
        if key in seen:
            return
        seen.add(key)
        rows.append(
            {
                "priority_id": f"HP{len(rows)}",
                "family": family,
                "evidence": clean,
                "anchor_hint": anchor_hint,
                "lane_hint": lane_hint,
                "source": "source-bound-standard-dictionary-cue",
            }
        )

    for text, evidence in sd.diagnosis_residual_additions(letter.note_text):
        add(
            family="diagnosis",
            evidence=evidence,
            anchor_hint=text,
            lane_hint="diagnosis_assertion",
        )
    for text, evidence, _attrs in sd.sf_residual_additions(letter.note_text):
        add(
            family="seizure_frequency",
            evidence=evidence,
            anchor_hint=text,
            lane_hint=_seizure_frequency_lane_hint(evidence.lower()),
        )
    for text, evidence, _attrs in sd.prescription_residual_additions(letter.note_text):
        add(
            family="medication",
            evidence=evidence,
            anchor_hint=text,
            lane_hint=_medication_lane_hint(evidence.lower()),
        )
    for text, evidence, _attrs in sd.investigation_residual_additions(letter.note_text):
        add(
            family="investigation",
            evidence=evidence,
            anchor_hint=text,
            lane_hint=_investigation_lane_hint(evidence.lower()),
        )
    return rows[:32]


def candidate_evidence_ledger_for_letter(
    letter: ExectLetter,
    *,
    max_items: int = 48,
) -> list[dict[str, Any]]:
    """Build source-near candidate spans used only as prompt attention scaffolding."""

    candidates: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    def add(
        *,
        family: str,
        evidence: str,
        source: str,
        lane_hint: str,
        anchor_hint: str,
    ) -> None:
        clean = " ".join(evidence.strip().split())
        if not clean or clean not in letter.note_text:
            return
        key = (family, clean.lower())
        if key in seen:
            return
        seen.add(key)
        candidates.append(
            {
                "candidate_id": f"K{len(candidates)}",
                "family": family,
                "evidence": clean,
                "anchor_hint": anchor_hint,
                "lane_hint": lane_hint,
                "source": source,
            }
        )

    for sentence, _, _ in _sentence_spans(letter.note_text):
        lower = sentence.lower()
        if _MEDICATION_RE.search(sentence):
            add(
                family="medication",
                evidence=sentence,
                source="sentence-medication-trigger",
                lane_hint=_medication_lane_hint(lower),
                anchor_hint=_first_match_text(_MEDICATION_RE, sentence),
            )
        if _INVESTIGATION_RE.search(sentence):
            add(
                family="investigation",
                evidence=sentence,
                source="sentence-investigation-trigger",
                lane_hint=_investigation_lane_hint(lower),
                anchor_hint=_first_match_text(_INVESTIGATION_RE, sentence),
            )
        if _DIAGNOSIS_RE.search(sentence):
            add(
                family="diagnosis",
                evidence=sentence,
                source="sentence-diagnosis-trigger",
                lane_hint=_diagnosis_lane_hint(lower),
                anchor_hint=_first_match_text(_DIAGNOSIS_RE, sentence),
            )
        if _SEIZURE_STATE_RE.search(sentence) and re.search(r"\bseizure", lower):
            add(
                family="seizure_frequency",
                evidence=sentence,
                source="sentence-seizure-state-trigger",
                lane_hint=_seizure_frequency_lane_hint(lower),
                anchor_hint=_seizure_anchor_hint(sentence),
            )

    return candidates[:max_items]


def _decision_procedure() -> list[str]:
    return [
        (
            "Scan the letter globally for the four key families; do not stop at "
            "section headers."
        ),
        (
            "Use candidate_evidence_ledger rows as likely evidence anchors, but "
            "do not emit a row unless the full sentence supports a requested family."
        ),
        (
            "For each candidate, choose a lane, then keep/reject/split/merge. "
            "Write the lane decision into event_state when it helps transparency."
        ),
        (
            "Render final mentions only after the source-near event state "
            "is clear. Counts, dates, result status, dose, and certainty belong in "
            "attributes, not in improvised text."
        ),
        (
            "Before returning JSON, remove duplicates and remove events whose "
            "evidence or mention text is not an exact source substring."
        ),
    ]


def _event_lane_guide() -> dict[str, list[str]]:
    return {
        "medication": [
            "current_regimen: current/taking/on medication with dose or frequency",
            "rescue_regimen: as required, if necessary, or for clusters",
            "future_or_historical_medication: start/introduce/increase/previous/stopped/trial",
            "reject: non-anti-seizure medication or unsupported plan",
        ],
        "diagnosis": [
            "diagnosis_assertion: patient-level epilepsy syndrome or named seizure type",
            "diagnosis_context_only: discussion, family history, risk, SUDEP, or education",
            "symptom_or_nonepileptic: blackout, collapse, anxiety, dissociative event, aura only",
            "reject: no explicit epileptic diagnosis or named epileptic seizure type",
        ],
        "seizure_frequency": [
            "active_rate: count/rate/current cadence for generic or named seizures",
            "seizure_free_anchor: no further seizures, seizure-free, last seizure/event date",
            "qualitative_change: frequent/infrequent/increased/decreased/returned/controlled",
            "reject: diagnosis-only, family history, unlabelled events, historical best period",
        ],
        "investigation": [
            "performed_investigation: completed MRI/CT/EEG/telemetry, especially with result",
            "not_performed: never had/no MRI/no EEG/no CT",
            "planned_investigation: arrange/request/repeat/future/follow-up",
            "reject: bare modality without performed/result/not-performed status",
        ],
    }


def _sentence_spans(text: str) -> list[tuple[str, int, int]]:
    spans: list[tuple[str, int, int]] = []
    for match in re.finditer(r"[^.!?\n\r]+(?:[.!?]+|$)", text):
        start, end = match.span()
        raw = match.group(0)
        leading = len(raw) - len(raw.lstrip())
        trailing = len(raw.rstrip())
        clean = raw.strip()
        if clean:
            spans.append((clean, start + leading, start + trailing))
    return spans


def _first_match_text(pattern: re.Pattern[str], text: str) -> str:
    match = pattern.search(text)
    return match.group(0) if match else ""


def _medication_lane_hint(lower: str) -> str:
    if re.search(r"\b(previous|previously|stopped|withdrawn|trial|allergic)\b", lower):
        return "future_or_historical_medication"
    if re.search(r"\b(start|commence|introduce|increase|target|plan|consider|if further)\b", lower):
        return "future_or_historical_medication"
    if re.search(r"\b(as required|prn|if necessary|rescue|clusters?)\b", lower):
        return "rescue_regimen"
    return "current_regimen"


def _investigation_lane_hint(lower: str) -> str:
    if re.search(r"\b(arrange|request|repeat|plan|organise|follow[- ]up|will have)\b", lower):
        return "planned_investigation"
    if re.search(r"\b(no|never had|not had|not performed)\b", lower):
        return "not_performed"
    if re.search(
        r"\b(normal|abnormal|show|showed|shown|shows|demonstrated|revealed|captured|done|had)\b",
        lower,
    ):
        return "performed_investigation"
    return "reject"


def _diagnosis_lane_hint(lower: str) -> str:
    if re.search(
        r"\b(family history|discussion|risk|sudep|education|brother|mother|father)\b",
        lower,
    ):
        return "diagnosis_context_only"
    if re.search(
        r"\b("
        r"not had any events|no events|no history|without seizures|"
        r"blackout|collapse|anxiety|dissociative|non[- ]epileptic|aura"
        r")\b",
        lower,
    ):
        return "symptom_or_nonepileptic"
    return "diagnosis_assertion"


def _seizure_frequency_lane_hint(lower: str) -> str:
    if re.search(
        r"\b(febrile seizures|family history|risk of seizures|previous event)\b",
        lower,
    ):
        return "reject"
    if re.search(
        r"\b(not had any events|no events which resemble|no history of seizures)\b",
        lower,
    ):
        return "reject"
    if re.search(
        r"\b(seizure[- ]free|no further|no more|not had|last seizure|last event)\b",
        lower,
    ):
        return "seizure_free_anchor"
    if re.search(
        r"\b(returned|frequent|infrequent|controlled|under control|increased|decreased)\b",
        lower,
    ):
        return "qualitative_change"
    if re.search(
        r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten|few|several|per|every|cluster)\b",
        lower,
    ):
        return "active_rate"
    return "reject"


def _seizure_anchor_hint(text: str) -> str:
    ordered = [
        r"focal\s+to\s+bilateral\s+convulsive\s+seizures?",
        r"generalised\s+tonic[- ](?:clonic|chronic)\s+seizures?",
        r"generalized\s+tonic[- ](?:clonic|chronic)\s+seizures?",
        r"tonic[- ](?:clonic|chronic)\s+seizures?",
        r"complex\s+partial\s+seizures?",
        r"dyscognitive\s+seizures?",
        r"absence[- ]like\s+seizures?",
        r"absence\s+seizures?",
        r"focal\s+seizures?",
        r"cluster\s+of\s+seizures",
        r"seizure[- ]free",
        r"seizures?",
    ]
    for pattern in ordered:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return "seizures"


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
            "explicitly asserted as epileptic diagnoses, even when they appear in a "
            "Diagnosis/problem-list section. Mention text should be the clean core "
            "concept span; hedging belongs in Certainty."
        ),
        "seizure_frequency": (
            "How often a seizure type occurs, including seizure-free duration, "
            "ranges, interval cadence, cluster counts, dated counts, and frequency "
            "change. Preserve the stated seizure anchor and temporal frame instead "
            "of converting it into a guessed rate; exclude non-epileptic events and "
            "blackouts unless the letter states they are epileptic seizures."
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
    return load_worked_examples()


def parse_structured_events_json(
    raw_output: str,
) -> tuple[StructuredExtractionRecord | None, list[str]]:
    extracted = extract_json_object(raw_output)
    try:
        payload, dialect_notes = parse_json_payload_with_schema_repair(
            extracted
        )
    except json.JSONDecodeError as exc:
        repaired_raw, rationale_notes = _strip_non_scored_rationale_fields(extracted)
        if not rationale_notes:
            return None, [f"invalid_json: {exc.msg}"]
        try:
            payload, dialect_notes = parse_json_payload_with_schema_repair(repaired_raw)
        except json.JSONDecodeError:
            return None, [f"invalid_json: {exc.msg}"]
        dialect_notes = [*dialect_notes, *rationale_notes]

    payload, coerce_notes = _coerce_structured_payload(payload)
    try:
        record = StructuredExtractionRecord.model_validate(payload)
    except Exception as exc:
        return None, [f"schema_validation_error: {exc}"]
    return record, [*dialect_notes, *coerce_notes]


def _strip_non_scored_rationale_fields(raw_payload: str) -> tuple[str, list[str]]:
    """Blank malformed free-text rationale values without touching scored fields."""

    repaired, count = re.subn(
        r'"rationale"\s*:\s*"(?:\\.|[^"\\])*?(?=\r?\n\s*[}\]])',
        '"rationale": ""',
        raw_payload,
        flags=re.DOTALL,
    )
    if count == 0:
        return raw_payload, []
    return repaired, ["json_dialect_repaired: stripped_non_scored_rationale"]


def _coerce_structured_payload(payload: Any) -> tuple[Any, list[str]]:
    """Coerce event and mention state values to strings and preserve diagnostics."""

    notes: list[str] = []
    if isinstance(payload, (list, tuple)):
        notes.append("coerced_top_level_event_array")
        payload = {"clinical_events": list(payload)}
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
        family = str(event.get("family", ""))
        mentions = event.get("mentions")
        if family == "reject" and (not isinstance(mentions, list) or not mentions):
            notes.append(f"dropped_no_mention_reject_event: event[{event_index}]")
            continue
        if family not in ALLOWED_EVENT_FAMILIES:
            notes.append(f"dropped_unknown_event_family: event[{event_index}] family={family!r}")
            continue
        event["event_state"] = _stringify_mapping(
            event.get("event_state") or {},
            notes=notes,
            prefix=f"event[{event_index}].event_state",
        )
        if isinstance(mentions, list):
            coerced_mentions: list[Any] = []
            for mention_index, mention in enumerate(mentions):
                if not isinstance(mention, dict):
                    notes.append(
                        "dropped_malformed_mention: "
                        f"event[{event_index}].mentions[{mention_index}] not_object"
                    )
                    continue
                mention = dict(mention)
                missing = [
                    key
                    for key in ("entity", "text")
                    if not str(mention.get(key) or "").strip()
                ]
                if missing:
                    notes.append(
                        "dropped_malformed_mention: "
                        f"event[{event_index}].mentions[{mention_index}] "
                        f"missing={','.join(missing)}"
                    )
                    continue
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
    prompt_version: str = PROMPT_VERSION,
    component_owner: str = COMPONENT_OWNER,
    pipeline_family: str = PIPELINE_FAMILY,
) -> tuple[PredictedLetter, list[str]]:
    all_warnings: list[str] = []
    entity_valid: list[MentionForEvidence] = []
    for mention in mentions:
        if mention.entity not in KEY_ENTITY_NAMES:
            all_warnings.append(f"dropped_out_of_scope_entity: {mention.entity!r}")
            continue
        repaired = _repair_evidence_from_mention_text(mention, note_text, all_warnings)
        entity_valid.append(repaired)

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
                component_owner=component_owner,
            )
        )

    predicted_mentions = _apply_render_safety_gates(predicted_mentions, all_warnings)

    return (
        project_cuis(
            PredictedLetter(
                letter_id=letter_id,
                mentions=tuple(predicted_mentions),
                diagnostics={
                    "prompt_version": prompt_version,
                    "pipeline_family": pipeline_family,
                    "n_evidence_invalid": len(evidence_invalid),
                    "attribute_warnings": all_warnings,
                },
            )
        ),
        all_warnings,
    )


def _repair_evidence_from_mention_text(
    mention: MentionForEvidence,
    note_text: str,
    warnings: list[str],
) -> MentionForEvidence:
    """Use exact model-selected mention text as evidence for source-near entities."""

    if mention.evidence and evidence_is_substring(note_text, mention.evidence):
        return mention
    if (
        mention.entity in {PRESCRIPTION.name, DIAGNOSIS.name}
        and mention.text
        and evidence_is_substring(note_text, mention.text)
    ):
        warnings.append(f"repaired_evidence_from_mention_text: text={mention.text!r}")
        return mention.model_copy(update={"evidence": mention.text})
    return mention


_SF_STATE_ATTRS = {
    "NumberOfSeizures",
    "LowerNumberOfSeizures",
    "UpperNumberOfSeizures",
    "NumberOfTimePeriods",
    "LowerNumberOfTimePeriods",
    "UpperNumberOfTimePeriods",
    "TimePeriod",
    "TimeSince_or_TimeOfEvent",
    "FrequencyChange",
    "PointInTime",
    "DayDate",
    "MonthDate",
    "YearDate",
    "AgeLower",
    "AgeUpper",
    "AgeUnit",
}


def _apply_render_safety_gates(
    mentions: list[PredictedMention],
    warnings: list[str],
) -> list[PredictedMention]:
    gated: list[PredictedMention] = []
    for mention in mentions:
        if mention.entity == SEIZURE_FREQUENCY.name and not _has_sf_state(mention):
            warnings.append(
                "SeizureFrequency: dropped_no_frequency_state_rendering: "
                f"{mention.text!r}"
            )
            continue
        gated.append(mention)
    return _drop_duplicate_modality_only_investigations(gated, warnings)


def _has_sf_state(mention: PredictedMention) -> bool:
    return any(
        key in _SF_STATE_ATTRS and str(value).strip()
        for key, value in mention.attributes.items()
    )


def _drop_duplicate_modality_only_investigations(
    mentions: list[PredictedMention],
    warnings: list[str],
) -> list[PredictedMention]:
    result_bearing_modalities = {
        modality
        for mention in mentions
        if mention.entity == INVESTIGATIONS.name
        for modality in _investigation_modalities(mention)
        if _has_investigation_result(mention, modality)
    }
    if not result_bearing_modalities:
        return mentions

    kept: list[PredictedMention] = []
    for mention in mentions:
        modalities = _investigation_modalities(mention)
        if (
            mention.entity == INVESTIGATIONS.name
            and modalities
            and not any(_has_investigation_result(mention, modality) for modality in modalities)
            and any(modality in result_bearing_modalities for modality in modalities)
        ):
            warnings.append(
                "Investigations: dropped_duplicate_modality_only_rendering: "
                f"{mention.text!r}"
            )
            continue
        kept.append(mention)
    return kept


def _investigation_modalities(mention: PredictedMention) -> set[str]:
    modalities: set[str] = set()
    for key in mention.attributes:
        for modality in ("MRI", "CT", "EEG"):
            if key.startswith(f"{modality}_"):
                modalities.add(modality)
    return modalities


def _has_investigation_result(mention: PredictedMention, modality: str) -> bool:
    return bool(str(mention.attributes.get(f"{modality}_Results", "")).strip())


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
    prompt_profile: PromptProfile = "full",
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
    prompt_version = prompt_version_for(prompt_profile)

    for letter in todo:
        prompt_input_json = build_prompt_input(letter, prompt_profile=prompt_profile)
        raw_output = ""
        call_error: str | None = None
        adapter_repair_notes: list[str] = []
        if mode == "live":
            try:
                prediction = program(prompt_input_json=prompt_input_json)
                raw_output = str(prediction.extraction_json)
            except Exception as exc:  # pragma: no cover
                call_error = f"{type(exc).__name__}: {exc}"
                recovered = raw_output_from_adapter_parse_error(call_error)
                if recovered:
                    raw_output = recovered
                    call_error = None
                    adapter_repair_notes.append(
                        "adapter_output_field_repaired: extraction_json_missing"
                    )

        record, parse_errors = (
            parse_structured_events_json(raw_output) if raw_output else (None, ["not_run"])
        )
        parse_errors = [*adapter_repair_notes, *parse_errors]
        mentions = flatten_events(record) if record else []
        predicted_letter, gate_warnings = to_predicted_letter(
            letter.letter_id,
            mentions,
            note_text=letter.note_text,
            prompt_version=prompt_version,
        )

        rows.append(
            {
                "letter_id": letter.letter_id,
                "split": split,
                "prompt_version": prompt_version,
                "prompt_profile": prompt_profile,
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
                prompt_version=prompt_version,
                prompt_profile=prompt_profile,
            )

    rows = merge_rows(rows, order, key="letter_id")
    metadata = {
        "prompt_version": prompt_version,
        "prompt_profile": prompt_profile,
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
        ).concept_negation,
        SEIZURE_FREQUENCY.name: score_frequency_state(
            gold_letters,
            pred_letters,
        ).clinical_headline,
        INVESTIGATIONS.name: score_investigations_components(
            gold_letters,
            pred_letters,
        ).clinical_headline,
    }
    precision_tp = sum(
        int(getattr(score, "precision_tp", getattr(score, "tp", 0)))
        for score in scores.values()
    )
    recall_tp = sum(
        int(getattr(score, "recall_tp", getattr(score, "tp", 0)))
        for score in scores.values()
    )
    pred_count = sum(
        int(getattr(score, "pred_count", getattr(score, "tp", 0) + getattr(score, "fp", 0)))
        for score in scores.values()
    )
    gold_count = sum(
        int(getattr(score, "gold_count", getattr(score, "tp", 0) + getattr(score, "fn", 0)))
        for score in scores.values()
    )
    precision = precision_tp / pred_count if pred_count else 0.0
    recall = recall_tp / gold_count if gold_count else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "target_headline_f1": KEY_ENTITY_ITEM_F1_TARGET,
        "overall": {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "tp": recall_tp,
            "fp": max(0, pred_count - precision_tp),
            "fn": max(0, gold_count - recall_tp),
        },
        "diagnosis_component": "concept_negation",
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
    overall = scores.get("overall", {})
    target = float(scores.get("target_headline_f1", KEY_ENTITY_ITEM_F1_TARGET))
    lines = [
        "",
        "## Key Clinical-Recovery Headlines",
        "",
        (
            f"- Canonical overall (`clinical_headline`, Diagnosis="
            f"`{scores.get('diagnosis_component', 'concept_negation')}`): "
            f"F1={overall.get('f1', 0):.3f} "
            f"P={overall.get('precision', 0):.3f} "
            f"R={overall.get('recall', 0):.3f}"
        ),
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
    prompt_version: str = PROMPT_VERSION,
    prompt_profile: PromptProfile = "full",
) -> None:
    summary = summarize_rows(rows)
    if jsonl_path is not None:
        write_jsonl(rows, jsonl_path)
    if report_path is not None and jsonl_path is not None:
        checkpoint_report_path = _checkpoint_report_path(report_path)
        write_report(
            rows,
            {
                "prompt_version": prompt_version,
                "prompt_profile": prompt_profile,
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
