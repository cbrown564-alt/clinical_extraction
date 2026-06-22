# ExECTv2 Clinical-Recovery Error Ledger

- Generated: `2026-06-22`
- JSON: `experiments\exectv2_v092_short_rationale_qwen_dev5_error_ledger_20260622.json`
- Split: `dev`
- Letters: 5
- Structured JSONL: `experiments\exectv2_llm_only_key_entities_structured_v092_short_rationale_dev5_qwen36_35b_ollama_autogpu_ctx16384_20260622.jsonl`
- Diagnosis JSONL: `None`
- SeizureFrequency JSONL: `None`
- Investigations JSONL: `None`

## Headline Scores

| Entity | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.800 | 1.000 | 0.667 | 6 | 0 | 3 |
| Diagnosis | 0.500 | 0.462 | 0.545 | 6 | 7 | 5 |
| SeizureFrequency | 0.941 | 0.889 | 1.000 | 8 | 1 | 0 |
| Investigations | 1.000 | 1.000 | 1.000 | 8 | 0 | 0 |

## Prescription

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["ordinary", "levetiracetam", "500", "mg", "1"]` | levetiracetam- | EA0007 |
| 1 | `["ordinary", "levetiracetam", "750", "mg", "1"]` | levetiracetam- | EA0007 |
| 1 | `["ordinary", "phenytoin", "75", "mg", "3"]` | Phenytoin- | EA0007 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 0 |  |  |  |

## Diagnosis

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 3 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised-tonic-clonic-seizure | EA0005, EA0006 |
| 2 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0006, EA0007 |
| 1 | `["Diagnosis", "epilepsy with generalised tonic clonic seizures alone", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy-with-generalised-tonic-clonic-seizures-alone | EA0005 |
| 1 | `["Diagnosis", "focal epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | focal-onset-epilepsy | EA0007 |
| 1 | `["Diagnosis", "focal epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal-epilepsy | EA0004 |
| 1 | `["Diagnosis", "focal seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0002 |
| 1 | `["Diagnosis", "temporal lobe epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | temporal-lobe-epilepsy | EA0002 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["Diagnosis", "focal", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal | EA0004 |
| 1 | `["Diagnosis", "temporal", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | Probable temporal | EA0002 |
| 1 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | generalised tonic clonic seizures | EA0006 |
| 1 | `["Diagnosis", "unclassified", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | unclassified, possibly generalised epilepsy | EA0006 |

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
| 1 | `[["cui", "C0036572"], "seizure-free"]` | seizures | EA0006 |

## Investigations

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 0 |  |  |  |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 0 |  |  |  |
