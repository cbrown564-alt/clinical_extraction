# ExECTv2 Clinical-Recovery Error Ledger

- Generated: `2026-06-22`
- JSON: `experiments\exectv2_v096_qwen_dev25_error_ledger_20260622.json`
- Split: `dev`
- Letters: 25
- Structured JSONL: `experiments\exectv2_holistic_finding_assembly_v096_qwen_dev25_20260622.jsonl`
- Diagnosis JSONL: `None`
- SeizureFrequency JSONL: `None`
- Investigations JSONL: `None`

## Headline Scores

| Entity | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.831 | 0.821 | 0.842 | 32 | 7 | 6 |
| Diagnosis | 0.729 | 0.721 | 0.738 | 31 | 12 | 11 |
| SeizureFrequency | 0.643 | 0.600 | 0.692 | 18 | 12 | 8 |
| Investigations | 0.950 | 0.950 | 0.950 | 19 | 1 | 1 |

## Prescription

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["ordinary", "carbamazepine", "500", "mg", "2"]` | Currently-she-is-taking-Tegretol-500-mg-BD | EA0015 |
| 1 | `["ordinary", "lamotrigine", "100", "mg", "1"]` | Lamictal-100-mg-in-the-morning | EA0025 |
| 1 | `["ordinary", "lamotrigine", "175", "mg", "1"]` | Lamictal- | EA0025 |
| 1 | `["ordinary", "levetiracetam", "250", "mg", "2"]` | levetiracetam-250-mg-BD | EA0015 |
| 1 | `["ordinary", "sodium-valproate", "300", "mg", "1"]` | He-is-on-Epilim-300-mg-in-the-morning | EA0019 |
| 1 | `["ordinary", "sodium-valproate", "600", "mg", "1"]` | Epilim- | EA0019 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["ordinary", "lamotrigine", "75", "mg", "2"]` | lamotrigine 75mg bd | EA0008 |
| 1 | `["ordinary", "levetiracetam", "250", "mg", "1"]` | levetiracetam | EA0008 |
| 1 | `["ordinary", "levetiracetam", "750", "mg", "2"]` | levetiracetam | EA0008 |
| 1 | `["ordinary", "sodium-valproate", "300/600", "mg", "2"]` | Epilim 300 mg in the morning and 600 mg in the evening | EA0019 |
| 1 | `["ordinary", "sodium-valproate", "800", "mg", "2"]` | Sodium Valproate 800mg bd | EA0021 |
| 1 | `["rescue", "clobazam", "as_required"]` | Clobazam | EA0011 |
| 1 | `["rescue", "lamotrigine", "as_required"]` | Lamictal 100 mg in the morning, 175 mg in the afternoon | EA0025 |

## Diagnosis

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 3 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0007, EA0010, EA0011 |
| 3 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised-tonic-clonic-seizure | EA0005, EA0006, EA0021 |
| 2 | `["Diagnosis", "focal seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0018, EA0022 |
| 2 | `["Diagnosis", "focal to bilateral convulsive seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | bilateral-convulsive-seizure | EA0009, EA0011 |
| 1 | `["Diagnosis", "epilepsy with generalised tonic clonic seizures alone", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy-with-generalised-tonic-clonic-seizures-alone | EA0005 |
| 1 | `["Diagnosis", "epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epilepsy | EA0027 |
| 1 | `["Diagnosis", "epileptic attack", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epileptic-attack | EA0015 |
| 1 | `["Diagnosis", "focal epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | focal-onset-epilepsy | EA0007 |
| 1 | `["Diagnosis", "focal seizure", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizure | EA0016 |
| 1 | `["Diagnosis", "focal seizures with altered awareness", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizures-with-altered-awareness | EA0011 |
| 1 | `["Diagnosis", "focal seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0002 |
| 1 | `["Diagnosis", "intractable epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | intractable-epilepsy | EA0014 |
| 1 | `["Diagnosis", "occipital lobe seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | occipital-lobe-seizures | EA0018 |
| 1 | `["Diagnosis", "temporal lobe epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | temporal-lobe-epilepsy | EA0011 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 2 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0014, EA0021 |
| 2 | `["Diagnosis", "focal", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal | EA0008, EA0011 |
| 1 | `["Diagnosis", "epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | epilepsy | EA0027 |
| 1 | `["Diagnosis", "focal epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | Focal epilepsy | EA0022 |
| 1 | `["Diagnosis", "general tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | general tonic clonic seizures | EA0014 |
| 1 | `["Diagnosis", "generalised epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | generalised epilepsy | EA0007 |
| 1 | `["Diagnosis", "generalised", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised | EA0021 |
| 1 | `["Diagnosis", "minor seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | minor seizures | EA0021 |
| 1 | `["Diagnosis", "occipital lobe seizures", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | occipital lobe seizures | EA0018 |
| 1 | `["Diagnosis", "structural epilepsy secondary to perinatal insult", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | structural epilepsy secondary to perinatal insult | EA0010 |
| 1 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised tonic clonic seizures | EA0020 |

## SeizureFrequency

### Residual By State

| Side | active-rate | seizure-free | unknown |
| --- | ---: | ---: | ---: |
| gold | 6 | 5 | 2 |
| predicted | 5 | 4 | 4 |

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 3 | `[["cui", "C0036572"], "active-rate"]` | seizures | EA0004, EA0007, EA0009 |
| 2 | `[["cui", "C0036572"], "seizure-free"]` | seizures | EA0010, EA0028 |
| 2 | `[["cui", "C0877017"], "seizure-free"]` | focal-to-bilateral-convulsive-seizure | EA0011 |
| 1 | `[["cui", "C0036572"], "unknown"]` | seizures | EA0022 |
| 1 | `[["cui", "C0270834"], "active-rate"]` | focal-seizures-with-altered-awareness | EA0011 |
| 1 | `[["cui", "C0494475"], "active-rate"]` | generalised-tonic-clonic-seizures | EA0006 |
| 1 | `[["cui", "C0563606"], "active-rate"]` | absence-like-seizures | EA0006 |
| 1 | `[["cui", "C0751494"], "seizure-free"]` | convulsive-seizure | EA0011 |
| 1 | `[["cui", "C0877017"], "unknown"]` | focal-to-bilateral-convulsive-seizures | EA0011 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 2 | `[["cui", "C0036572"], "active-rate"]` | seizure | EA0019 |
| 1 | `[["cui", "C0036572"], "seizure-free"]` | seizures | EA0016 |
| 1 | `[["cui", "C0149958"], "unknown"]` | complex partial seizures | EA0014 |
| 1 | `[["cui", "C0494475"], "unknown"]` | generalised tonic clonic seizures | EA0021 |
| 1 | `[["cui", "C0563606"], "unknown"]` | absence like seizures | EA0006 |
| 1 | `[["cui", "C0877017"], "active-rate"]` | focal to bilateral convulsive seizures | EA0010 |
| 1 | `[["cui", "C1299590"], "seizure-free"]` | seizure-free | EA0028 |
| 1 | `[["phrase", "epilepsy"], "seizure-free"]` | epilepsy | EA0012 |
| 1 | `[["phrase", "epileptic seizures"], "seizure-free"]` | epileptic seizures | EA0022 |
| 1 | `[["phrase", "episodes of loss of consciousness"], "active-rate"]` | episodes of loss of consciousness | EA0023 |
| 1 | `[["phrase", "general tonic clonic seizures"], "unknown"]` | general tonic clonic seizures | EA0014 |
| 1 | `[["phrase", "temporal lobe onset focal seizures"], "active-rate"]` | temporal lobe onset focal seizures | EA0018 |

## Investigations

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["CT", "Yes", "Abnormal"]` | CT-scan | EA0016 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["MRI", null, null]` | MRI | EA0024 |
