# ExECTv2 Diagnosis Reconciler v0.2 dev140

Date: 2026-06-18  
Split: dev140  
Model: `openai/gpt-4.1-mini`  
Inputs: Diagnosis verifier v0.6 + Diagnosis decomposer v0.1

## Decision

Reject as current Diagnosis candidate. v0.2 adds explicit candidate concept
groups and slightly improves the dev25 pilot, but it transfers worse than v0.1
on dev140.

| Run | F1 | P | R | Gate |
| --- | ---: | ---: | ---: | --- |
| Diagnosis verifier v0.6 dev140 | 0.651 | 0.706 | 0.604 | 0 call failures, 0 parse failures, evidence 0.9906 |
| Diagnosis reconciler v0.1 dev140 | 0.658 | 0.658 | 0.658 | 0 call failures, 0 parse failures, evidence 0.9954 |
| Diagnosis reconciler v0.2 dev25 pilot | 0.844 | 0.821 | 0.868 | 0 call failures, 0 parse failures, evidence 1.0000 |
| Diagnosis reconciler v0.2 dev140 | 0.647 | 0.636 | 0.658 | 0 call failures, 0 parse failures, evidence 0.9956 |

## Interpretation

The v0.2 prompt surfaces candidate concept groups for generic epilepsy,
focal-family epilepsy, tonic-clonic variants, secondary generalised concepts,
and structural/symptomatic epilepsy. This was designed to make the model
classify residual concept families explicitly rather than reconcile a flat list.

The grouping helped on dev25 but did not transfer. Recall stayed flat versus
v0.1 (`0.658`), while precision fell from `0.658` to `0.636`. That means the
model did not solve the key recall problem and reintroduced over-emission,
especially generic epilepsy. The next loop should not add more candidate
grouping prose; it should gate over-emitted concept families before final
rendering or split the task into high-recall collection plus deterministic/LLM
binary acceptance decisions per concept family.

## Residual Pattern

From `experiments/exectv2_diagnosis_reconciler_v02_residual_ledger_dev140_20260618.md`:

- Gold misses: generic epilepsy certainty-5 `15`, focal epilepsy certainty-5
  `7`, focal seizures certainty-5 `6`, epilepsy certainty-4 `5`, tonic-clonic
  seizures certainty-5 `5`.
- Predicted over-emissions: generic epilepsy certainty-5 `56`, tonic-clonic
  seizures certainty-5 `24`, absence seizures certainty-5 `8`, symptomatic
  structural focal epilepsy `7`.
- Compared with v0.1, generic epilepsy misses fell slightly (`17` -> `15`) but
  generic epilepsy over-emissions rose (`52` -> `56`), and the overall FP count
  increased (`126` -> `139`).

## Next Loop

Keep Diagnosis reconciler v0.1 as the current numeric Diagnosis candidate
(`0.658`). The next Diagnosis phase should test a constrained accept/reject
verifier over concept-family candidates:

- one binary decision per normalized concept/evidence pair rather than a
  free-form final mention list;
- explicit rejection labels for section context, frequency-only seizure type,
  historical/background epilepsy, inferred structural cause, and non-epileptic
  event;
- an ablation that reports whether the gate improves generic epilepsy and
  tonic-clonic precision without losing focal epilepsy and secondary-generalised
  recall.
