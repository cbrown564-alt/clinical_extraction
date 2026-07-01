> **Superseded for navigation —** canonical summary: [`DIAGNOSIS_FAMILY_LADDER_CANON.md`](../../../canon/workstreams/DIAGNOSIS_FAMILY_LADDER_CANON.md). Full detail retained below.

# ExECTv2 Diagnosis Verifier v0.4 Pilot

Date: 2026-06-18  
Split: dev25 only  
Pipeline: `exectv2_llm_diagnosis_verifier`  
Model: `openai/gpt-4.1-mini`  
Draft source: `exectv2_llm_only_key_entities_structured_v0.5`

## Decision

v0.4 is the best Diagnosis-specific candidate so far, but remains revise-only.
It improves the objective-aligned Diagnosis clinical-recovery headline from
v0.3 `0.701` to `0.768` F1 while preserving the exact-evidence gate:

| Candidate | Diagnosis clinical F1 | Precision | Recall | Evidence validity |
| --- | ---: | ---: | ---: | ---: |
| v0.5 single structured prompt | 0.569 | 0.554 | 0.585 | 0.9684 |
| Diagnosis verifier v0.2 | 0.619 | 0.682 | 0.566 | 1.0000 |
| Diagnosis verifier v0.3 | 0.701 | 0.773 | 0.641 | 1.0000 |
| Diagnosis verifier v0.4 | 0.768 | 0.826 | 0.717 | 1.0000 |

The v0.4 prompt targeted only recurring v0.3 residuals: singular one-off
seizure text, duplicated independently supported seizure-type assertions,
uncertain focal-onset lines, parenthetical probable-cause wording, intractable
epilepsy specificity, epileptic-event normalization, remote febrile seizure
suppression, and generic "reviewed with epilepsy" recovery.

## Readout

v0.4 improved clinical precision (`0.773 -> 0.826`) and recall (`0.641 ->
0.717`) together. Source-near overlap rose to `0.792` F1, and attribute
agreement rose to `0.800`. The run had `0` call failures, `0` parse failures,
and `45/45` evidence-valid rendered mentions.

Diagnosis is now close to but still below the target F1 `0.8`; there are 15
clinical-recovery false negatives remaining on dev25. Because v0.4 preserved
precision while lifting recall, one further residual-error iteration is
justified before dev140.

## Next Iteration

Build v0.5 only if the v0.4 miss table shows a small number of recurring,
clinically defensible fixes. Otherwise stop prompt accretion and move to a
decomposed candidate/verifier architecture.

Potential v0.5 acceptance gate on dev25:

- Diagnosis clinical F1 at or above `0.8`, or a clear precision-preserving lift
  that justifies dev140.
- Evidence validity remains `1.0000`.
- No broad new symptom/history false positives.
