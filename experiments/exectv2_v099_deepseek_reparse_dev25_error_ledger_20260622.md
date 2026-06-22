# ExECTv2 Clinical-Recovery Error Ledger

- Generated: `2026-06-22`
- JSON: `experiments\exectv2_v099_deepseek_reparse_dev25_error_ledger_20260622.json`
- Split: `dev`
- Letters: 25
- Structured JSONL: `experiments\exectv2_holistic_finding_assembly_v099_deepseek_reparse_dev25_20260622.jsonl`
- Diagnosis JSONL: `None`
- SeizureFrequency JSONL: `None`
- Investigations JSONL: `None`

## Headline Scores

| Entity | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.962 | 0.927 | 1.000 | 38 | 3 | 0 |
| Diagnosis | 0.815 | 0.846 | 0.786 | 33 | 6 | 9 |
| SeizureFrequency | 0.750 | 0.700 | 0.808 | 21 | 9 | 5 |
| Investigations | 0.976 | 0.952 | 1.000 | 20 | 1 | 0 |

## Prescription

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 0 |  |  |  |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["ordinary", "lamotrigine", "75", "mg", "2"]` | lamotrigine 75mg bd | EA0008 |
| 1 | `["ordinary", "levetiracetam", "250", "mg", "1"]` | levetiracetam | EA0008 |
| 1 | `["rescue", "clobazam", "as_required"]` | Clobazam | EA0011 |

## Diagnosis

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 3 | `["Diagnosis", "focal to bilateral convulsive seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | bilateral-convulsive-seizure | EA0009, EA0010, EA0011 |
| 3 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised-tonic-clonic-seizures | EA0006, EA0021, EA0025 |
| 2 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0007, EA0010 |
| 2 | `["Diagnosis", "focal seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0018, EA0022 |
| 1 | `["Diagnosis", "epilepsy with generalised tonic clonic seizures alone", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epilepsy-with-generalised-tonic-clonic-seizure-alone | EA0005 |
| 1 | `["Diagnosis", "epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epilepsy | EA0027 |
| 1 | `["Diagnosis", "epileptic attack", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epileptic-attack | EA0015 |
| 1 | `["Diagnosis", "focal epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | focal-onset-epilepsy | EA0007 |
| 1 | `["Diagnosis", "focal seizure", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizure | EA0016 |
| 1 | `["Diagnosis", "focal seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0002 |
| 1 | `["Diagnosis", "occipital lobe seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | occipital-lobe-seizures | EA0018 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 2 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0008, EA0021 |
| 2 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised tonic clonic seizures | EA0005, EA0020 |
| 1 | `["Diagnosis", "epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | epilepsy | EA0027 |
| 1 | `["Diagnosis", "focal seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal seizures | EA0022 |
| 1 | `["Diagnosis", "focal to bilateral convulsive seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal to bilateral convulsive seizures | EA0010 |

## SeizureFrequency

### Residual By State

| Side | active-rate | seizure-free | unknown |
| --- | ---: | ---: | ---: |
| gold | 3 | 3 | 3 |
| predicted | 3 | 4 | 2 |

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 2 | `[["cui", "C0036572"], "active-rate"]` | seizures | EA0007, EA0009 |
| 1 | `[["cui", "C0027066"], "unknown"]` | myoclonic-jerks | EA0025 |
| 1 | `[["cui", "C0036572"], "seizure-free"]` | seizures | EA0010 |
| 1 | `[["cui", "C0036572"], "unknown"]` | seizures | EA0022 |
| 1 | `[["cui", "C0494475"], "active-rate"]` | generalised-tonic-clonic-seizures | EA0006 |
| 1 | `[["cui", "C0751494"], "seizure-free"]` | convulsive-seizure | EA0011 |
| 1 | `[["cui", "C0877017"], "seizure-free"]` | focal-to-bilateral-convulsive-seizure | EA0011 |
| 1 | `[["cui", "C0877017"], "unknown"]` | focal-to-bilateral-convulsive-seizures | EA0011 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 2 | `[["cui", "C0036572"], "seizure-free"]` | seizures | EA0016, EA0019 |
| 1 | `[["cui", "C0036572"], "active-rate"]` | seizure | EA0016 |
| 1 | `[["cui", "C0036572"], "unknown"]` | seizures | EA0009 |
| 1 | `[["cui", "C0877017"], "seizure-free"]` | focal to bilateral convulsive seizures | EA0010 |
| 1 | `[["phrase", "epileptic seizures"], "seizure-free"]` | epileptic seizures | EA0022 |
| 1 | `[["phrase", "episodes"], "active-rate"]` | episodes | EA0018 |
| 1 | `[["phrase", "general and complex partial seizures"], "unknown"]` | general and complex partial seizures | EA0014 |
| 1 | `[["phrase", "minor seizures"], "active-rate"]` | minor seizures | EA0021 |

## Investigations

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 0 |  |  |  |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["EEG", "Yes", "Abnormal"]` | EEG | EA0015 |
