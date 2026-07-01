> **Superseded for navigation —** canonical summary: [`DIAGNOSIS_FAMILY_LADDER_CANON.md`](../../../canon/workstreams/DIAGNOSIS_FAMILY_LADDER_CANON.md). Full detail retained below.

# ExECTv2 Diagnosis Verifier v0.2 Pilot

Date: 2026-06-18  
Split: dev25 only  
Pipeline: `exectv2_llm_diagnosis_verifier`  
Model: `openai/gpt-4.1-mini`  
Draft source: `exectv2_llm_only_key_entities_structured_v0.5`

## Decision

v0.2 is the best Diagnosis-specific multi-prompt candidate so far, but it is
still revise-only. It improves the objective-aligned Diagnosis clinical-recovery
headline from v0.1 `0.592` to `0.619` F1 while preserving a clean gate:

| Candidate | Diagnosis clinical F1 | Precision | Recall | Evidence validity |
| --- | ---: | ---: | ---: | ---: |
| v0.5 single structured prompt | 0.569 | 0.554 | 0.585 | 0.9684 |
| Diagnosis verifier v0.1 | 0.592 | 0.644 | 0.547 | 1.0000 |
| Diagnosis verifier v0.2 | 0.619 | 0.682 | 0.566 | 1.0000 |

The v0.2 change explicitly allowed model-owned normalized Diagnosis concept text
when evidence is exact. This is not deterministic repair: the model emits the
clinical concept phrase, and deterministic code only validates evidence,
schema-legal attributes, strips model CUI/CUIPhrase, projects CUIs, and scores.

## Readout

The v0.2 verifier improved source-near overlap (`0.694 -> 0.727` F1) and
clinical precision (`0.644 -> 0.682`), with a small recall recovery (`0.547 ->
0.566`). The remaining gap is still recall-heavy: 23 clinical-recovery false
negatives remain on dev25.

## Next Iteration

Build v0.3 from the v0.2 miss table:

1. Target the remaining recurring misses, especially tonic-clonic seizure
   concepts, focal seizure variants, uncertain epilepsy syndromes, and generic
   epilepsy concepts that are suppressed by over-specific rendering.
2. Keep the exact-evidence gate at `1.0000`; do not allow model-only concepts
   without a source substring as evidence.
3. If v0.3 cannot move Diagnosis materially above `0.65`, stop prompt accretion
   and test a candidate-merge policy between v0.5 and the verifier.
