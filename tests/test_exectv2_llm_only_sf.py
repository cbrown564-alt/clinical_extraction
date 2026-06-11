"""Tests for the ExECTv2 LLM-only SeizureFrequency extractors.

Covers:
  - Prompt hygiene: no internal architecture vocabulary in model-facing strings
  - parse_extraction_json: valid JSON → ExtractionRecord, invalid → error list
  - repair_attributes: illegal keys/values stripped with warnings
  - check_evidence: non-substring evidence dropped, valid evidence kept
  - to_predicted_letter: adapter produces correct PredictedLetter shape
"""

from __future__ import annotations

import json

import pytest

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    ENTITY_REGISTRY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    SEIZURE_FREQUENCY,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_per_entity,
    llm_only_single_pass,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_per_entity import (
    ExECTv2PerEntitySFSignature,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    ExECTv2SinglePassSFSignature,
    ExtractionRecord,
    MentionRecord,
    check_evidence,
    parse_extraction_json,
    repair_attributes,
    to_predicted_letter,
)

# ── Fixtures ──────────────────────────────────────────────────────────────────

_NOTE = (
    "This lady is a 42-year-old with focal epilepsy. "
    "She reports approximately 2 seizures per month, down from 4 per month "
    "before the medication change. She has been seizure free for 3 months "
    "following the last dose adjustment."
)

_LETTER = ExectLetter(letter_id="TEST001", note_text=_NOTE)

_SF_SPEC = ENTITY_REGISTRY[SEIZURE_FREQUENCY]

# ── Prompt hygiene ────────────────────────────────────────────────────────────

FORBIDDEN_PHRASES = (
    "Decision 000",
    "decision 000",
    "deterministic code",
    "downstream deterministic",
    "architecture gate",
    "deterministic candidates",
    "gold labels",
    "gold_label",
    "parser-ready",
    "scorer-facing",
    "scoring-facing",
    "benchmark",
    "synthetic",
    "prompt_policy_taxonomy",
    " -> ",
)


@pytest.mark.parametrize(
    ("name", "builder"),
    [
        ("single_pass", llm_only_single_pass.build_prompt_input),
        ("per_entity", llm_only_per_entity.build_prompt_input),
    ],
)
def test_prompt_hygiene_no_internal_vocabulary(name: str, builder) -> None:
    payload = builder(_LETTER)
    text = payload if isinstance(payload, str) else json.dumps(payload)
    leaked = [phrase for phrase in FORBIDDEN_PHRASES if phrase in text]
    assert leaked == [], f"{name}: leaked internal phrases {leaked}"


# ── parse_extraction_json ─────────────────────────────────────────────────────


def test_parse_valid_json_returns_extraction_record() -> None:
    raw = json.dumps({
        "mentions": [
            {
                "text": "2 seizures per month",
                "attributes": {
                    "NumberOfSeizures": "2",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Month",
                },
                "evidence": "2 seizures per month",
                "confidence": "high",
                "rationale": "The note states 2 seizures per month.",
            }
        ]
    })
    record, errors = parse_extraction_json(raw)
    assert record is not None
    assert len(record.mentions) == 1
    assert record.mentions[0].text == "2 seizures per month"
    assert not any(e.startswith(("invalid_json:", "schema_validation_error:")) for e in errors)


def test_parse_empty_mentions_is_valid() -> None:
    raw = json.dumps({"mentions": []})
    record, errors = parse_extraction_json(raw)
    assert record is not None
    assert record.mentions == []
    assert not any(e.startswith(("invalid_json:", "schema_validation_error:")) for e in errors)


def test_parse_invalid_json_returns_none_and_error() -> None:
    record, errors = parse_extraction_json("not json at all {")
    assert record is None
    assert any(e.startswith("invalid_json:") for e in errors)


def test_parse_missing_mentions_key_defaults_to_empty() -> None:
    # ExtractionRecord has default mentions=[]; extra keys are ignored
    raw = json.dumps({"other_key": "ignored"})
    record, errors = parse_extraction_json(raw)
    assert record is not None
    assert record.mentions == []


def test_parse_numeric_attribute_values_are_coerced_to_strings() -> None:
    raw = json.dumps({
        "mentions": [
            {
                "text": "2 per month",
                "attributes": {"NumberOfSeizures": 2, "NumberOfTimePeriods": 1},
                "evidence": "2 per month",
                "confidence": "high",
                "rationale": "Two per month.",
            }
        ]
    })
    record, errors = parse_extraction_json(raw)
    assert record is not None
    assert record.mentions[0].attributes["NumberOfSeizures"] == "2"
    assert any("coerced_attribute_value" in e for e in errors)


def test_parse_fenced_json_is_extracted() -> None:
    raw = '```json\n{"mentions": []}\n```'
    record, errors = parse_extraction_json(raw)
    assert record is not None
    assert record.mentions == []


def test_parse_not_run_sentinel() -> None:
    record, errors = parse_extraction_json("")
    # empty string → not_run via the caller; direct parse gives invalid_json
    assert record is None


# ── repair_attributes ─────────────────────────────────────────────────────────


def test_repair_attributes_keeps_legal_attributes() -> None:
    attrs = {"NumberOfSeizures": "2", "TimePeriod": "Month", "NumberOfTimePeriods": "1"}
    repaired, warnings = repair_attributes(attrs, spec=_SF_SPEC)
    assert repaired == attrs
    assert warnings == []


def test_repair_attributes_drops_illegal_key() -> None:
    attrs = {"NumberOfSeizures": "2", "IllegalKey": "foo"}
    repaired, warnings = repair_attributes(attrs, spec=_SF_SPEC)
    assert "IllegalKey" not in repaired
    assert "NumberOfSeizures" in repaired
    assert any("dropped_illegal_attribute" in w for w in warnings)


def test_repair_attributes_drops_illegal_closed_vocab_value() -> None:
    # TimePeriod only accepts Day/Week/Month/Year/days
    attrs = {"TimePeriod": "Fortnight"}
    repaired, warnings = repair_attributes(attrs, spec=_SF_SPEC)
    assert "TimePeriod" not in repaired
    assert any("dropped_illegal_value" in w for w in warnings)


def test_repair_attributes_accepts_legal_closed_vocab_value() -> None:
    attrs = {"TimePeriod": "Week", "FrequencyChange": "Decreased"}
    repaired, warnings = repair_attributes(attrs, spec=_SF_SPEC)
    assert repaired["TimePeriod"] == "Week"
    assert repaired["FrequencyChange"] == "Decreased"
    assert warnings == []


def test_repair_attributes_skips_noise_attributes_silently() -> None:
    # DiagCategory is a noise attribute on SF
    attrs = {"NumberOfSeizures": "2", "DiagCategory": "Epilepsy"}
    repaired, warnings = repair_attributes(attrs, spec=_SF_SPEC)
    assert "DiagCategory" not in repaired
    assert "NumberOfSeizures" in repaired
    # noise attributes are silently dropped — no warning
    assert not any("DiagCategory" in w for w in warnings)


# ── check_evidence ────────────────────────────────────────────────────────────


def _make_mention(text: str, evidence: str) -> MentionRecord:
    return MentionRecord(
        text=text,
        attributes={},
        evidence=evidence,
        confidence="high",
        rationale="test",
    )


def test_check_evidence_valid_substring_is_kept() -> None:
    mention = _make_mention("2 seizures per month", "2 seizures per month")
    valid, invalid, warnings = check_evidence([mention], note_text=_NOTE)
    assert len(valid) == 1
    assert len(invalid) == 0
    assert warnings == []


def test_check_evidence_non_substring_is_dropped() -> None:
    mention = _make_mention("fabricated phrase", "fabricated phrase")
    valid, invalid, warnings = check_evidence([mention], note_text=_NOTE)
    assert len(valid) == 0
    assert len(invalid) == 1
    assert any("dropped_evidence_not_substring" in w for w in warnings)


def test_check_evidence_empty_evidence_is_dropped() -> None:
    mention = _make_mention("some phrase", "")
    valid, invalid, warnings = check_evidence([mention], note_text=_NOTE)
    assert len(valid) == 0
    assert len(invalid) == 1
    assert any("dropped_empty_evidence" in w for w in warnings)


def test_check_evidence_mixed_batch() -> None:
    mentions = [
        _make_mention("2 seizures per month", "2 seizures per month"),  # valid
        _make_mention("ghost phrase", "ghost phrase"),                  # invalid
        _make_mention("seizure free for 3 months", "seizure free for 3 months"),  # valid
    ]
    valid, invalid, _ = check_evidence(mentions, note_text=_NOTE)
    assert len(valid) == 2
    assert len(invalid) == 1


# ── to_predicted_letter ───────────────────────────────────────────────────────


def test_to_predicted_letter_produces_correct_shape() -> None:
    mentions = [
        MentionRecord(
            text="2 seizures per month",
            attributes={"NumberOfSeizures": "2", "TimePeriod": "Month"},
            evidence="2 seizures per month",
            confidence="high",
            rationale="Stated directly.",
        )
    ]
    letter, warnings = to_predicted_letter(
        "TEST001", mentions, spec=_SF_SPEC, note_text=_NOTE
    )
    assert letter.letter_id == "TEST001"
    assert len(letter.mentions) == 1
    m = letter.mentions[0]
    assert m.entity == SEIZURE_FREQUENCY
    assert m.text == "2 seizures per month"
    assert m.attributes["NumberOfSeizures"] == "2"
    assert m.confidence == "high"
    assert m.component_owner == "llm_only_single_pass"


def test_to_predicted_letter_drops_evidence_invalid_mentions() -> None:
    mentions = [
        MentionRecord(
            text="valid phrase",
            attributes={},
            evidence="2 seizures per month",  # valid substring
            confidence="high",
            rationale="ok",
        ),
        MentionRecord(
            text="hallucinated phrase",
            attributes={},
            evidence="this text is not in the note at all",  # invalid
            confidence="low",
            rationale="bad",
        ),
    ]
    letter, warnings = to_predicted_letter(
        "TEST001", mentions, spec=_SF_SPEC, note_text=_NOTE
    )
    assert len(letter.mentions) == 1
    assert letter.mentions[0].text == "valid phrase"
    assert any("dropped" in w for w in warnings)


def test_to_predicted_letter_strips_illegal_attributes() -> None:
    mentions = [
        MentionRecord(
            text="2 seizures per month",
            attributes={"NumberOfSeizures": "2", "BadAttr": "x"},
            evidence="2 seizures per month",
            confidence="high",
            rationale="ok",
        )
    ]
    letter, warnings = to_predicted_letter(
        "TEST001", mentions, spec=_SF_SPEC, note_text=_NOTE
    )
    assert len(letter.mentions) == 1
    assert "BadAttr" not in letter.mentions[0].attributes
    assert any("dropped_illegal_attribute" in w for w in warnings)


# ── Prompt content sanity ─────────────────────────────────────────────────────


def test_single_pass_prompt_contains_letter_text() -> None:
    payload_str = llm_only_single_pass.build_prompt_input(_LETTER)
    payload = json.loads(payload_str)
    assert payload["letter_text"] == _NOTE


def test_per_entity_prompt_contains_letter_text() -> None:
    payload_str = llm_only_per_entity.build_prompt_input(_LETTER)
    payload = json.loads(payload_str)
    assert payload["letter_text"] == _NOTE


def test_single_pass_prompt_version_recorded() -> None:
    payload_str = llm_only_single_pass.build_prompt_input(_LETTER)
    payload = json.loads(payload_str)
    assert payload["prompt_version"] == llm_only_single_pass.PROMPT_VERSION


def test_per_entity_prompt_version_recorded() -> None:
    payload_str = llm_only_per_entity.build_prompt_input(_LETTER)
    payload = json.loads(payload_str)
    assert payload["prompt_version"] == llm_only_per_entity.PROMPT_VERSION


def test_prompt_versions_are_distinct() -> None:
    assert llm_only_single_pass.PROMPT_VERSION != llm_only_per_entity.PROMPT_VERSION


# ── DSPy signature component hygiene (ADR 0015) ───────────────────────────────
# Signature docstrings and InputField/OutputField desc strings are model-facing
# and must comply with the same hygiene rules as build_prompt_input payloads.


def _collect_signature_text(sig_class) -> str:
    """Collect the docstring and all field desc strings from a DSPy Signature."""
    import dspy

    parts = [sig_class.__doc__ or ""]
    for field_name in sig_class.model_fields:
        field = sig_class.model_fields[field_name]
        extra = field.json_schema_extra or {}
        parts.append(extra.get("desc", ""))
    return " ".join(parts)


@pytest.mark.parametrize(
    ("name", "sig_class"),
    [
        ("ExECTv2SinglePassSFSignature", ExECTv2SinglePassSFSignature),
        ("ExECTv2PerEntitySFSignature", ExECTv2PerEntitySFSignature),
    ],
)
def test_dspy_signature_components_do_not_expose_internal_vocabulary(
    name: str,
    sig_class,
) -> None:
    text = _collect_signature_text(sig_class)
    leaked = [phrase for phrase in FORBIDDEN_PHRASES if phrase in text]
    assert leaked == [], f"{name}: leaked internal phrases {leaked}"


@pytest.mark.parametrize(
    ("name", "sig_class"),
    [
        ("ExECTv2SinglePassSFSignature", ExECTv2SinglePassSFSignature),
        ("ExECTv2PerEntitySFSignature", ExECTv2PerEntitySFSignature),
    ],
)
def test_dspy_signature_does_not_use_extraction_vocabulary(
    name: str,
    sig_class,
) -> None:
    """'extraction instructions' is the specific form the ADR flags as non-compliant."""
    text = _collect_signature_text(sig_class)
    assert "extraction instructions" not in text, (
        f"{name}: contains forbidden phrase 'extraction instructions' (ADR 0015)"
    )
