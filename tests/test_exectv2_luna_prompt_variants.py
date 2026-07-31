"""Selectable Luna ExECT prompt variants keep schema frozen and default intact."""

from __future__ import annotations

import json

import pytest

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)

_LETTER = ExectLetter(
    letter_id="TEST_LUNA",
    note_text=(
        "Known focal epilepsy. Two seizures per month. Last seizure yesterday. "
        "Continues levetiracetam 500 mg twice daily."
    ),
)


def test_default_prompt_version_remains_v0_9_24() -> None:
    assert structured.PROMPT_VERSION == structured.PROMPT_VERSION_V0_9_24
    payload = json.loads(structured.build_prompt_input(_LETTER))
    assert payload["prompt_version"] == structured.PROMPT_VERSION_V0_9_24
    assert "extra_clinical_guidance" not in payload


@pytest.mark.parametrize(
    ("version", "needle"),
    [
        (
            structured.PROMPT_VERSION_V0_9_25_LUNA_SF_STATE,
            "Do not also invent a seizure-free mention",
        ),
        (
            structured.PROMPT_VERSION_V0_9_25_LUNA_SF_BOUNDARY_DX,
            "prefer the most specific syndrome",
        ),
    ],
)
def test_luna_variants_add_guidance_without_schema_change(
    version: str,
    needle: str,
) -> None:
    control = json.loads(structured.build_prompt_input(_LETTER))
    payload = json.loads(
        structured.build_prompt_input(_LETTER, prompt_version=version)
    )
    assert payload["prompt_version"] == version
    assert payload["output_schema"] == control["output_schema"]
    assert payload["attribute_vocabulary"] == control["attribute_vocabulary"]
    guidance = " ".join(payload["extra_clinical_guidance"])
    assert needle in guidance
    assert "gold" not in guidance.lower()
    assert "dev140" not in guidance.lower()
    assert "scorer" not in guidance.lower()


def test_set_active_prompt_version_round_trip() -> None:
    original = structured.PROMPT_VERSION
    try:
        structured.set_active_prompt_version(
            structured.PROMPT_VERSION_V0_9_25_LUNA_SF_STATE
        )
        payload = json.loads(structured.build_prompt_input(_LETTER))
        assert (
            payload["prompt_version"]
            == structured.PROMPT_VERSION_V0_9_25_LUNA_SF_STATE
        )
    finally:
        structured.set_active_prompt_version(original)
