# ExECTv2 Clinical-Recovery Error Ledger

- Generated: `2026-06-22`
- JSON: `experiments\exectv2_v0910_qwencompact_dev25_error_ledger_20260622.json`
- Split: `dev`
- Letters: 25
- Structured JSONL: `experiments\exectv2_holistic_finding_assembly_v0910_qwencompact_dev25_20260622.jsonl`
- Diagnosis JSONL: `None`
- SeizureFrequency JSONL: `None`
- Investigations JSONL: `None`

## Headline Scores

| Entity | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.949 | 0.925 | 0.974 | 37 | 3 | 1 |
| Diagnosis | 0.657 | 0.774 | 0.571 | 24 | 7 | 18 |
| SeizureFrequency | 0.583 | 0.636 | 0.538 | 14 | 8 | 12 |
| Investigations | 0.927 | 0.905 | 0.950 | 19 | 2 | 1 |

## Prescription

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["ordinary", "lamotrigine", "175", "mg", "1"]` | Lamictal- | EA0025 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["ordinary", "lamotrigine", "100", "mg", "2"]` | lamotrigine 100 mg | EA0009 |
| 1 | `["ordinary", "lamotrigine", "75", "mg", "2"]` | lamotrigine 75mg bd | EA0008 |
| 1 | `["ordinary", "levetiracetam", "750", "mg", "2"]` | levetiracetam 750 mg | EA0009 |

## Diagnosis

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 7 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised-tonic-clonic-seizure | EA0005, EA0006, EA0021, EA0025 |
| 4 | `["Diagnosis", "focal to bilateral convulsive seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | bilateral-convulsive-seizure | EA0009, EA0010, EA0011 |
| 3 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0007, EA0010, EA0011 |
| 2 | `["Diagnosis", "focal seizures with altered awareness", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizures-with-altered-awareness | EA0008, EA0011 |
| 2 | `["Diagnosis", "focal seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0018, EA0022 |
| 2 | `["Diagnosis", "focal seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0002 |
| 1 | `["Diagnosis", "epilepsy with generalised tonic clonic seizures alone", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epilepsy-with-generalised-tonic-clonic-seizure-alone | EA0005 |
| 1 | `["Diagnosis", "epileptic attack", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epileptic-attack | EA0015 |
| 1 | `["Diagnosis", "focal epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | focal-onset-epilepsy | EA0007 |
| 1 | `["Diagnosis", "focal epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | symptomatic-structural-focal-epilepsy | EA0010 |
| 1 | `["Diagnosis", "focal seizure", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizure | EA0016 |
| 1 | `["Diagnosis", "juvenile myoclonic epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | jme | EA0026 |
| 1 | `["Diagnosis", "occipital lobe seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | occipital-lobe-seizures | EA0018 |
| 1 | `["Diagnosis", "secondary generalised seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | secondary-generalised-seizures | EA0002 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 7 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0002, EA0005, EA0006, EA0008, EA0014, EA0019, EA0021 |
| 2 | `["Diagnosis", "epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epilepsy | EA0002, EA0004 |
| 1 | `["Diagnosis", "focal", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal | EA0011 |
| 1 | `["Diagnosis", "juvenile myoclonic epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | JME | EA0026 |
| 1 | `["Diagnosis", "mild head injury", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | Mild head injury | EA0022 |

## SeizureFrequency

### Residual By State

| Side | active-rate | seizure-free | unknown |
| --- | ---: | ---: | ---: |
| gold | 6 | 5 | 4 |
| predicted | 4 | 4 | 2 |

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 2 | `[["cui", "C0036572"], "seizure-free"]` | seizures | EA0010, EA0028 |
| 2 | `[["cui", "C0036572"], "unknown"]` | seizure | EA0008, EA0022 |
| 2 | `[["cui", "C0494475"], "active-rate"]` | generalised-tonic-clonic-seizures | EA0006 |
| 1 | `[["cui", "C0027066"], "unknown"]` | myoclonic-jerks | EA0025 |
| 1 | `[["cui", "C0036572"], "active-rate"]` | seizures | EA0007 |
| 1 | `[["cui", "C0270834"], "active-rate"]` | focal-seizures-with-altered-awareness | EA0011 |
| 1 | `[["cui", "C0563606"], "active-rate"]` | absence-like-seizures | EA0006 |
| 1 | `[["cui", "C0751494"], "seizure-free"]` | convulsive-seizure | EA0011 |
| 1 | `[["cui", "C0751495"], "seizure-free"]` | focal-seizures | EA0022 |
| 1 | `[["cui", "C0877017"], "seizure-free"]` | focal-to-bilateral-convulsive-seizure | EA0011 |
| 1 | `[["cui", "C0877017"], "unknown"]` | focal-to-bilateral-convulsive-seizures | EA0011 |
| 1 | `[["cui", "C3203523"], "active-rate"]` | cluster-of-seizures | EA0009 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 2 | `[["cui", "C0036572"], "active-rate"]` | seizures | EA0009 |
| 2 | `[["cui", "C0036572"], "seizure-free"]` | seizures | EA0006, EA0019 |
| 1 | `[["cui", "C0751495"], "unknown"]` | focal seizures | EA0022 |
| 1 | `[["cui", "C0877017"], "seizure-free"]` | focal to bilateral convulsive seizures | EA0010 |
| 1 | `[["phrase", "epileptic seizures"], "unknown"]` | epileptic seizures | EA0022 |
| 1 | `[["phrase", "episodes around twice a week"], "active-rate"]` | episodes around twice a week | EA0018 |
| 1 | `[["phrase", "further seizures"], "seizure-free"]` | further seizures | EA0028 |
| 1 | `[["phrase", "one seizure"], "active-rate"]` | one seizure | EA0016 |

## Investigations

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["MRI", "Yes", "Abnormal"]` | MRI-scan | EA0002 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["EEG", "Yes", "Abnormal"]` | EEG recording | EA0015 |
| 1 | `["MRI", "Yes", "Abnormal"]` | MRI | EA0009 |
