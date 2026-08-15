"""Full-profile prompt builder for the structured-event extractor."""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.prompts.key_entities.loader import (
    load_v16_shape_examples,
)

from .constants import (
    PROMPT_VERSION_V0_9_25_LUNA_SF_BOUNDARY_DX,
    PROMPT_VERSION_V0_9_25_LUNA_SF_STATE,
    PROMPT_VERSION_V10,
    PROMPT_VERSION_V11,
    PROMPT_VERSION_V12,
    PROMPT_VERSION_V13,
    PROMPT_VERSION_V14,
    PROMPT_VERSION_V15,
    PROMPT_VERSION_V16,
    PROMPT_VERSION_V17,
    PromptProfile,
    prompt_version_for,
)
from .prompt_content import (
    _attribute_vocabulary,
    _decision_procedure,
    _event_lane_guide,
    _family_guidance,
    _worked_examples,
    candidate_evidence_ledger_for_letter,
)
from .prompt_luna_variants import (
    LUNA_SF_BOUNDARY_DX_GUIDANCE,
    LUNA_SF_STATE_GUIDANCE,
)
from .prompt_rules_full import (
    _clinical_rules,
)


def build_full_prompt_input(
    letter: ExectLetter,
    *,
    prompt_profile: PromptProfile = "full",
    prompt_version: str | None = None,
) -> str:
    """Build the comprehensive structured-event payload."""

    selected_prompt_version = prompt_version_for(
        prompt_profile,
        prompt_version=prompt_version,
    )
    if selected_prompt_version == PROMPT_VERSION_V10:
        return _build_v10_prompt_input(letter, selected_prompt_version)
    if selected_prompt_version == PROMPT_VERSION_V11:
        return _build_v11_prompt_input(letter, selected_prompt_version)
    if selected_prompt_version == PROMPT_VERSION_V12:
        return _build_v12_prompt_input(letter, selected_prompt_version)
    if selected_prompt_version == PROMPT_VERSION_V13:
        return _build_v13_prompt_input(letter, selected_prompt_version)
    if selected_prompt_version == PROMPT_VERSION_V14:
        return _build_v14_prompt_input(letter, selected_prompt_version)
    if selected_prompt_version == PROMPT_VERSION_V15:
        return _build_v15_prompt_input(letter, selected_prompt_version)
    if selected_prompt_version == PROMPT_VERSION_V16:
        return _build_v16_prompt_input(letter, selected_prompt_version)
    if selected_prompt_version == PROMPT_VERSION_V17:
        return _build_v17_prompt_input(letter)
    payload = {
        "prompt_version": selected_prompt_version,
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
                                "One of Prescription, Diagnosis, SeizureFrequency, Investigations."
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
        "clinical_rules": _clinical_rules(),
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    extra = _luna_extra_guidance(selected_prompt_version)
    if extra:
        payload["extra_clinical_guidance"] = list(extra)
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _luna_extra_guidance(prompt_version: str) -> tuple[str, ...]:
    if prompt_version == PROMPT_VERSION_V0_9_25_LUNA_SF_STATE:
        return LUNA_SF_STATE_GUIDANCE
    if prompt_version == PROMPT_VERSION_V0_9_25_LUNA_SF_BOUNDARY_DX:
        return LUNA_SF_BOUNDARY_DX_GUIDANCE
    return ()


_V10_TASK = (
    "Read the clinical letter once. Build a compact list of clinical events "
    "for medication, diagnosis, seizure frequency, and investigations. Each "
    "event may render one or more entity mentions when the same clinical fact "
    "validly belongs to more than one requested family."
)

_V10_FAMILY_GUIDANCE = {
    "medication": (
        "anti-seizure medication events; render Prescription with DrugName, "
        "DrugDose, DoseUnit, and Frequency when stated."
    ),
    "diagnosis": (
        "epilepsy, focal epilepsy, seizure disorder, or named seizure types; "
        "render DiagCategory, Certainty, and Negation when supported."
    ),
    "seizure_frequency": (
        "how often a seizure type occurs, including seizure-free duration, "
        "ranges, cluster cadence, dated counts, and frequency change."
    ),
    "investigation": (
        "EEG, MRI, CT, telemetry; render performed / result / type attributes."
    ),
}

_V10_CLINICAL_RULES = [
    (
        "Use one event per medication, diagnostic concept, seizure-rate "
        "statement, or test."
    ),
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
        "SeizureFrequency mention text is the seizure-type anchor; counts and "
        "dates live in event_state or attributes."
    ),
    (
        "Medication mention text is the drug name where possible; dose and "
        "frequency live in attributes."
    ),
    (
        "Use one investigation event per modality; performed, result, and type "
        "live in attributes."
    ),
    'If nothing requested is present, return {"clinical_events": []}.',
    "Return exactly one JSON object. Do not wrap it in markdown fences.",
]


def _build_v10_prompt_input(letter: ExectLetter, prompt_version: str) -> str:
    payload = {
        "prompt_version": prompt_version,
        "task": _V10_TASK,
        "output_schema": {
            "clinical_events": [
                {
                    "family": (
                        "medication | diagnosis | seizure_frequency | investigation"
                    ),
                    "anchor_text": (
                        "Short exact substring naming the clinical event. Use the "
                        "family guidance below."
                    ),
                    "evidence": (
                        "Exact clause or sentence copied from the letter that "
                        "supports the event and all rendered mentions."
                    ),
                    "event_state": (
                        "Source-near state for clinical reasoning, such as "
                        "medication dose/frequency, diagnostic assertion, "
                        "seizure rate, or test result. Values must be strings."
                    ),
                    "mentions": [
                        {
                            "entity": (
                                "One of Prescription, Diagnosis, "
                                "SeizureFrequency, Investigations."
                            ),
                            "text": (
                                "Short exact substring used for scoring this "
                                "entity."
                            ),
                            "attributes": "Only attributes legal for that entity.",
                        }
                    ],
                    "confidence": "low | medium | high",
                    "rationale": "One brief sentence explaining the event.",
                }
            ]
        },
        "family_guidance": dict(_V10_FAMILY_GUIDANCE),
        "attribute_vocabulary": _attribute_vocabulary(),
        "clinical_rules": list(_V10_CLINICAL_RULES),
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


_V11_TASK = (
    "Read the clinical letter once. Extract current clinical events for "
    "medication, diagnosis, seizure frequency, and investigations. Each event "
    "may render one or more entity mentions when the same fact belongs to more "
    "than one requested family."
)

_V11_FAMILY_GUIDANCE = {
    "medication": (
        "Find current anti-seizure medication statements. Render Prescription "
        "with DrugName, DrugDose, DoseUnit, and Frequency when the letter "
        "states them. Mention text is the drug name, or the short regimen "
        "span when that is all the letter gives."
    ),
    "diagnosis": (
        "Find named epileptic diagnoses and named seizure types. Render "
        "Diagnosis with DiagCategory, Certainty, and Negation. Mention text "
        "is the core concept span."
    ),
    "seizure_frequency": (
        "Find how often a seizure type occurs now, including seizure-free "
        "duration, ranges, clusters, dated counts, and frequency change. "
        "Mention text is the seizure-type anchor. Put counts and dates in "
        "attributes. Choose the named type when the count belongs to that "
        "type; otherwise use the generic seizure span."
    ),
    "investigation": (
        "Find completed EEG, MRI, CT, or telemetry statements. Render "
        "performed, result, and type attributes when the letter states them. "
        "One event per modality."
    ),
}

_V11_CLINICAL_RULES = [
    (
        "Use one event per medication, diagnostic concept, seizure-rate "
        "statement, or test."
    ),
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
        "SeizureFrequency mention text is the seizure-type anchor; counts and "
        "dates live in event_state or attributes."
    ),
    (
        "A SeizureFrequency mention must include a frequency-state attribute "
        "such as NumberOfSeizures, a lower/upper count, FrequencyChange, or a "
        "time frame."
    ),
    (
        "Medication mention text is the drug name where possible; dose and "
        "frequency live in attributes."
    ),
    (
        "Use one investigation event per modality; performed, result, and type "
        "live in attributes."
    ),
    (
        "Every rendered mention must include entity and text."
    ),
    'If nothing requested is present, return {"clinical_events": []}.',
    "Return exactly one JSON object. Do not wrap it in markdown fences.",
]


def _build_v11_prompt_input(letter: ExectLetter, prompt_version: str) -> str:
    payload = {
        "prompt_version": prompt_version,
        "task": _V11_TASK,
        "output_schema": {
            "clinical_events": [
                {
                    "family": (
                        "medication | diagnosis | seizure_frequency | investigation"
                    ),
                    "anchor_text": (
                        "Short exact substring naming the clinical event. Use the "
                        "family guidance below."
                    ),
                    "evidence": (
                        "Exact clause or sentence copied from the letter that "
                        "supports the event and all rendered mentions."
                    ),
                    "event_state": (
                        "Source-near state such as dose, diagnostic assertion, "
                        "seizure rate, or test result. Values must be strings."
                    ),
                    "mentions": [
                        {
                            "entity": (
                                "One of Prescription, Diagnosis, "
                                "SeizureFrequency, Investigations."
                            ),
                            "text": (
                                "Short exact substring used for scoring this "
                                "entity."
                            ),
                            "attributes": "Only attributes legal for that entity.",
                        }
                    ],
                    "confidence": "low | medium | high",
                    "rationale": "One brief sentence explaining the event.",
                }
            ]
        },
        "family_guidance": dict(_V11_FAMILY_GUIDANCE),
        "attribute_vocabulary": _attribute_vocabulary(),
        "clinical_rules": list(_V11_CLINICAL_RULES),
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


_V12_TASK = (
    "Read the clinical letter once. Extract current clinical events for "
    "medication, diagnosis, seizure frequency, and investigations. Each event "
    "may render one or more entity mentions when the same fact belongs to more "
    "than one requested family. Prefer current epileptic facts over plans, "
    "remote history, driving advice, and non-epilepsy drugs."
)

_V12_FAMILY_GUIDANCE = {
    "medication": (
        "Find current anti-seizure medication statements. Render Prescription "
        "with DrugName, DrugDose, DoseUnit, and Frequency when the letter "
        "states them. Mention text is the drug name, or the short regimen "
        "span when that is all the letter gives. Do not emit a planned start, "
        "a previous titration step, or a drug that is not an anti-seizure "
        "medicine."
    ),
    "diagnosis": (
        "Find named epileptic diagnoses and named seizure types. Render "
        "Diagnosis with DiagCategory, Certainty, and Negation. Mention text "
        "is the core concept span. Do not also emit a bare symptom word as a "
        "diagnosis when a named seizure type already covers that fact."
    ),
    "seizure_frequency": (
        "Find how often a seizure type occurs now, including current "
        "seizure-free duration, ranges, clusters, dated counts, and frequency "
        "change. Mention text is the seizure-type anchor. Put counts and dates "
        "in attributes. Choose the named type when the count belongs to that "
        "type; otherwise use the generic seizure span. Do not emit driving, "
        "licence, counselling, or risk language as frequency. Do not emit "
        "remote childhood or febrile history as a current rate. Do not emit a "
        "body-part or symptom word as a second rate when a named type already "
        "carries that count. If the letter also has a separate qualitative "
        "statement that seizures have returned or changed without a count, "
        "emit that companion on the generic seizure span."
    ),
    "investigation": (
        "Find completed EEG, MRI, CT, or telemetry statements. Render "
        "performed, result, and type attributes when the letter states them. "
        "One event per modality. Do not emit planned or discussed tests."
    ),
}

_V12_CLINICAL_RULES = [
    *_V11_CLINICAL_RULES,
    (
        "Emit only current epileptic frequency, current anti-seizure regimen, "
        "completed tests, and named current diagnoses."
    ),
    (
        "Do not emit driving, licence, counselling, risk, or well-controlled "
        "language as SeizureFrequency."
    ),
    (
        "Do not emit remote childhood or febrile history as a current "
        "SeizureFrequency rate."
    ),
    (
        "One SeizureFrequency rate per seizure type. Do not also emit a "
        "body-part or symptom word as a second rate when a named type already "
        "carries that count."
    ),
    (
        "If the letter has both a typed current rate and a separate "
        "qualitative statement that seizures have returned or changed without "
        "a count, also emit the qualitative companion on the generic seizure "
        "span with a change or time attribute."
    ),
    (
        "Current anti-seizure regimen only. Do not emit planned starts, "
        "if-further instructions, previous titration steps, or non-epilepsy "
        "drugs."
    ),
    (
        "Completed tests only. Do not emit planned or discussed tests."
    ),
]


def _build_v12_prompt_input(letter: ExectLetter, prompt_version: str) -> str:
    payload = {
        "prompt_version": prompt_version,
        "task": _V12_TASK,
        "output_schema": {
            "clinical_events": [
                {
                    "family": (
                        "medication | diagnosis | seizure_frequency | investigation"
                    ),
                    "anchor_text": (
                        "Short exact substring naming the clinical event. Use the "
                        "family guidance below."
                    ),
                    "evidence": (
                        "Exact clause or sentence copied from the letter that "
                        "supports the event and all rendered mentions."
                    ),
                    "event_state": (
                        "Source-near state such as dose, diagnostic assertion, "
                        "seizure rate, or test result. Values must be strings."
                    ),
                    "mentions": [
                        {
                            "entity": (
                                "One of Prescription, Diagnosis, "
                                "SeizureFrequency, Investigations."
                            ),
                            "text": (
                                "Short exact substring used for scoring this "
                                "entity."
                            ),
                            "attributes": "Only attributes legal for that entity.",
                        }
                    ],
                    "confidence": "low | medium | high",
                    "rationale": "One brief sentence explaining the event.",
                }
            ]
        },
        "family_guidance": dict(_V12_FAMILY_GUIDANCE),
        "attribute_vocabulary": _attribute_vocabulary(),
        "clinical_rules": list(_V12_CLINICAL_RULES),
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


_V13_TASK = (
    "Read the clinical letter once. Extract current epileptic diagnoses, "
    "current seizure frequency, current anti-seizure medication, and completed "
    "EEG, MRI, CT, or telemetry. Copy only exact substrings from the letter. "
    "The same fact may render more than one family when the letter states both."
)

_V13_FAMILY_GUIDANCE = dict(_V11_FAMILY_GUIDANCE)

_V13_CLINICAL_RULES = [
    *_V11_CLINICAL_RULES,
    (
        "Counts, dates, and doses belong in attributes. You may copy the "
        "letter's own words into those fields, including approximate counts. "
        "Do not leave a SeizureFrequency mention without a frequency-state "
        "attribute."
    ),
]


def _build_v13_prompt_input(letter: ExectLetter, prompt_version: str) -> str:
    payload = {
        "prompt_version": prompt_version,
        "task": _V13_TASK,
        "output_schema": {
            "clinical_events": [
                {
                    "family": (
                        "medication | diagnosis | seizure_frequency | investigation"
                    ),
                    "anchor_text": "Short exact substring naming the clinical event.",
                    "evidence": (
                        "Exact clause or sentence copied from the letter."
                    ),
                    "event_state": (
                        "Optional. Short source-near state. Scored values live "
                        "in mention attributes."
                    ),
                    "mentions": [
                        {
                            "entity": (
                                "One of Prescription, Diagnosis, "
                                "SeizureFrequency, Investigations."
                            ),
                            "text": "Short exact substring used for scoring.",
                            "attributes": "Only attributes legal for that entity.",
                        }
                    ],
                    "confidence": "Optional. low | medium | high",
                    "rationale": "Optional. One short sentence.",
                }
            ]
        },
        "family_guidance": dict(_V13_FAMILY_GUIDANCE),
        "attribute_vocabulary": _attribute_vocabulary(),
        "clinical_rules": list(_V13_CLINICAL_RULES),
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


_V14_TASK = (
    "Read the clinical letter once. Extract current epileptic diagnoses, "
    "current seizure frequency, current anti-seizure medication, and completed "
    "EEG, MRI, CT, or telemetry. Copy only exact substrings from the letter. "
    "The same fact may render more than one family when the letter states both."
)

_V14_SF_GUIDANCE = (
    "Fill every SeizureFrequency role the letter states. An empty role is "
    "allowed. current_rate: a count, range, interval, cluster, or dated count "
    "that is happening now. seizure_free: last event, none since, no further, "
    "or no seizures since a stated time; mention text is the type in that "
    "clause; set NumberOfSeizures to 0 and TimeSince_or_TimeOfEvent to Since. "
    "change_companion: returned, worse, or improved without a count; mention "
    "text is always the generic seizure span. Mention text must be an exact "
    "letter substring that is generic seizure or seizures, or a named seizure "
    "type that appears in the evidence. If the count clause contains a named "
    "type, that type is the mention. Put counts and dates in attributes."
)

_V14_FAMILY_GUIDANCE = {
    **dict(_V11_FAMILY_GUIDANCE),
    "seizure_frequency": _V14_SF_GUIDANCE,
}

_V14_CLINICAL_RULES = list(_V13_CLINICAL_RULES)


def _build_v14_prompt_input(letter: ExectLetter, prompt_version: str) -> str:
    payload = {
        "prompt_version": prompt_version,
        "task": _V14_TASK,
        "output_schema": {
            "clinical_events": [
                {
                    "family": (
                        "medication | diagnosis | seizure_frequency | investigation"
                    ),
                    "anchor_text": "Short exact substring naming the clinical event.",
                    "evidence": (
                        "Exact clause or sentence copied from the letter."
                    ),
                    "event_state": (
                        "Optional. Short source-near state. Scored values live "
                        "in mention attributes."
                    ),
                    "mentions": [
                        {
                            "entity": (
                                "One of Prescription, Diagnosis, "
                                "SeizureFrequency, Investigations."
                            ),
                            "text": "Short exact substring used for scoring.",
                            "attributes": "Only attributes legal for that entity.",
                        }
                    ],
                    "confidence": "Optional. low | medium | high",
                    "rationale": "Optional. One short sentence.",
                }
            ]
        },
        "family_guidance": dict(_V14_FAMILY_GUIDANCE),
        "attribute_vocabulary": _attribute_vocabulary(),
        "clinical_rules": list(_V14_CLINICAL_RULES),
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


_V15_TASK = (
    "Read the clinical letter once. Use candidate_spans as possible evidence; "
    "accept, reject, or encode each span. Extract current epileptic diagnoses, "
    "current seizure frequency, current anti-seizure medication, and completed "
    "EEG, MRI, CT, or telemetry. You may add a fact that is not listed if the "
    "letter states it. Copy only exact substrings from the letter. The same "
    "fact may render more than one family when the letter states both."
)

_V15_CLINICAL_RULES = [
    *_V14_CLINICAL_RULES,
    (
        "candidate_spans are possible evidence only. Do not emit a span "
        "unless the letter supports that family. You may emit a stated fact "
        "that is not listed."
    ),
]


def _v15_candidate_spans(letter: ExectLetter) -> list[dict[str, str]]:
    rows = candidate_evidence_ledger_for_letter(letter)
    return [
        {
            "family": str(row.get("family") or ""),
            "evidence": str(row.get("evidence") or ""),
            "anchor_hint": str(row.get("anchor_hint") or ""),
        }
        for row in rows
    ]


def _build_v15_prompt_input(letter: ExectLetter, prompt_version: str) -> str:
    payload = {
        "prompt_version": prompt_version,
        "task": _V15_TASK,
        "output_schema": {
            "clinical_events": [
                {
                    "family": (
                        "medication | diagnosis | seizure_frequency | investigation"
                    ),
                    "anchor_text": "Short exact substring naming the clinical event.",
                    "evidence": (
                        "Exact clause or sentence copied from the letter."
                    ),
                    "event_state": (
                        "Optional. Short source-near state. Scored values live "
                        "in mention attributes."
                    ),
                    "mentions": [
                        {
                            "entity": (
                                "One of Prescription, Diagnosis, "
                                "SeizureFrequency, Investigations."
                            ),
                            "text": "Short exact substring used for scoring.",
                            "attributes": "Only attributes legal for that entity.",
                        }
                    ],
                    "confidence": "Optional. low | medium | high",
                    "rationale": "Optional. One short sentence.",
                }
            ]
        },
        "family_guidance": dict(_V14_FAMILY_GUIDANCE),
        "attribute_vocabulary": _attribute_vocabulary(),
        "clinical_rules": list(_V15_CLINICAL_RULES),
        "candidate_spans": _v15_candidate_spans(letter),
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _build_v16_prompt_input(letter: ExectLetter, prompt_version: str) -> str:
    payload = {
        "prompt_version": prompt_version,
        "task": _V13_TASK,
        "output_schema": {
            "clinical_events": [
                {
                    "family": (
                        "medication | diagnosis | seizure_frequency | investigation"
                    ),
                    "anchor_text": "Short exact substring naming the clinical event.",
                    "evidence": (
                        "Exact clause or sentence copied from the letter."
                    ),
                    "event_state": (
                        "Optional. Short source-near state. Scored values live "
                        "in mention attributes."
                    ),
                    "mentions": [
                        {
                            "entity": (
                                "One of Prescription, Diagnosis, "
                                "SeizureFrequency, Investigations."
                            ),
                            "text": "Short exact substring used for scoring.",
                            "attributes": "Only attributes legal for that entity.",
                        }
                    ],
                    "confidence": "Optional. low | medium | high",
                    "rationale": "Optional. One short sentence.",
                }
            ]
        },
        "family_guidance": dict(_V13_FAMILY_GUIDANCE),
        "attribute_vocabulary": _attribute_vocabulary(),
        "clinical_rules": list(_V13_CLINICAL_RULES),
        "worked_examples": load_v16_shape_examples(),
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _build_v17_prompt_input(letter: ExectLetter) -> str:
    """Build v16's clinical contract without model-facing run metadata.

    Dict insertion order is the designed semantic order. Do not sort these keys:
    the task leads, supporting instructions follow, and the current letter ends
    the request after the synthetic examples.
    """

    payload = {
        "task": _V13_TASK,
        "output_schema": {
            "clinical_events": [
                {
                    "family": (
                        "medication | diagnosis | seizure_frequency | investigation"
                    ),
                    "anchor_text": "Short exact substring naming the clinical event.",
                    "evidence": "Exact clause or sentence copied from the letter.",
                    "event_state": (
                        "Optional. Short state matching the letter's wording and "
                        "context. Put answer values in mention attributes."
                    ),
                    "mentions": [
                        {
                            "entity": (
                                "One of Prescription, Diagnosis, "
                                "SeizureFrequency, Investigations."
                            ),
                            "text": "Short exact substring for this mention.",
                            "attributes": "Only attributes legal for that entity.",
                        }
                    ],
                    "confidence": "Optional. low | medium | high",
                    "rationale": "Optional. One short sentence.",
                }
            ],
            "patient_history": [
                {
                    "span": (
                        "Exact short span diverted from the Diagnosis or "
                        "SeizureFrequency answer."
                    ),
                    "kind": (
                        "unclassified_event | non_epileptic_event | febrile_event | "
                        "generic_jerk_or_absence | comorbidity"
                    ),
                }
            ],
            "medication_history": [
                {
                    "span": "Exact short span diverted from the Prescription answer.",
                    "kind": "planned_medication | past_medication",
                }
            ]
        },
        "family_guidance": dict(_V13_FAMILY_GUIDANCE),
        "attribute_vocabulary": _attribute_vocabulary(),
        "clinical_rules": list(_V13_CLINICAL_RULES),
        "worked_examples": load_v16_shape_examples(),
        "letter_text": letter.note_text,
    }
    payload["clinical_rules"] = [
        *payload["clinical_rules"],
        (
            "Use patient_history as a sink instead of Diagnosis or SeizureFrequency "
            "for unrelated events: events, episodes, collapses, blackouts, TLOC, "
            "seizure-like events; explicit NES or dissociative events; febrile events "
            "whether affirmed or denied; generic jerks or absences only when they "
            "are not a named epileptic type; and anxiety, depression, alcohol, "
            "migraine, or headache leaking into Diagnosis."
        ),
        (
            "Do not put named seizure types, seizure-free statements, numbered "
            "current rates, current anti-seizure medicines, or completed tests in "
            "patient_history. A generic seizure with a real rate and a last-event "
            "zero for a type the patient has remain SeizureFrequency facts; "
            "do not divert them."
        ),
        (
            "Use medication_history instead of Prescription for planned, requested, "
            "future, stopped, or previously tried medicines. Keep current medicines "
            "in the Prescription family."
        ),
        "Sink entries are logged only and are not clinical_events or output mentions.",
    ]
    return json.dumps(payload, ensure_ascii=False)
