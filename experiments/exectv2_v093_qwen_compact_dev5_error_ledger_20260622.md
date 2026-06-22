# ExECTv2 Clinical-Recovery Error Ledger

- Generated: `2026-06-22`
- JSON: `experiments\exectv2_v093_qwen_compact_dev5_error_ledger_20260622.json`
- Split: `dev`
- Letters: 5
- Structured JSONL: `experiments\exectv2_holistic_finding_assembly_v093_qwen_compact_dev5_20260621.jsonl`
- Diagnosis JSONL: `None`
- SeizureFrequency JSONL: `None`
- Investigations JSONL: `None`

## Headline Scores

| Entity | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.875 | 1.000 | 0.778 | 7 | 0 | 2 |
| Diagnosis | 0.210 | 0.250 | 0.182 | 2 | 6 | 9 |
| SeizureFrequency | 0.625 | 0.625 | 0.625 | 5 | 3 | 3 |
| Investigations | 1.000 | 1.000 | 1.000 | 8 | 0 | 0 |

## Prescription

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["ordinary", "carbamazepine", "200", "mg", "2"]` | Carbamazepine-200-mg-twice-a-day | EA0005 |
| 1 | `["ordinary", "phenytoin", "75", "mg", "3"]` | Phenytoin- | EA0007 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 0 |  |  |  |

## Diagnosis

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 4 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised-tonic-clonic-seizure | EA0005, EA0006 |
| 2 | `["Diagnosis", "focal seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0002 |
| 1 | `["Diagnosis", "epilepsy with generalised tonic clonic seizures alone", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epilepsy-with-generalised-tonic-clonic-seizure-alone | EA0005 |
| 1 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0007 |
| 1 | `["Diagnosis", "focal epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | focal-onset-epilepsy | EA0007 |
| 1 | `["Diagnosis", "focal epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal-epilepsy | EA0004 |
| 1 | `["Diagnosis", "generalised epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | generalised-epilepsy | EA0006 |
| 1 | `["Diagnosis", "secondary generalised seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | secondary-generalised-seizures | EA0002 |
| 1 | `["Diagnosis", "temporal lobe epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | temporal-lobe-epilepsy | EA0002 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["Diagnosis", "focal", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal | EA0004 |
| 1 | `["Diagnosis", "generalised", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | possibly generalised | EA0006 |

## SeizureFrequency

### Residual By State

| Side | active-rate | seizure-free | unknown |
| --- | ---: | ---: | ---: |
| gold | 4 | 1 | 0 |
| predicted | 1 | 0 | 2 |

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 2 | `[["cui", "C0036572"], "active-rate"]` | seizures | EA0005, EA0007 |
| 1 | `[["cui", "C0494475"], "active-rate"]` | generalised-tonic-clonic-seizures | EA0006 |
| 1 | `[["cui", "C0494475"], "seizure-free"]` | generalised-tonic-clonic-seizure | EA0005 |
| 1 | `[["cui", "C0751495"], "active-rate"]` | focal-seizures | EA0002 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `[["cui", "C0494475"], "unknown"]` | Generalised tonic clonic seizure | EA0005 |
| 1 | `[["cui", "C0751495"], "unknown"]` | focal seizures | EA0002 |
| 1 | `[["phrase", "roughly two seizures"], "active-rate"]` | roughly two seizures | EA0005 |

## Investigations

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 0 |  |  |  |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 0 |  |  |  |
