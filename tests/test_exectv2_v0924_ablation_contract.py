"""Contract tests for v0.9.24 leave-one-out prompt ablations."""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)

PROMPT_VERSION_V0_9_26_DROP_SCAFFOLD = structured.PROMPT_VERSION_V0_9_26_DROP_SCAFFOLD
PROMPT_VERSION_V0_9_27_DROP_EXAMPLES = structured.PROMPT_VERSION_V0_9_27_DROP_EXAMPLES
PROMPT_VERSION_V0_9_28_DROP_ENCODING_RULES = (
    structured.PROMPT_VERSION_V0_9_28_DROP_ENCODING_RULES
)
PROMPT_VERSION_V0_9_29_DROP_SCOPE_RULES = structured.PROMPT_VERSION_V0_9_29_DROP_SCOPE_RULES

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
_LEDGER_RULE = "First classify each candidate_evidence_ledger item"
_ENCODING_RULE = "LowerNumberOfSeizures and UpperNumberOfSeizures"
_SCOPE_RULE = "Do not add a generic epilepsy companion"
_EXAMPLE_09 = "several seizures since the last clinic appointment"


def _payload(version: str) -> dict:
    return json.loads(structured.build_prompt_input(_LETTER, prompt_version=version))


def _control() -> dict:
    return _payload(structured.PROMPT_VERSION_V0_9_24)


def test_default_prompt_stays_v0924() -> None:
    assert structured.PROMPT_VERSION == structured.PROMPT_VERSION_V0_9_24
    payload = json.loads(structured.build_prompt_input(_LETTER))
    assert payload["prompt_version"] == structured.PROMPT_VERSION_V0_9_24
    assert len(payload["clinical_rules"]) == 83
    assert len(payload["worked_examples"]) == 49


def test_drop_scaffold_removes_only_attention_blocks() -> None:
    control = _control()
    payload = _payload(PROMPT_VERSION_V0_9_26_DROP_SCAFFOLD)
    assert payload["prompt_version"] == PROMPT_VERSION_V0_9_26_DROP_SCAFFOLD
    for key in _SCAFFOLD_KEYS:
        assert key not in payload
        assert key in control
    assert "candidate_evidence_ledger" not in payload["task"]
    assert _LEDGER_RULE not in " ".join(payload["clinical_rules"])
    assert len(payload["clinical_rules"]) == 79
    assert len(payload["worked_examples"]) == 49
    assert _ENCODING_RULE in " ".join(payload["clinical_rules"])
    assert _SCOPE_RULE in " ".join(payload["clinical_rules"])
    assert structured.PROMPT_VERSION == structured.PROMPT_VERSION_V0_9_24


def test_drop_examples_removes_only_worked_examples() -> None:
    payload = _payload(PROMPT_VERSION_V0_9_27_DROP_EXAMPLES)
    assert "worked_examples" not in payload
    assert _EXAMPLE_09 not in json.dumps(payload)
    assert len(payload["clinical_rules"]) == 83
    for key in _SCAFFOLD_KEYS:
        assert key in payload
    assert _LEDGER_RULE in " ".join(payload["clinical_rules"])
    assert structured.PROMPT_VERSION == structured.PROMPT_VERSION_V0_9_24


def test_drop_encoding_removes_only_encoding_rules() -> None:
    payload = _payload(PROMPT_VERSION_V0_9_28_DROP_ENCODING_RULES)
    rules = " ".join(payload["clinical_rules"])
    assert _ENCODING_RULE not in rules
    assert _SCOPE_RULE in rules
    assert _LEDGER_RULE in rules
    assert len(payload["clinical_rules"]) == 54
    assert len(payload["worked_examples"]) == 49
    for key in _SCAFFOLD_KEYS:
        assert key in payload
    assert structured.PROMPT_VERSION == structured.PROMPT_VERSION_V0_9_24


def test_drop_scope_removes_only_scope_rules() -> None:
    payload = _payload(PROMPT_VERSION_V0_9_29_DROP_SCOPE_RULES)
    rules = " ".join(payload["clinical_rules"])
    assert _SCOPE_RULE not in rules
    assert _ENCODING_RULE in rules
    assert len(payload["clinical_rules"]) == 58
    assert len(payload["worked_examples"]) == 49
    for key in _SCAFFOLD_KEYS:
        assert key in payload
    assert structured.PROMPT_VERSION == structured.PROMPT_VERSION_V0_9_24


def test_ablation_check_does_not_change_default() -> None:
    from scripts.run_exectv2_v0924_ablation_luna_dev20 import verify_payload

    before = structured.PROMPT_VERSION
    payload = verify_payload()
    assert payload["ok"] is True
    assert payload["default_prompt_version"] == structured.PROMPT_VERSION_V0_9_24
    assert structured.PROMPT_VERSION == before == structured.PROMPT_VERSION_V0_9_24


def test_each_ablation_is_leave_one_out() -> None:
    payload = _payload(PROMPT_VERSION_V0_9_26_DROP_SCAFFOLD)
    assert "worked_examples" in payload
    examples = _payload(PROMPT_VERSION_V0_9_27_DROP_EXAMPLES)
    assert examples["architecture"]["name"] == "single hybrid key-family event ledger"
    encoding = _payload(PROMPT_VERSION_V0_9_28_DROP_ENCODING_RULES)
    assert encoding["worked_examples"]
    scope = _payload(PROMPT_VERSION_V0_9_29_DROP_SCOPE_RULES)
    assert scope["worked_examples"]
