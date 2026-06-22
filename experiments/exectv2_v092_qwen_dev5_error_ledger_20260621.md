# ExECTv2 Clinical-Recovery Error Ledger

- Generated: `2026-06-21`
- JSON: `experiments\exectv2_v092_qwen_dev5_error_ledger_20260621.json`
- Split: `dev`
- Letters: 5
- Structured JSONL: `experiments\exectv2_llm_only_key_entities_structured_v092_dev5_qwen36_35b_ollama_autogpu_ctx16384_20260621.jsonl`
- Diagnosis JSONL: `None`
- SeizureFrequency JSONL: `None`
- Investigations JSONL: `None`

## Headline Scores

| Entity | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.889 | 0.889 | 0.889 | 8 | 1 | 1 |
| Diagnosis | 0.417 | 0.385 | 0.455 | 5 | 8 | 6 |
| SeizureFrequency | 0.941 | 0.889 | 1.000 | 8 | 1 | 0 |
| Investigations | 1.000 | 1.000 | 1.000 | 8 | 0 | 0 |

## Prescription

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["ordinary", "levetiracetam", "500", "mg", "1"]` | levetiracetam- | EA0007 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["ordinary", "levetiracetam", "500", "mg", "2"]` | 500 mg nocte | EA0007 |

## Diagnosis

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 2 | `["Diagnosis", "focal seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0002 |
| 1 | `["Diagnosis", "epilepsy with generalised tonic clonic seizures alone", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy-with-generalised-tonic-clonic-seizures-alone | EA0005 |
| 1 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0007 |
| 1 | `["Diagnosis", "focal epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | focal-onset-epilepsy | EA0007 |
| 1 | `["Diagnosis", "focal epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal-epilepsy | EA0004 |
| 1 | `["Diagnosis", "secondary generalised seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | secondary-generalised-seizures | EA0002 |
| 1 | `["Diagnosis", "temporal lobe epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | temporal-lobe-epilepsy | EA0002 |
| 1 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised-tonic-clonic-seizures | EA0006 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["Diagnosis", "absence like seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | absence-like seizures | EA0006 |
| 1 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0005 |
| 1 | `["Diagnosis", "focal", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal | EA0004 |
| 1 | `["Diagnosis", "temporal lobe", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | probable temporal lobe | EA0002 |
| 1 | `["Diagnosis", "unclassified", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | unclassified | EA0007 |

## SeizureFrequency

### Residual By State

| Side | active-rate | seizure-free | unknown |
| --- | ---: | ---: | ---: |
| gold | 2 | 0 | 0 |
| predicted | 0 | 1 | 0 |

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `[["cui", "C0036572"], "active-rate"]` | seizures | EA0007 |
| 1 | `[["cui", "C0494475"], "active-rate"]` | generalised-tonic-clonic-seizures | EA0006 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `[["cui", "C0751495"], "seizure-free"]` | focal seizures | EA0005 |

## Investigations

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 0 |  |  |  |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 0 |  |  |  |
