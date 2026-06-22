# ExECTv2 Clinical-Recovery Error Ledger

- Generated: `2026-06-22`
- JSON: `experiments\exectv2_v0916_deepseek_reparse_dev140_error_ledger_20260622.json`
- Split: `dev`
- Letters: 140
- Structured JSONL: `experiments\exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140_20260622.jsonl`
- Diagnosis JSONL: `None`
- SeizureFrequency JSONL: `None`
- Investigations JSONL: `None`

## Headline Scores

| Entity | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.943 | 0.943 | 0.943 | 182 | 11 | 11 |
| Diagnosis | 0.821 | 0.827 | 0.816 | 253 | 53 | 57 |
| SeizureFrequency | 0.868 | 0.878 | 0.857 | 144 | 20 | 24 |
| Investigations | 0.923 | 0.968 | 0.882 | 120 | 4 | 16 |

## Prescription

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 2 | `["ordinary", "lamotrigine", "150", "mg", "2"]` | Lamotrigine- | EA0104, EA0182 |
| 1 | `["ordinary", "clobazam", "10", "mg", "1"]` | Current-medication:-Clobazam-10mg-on | EA0047 |
| 1 | `["ordinary", "lamotrigine", "100", "mg", "2"]` | Lamotrigine-100mg | EA0127 |
| 1 | `["ordinary", "lamotrigine", "200", "mg", "2"]` | lamotrigine- | EA0150 |
| 1 | `["ordinary", "lamotrigine", "75", "mg", "1"]` | Lamotrigine | EA0087 |
| 1 | `["ordinary", "lamotrigine", "75", "mg", "2"]` | He-is-currently-taking-lamotrigine-75mg-twice-a-day | EA0186 |
| 1 | `["ordinary", "levetiracetam", "1500", "mg", "2"]` | levetiracetam- | EA0150 |
| 1 | `["ordinary", "levetiracetam", "250", "mg", "1"]` | Levetiracetam-250mgs-once-a-day | EA0116 |
| 1 | `["ordinary", "perampanel", "50", "mg", "2"]` | Brivetiracetam- | EA0146 |
| 1 | `["ordinary", "sodium-valproate", "200", "mg", "2"]` | Sodium-Valproate-200-mg-twice-a-day-(to-be-increased-to-300-mg-BD-in-steps-of-100-mg-every-two-weeks) | EA0047 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["ordinary", "brivaracetam", "100", "mg", "2"]` | Brivaracetam 100mgs bd | EA0111 |
| 1 | `["ordinary", "brivaracetam", "50", "mg", "2"]` | Brivetiracetam 50mg bd | EA0146 |
| 1 | `["ordinary", "carbamazepine-controlled-release", "400", "mg", "2"]` | Carbamazepine Controlled Release 400mgs bd | EA0114 |
| 1 | `["ordinary", "levetiracetam", "1500", "mg", "2"]` | Levetiracetam 1500mg bd | EA0087 |
| 1 | `["ordinary", "levetiracetam", "500", "mg", "2"]` | Levetiracetam 500mg bd | EA0092 |
| 1 | `["ordinary", "phenytoin", "120", "mg", "2"]` | Phenytoin 120mg bd | EA0096 |
| 1 | `["ordinary", "sodium-valproate", "440", "mg", "2"]` | Sodium Valproate 440mg bd | EA0096 |
| 1 | `["rescue", "lamotrigine", "as_required"]` | lamotrigine 200mg bd | EA0150 |
| 1 | `["rescue", "levetiracetam", "as_required"]` | levetiracetam 1500mg bd | EA0150 |
| 1 | `["rescue", "midazolam", "as_required"]` | midazolam | EA0121 |
| 1 | `["rescue", "phenytoin", "as_required"]` | Phenytoin | EA0092 |

## Diagnosis

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 20 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0007, EA0010, EA0011, EA0035, EA0039, EA0049, EA0056, EA0124, ... |
| 11 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised-tonic-clonic-seizures | EA0006, EA0021, EA0025, EA0049, EA0079, EA0087, EA0111, EA0161 |
| 5 | `["Diagnosis", "focal seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0018, EA0022, EA0110, EA0132, EA0171 |
| 3 | `["Diagnosis", "focal to bilateral convulsive seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | bilateral-convulsive-seizure | EA0009, EA0011, EA0034 |
| 2 | `["Diagnosis", "epilepsy with generalised tonic clonic seizures alone", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epilepsy-with-generalised-tonic-clonic-seizure-alone | EA0005, EA0043 |
| 2 | `["Diagnosis", "epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epilepsy | EA0027, EA0164 |
| 2 | `["Diagnosis", "epileptic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epileptic-seizures | EA0057 |
| 2 | `["Diagnosis", "focal epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal-epilepsy | EA0141, EA0171 |
| 2 | `["Diagnosis", "focal seizures with altered awareness", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizures-with-altered-awareness | EA0054, EA0158 |
| 2 | `["Diagnosis", "focal seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0002, EA0133 |
| 2 | `["Diagnosis", "focal", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | Focal | EA0143, EA0190 |
| 2 | `["Diagnosis", "generalised seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised-seizures | EA0075, EA0136 |
| 2 | `["Diagnosis", "juvenile myoclonic epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | juvenile-myoclonic-epilepsy | EA0033, EA0125 |
| 2 | `["Diagnosis", "secondary generalised seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | secondary-generalised-seizures | EA0137, EA0152 |
| 1 | `["Diagnosis", "complex partial seizure", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | complex-partial-seizure | EA0157 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 41 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0002, EA0005, EA0006, EA0008, EA0019, EA0034, EA0040, EA0045, ... |
| 8 | `["Diagnosis", "epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epilepsy | EA0002, EA0004, EA0035, EA0047, EA0157, EA0168, EA0180, EA0188 |
| 6 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised tonic clonic seizures | EA0005, EA0020, EA0044, EA0162, EA0183, EA0195 |
| 5 | `["Diagnosis", "focal seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal seizures | EA0022, EA0110, EA0116, EA0132, EA0171 |
| 3 | `["Diagnosis", "epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | epilepsy | EA0027, EA0153, EA0168 |
| 2 | `["Diagnosis", "epileptic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epileptic seizures | EA0022, EA0164 |
| 2 | `["Diagnosis", "focal epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | localisation related epilepsy | EA0056, EA0152 |
| 2 | `["Diagnosis", "focal seizures with altered awareness", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal seizures with altered awareness | EA0143, EA0153 |
| 2 | `["Diagnosis", "nocturnal generalised tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | nocturnal generalised tonic clonic seizures | EA0079, EA0111 |
| 1 | `["Diagnosis", "absence events", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | absence events | EA0124 |
| 1 | `["Diagnosis", "absences", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | Generalised epilepsy with absences and GTCS | EA0161 |
| 1 | `["Diagnosis", "childhood absence seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | childhood absence seizures | EA0189 |
| 1 | `["Diagnosis", "complex partial seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | complex partial seizures | EA0157 |
| 1 | `["Diagnosis", "drug refactory focal epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | Drug refactory focal epilepsy | EA0175 |
| 1 | `["Diagnosis", "drug refractory epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | drug refractory epilepsy | EA0188 |

## SeizureFrequency

### Residual By State

| Side | active-rate | seizure-free | unknown |
| --- | ---: | ---: | ---: |
| gold | 10 | 10 | 16 |
| predicted | 14 | 5 | 5 |

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 10 | `[["cui", "C0036572"], "unknown"]` | seizures | EA0022, EA0059, EA0106, EA0108, EA0119, EA0123, EA0136, EA0161, ... |
| 5 | `[["cui", "C0036572"], "seizure-free"]` | seizures | EA0044, EA0063, EA0168, EA0180, EA0191 |
| 4 | `[["cui", "C0036572"], "active-rate"]` | seizures | EA0007, EA0009, EA0119, EA0199 |
| 3 | `[["cui", "C0027066"], "unknown"]` | myoclonic-jerks | EA0025, EA0049, EA0128 |
| 3 | `[["cui", "C0494475"], "active-rate"]` | generalised-tonic-clonic-seizures | EA0006, EA0038, EA0087 |
| 2 | `[["cui", "C0877017"], "active-rate"]` | focal-to-bilateral-convulsive-seizures | EA0054 |
| 2 | `[["cui", "C0877017"], "seizure-free"]` | focal-to-bilateral-convulsive-seizure | EA0011, EA0133 |
| 1 | `[["cui", "C0016399"], "seizure-free"]` | focal | EA0186 |
| 1 | `[["cui", "C0494475"], "seizure-free"]` | generalised-tonic-clonic-seizures | EA0020 |
| 1 | `[["cui", "C0494475"], "unknown"]` | tonic-clonic-seizures | EA0161 |
| 1 | `[["cui", "C0563606"], "active-rate"]` | absences | EA0047 |
| 1 | `[["cui", "C0563606"], "unknown"]` | absences | EA0082 |
| 1 | `[["cui", "C0751495"], "unknown"]` | focal-seizures | EA0068 |
| 1 | `[["cui", "C1299590"], "seizure-free"]` | seizure | EA0180 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 7 | `[["cui", "C0036572"], "active-rate"]` | seizures | EA0040, EA0085, EA0104, EA0148, EA0153, EA0198 |
| 4 | `[["cui", "C0036572"], "seizure-free"]` | seizures | EA0016, EA0071, EA0135, EA0171 |
| 2 | `[["cui", "C0494475"], "unknown"]` | generalised tonic clonic seizures | EA0049, EA0131 |
| 1 | `[["cui", "C0016399"], "unknown"]` | focal motor seizures | EA0158 |
| 1 | `[["cui", "C0036572"], "unknown"]` | seizures | EA0172 |
| 1 | `[["cui", "C0149958"], "active-rate"]` | complex partial seizures | EA0092 |
| 1 | `[["cui", "C0270834"], "active-rate"]` | focal impaired awareness seizures | EA0114 |
| 1 | `[["cui", "C0270834"], "unknown"]` | focal seizures with altered awareness | EA0121 |
| 1 | `[["cui", "C0270838"], "active-rate"]` | secondarily generalised seizures | EA0143 |
| 1 | `[["cui", "C0494475"], "active-rate"]` | generalised tonic clonic seizures | EA0020 |
| 1 | `[["cui", "C0751495"], "active-rate"]` | focal seizures | EA0133 |
| 1 | `[["cui", "C0877017"], "active-rate"]` | focal to bilateral convulsive seizure | EA0034 |
| 1 | `[["cui", "C1299590"], "seizure-free"]` | seizure-free | EA0006 |
| 1 | `[["phrase", "cluster of three seizures"], "active-rate"]` | cluster of three seizures | EA0162 |

## Investigations

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 6 | `["EEG", "Yes", "Abnormal"]` | EEG | EA0044, EA0111, EA0132, EA0175, EA0200 |
| 3 | `["EEG", "Yes", "Normal"]` | EEG | EA0076, EA0102, EA0146 |
| 2 | `["MRI", "Yes", "Abnormal"]` | MRI | EA0061, EA0142 |
| 2 | `["MRI", "Yes", "Normal"]` | MRI | EA0076, EA0188 |
| 1 | `["CT", "Yes", "Normal"]` | CT | EA0073 |
| 1 | `["CT", "Yes", "Unknown"]` | CT | EA0062 |
| 1 | `["EEG", "Yes", "Unknown"]` | EEG- | EA0179 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 2 | `["EEG", "Yes", "Abnormal"]` | EEG | EA0102, EA0120 |
| 1 | `["CT", "Yes", "Normal"]` | CT | EA0062 |
| 1 | `["EEG", "Yes", "Normal"]` | EEG | EA0182 |
