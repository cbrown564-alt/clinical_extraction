# ExECTv2 Clinical-Recovery Error Ledger

- Generated: `2026-06-22`
- JSON: `experiments\exectv2_v0910_qwencompact_dictionary_replay_dev25_error_ledger_20260622.json`
- Split: `dev`
- Letters: 25
- Structured JSONL: `experiments\exectv2_holistic_finding_assembly_v0910_qwencompact_dictionary_replay_dev25_20260622.jsonl`
- Diagnosis JSONL: `None`
- SeizureFrequency JSONL: `None`
- Investigations JSONL: `None`

## Headline Scores

| Entity | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.949 | 0.925 | 0.974 | 37 | 3 | 1 |
| Diagnosis | 0.693 | 0.788 | 0.619 | 26 | 7 | 16 |
| SeizureFrequency | 0.588 | 0.600 | 0.577 | 15 | 10 | 11 |
| Investigations | 1.000 | 1.000 | 1.000 | 20 | 0 | 0 |

## Prescription

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["ordinary", "sodium-valproate", "700", "mg", "1"]` | sodium-valproate-700-mg | EA0026 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["ordinary", "lamotrigine", "75", "mg", "2"]` | lamotrigine 75mg bd | EA0008 |
| 1 | `["ordinary", "lefitiracetam", "250", "mg", "1"]` | lefitiracetam 250mg once-a-day | EA0008 |
| 1 | `["rescue", "clobazam", "as_required"]` | Clobazam ... as required basis | EA0011 |

## Diagnosis

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 8 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised-tonic-clonic-seizure | EA0005, EA0006, EA0021, EA0025, EA0026 |
| 4 | `["Diagnosis", "focal to bilateral convulsive seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | bilateral-convulsive-seizure | EA0009, EA0010, EA0011 |
| 2 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0007, EA0011 |
| 2 | `["Diagnosis", "focal seizures with altered awareness", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizures-with-altered-awareness | EA0008, EA0011 |
| 2 | `["Diagnosis", "focal seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0002 |
| 1 | `["Diagnosis", "epilepsy with generalised tonic clonic seizures alone", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epilepsy-with-generalised-tonic-clonic-seizure-alone | EA0005 |
| 1 | `["Diagnosis", "focal epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | focal-onset-epilepsy | EA0007 |
| 1 | `["Diagnosis", "focal epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-epilepsy | EA0002 |
| 1 | `["Diagnosis", "focal seizure", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizure | EA0016 |
| 1 | `["Diagnosis", "focal seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0022 |
| 1 | `["Diagnosis", "secondary generalised seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | secondary-generalised-seizures | EA0002 |
| 1 | `["Diagnosis", "secondary generalised tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | secondary-generalised-tonic-clonic-seizures | EA0021 |
| 1 | `["Diagnosis", "temporal lobe epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | temporal-lobe-epilepsy | EA0002 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0021 |
| 1 | `["Diagnosis", "focal epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal epilepsy | EA0002 |
| 1 | `["Diagnosis", "focal", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal | EA0011 |
| 1 | `["Diagnosis", "generalised", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised | EA0021 |
| 1 | `["Diagnosis", "myoclonic jerks", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | generalised tonic clonic seizures with myoclonic jerks, possible JME | EA0026 |
| 1 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | generalised tonic clonic seizures with myoclonic jerks, possible JME | EA0026 |

## SeizureFrequency

### Residual By State

| Side | active-rate | seizure-free | unknown |
| --- | ---: | ---: | ---: |
| gold | 5 | 5 | 4 |
| predicted | 4 | 3 | 3 |

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 2 | `[["cui", "C0036572"], "unknown"]` | seizure | EA0008, EA0022 |
| 2 | `[["cui", "C0494475"], "active-rate"]` | generalised-tonic-clonic-seizures | EA0006, EA0019 |
| 1 | `[["cui", "C0027066"], "unknown"]` | myoclonic-jerks | EA0025 |
| 1 | `[["cui", "C0036572"], "active-rate"]` | seizures | EA0007 |
| 1 | `[["cui", "C0036572"], "seizure-free"]` | seizures | EA0010 |
| 1 | `[["cui", "C0270834"], "active-rate"]` | focal-seizures-with-altered-awareness | EA0011 |
| 1 | `[["cui", "C0494475"], "seizure-free"]` | generalised-tonic-clonic-seizure | EA0005 |
| 1 | `[["cui", "C0751494"], "seizure-free"]` | convulsive-seizure | EA0011 |
| 1 | `[["cui", "C0751495"], "seizure-free"]` | focal-seizures | EA0022 |
| 1 | `[["cui", "C0877017"], "seizure-free"]` | focal-to-bilateral-convulsive-seizure | EA0011 |
| 1 | `[["cui", "C0877017"], "unknown"]` | focal-to-bilateral-convulsive-seizures | EA0011 |
| 1 | `[["cui", "C3203523"], "active-rate"]` | cluster-of-seizures | EA0009 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 2 | `[["cui", "C0036572"], "seizure-free"]` | seizures | EA0006, EA0019 |
| 1 | `[["cui", "C0494475"], "active-rate"]` | Generalised tonic clonic seizure | EA0005 |
| 1 | `[["cui", "C0751495"], "unknown"]` | focal seizures | EA0022 |
| 1 | `[["cui", "C0877017"], "active-rate"]` | focal to bilateral convulsive seizures | EA0010 |
| 1 | `[["phrase", "epileptic seizures"], "unknown"]` | epileptic seizures | EA0022 |
| 1 | `[["phrase", "episodes of loss of consciousness"], "active-rate"]` | episodes of loss of consciousness | EA0023 |
| 1 | `[["phrase", "episodes"], "active-rate"]` | episodes | EA0018 |
| 1 | `[["phrase", "general and complex partial seizures"], "unknown"]` | general and complex partial seizures | EA0014 |
| 1 | `[["phrase", "previous seizures"], "seizure-free"]` | previous seizures | EA0016 |

## Investigations

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 0 |  |  |  |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 0 |  |  |  |
