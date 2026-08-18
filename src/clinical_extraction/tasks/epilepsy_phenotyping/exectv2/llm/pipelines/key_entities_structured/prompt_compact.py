"""Compact structured prompt.

Ordinary-language one-call request. No examples. No research metadata.

Hybrid Compact (``exectv2_compact_ledger`` / ``exect_llm_with_rules``) adds
suggested evidence and category lanes. LLM-only (``exect_llm_only``) uses the
same schema, rules, and vocabulary without that scan.

All model-facing Compact text lives here.
"""

from __future__ import annotations

import json
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter

from .prompt_content import candidate_evidence_ledger_for_letter

COMPACT_AUTHORED_KEYS = (
    "task",
    "output_schema",
    "decision_procedure",
    "family_guidance",
    "attribute_vocabulary",
    "categories",
    "clinical_rules",
    "suggested_evidence",
    "letter_text",
)
LLM_ONLY_AUTHORED_KEYS = (
    "task",
    "output_schema",
    "decision_procedure",
    "family_guidance",
    "attribute_vocabulary",
    "clinical_rules",
    "letter_text",
)

_HYBRID_TASK = (
    "Read the clinical letter once. Use the suggested evidence as a starting "
    "point, then list the medication, diagnosis, seizure-frequency, and "
    "investigation facts the letter states. If one fact belongs to more than "
    "one of those families, include each valid family separately."
)

_LLM_ONLY_TASK = (
    "Read the clinical letter once. List the medication, diagnosis, "
    "seizure-frequency, and investigation facts the letter states. If one "
    "fact belongs to more than one of those families, include each valid "
    "family separately."
)

_SHARED_DECISION_SCAN = (
    "Scan the whole letter for medication, diagnosis, seizure frequency, "
    "and investigations. Do not stop at section headers."
)
_SHARED_DECISION_WRITE = (
    "Write the listed items only after the state is clear from the letter. "
    "Counts, dates, result status, and dose belong in attributes, not in "
    "made-up wording."
)
_SHARED_DECISION_EXACT = (
    "Before returning JSON, remove duplicates and remove events whose "
    "evidence or fact is not an exact copy from the letter."
)

_HYBRID_DECISION_PROCEDURE = [
    _SHARED_DECISION_SCAN,
    (
        "Treat suggested-evidence rows as likely supporting sentences, but do "
        "not include a fact unless the full sentence supports that family."
    ),
    "For each suggested row, choose a category, then keep, reject, split, or merge.",
    _SHARED_DECISION_WRITE,
    _SHARED_DECISION_EXACT,
]

_LLM_ONLY_DECISION_PROCEDURE = [
    _SHARED_DECISION_SCAN,
    _SHARED_DECISION_WRITE,
    _SHARED_DECISION_EXACT,
]

_FAMILY_GUIDANCE = {
    "medication": (
        "Anti-seizure medicines. Include DrugName, DrugDose, DoseUnit, and "
        "Frequency when stated. Copy the medication wording from the letter: "
        "the full short regimen when it appears in a list, or the drug name "
        "alone when that is all the note states."
    ),
    "diagnosis": (
        "Diagnoses such as epilepsy, focal epilepsy, seizure disorder, or "
        "named seizure types. Include DiagCategory. Do not include vague "
        "symptoms or non-epileptic alternatives unless the letter states they "
        "are epileptic diagnoses, even when they appear under a diagnosis or "
        "problem-list heading."
    ),
    "seizure_frequency": (
        "How often a seizure type occurs, including seizure-free duration, "
        "ranges, interval rates, cluster counts, dated counts, and frequency "
        "change. Keep the stated seizure words and time period; do not turn "
        "them into a guessed rate. Exclude non-epileptic events and blackouts "
        "unless the letter states they are epileptic seizures."
    ),
    "investigation": (
        "EEG, MRI, and CT statements. Include EEG_Performed, EEG_Results, "
        "MRI_Performed, MRI_Results, CT_Performed, and CT_Results only for "
        "completed tests or tests with a result, not planned repeats or a "
        "test name with no result."
    ),
}

_OUTPUT_SCHEMA = {
    "clinical_events": [
        {
            "family": "medication | diagnosis | seizure_frequency | investigation",
            "evidence": "Exact clause or sentence copied from the letter.",
            "fact": "Short exact copy from the letter that names the fact.",
            "attributes": "Only attributes allowed for that family.",
        }
    ]
}

_ATTRIBUTE_VOCABULARY: dict[str, dict[str, Any]] = {
    "medication": {
        "DoseUnit": ["g", "mg"],
        "DrugDose": "string copied from the letter.",
        "DrugName": "string copied from the letter.",
        "Frequency": ["1", "2", "3", "As_Required"],
    },
    "diagnosis": {
        "DiagCategory": [
            "Epilepsy",
            "MultipleSeizures",
            "SingleSeizure"
        ],
    },
    "seizure_frequency": {
        "AgeLower": "string copied from the letter.",
        "AgeUnit": ["Month", "Year"],
        "AgeUpper": "string copied from the letter.",
        "DayDate": "string copied from the letter.",
        "FrequencyChange": [
            "Decreased",
            "Frequent",
            "Increased",
            "Infrequent",
            "Same",
        ],
        "LowerNumberOfSeizures": "string copied from the letter.",
        "LowerNumberOfTimePeriods": "string copied from the letter.",
        "MonthDate": "string copied from the letter.",
        "NumberOfSeizures": "string copied from the letter.",
        "NumberOfTimePeriods": "string copied from the letter.",
        "PointInTime": [
            "Birthday",
            "DrugChange",
            "LastClinic",
            "Last_Month",
            "Last_Week",
            "Last_Year",
            "Surgery",
        ],
        "TimePeriod": ["Day", "Month", "Week", "Year"],
        "TimeSince_or_TimeOfEvent": ["During", "Since"],
        "UpperNumberOfSeizures": "string copied from the letter.",
        "UpperNumberOfTimePeriods": "string copied from the letter.",
        "YearDate": "string copied from the letter.",
    },
    "investigation": {
        "CT_Performed": ["No", "Yes"],
        "CT_Results": ["Abnormal", "Normal", "Unknown"],
        "EEG_Performed": ["No", "Yes"],
        "EEG_Results": ["Abnormal", "Normal", "Unknown"],
        "MRI_Performed": ["No", "Yes"],
        "MRI_Results": ["Abnormal", "Normal", "Unknown"],
    },
}

_CATEGORIES = {
    "medication": [
        "current_regimen: current/taking/on medication with dose or frequency",
        "rescue_regimen: as required, if necessary, or for clusters",
        "future_or_historical_medication: start/introduce/increase/previous/stopped/trial",
        "reject: non-anti-seizure medication or unsupported plan",
    ],
    "diagnosis": [
        "diagnosis_assertion: this patient's epilepsy syndrome or named seizure type",
        "diagnosis_context_only: discussion, family history, risk, SUDEP, or education",
        "symptom_or_nonepileptic: blackout, collapse, anxiety, dissociative event, aura only",
        "reject: no explicit epileptic diagnosis or named epileptic seizure type",
    ],
    "seizure_frequency": [
        "active_rate: count or rate for generic or named seizures",
        "seizure_free_anchor: no further seizures, seizure-free, last seizure/event date",
        "qualitative_change: frequent/infrequent/increased/decreased/returned/controlled",
        "reject: diagnosis-only, family history, unnamed events, or an old best period",
    ],
    "investigation": [
        "performed_investigation: completed MRI/CT/EEG/telemetry, especially with result",
        "planned_investigation: arrange/request/repeat/future/follow-up",
        "reject: a test name with no completed or result status",
    ],
}

_HYBRID_RULES = [
    (
        "First classify each suggested-evidence row into a category: "
        "current_regimen, rescue_regimen, future_or_historical_medication, "
        "diagnosis_assertion, diagnosis_context_only, active_rate, "
        "seizure_free_anchor, qualitative_change, performed_investigation, "
        "planned_investigation, or reject."
    ),
    (
        "Suggested-evidence rows are only hints. Keep, reject, split, merge, "
        "or add events based only on the full letter and exact evidence."
    ),
]

_SHARED_RULE_SECTIONS: dict[str, list[str]] = {
    "shared": [
        "Use one event per medication, diagnostic concept, seizure-rate statement, or test.",
        (
            "Do not include negated resemblance statements as diagnosis or "
            "seizure frequency. Phrases such as 'no events which resemble "
            "absences, myoclonus or focal seizures' are explicit absence of "
            "those events, not affirmed diagnoses or seizure-frequency states."
        ),
        (
            "For named seizure types, preserve clinically meaningful modifiers "
            "that are part of the exact phrase, including 'with altered awareness', "
            "'focal to bilateral', lobe qualifiers, convulsive, tonic clonic, "
            "absence-like, and myoclonic."
        ),
    ],
    "diagnosis": [
    (
        "For diagnosis, split compound seizure clauses into separate diagnoses "
        "when the letter names more than one seizure type."
    ),
    (
        "Prefer the most specific epilepsy syndrome or seizure type stated in "
        "the letter, such as focal epilepsy, temporal lobe epilepsy, primary "
        "generalised epilepsy, or JME. When the letter explicitly states both "
        "a generic epilepsy diagnosis and a specific syndrome or seizure type, "
        "include both as separate diagnosis events; do not collapse one into "
        "the other."
    ),
    (
        "Do not add a separate generic epilepsy diagnosis to a specific "
        "epilepsy subtype unless the letter separately states generic epilepsy "
        "as its own diagnosis or context says the patient has/has known "
        "epilepsy. For example, 'Diagnosis: symptomatic structural focal "
        "epilepsy' includes only 'symptomatic structural focal epilepsy'."
    ),
    (
        "Onset-history phrases such as 'epilepsy started at age 4' are not "
        "a separate diagnosis event when the same letter already provides "
        "the current diagnosis or named seizure types."
    ),
    (
        "For abbreviated syndromes, use the exact abbreviation as fact when "
        "that is the wording in the letter, for example 'JME' or 'jme'."
    ),
    (
        "Do not include vague symptoms, blackout/loss-of-consciousness "
        "descriptions, anxiety, or non-epileptic events as diagnosis unless "
        "the same phrase is explicitly asserted as an epileptic seizure, "
        "epilepsy diagnosis, or named seizure type."
    ),
    (
        "Do not include isolated symptoms or aura features as diagnosis, "
        "including myoclonic jerks, jerks, flashing lights, odd sensations, "
        "altered awareness by itself, or dizziness, unless the phrase is part "
        "of a named seizure type such as 'focal seizures with altered awareness'."
    ),
    (
        "For tonic-clonic seizure wording, preserve 'tonic clonic' or "
        "'tonic-clonic'. Never write 'tonic chronic'."
    ),
    (
        "A problem-list or diagnosis header is not enough by itself: still "
        "exclude anxiety, dissociative/non-epileptic events, blackouts, "
        "collapse, and loss of consciousness from diagnosis unless the phrase "
        "is explicitly asserted as epileptic."
    ),
    ],
    "seizure_frequency": [
    (
        "For seizure frequency, fact is only the seizure-type wording; do "
        "not include counts, dates, or the words 'seizure frequency' in fact. "
        "Attributes carry counts, periods, dates, and changes."
    ),
    (
        "Never include a seizure-frequency event with empty attributes. A "
        "valid event must include NumberOfSeizures, LowerNumberOfSeizures, "
        "FrequencyChange, TimeSince_or_TimeOfEvent, PointInTime, DayDate, "
        "MonthDate, YearDate, AgeLower, or AgeUpper."
    ),
    (
        "For seizure-frequency wording, use the generic seizure phrase when "
        "the count refers to seizures generally; use a named seizure type only "
        "when the count explicitly belongs to that type."
    ),
    (
        "Seizure type and frequency headings often state the frequency. If a "
        "heading says 'seizures every 3 to 4 weeks', 'several seizures since "
        "last clinic', '2 generalised tonic clonic seizures 2014', or a named "
        "seizure type plus a date, include a seizure-frequency event for those "
        "seizure words even when the count is approximate or dated. Do not "
        "replace a heading frequency with a later vague narrative estimate "
        "unless the later statement is an explicit newer quantified correction."
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
        "Statements that seizures have returned or have been experienced "
        "since a triggering event are active seizure states. Use active-rate "
        "attributes when a count, cadence, date, or since period is present. "
        "If the letter names current seizures but gives no count, cadence, "
        "change, or seizure-free time frame, do not invent a rate."
    ),
    (
        "When a named seizure-frequency statement says 'focal seizures with "
        "altered awareness approximately 1 per fortnight', keep the full named "
        "wording 'focal seizures with altered awareness' rather than shortening "
        "it to 'focal seizures'."
    ),
    (
        "Do not include seizure frequency for generic events, blackouts, "
        "collapse, anxiety attacks, or dissociative/non-epileptic events "
        "unless the same phrase is explicitly asserted as epileptic seizures."
    ),
    (
        "Reject vague words such as 'events', 'episodes', 'episodes of loss "
        "of consciousness', 'minor seizures', and 'jerks' when the letter "
        "describes uncertain attacks, dizziness, loss of consciousness, "
        "shaking, or light-triggered jerks without explicitly asserting that "
        "those words themselves are an epileptic seizure type."
    ),
    (
        "Do not include childhood febrile seizures, family-history seizures, "
        "risk discussion, or old previous-event context as current seizure "
        "frequency unless the sentence explicitly gives the patient's current "
        "frequency state."
    ),
    (
        "Do not include risk or counselling statements such as 'risk of "
        "further seizures', 'at risk of further seizures', or 'even though he "
        "has only had one seizure' as seizure frequency."
    ),
    (
        "Do not include non-epileptic or diagnostically vague episode "
        "descriptions as seizure frequency, even when they include a cadence, "
        "such as 'episodes around twice a week of an unusual thought'."
    ),
    (
        "Do not include old or contextual minor-seizure episode phrases such "
        "as 'the episodes occur 4 to 5 times a year' unless the sentence "
        "explicitly asserts an epileptic seizure type."
    ),
    (
        "Onset-history statements such as 'seizures since the age of 13' are "
        "not seizure frequency by themselves. Use them only as a seizure-free "
        "since-age time point when the same sentence says the last seizures "
        "were in a past age range such as the teenage years."
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
        "the note counts clusters, for example fact 'cluster of seizures' with "
        "NumberOfSeizures='1' and the stated date or time frame."
    ),
    (
        "For frequency-change statements without an exact count, include a "
        "seizure-frequency event with FrequencyChange only: Decreased, "
        "Frequent, Increased, Infrequent, or Same."
    ),
    (
        "For dated counts such as '2 to 3 in March', use "
        "LowerNumberOfSeizures and UpperNumberOfSeizures plus MonthDate or "
        "YearDate and TimeSince_or_TimeOfEvent='During'; do not invent "
        "TimePeriod='Month' unless the note says per month."
    ),
    (
        "For 'since last clinic', use TimeSince_or_TimeOfEvent='Since' and "
        "PointInTime='LastClinic'; do not put 'since last clinic' in "
        "TimePeriod."
    ),
    (
        "For last-event or seizure-free statements, use NumberOfSeizures='0' "
        "with TimeSince_or_TimeOfEvent='Since' and the stated MonthDate, "
        "YearDate, or PointInTime. Do not convert last-event dates into an "
        "annual recurring rate."
    ),
    (
        "Phrases like 'last seizure', 'last event', or 'has had none since' "
        "mean seizure-free since that point for the named seizure type; do "
        "not include them as one seizure during that date or as an active "
        "current-rate statement."
    ),
    (
        "Do not infer seizure-free from phrases like 'last seizure coincided "
        "with missing medication' or 'previous seizure was a year ago' unless "
        "the letter also gives a clear no-further/since frame for the same "
        "seizure type."
    ),
    (
        "For seizure-free statements, set fact to the underlying seizure "
        "phrase when it is present in the same sentence, such as 'seizures' "
        "or 'focal seizures'; otherwise use the exact seizure-free phrase."
    ),
    (
        "Do not include safety-advice, conditional, or instructional "
        "statements as seizure frequency. Phrases such as 'if you have a "
        "seizure', 'in the event of a seizure', 'advised what to do if "
        "seizures occur', or general SUDEP/driving advice describe guidance, "
        "not a current rate."
    ),
    (
        "Do not include a bare seizure-free or 'well controlled' "
        "seizure-frequency event unless it names the seizure type and gives a "
        "since, last, date, or drug-change frame. Phrases such as 'remains "
        "seizure free and is now driving' or 'seizures were well controlled "
        "on medication' are not enough on their own."
    ),
    (
        "Do not use a pointing phrase such as 'these seizures', 'such "
        "episodes', or 'the events' as the seizure-frequency fact. Use the "
        "specific named seizure type stated earlier in the same context, or "
        "the generic 'seizures' when the count refers to seizures in general."
    ),
    (
        "When a sentence names two seizure types joined by 'and' with a "
        "single shared count, include the count against the seizure type it "
        "actually belongs to, not a merged 'X and Y' wording; only split into "
        "two seizure-frequency events if the letter gives each type its own "
        "count or state."
    ),
    (
        "Include at most one seizure-frequency event per distinct rate "
        "statement. Do not include both a generic 'seizures' event and a "
        "named-type event for the same single count in the same clause."
    ),
    ],
    "medication": [
    (
        "Current ordinary regimens and rescue as-required regimens include "
        "medication events; previous trials, stopped drugs, future starts, "
        "titration targets, options, and if-further-seizures plans are usually "
        "rejected."
    ),
    (
        "If a current regimen gives unequal time-of-day doses such as "
        "'Epilim 300 mg mane and 600 mg nocte' or 'Lamictal 100 mg in the "
        "morning, 175 mg in the afternoon', include separate medication "
        "events with Frequency='1'. Do not mark these current scheduled "
        "doses as As_Required."
    ),
    (
        "When the current regimen says 'twice a day', 'twice daily', or "
        "'bd', include Frequency='2'; when it says once daily, mane, nocte, "
        "morning, or evening, include Frequency='1'."
    ),
    (
        "For medication list entries that contain a compact regimen, write "
        "fact as the exact medication wording including dose and frequency "
        "when those words are part of the same short line, for example "
        "'Topiramate 100 mg BD'."
    ),
    ],
    "investigation": [
    (
        "ECG is not one of the requested investigations. Never map ECG to "
        "EEG, MRI, or CT, and do not include an investigation event from "
        "ECG-only evidence."
    ),
    (
        "If the test sentence contains 'will', 'arrange', 'request', "
        "'await'/'awaiting', 'appointment', 'suggest', 'recommend', 'should "
        "update', 'chase', 'up to date', 'not yet performed/received', or "
        "'planned', treat it as a pending test and do not include an "
        "investigation event for it unless a separate completed result for "
        "the same modality is also stated."
    ),
    (
        "Do not include a bare test-name-only investigation when the note "
        "gives no completion or result statement, and do not add a duplicate "
        "test-name-only event when a result-bearing event for the same "
        "modality is already included."
    ),
    ],
    "output": [
        'If no requested findings are present, return {"clinical_events": []}.',
        "Return exactly one JSON object. No markdown code fences.",
    ],
}

SHARED_RULE_SECTION_KEYS = tuple(_SHARED_RULE_SECTIONS)


def compact_rule_count(rules: dict[str, list[str]]) -> int:
    """Count authored Compact rules across sections."""

    return sum(len(section) for section in rules.values())


def _sectioned_rules(*, include_suggested: bool) -> dict[str, list[str]]:
    rules = {key: list(rows) for key, rows in _SHARED_RULE_SECTIONS.items()}
    if include_suggested:
        return {"suggested_evidence": list(_HYBRID_RULES), **rules}
    return rules


def build_compact_prompt_input(letter: ExectLetter) -> str:
    """Build the Compact hybrid payload, including suggested evidence."""

    payload = {
        "task": _HYBRID_TASK,
        "output_schema": _OUTPUT_SCHEMA,
        "decision_procedure": list(_HYBRID_DECISION_PROCEDURE),
        "family_guidance": dict(_FAMILY_GUIDANCE),
        "attribute_vocabulary": dict(_ATTRIBUTE_VOCABULARY),
        "categories": {family: list(rows) for family, rows in _CATEGORIES.items()},
        "clinical_rules": _sectioned_rules(include_suggested=True),
        "suggested_evidence": _suggested_evidence(letter),
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False)


def build_compact_llm_only_prompt_input(letter: ExectLetter) -> str:
    """Build the Compact LLM-only payload, without suggested evidence."""

    payload = {
        "task": _LLM_ONLY_TASK,
        "output_schema": _OUTPUT_SCHEMA,
        "decision_procedure": list(_LLM_ONLY_DECISION_PROCEDURE),
        "family_guidance": dict(_FAMILY_GUIDANCE),
        "attribute_vocabulary": dict(_ATTRIBUTE_VOCABULARY),
        "clinical_rules": _sectioned_rules(include_suggested=False),
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False)


def _suggested_evidence(letter: ExectLetter) -> list[dict[str, str]]:
    return [
        {
            "family": str(row["family"]),
            "evidence": str(row["evidence"]),
            "name_hint": str(row["anchor_hint"]),
            "category": str(row["lane_hint"]),
        }
        for row in candidate_evidence_ledger_for_letter(letter)
    ]
