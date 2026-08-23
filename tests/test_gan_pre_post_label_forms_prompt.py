"""Always-on contract for Gan both-extract."""

from __future__ import annotations

import json

import pytest

from clinical_extraction.paper.gan import verify_gan
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    prompt_llm_and_rules_extract as and_rules_extract,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    build_prompt_input,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_label_forms import (
    label_forms_payload,
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


def test_both_extract_keeps_suggested_rows_and_forms() -> None:
    payload = json.loads(
        and_rules_extract.build_llm_and_rules_extract_prompt_input(_record())
    )
    blob = json.dumps(payload)
    authored = and_rules_extract.LLM_AND_RULES_EXTRACT_AUTHORED_KEYS
    assert set(payload) == set(authored)
    assert payload["suggested_evidence"] == and_rules_extract.suggested_evidence_rows(
        _record()
    )
    assert payload["label_forms"] == label_forms_payload()
    assert "keep, reject, split, or merge" in blob
    assert "allowed forms" in blob.lower()
    assert "gold" not in blob.lower()
    assert "Gan 2026" not in blob


def test_hybrid_dispatch_both_extract_adds_forms() -> None:
    variant = json.loads(
        build_prompt_input(
            _record(),
            prompt_version=and_rules_extract.GAN_LLM_AND_RULES_EXTRACT,
        )
    )
    assert variant["label_forms"] == label_forms_payload()
    assert variant["suggested_evidence"]


def test_both_extract_verify_is_gemini_only() -> None:
    payload = verify_gan("gan_llm_and_rules_extract", "dev750", "gemini37flash")
    assert payload["ok"] is True
    assert payload["prompt_version"] == and_rules_extract.GAN_LLM_AND_RULES_EXTRACT
    holdout = verify_gan("gan_llm_and_rules_extract", "test450", "gemini37flash")
    assert holdout["row_policy"] == "aggregate_only"
    assert holdout["holdout_scratch"].endswith("gan_llm_and_rules_extract")
    with pytest.raises(RuntimeError, match="Gemini only"):
        verify_gan("gan_llm_and_rules_extract", "dev750", "grok46")
