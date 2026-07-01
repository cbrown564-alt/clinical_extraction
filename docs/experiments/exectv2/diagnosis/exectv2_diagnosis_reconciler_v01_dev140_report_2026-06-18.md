> **Superseded for navigation —** canonical summary: [`DIAGNOSIS_FAMILY_LADDER_CANON.md`](../../../canon/workstreams/DIAGNOSIS_FAMILY_LADDER_CANON.md). Full detail retained below.

# ExECTv2 Diagnosis Reconciler v0.1 dev140

Date: 2026-06-18  
Split: dev140  
Model: `openai/gpt-4.1-mini`  
Inputs: Diagnosis verifier v0.6 + Diagnosis decomposer v0.1  

## Decision

Revise-only. The reconciler is the best Diagnosis dev140 score so far, but the
gain is small and still far below the `0.8` clinical-recovery target.

| Run | F1 | P | R | Gate |
| --- | ---: | ---: | ---: | --- |
| Diagnosis verifier v0.6 dev140 | 0.651 | 0.706 | 0.604 | 0 call failures, 0 parse failures, evidence 0.9906 |
| Diagnosis decomposer v0.1 dev140 | 0.642 | 0.631 | 0.653 | 0 call failures, 0 parse failures, evidence 1.0000 |
| Diagnosis reconciler v0.1 dev25 pilot | 0.833 | 0.818 | 0.849 | 0 call failures, 0 parse failures, evidence 1.0000 |
| Diagnosis reconciler v0.1 dev140 | 0.658 | 0.658 | 0.658 | 0 call failures, 0 parse failures, evidence 0.9954 |

## Interpretation

The reconciler confirms the right decomposition direction but not a sufficient
solution. It improves over both inputs on the dev140 headline (`0.658` vs
`0.651`/`0.642`) by balancing the verifier's precision with the decomposer's
recall. The improvement is too small to promote.

The source-near overlap remains useful (`F1 0.787`, recall `0.817`), so the
letter evidence is often being found. The failure is clinical concept/assertion
selection: deciding which explicit epilepsy/seizure-type spans should become
Diagnosis mentions and how specific they should be.

## Residual Pattern

From `experiments/exectv2_diagnosis_reconciler_v01_residual_ledger_dev140_20260618.md`:

- Gold misses: generic epilepsy certainty-5 `17`, focal epilepsy certainty-5 `7`,
  secondary generalised seizures `6`, focal seizures certainty-5 `5`, tonic
  clonic seizures certainty-5 `5`.
- Predicted over-emissions: generic epilepsy certainty-5 `52`, tonic clonic
  seizures certainty-5 `26`, absence seizures certainty-5 `8`, symptomatic
  structural focal epilepsy `7`.
- Concept-only F1 is `0.713` while concept+assertion F1 is `0.659`, so assertion
  certainty and over-specific/under-specific concept rendering are both still
  material.

## Next Loop

The next Diagnosis iteration should be a constrained verifier over candidate
concept groups, not another free-form expansion:

- explicitly classify generic epilepsy evidence as patient-level established,
  historical/background, section context only, or reject;
- group tonic-clonic/generalised-tonic-clonic/secondary-generalised variants
  before choosing one normalized concept;
- require a direct epilepsy/syndrome assertion for structural/symptomatic focal
  epilepsy rather than allowing causal inference from MRI/stroke context;
- keep a recovery path for focal epilepsy and secondary generalised seizures,
  which remain among the largest misses.

Keep v0.1 reconciler as the current numeric Diagnosis candidate only because it
slightly beats v0.6. It is not close to the target.
