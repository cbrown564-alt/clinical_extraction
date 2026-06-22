# ExECTv2 Clinical-Recovery Error Ledger

- Generated: `2026-06-21`
- JSON: `experiments\exectv2_v09_qwen_dev5_error_ledger_20260621.json`
- Split: `dev`
- Letters: 5
- Structured JSONL: `experiments\exectv2_llm_only_key_entities_structured_v09_dev5_qwen36_35b_ollama_autogpu_ctx16384_20260621.jsonl`
- Diagnosis JSONL: `None`
- SeizureFrequency JSONL: `None`
- Investigations JSONL: `None`

## Headline Scores

| Entity | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.941 | 1.000 | 0.889 | 8 | 0 | 1 |
| Diagnosis | 0.381 | 0.400 | 0.364 | 4 | 6 | 7 |
| SeizureFrequency | 0.778 | 0.700 | 0.875 | 7 | 3 | 1 |
| Investigations | 1.000 | 1.000 | 1.000 | 8 | 0 | 0 |

## Prescription

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["ordinary", "phenytoin", "75", "mg", "3"]` | Phenytoin- | EA0007 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 0 |  |  |  |

## Diagnosis

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 4 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0004, EA0006, EA0007 |
| 1 | `["Diagnosis", "epilepsy with generalised tonic clonic seizures alone", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epilepsy-with-generalised-tonic-clonic-seizure-alone | EA0005 |
| 1 | `["Diagnosis", "epilepsy with generalised tonic clonic seizures alone", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy-with-generalised-tonic-clonic-seizures-alone | EA0005 |
| 1 | `["Diagnosis", "focal epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | focal-onset-epilepsy | EA0007 |
| 1 | `["Diagnosis", "focal epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal-epilepsy | EA0004 |
| 1 | `["Diagnosis", "focal epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-epilepsy | EA0002 |
| 1 | `["Diagnosis", "generalised epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | generalised-epilepsy | EA0006 |
| 1 | `["Diagnosis", "genetic generalised epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | genetic-generalised-epilepsy | EA0005 |
| 1 | `["Diagnosis", "temporal lobe epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | temporal-lobe-epilepsy | EA0002 |
| 1 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised-tonic-clonic-seizures | EA0006 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["Diagnosis", "absence like seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | absence-like seizures | EA0006 |
| 1 | `["Diagnosis", "convulsive seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | convulsive seizures | EA0002 |
| 1 | `["Diagnosis", "epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | epilepsy | EA0006 |
| 1 | `["Diagnosis", "focal epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal epilepsy | EA0002 |
| 1 | `["Diagnosis", "focal", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | probable focal | EA0004 |
| 1 | `["Diagnosis", "generalised epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised epilepsy | EA0005 |

## SeizureFrequency

### Residual By State

| Side | active-rate | seizure-free | unknown |
| --- | ---: | ---: | ---: |
| gold | 2 | 1 | 0 |
| predicted | 1 | 2 | 0 |

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `[["cui", "C0036572"], "active-rate"]` | seizures | EA0007 |
| 1 | `[["cui", "C0494475"], "active-rate"]` | generalised-tonic-clonic-seizures | EA0006 |
| 1 | `[["cui", "C0494475"], "seizure-free"]` | generalised-tonic-clonic-seizure | EA0005 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `[["cui", "C0036572"], "seizure-free"]` | seizure | EA0005 |
| 1 | `[["cui", "C0494475"], "active-rate"]` | Generalised tonic clonic seizure | EA0005 |
| 1 | `[["cui", "C1299590"], "seizure-free"]` | seizure free | EA0006 |

## Investigations

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 0 |  |  |  |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 0 |  |  |  |
