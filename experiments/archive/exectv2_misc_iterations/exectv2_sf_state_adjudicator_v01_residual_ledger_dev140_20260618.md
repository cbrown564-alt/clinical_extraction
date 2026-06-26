# ExECTv2 SF State Adjudicator v0.1 Residual Ledger

- Generated: `2026-06-18`
- JSON: `experiments\exectv2_sf_state_adjudicator_v01_residual_ledger_dev140_20260618.json`
- JSONL: `experiments\exectv2_hybrid_sf_state_adjudicator_v01_dev140_gpt41mini_20260618.jsonl`
- Split: `dev`
- Letters: 140

## Headline

| Component | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| clinical_headline | 0.674 | 0.653 | 0.695 | 130 | 69 | 57 |
| active_rate | 0.726 | 0.652 | 0.820 | 73 | 39 | 16 |
| seizure_free | 0.734 | 0.746 | 0.723 | 47 | 16 | 18 |
| unknown | 0.351 | 0.417 | 0.303 | 10 | 14 | 23 |

## Residual By State

| State | Gold misses | Predicted over-emissions |
| --- | ---: | ---: |
| active-rate | 16 | 39 |
| seizure-free | 18 | 16 |
| unknown | 23 | 14 |

## Top Gold Misses

| Count | State | Key | Example | Letters |
| ---: | --- | --- | --- | --- |
| 11 | unknown | `[["cui", "C0036572"], "unknown"]` | seizures | EA0050, EA0059, EA0106, EA0108, EA0111, EA0121, EA0123, EA0131 |
| 10 | seizure-free | `[["cui", "C0036572"], "seizure-free"]` | seizures | EA0063, EA0137, EA0143, EA0162, EA0168, EA0173, EA0180, EA0182 |
| 5 | active-rate | `[["cui", "C0036572"], "active-rate"]` | seizure | EA0108, EA0113, EA0117, EA0119, EA0154 |
| 4 | active-rate | `[["cui", "C0494475"], "active-rate"]` | generalised-tonic-clonic-seizures | EA0006, EA0079, EA0096, EA0139 |
| 4 | seizure-free | `[["cui", "C1299590"], "seizure-free"]` | seizure-free | EA0127, EA0176, EA0180, EA0190 |
| 3 | seizure-free | `[["cui", "C0877017"], "seizure-free"]` | focal-to-bilateral-convulsive-seizure | EA0011, EA0061, EA0121 |
| 3 | unknown | `[["cui", "C0563606"], "unknown"]` | absence | EA0049, EA0050, EA0082 |
| 3 | unknown | `[["cui", "C0494475"], "unknown"]` | generalised | EA0087, EA0123, EA0161 |
| 2 | active-rate | `[["cui", "C0027066"], "active-rate"]` | myoclonic-jerks | EA0049, EA0050 |
| 2 | unknown | `[["cui", "C0027066"], "unknown"]` | myoclonic-jerks | EA0049, EA0128 |
| 2 | active-rate | `[["cui", "C0877017"], "active-rate"]` | focal-to-bilateral-convulsive-seizures | EA0054 |
| 2 | unknown | `[["cui", "C0270834"], "unknown"]` | dyscognitive-seizures | EA0169, EA0181 |
| 1 | active-rate | `[["cui", "C0270834"], "active-rate"]` | focal-seizures-with-altered-awareness | EA0054 |
| 1 | active-rate | `[["cui", "C0270838"], "active-rate"]` | secondary-generalised-seizures | EA0056 |
| 1 | unknown | `[["cui", "C0751495"], "unknown"]` | focal-seizures | EA0068 |

## Top Predicted Over-Emissions

| Count | State | Key | Example | Letters |
| ---: | --- | --- | --- | --- |
| 18 | active-rate | `[["cui", "C0036572"], "active-rate"]` | seizures | EA0021, EA0052, EA0062, EA0079, EA0085, EA0104, EA0110, EA0129 |
| 9 | seizure-free | `[["cui", "C0036572"], "seizure-free"]` | seizures | EA0016, EA0024, EA0035, EA0071, EA0085, EA0116, EA0123, EA0171 |
| 7 | unknown | `[["cui", "C0036572"], "unknown"]` | seizures | EA0040, EA0079, EA0096, EA0117, EA0135, EA0166, EA0190 |
| 5 | seizure-free | `[["cui", "C1299590"], "seizure-free"]` | seizure free | EA0038, EA0087, EA0104, EA0143 |
| 3 | unknown | `[["cui", "C0494475"], "unknown"]` | generalised tonic clonic seizures | EA0096, EA0131, EA0139 |
| 3 | active-rate | `[["cui", "C0494475"], "active-rate"]` | grand mal | EA0146, EA0162, EA0200 |
| 1 | active-rate | `[["phrase", "febrile seizure"], "active-rate"]` | febrile seizure | EA0043 |
| 1 | unknown | `[["phrase", "seizure clusters"], "unknown"]` | seizure clusters | EA0050 |
| 1 | active-rate | `[["cui", "C0016399"], "active-rate"]` | focal motor seizures | EA0057 |
| 1 | active-rate | `[["phrase", "dissociative seizures"], "active-rate"]` | dissociative seizures | EA0057 |
| 1 | seizure-free | `[["cui", "C0751495"], "seizure-free"]` | focal seizures | EA0059 |
| 1 | active-rate | `[["phrase", "focal to bilateral seizures"], "active-rate"]` | focal to bilateral seizures | EA0061 |
| 1 | active-rate | `[["phrase", "seizure like episodes"], "active-rate"]` | seizure-like episodes | EA0076 |
| 1 | unknown | `[["cui", "C0027066"], "unknown"]` | myoclonic jerks | EA0087 |
| 1 | active-rate | `[["cui", "C0149958"], "active-rate"]` | complex partial seizures | EA0092 |
