# ExECTv2 Clinical-Recovery Error Ledger

- Generated: `2026-06-22`
- JSON: `experiments\exectv2_v094_qwen_reparse_dev1_error_ledger_20260622.json`
- Split: `dev`
- Letters: 1
- Structured JSONL: `experiments\exectv2_holistic_finding_assembly_v094_qwen_reparse_dev1_20260621.jsonl`
- Diagnosis JSONL: `None`
- SeizureFrequency JSONL: `None`
- Investigations JSONL: `None`

## Headline Scores

| Entity | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 1.000 | 1.000 | 1.000 | 2 | 0 | 0 |
| Diagnosis | 0.571 | 0.500 | 0.667 | 2 | 2 | 1 |
| SeizureFrequency | 1.000 | 1.000 | 1.000 | 2 | 0 | 0 |
| Investigations | 1.000 | 1.000 | 1.000 | 1 | 0 | 0 |

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
| 1 | `["Diagnosis", "focal seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0002 |
| 1 | `["Diagnosis", "temporal lobe epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | temporal-lobe-epilepsy | EA0002 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["Diagnosis", "focal epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | probable focal epilepsy | EA0002 |

## SeizureFrequency

### Residual By State

| Side | active-rate | seizure-free | unknown |
| --- | ---: | ---: | ---: |
| gold | 0 | 0 | 0 |
| predicted | 0 | 0 | 0 |

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 0 |  |  |  |

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
