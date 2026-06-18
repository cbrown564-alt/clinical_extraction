# ExECTv2 SeizureFrequency Verifier v0.2 Pilot

Date: 2026-06-18  
Split: dev25 only  
Pipeline: `exectv2_llm_sf_verifier`  
Model: `openai/gpt-4.1-mini`  
Draft source: `exectv2_llm_only_key_entities_structured_v0.5`

## Decision

v0.2 is a strong near-miss, not a promoted SeizureFrequency candidate. It
improved the clinical-recovery headline from v0.1 `0.667` to `0.788` F1 with a
clean evidence gate, but remained just below the `0.8` target:

| Candidate | SeizureFrequency clinical F1 | Precision | Recall | Evidence validity |
| --- | ---: | ---: | ---: | ---: |
| v0.5 single structured prompt | 0.633 | 0.655 | 0.613 | 0.9684 |
| SeizureFrequency verifier v0.1 | 0.667 | 0.629 | 0.710 | 1.0000 |
| SeizureFrequency verifier v0.2 | 0.788 | 0.743 | 0.839 | 1.0000 |

The main lesson is architectural: the verifier path can recover SF recall while
repairing much of the over-emission created by a single broad structured prompt.
v0.3 should be a narrow residual pass, not a new architecture.

## Readout

The run had `0` call failures, `0` parse failures, and `35/35`
evidence-valid rendered mentions. Source-near overlap reached `0.818` F1.

The v0.2 changes strengthened the named-seizure-frequency gate and added
examples for unlabelled episodes/events, previous-event traps, teenage-years
seizure-free rendering, cluster-plus-rate extraction, and drug-change
seizure-free handling.

## Next Iteration

The residual errors are narrow enough for one more dev25 iteration: suppress
`NumberOfSeizures="unknown"`, previous generic seizure events, unlabelled
episodes/events rates, and non-myoclonic jerks; recover generic seizure
improvement after drug change and duplicated independently supported
focal-to-bilateral seizure-free states.
