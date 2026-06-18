# ExECTv2 Prescription/Investigations Verifier v0.1 dev140

Date: 2026-06-18  
Split: dev140  
Pipeline: `exectv2_llm_med_inv_verifier`  
Model: `openai/gpt-4.1-mini`  
Draft source: `exectv2_llm_only_key_entities_structured_v0.5`

## Decision

v0.1 is useful as a Prescription verifier but rejected as an Investigations
verifier. It clears the medication target on dev140, improving Prescription from
the single structured draft's `0.777` F1 to `0.817`, but it damages
Investigations badly (`0.786` to `0.496`).

| Entity | Baseline dev140 F1 | Verifier v0.1 F1 | Precision | Recall | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| Prescription | 0.777 | 0.817 | 0.773 | 0.865 | Use as medication candidate |
| Investigations | 0.786 | 0.496 | 0.408 | 0.632 | Reject; keep baseline |

The run had `0` call failures, `0` parse failures, and evidence validity
`0.9792`.

## Interpretation

The medication improvement supports the ledger diagnosis: a focused verifier can
separate current regimens, rescue medication, split-dose schedules, and future
titration plans better than the broad structured prompt. Recall improved
substantially (`0.788` to `0.865`) while precision stayed similar.

The Investigations regression shows that bundling near-target families into one
verifier is too blunt. The prompt became conservative about planned tests but
over-produced incomplete or mismatched investigation facts and lost many
normal/abnormal result matches. The next Investigations iteration should be a
separate verifier with a simpler modality/result decision table, not another
combined Prescription/Investigations prompt.

## Next Step

Use v0.1 as the current Prescription candidate on dev140. Keep the single
structured v0.5 output for Investigations until a dedicated Investigations
verifier beats `0.786` on dev140.
