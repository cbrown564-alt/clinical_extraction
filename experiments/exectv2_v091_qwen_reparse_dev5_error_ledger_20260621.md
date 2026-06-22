# ExECTv2 Clinical-Recovery Error Ledger

- Generated: `2026-06-21`
- JSON: `experiments\exectv2_v091_qwen_reparse_dev5_error_ledger_20260621.json`
- Split: `dev`
- Letters: 5
- Structured JSONL: `experiments\exectv2_llm_only_key_entities_structured_v091_reparse_dev5_qwen36_35b_ollama_autogpu_ctx16384_20260621.jsonl`
- Diagnosis JSONL: `None`
- SeizureFrequency JSONL: `None`
- Investigations JSONL: `None`

## Headline Scores

| Entity | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 1.000 | 1.000 | 1.000 | 9 | 0 | 0 |
| Diagnosis | 0.538 | 0.467 | 0.636 | 7 | 8 | 4 |
| SeizureFrequency | 0.875 | 0.875 | 0.875 | 7 | 1 | 1 |
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
| 2 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised-tonic-clonic-seizure | EA0005, EA0006 |
| 1 | `["Diagnosis", "epilepsy with generalised tonic clonic seizures alone", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epilepsy-with-generalised-tonic-clonic-seizure-alone | EA0005 |
| 1 | `["Diagnosis", "focal epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | focal-onset-epilepsy | EA0007 |
| 1 | `["Diagnosis", "focal epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal-epilepsy | EA0004 |
| 1 | `["Diagnosis", "focal seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0002 |
| 1 | `["Diagnosis", "generalised epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | generalised-epilepsy | EA0006 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 2 | `["Diagnosis", "focal", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | probable focal | EA0004, EA0007 |
| 1 | `["Diagnosis", "absence like seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | absence like seizures | EA0006 |
| 1 | `["Diagnosis", "epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | Epilepsy | EA0006 |
| 1 | `["Diagnosis", "generalised", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | generalised | EA0006 |
| 1 | `["Diagnosis", "seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | seizures | EA0007 |

## SeizureFrequency

### Residual By State

| Side | active-rate | seizure-free | unknown |
| --- | ---: | ---: | ---: |
| gold | 3 | 0 | 0 |
| predicted | 0 | 0 | 1 |

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `[["cui", "C0036572"], "active-rate"]` | seizures | EA0007 |
| 1 | `[["cui", "C0494475"], "active-rate"]` | generalised-tonic-clonic-seizures | EA0006 |
| 1 | `[["cui", "C0563606"], "active-rate"]` | absence-like-seizures | EA0006 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `[["cui", "C0563606"], "unknown"]` | absence like seizures | EA0006 |

## Investigations

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 0 |  |  |  |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 0 |  |  |  |
