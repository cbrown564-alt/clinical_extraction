"""Tests for the ExECTv2 multi-stage (generate -> verify) GEPA program.

Phase 0 gate (docs/plans/exectv2_gepa_multistage_program_scope_2026-06-28.md):
the ``forward`` merge must flow the *verified* facts (not the drafts) into the
final ``clinical_facts_json`` without injecting a synthetic ``attributes`` key (the
trap the per-family build hit), and stamp the summed evolvable-instruction tokens.
The warm-start seed loader must parse the evolved multifamily artifact.
"""

from __future__ import annotations

import json

import dspy
from dspy.utils.dummies import DummyLM

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program import (
    OUTPUT_SCHEMA_JSON,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program_multistage import (
    FAMILIES,
    EVOLVED_MULTIFAMILY_INSTRUCTION,
    build_multistage_program,
    combined_instruction,
    load_evolved_s0_seeds,
    parse_combined_instruction,
)


def _facts(facts: list[dict], output_key: str) -> dict[str, str]:
    return {output_key: json.dumps({"clinical_facts": facts})}


# The forward loops families in order, emitting (generate, verify) per family. Each
# generate predictor outputs `clinical_facts_json`; each verify outputs
# `verified_facts_json`. DummyLM returns these dicts in call order.
_DRAFT_DX = {
    "family": "diagnosis",
    "concept": "focal epilepsy probable temporal",
    "negation": "affirmed",
    "evidence": "focal epilepsy",
}
_VERIFIED_DX = {
    "family": "diagnosis",
    "concept": "focal epilepsy",
    "negation": "affirmed",
    "evidence": "focal epilepsy",
}
_INV = {"family": "investigation", "modality": "MRI", "result": "normal", "evidence": "MRI was normal"}

_RESPONSES = [
    _facts([_DRAFT_DX], "clinical_facts_json"),                     # generate diagnosis
    _facts([_VERIFIED_DX], "verified_facts_json"),                  # verify diagnosis (corrected)
    _facts(                                                          # generate seizure_frequency
        [{"family": "seizure_frequency", "seizure_type": "seizures", "state": "unknown", "evidence": "seizures"}],
        "clinical_facts_json",
    ),
    _facts([], "verified_facts_json"),                              # verify SF (drops bare-unknown)
    _facts([], "clinical_facts_json"),                              # generate prescription
    _facts([], "verified_facts_json"),                              # verify prescription
    _facts([_INV], "clinical_facts_json"),                          # generate investigation
    _facts([_INV], "verified_facts_json"),                          # verify investigation (kept)
]


def _run_forward() -> dspy.Prediction:
    program = build_multistage_program()
    with dspy.context(lm=DummyLM(list(_RESPONSES))):
        return program(letter_text="focal epilepsy. MRI was normal.", output_schema=OUTPUT_SCHEMA_JSON)


def test_forward_merges_verified_not_draft_facts():
    prediction = _run_forward()
    merged = json.loads(prediction.clinical_facts_json)["clinical_facts"]
    concepts = [f.get("concept") for f in merged if f["family"] == "diagnosis"]
    # The corrected (verify-stage) diagnosis flows through; the draft does not.
    assert concepts == ["focal epilepsy"]
    assert "focal epilepsy probable temporal" not in concepts


def test_forward_drops_verify_rejected_family():
    prediction = _run_forward()
    merged = json.loads(prediction.clinical_facts_json)["clinical_facts"]
    families = [f["family"] for f in merged]
    # SF generate drafted a bare-unknown fact; verify rejected it -> absent from merge.
    assert "seizure_frequency" not in families
    # The two kept facts are the corrected diagnosis and the verified investigation.
    assert families == ["diagnosis", "investigation"]


def test_forward_injects_no_synthetic_attributes_key():
    prediction = _run_forward()
    merged = json.loads(prediction.clinical_facts_json)["clinical_facts"]
    # The per-family build's trap: a synthetic empty `attributes` dict that the metric
    # parser coerces to a string and rejects. The raw emitted facts must carry none.
    assert all("attributes" not in fact for fact in merged)


def test_forward_stamps_summed_evolvable_tokens():
    prediction = _run_forward()
    # Eight evolvable instructions (4 generate + 4 verify) are summed; no demos seeded.
    assert prediction.instruction_tokens > 0
    assert prediction.demo_tokens == 0


def test_combined_instruction_labels_all_eight_stages():
    program = build_multistage_program()
    text = combined_instruction(program)
    for family in FAMILIES:
        assert f"=== generate.{family} ===" in text
        assert f"=== verify.{family} ===" in text


def test_warm_start_overrides_only_s0():
    seeds = {family: f"WARM S0 {family}." for family in FAMILIES}
    program = build_multistage_program(s0_seed_instructions=seeds)
    text = combined_instruction(program)
    blocks = parse_combined_instruction(text)
    for family in FAMILIES:
        assert blocks[f"generate.{family}"] == f"WARM S0 {family}."
        # Verify stages keep their lean distilled seeds (not overridden by S0 warm-start).
        assert "WARM S0" not in blocks[f"verify.{family}"]
        assert blocks[f"verify.{family}"]


def test_load_evolved_s0_seeds_parses_four_families():
    if not EVOLVED_MULTIFAMILY_INSTRUCTION.exists():
        import pytest

        pytest.skip("evolved 0.731 artifact not present")
    seeds = load_evolved_s0_seeds()
    assert set(seeds) == set(FAMILIES)
    # Every seed is non-empty and the diagnosis JSON wrapper is unwrapped to plain text.
    assert all(seeds[family].strip() for family in FAMILIES)
    assert not seeds["diagnosis"].strip().startswith("{")
