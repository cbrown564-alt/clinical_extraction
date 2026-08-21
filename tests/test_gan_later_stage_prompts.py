"""Always-on contract for Gan later-stage encode and select prompts."""

from __future__ import annotations

import json

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
    assert "leave event_id unchanged" in blob.lower()
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
    assert payload["first_choice"] == {
        "selected_event_ids": ["e1"],
        "label": "≤ 4 per day",
    }
    assert "raw_value" not in blob
    assert "keep that first choice" in blob.lower()
    assert "usual gap between seizures" in blob.lower()
    assert "so far this year" in blob.lower()
    assert "recent count" in blob.lower()
    assert "not epileptic seizures" in blob.lower()
    assert "year-to-date" not in blob.lower()
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
    ):
        assert term not in lowered, term
