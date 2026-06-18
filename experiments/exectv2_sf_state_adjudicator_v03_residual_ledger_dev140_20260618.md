# ExECTv2 SF State Adjudicator v0.3 Residual Ledger

- Generated: `2026-06-18`
- JSON: `experiments\exectv2_sf_state_adjudicator_v03_residual_ledger_dev140_20260618.json`
- JSONL: `experiments\exectv2_hybrid_sf_state_adjudicator_v03_dev140_gpt41mini_20260618.jsonl`
- Split: `dev`
- Letters: 140

## Headline

| Component | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| clinical_headline | 0.681 | 0.667 | 0.695 | 130 | 65 | 57 |
| active_rate | 0.722 | 0.667 | 0.787 | 70 | 35 | 19 |
| seizure_free | 0.754 | 0.807 | 0.708 | 46 | 11 | 19 |
| unknown | 0.424 | 0.424 | 0.424 | 14 | 19 | 19 |

## Residual By State

| State | Gold misses | Predicted over-emissions |
| --- | ---: | ---: |
| active-rate | 19 | 35 |
| seizure-free | 19 | 11 |
| unknown | 19 | 19 |

## Top Gold Misses

| Count | State | Key | Example | Letters |
| ---: | --- | --- | --- | --- |
| 11 | seizure-free | `[["cui", "C0036572"], "seizure-free"]` | seizures | EA0063, EA0075, EA0137, EA0143, EA0162, EA0168, EA0173, EA0180, ... |
| 7 | active-rate | `[["cui", "C0036572"], "active-rate"]` | seizure | EA0108, EA0117, EA0119, EA0151, EA0154, EA0169, EA0181 |
| 7 | unknown | `[["cui", "C0036572"], "unknown"]` | seizures | EA0106, EA0108, EA0111, EA0119, EA0121, EA0123, EA0198 |
| 4 | seizure-free | `[["cui", "C1299590"], "seizure-free"]` | seizure-free | EA0127, EA0176, EA0180, EA0190 |
| 3 | active-rate | `[["cui", "C0494475"], "active-rate"]` | generalised-tonic-clonic-seizures | EA0006, EA0096, EA0139 |
| 3 | seizure-free | `[["cui", "C0877017"], "seizure-free"]` | focal-to-bilateral-convulsive-seizure | EA0011, EA0061, EA0121 |
| 3 | unknown | `[["cui", "C0494475"], "unknown"]` | generalised | EA0087, EA0123, EA0161 |
| 3 | unknown | `[["cui", "C0563606"], "unknown"]` | absence | EA0049, EA0050, EA0082 |
| 2 | active-rate | `[["cui", "C0027066"], "active-rate"]` | myoclonic-jerks | EA0049, EA0050 |
| 2 | active-rate | `[["cui", "C0270834"], "active-rate"]` | focal-seizures-with-altered-awareness | EA0054, EA0158 |
| 2 | active-rate | `[["cui", "C0877017"], "active-rate"]` | focal-to-bilateral-convulsive-seizures | EA0054 |
| 2 | unknown | `[["cui", "C0027066"], "unknown"]` | myoclonic-jerks | EA0049, EA0128 |
| 2 | unknown | `[["cui", "C0270834"], "unknown"]` | dyscognitive-seizures | EA0169, EA0181 |
| 1 | active-rate | `[["cui", "C0270838"], "active-rate"]` | secondary-generalised-seizures | EA0056 |
| 1 | active-rate | `[["cui", "C0563606"], "active-rate"]` | absence | EA0124 |

## Top Predicted Over-Emissions

| Count | State | Key | Example | Letters |
| ---: | --- | --- | --- | --- |
| 11 | active-rate | `[["cui", "C0036572"], "active-rate"]` | seizures | EA0052, EA0062, EA0085, EA0129, EA0141, EA0142, EA0148, EA0153, ... |
| 6 | unknown | `[["cui", "C0036572"], "unknown"]` | seizures | EA0040, EA0096, EA0104, EA0117, EA0135, EA0199 |
| 5 | active-rate | `[["cui", "C0494475"], "active-rate"]` | Generalised tonic clonic seizure | EA0005, EA0021, EA0146, EA0162, EA0200 |
| 4 | seizure-free | `[["cui", "C0036572"], "seizure-free"]` | seizure | EA0071, EA0116, EA0123, EA0171 |
| 4 | seizure-free | `[["cui", "C1299590"], "seizure-free"]` | seizure free | EA0038, EA0087, EA0143 |
| 3 | unknown | `[["cui", "C0494475"], "unknown"]` | generalised tonic clonic seizures | EA0096, EA0131, EA0139 |
| 2 | active-rate | `[["phrase", "focal dyscognitive seizures"], "active-rate"]` | focal dyscognitive seizures | EA0169, EA0181 |
| 2 | unknown | `[["cui", "C0016399"], "unknown"]` | focal motor seizures | EA0158, EA0186 |
| 2 | unknown | `[["cui", "C0270834"], "unknown"]` | focal seizures with altered awareness | EA0121, EA0158 |
| 1 | active-rate | `[["cui", "C0016399"], "active-rate"]` | focal motor seizures | EA0057 |
| 1 | active-rate | `[["cui", "C0149958"], "active-rate"]` | complex partial seizures | EA0092 |
| 1 | active-rate | `[["cui", "C0270838"], "active-rate"]` | secondarily generalised seizures | EA0143 |
| 1 | active-rate | `[["cui", "C0751495"], "active-rate"]` | focal seizures | EA0109 |
| 1 | active-rate | `[["cui", "C0877017"], "active-rate"]` | focal to bilateral convulsive seizures | EA0121 |
| 1 | active-rate | `[["phrase", "absence events"], "active-rate"]` | absence events | EA0124 |
