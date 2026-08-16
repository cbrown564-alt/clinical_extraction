"""Contract tests for retained v0.9.24 / v0.9.40 structured prompts."""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)

PROMPT_VERSION_V0_9_40_DROP_ENCODING_NON_SF_ALL_EXAMPLES = (
    structured.PROMPT_VERSION_V0_9_40_DROP_ENCODING_NON_SF_ALL_EXAMPLES
)

_LETTER = ExectLetter(
    letter_id="TEST001",
    note_text=(
        "She has focal epilepsy with 2 focal seizures per month. "
        "Current treatment is lamotrigine 200 mg twice daily. "
        "MRI brain was normal."
    ),
)
_SCAFFOLD_KEYS = (
    "architecture",
    "decision_procedure",
    "candidate_evidence_ledger",
    "event_lane_guide",
)
_ENCODING_RULE = "LowerNumberOfSeizures"
_SCOPE_RULE = "Do not add a generic epilepsy companion"
_SF_REFUSE_RULE = "Do not render SeizureFrequency for generic events"
_DX_ENCODING_RULE = "Every Diagnosis mention must include Certainty"
_EXAMPLE_09 = "several seizures since the last clinic appointment"


def _payload(version: str) -> dict:
    return json.loads(structured.build_prompt_input(_LETTER, prompt_version=version))


def test_default_prompt_stays_v0924() -> None:
    assert structured.PROMPT_VERSION == structured.PROMPT_VERSION_V0_9_24
    payload = json.loads(structured.build_prompt_input(_LETTER))
    assert payload["prompt_version"] == structured.PROMPT_VERSION_V0_9_24
    assert len(payload["clinical_rules"]) == 83
    assert len(payload["worked_examples"]) == 49


def test_ablation_check_does_not_change_default() -> None:
    from scripts.run_exectv2_v0924_ablation_luna_dev20 import verify_payload

    before = structured.PROMPT_VERSION
    payload = verify_payload()
    assert payload["ok"] is True
    assert payload["default_prompt_version"] == structured.PROMPT_VERSION_V0_9_24
    assert structured.PROMPT_VERSION == before == structured.PROMPT_VERSION_V0_9_24


def test_cheap_stack_drops_non_sf_encoding_and_all_examples() -> None:
    payload = _payload(PROMPT_VERSION_V0_9_40_DROP_ENCODING_NON_SF_ALL_EXAMPLES)
    assert "worked_examples" not in payload
    assert _EXAMPLE_09 not in json.dumps(payload)
    rules = " ".join(payload["clinical_rules"])
    assert _DX_ENCODING_RULE not in rules
    assert _ENCODING_RULE in rules
    assert _SF_REFUSE_RULE in rules
    assert _SCOPE_RULE in rules
    assert len(payload["clinical_rules"]) == 67
    for key in _SCAFFOLD_KEYS:
        assert key in payload
    assert structured.PROMPT_VERSION == structured.PROMPT_VERSION_V0_9_24
