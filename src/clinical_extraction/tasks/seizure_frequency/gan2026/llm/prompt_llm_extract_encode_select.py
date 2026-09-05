"""One-call Gan find, encode, and select.

Self-contained request. The letter is in the request. This is a
controlled bundling ablation, not the cited extract.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord

GAN_LLM_EXTRACT_ENCODE_SELECT = "gan_llm_extract_encode_select"
LLM_EXTRACT_ENCODE_SELECT_TEMPLATE_KEYS = (
    "task",
    "instructions",
    "fact_schema",
    "label_forms",
    "selection_schema",
    "cases",
)
LLM_EXTRACT_ENCODE_SELECT_AUTHORED_KEYS = (
    *LLM_EXTRACT_ENCODE_SELECT_TEMPLATE_KEYS,
    "note_text",
)
CASE_KEYS = ("title", "instruction", "example")
EXAMPLE_KEYS = ("facts", "answer")

TASK = (
    "Read the clinical note. Extract every seizure-frequency "
    "fact, then select how often seizures are happening now."
)

EXTRACT_INSTRUCTIONS = [
    "Read the full clinical note and extract every seizure-frequency fact.",
    (
        "For each fact, write both raw_value and normalised_label. If you "
        "cannot write both, do not add the fact. Use raw_value for the "
        "original wording: the stated rate, duration, last-seizure "
        "statement, or wording that shows frequency is unknown or not mentioned. "
        "Write normalised_label using only the allowed forms. Copy an example "
        "and change the numbers if needed."
    ),
    (
        "Fact kind must be one of frequency_rate, cluster_frequency, seizure_free, "
        "last_event_only, unknown_frequency, or no_reference."
    ),
    (
        "Use one no_reference fact only when the note contains no usable "
        "seizure-frequency evidence. Write both fields as no seizure frequency "
        "reference. Do not use no_reference when seizures are discussed but "
        "frequency is unclear; use unknown_frequency instead."
    ),
    (
        "Keep seizure-free statements separate from unknown or last-seizure-only "
        "statements."
    ),
    (
        "When the note says a last seizure occurred on a date and the patient has "
        "been well, stable, or seizure-free since, still extract the dated last-seizure "
        "fact as its own fact even if the selection is seizure-free."
    ),
    (
        "When the note says a count such as 3 or 4 jerks occurred since a dated "
        "last tonic-clonic seizure, keep that count and the date in the fact list."
    ),
    "Every evidence value must be an exact substring from the note when possible.",
    "Return exactly one JSON object with no markdown.",
]

FACT_SCHEMA = {
    "fact_id": "stable string such as f1",
    "kind": [
        "frequency_rate",
        "cluster_frequency",
        "seizure_free",
        "last_event_only",
        "unknown_frequency",
        "no_reference",
    ],
    "raw_value": "original wording from the note",
    "normalised_label": "allowed-form label",
    "applies_to": "seizure type or other described attack, or null",
    "time_window": "original timeframe from the note, or null",
    "temporality": ["current", "recent", "historical", "future", "unclear"],
    "evidence": "exact note substring",
}

LABEL_FORM_RULES = [
    "Write the label using only the forms below. Copy an example and change the numbers if needed.",
    "Use digits, not word numbers.",
    "Use day, week, month, or year. Prefer the singular word.",
    "A night count is a day count: once per night becomes 1 per day.",
    (
        "Write an upper or lower limit as that number: at most four per day, "
        "or ≤ four per day, becomes 4 per day."
    ),
    "Do not write <=, >=, up to, at most, several, handful, frequent, or a calendar date.",
    (
        "If none of these forms fit, write unknown when seizures are "
        "discussed, or no seizure frequency reference when there is no "
        "usable frequency evidence."
    ),
]

LABEL_FORMS: list[dict[str, Any]] = [
    {
        "form": "N per unit",
        "description": "A single count in one day, week, month, or year.",
        "examples": ["1 per day", "4 per week", "3 per month", "2 per year"],
    },
    {
        "form": "N per N unit",
        "description": "A single count over a stated number of days, weeks, months, or years.",
        "examples": ["1 per 2 day", "1 per 2 week", "2 per 6 months"],
    },
    {
        "form": "N per N to N unit",
        "description": "A single count over a range of days, weeks, months, or years.",
        "examples": ["1 per 2 to 3 days", "1 per 2 to 3 weeks", "1 per 4 to 6 months"],
    },
    {
        "form": "N to N per unit",
        "description": "A count range in one day, week, month, or year.",
        "examples": [
            "2 to 3 per day",
            "2 to 4 per week",
            "3 to 5 per month",
            "2 to 4 per year",
        ],
    },
    {
        "form": "N to N per N unit",
        "description": "A count range over a stated number of days, weeks, months, or years.",
        "examples": ["2 to 4 per 3 months", "2 to 3 per 2 weeks"],
    },
    {
        "form": "multiple per unit",
        "description": "More than one seizure in one day, week, or month, with no number given.",
        "examples": ["multiple per day", "multiple per week", "multiple per month"],
    },
    {
        "form": "multiple per N unit",
        "description": (
            "More than one seizure over a stated number of months, with no number given."
        ),
        "examples": ["multiple per 2 months"],
    },
    {
        "form": "N per multiple unit",
        "description": "A count over an unstated number of days or months.",
        "examples": ["1 per multiple days", "1 per multiple months"],
    },
    {
        "form": "cluster per unit, N per cluster",
        "description": (
            "How often clusters happen, and how many seizures are in each "
            "cluster. The cluster count or the time between clusters may be a range."
        ),
        "examples": [
            "1 cluster per day, 5 per cluster",
            "1 cluster per week, 4 per cluster",
            "1 cluster per 4 months, 5 per cluster",
            "6 cluster per month, 4 per cluster",
            "1 cluster per 4 to 5 days, 2 per cluster",
        ],
    },
    {
        "form": "cluster per unit, range per cluster",
        "description": "How often clusters happen, and a range of seizures in each cluster.",
        "examples": [
            "1 cluster per day, 2 to 4 per cluster",
            "1 cluster per week, 3 to 6 per cluster",
            "1 cluster per month, 4 to 6 per cluster",
        ],
    },
    {
        "form": "cluster per unit, multiple per cluster",
        "description": (
            "How often clusters happen, and more than one seizure in each "
            "cluster with no number given."
        ),
        "examples": [
            "1 cluster per day, multiple per cluster",
            "1 cluster per week, multiple per cluster",
            "1 cluster per month, multiple per cluster",
        ],
    },
    {
        "form": "unknown cluster count",
        "description": "Clusters are described, but how often they happen is not known.",
        "examples": [
            "unknown, 5 per cluster",
            "unknown, 2 to 4 per cluster",
            "unknown, multiple per cluster",
        ],
    },
    {
        "form": "seizure free for a duration",
        "description": "No seizures for a stated length of time.",
        "examples": [
            "seizure free for 6 months",
            "seizure free for 3 months",
            "seizure free for 2 to 3 months",
        ],
    },
    {
        "form": "seizure free for a vague duration",
        "description": "No seizures for an unstated length of time.",
        "examples": [
            "seizure free for multiple months",
            "seizure free for multiple years",
        ],
    },
    {
        "form": "unknown",
        "description": "Seizures are discussed, but there is no usable frequency.",
        "examples": ["unknown"],
    },
    {
        "form": "no seizure frequency reference",
        "description": "There is no usable frequency evidence.",
        "examples": ["no seizure frequency reference"],
    },
]

SELECTION_SCHEMA = {
    "selected_fact_ids": "list of selected fact_id strings",
    "final_kind": [
        "frequency",
        "seizure_free",
        "unknown",
        "no_reference",
        "unresolved_multiple",
    ],
    "final_label": "normalised label, or null if the note does not give a count",
    "evidence": "exact note substring supporting the final selection",
    "rationale": "brief clinical reason for selecting these facts",
}


def _example_fact(
    fact_id: str,
    *,
    normalised_label: str,
    evidence: str,
    kind: str = "frequency_rate",
    temporality: str = "current",
    applies_to: str | None = "seizures",
    time_window: str | None = None,
) -> dict[str, Any]:
    return {
        "fact_id": fact_id,
        "kind": kind,
        "raw_value": evidence,
        "normalised_label": normalised_label,
        "temporality": temporality,
        "applies_to": applies_to,
        "time_window": time_window,
        "evidence": evidence,
    }


def _example_payload(
    facts: Sequence[Mapping[str, Any]],
    *,
    answer_fact_ids: Sequence[str],
    answer_label: str | None = None,
) -> dict[str, Any]:
    answer: dict[str, Any] = {
        "selected_fact_ids": list(answer_fact_ids),
    }
    if answer_label is not None:
        answer["label"] = answer_label
    return {
        "facts": [dict(fact) for fact in facts],
        "answer": answer,
    }


SELECT_BRIDGE = (
    "Use the cases below to decide the patient's current seizure frequency "
    "pattern. If a case matches, follow it. Write a new "
    "seizure-frequency label only when no single fact is the answer."
)

INSTRUCTIONS = [*EXTRACT_INSTRUCTIONS, SELECT_BRIDGE]

CASES: list[dict[str, Any]] = [
    {
        "title": "Usual gap",
        "instruction": (
            "If one fact is unknown, 1 per day, or multiple per day "
            "during short or occasional daily spells, and another "
            "fact gives the usual gap between seizures, prefer that "
            "usual gap."
        ),
        "example": _example_payload(
            [
                _example_fact(
                    "f1",
                    normalised_label="1 per day",
                    evidence="brief periods of daily seizures",
                ),
                _example_fact(
                    "f2",
                    normalised_label="1 per 2 week",
                    evidence="usually every 2 weeks",
                ),
            ],
            answer_fact_ids=["f2"],
        ),
    },
    {
        "title": "Usual rate, not a year total",
        "instruction": (
            "If one fact is how many seizures so far this year, and "
            "another fact gives the usual or typical rate, prefer "
            "the usual rate."
        ),
        "example": _example_payload(
            [
                _example_fact(
                    "f1",
                    normalised_label="4 per year",
                    evidence="4 seizures so far this year",
                    time_window="this year",
                ),
                _example_fact(
                    "f2",
                    normalised_label="1 per month",
                    evidence="typically 1 per month",
                ),
            ],
            answer_fact_ids=["f2"],
        ),
    },
    {
        "title": "Recent seizures after a quiet spell",
        "instruction": (
            "If the facts give a recent count and how long the "
            "person had been seizure-free, write that count over "
            "that time. Do this only if no fact already has that "
            "label."
        ),
        "example": _example_payload(
            [
                _example_fact(
                    "f1",
                    normalised_label="unknown",
                    kind="unknown_frequency",
                    evidence="2 tonic-clonic seizures",
                    applies_to="tonic-clonic seizures",
                ),
                _example_fact(
                    "f2",
                    normalised_label="seizure free for 6 month",
                    kind="seizure_free",
                    evidence="seizure-free for 6 months before that",
                    time_window="6 months",
                ),
            ],
            answer_fact_ids=["f1", "f2"],
            answer_label="2 per 6 month",
        ),
    },
    {
        "title": "Not epileptic seizures",
        "instruction": (
            "If the current facts are attacks that are not epileptic "
            "seizures, write seizure free for multiple year."
        ),
        "example": _example_payload(
            [
                _example_fact(
                    "f1",
                    normalised_label="unknown",
                    kind="unknown_frequency",
                    evidence="these are non-epileptic attacks",
                    applies_to="non-epileptic attacks",
                ),
                _example_fact(
                    "f2",
                    normalised_label="unknown",
                    kind="unknown_frequency",
                    evidence="no epileptic seizures",
                ),
            ],
            answer_fact_ids=["f1", "f2"],
            answer_label="seizure free for multiple year",
        ),
    },
    {
        "title": "Month counts",
        "instruction": (
            "Quotes name how many seizures happened in named months, "
            "such as 3 in March and 6 in May. "
            "Add those counts and write the total over that time. Use "
            "this instead of the last month alone, unknown, or a "
            "short or vague seizure-free label. Do not replace a rate "
            "per day or per week. Do not replace seizure-free for 4 "
            "months or longer, or for any number of years. You may "
            "replace a vague seizure free for multiple label."
        ),
        "example": _example_payload(
            [
                _example_fact(
                    "f1",
                    normalised_label="3 per month",
                    evidence="3 seizures in March",
                    time_window="March",
                ),
                _example_fact(
                    "f2",
                    normalised_label="6 per month",
                    evidence="6 seizures in May",
                    time_window="May",
                ),
            ],
            answer_fact_ids=["f1", "f2"],
            answer_label="9 per 3 month",
        ),
    },
    {
        "title": "Dated seizures",
        "instruction": (
            "Two or more facts name seizures on different dates or "
            "months, or a quote already says how many seizures "
            "happened in a number of months. Write that count over "
            "that time. Use this instead of unknown, seizure-free "
            "after the last date, or a monthly or yearly rate when "
            "that time is more than 1 month. Do not replace a rate "
            "per day or per week. Do this only if the last dated "
            "fact looks current or recent. Ignore dates described "
            "as before an improvement."
        ),
        "example": _example_payload(
            [
                _example_fact(
                    "f1",
                    normalised_label="unknown",
                    kind="unknown_frequency",
                    evidence="a seizure in March 2019",
                    time_window="March 2019",
                ),
                _example_fact(
                    "f2",
                    normalised_label="unknown",
                    kind="unknown_frequency",
                    evidence="a seizure in May 2019",
                    time_window="May 2019",
                ),
            ],
            answer_fact_ids=["f1", "f2"],
            answer_label="2 per 2 month",
        ),
    },
    {
        "title": "Burst after a change",
        "instruction": (
            "If the quotes describe seizures soon after a treatment "
            "change, then no further seizures for a stated time, "
            "write that burst count over the quiet time. Do this "
            "only if the quotes already give both the burst and the "
            "quiet time."
        ),
        "example": _example_payload(
            [
                _example_fact(
                    "f1",
                    normalised_label="3 per week",
                    evidence="3 seizures shortly after the dose change",
                    time_window="following week",
                ),
                _example_fact(
                    "f2",
                    normalised_label="seizure free for 6 month",
                    kind="seizure_free",
                    evidence="no further seizures since then",
                    time_window="6 months",
                ),
            ],
            answer_fact_ids=["f1", "f2"],
            answer_label="3 per 6 month",
        ),
    },
    {
        "title": "Short quiet spell after a last seizure",
        "instruction": (
            "If a quote names the last seizure on a calendar day, or "
            "a burst count, and says the person has been well since "
            "then, and the quiet spell is less than 6 "
            "months, write that count over that time."
        ),
        "example": _example_payload(
            [
                _example_fact(
                    "f1",
                    normalised_label="unknown",
                    kind="last_event_only",
                    evidence="last seizure on 12 March",
                    time_window="12 March",
                ),
                _example_fact(
                    "f2",
                    normalised_label="seizure free for 3 week",
                    kind="seizure_free",
                    evidence="remained well since then",
                    time_window="3 weeks",
                ),
            ],
            answer_fact_ids=["f1", "f2"],
            answer_label="1 per month",
        ),
    },
    {
        "title": "Overall count",
        "instruction": (
            "If several seizure types are listed, choose the highest "
            "current or recent overall count, not a breakdown by type."
        ),
        "example": _example_payload(
            [
                _example_fact(
                    "f1",
                    normalised_label="4 per month",
                    evidence="4 focal seizures this month",
                    applies_to="focal seizures",
                    time_window="this month",
                ),
                _example_fact(
                    "f2",
                    normalised_label="2 per month",
                    evidence="2 tonic-clonic seizures this month",
                    applies_to="tonic-clonic seizures",
                    time_window="this month",
                ),
                _example_fact(
                    "f3",
                    normalised_label="6 per month",
                    evidence="6 seizures this month in total",
                    time_window="this month",
                ),
            ],
            answer_fact_ids=["f3"],
        ),
    },
    {
        "title": "Do not choose seizure-free while seizures continue",
        "instruction": (
            "Do not choose seizure-free if other current seizure-like "
            "attacks are still happening."
        ),
        "example": _example_payload(
            [
                _example_fact(
                    "f1",
                    normalised_label="seizure free for 2 month",
                    kind="seizure_free",
                    evidence="seizure free for 2 months",
                    time_window="2 months",
                ),
                _example_fact(
                    "f2",
                    normalised_label="1 per week",
                    evidence="absences continue weekly",
                    applies_to="absences",
                ),
            ],
            answer_fact_ids=["f2"],
        ),
    },
]


def llm_extract_encode_select_prompt_template() -> dict[str, Any]:
    """Fixed one-call request without the letter body."""

    return {
        "task": TASK,
        "instructions": list(INSTRUCTIONS),
        "fact_schema": dict(FACT_SCHEMA),
        "label_forms": {
            "rules": list(LABEL_FORM_RULES),
            "forms": [dict(row) for row in LABEL_FORMS],
        },
        "selection_schema": dict(SELECTION_SCHEMA),
        "cases": [
            {
                "title": row["title"],
                "instruction": row["instruction"],
                "example": {key: row["example"][key] for key in EXAMPLE_KEYS},
            }
            for row in CASES
        ],
    }


def build_llm_extract_encode_select_prompt_input(record: GanFrequencyRecord) -> str:
    """Build the one-call find, encode, and select payload."""

    payload = {
        **llm_extract_encode_select_prompt_template(),
        "note_text": record.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)
