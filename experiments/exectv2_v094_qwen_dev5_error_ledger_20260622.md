# ExECTv2 Clinical-Recovery Error Ledger

- Generated: `2026-06-22`
- JSON: `experiments\exectv2_v094_qwen_dev5_error_ledger_20260622.json`
- Split: `dev`
- Letters: 5
- Structured JSONL: `experiments\exectv2_holistic_finding_assembly_v094_qwen_dev5_20260621.jsonl`
- Diagnosis JSONL: `None`
- SeizureFrequency JSONL: `None`
- Investigations JSONL: `None`

## Headline Scores

| Entity | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 1.000 | 1.000 | 1.000 | 9 | 0 | 0 |
| Diagnosis | 0.783 | 0.750 | 0.818 | 9 | 3 | 2 |
| SeizureFrequency | 0.933 | 1.000 | 0.875 | 7 | 0 | 1 |
| Investigations | 1.000 | 1.000 | 1.000 | 8 | 0 | 0 |

## Prescription

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 0 |  |  |  |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 0 |  |  |  |

## Diagnosis

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 2 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0006, EA0007 |
| 1 | `["Diagnosis", "epilepsy with generalised tonic clonic seizures alone", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy-with-generalised-tonic-clonic-seizures-alone | EA0005 |
| 1 | `["Diagnosis", "focal epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | focal-onset-epilepsy | EA0007 |
| 1 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised-tonic-clonic-seizure | EA0005 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 2 | `["Diagnosis", "absence like seizure", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | absence like seizure | EA0006 |
| 1 | `["Diagnosis", "absence like episode", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | absence-like episode | EA0006 |
| 1 | `["Diagnosis", "epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | Epilepsy | EA0006 |

## SeizureFrequency

### Residual By State

| Side | active-rate | seizure-free | unknown |
| --- | ---: | ---: | ---: |
| gold | 2 | 0 | 0 |
| predicted | 0 | 0 | 0 |

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `[["cui", "C0036572"], "active-rate"]` | seizures | EA0007 |
| 1 | `[["cui", "C0563606"], "active-rate"]` | absence-like-seizures | EA0006 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 0 |  |  |  |

## Investigations

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 0 |  |  |  |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 0 |  |  |  |
