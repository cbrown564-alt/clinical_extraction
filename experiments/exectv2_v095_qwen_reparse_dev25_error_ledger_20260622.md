# ExECTv2 Clinical-Recovery Error Ledger

- Generated: `2026-06-22`
- JSON: `experiments\exectv2_v095_qwen_reparse_dev25_error_ledger_20260622.json`
- Split: `dev`
- Letters: 25
- Structured JSONL: `experiments\exectv2_holistic_finding_assembly_v095_qwen_reparse_dev25_20260621.jsonl`
- Diagnosis JSONL: `None`
- SeizureFrequency JSONL: `None`
- Investigations JSONL: `None`

## Headline Scores

| Entity | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.923 | 0.900 | 0.947 | 36 | 4 | 2 |
| Diagnosis | 0.731 | 0.667 | 0.809 | 34 | 17 | 8 |
| SeizureFrequency | 0.643 | 0.600 | 0.692 | 18 | 12 | 8 |
| Investigations | 0.950 | 0.950 | 0.950 | 19 | 1 | 1 |

## Prescription

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["ordinary", "levetiracetam", "1000", "mg", "2"]` | levetiracetam-1000-mg-twice-today | EA0018 |
| 1 | `["ordinary", "sodium-valproate", "500", "mg", "2"]` | Currently-she-is-taking-sodium-valproate-500-mg-twice-a-day | EA0018 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["ordinary", "lamotrigine", "75", "mg", "2"]` | lamotrigine 75mg bd | EA0008 |
| 1 | `["ordinary", "levetiracetam", "750", "mg", "2"]` | levetiracetam | EA0008 |
| 1 | `["rescue", "clobazam", "as_required"]` | Clobazam | EA0011 |
| 1 | `["rescue", "sodium-valproate", "as_required"]` | sodium valproate | EA0018 |

## Diagnosis

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 5 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised-tonic-clonic-seizure | EA0005, EA0006, EA0021, EA0025 |
| 3 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0007, EA0010, EA0011 |
| 2 | `["Diagnosis", "focal seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0018, EA0022 |
| 2 | `["Diagnosis", "focal to bilateral convulsive seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-to-bilateral-convulsive-seizures | EA0010, EA0011 |
| 1 | `["Diagnosis", "epilepsy with generalised tonic clonic seizures alone", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epilepsy-with-generalised-tonic-clonic-seizure-alone | EA0005 |
| 1 | `["Diagnosis", "epilepsy with generalised tonic clonic seizures alone", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy-with-generalised-tonic-clonic-seizures-alone | EA0005 |
| 1 | `["Diagnosis", "epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epilepsy | EA0027 |
| 1 | `["Diagnosis", "focal epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | focal-onset-epilepsy | EA0007 |
| 1 | `["Diagnosis", "focal seizure", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizure | EA0016 |
| 1 | `["Diagnosis", "focal seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0002 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 3 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0015, EA0021 |
| 2 | `["Diagnosis", "focal epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | symptomatic structural focal epilepsy | EA0008, EA0022 |
| 2 | `["Diagnosis", "focal", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal | EA0008, EA0011 |
| 1 | `["Diagnosis", "cluster of seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | cluster of seizures | EA0009 |
| 1 | `["Diagnosis", "epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | epilepsy | EA0027 |
| 1 | `["Diagnosis", "episodes", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | episodes | EA0021 |
| 1 | `["Diagnosis", "events", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | events | EA0024 |
| 1 | `["Diagnosis", "focal epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal epilepsy | EA0010 |
| 1 | `["Diagnosis", "focal to bilateral convulsive seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal to bilateral convulsive seizures | EA0010 |
| 1 | `["Diagnosis", "general seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | general seizures | EA0014 |
| 1 | `["Diagnosis", "generalised epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | generalised epilepsy | EA0007 |
| 1 | `["Diagnosis", "generalised", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised | EA0021 |
| 1 | `["Diagnosis", "loss of consciousness", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | loss of consciousness | EA0023 |
| 1 | `["Diagnosis", "minor seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | minor seizures | EA0021 |
| 1 | `["Diagnosis", "seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | seizures | EA0009 |

## SeizureFrequency

### Residual By State

| Side | active-rate | seizure-free | unknown |
| --- | ---: | ---: | ---: |
| gold | 6 | 4 | 3 |
| predicted | 6 | 3 | 3 |

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 3 | `[["cui", "C0036572"], "active-rate"]` | seizures | EA0004, EA0007, EA0009 |
| 2 | `[["cui", "C0036572"], "unknown"]` | seizure | EA0008, EA0022 |
| 1 | `[["cui", "C0036572"], "seizure-free"]` | seizures | EA0010 |
| 1 | `[["cui", "C0270834"], "active-rate"]` | focal-seizures-with-altered-awareness | EA0011 |
| 1 | `[["cui", "C0494475"], "active-rate"]` | generalised-tonic-clonic-seizures | EA0006 |
| 1 | `[["cui", "C0563606"], "active-rate"]` | absence-like-seizures | EA0006 |
| 1 | `[["cui", "C0563606"], "seizure-free"]` | absences | EA0020 |
| 1 | `[["cui", "C0751494"], "seizure-free"]` | convulsive-seizure | EA0011 |
| 1 | `[["cui", "C0877017"], "seizure-free"]` | focal-to-bilateral-convulsive-seizure | EA0011 |
| 1 | `[["cui", "C0877017"], "unknown"]` | focal-to-bilateral-convulsive-seizures | EA0011 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 2 | `[["cui", "C0036572"], "seizure-free"]` | seizures | EA0016, EA0019 |
| 1 | `[["cui", "C0036572"], "unknown"]` | seizures | EA0009 |
| 1 | `[["cui", "C0751495"], "active-rate"]` | focal seizures | EA0018 |
| 1 | `[["cui", "C0877017"], "active-rate"]` | focal to bilateral convulsive seizures | EA0010 |
| 1 | `[["cui", "C1299590"], "seizure-free"]` | seizure-free | EA0024 |
| 1 | `[["phrase", "episodes of loss of consciousness"], "active-rate"]` | episodes of loss of consciousness | EA0023 |
| 1 | `[["phrase", "episodes"], "active-rate"]` | episodes | EA0021 |
| 1 | `[["phrase", "events"], "active-rate"]` | events | EA0024 |
| 1 | `[["phrase", "general and complex partial seizures"], "unknown"]` | general and complex partial seizures | EA0014 |
| 1 | `[["phrase", "jerks"], "unknown"]` | jerks | EA0027 |
| 1 | `[["phrase", "minor seizures"], "active-rate"]` | minor seizures | EA0021 |

## Investigations

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["CT", "Yes", "Abnormal"]` | CT-scan | EA0016 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["EEG", "Yes", "Abnormal"]` | EEG | EA0015 |
