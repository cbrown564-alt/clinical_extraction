"""Always-on contract for the Gan extract label-forms prompt."""

from __future__ import annotations

import json

import pytest

from clinical_extraction.paper.gan import verify_gan
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    build_prompt_input,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_label_forms import (
    label_forms_payload,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_extract_label_forms import (
    GAN_LLM_EXTRACT_LABEL_FORMS,
    LLM_EXTRACT_LABEL_FORMS_AUTHORED_KEYS,
    build_llm_extract_label_forms_prompt_input,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_with_rules import (
    EVENT_SCHEMA,
    SELECTION_SCHEMA,
    build_llm_with_rules_prompt_input,
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


def test_extract_label_forms_payload_keeps_events_source_near() -> None:
    payload = json.loads(build_llm_extract_label_forms_prompt_input(_record()))
    blob = json.dumps(payload)
    assert set(payload) == set(LLM_EXTRACT_LABEL_FORMS_AUTHORED_KEYS)
    assert payload["event_schema"] == EVENT_SCHEMA
    assert payload["selection_schema"] == SELECTION_SCHEMA
    assert payload["label_forms"] == label_forms_payload()
    assert payload["note_text"] == _record().note_text
    assert "allowed forms" in blob.lower()
    assert "raw_value" in blob
    assert "1 cluster per 4 month, 5 per cluster" in blob
    assert "gold" not in blob.lower()
    assert "Gan 2026" not in blob
    assert "prompt_version" not in payload
    assert "source_row_index" not in payload


def test_extract_label_forms_does_not_change_with_rules_payload() -> None:
    baseline = json.loads(build_llm_with_rules_prompt_input(_record()))
    assert "label_forms" not in baseline
    assert "may be a normalized label such as 1 per day" in json.dumps(baseline)


def test_hybrid_dispatch_keeps_default_with_rules() -> None:
    default = json.loads(build_prompt_input(_record()))
    variant = json.loads(
        build_prompt_input(_record(), prompt_version=GAN_LLM_EXTRACT_LABEL_FORMS)
    )
    assert "label_forms" not in default
    assert variant["label_forms"] == label_forms_payload()


def test_extract_label_forms_verify_is_gemini_only() -> None:
    payload = verify_gan("gan_llm_extract_label_forms", "dev750", "gemini37flash")
    assert payload["ok"] is True
    assert payload["prompt_version"] == GAN_LLM_EXTRACT_LABEL_FORMS
    assert payload["row_policy"] == "development_review_permitted"
    holdout = verify_gan("gan_llm_extract_label_forms", "test450", "gemini37flash")
    assert holdout["row_policy"] == "aggregate_only"
    assert holdout["holdout_scratch"].endswith("gan_llm_extract_label_forms")
    with pytest.raises(RuntimeError, match="Gemini only"):
        verify_gan("gan_llm_extract_label_forms", "dev750", "grok46")
