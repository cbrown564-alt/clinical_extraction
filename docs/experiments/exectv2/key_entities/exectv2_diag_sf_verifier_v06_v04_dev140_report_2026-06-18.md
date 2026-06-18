# ExECTv2 Diagnosis v0.6 and SeizureFrequency v0.4 dev140

Date: 2026-06-18  
Split: dev140  
Model: `openai/gpt-4.1-mini`  
Substrate: `exectv2_llm_only_key_entities_structured_v0.5`

## Decision

Revise-only. The residual-led prompt iteration improves both remaining families
on dev140, but neither clears the `0.8` clinical-recovery target.

| Family | Previous dev140 | New dev140 | Gate |
| --- | ---: | ---: | --- |
| Diagnosis verifier v0.5 -> v0.6 | 0.616 | 0.651 | 0 call failures, 0 parse failures, evidence 0.9906 |
| SeizureFrequency verifier v0.3 -> v0.4 | 0.602 | 0.623 | 0 call failures, 0 parse failures, evidence 0.9905 |

## Interpretation

Diagnosis v0.6 targeted explicit multi-concept diagnosis headings, especially
generic epilepsy plus focal/generalised/symptomatic concepts. It recovered some
generic epilepsy and structural focal epilepsy misses, but the updated ledger
still shows 57 missed established generic epilepsy keys and persistent seizure
type/hierarchy misses.

SeizureFrequency v0.4 targeted headline-state anchors rather than exact rate
formatting: generic returned-seizure states, duplicate seizure-free anchors, and
numeric fragments rendered as seizure anchors. It improved recall, but the
updated ledger still shows generic seizure unknown/seizure-free/active-rate
state confusion and named-type active-rate/unknown confusion.

## Next Architecture

Do not keep accreting broad rules into the same verifier prompt. For Diagnosis,
split the task into a diagnosis-heading decomposer and a narrative seizure-type
collector, then reconcile duplicates. For SeizureFrequency, build a candidate
span/state adjudicator that classifies candidate spans into `active-rate`,
`seizure-free`, `unknown`, or `reject`, with text-anchor normalization as an
explicit output field.

Updated residual ledger:
`experiments/exectv2_key_entities_clinical_error_ledger_diagv06_sfv04_dev140_20260618.md`.
