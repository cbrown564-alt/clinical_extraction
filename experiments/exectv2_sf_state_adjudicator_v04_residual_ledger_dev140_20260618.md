# ExECTv2 SF State Adjudicator v0.4 Residual Ledger

- Generated: `2026-06-18`
- JSON: `experiments\exectv2_sf_state_adjudicator_v04_residual_ledger_dev140_20260618.json`
- JSONL: `experiments\exectv2_hybrid_sf_state_adjudicator_v04_dev140_gpt41mini_20260618.jsonl`
- Split: `dev`
- Letters: 140

## Headline

| Component | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| clinical_headline | 0.707 | 0.704 | 0.711 | 133 | 56 | 54 |
| active_rate | 0.746 | 0.692 | 0.809 | 72 | 32 | 17 |
| seizure_free | 0.738 | 0.789 | 0.692 | 45 | 12 | 20 |
| unknown | 0.525 | 0.571 | 0.485 | 16 | 12 | 17 |

## Residual By State

| State | Gold misses | Predicted over-emissions |
| --- | ---: | ---: |
| active-rate | 17 | 32 |
| seizure-free | 20 | 12 |
| unknown | 17 | 12 |

## Top Gold Misses

| Count | State | Key | Example | Letters |
| ---: | --- | --- | --- | --- |
| 12 | seizure-free | `[["cui", "C0036572"], "seizure-free"]` | seizures | EA0063, EA0068, EA0075, EA0137, EA0143, EA0162, EA0168, EA0173, ... |
| 6 | unknown | `[["cui", "C0036572"], "unknown"]` | seizures | EA0106, EA0108, EA0111, EA0121, EA0123, EA0198 |
| 4 | active-rate | `[["cui", "C0036572"], "active-rate"]` | seizure | EA0108, EA0119, EA0169, EA0181 |
| 4 | active-rate | `[["cui", "C0494475"], "active-rate"]` | generalised-tonic-clonic-seizures | EA0006, EA0038, EA0096, EA0139 |
| 4 | seizure-free | `[["cui", "C1299590"], "seizure-free"]` | seizure-free | EA0127, EA0176, EA0180, EA0190 |
| 3 | seizure-free | `[["cui", "C0877017"], "seizure-free"]` | focal-to-bilateral-convulsive-seizure | EA0011, EA0061, EA0121 |
| 3 | unknown | `[["cui", "C0563606"], "unknown"]` | absence | EA0049, EA0050, EA0082 |
| 2 | active-rate | `[["cui", "C0027066"], "active-rate"]` | myoclonic-jerks | EA0049, EA0050 |
| 2 | active-rate | `[["cui", "C0270834"], "active-rate"]` | focal-seizures-with-altered-awareness | EA0054, EA0158 |
| 2 | active-rate | `[["cui", "C0877017"], "active-rate"]` | focal-to-bilateral-convulsive-seizures | EA0054 |
| 2 | unknown | `[["cui", "C0027066"], "unknown"]` | myoclonic-jerks | EA0049, EA0128 |
| 2 | unknown | `[["cui", "C0270834"], "unknown"]` | dyscognitive-seizures | EA0169, EA0181 |
| 2 | unknown | `[["cui", "C0494475"], "unknown"]` | generalised | EA0087, EA0161 |
| 1 | active-rate | `[["cui", "C0270838"], "active-rate"]` | secondary-generalised-seizures | EA0056 |
| 1 | active-rate | `[["cui", "C0563606"], "active-rate"]` | absence | EA0124 |

## Top Predicted Over-Emissions

| Count | State | Key | Example | Letters |
| ---: | --- | --- | --- | --- |
| 13 | active-rate | `[["cui", "C0036572"], "active-rate"]` | seizures | EA0052, EA0062, EA0085, EA0104, EA0129, EA0141, EA0142, EA0148, ... |
| 5 | active-rate | `[["cui", "C0494475"], "active-rate"]` | Generalised tonic clonic seizure | EA0005, EA0021, EA0146, EA0162, EA0183 |
| 5 | seizure-free | `[["cui", "C0036572"], "seizure-free"]` | seizure | EA0071, EA0087, EA0160, EA0171, EA0190 |
| 4 | unknown | `[["cui", "C0036572"], "unknown"]` | seizures | EA0040, EA0096, EA0135, EA0199 |
| 3 | seizure-free | `[["cui", "C1299590"], "seizure-free"]` | seizure free | EA0038, EA0143 |
| 2 | active-rate | `[["phrase", "focal dyscognitive seizures"], "active-rate"]` | focal dyscognitive seizures | EA0169, EA0181 |
| 2 | unknown | `[["cui", "C0016399"], "unknown"]` | focal motor seizures | EA0158, EA0186 |
| 2 | unknown | `[["cui", "C0270834"], "unknown"]` | focal seizures with altered awareness | EA0121, EA0158 |
| 2 | unknown | `[["cui", "C0494475"], "unknown"]` | generalised tonic clonic seizures | EA0096, EA0131 |
| 1 | active-rate | `[["cui", "C0016399"], "active-rate"]` | focal motor seizures | EA0057 |
| 1 | active-rate | `[["cui", "C0149958"], "active-rate"]` | complex partial seizures | EA0092 |
| 1 | active-rate | `[["cui", "C0270838"], "active-rate"]` | secondarily generalised seizures | EA0143 |
| 1 | active-rate | `[["cui", "C0751495"], "active-rate"]` | focal seizures | EA0109 |
| 1 | active-rate | `[["cui", "C0877017"], "active-rate"]` | focal to bilateral convulsive seizures | EA0121 |
| 1 | active-rate | `[["phrase", "absence events"], "active-rate"]` | absence events | EA0124 |
