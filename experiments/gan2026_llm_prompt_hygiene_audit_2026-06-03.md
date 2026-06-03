# Gan 2026 LLM Prompt Hygiene Audit - 2026-06-03

## Summary

This audit found that all seven current Gan 2026 LLM prompt builders exposed at
least one model-facing prompt hygiene issue under the expanded standard used in
this cleanup. The issues were not limited to explicit architecture language.
Several prompts also told the model about absent context, internal evaluation
surfaces, parser/scorer framing, prompt policy metadata, or highly specific
dataset-shaped conversion examples.

These prompt features are plausible contributors to a validation/test
generalization gap because they can train the model's local behavior around
benchmark and dataset conventions rather than around portable clinical
seizure-frequency reasoning.

## Failure Modes Found

- Absent-context instructions: prompts said not to use deterministic candidates,
  rule candidates, or gold labels even though the model never receives those
  inputs.
- Internal surface language: prompts mentioned parser-ready labels,
  Gan-compatible or Gan-facing labels, scorer-facing or scoring-facing output,
  benchmark records, and synthetic letters.
- Internal metadata in model payloads: `prompt_policy_taxonomy`,
  `required_ablations_before_ladder_runs`, and score-layer names were included
  in prompt payloads.
- Over-specific examples: the claim-table prompt contained many arrow-style
  mappings and dataset-specific conventions. These were replaced with broader
  clinical and normalization rules.

## Affected Implementations

- `llm_only_direct_labeler.build_prompt_input`
- `llm_only_claim_table_selector.build_prompt_input`
- `llm_only_structured_events.build_prompt_input`
- `llm_only_minimal_evidence_selector.build_prompt_input`
- `llm_heavy_clinical_frequency_reasoner.build_prompt_input`
- `llm_only_typed_adapter_reasoner.build_typed_adapter_inputs`
- `llm_heavy_evidence_selection_with_deterministic_adapters.build_typed_inputs`

## Cleanup Performed

- Reworded prompts to say only what the model needs to do: read the clinical
  note, extract seizure-frequency facts, copy exact evidence, select the current
  or recent prediction-bearing state, and produce normalized labels or typed
  operands.
- Removed prompt references to gold labels, deterministic candidates, parser
  readiness, Gan-facing compatibility, scorer-facing output, benchmark records,
  synthetic letters, and internal decision/architecture wording.
- Removed `prompt_policy_taxonomy`, `required_ablations_before_ladder_runs`, and
  heavy-reasoner score-layer names from model-facing payloads.
- Replaced memorized-looking conversion examples with broader rules for count
  and range denominators, interval preservation, cluster cadence versus burden,
  same-window count addition, explicit maximum burden, and boundary states.
- Kept internal policy constants, run metadata, report language, scoring layers,
  and architecture labels available outside the prompt payload.

## Prevention

Added `tests/test_gan2026_llm_prompt_hygiene.py`, which constructs every current
LLM model-facing payload builder and rejects internal/protocol phrases:
deterministic candidates, gold labels, parser-ready wording, Gan-compatible or
Gan-facing wording, scorer/scoring-facing wording, benchmark/synthetic wording,
internal prompt policy fields, required ablation fields, decision IDs,
architecture-gate language, and arrow-style mapping examples.

This guardrail is intentionally payload-based rather than grep-only: it checks
the text the model actually receives.

## Verification

- `python -m pytest tests/test_gan2026_llm_only_claim_table_selector.py tests/test_gan2026_llm_only_direct_labeler.py tests/test_gan2026_llm_only_structured_events.py tests/test_gan2026_llm_only_minimal_evidence_selector.py tests/test_gan2026_llm_heavy_clinical_frequency_reasoner.py tests/test_gan2026_llm_only_typed_adapter_reasoner.py tests/test_gan2026_llm_heavy_evidence_selection_with_deterministic_adapters.py tests/test_gan2026_llm_prompt_hygiene.py -q`
  passed with 107 tests.

## Residual Risk

The cleanup preserves existing output schemas where changing field names would
alter downstream parser contracts. Some field names still include historical
terms such as `raw_llm_final_label` and `raw_model_parser_label`; the prompt text
around those fields now describes normalized clinical label behavior rather than
internal parser surfaces.
