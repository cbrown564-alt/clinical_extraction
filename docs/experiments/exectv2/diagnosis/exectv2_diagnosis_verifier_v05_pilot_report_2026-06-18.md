> **Superseded for navigation —** canonical summary: [`DIAGNOSIS_FAMILY_LADDER_CANON.md`](../../../canon/workstreams/DIAGNOSIS_FAMILY_LADDER_CANON.md). Full detail retained below.

# ExECTv2 Diagnosis Verifier v0.5 Pilot

Date: 2026-06-18  
Split: dev25 only  
Pipeline: `exectv2_llm_diagnosis_verifier`  
Model: `openai/gpt-4.1-mini`  
Draft source: `exectv2_llm_only_key_entities_structured_v0.5`

## Decision

v0.5 is the first Diagnosis-specific candidate to clear the development target
on dev25. It improves the objective-aligned Diagnosis clinical-recovery
headline from v0.4 `0.768` to `0.837` F1 while preserving evidence validity:

| Candidate | Diagnosis clinical F1 | Precision | Recall | Evidence validity |
| --- | ---: | ---: | ---: | ---: |
| v0.5 single structured prompt | 0.569 | 0.554 | 0.585 | 0.9684 |
| Diagnosis verifier v0.3 | 0.701 | 0.773 | 0.641 | 1.0000 |
| Diagnosis verifier v0.4 | 0.768 | 0.826 | 0.717 | 1.0000 |
| Diagnosis verifier v0.5 | 0.837 | 0.911 | 0.774 | 1.0000 |

This is a development-surface success, not a generalization claim. The next
Diagnosis step is dev140 confirmation once the combined key-family architecture
is ready for a broader run.

## Readout

v0.5 improved precision sharply (`0.826 -> 0.911`) while also improving recall
(`0.717 -> 0.774`). Source-near overlap rose to `0.840` F1. The run had `0`
call failures, `0` parse failures, and `44/44` evidence-valid rendered
mentions.

The v0.5 prompt remained error-analysis-led: it suppressed generic `seizures`,
non-epileptic/dissociative over-emission, and inferred generic epilepsy while
recovering specific syndromes such as genetic generalised epilepsy and
intractable epilepsy, secondary tonic-clonic component concepts, and focal
seizures under control.

## Next Iteration

Do not keep accreting Diagnosis prompt rules on dev25 unless dev140 exposes a
new recurring failure class. The key-entity objective should now shift to the
remaining below-target family: SeizureFrequency, whose best single structured
dev25 headline is still `0.633`.
