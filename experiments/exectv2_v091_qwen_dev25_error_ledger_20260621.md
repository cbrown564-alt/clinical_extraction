# ExECTv2 Clinical-Recovery Error Ledger

- Generated: `2026-06-22`
- JSON: `experiments\exectv2_v091_qwen_dev25_error_ledger_20260621.json`
- Split: `dev`
- Letters: 25
- Structured JSONL: `experiments\exectv2_llm_only_key_entities_structured_v091_dev25_qwen36_35b_ollama_autogpu_ctx16384_20260621.jsonl`
- Diagnosis JSONL: `None`
- SeizureFrequency JSONL: `None`
- Investigations JSONL: `None`

## Headline Scores

| Entity | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.754 | 0.839 | 0.684 | 26 | 5 | 12 |
| Diagnosis | 0.523 | 0.500 | 0.548 | 23 | 23 | 19 |
| SeizureFrequency | 0.632 | 0.581 | 0.692 | 18 | 13 | 8 |
| Investigations | 0.895 | 0.944 | 0.850 | 17 | 1 | 3 |

## Prescription

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["ordinary", "carbamazepine", "200", "mg", "2"]` | Carbamazepine-200-mg-twice-a-day | EA0005 |
| 1 | `["ordinary", "eslicarbazepine", "800", "mg", "1"]` | eslicarbazepine | EA0011 |
| 1 | `["ordinary", "lamotrigine", "100", "mg", "1"]` | Lamictal-100-mg-in-the-morning | EA0025 |
| 1 | `["ordinary", "lamotrigine", "175", "mg", "1"]` | Lamictal- | EA0025 |
| 1 | `["ordinary", "lamotrigine", "250", "mg", "2"]` | Medication:-lamotrigine-250-milligrams-twice-a-day | EA0030 |
| 1 | `["ordinary", "levetiracetam", "1000", "mg", "2"]` | Keppra-1000-milligrams-twice-a-day | EA0030 |
| 1 | `["ordinary", "levetiracetam", "500", "mg", "1"]` | levetiracetam- | EA0007 |
| 1 | `["ordinary", "levetiracetam", "750", "mg", "1"]` | levetiracetam- | EA0007 |
| 1 | `["ordinary", "phenytoin", "75", "mg", "3"]` | Phenytoin- | EA0007 |
| 1 | `["ordinary", "sodium-valproate", "500", "mg", "2"]` | Currently-she-is-taking-sodium-valproate-500-mg-twice-a-day | EA0018 |
| 1 | `["ordinary", "sodium-valproate", "700", "mg", "1"]` | Medication:-Sodium-Valproate-700mg-in-the-morning | EA0021 |
| 1 | `["ordinary", "sodium-valproate", "800", "mg", "1"]` | Sodium-Valproate | EA0021 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["ordinary", "lamotrigine", "275", "mg", "2"]` | Lamictal 100 mg in the morning, 175 mg in the afternoon | EA0025 |
| 1 | `["ordinary", "levetiracetam", "750mg mane, 500 mg nocte", "mg", "2"]` | levetiracetam 750mg mane, 500 mg nocte | EA0007 |
| 1 | `["ordinary", "phenytoin", "75mg", "mg", "3"]` | Phenytoin 75mg tds | EA0007 |
| 1 | `["ordinary", "sodium-valproate", "700/800", "mg", "2"]` | Sodium Valproate 700mg in the morning and 800mg nocte | EA0021 |
| 1 | `["ordinary", "sodium-valproate", "800", "mg", "2"]` | Sodium Valproate 800mg bd | EA0021 |

## Diagnosis

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 4 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0006, EA0007, EA0010, EA0011 |
| 3 | `["Diagnosis", "focal to bilateral convulsive seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | bilateral-convulsive-seizure | EA0009, EA0010, EA0011 |
| 3 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised-tonic-clonic-seizure | EA0005, EA0006, EA0021 |
| 2 | `["Diagnosis", "focal epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | symptomatic-structural-focal-epilepsy | EA0008, EA0010 |
| 2 | `["Diagnosis", "focal seizures with altered awareness", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizures-with-altered-awareness | EA0008, EA0011 |
| 1 | `["Diagnosis", "epilepsy with generalised tonic clonic seizures alone", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epilepsy-with-generalised-tonic-clonic-seizure-alone | EA0005 |
| 1 | `["Diagnosis", "epilepsy with generalised tonic clonic seizures alone", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy-with-generalised-tonic-clonic-seizures-alone | EA0005 |
| 1 | `["Diagnosis", "epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epilepsy | EA0027 |
| 1 | `["Diagnosis", "epileptic attack", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epileptic-attack | EA0015 |
| 1 | `["Diagnosis", "focal epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | focal-onset-epilepsy | EA0007 |
| 1 | `["Diagnosis", "focal epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal-epilepsy | EA0004 |
| 1 | `["Diagnosis", "focal seizure", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizure | EA0016 |
| 1 | `["Diagnosis", "focal seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0022 |
| 1 | `["Diagnosis", "genetic generalised epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | genetic-generalised-epilepsy | EA0005 |
| 1 | `["Diagnosis", "juvenile myoclonic epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | jme | EA0030 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 3 | `["Diagnosis", "myoclonic jerks", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised tonic clonic seizures with myoclonic jerks | EA0025, EA0026 |
| 1 | `["Diagnosis", "absence like seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | absence like seizures | EA0006 |
| 1 | `["Diagnosis", "absences", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | absences | EA0020 |
| 1 | `["Diagnosis", "convulsive seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | convulsive seizures | EA0002 |
| 1 | `["Diagnosis", "dissociative seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | Dissociative seizures | EA0022 |
| 1 | `["Diagnosis", "epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | epilepsy | EA0027 |
| 1 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0021 |
| 1 | `["Diagnosis", "epileptic", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epileptic | EA0015 |
| 1 | `["Diagnosis", "epileptic", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epileptic | EA0015 |
| 1 | `["Diagnosis", "focal epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | symptomatic structural focal epilepsy | EA0010 |
| 1 | `["Diagnosis", "focal to bilateral convulsive seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal to bilateral convulsive seizures | EA0010 |
| 1 | `["Diagnosis", "focal", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | probable focal | EA0004 |
| 1 | `["Diagnosis", "general seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | general seizures | EA0014 |
| 1 | `["Diagnosis", "generalised epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | genetic generalised epilepsy-epilepsy with generalised tonic chronic seizures alone | EA0005 |
| 1 | `["Diagnosis", "generalised tonic chronic seizures alone", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | genetic generalised epilepsy-epilepsy with generalised tonic chronic seizures alone | EA0005 |

## SeizureFrequency

### Residual By State

| Side | active-rate | seizure-free | unknown |
| --- | ---: | ---: | ---: |
| gold | 7 | 3 | 3 |
| predicted | 7 | 4 | 3 |

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 4 | `[["cui", "C0036572"], "active-rate"]` | seizures | EA0004, EA0007, EA0009 |
| 2 | `[["cui", "C0036572"], "unknown"]` | seizure | EA0008, EA0022 |
| 2 | `[["cui", "C0270834"], "active-rate"]` | focal-seizures-with-altered-awareness | EA0008, EA0011 |
| 1 | `[["cui", "C0036572"], "seizure-free"]` | seizures | EA0010 |
| 1 | `[["cui", "C0494475"], "active-rate"]` | generalised-tonic-clonic-seizures | EA0006 |
| 1 | `[["cui", "C0751494"], "seizure-free"]` | convulsive-seizure | EA0011 |
| 1 | `[["cui", "C0877017"], "seizure-free"]` | focal-to-bilateral-convulsive-seizure | EA0011 |
| 1 | `[["cui", "C0877017"], "unknown"]` | focal-to-bilateral-convulsive-seizures | EA0011 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 3 | `[["cui", "C0036572"], "active-rate"]` | seizures | EA0010, EA0019 |
| 2 | `[["cui", "C0036572"], "seizure-free"]` | seizures | EA0016, EA0019 |
| 1 | `[["cui", "C0494475"], "unknown"]` | generalised tonic clonic seizures | EA0021 |
| 1 | `[["phrase", "convulsive seizures"], "active-rate"]` | convulsive seizures | EA0002 |
| 1 | `[["phrase", "epileptic seizures"], "seizure-free"]` | epileptic seizures | EA0022 |
| 1 | `[["phrase", "epileptic"], "unknown"]` | epileptic | EA0015 |
| 1 | `[["phrase", "events"], "active-rate"]` | events | EA0024 |
| 1 | `[["phrase", "events"], "seizure-free"]` | events | EA0024 |
| 1 | `[["phrase", "few seizures per year"], "active-rate"]` | few seizures per year | EA0004 |
| 1 | `[["phrase", "general and complex partial seizures"], "unknown"]` | general and complex partial seizures | EA0014 |
| 1 | `[["phrase", "several seizures"], "active-rate"]` | several seizures | EA0004 |

## Investigations

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["CT", "Yes", "Abnormal"]` | CT-scan | EA0016 |
| 1 | `["EEG", "Yes", "Abnormal"]` | EEG | EA0030 |
| 1 | `["MRI", "Yes", "Abnormal"]` | MRI- | EA0030 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["EEG", "Yes", "Abnormal"]` | EEG recording | EA0015 |
