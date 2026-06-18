# ExECTv2 SeizureFrequency Verifier v0.3 Pilot

Date: 2026-06-18  
Split: dev25 only  
Pipeline: `exectv2_llm_sf_verifier`  
Model: `openai/gpt-4.1-mini`  
Draft source: `exectv2_llm_only_key_entities_structured_v0.5`

## Decision

v0.3 is the first SeizureFrequency-specific candidate to clear the dev25 target.
It improves the objective-aligned SeizureFrequency clinical-recovery headline
from v0.2 `0.788` to `0.831` F1 while preserving evidence validity:

| Candidate | SeizureFrequency clinical F1 | Precision | Recall | Evidence validity |
| --- | ---: | ---: | ---: | ---: |
| v0.5 single structured prompt | 0.633 | 0.655 | 0.613 | 0.9684 |
| SeizureFrequency verifier v0.1 | 0.667 | 0.629 | 0.710 | 1.0000 |
| SeizureFrequency verifier v0.2 | 0.788 | 0.743 | 0.839 | 1.0000 |
| SeizureFrequency verifier v0.3 | 0.831 | 0.794 | 0.871 | 1.0000 |

This is a development-surface success only. The key-entity dev25 target is now
cleared for medication, Diagnosis, SeizureFrequency, and Investigations, but the
combined architecture still needs a predeclared dev140 readout before any
generalization claim.

## Readout

The run had `0` call failures, `0` parse failures, and `34/34`
evidence-valid rendered mentions. Source-near overlap reached `0.831` F1 with
`0.871` recall.

The v0.3 prompt remained residual-error-led: it prohibited count fields with
`unknown`, hardened suppression of previous-event and unlabelled episode/event
rates, clarified generic `last seizures were in teenage years` rendering,
suppressed non-myoclonic jerks, and recovered drug-change improvement and
duplicated focal-to-bilateral seizure-free states.

## Next Iteration

Do not tune further on dev25 before broadening. The next useful step is a
predeclared dev140 run that combines the best current key-family components:
the v0.5 single structured prompt for medication and Investigations, Diagnosis
verifier v0.5, and SeizureFrequency verifier v0.3.
