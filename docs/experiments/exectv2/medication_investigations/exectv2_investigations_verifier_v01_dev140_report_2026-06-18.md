# ExECTv2 Investigations Verifier v0.1 dev140

Date: 2026-06-18  
Split: dev140  
Pipeline: `exectv2_llm_investigations_verifier`  
Model: `openai/gpt-4.1-mini`  
Draft source: `exectv2_llm_only_key_entities_structured_v0.5`

## Decision

v0.1 is the first Investigations-specific candidate to clear the dev140 target.
It improves the single structured v0.5 baseline from `0.786` to `0.872` F1 with
a clean gate:

| Candidate | Investigations F1 | Precision | Recall | Evidence validity |
| --- | ---: | ---: | ---: | ---: |
| single structured v0.5 | 0.786 | 0.752 | 0.824 | 0.9563 overall draft |
| combined medication/investigations verifier v0.1 | 0.496 | 0.408 | 0.632 | 0.9792 |
| Investigations verifier v0.1 | 0.872 | 0.869 | 0.875 | 0.9928 |

This confirms the task-decomposition lesson from the failed combined verifier:
Investigations should have its own small adjudication prompt focused on
performed-vs-planned tests and result extraction.

## Readout

The run had `0` call failures, `0` parse failures, and `137/138`
evidence-valid rendered mentions. Clinical-recovery counts were TP `119`, FP
`18`, FN `17`.

The v0.1 prompt targeted the dev140 ledger residuals: suppressing planned MRI/EEG
or modality-only test mentions, and recovering explicit normal/abnormal results
from MRI, CT, EEG, video EEG, and sleep-deprived EEG phrases.

## Next Step

Use Investigations verifier v0.1 as the current dev140 Investigations candidate.
The remaining below-target key families are Diagnosis and SeizureFrequency.
