# ExECTv2 SeizureFrequency Candidate-Span State Adjudicator v0.3 dev140

Date: 2026-06-18  
Split: dev140  
Model: `openai/gpt-4.1-mini`  
Substrate: `exectv2_llm_only_key_entities_structured_v0.5`

## Decision

Revise-only. v0.3 is the best SeizureFrequency dev140 state-adjudicator result
so far, but the gain is small and still below the `0.8` clinical-recovery target.

| Run | F1 | P | R | Gate |
| --- | ---: | ---: | ---: | --- |
| SF state adjudicator v0.1 dev140 | 0.674 | 0.653 | 0.695 | 0 call failures, 0 parse failures, evidence 1.0000 |
| SF state adjudicator v0.2 dev140 | 0.672 | 0.687 | 0.658 | 0 call failures, 0 parse failures, evidence 1.0000 |
| SF state adjudicator v0.3 dev25 pilot | 0.921 | 0.906 | 0.935 | 0 call failures, 0 parse failures, evidence 1.0000 |
| SF state adjudicator v0.3 dev140 | 0.681 | 0.667 | 0.695 | 0 call failures, 0 parse failures, evidence 1.0000 |

## Interpretation

v0.3 added an explicit unknown/change-state recovery lane after v0.2 showed that
global generic-seizure tightening improved precision but collapsed unknown-state
recall. The change worked in the intended direction: unknown F1 rose from
`0.235` to `0.424`, and the overall headline moved from `0.672` to `0.681`.

The improvement is not large enough to treat prompt wording as the main remaining
lever. Active-rate remains around `0.72` F1, seizure-free remains around `0.75`,
and unknown is still weak at `0.424`. The residual load is now more balanced
across state families rather than dominated by one missing lane.

## Residual Pattern

From `experiments/exectv2_sf_state_adjudicator_v03_residual_ledger_dev140_20260618.md`:

- Gold misses: generic seizure-free `11`, generic seizure active-rate `7`,
  generic seizure unknown `7`.
- Predicted over-emissions: generic seizure active-rate `11`, generic seizure
  unknown `6`, generalised tonic-clonic active-rate `5`.
- State totals: active-rate `19` misses / `35` over-emissions; seizure-free
  `19` / `11`; unknown `19` / `19`.

## Next Loop

Keep v0.3 as the current numeric SF candidate (`0.681`) because it is the best
dev140 result so far, but move beyond broad prompt accretion. The next SF loop
should test a stronger decomposition:

- candidate expansion/typing that separates generic seizure, named seizure type,
  seizure-free anchor, prior-event anchor, and qualitative change before the LLM;
- a constrained state classifier over those typed candidates rather than a
  general final-mention renderer;
- explicit duplicate handling for repeated generic/named statements and
  historical single-event contexts.

Diagnosis remains separately below target and should continue with a constrained
concept-group verifier rather than another broad heading/narrative pass.
