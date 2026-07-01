> **Superseded for navigation —** canonical summary: [`DIAGNOSIS_FAMILY_LADDER_CANON.md`](../../../canon/workstreams/DIAGNOSIS_FAMILY_LADDER_CANON.md). Full detail retained below.

# ExECTv2 Diagnosis Verifier v0.3 Pilot

Date: 2026-06-18  
Split: dev25 only  
Pipeline: `exectv2_llm_diagnosis_verifier`  
Model: `openai/gpt-4.1-mini`  
Draft source: `exectv2_llm_only_key_entities_structured_v0.5`

## Decision

v0.3 is the best Diagnosis-specific candidate so far, but remains revise-only.
It improves the objective-aligned Diagnosis clinical-recovery headline from
v0.2 `0.619` to `0.701` F1 while preserving a clean gate:

| Candidate | Diagnosis clinical F1 | Precision | Recall | Evidence validity |
| --- | ---: | ---: | ---: | ---: |
| v0.5 single structured prompt | 0.569 | 0.554 | 0.585 | 0.9684 |
| Diagnosis verifier v0.1 | 0.592 | 0.644 | 0.547 | 1.0000 |
| Diagnosis verifier v0.2 | 0.619 | 0.682 | 0.566 | 1.0000 |
| Diagnosis verifier v0.3 | 0.701 | 0.773 | 0.641 | 1.0000 |

The v0.3 prompt targeted the v0.2 residual misses: repeated tonic-clonic
diagnosis assertions, epilepsy-with-generalised-tonic-clonic-seizures-alone
syndrome rendering, uncertain temporal/focal seizure-type diagnoses, intractable
epilepsy specificity, and suppression of bare symptom/non-named seizure labels.
The model still owns the revised Diagnosis mentions. Deterministic code remains
limited to schema/evidence validation, legal attribute repair, stripping model
`CUI`/`CUIPhrase`, CUI projection, and scoring.

## Readout

v0.3 improved clinical recall (`0.566 -> 0.641`) and precision (`0.682 ->
0.773`) simultaneously. Source-near overlap also rose (`0.727 -> 0.755` F1).
The run had `0` call failures, `0` parse failures, and `42/42` evidence-valid
rendered mentions.

The remaining gap is still recall-heavy enough to justify one more targeted
Diagnosis loop: dev25 has 19 clinical-recovery false negatives, and Diagnosis
is still below the target F1 `0.8`.

## Next Iteration

Build v0.4 from the v0.3 miss table before dev140:

1. Inspect the remaining false negatives and false positives by clinical concept
   and source phrase. Do not broaden rules unless the miss recurs.
2. Protect the precision gain above `0.75` and the exact-evidence gate at
   `1.0000`.
3. If v0.4 cannot move Diagnosis near or above `0.75`, pivot from prompt
   accretion to a principled candidate/verifier decomposition, such as separate
   syndrome, seizure-type, and uncertainty passes with a final verifier.
