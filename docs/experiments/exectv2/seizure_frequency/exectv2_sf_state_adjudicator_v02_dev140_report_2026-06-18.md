> **Superseded for navigation —** canonical summary: [`SF_ADJUDICATOR_LADDER_CANON.md`](../../../canon/workstreams/SF_ADJUDICATOR_LADDER_CANON.md). Full detail retained below.

# ExECTv2 SeizureFrequency Candidate-Span State Adjudicator v0.2 dev140

Date: 2026-06-18  
Split: dev140  
Model: `openai/gpt-4.1-mini`  
Substrate: `exectv2_llm_only_key_entities_structured_v0.5`

## Decision

Revise-only. v0.2 successfully tightens generic seizure over-emission but does
not improve the dev140 headline because recall falls, especially for unknown
frequency states.

| Run | F1 | P | R | Gate |
| --- | ---: | ---: | ---: | --- |
| SF state adjudicator v0.1 dev140 | 0.674 | 0.653 | 0.695 | 0 call failures, 0 parse failures, evidence 1.0000 |
| SF state adjudicator v0.2 dev25 pilot | 0.951 | 0.967 | 0.935 | 0 call failures, 0 parse failures, evidence 1.0000 |
| SF state adjudicator v0.2 dev140 | 0.672 | 0.687 | 0.658 | 0 call failures, 0 parse failures, evidence 1.0000 |

## Interpretation

The v0.2 prompt-policy change did what it was designed to do locally: it reduced
generic active-rate and seizure-free over-emission. On full dev140 this traded
away too much recall. Precision rises from `0.653` to `0.687`, but recall drops
from `0.695` to `0.658`, leaving F1 essentially flat/slightly worse.

The residual ledger shows that the stricter policy helped seizure-free precision
(`0.825`) and active-rate precision (`0.673`), but unknown states became the
dominant failure (`F1 0.235`, recall `0.182`). The next iteration should not
keep tightening generic rejection globally; it needs a separate unknown-state
recovery path.

## Residual Pattern

From `experiments/exectv2_sf_state_adjudicator_v02_residual_ledger_dev140_20260618.md`:

- Gold misses: generic seizure unknown `13`, generic seizure-free `10`, generic
  seizure active-rate `7`.
- Predicted over-emissions: generic seizure active-rate `13`, generic seizure
  unknown `4`, generic seizure-free `3`.
- State totals: active-rate `19` misses / `34` over-emissions; seizure-free
  `18` / `10`; unknown `27` / `12`.

## Next Loop

Use a two-lane SF adjudicator rather than one global keep/reject policy:

- Lane 1: strict active-rate/seizure-free gate to preserve the v0.2 precision
  gains.
- Lane 2: explicit unknown/change-state recovery for phrases such as returned,
  increasing, frequent, infrequent, improved, deteriorated, and controlled,
  separated from numeric active-rate extraction.

Keep v0.1 as the current numeric SF candidate (`0.674`) unless v0.3 improves on
dev140.
