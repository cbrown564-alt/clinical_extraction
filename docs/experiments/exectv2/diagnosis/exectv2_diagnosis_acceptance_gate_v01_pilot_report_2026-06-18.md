# ExECTv2 Diagnosis Acceptance Gate v0.1 dev25

Date: 2026-06-18  
Split: dev25  
Model: `openai/gpt-4.1-mini`  
Inputs: Diagnosis verifier v0.6 + Diagnosis decomposer v0.1

## Decision

Reject before dev140. The constrained accept/reject framing is clean, but v0.1
is far too conservative on the development pilot and does not justify a full
dev140 run.

| Run | F1 | P | R | Gate |
| --- | ---: | ---: | ---: | --- |
| Diagnosis reconciler v0.1 dev25 | 0.833 | 0.818 | 0.849 | 0 call failures, 0 parse failures, evidence 1.0000 |
| Diagnosis reconciler v0.2 dev25 | 0.844 | 0.821 | 0.868 | 0 call failures, 0 parse failures, evidence 1.0000 |
| Diagnosis acceptance gate v0.1 dev25 | 0.625 | 0.698 | 0.566 | 0 call failures, 0 parse failures, evidence 1.0000 |

## Interpretation

The candidate pool has theoretical headroom: the verifier plus decomposer union
has enough recall that a strong accept/reject gate could be useful. This first
gate prompt did not realize that headroom. It accepted `42/87` candidates and
landed at only `0.566` recall on dev25, so the prompt is rejecting too many
true Diagnosis concepts.

The likely failure is over-correction after the v0.2 reconciler's generic
epilepsy and tonic-clonic over-emission. The v0.1 gate rejects frequency-only
seizure-type candidates too aggressively; in ExECTv2, seizure-type/frequency
headings often also carry Diagnosis mentions. A second gate should separate
generic count/rate over-emission from named seizure-type recovery rather than
using one broad rejection rule.

## Next Loop

Do not run v0.1 on dev140. Revise the gate only if it gains a recovery lane for:

- named seizure-type/frequency headings that should count as Diagnosis;
- secondary generalised and focal seizure concepts;
- generic epilepsy evidence that is explicit patient-level diagnosis rather than
  section context.

The next useful Diagnosis comparison is a gate v0.2 pilot with separate
acceptance rules for generic epilepsy, named seizure types, and structural
epilepsy inference.
