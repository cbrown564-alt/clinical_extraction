# Protocol: Rules find dialects for LLM extract comparison

Date: 2026-08-31
Status: complete
Owner: this file
Report: [dialect result](gan_rules_find_llm_dialects_2026-08-31.md)
Parent: [Phase E2](gan_rules_only_three_stage_phase_e2_protocol_2026-08-30.md)
Guardrail: `gan2026-scoring-guardrail`
Split: `dev750` only; `test450` sealed. Zero model calls.

## Primary question

Given atomic `FindFact` slots, which string dialect should rules find
use for Purist comparison to LLM find?

## Decision to test

LLM find is scored on `selection.final_label` after a `raw_model`
parse (`living_gan_stages`). Gold is codebook. Therefore:

- **`gan_llm_extract`:** project slots through the codebook writer
  (`encode_find_fact`). That is the same family the cited extract
  prompt requires and the only dialect `score_label` accepts without
  format repair.
- **`gan_llm_extract_raw`:** project slots to a source-near phrase
  that keeps found tokens (word numbers, compact units, adjectives).
  That maps to extract_raw `raw_value` / letter-adjacent
  `final_label`. Purist on that string measures the same dialect tax
  as source-near LLM find.

Atomic `find_tag` stays diagnostic. It is not a comparison dialect.
Select and encode stops stay unchanged. Cited five-cell stops stay
**292 / 292 / 325**.

## Gates

- **D1:** codebook projection equals `encode_find_fact` on fixtures.
- **D2:** source-near projection keeps raw tokens (`four per day`,
  `5 per mo`, `daily`) and differs from codebook on those fixtures.
- **D3:** default select remains 669/750; promoted select 691/750.
- **D4:** codebook-dialect find Purist equals the Phase E2 encode
  stop on the same document-order pick (577 default / 599 promoted)
  when the codebook string is scored unrepaired. Encode stop may
  still apply living repair; record any gap.

No holdout. No `_gan_grid` rewire.
