# ExECTv2 Diagnosis Verifier v0.1 Pilot

Date: 2026-06-18  
Split: dev25 only  
Pipeline: `exectv2_llm_diagnosis_verifier`  
Model: `openai/gpt-4.1-mini`  
Draft source: `exectv2_llm_only_key_entities_structured_v0.5`

## Decision

The v0.1 Diagnosis verifier is a useful but not sufficient architectural step.
It reviews the v0.5 single structured prompt's draft Diagnosis mentions and asks
the model to keep, delete, edit, or add final Diagnosis mentions. Deterministic
code only validates JSON, exact evidence, legal attributes, strips
model-supplied CUI/CUIPhrase, projects CUIs, and scores.

The verifier improves the objective-aligned Diagnosis clinical-recovery headline
from `0.569` to `0.592` on dev25, with a clean gate:

| Candidate | Diagnosis clinical F1 | Precision | Recall | Evidence validity |
| --- | ---: | ---: | ---: | ---: |
| v0.5 single structured prompt | 0.569 | 0.554 | 0.585 | 0.9684 |
| v0.1 Diagnosis verifier | 0.592 | 0.644 | 0.547 | 1.0000 |

This is the first multi-prompt variant to improve over the best single-prompt
Diagnosis candidate, but the gain comes through precision more than recall and
remains far below the `0.8` family target. It should be revised before dev140.

## Error-Analysis Read

The verifier's higher precision suggests the review framing helps suppress
Diagnosis false positives and clean concept spans. Its lower recall shows it is
too conservative: the next iteration should add targeted recall pressure for
the remaining gold diagnosis concepts without reintroducing symptom-only or
non-epileptic false positives.

## Next Iteration

Build verifier v0.2 on dev25:

1. Inspect v0.1 false negatives by concept family and preserve the exact
   evidence-valid output contract.
2. Add targeted recall rules for recurring misses such as tonic-clonic seizure
   concepts, focal seizure variants, uncertain epilepsy syndromes, and JME.
3. Keep the verifier as an LLM-owned clinical-selection stage; do not introduce
   deterministic semantic repair.
