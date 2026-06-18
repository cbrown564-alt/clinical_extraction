# ExECTv2 SeizureFrequency Verifier v0.1 Pilot

Date: 2026-06-18  
Split: dev25 only  
Pipeline: `exectv2_llm_sf_verifier`  
Model: `openai/gpt-4.1-mini`  
Draft source: `exectv2_llm_only_key_entities_structured_v0.5`

## Decision

v0.1 is a clean diagnostic improvement, but not a promoted SeizureFrequency
candidate. It improves the objective-aligned SeizureFrequency clinical-recovery
headline from the v0.5 single structured prompt's `0.633` F1 to `0.667`, but
remains below the `0.8` target and traded precision for recall:

| Candidate | SeizureFrequency clinical F1 | Precision | Recall | Evidence validity |
| --- | ---: | ---: | ---: | ---: |
| v0.5 single structured prompt | 0.633 | 0.655 | 0.613 | 0.9684 |
| SeizureFrequency verifier v0.1 | 0.667 | 0.629 | 0.710 | 1.0000 |

This supports the multi-prompt verifier path as a useful diagnostic layer, but
not yet as the final key-family architecture. v0.2 should be residual-error-led
and should specifically recover precision while preserving the recall gains.

## Readout

The run had `0` call failures, `0` parse failures, and `35/35`
evidence-valid rendered mentions. Source-near overlap was `0.727` F1 with
`0.774` recall.

The v0.1 prompt targeted the observed dev25 residuals from the single structured
v0.5 run: clean text over source typos such as `tonic chronic`, `several` and
`a few` count conventions, duplicated independently supported mentions,
single-event suppression, generic episode suppression, and drug-change
seizure-free handling.

## Next Iteration

Run residual analysis before adding prompt rules. The important v0.2 question is
whether the verifier can distinguish clinically meaningful SeizureFrequency
states from tempting but unscored frequency-like language without losing the
active-rate and seizure-free recalls it recovered.
