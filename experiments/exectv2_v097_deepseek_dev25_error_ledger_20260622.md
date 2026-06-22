# ExECTv2 Clinical-Recovery Error Ledger

- Generated: `2026-06-22`
- JSON: `experiments\exectv2_v097_deepseek_dev25_error_ledger_20260622.json`
- Split: `dev`
- Letters: 25
- Structured JSONL: `experiments\exectv2_llm_only_key_entities_structured_v097_dev25_deepseek_chat_20260622.jsonl`
- Diagnosis JSONL: `None`
- SeizureFrequency JSONL: `None`
- Investigations JSONL: `None`

## Headline Scores

| Entity | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.961 | 0.949 | 0.974 | 37 | 2 | 1 |
| Diagnosis | 0.767 | 0.750 | 0.786 | 33 | 11 | 9 |
| SeizureFrequency | 0.759 | 0.688 | 0.846 | 22 | 10 | 4 |
| Investigations | 0.909 | 0.833 | 1.000 | 20 | 4 | 0 |

## Prescription

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["ordinary", "levetiracetam", "1000", "mg", "2"]` | Keppra-1000-milligrams-twice-a-day | EA0030 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["ordinary", "lamotrigine", "75", "mg", "2"]` | lamotrigine 75mg bd | EA0008 |
| 1 | `["rescue", "clobazam", "as_required"]` | Clobazam | EA0011 |

## Diagnosis

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 3 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0007, EA0010, EA0011 |
| 3 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised-tonic-clonic-seizures | EA0006, EA0021, EA0025 |
| 2 | `["Diagnosis", "focal seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0018, EA0022 |
| 2 | `["Diagnosis", "focal to bilateral convulsive seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-to-bilateral-convulsive-seizures | EA0011 |
| 1 | `["Diagnosis", "epilepsy with generalised tonic clonic seizures alone", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epilepsy-with-generalised-tonic-clonic-seizure-alone | EA0005 |
| 1 | `["Diagnosis", "epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epilepsy | EA0027 |
| 1 | `["Diagnosis", "epileptic attack", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epileptic-attack | EA0015 |
| 1 | `["Diagnosis", "focal epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | focal-onset-epilepsy | EA0007 |
| 1 | `["Diagnosis", "focal seizures with altered awareness", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizures-with-altered-awareness | EA0011 |
| 1 | `["Diagnosis", "focal seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0002 |
| 1 | `["Diagnosis", "intractable epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | intractable-epilepsy | EA0014 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 2 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0014, EA0021 |
| 2 | `["Diagnosis", "myoclonic jerks", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | myoclonic jerks | EA0025, EA0026 |
| 2 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised tonic chronic seizures | EA0005, EA0020 |
| 1 | `["Diagnosis", "absence like seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | absence like seizures | EA0006 |
| 1 | `["Diagnosis", "epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | epilepsy | EA0027 |
| 1 | `["Diagnosis", "epileptic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epileptic seizures | EA0022 |
| 1 | `["Diagnosis", "focal seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal seizures | EA0022 |
| 1 | `["Diagnosis", "general seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | general seizures | EA0014 |

## SeizureFrequency

### Residual By State

| Side | active-rate | seizure-free | unknown |
| --- | ---: | ---: | ---: |
| gold | 2 | 3 | 2 |
| predicted | 1 | 6 | 3 |

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `[["cui", "C0036572"], "active-rate"]` | seizures | EA0007 |
| 1 | `[["cui", "C0036572"], "seizure-free"]` | seizures | EA0010 |
| 1 | `[["cui", "C0036572"], "unknown"]` | seizures | EA0022 |
| 1 | `[["cui", "C0494475"], "active-rate"]` | generalised-tonic-clonic-seizures | EA0006 |
| 1 | `[["cui", "C0751494"], "seizure-free"]` | convulsive-seizure | EA0011 |
| 1 | `[["cui", "C0877017"], "seizure-free"]` | focal-to-bilateral-convulsive-seizure | EA0011 |
| 1 | `[["cui", "C0877017"], "unknown"]` | focal-to-bilateral-convulsive-seizures | EA0011 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 3 | `[["cui", "C0036572"], "seizure-free"]` | seizure | EA0005, EA0016, EA0019 |
| 1 | `[["cui", "C0036572"], "unknown"]` | seizures | EA0007 |
| 1 | `[["cui", "C0149958"], "unknown"]` | complex partial seizures | EA0014 |
| 1 | `[["cui", "C0494475"], "seizure-free"]` | generalised tonic clonic seizures | EA0021 |
| 1 | `[["cui", "C0877017"], "active-rate"]` | focal to bilateral convulsive seizures | EA0010 |
| 1 | `[["cui", "C1299590"], "seizure-free"]` | seizure free | EA0006 |
| 1 | `[["phrase", "epileptic seizures"], "seizure-free"]` | epileptic seizures | EA0022 |
| 1 | `[["phrase", "general seizures"], "unknown"]` | general seizures | EA0014 |

## Investigations

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 0 |  |  |  |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["CT", "No", "Unknown"]` | ECG | EA0016 |
| 1 | `["EEG", "No", "Unknown"]` | ECG | EA0016 |
| 1 | `["EEG", "Yes", "Abnormal"]` | EEG | EA0015 |
| 1 | `["MRI", "No", "Unknown"]` | ECG | EA0016 |
