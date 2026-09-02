"""Always-on contract for Gan later-stage encode and select prompts."""

from __future__ import annotations

import json

from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_label_forms import (
    label_forms_payload,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_encode import (
    LLM_ENCODE_AUTHORED_KEYS,
    build_llm_encode_prompt_input,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_select import (
    LLM_SELECT_AUTHORED_KEYS,
    build_llm_select_prompt_input,
)

_EXTRACT_EVENTS = [
    {
        "event_id": "e1",
        "kind": "frequency_rate",
        "raw_value": "≤ four per day",
        "applies_to": "seizures",
        "time_window": "current",
        "temporality": "current",
        "assertion_status": "asserted",
        "evidence": "≤ four per day, with variable clustering",
        "notes": "drop me",
    },
    {
        "event_id": "e2",
        "kind": "seizure_free",
        "raw_value": "seizure free for years",
        "applies_to": None,
        "time_window": "historical",
        "temporality": "historical",
        "assertion_status": "historical",
        "evidence": "was seizure free for years",
    },
]


def test_label_forms_describe_each_shape_without_sentinel() -> None:
    payload = label_forms_payload()
    forms = payload["forms"]
    names = [row["form"] for row in forms]
    assert "sentinels" not in names
    assert "sentinel" not in json.dumps(payload).lower()
    assert names.count("unknown") == 1
    assert names.count("no seizure frequency reference") == 1
    for row in forms:
        assert set(row) == {"form", "description", "examples"}
        assert row["description"].strip()
        assert row["examples"]


def test_encode_payload_is_label_only_join() -> None:
    payload = json.loads(build_llm_encode_prompt_input(_EXTRACT_EVENTS))
    blob = json.dumps(payload)
    assert set(payload) == set(LLM_ENCODE_AUTHORED_KEYS)
    assert "note_text" not in payload
    assert payload["events"] == [
        {
            "event_id": "e1",
            "stated_value": "≤ four per day",
            "evidence": "≤ four per day, with variable clustering",
        },
        {
            "event_id": "e2",
            "stated_value": "seizure free for years",
            "evidence": "was seizure free for years",
        },
    ]
    assert payload["label_forms"] == label_forms_payload()
    assert "leave event_id unchanged" in blob.lower()
    assert "1 cluster per 4 month, 5 per cluster" in blob
    assert "6 cluster per month, 4 per cluster" in blob
    assert "1 cluster per 4 to 5 day, 2 per cluster" in blob
    assert "seizure free for multiple month" in blob
    assert "unknown" in blob
    assert "no seizure frequency reference" in blob
    assert "4 per day" in blob
    _assert_no_internal_prompt_language(blob)


def test_select_payload_is_choose_ready_with_extract_hint() -> None:
    encoded = [
        {
            "event_id": "e1",
            "designed_form_label": "4 per day",
            "kind": "frequency_rate",
            "temporality": "current",
            "assertion_status": "asserted",
            "applies_to": "seizures",
            "time_window": "current",
            "evidence": "≤ four per day, with variable clustering",
            "raw_value": "must not appear",
        }
    ]
    payload = json.loads(
        build_llm_select_prompt_input(
            encoded,
            extract_selected_event_ids=["e1"],
            extract_label="≤ 4 per day",
        )
    )
    blob = json.dumps(payload)
    assert set(payload) == set(LLM_SELECT_AUTHORED_KEYS)
    assert "note_text" not in payload
    assert payload["events"] == [
        {
            "event_id": "e1",
            "label": "4 per day",
            "kind": "frequency_rate",
            "temporality": "current",
            "assertion_status": "asserted",
            "applies_to": "seizures",
            "time_window": "current",
            "evidence": "≤ four per day, with variable clustering",
        }
    ]
    assert payload["label_forms"] == label_forms_payload()
    assert payload["first_choice"] == {
        "selected_event_ids": ["e1"],
        "label": "≤ 4 per day",
    }
    assert "raw_value" not in blob
    assert "keep it unless one of the cases below" in blob.lower()
    assert "supporting quote" in blob.lower()
    assert "already in the events or their quotes" in blob.lower()
    cases = payload["cases"]
    assert len(cases) == 10
    titles = [row["title"] for row in cases]
    assert titles == [
        "Usual gap",
        "Usual rate, not a year total",
        "Recent seizures after a quiet spell",
        "Not epileptic seizures",
        "Month counts",
        "Dated seizures",
        "Burst after a change",
        "Short quiet spell after a last event",
        "Overall count",
        "Do not choose seizure-free while events continue",
    ]
    for row in cases:
        assert set(row) == {"title", "instruction", "example"}
        assert row["instruction"].strip()
        example = row["example"]
        assert set(example) == {"first_choice", "events", "answer"}
        assert example["first_choice"]["selected_event_ids"]
        assert "label" in example["first_choice"]
        assert len(example["events"]) >= 2
        for event in example["events"]:
            assert set(event) == {
                "event_id",
                "label",
                "kind",
                "temporality",
                "assertion_status",
                "applies_to",
                "time_window",
                "evidence",
            }
            assert event["event_id"]
            assert event["evidence"]
        assert example["answer"]["selected_event_ids"]
        chosen = set(example["first_choice"]["selected_event_ids"])
        event_ids = {event["event_id"] for event in example["events"]}
        assert chosen <= event_ids
        assert set(example["answer"]["selected_event_ids"]) <= event_ids
    assert "usual gap between seizures" in blob.lower()
    assert "so far this year" in blob.lower()
    assert "recent count" in blob.lower()
    assert "not epileptic seizures" in blob.lower()
    assert "seizure free for multiple year" in blob
    assert "named months" in blob.lower()
    assert "add those counts" in blob.lower()
    assert "4 months or longer" in blob.lower()
    assert "rate per day or per week" in blob.lower()
    assert "different dates or months" in blob.lower()
    assert "more than 1 month" in blob.lower()
    assert "before an improvement" in blob.lower()
    assert "current or recent" in blob.lower()
    assert "last seizure on a calendar day" in blob.lower()
    assert "fewer than 6 months" in blob.lower()
    assert "5 weeks or less" in blob.lower()
    assert "typically 1 per month" in blob.lower()
    assert "3 in march and 6 in may" in blob.lower()
    assert "12 march" in blob.lower()
    assert "four cases" not in blob.lower()
    assert "year-to-date" not in blob.lower()
    assert "current-state" not in blob.lower()
    assert "burden" not in blob.lower()
    assert "write no seizure frequency reference" not in blob.lower()
    assert "monthly_diary" not in blob.lower()
    assert "dated_sequence" not in blob.lower()
    assert "post_change_burst" not in blob.lower()
    assert "last_event_well_since" not in blob.lower()
    _assert_no_internal_prompt_language(blob)


def _assert_no_internal_prompt_language(blob: str) -> None:
    lowered = blob.lower()
    for term in (
        "extract pick",
        "extract_pick",
        "raw_value",
        "designed",
        "codebook",
        "frozen",
        "hybrid",
        "gold",
        "gan",
        "encode",
        "sentinel",
    ):
        assert term not in lowered, term
