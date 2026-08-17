"""Contract tests for retained v0.9.24 / v0.9.40 and study-only further prunes."""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from scripts.run_exectv2_v0924_ablation_luna_dev20 import verify_payload

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
_CHEAP_SCAFFOLD_KEYS = (
    "decision_procedure",
    "suggested_evidence",
    "categories",
)
_CHEAP_SLOP = (
    "source-near",
    "attention scaffolding",
    "annotation-facing",
    "component_ownership",
    "Gan structured",
    "deterministic ledger",
    "ontology",
    "trace strings",
    "final-justification",
    "SF precision",
    "SF recall",
    "SF state choice",
    "scorable",
    "ExECTv2",
    "anaphoric",
    "spell anchors",
    "used for scoring",
    "candidate_id",
    "sentence-diagnosis-trigger",
    "sentence-medication-trigger",
    "generic epilepsy companion",
    " emit",
    "Emit ",
    " SF ",
    "event lane",
    "patient-level",
    "bare modality",
)
_ENCODING_RULE = "LowerNumberOfSeizures"
_SCOPE_RULE = "Do not add a separate generic epilepsy diagnosis"
_SF_REFUSE_RULE = "Do not include SeizureFrequency for generic events"
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
    before = structured.PROMPT_VERSION
    payload = verify_payload()
    assert payload["ok"] is True
    assert payload["default_prompt_version"] == structured.PROMPT_VERSION_V0_9_24
    assert structured.PROMPT_VERSION == before == structured.PROMPT_VERSION_V0_9_24


def test_cheap_stack_drops_non_sf_encoding_and_all_examples() -> None:
    control = _payload(structured.PROMPT_VERSION_V0_9_24)
    payload = _payload(PROMPT_VERSION_V0_9_40_DROP_ENCODING_NON_SF_ALL_EXAMPLES)
    blob = json.dumps(payload)
    assert "worked_examples" not in payload
    assert "architecture" not in payload
    assert "candidate_evidence_ledger" not in payload
    assert "event_lane_guide" not in payload
    assert _EXAMPLE_09 not in blob
    leaked = [phrase for phrase in _CHEAP_SLOP if phrase in blob]
    assert leaked == []
    rules = " ".join(payload["clinical_rules"])
    assert _DX_ENCODING_RULE not in rules
    assert _ENCODING_RULE in rules
    assert _SF_REFUSE_RULE in rules
    assert _SCOPE_RULE in rules
    assert len(payload["clinical_rules"]) == 67
    for key in _CHEAP_SCAFFOLD_KEYS:
        assert key in payload
    assert payload["suggested_evidence"]
    row = payload["suggested_evidence"][0]
    assert set(row) == {"family", "evidence", "name_hint", "category"}
    assert "source" not in row
    assert "candidate_id" not in row
    assert "lane_hint" not in row
    assert "anchor_hint" not in row
    assert "architecture" in control
    assert "source-near" in json.dumps(control)
    assert structured.PROMPT_VERSION == structured.PROMPT_VERSION_V0_9_24


_IX_PENDING_DROPPED = (
    "Completed historical tests and tests with results include Investigations",
    "Do not include future planned, requested, repeat, or follow-up investigations",
    "Never include an Investigations mention whose only support is pending-test",
)
_IX_PENDING_KEPT = (
    "If the test sentence contains 'will'",
    "Do not include a bare test-name-only investigation",
)
_REFUSE_DROPPED = (
    "Do not include vague symptoms, blackout/loss-of-consciousness",
    "Do not include isolated symptoms or aura features as Diagnosis",
    "A problem-list or Diagnosis header is not enough by itself",
    "Do not include SeizureFrequency for generic events, blackouts",
    "Reject vague words such as 'events', 'episodes'",
    "Do not include childhood febrile seizures, family-history seizures",
    "Do not include risk or counselling statements",
    "Do not include non-epileptic or diagnostically vague episode descriptions",
    "Do not include old or contextual minor-seizure episode phrases",
    "Do not include safety-advice, conditional, or instructional statements",
)
_REFUSE_KEPT = (
    "Do not include negated resemblance statements",
    "Do not use a pointing phrase",
    "Do not include a bare seizure-free",
    "remains seizure free and is now driving",
)
_COMBINED_REFUSE = (
    "unless the letter explicitly states that phrase is an epileptic seizure"
)
_CATEGORY_REPRINT = (
    "First classify each suggested-evidence row into a category:"
)


def test_further_prune_arms_are_one_cut_each() -> None:
    cheap = _payload(PROMPT_VERSION_V0_9_40_DROP_ENCODING_NON_SF_ALL_EXAMPLES)
    ix_pending = _payload(structured.PROMPT_VERSION_V0_9_41_CHEAP_DROP_IX_PENDING_REPEAT)
    scaffold = _payload(structured.PROMPT_VERSION_V0_9_42_CHEAP_DROP_SCAFFOLD_REPRINT)
    refuse = _payload(structured.PROMPT_VERSION_V0_9_43_CHEAP_COLLAPSE_REFUSE)

    cheap_rules = " ".join(cheap["clinical_rules"])
    ix_rules = " ".join(ix_pending["clinical_rules"])
    scaffold_rules = " ".join(scaffold["clinical_rules"])
    refuse_rules = " ".join(refuse["clinical_rules"])

    assert structured.PROMPT_VERSION == structured.PROMPT_VERSION_V0_9_24
    assert len(cheap["clinical_rules"]) == 67
    assert cheap["prompt_version"] == PROMPT_VERSION_V0_9_40_DROP_ENCODING_NON_SF_ALL_EXAMPLES
    assert "letter_id" in cheap
    assert _CATEGORY_REPRINT in cheap_rules
    for phrase in _IX_PENDING_DROPPED + _REFUSE_DROPPED:
        assert phrase in cheap_rules

    assert len(ix_pending["clinical_rules"]) == 64
    assert ix_pending["prompt_version"].endswith("ix_pending_repeat")
    for phrase in _IX_PENDING_DROPPED:
        assert phrase not in ix_rules
    for phrase in _IX_PENDING_KEPT + _REFUSE_DROPPED:
        assert phrase in ix_rules
    assert _CATEGORY_REPRINT in ix_rules
    assert "letter_id" in ix_pending

    assert len(scaffold["clinical_rules"]) == 66
    assert "prompt_version" not in scaffold
    assert "letter_id" not in scaffold
    assert _CATEGORY_REPRINT not in scaffold_rules
    assert "categories" in scaffold
    assert scaffold["suggested_evidence"]
    assert len(scaffold["decision_procedure"]) == 3
    for phrase in _IX_PENDING_DROPPED + _REFUSE_DROPPED:
        assert phrase in scaffold_rules

    assert len(refuse["clinical_rules"]) == 58
    assert refuse["prompt_version"].endswith("collapse_refuse")
    assert _COMBINED_REFUSE in refuse_rules
    for phrase in _REFUSE_DROPPED:
        assert phrase not in refuse_rules
    for phrase in _REFUSE_KEPT + _IX_PENDING_DROPPED:
        assert phrase in refuse_rules
    assert _CATEGORY_REPRINT in refuse_rules
    assert "cui" not in json.dumps(ix_pending).lower()
    assert "cui" not in json.dumps(scaffold).lower()
    assert "cui" not in json.dumps(refuse).lower()
    assert structured.PROMPT_VERSION == structured.PROMPT_VERSION_V0_9_24


_COMBO_NAME_SENTENCE = (
    'If the letter says "2 to 3 focal seizures a week", the mention text is '
    "focal seizures. The \"2 to 3\" and the \"week\" go in attributes, not in "
    "mention text."
)


def test_combo_clinical_name_adds_one_sentence_to_cheap_stack() -> None:
    cheap = _payload(PROMPT_VERSION_V0_9_40_DROP_ENCODING_NON_SF_ALL_EXAMPLES)
    payload = _payload(structured.PROMPT_VERSION_V0_9_40_COMBO_CLINICAL_NAME)
    assert structured.PROMPT_VERSION == structured.PROMPT_VERSION_V0_9_24
    assert payload["prompt_version"] == structured.PROMPT_VERSION_V0_9_40_COMBO_CLINICAL_NAME
    assert _COMBO_NAME_SENTENCE not in cheap["task"]
    assert cheap["task"] in payload["task"]
    assert payload["task"].endswith(_COMBO_NAME_SENTENCE)
    assert payload["clinical_rules"] == cheap["clinical_rules"]
    assert payload["family_guidance"] == cheap["family_guidance"]
    assert "worked_examples" not in payload
    assert _COMBO_NAME_SENTENCE not in json.dumps(cheap)
    assert structured.PROMPT_VERSION == structured.PROMPT_VERSION_V0_9_24


def test_stacked_further_prune_applies_all_three_cuts() -> None:
    cheap = _payload(PROMPT_VERSION_V0_9_40_DROP_ENCODING_NON_SF_ALL_EXAMPLES)
    stacked = _payload(structured.PROMPT_VERSION_V0_9_44_CHEAP_STACK_FURTHER_PRUNES)
    cheap_rules = " ".join(cheap["clinical_rules"])
    stacked_rules = " ".join(stacked["clinical_rules"])

    assert structured.PROMPT_VERSION == structured.PROMPT_VERSION_V0_9_24
    assert len(cheap["clinical_rules"]) == 67
    assert len(stacked["clinical_rules"]) == 54
    assert "prompt_version" not in stacked
    assert "letter_id" not in stacked
    assert len(stacked["decision_procedure"]) == 3
    assert "categories" in stacked
    assert stacked["suggested_evidence"]
    assert _CATEGORY_REPRINT in cheap_rules
    assert _CATEGORY_REPRINT not in stacked_rules
    assert _COMBINED_REFUSE in stacked_rules
    for phrase in _IX_PENDING_DROPPED + _REFUSE_DROPPED:
        assert phrase in cheap_rules
        assert phrase not in stacked_rules
    for phrase in _IX_PENDING_KEPT + _REFUSE_KEPT:
        assert phrase in stacked_rules
    assert "cui" not in json.dumps(stacked).lower()
    assert structured.PROMPT_VERSION == structured.PROMPT_VERSION_V0_9_24
