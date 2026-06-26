"""Static prompt guidance, render policies, and worked-example selection."""

from __future__ import annotations

from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.prompts.key_entities.loader import (
    load_dedup_fact_worked_examples,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.generation_selection.types import (
    DedupFactFamily,
    PromptProfile,
)


def _clinical_rules() -> list[str]:
    return [
        (
            "Scan the whole letter for current anti-seizure medication, diagnoses, "
            "seizure-frequency states, and completed investigations."
        ),
        (
            "Use exact substrings for evidence; source-near evidence is required "
            "for every final mention."
        ),
        (
            "Render mention text as the clinical concept; put dose, count, date, "
            "result, and certainty details in attributes."
        ),
        (
            "For SeizureFrequency, mention text should be the seizure type or "
            "state anchor, such as focal seizures or secondary generalised "
            "seizures, not the count phrase."
        ),
        (
            "For dated seizure counts such as in March, use MonthDate plus "
            "TimeSince_or_TimeOfEvent='During'; do not convert a dated count "
            "into a per-month rate unless the letter says per month."
        ),
        (
            "MonthDate must be numeric, e.g. January='1' and March='3'. "
            "Do not use PointInTime='Last_Month' or NumberOfTimePeriods for a "
            "named calendar month. Do not add TimePeriod for a named calendar "
            "month unless the note says per month."
        ),
        (
            "A SeizureFrequency mention must include count, date, interval, "
            "seizure-free, or change-state attributes directly in "
            "mention.attributes."
        ),
        (
            "Separate patient-level epilepsy diagnoses from named seizure-type "
            "diagnoses when both are stated."
        ),
        (
            "When a Diagnosis heading says focal epilepsy-probable temporal, "
            "emit both focal epilepsy and temporal lobe epilepsy; probable "
            "temporal is not a standalone mention."
        ),
        (
            "Do not de-duplicate repeated source-supported facts across different "
            "source events. If the same diagnosis or seizure-frequency state is "
            "explicitly represented in both a diagnosis/list section and a "
            "seizure-frequency statement, emit a rendered mention for each "
            "source event."
        ),
        (
            "Final mentions may repeat the same entity, text, and attributes when "
            "different evidence clauses support separate rendered mentions. Keep "
            "the repeated mentions instead of merging them."
        ),
        (
            "For generic epilepsy headings such as epilepsy-unclassified, render "
            "the core Diagnosis text as epilepsy unless a more specific epilepsy "
            "syndrome is explicitly stated."
        ),
        (
            "Named seizure types such as focal seizures, absence seizures, and "
            "secondary generalised seizures use Diagnosis DiagCategory "
            "MultipleSeizures."
        ),
        (
            "When a source sentence gives a frequency for a named plural seizure "
            "type, emit both a Diagnosis mention for that seizure type and a "
            "SeizureFrequency mention for the same source sentence."
        ),
        (
            "For count ranges such as 2 to 3, several, or between 4 and 6, do "
            "not put the range phrase in NumberOfSeizures. Use "
            "LowerNumberOfSeizures and UpperNumberOfSeizures."
        ),
        (
            "Do not render planned investigations or future medication changes "
            "as completed/current facts."
        ),
        (
            "Retain prior completed MRI, CT, EEG, VEEG, video EEG, or telemetry "
            "mentions when the letter states a result. Words such as previous, "
            "prior, old, or 2012 do not make a completed result future or planned."
        ),
        (
            "For Investigations mention text, include the modality plus test word "
            "as the source span when present, such as MRI scan, CT head, EEG, "
            "video EEG, VEEG, or telemetry."
        ),
        (
            "Do not emit not-performed Investigation facts for planned, repeat, "
            "awaiting, or future tests; omit those tests instead."
        ),
        "Never emit a SeizureFrequency mention with empty state attributes.",
    ]


def _mention_attribute_contract() -> dict[str, list[str]]:
    return {
        "Prescription": [
            "DrugName, DrugDose, DoseUnit, and Frequency belong in mention.attributes.",
            "Do not place medication scoring fields only in event_state.",
        ],
        "Diagnosis": [
            "DiagCategory, Certainty, and Negation belong in mention.attributes.",
            "Named seizure types should use DiagCategory='MultipleSeizures'.",
        ],
        "SeizureFrequency": [
            (
                "NumberOfSeizures, LowerNumberOfSeizures, UpperNumberOfSeizures, "
                "NumberOfTimePeriods, TimePeriod, MonthDate, YearDate, "
                "TimeSince_or_TimeOfEvent, PointInTime, and FrequencyChange "
                "belong in mention.attributes."
            ),
            (
                "Do not put diagnosis attributes such as DiagCategory on "
                "SeizureFrequency mentions."
            ),
        ],
        "Investigations": [
            (
                "MRI_Performed, MRI_Results, EEG_Performed, EEG_Results, "
                "CT_Performed, and CT_Results belong in mention.attributes."
            ),
            "Do not emit planned, repeat, awaiting, or future investigation requests.",
        ],
    }


def _render_text_policy() -> list[str]:
    return [
        (
            "Use source_text for the short exact source span that names the fact; "
            "use text for the final rendered mention text."
        ),
        (
            "The text field may be a compact normalized clinical render and does "
            "not need to be an exact source substring. The evidence field must "
            "still be an exact source substring."
        ),
        (
            "For Diagnosis, use one named concept per mention: epilepsy, focal "
            "epilepsy, temporal lobe epilepsy, genetic generalised epilepsy, "
            "epilepsy with generalised tonic clonic seizures alone, focal-onset "
            "epilepsy, focal seizures, secondary generalised seizures, or "
            "generalised tonic clonic seizures when supported."
        ),
        (
            "Do not combine multiple Diagnosis concepts into one text value. "
            "Split compound diagnosis headings into separate generated_mentions."
        ),
        (
            "For singular seizure events, use singular text and "
            "DiagCategory='SingleSeizure'. For plural seizure types, use plural "
            "text and DiagCategory='MultipleSeizures'."
        ),
        (
            "For Prescription text, include the medication name plus dose and "
            "frequency. If the source line starts with Current medication or "
            "Current antiepileptic medication, source_text may include that label "
            "when it is part of the medication statement."
        ),
        (
            "For Investigations text, include modality plus visible year or result "
            "words when present, such as MRI 2012 normal, MRI scan, EEG 2015 "
            "normal, EEG abnormal, CT head normal, or video EEG."
        ),
        (
            "For SeizureFrequency text, use the seizure type or state anchor, "
            "such as seizures, focal seizures, absence-like seizures, "
            "generalised tonic clonic seizures, or seizure-free."
        ),
    ]


def _clean_render_text_policy() -> list[str]:
    return [
        (
            "source_text must be copied from the letter. clean_text should be a "
            "compact clinical label for the same fact, not a full sentence."
        ),
        (
            "For Prescription clean_text, copy the medication phrase from the "
            "letter as closely as possible, preserving abbreviations such as BD, "
            "mane, nocte, OD, PRN, and source spelling of the dose/frequency. "
            "Keep DrugName as the generic medication name in attributes."
        ),
        (
            "For Diagnosis clean_text, emit one concept per mention. Split "
            "compound headings into separate rows such as epilepsy, focal "
            "epilepsy, temporal lobe epilepsy, focal seizures, or generalised "
            "tonic clonic seizures when each is supported."
        ),
        (
            "For named seizure types, emit a Diagnosis row for every source "
            "statement that names the seizure type. If a frequency sentence "
            "names focal seizures or secondary generalised seizures, emit both "
            "the Diagnosis row and the SeizureFrequency row from that sentence, "
            "even if the same seizure type was named earlier."
        ),
        (
            "For SeizureFrequency clean_text, name the seizure type or state, "
            "such as seizures, focal seizures, secondary generalised seizures, "
            "generalised tonic clonic seizures, or seizure-free. Put counts, "
            "dates, intervals, and changes in attributes."
        ),
        (
            "For Investigations clean_text, prefer the compact test phrase "
            "that names the modality, such as MRI scan, MRI, EEG, CT head, "
            "video EEG, VEEG, or telemetry. Put normal/abnormal result state "
            "in attributes rather than lengthening clean_text unless the source "
            "phrase itself is only a result phrase such as EEG abnormal."
        ),
        (
            "When the same clinical fact is explicitly stated in separate source "
            "events, emit separate generated rows with separate mention_id values."
        ),
    ]


def _forbidden_attribute_combinations() -> list[dict[str, str]]:
    return [
        {
            "entity": "SeizureFrequency",
            "when": "MonthDate is present because the letter names a calendar month",
            "forbid": "NumberOfTimePeriods, TimePeriod, and PointInTime",
            "reason": (
                "A calendar month is a date anchor, not a rate denominator or "
                "relative point-in-time."
            ),
        },
        {
            "entity": "Investigations",
            "when": "the test is planned, requested, repeat, awaiting, or future",
            "forbid": "MRI_Performed, EEG_Performed, CT_Performed, and result attributes",
            "reason": "Future tests are omitted from final_events.",
        },
    ]


def _dedup_fact_worked_examples(
    prompt_profile: PromptProfile,
    *,
    target_family: DedupFactFamily | None = None,
) -> list[dict[str, Any]]:
    examples = load_dedup_fact_worked_examples()
    if prompt_profile == "full_examples":
        selected_examples = examples
    elif prompt_profile == "decision_table":
        selected_examples = [examples[index] for index in (0, 2, 4, 5)]
    else:
        selected_examples = examples[:4]
    if target_family is None:
        return selected_examples

    filtered_examples: list[dict[str, Any]] = []
    for example in selected_examples:
        family_facts = [
            fact
            for fact in example.get("clinical_facts", [])
            if fact.get("family") == target_family
        ]
        filtered = {
            "note_fragment": example["note_fragment"],
            "clinical_facts": family_facts,
        }
        if not family_facts and "omission_note" in example:
            filtered["omission_note"] = example["omission_note"]
        elif not family_facts:
            filtered["omission_note"] = (
                f"No source-supported {target_family} facts are emitted for this "
                "family-specific call."
            )
        elif "omission_note" in example:
            filtered["omission_note"] = example["omission_note"]
        filtered_examples.append(filtered)
    return filtered_examples


def _worked_examples(prompt_profile: PromptProfile) -> list[dict[str, Any]]:
    examples = structured._worked_examples()
    if prompt_profile == "full_examples":
        return examples
    compact_indexes = (
        0,
        1,
        2,
        5,
        10,
        11,
        12,
        21,
        22,
        23,
        24,
        36,
        38,
        39,
        40,
    )
    return [examples[index] for index in compact_indexes if index < len(examples)]
