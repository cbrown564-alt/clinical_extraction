"""Always-on contract for the Gan codebook extract prompt."""

from __future__ import annotations

import json
from pathlib import Path

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
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_extract import (
    GAN_LLM_EXTRACT,
    LLM_EXTRACT_AUTHORED_KEYS,
    LLM_EXTRACT_TEMPLATE_KEYS,
    build_llm_extract_prompt_input,
    llm_extract_prompt_template,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_extract_raw import (
    EVENT_SCHEMA,
    SELECTION_SCHEMA,
    build_llm_extract_raw_prompt_input,
)

SUPPORTING_EXTRACT_TEMPLATE = (
    Path(__file__).resolve().parents[1]
    / "paper"
    / "supporting materials"
    / "gan_llm_extract_prompt_template.json"
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


def test_extract_template_omits_letter_and_research_metadata() -> None:
    template = llm_extract_prompt_template()
    payload = json.loads(build_llm_extract_prompt_input(_record()))
    assert tuple(template) == LLM_EXTRACT_TEMPLATE_KEYS
    assert "note_text" not in template
    assert "prompt_version" not in template
    assert template["label_forms"] == label_forms_payload()
    assert {**template, "note_text": _record().note_text} == payload


def test_supporting_extract_template_matches_living_prompt() -> None:
    on_disk = json.loads(SUPPORTING_EXTRACT_TEMPLATE.read_text(encoding="utf-8"))
    assert on_disk == llm_extract_prompt_template()


def test_extract_payload_keeps_events_source_near() -> None:
    payload = json.loads(build_llm_extract_prompt_input(_record()))
    blob = json.dumps(payload)
    assert set(payload) == set(LLM_EXTRACT_AUTHORED_KEYS)
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


def test_extract_does_not_change_raw_payload() -> None:
    baseline = json.loads(build_llm_extract_raw_prompt_input(_record()))
    assert "label_forms" not in baseline
    assert "may be a normalized label such as 1 per day" in json.dumps(baseline)


def test_hybrid_dispatch_keeps_default_extract_raw() -> None:
    default = json.loads(build_prompt_input(_record()))
    variant = json.loads(build_prompt_input(_record(), prompt_version=GAN_LLM_EXTRACT))
    assert "label_forms" not in default
    assert variant["label_forms"] == label_forms_payload()


def test_extract_verify_accepts_roster_models() -> None:
    payload = verify_gan("gan_llm_extract", "dev750", "gemini37flash")
    assert payload["ok"] is True
    assert payload["prompt_version"] == GAN_LLM_EXTRACT
    assert payload["row_policy"] == "development_review_permitted"
    holdout = verify_gan("gan_llm_extract", "test450", "gemini37flash")
    assert holdout["row_policy"] == "aggregate_only"
    assert holdout["holdout_scratch"].endswith("gan_llm_extract")
    for slug in ("grok46", "gpt56luna", "deepseek_v4_flash"):
        roster = verify_gan("gan_llm_extract", "dev750", slug)
        assert roster["ok"] is True
        assert roster["model_slug"] == slug
