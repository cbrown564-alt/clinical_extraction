"""Always-on contract for one-call find, encode, and select."""

from __future__ import annotations

import json

from clinical_extraction.paper.gan import verify_gan
from clinical_extraction.paper.methods import LIVE_METHODS
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    prompt_llm_extract_encode_select as extract_encode_select,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    build_prompt_input,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_extract import (
    llm_extract_prompt_template,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_select import (
    CASE_KEYS,
    EXAMPLE_KEYS,
    select_cases_payload,
)


def _record() -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=10,
        note_text="Present seizure frequency: two seizures per month.",
        gold_label="2 per month",
        gold_reference="two seizures per month",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label="2 per month",
        gold_label_kind=FrequencyLabelKind.FREQUENCY,
        gold_yearly_bounds=(24.0, 24.0),
        gold_monthly_frequency=2.0,
    )


def test_one_call_keeps_extract_and_adds_living_select_cases() -> None:
    baseline = llm_extract_prompt_template()
    variant = extract_encode_select.llm_extract_encode_select_prompt_template()
    cases = select_cases_payload()
    assert variant["task"] == baseline["task"]
    assert variant["event_schema"] == baseline["event_schema"]
    assert variant["selection_schema"] == baseline["selection_schema"]
    assert variant["label_forms"] == baseline["label_forms"]
    assert variant["instructions"][: len(baseline["instructions"])] == baseline[
        "instructions"
    ]
    assert variant["instructions"][-1] == extract_encode_select.SELECT_BRIDGE
    assert variant["cases"] == cases
    assert [row["title"] for row in cases] == [
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
    for row in variant["cases"]:
        assert set(row) == set(CASE_KEYS)
        assert set(row["example"]) == set(EXAMPLE_KEYS)


def test_one_call_payload_is_model_facing_and_registered() -> None:
    payload = json.loads(
        build_prompt_input(
            _record(),
            prompt_version=extract_encode_select.GAN_LLM_EXTRACT_ENCODE_SELECT,
        )
    )
    blob = json.dumps(payload)
    assert set(payload) == set(
        extract_encode_select.LLM_EXTRACT_ENCODE_SELECT_AUTHORED_KEYS
    )
    assert payload["note_text"] == _record().note_text
    assert "prompt_version" not in payload
    assert "source_row_index" not in payload
    assert "Gan 2026" not in blob
    assert "gan_llm" not in blob
    assert "codebook" not in blob.lower()
    assert "benchmark" not in blob.lower()
    assert LIVE_METHODS["gan_llm_extract_encode_select"]["paper_cell"] is False
    verified = verify_gan(
        "gan_llm_extract_encode_select", "test450", "gemini37flash"
    )
    assert verified["ok"] is True
    assert verified["row_policy"] == "aggregate_only"
    assert verified["prompt_version"] == (
        extract_encode_select.GAN_LLM_EXTRACT_ENCODE_SELECT
    )
