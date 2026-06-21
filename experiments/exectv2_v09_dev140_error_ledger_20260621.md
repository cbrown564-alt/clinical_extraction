# ExECTv2 Clinical-Recovery Error Ledger

- Generated: `2026-06-21`
- JSON: `experiments\exectv2_v09_dev140_error_ledger_20260621.json`
- Split: `dev`
- Letters: 140
- Structured JSONL: `experiments\exectv2_llm_only_key_entities_structured_v09_dev140_gpt41mini_20260621.jsonl`
- Diagnosis JSONL: `None`
- SeizureFrequency JSONL: `None`
- Investigations JSONL: `None`

## Headline Scores

| Entity | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.751 | 0.785 | 0.720 | 139 | 38 | 54 |
| Diagnosis | 0.591 | 0.613 | 0.571 | 177 | 112 | 133 |
| SeizureFrequency | 0.668 | 0.624 | 0.720 | 121 | 73 | 47 |
| Investigations | 0.855 | 0.916 | 0.801 | 109 | 10 | 27 |

## Prescription

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 3 | `["ordinary", "clobazam", "10", "mg", "1"]` | Current-medication:-Clobazam-10mg-on | EA0047, EA0082, EA0135 |
| 3 | `["ordinary", "perampanel", "8", "mg", "1"]` | Perampanel- | EA0117, EA0121, EA0158 |
| 2 | `["ordinary", "carbamazepine", "200", "mg", "1"]` | Carbamazepine-400mg/400-mg/200mg | EA0038, EA0088 |
| 2 | `["ordinary", "carbamazepine", "400", "mg", "1"]` | Carbamazepine | EA0038 |
| 2 | `["ordinary", "lamotrigine", "150", "mg", "2"]` | Lamotrigine- | EA0104, EA0182 |
| 2 | `["ordinary", "sodium-valproate", "200", "mg", "2"]` | Sodium-Valproate-200-mg-twice-a-day-(to-be-increased-to-300-mg-BD-in-steps-of-100-mg-every-two-weeks) | EA0047, EA0102 |
| 2 | `["ordinary", "sodium-valproate", "700", "mg", "1"]` | Medication:-Sodium-Valproate-700mg-in-the-morning | EA0021, EA0183 |
| 2 | `["ordinary", "sodium-valproate", "800", "mg", "1"]` | Sodium-Valproate | EA0021, EA0183 |
| 2 | `["rescue", "clobazam", "as_required"]` | Clobazam- | EA0152, EA0158 |
| 2 | `["rescue", "midazolam", "as_required"]` | Midazolam- | EA0121, EA0158 |
| 1 | `["ordinary", "brivaracetam", "50", "mg", "2"]` | Brivetiracetam- | EA0067 |
| 1 | `["ordinary", "carbamazepine", "100", "mg", "1"]` | Medication:-Carbamazepine-100mg-am | EA0088 |
| 1 | `["ordinary", "carbamazepine", "200", "mg", "2"]` | Carbamazepine-200-mg-twice-a-day | EA0005 |
| 1 | `["ordinary", "carbamazepine", "300", "mg", "2"]` | Carbamazepine-300mg-bd | EA0108 |
| 1 | `["ordinary", "clobazam", "10", "mg", "2"]` | Clobazam-10-mg-BD | EA0038 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 4 | `["ordinary", "lamotrigine", "25", "mg", "1"]` | lamotrigine | EA0043, EA0062, EA0141, EA0153 |
| 3 | `["ordinary", "levetiracetam", "250", "mg", "1"]` | levetiracetam at a dose of 250mg once-a-day | EA0008, EA0016, EA0110 |
| 2 | `["ordinary", "brivaracetam", "100", "mg", "2"]` | Brivaracetam 100mgs bd | EA0111, EA0150 |
| 2 | `["ordinary", "lamotrigine", "75", "mg", "2"]` | lamotrigine 75mg bd | EA0008, EA0154 |
| 2 | `["ordinary", "sodium-valproate", "700", "mg", "2"]` | Sodium Valproate 700mg in the morning and 800mg nocte | EA0021, EA0183 |
| 1 | `["ordinary", "brivaracetam", "50", "mg", "2"]` | Brivetiracetam 50mg bd | EA0146 |
| 1 | `["ordinary", "carbamazepine", "100", "mg", "2"]` | Carbamazepine 100mg bd | EA0109 |
| 1 | `["ordinary", "carbamazepine", "600", "mg", "2"]` | carbamazepine | EA0078 |
| 1 | `["ordinary", "clobazam", "10", "mg", "2"]` | Clobazam 10mg bd as required | EA0158 |
| 1 | `["ordinary", "clobazam", "10-20", "mg", "2"]` | Clobazam 10-20mg bd | EA0152 |
| 1 | `["ordinary", "eplim-chrono", "1000", "mg", "2"]` | Eplim Chrono 1000mg bd | EA0136 |
| 1 | `["ordinary", "eslicarbazepine", "1200", "mg", "1"]` | eslicarbazepine | EA0135 |
| 1 | `["ordinary", "eslicarbazepine", "400", "mg", "1"]` | eslicarbazepine 400mg od | EA0132 |
| 1 | `["ordinary", "eslicarbazepine", "800", "mg", "1"]` | eslicarbazepine 800mg od | EA0132 |
| 1 | `["ordinary", "eslicarbazine", "800", "mg", "1"]` | eslicarbazine 800mg od | EA0052 |

## Diagnosis

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 53 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0004, EA0006, EA0007, EA0010, EA0011, EA0033, EA0035, EA0039, ... |
| 22 | `["Diagnosis", "focal epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-epilepsy | EA0002, EA0010, EA0046, EA0054, EA0057, EA0059, EA0061, EA0106, ... |
| 17 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised-tonic-clonic-seizure | EA0005, EA0006, EA0021, EA0025, EA0038, EA0049, EA0079, EA0082, ... |
| 6 | `["Diagnosis", "focal epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal-epilepsy | EA0004, EA0045, EA0132, EA0141, EA0157, EA0171 |
| 6 | `["Diagnosis", "focal seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0002, EA0034, EA0109, EA0126, EA0133 |
| 6 | `["Diagnosis", "focal to bilateral convulsive seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | bilateral-convulsive-seizure | EA0009, EA0011, EA0034, EA0054, EA0061, EA0133 |
| 4 | `["Diagnosis", "epileptic seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epileptic-seizures | EA0043, EA0135, EA0141, EA0164 |
| 4 | `["Diagnosis", "generalised", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised | EA0123, EA0128, EA0183, EA0195 |
| 3 | `["Diagnosis", "epilepsy with generalised tonic clonic seizures alone", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy-with-generalised-tonic-clonic-seizures-alone | EA0005, EA0035, EA0044 |
| 3 | `["Diagnosis", "epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epilepsy | EA0027, EA0132, EA0164 |
| 3 | `["Diagnosis", "focal seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0022, EA0110, EA0171 |
| 3 | `["Diagnosis", "generalised seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised-seizures | EA0075, EA0107, EA0136 |
| 3 | `["Diagnosis", "juvenile myoclonic epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | juvenile-myoclonic-epilepsy | EA0085, EA0113, EA0128 |
| 3 | `["Diagnosis", "juvenile myoclonic epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | juvenile-myoclonic-epilepsy | EA0033, EA0049, EA0125 |
| 3 | `["Diagnosis", "secondary generalised seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | secondary-generalised-seizures | EA0040, EA0072, EA0152 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 9 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0012, EA0014, EA0021, EA0034, EA0125, EA0132, EA0164, EA0179, ... |
| 9 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised tonic clonic seizures | EA0020, EA0043, EA0044, EA0111, EA0116, EA0162, EA0183, EA0195, ... |
| 6 | `["Diagnosis", "dissociative seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | dissociative seizures | EA0022, EA0057, EA0082, EA0117, EA0120, EA0146 |
| 6 | `["Diagnosis", "epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epilepsy | EA0004, EA0006, EA0141, EA0171, EA0179, EA0186 |
| 5 | `["Diagnosis", "focal epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal epilepsy | EA0002, EA0061, EA0186, EA0188 |
| 5 | `["Diagnosis", "myoclonic jerks", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | myoclonic jerks | EA0025, EA0026, EA0033, EA0050, EA0128 |
| 5 | `["Diagnosis", "symptomatic structural epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | symptomatic structural epilepsy | EA0106, EA0133, EA0150, EA0152, EA0158 |
| 4 | `["Diagnosis", "absences", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | absences | EA0033, EA0047, EA0050, EA0096 |
| 2 | `["Diagnosis", "epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | epilepsy | EA0027, EA0164 |
| 2 | `["Diagnosis", "febrile seizure", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | febrile seizure | EA0043, EA0061 |
| 2 | `["Diagnosis", "focal dyscognitive seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal dyscognitive seizures | EA0169, EA0181 |
| 2 | `["Diagnosis", "focal seizures with altered awareness", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal seizures with altered awareness | EA0143, EA0153 |
| 2 | `["Diagnosis", "non epileptic psychogenic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | non-epileptic psychogenic seizures | EA0056, EA0102 |
| 2 | `["Diagnosis", "tuberous sclerosis", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | tuberous sclerosis | EA0126, EA0158 |
| 1 | `["Diagnosis", "absence epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | absence epilepsy | EA0049 |

## SeizureFrequency

### Residual By State

| Side | active-rate | seizure-free | unknown |
| --- | ---: | ---: | ---: |
| gold | 25 | 18 | 21 |
| predicted | 38 | 21 | 21 |

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 12 | `[["cui", "C0036572"], "unknown"]` | seizures | EA0022, EA0050, EA0108, EA0111, EA0119, EA0121, EA0123, EA0125, ... |
| 9 | `[["cui", "C0036572"], "seizure-free"]` | seizures | EA0010, EA0044, EA0063, EA0137, EA0162, EA0168, EA0182, EA0191 |
| 7 | `[["cui", "C0036572"], "active-rate"]` | seizures | EA0007, EA0009, EA0108, EA0113, EA0119, EA0195 |
| 7 | `[["cui", "C0494475"], "active-rate"]` | generalised-tonic-clonic-seizures | EA0006, EA0019, EA0038, EA0049, EA0079, EA0096, EA0139 |
| 3 | `[["cui", "C0027066"], "active-rate"]` | myoclonic-jerks | EA0049, EA0050, EA0087 |
| 3 | `[["cui", "C0563606"], "active-rate"]` | absence-like-seizures | EA0006, EA0047, EA0161 |
| 3 | `[["cui", "C0877017"], "seizure-free"]` | focal-to-bilateral-convulsive-seizure | EA0011, EA0121, EA0133 |
| 2 | `[["cui", "C0027066"], "unknown"]` | myoclonic-jerks | EA0025, EA0128 |
| 2 | `[["cui", "C0494475"], "unknown"]` | generalised | EA0087, EA0161 |
| 2 | `[["cui", "C0563606"], "unknown"]` | absences | EA0050, EA0082 |
| 2 | `[["cui", "C0877017"], "active-rate"]` | focal-to-bilateral-convulsive-seizures | EA0054 |
| 2 | `[["cui", "C1299590"], "seizure-free"]` | seizure-free | EA0127, EA0180 |
| 2 | `[["cui", "C3203523"], "active-rate"]` | cluster-of-seizures | EA0009, EA0110 |
| 1 | `[["cui", "C0016399"], "seizure-free"]` | focal | EA0186 |
| 1 | `[["cui", "C0234533"], "seizure-free"]` | generalised-convulsions | EA0136 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 18 | `[["cui", "C0036572"], "active-rate"]` | seizure | EA0016, EA0021, EA0043, EA0062, EA0085, EA0109, EA0129, EA0137, ... |
| 12 | `[["cui", "C0036572"], "unknown"]` | seizures | EA0007, EA0021, EA0040, EA0078, EA0096, EA0104, EA0143, EA0158, ... |
| 9 | `[["cui", "C0036572"], "seizure-free"]` | seizures | EA0016, EA0019, EA0071, EA0096, EA0123, EA0127, EA0141, EA0171 |
| 8 | `[["cui", "C1299590"], "seizure-free"]` | seizure free | EA0006, EA0035, EA0038, EA0085, EA0087, EA0104, EA0113, EA0157 |
| 3 | `[["cui", "C0494475"], "unknown"]` | generalised tonic clonic seizures | EA0021, EA0096, EA0183 |
| 3 | `[["cui", "C0877017"], "active-rate"]` | focal to bilateral convulsive seizures | EA0010, EA0121, EA0132 |
| 2 | `[["cui", "C0751495"], "active-rate"]` | focal seizures | EA0018, EA0132 |
| 2 | `[["cui", "C0751495"], "unknown"]` | focal seizures | EA0121, EA0133 |
| 1 | `[["cui", "C0016399"], "unknown"]` | focal motor seizures | EA0186 |
| 1 | `[["cui", "C0494475"], "active-rate"]` | grand mal | EA0146 |
| 1 | `[["cui", "C0877017"], "seizure-free"]` | focal to bilateral convulsive seizures | EA0045 |
| 1 | `[["phrase", "absence seizures"], "active-rate"]` | absence seizures | EA0161 |
| 1 | `[["phrase", "absence seizures"], "seizure-free"]` | absence seizures | EA0189 |
| 1 | `[["phrase", "attacks"], "active-rate"]` | attacks | EA0052 |
| 1 | `[["phrase", "attacks"], "unknown"]` | attacks | EA0104 |

## Investigations

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 10 | `["EEG", "Yes", "Abnormal"]` | EEG | EA0082, EA0111, EA0117, EA0131, EA0132, EA0150, EA0152, EA0182, ... |
| 8 | `["MRI", "Yes", "Abnormal"]` | MRI-scan | EA0002, EA0010, EA0046, EA0054, EA0061, EA0104, EA0106 |
| 3 | `["EEG", "Yes", "Normal"]` | EEG | EA0082, EA0102, EA0146 |
| 2 | `["CT", "Yes", "Normal"]` | CT | EA0073, EA0189 |
| 1 | `["CT", "Yes", "Abnormal"]` | CT-scan | EA0016 |
| 1 | `["CT", "Yes", "Unknown"]` | CT | EA0062 |
| 1 | `["EEG", "Yes", "Unknown"]` | EEG- | EA0179 |
| 1 | `["MRI", "Yes", "Normal"]` | MRI | EA0188 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 4 | `["MRI", "Yes", null]` | MRI scan | EA0002, EA0010, EA0054, EA0061 |
| 2 | `["EEG", "Yes", "Abnormal"]` | EEG | EA0015, EA0102 |
| 1 | `["CT", "Yes", null]` | CT | EA0062 |
| 1 | `["EEG", "Yes", "Normal"]` | EEG | EA0182 |
| 1 | `["EEG", "Yes", null]` | EEG | EA0117 |
| 1 | `["MRI", "Yes", "Normal"]` | MRI | EA0106 |
