# ExECTv2 Diagnosis Heading/Narrative Decomposer v0.1 dev140

Date: 2026-06-18  
Split: dev140  
Model: `openai/gpt-4.1-mini`  
Substrate: `exectv2_llm_only_key_entities_structured_v0.5`

## Decision

Reject as current Diagnosis candidate. The heading/narrative decomposition clears
the dev25 pilot target, but does not transfer to dev140 and underperforms the
current Diagnosis verifier v0.6.

| Run | F1 | P | R | Gate |
| --- | ---: | ---: | ---: | --- |
| Diagnosis verifier v0.6 dev140 | 0.651 | 0.706 | 0.604 | 0 call failures, 0 parse failures, evidence 0.9906 |
| Diagnosis decomposer v0.1 dev25 pilot | 0.814 | 0.767 | 0.868 | 0 call failures, 0 parse failures, evidence 1.0000 |
| Diagnosis decomposer v0.1 dev140 | 0.642 | 0.631 | 0.653 | 0 call failures, 0 parse failures, evidence 1.0000 |

## Interpretation

The decomposition did what it was designed to do mechanically: it surfaced many
more candidate spans (`812` spans, `462` rendered mentions) and improved
source-near recall (`0.830`). But the clinical-recovery headline fell from the
current v0.6 verifier's `0.651` to `0.642` because the extra recall came with a
larger precision leak.

This means the next Diagnosis iteration should not simply add more heading and
narrative span context. It needs a stricter reconciliation step or verifier over
the decomposed output, especially for over-emitted tonic-clonic/absence/focal
seizure assertions and uncertain focal-epilepsy variants.

## Next Loop

Keep Diagnosis verifier v0.6 as the current dev140 Diagnosis candidate. If we
continue decomposition, make the second step explicit:

- heading collector emits generic epilepsy and syndrome candidates;
- narrative seizure-type collector emits asserted seizure-type candidates;
- a verifier/reconciler decides which candidates are true Diagnosis mentions,
  suppressing frequency-only and non-diagnostic seizure-type spans.

Do not promote the decomposer v0.1 output directly.
