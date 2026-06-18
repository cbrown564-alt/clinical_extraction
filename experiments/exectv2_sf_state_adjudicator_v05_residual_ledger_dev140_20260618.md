# ExECTv2 SF State Adjudicator v0.5 Residual Ledger

- Generated: `2026-06-18`
- JSON: `experiments\exectv2_sf_state_adjudicator_v05_residual_ledger_dev140_20260618.json`
- JSONL: `experiments\exectv2_hybrid_sf_state_adjudicator_v05_dev140_gpt41mini_20260618.jsonl`
- Split: `dev`
- Letters: 140

## Headline

| Component | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| clinical_headline | 0.721 | 0.710 | 0.733 | 137 | 56 | 50 |
| active_rate | 0.762 | 0.720 | 0.809 | 72 | 28 | 17 |
| seizure_free | 0.781 | 0.794 | 0.769 | 50 | 13 | 15 |
| unknown | 0.476 | 0.500 | 0.455 | 15 | 15 | 18 |

## Residual By State

| State | Gold misses | Predicted over-emissions |
| --- | ---: | ---: |
| active-rate | 17 | 28 |
| seizure-free | 15 | 13 |
| unknown | 18 | 15 |

## Top Gold Misses

| Count | State | Key | Example | Letters |
| ---: | --- | --- | --- | --- |
| 6 | unknown | `(('cui', 'C0036572'), 'unknown')` | seizures | EA0022, EA0106, EA0108, EA0111, EA0121, EA0123, EA0198 |
| 6 | seizure-free | `(('cui', 'C0036572'), 'seizure-free')` | seizure | EA0063, EA0137, EA0143, EA0162, EA0168, EA0180, EA0182, EA0191 |
| 3 | seizure-free | `(('cui', 'C0036572'), 'seizure-free')` | seizures | EA0063, EA0137, EA0143, EA0162, EA0168, EA0180, EA0182, EA0191 |
| 3 | active-rate | `(('cui', 'C0036572'), 'active-rate')` | seizures | EA0108, EA0117, EA0119, EA0169, EA0181 |
| 2 | active-rate | `(('cui', 'C0494475'), 'active-rate')` | generalised-tonic-clonic-seizures | EA0006, EA0038, EA0096 |
| 2 | seizure-free | `(('cui', 'C0877017'), 'seizure-free')` | focal-to-bilateral-convulsive-seizure | EA0011, EA0121 |
| 2 | active-rate | `(('cui', 'C0027066'), 'active-rate')` | myoclonic-jerks | EA0049, EA0050 |
| 2 | unknown | `(('cui', 'C0027066'), 'unknown')` | myoclonic-jerks | EA0049, EA0128 |
| 2 | unknown | `(('cui', 'C0563606'), 'unknown')` | absences | EA0049, EA0050, EA0082 |
| 2 | active-rate | `(('cui', 'C0270834'), 'active-rate')` | focal-seizures-with-altered-awareness | EA0054, EA0158 |
| 2 | active-rate | `(('cui', 'C0877017'), 'active-rate')` | focal-to-bilateral-convulsive-seizures | EA0054 |
| 2 | active-rate | `(('cui', 'C0036572'), 'active-rate')` | seizure | EA0108, EA0117, EA0119, EA0169, EA0181 |
| 2 | unknown | `(('cui', 'C0270834'), 'unknown')` | dyscognitive-seizures | EA0169, EA0181 |
| 2 | seizure-free | `(('cui', 'C1299590'), 'seizure-free')` | seizure | EA0127, EA0180, EA0190 |
| 1 | active-rate | `(('cui', 'C0494475'), 'active-rate')` | generalised-tonic-clonic-seizure | EA0006, EA0038, EA0096 |

## Top Predicted Over-Emissions

| Count | State | Key | Example | Letters |
| ---: | --- | --- | --- | --- |
| 9 | active-rate | `(('cui', 'C0036572'), 'active-rate')` | seizures | EA0052, EA0062, EA0085, EA0104, EA0129, EA0142, EA0148, EA0153, EA0172, EA0182, EA0198 |
| 7 | unknown | `(('cui', 'C0036572'), 'unknown')` | seizures | EA0040, EA0079, EA0096, EA0117, EA0135, EA0166, EA0199 |
| 5 | seizure-free | `(('cui', 'C0036572'), 'seizure-free')` | seizures | EA0071, EA0113, EA0123, EA0160, EA0171, EA0190 |
| 3 | seizure-free | `(('cui', 'C1299590'), 'seizure-free')` | seizure free | EA0006, EA0038, EA0087, EA0104, EA0143 |
| 3 | active-rate | `(('cui', 'C0494475'), 'active-rate')` | generalised tonic clonic seizures | EA0021, EA0146, EA0162, EA0183, EA0200 |
| 2 | unknown | `(('cui', 'C0494475'), 'unknown')` | generalised tonic clonic seizures | EA0096, EA0131 |
| 2 | unknown | `(('cui', 'C0270834'), 'unknown')` | focal seizures with altered awareness | EA0121, EA0158 |
| 2 | seizure-free | `(('cui', 'C1299590'), 'seizure-free')` | seizure-free | EA0006, EA0038, EA0087, EA0104, EA0143 |
| 2 | unknown | `(('cui', 'C0016399'), 'unknown')` | focal motor seizures | EA0158, EA0186 |
| 2 | active-rate | `(('cui', 'C0270834'), 'active-rate')` | focal dyscognitive seizures | EA0114, EA0169, EA0181 |
| 2 | active-rate | `(('cui', 'C0036572'), 'active-rate')` | seizure | EA0052, EA0062, EA0085, EA0104, EA0129, EA0142, EA0148, EA0153, EA0172, EA0182, EA0198 |
| 1 | active-rate | `(('phrase', 'absences and jerks'), 'active-rate')` | absences and jerks | EA0047 |
| 1 | active-rate | `(('cui', 'C0016399'), 'active-rate')` | focal motor seizures | EA0057 |
| 1 | active-rate | `(('phrase', 'dissociative seizures'), 'active-rate')` | dissociative seizures | EA0057 |
| 1 | seizure-free | `(('cui', 'C0036572'), 'seizure-free')` | seizure | EA0071, EA0113, EA0123, EA0160, EA0171, EA0190 |
