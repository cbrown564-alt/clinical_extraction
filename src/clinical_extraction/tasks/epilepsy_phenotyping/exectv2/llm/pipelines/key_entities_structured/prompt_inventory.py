"""Inventory extract prompt.

Ordinary-language one-call request for recall-first listing of stated
diagnoses, named seizure types, and frequency or control statements.
Not a Compact inherit-and-drop list. Living paper extract
(``exect_llm_extract``). No research metadata.
"""

from __future__ import annotations

import json
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter

from .prompt_content import suggested_evidence_rows

INVENTORY_AUTHORED_KEYS = (
    "task",
    "output_schema",
    "decision_procedure",
    "family_guidance",
    "attribute_vocabulary",
    "clinical_rules",
    "examples",
    "letter_text",
)
INVENTORY_BOTH_AUTHORED_KEYS = (
    "task",
    "output_schema",
    "decision_procedure",
    "family_guidance",
    "attribute_vocabulary",
    "clinical_rules",
    "examples",
    "suggested_evidence",
    "letter_text",
)

_TASK = (
    "Read the clinical letter once. List the medication, diagnosis, "
    "seizure-frequency, and investigation facts the letter states. If one "
    "fact belongs to more than one of those families, include each valid "
    "family separately."
)
_TASK_BOTH = (
    "Read the clinical letter once. Use the suggested evidence as a starting "
    "point, then list the medication, diagnosis, seizure-frequency, and "
    "investigation facts the letter states. If one fact belongs to more than "
    "one of those families, include each valid family separately."
)

_DECISION_PROCEDURE = [
    (
        "Scan the whole letter for medication, diagnosis, seizure frequency, "
        "and investigations. Do not stop at section headers."
    ),
    (
        "Write every stated diagnosis, named seizure type, and frequency or "
        "control statement."
    ),
    (
        "Provide exact evidence from the letter for each event. "
    ),
]
_DECISION_BOTH = [
    _DECISION_PROCEDURE[0],
    (
        "Treat suggested-evidence rows as likely supporting sentences. Keep a "
        "fact when the letter supports it. Still write stated facts that are "
        "not in the suggested list."
    ),
    *_DECISION_PROCEDURE[1:],
]

_FAMILY_GUIDANCE = {
    "medication": (
        "Anti-seizure medicines. Include name, dose, unit, and frequency when "
        "stated. Copy the medication wording from the letter: the full short "
        "regimen when it appears in a list, or the drug name alone when that "
        "is all the note states."
    ),
    "diagnosis": (
        "Diagnoses such as epilepsy, focal epilepsy, seizure disorder, or "
        "named seizure types, including heading types such as myoclonic jerks "
        "or absences. Include DiagCategory. Blackouts, anxiety, or "
        "dissociative events are not diagnoses unless the letter states they "
        "are epileptic."
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
        "dose": "Numeric dose only, without the unit.",
        "frequency": ["1", "2", "3", "as_required"],
        "name": "Drug name as written.",
        "unit": ["g", "mg"],
    },
    "diagnosis": {
        "DiagCategory": ["Epilepsy", "MultipleSeizures", "SingleSeizure"],
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

_CLINICAL_RULES: dict[str, list[str]] = {
    "shared": [
        (
            "Write a separate event for each stated medication, diagnosis, "
            "named seizure type, frequency or control statement, or test. "
        ),
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
            "If the letter names a syndrome and a seizure type, such as juvenile "
            "absence epilepsy and tonic clonic seizures, include each as its own "
            "diagnosis event."
        ),
        (
            "If the letter states a more specific place or type in the same "
            "diagnosis heading or the next sentence — such as probable focal, "
            "? temporal, occipital, frontal, nocturnal GTCS, or a named type "
            "beside a syndrome — write that as its own diagnosis event as well "
            "as the heading syndrome. Extra stated types are acceptable; do not "
            "skip a stated type to stay tidy."
        ),
        (
            "Every named seizure type in a seizure-type or frequency heading is also "
            "a diagnosis event, even when it only appears in that heading."
        ),
        (
            "If a heading says epilepsy with probable, possible, unclassified, or a "
            "question-mark place such as probable focal or ? temporal, write epilepsy "
            "and the implied syndrome or place, for example focal epilepsy or "
            "temporal lobe epilepsy. Do not write the hedge word alone as the fact."
        ),
        (
            "Keep a generic epilepsy diagnosis when the letter states it, even if a "
            "more specific syndrome or seizure type is also present."
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
            "For tonic-clonic seizure wording, preserve 'tonic clonic' or "
            "'tonic-clonic'. Fix misspellings like 'tonic chronic'."
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
            "For seizure-frequency wording, use the generic seizure phrase when "
            "the count refers to seizures generally; use a named seizure type only "
            "when the count explicitly belongs to that type."
        ),
        (
            "Seizure type and frequency headings often state the frequency. If a "
            "heading says 'seizures every 3 to 4 weeks', 'several seizures since "
            "last clinic', '2 generalised tonic clonic seizures 2014', or a named "
            "seizure type plus a date, include a seizure-frequency event for those "
            "seizure words even when the count is approximate or dated. Also write "
            "a later statement if it names a rate, a return of seizures, or a "
            "control state."
        ),
        (
            "When a heading names more than one seizure type, write a "
            "seizure-frequency event for each named type using that type's own rate. "
            "If the letter also states a generic seizure-free or unknown seizure "
            "state beside those typed rates, keep a separate generic seizure event "
            "for that state."
        ),
        (
            "A no-further, remains-seizure-free, last-event, returned, or "
            "well-controlled statement is still a seizure-frequency event. If the "
            "letter gives no count, still write the event and do not invent a number."
        ),
        (
            "Heading-named myoclonic jerks and absences are seizure-frequency events "
            "when the letter lists them as a seizure type or gives them a cadence."
        ),
        (
            "A heading that names a seizure type and a last event or year is still a "
            "seizure-frequency event. Write it even when that date is years ago."
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
            "If the letter names current seizures but gives no count, still write "
            "the event and do not invent a number."
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
            "events with frequency='1'. Do not mark these current scheduled "
            "doses as as_required."
        ),
        (
            "When the current regimen says 'twice a day', 'twice daily', or "
            "'bd', include frequency='2'; when it says once daily, mane, nocte, "
            "morning, or evening, include frequency='1'."
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

_EXAMPLES = [
    {
        "letter": (
            "Diagnosis: symptomatic structural focal epilepsy. "
            "Seizure type and frequency: focal seizures with altered awareness every 3 weeks."
        ),
        "clinical_events": [
            {
                "family": "diagnosis",
                "evidence": "Diagnosis: symptomatic structural focal epilepsy.",
                "fact": "symptomatic structural focal epilepsy",
                "attributes": {"DiagCategory": "Epilepsy"},
            },
            {
                "family": "diagnosis",
                "evidence": (
                    "Seizure type and frequency: focal seizures with altered "
                    "awareness every 3 weeks."
                ),
                "fact": "focal seizures with altered awareness",
                "attributes": {"DiagCategory": "Epilepsy"},
            },
        ],
    },
    {
        "letter": (
            "She was diagnosed with epilepsy at the age of 4. "
            "She continues to have juvenile absence epilepsy and tonic clonic seizures."
        ),
        "clinical_events": [
            {
                "family": "diagnosis",
                "evidence": "She was diagnosed with epilepsy at the age of 4.",
                "fact": "epilepsy",
                "attributes": {"DiagCategory": "Epilepsy"},
            },
            {
                "family": "diagnosis",
                "evidence": (
                    "She continues to have juvenile absence epilepsy and "
                    "tonic clonic seizures."
                ),
                "fact": "juvenile absence epilepsy",
                "attributes": {"DiagCategory": "Epilepsy"},
            },
            {
                "family": "diagnosis",
                "evidence": (
                    "She continues to have juvenile absence epilepsy and "
                    "tonic clonic seizures."
                ),
                "fact": "tonic clonic seizures",
                "attributes": {"DiagCategory": "Epilepsy"},
            },
        ],
    },
    {
        "letter": (
            "Diagnosis: juvenile myoclonic epilepsy. "
            "Seizure types: nocturnal GTCS."
        ),
        "clinical_events": [
            {
                "family": "diagnosis",
                "evidence": "Diagnosis: juvenile myoclonic epilepsy.",
                "fact": "juvenile myoclonic epilepsy",
                "attributes": {"DiagCategory": "Epilepsy"},
            },
            {
                "family": "diagnosis",
                "evidence": "Seizure types: nocturnal GTCS.",
                "fact": "nocturnal GTCS",
                "attributes": {"DiagCategory": "Epilepsy"},
            },
        ],
    },
    {
        "letter": (
            "Diagnosis: juvenile myoclonic epilepsy. "
            "Seizure type and frequency: generalised tonic clonic seizures "
            "1 to 2 every month. Myoclonic jerks daily. Occasional absences. "
            "Unfortunately the seizures have returned."
        ),
        "clinical_events": [
            {
                "family": "diagnosis",
                "evidence": "Diagnosis: juvenile myoclonic epilepsy.",
                "fact": "juvenile myoclonic epilepsy",
                "attributes": {"DiagCategory": "Epilepsy"},
            },
            {
                "family": "diagnosis",
                "evidence": (
                    "Seizure type and frequency: generalised tonic clonic "
                    "seizures 1 to 2 every month."
                ),
                "fact": "generalised tonic clonic seizures",
                "attributes": {"DiagCategory": "Epilepsy"},
            },
            {
                "family": "diagnosis",
                "evidence": "Myoclonic jerks daily.",
                "fact": "Myoclonic jerks",
                "attributes": {"DiagCategory": "Epilepsy"},
            },
            {
                "family": "diagnosis",
                "evidence": "Occasional absences.",
                "fact": "absences",
                "attributes": {"DiagCategory": "Epilepsy"},
            },
            {
                "family": "seizure_frequency",
                "evidence": (
                    "Seizure type and frequency: generalised tonic clonic "
                    "seizures 1 to 2 every month."
                ),
                "fact": "generalised tonic clonic seizures",
                "attributes": {
                    "LowerNumberOfSeizures": "1",
                    "UpperNumberOfSeizures": "2",
                    "TimePeriod": "Month",
                },
            },
            {
                "family": "seizure_frequency",
                "evidence": "Myoclonic jerks daily.",
                "fact": "Myoclonic jerks",
                "attributes": {
                    "NumberOfSeizures": "1",
                    "TimePeriod": "Day",
                },
            },
            {
                "family": "seizure_frequency",
                "evidence": "Occasional absences.",
                "fact": "absences",
                "attributes": {"FrequencyChange": "Infrequent"},
            },
            {
                "family": "seizure_frequency",
                "evidence": "Unfortunately the seizures have returned.",
                "fact": "seizures",
                "attributes": {"FrequencyChange": "Increased"},
            },
        ],
    },
    {
        "letter": "She is feeling well and has not had any further seizures.",
        "clinical_events": [
            {
                "family": "seizure_frequency",
                "evidence": (
                    "She is feeling well and has not had any further seizures."
                ),
                "fact": "seizures",
                "attributes": {"NumberOfSeizures": "0"},
            }
        ],
    },
]

INVENTORY_RULE_COUNT = 50


def build_inventory_prompt_input(
    letter: ExectLetter, *, include_suggested: bool = False
) -> str:
    """Build the living extract payload, or both-extract with suggested rows."""

    payload: dict[str, Any] = {
        "task": _TASK_BOTH if include_suggested else _TASK,
        "output_schema": _OUTPUT_SCHEMA,
        "decision_procedure": (
            list(_DECISION_BOTH) if include_suggested else list(_DECISION_PROCEDURE)
        ),
        "family_guidance": dict(_FAMILY_GUIDANCE),
        "attribute_vocabulary": dict(_ATTRIBUTE_VOCABULARY),
        "clinical_rules": {key: list(rows) for key, rows in _CLINICAL_RULES.items()},
        "examples": list(_EXAMPLES),
    }
    if include_suggested:
        payload["suggested_evidence"] = suggested_evidence_rows(letter)
    payload["letter_text"] = letter.note_text
    return json.dumps(payload, ensure_ascii=False)


def build_inventory_both_prompt_input(letter: ExectLetter) -> str:
    """Build both-extract: living extract plus suggested candidates."""

    return build_inventory_prompt_input(letter, include_suggested=True)
