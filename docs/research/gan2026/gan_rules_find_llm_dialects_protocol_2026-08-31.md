# Protocol: Rules find dialects for LLM extract comparison

Date: 2026-08-31
Status: complete; living find promoted to source-near 2026-08-31
Owner: this file
Report: [dialect result](gan_rules_find_llm_dialects_2026-08-31.md)
Parent: [Phase E2](gan_rules_only_three_stage_phase_e2_protocol_2026-08-30.md)
Guardrail: `gan2026-scoring-guardrail`
Split: `dev750` only; `test450` sealed. Zero model calls.

## Primary question

Given atomic `FindFact` slots, which string dialect should rules find
use for Purist comparison to LLM find?

## Decision

`gan_llm_extract` is bundled find-and-encode: the model writes
codebook `final_label`. `gan_llm_extract_raw` is find: source-near
form, no codebook writer. Cell 3 therefore shares encode between the
model and `gan_rules_encode`.

Living rules find is the source-near projection. The codebook
projection is the encode-comparable column, not find.

Atomic `find_tag` stays diagnostic. Select and encode stops stay
unchanged. Cited five-cell select stays **325/450**. Phase D
**292 / 292** remains the fused codebook instrumentation.

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
