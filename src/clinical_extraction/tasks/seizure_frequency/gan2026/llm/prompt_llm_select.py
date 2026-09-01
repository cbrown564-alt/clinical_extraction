"""Gan later-stage select prompt.

Chooses how often seizures are happening now from already labelled
events and their quotes. No note text. No research metadata.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_label_forms import (
    label_forms_payload,
)

GAN_LLM_SELECT = "gan_llm_select"
GAN_LLM_SELECT_POLICY_EXAMPLES = "gan_llm_select_policy_examples"
LLM_SELECT_AUTHORED_KEYS = (
    "task",
    "instructions",
    "cases",
    "label_forms",
    "selection_schema",
    "first_choice",
    "events",
)
CASE_KEYS = ("title", "instruction", "example")
EXAMPLE_KEYS = ("first_choice", "events", "answer")

_SELECT_EVENT_KEYS = (
    "event_id",
    "label",
    "kind",
    "temporality",
    "assertion_status",
    "applies_to",
    "time_window",
    "evidence",
)

TASK = "Choose which events describe how often seizures are happening now."

INSTRUCTIONS = [
    (
        "Each event has a seizure-frequency label and a supporting "
        "quote. Use both. The quote can justify a different answer than "
        "the label. Use only facts already in the events or their "
        "quotes. Any new label must match one of the label forms."
    ),
    (
        "A first choice is given. Keep it unless one of the cases below "
        "applies."
    ),
    (
        "Return the selected event ids. Write a new label only when no "
        "single event is the answer. Do not add events. Do not write a "
        "new quote. Return exactly one JSON object with no markdown."
    ),
]

def _example_event(
    event_id: str,
    *,
    label: str,
    evidence: str,
    kind: str = "frequency_rate",
    temporality: str = "current",
    assertion_status: str = "asserted",
    applies_to: str | None = "seizures",
    time_window: str | None = None,
) -> dict[str, Any]:
    return {
        "event_id": event_id,
        "label": label,
        "kind": kind,
        "temporality": temporality,
        "assertion_status": assertion_status,
        "applies_to": applies_to,
        "time_window": time_window,
        "evidence": evidence,
    }


def _example_payload(
    events: Sequence[Mapping[str, Any]],
    *,
    selected_event_ids: Sequence[str],
    first_label: str,
    answer_event_ids: Sequence[str],
    answer_label: str | None = None,
) -> dict[str, Any]:
    answer: dict[str, Any] = {
        "selected_event_ids": list(answer_event_ids),
    }
    if answer_label is not None:
        answer["label"] = answer_label
    return {
        "first_choice": {
            "selected_event_ids": list(selected_event_ids),
            "label": first_label,
        },
        "events": [dict(event) for event in events],
        "answer": answer,
    }


CASES: list[dict[str, Any]] = [
    {
        "title": "Usual gap",
        "instruction": (
            "The first choice is unknown, 1 per day, or multiple per "
            "day during short or occasional daily spells. Another "
            "event gives the usual gap between seizures. Prefer that "
            "usual gap."
        ),
        "example": _example_payload(
            [
                _example_event(
                    "e1",
                    label="1 per day",
                    evidence="brief periods of daily seizures",
                ),
                _example_event(
                    "e2",
                    label="1 per 2 week",
                    evidence="usually every 2 weeks",
                ),
            ],
            selected_event_ids=["e1"],
            first_label="1 per day",
            answer_event_ids=["e2"],
        ),
    },
    {
        "title": "Usual rate, not a year total",
        "instruction": (
            "The first choice is how many seizures so far this year. "
            "Another event gives the usual or typical rate. Prefer "
            "the usual rate."
        ),
        "example": _example_payload(
            [
                _example_event(
                    "e1",
                    label="4 per year",
                    evidence="4 seizures so far this year",
                    time_window="this year",
                ),
                _example_event(
                    "e2",
                    label="1 per month",
                    evidence="typically 1 per month",
                ),
            ],
            selected_event_ids=["e1"],
            first_label="4 per year",
            answer_event_ids=["e2"],
        ),
    },
    {
        "title": "Recent seizures after a quiet spell",
        "instruction": (
            "The first choice is unknown or no seizure frequency "
            "reference. The events give a recent count and how long "
            "the person had been seizure-free. Write that count over "
            "that time. Do this only if no event already has that "
            "label."
        ),
        "example": _example_payload(
            [
                _example_event(
                    "e1",
                    label="unknown",
                    kind="unknown_frequency",
                    evidence="2 tonic-clonic seizures",
                    applies_to="tonic-clonic seizures",
                ),
                _example_event(
                    "e2",
                    label="seizure free for 6 month",
                    kind="seizure_free",
                    evidence="seizure-free for 6 months before that",
                    time_window="6 months",
                ),
            ],
            selected_event_ids=["e1"],
            first_label="unknown",
            answer_event_ids=["e1", "e2"],
            answer_label="2 per 6 month",
        ),
    },
    {
        "title": "Not epileptic seizures",
        "instruction": (
            "The first choice is unknown or no seizure frequency "
            "reference. The current events are attacks that are not "
            "epileptic seizures. Write seizure free for multiple year."
        ),
        "example": _example_payload(
            [
                _example_event(
                    "e1",
                    label="unknown",
                    kind="unknown_frequency",
                    evidence="these are non-epileptic attacks",
                    applies_to="non-epileptic attacks",
                ),
                _example_event(
                    "e2",
                    label="unknown",
                    kind="unknown_frequency",
                    evidence="no epileptic seizures",
                ),
            ],
            selected_event_ids=["e1"],
            first_label="unknown",
            answer_event_ids=["e1", "e2"],
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
                _example_event(
                    "e1",
                    label="3 per month",
                    evidence="3 seizures in March",
                    time_window="March",
                ),
                _example_event(
                    "e2",
                    label="6 per month",
                    evidence="6 seizures in May",
                    time_window="May",
                ),
            ],
            selected_event_ids=["e2"],
            first_label="6 per month",
            answer_event_ids=["e1", "e2"],
            answer_label="9 per 3 month",
        ),
    },
    {
        "title": "Dated seizures",
        "instruction": (
            "Two or more events name seizures on different dates or "
            "months, or a quote already says how many seizures "
            "happened in a number of months. Write that count over "
            "that time. Use this instead of unknown, seizure-free "
            "after the last date, or a monthly or yearly rate when "
            "that time is more than 1 month. Do not replace a rate "
            "per day or per week. Do this only if the last dated "
            "event looks current or recent. Ignore dates described "
            "as before an improvement."
        ),
        "example": _example_payload(
            [
                _example_event(
                    "e1",
                    label="unknown",
                    kind="unknown_frequency",
                    evidence="a seizure in March 2019",
                    time_window="March 2019",
                ),
                _example_event(
                    "e2",
                    label="unknown",
                    kind="unknown_frequency",
                    evidence="a seizure in May 2019",
                    time_window="May 2019",
                ),
            ],
            selected_event_ids=["e1"],
            first_label="unknown",
            answer_event_ids=["e1", "e2"],
            answer_label="2 per 2 month",
        ),
    },
    {
        "title": "Burst after a change",
        "instruction": (
            "The first choice is seizure-free, or a rate per day or "
            "per week. The quotes describe seizures soon after a "
            "treatment change, then no further seizures for a stated "
            "time. Write that burst count over the quiet time. Do "
            "this only if the quotes already give both the burst and "
            "the quiet time."
        ),
        "example": _example_payload(
            [
                _example_event(
                    "e1",
                    label="3 per week",
                    evidence="3 seizures shortly after the dose change",
                    time_window="following week",
                ),
                _example_event(
                    "e2",
                    label="seizure free for 6 month",
                    kind="seizure_free",
                    evidence="no further seizures since then",
                    time_window="6 months",
                ),
            ],
            selected_event_ids=["e2"],
            first_label="seizure free for 6 month",
            answer_event_ids=["e1", "e2"],
            answer_label="3 per 6 month",
        ),
    },
    {
        "title": "Short quiet spell after a last event",
        "instruction": (
            "The first choice is seizure-free for weeks, or for fewer "
            "than 6 months. A quote names the last seizure on a "
            "calendar day, or a burst count, and says the person has "
            "been well since then. Write that count over that time. "
            "If the quiet spell is 5 weeks or less, write the count "
            "per month."
        ),
        "example": _example_payload(
            [
                _example_event(
                    "e1",
                    label="unknown",
                    kind="last_event_only",
                    evidence="last seizure on 12 March",
                    time_window="12 March",
                ),
                _example_event(
                    "e2",
                    label="seizure free for 3 week",
                    kind="seizure_free",
                    evidence="remained well since then",
                    time_window="3 weeks",
                ),
            ],
            selected_event_ids=["e2"],
            first_label="seizure free for 3 week",
            answer_event_ids=["e1", "e2"],
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
                _example_event(
                    "e1",
                    label="4 per month",
                    evidence="4 focal seizures this month",
                    applies_to="focal seizures",
                    time_window="this month",
                ),
                _example_event(
                    "e2",
                    label="2 per month",
                    evidence="2 tonic-clonic seizures this month",
                    applies_to="tonic-clonic seizures",
                    time_window="this month",
                ),
                _example_event(
                    "e3",
                    label="6 per month",
                    evidence="6 seizures this month in total",
                    time_window="this month",
                ),
            ],
            selected_event_ids=["e1"],
            first_label="4 per month",
            answer_event_ids=["e3"],
        ),
    },
    {
        "title": "Do not choose seizure-free while events continue",
        "instruction": (
            "Do not choose seizure-free if other current seizure-like "
            "events are still happening."
        ),
        "example": _example_payload(
            [
                _example_event(
                    "e1",
                    label="seizure free for 2 month",
                    kind="seizure_free",
                    evidence="seizure free for 2 months",
                    time_window="2 months",
                ),
                _example_event(
                    "e2",
                    label="1 per week",
                    evidence="absences continue weekly",
                    applies_to="absences",
                ),
            ],
            selected_event_ids=["e1"],
            first_label="seizure free for 2 month",
            answer_event_ids=["e2"],
        ),
    },
]

SELECTION_SCHEMA = {
    "selected_event_ids": "ids of the events used for the answer",
    "label": (
        "new seizure-frequency label from the label forms, only when no "
        "single event is the answer; otherwise omit"
    ),
}


def _select_event_view(event: Mapping[str, Any]) -> dict[str, Any]:
    label = event.get("label")
    if label is None:
        label = event.get("designed_form_label")
    row: dict[str, Any] = {
        "event_id": str(event["event_id"]),
        "label": str(label) if label is not None else "",
        "kind": event.get("kind"),
        "temporality": event.get("temporality"),
        "assertion_status": event.get("assertion_status"),
        "applies_to": event.get("applies_to"),
        "time_window": event.get("time_window"),
        "evidence": str(event.get("evidence") or ""),
    }
    return {key: row[key] for key in _SELECT_EVENT_KEYS}


def build_llm_select_prompt_input(
    events: Sequence[Mapping[str, Any]],
    *,
    extract_selected_event_ids: Sequence[str],
    extract_label: str | None,
) -> str:
    """Build the later-stage select payload from labelled events."""

    payload = {
        "task": TASK,
        "instructions": list(INSTRUCTIONS),
        "cases": [
            {
                "title": row["title"],
                "instruction": row["instruction"],
                "example": {key: row["example"][key] for key in EXAMPLE_KEYS},
            }
            for row in CASES
        ],
        "label_forms": label_forms_payload(),
        "selection_schema": dict(SELECTION_SCHEMA),
        "first_choice": {
            "selected_event_ids": [str(item) for item in extract_selected_event_ids],
            "label": extract_label,
        },
        "events": [_select_event_view(event) for event in events],
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)
