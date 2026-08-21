"""Projection and parse contract for Gan later-stage encode and select."""

from __future__ import annotations

import pytest

from clinical_extraction.paper.gan import verify_gan
from clinical_extraction.paper.gan_later_stage import (
    parse_encode_labels,
    parse_select_answer,
    project_encode_label,
    project_select_label,
)


def test_encode_projects_the_extract_pick_label() -> None:
    assert (
        project_encode_label({"e1": "4 per day", "e2": "unknown"}, ["e1"]) == "4 per day"
    )


def test_select_uses_a_written_label_only_when_present() -> None:
    labels = {"e1": "4 per day", "e2": "1 per month"}
    assert project_select_label(labels, ["e2"], None) == "1 per month"
    assert project_select_label(labels, ["e1", "e2"], "2 per 6 month") == "2 per 6 month"


def test_parse_encode_and_select_payloads() -> None:
    assert parse_encode_labels(
        '{"labels": [{"event_id": "e1", "label": "4 per day"}]}'
    ) == [{"event_id": "e1", "label": "4 per day"}]
    assert parse_select_answer('{"selected_event_ids": ["e1"]}') == {
        "selected_event_ids": ["e1"]
    }
    assert parse_select_answer(
        '{"events": [], "selection": {"selected_event_ids": ["e2"], "label": "1 per month"}}'
    ) == {"selected_event_ids": ["e2"], "label": "1 per month"}


def test_later_stage_verify_is_gemini_only() -> None:
    assert verify_gan("gan_llm_encode", "dev750", "gemini37flash")["ok"] is True
    assert verify_gan("gan_llm_select", "dev750", "gemini37flash")["ok"] is True
    with pytest.raises(RuntimeError, match="Gemini only"):
        verify_gan("gan_llm_encode", "dev750", "grok46")
