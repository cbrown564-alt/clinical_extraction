# ExECTv2 Clinical-Recovery Error Ledger

- Generated: `2026-06-21`
- JSON: `experiments\exectv2_holistic_finding_assembly_v07_error_ledger_dev140_20260621.json`
- Split: `dev`
- Letters: 140
- Structured JSONL: `experiments\exectv2_holistic_finding_assembly_v07_dev140_20260621.jsonl`
- Diagnosis JSONL: `None`
- SeizureFrequency JSONL: `None`
- Investigations JSONL: `None`

## Headline Scores

| Entity | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.821 | 0.809 | 0.834 | 161 | 38 | 32 |
| Diagnosis | 0.813 | 0.800 | 0.826 | 256 | 64 | 54 |
| SeizureFrequency | 0.926 | 0.918 | 0.934 | 157 | 14 | 11 |
| Investigations | 0.913 | 0.938 | 0.890 | 121 | 8 | 15 |

## Prescription

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 3 | `["ordinary", "lamotrigine", "150", "mg", "2"]` | Lamotrigine- | EA0104, EA0182 |
| 2 | `["ordinary", "carbamazepine", "200", "mg", "1"]` | Carbamazepine-400mg/400-mg/200mg | EA0038, EA0178 |
| 2 | `["ordinary", "carbamazepine", "400", "mg", "1"]` | Carbamazepine | EA0038 |
| 2 | `["ordinary", "sodium-valproate", "1000", "mg", "2"]` | Eplim-Chrono | EA0136, EA0198 |
| 2 | `["ordinary", "sodium-valproate", "200", "mg", "2"]` | Sodium-Valproate-200-mg-twice-a-day-(to-be-increased-to-300-mg-BD-in-steps-of-100-mg-every-two-weeks) | EA0047, EA0102 |
| 2 | `["ordinary", "sodium-valproate", "400", "mg", "2"]` | Medication:-epilim-400-milligrammes-twice-a-day | EA0125, EA0180 |
| 2 | `["ordinary", "sodium-valproate", "700", "mg", "1"]` | sodium-valproate-700-mg | EA0026, EA0124 |
| 2 | `["rescue", "clobazam", "as_required"]` | Clobazam- | EA0152, EA0158 |
| 2 | `["rescue", "midazolam", "as_required"]` | Midazolam- | EA0121, EA0158 |
| 1 | `["ordinary", "carbamazepine", "300", "mg", "1"]` | Tegretaol | EA0178 |
| 1 | `["ordinary", "carbamazepine", "400", "mg", "2"]` | He-is-currently-taking-carbamazepine-(Tegretol-retard)-400mg-twice-a-day-as-well-as-sodium-valproate-400mg-twice-a-day | EA0167 |
| 1 | `["ordinary", "clobazam", "10", "mg", "1"]` | Current-medication:-Clobazam-10mg-on | EA0047 |
| 1 | `["ordinary", "lamotrigine", "250", "mg", "2"]` | lamtorigine-250mg-bd | EA0061 |
| 1 | `["ordinary", "lamotrigine", "50", "mg", "1"]` | Lamotrigine-50mg-am | EA0087 |
| 1 | `["ordinary", "lamotrigine", "75", "mg", "1"]` | Lamotrigine | EA0087 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 5 | `["ordinary", "lamotrigine", "75", "mg", "2"]` | lamotrigine 75mg | EA0008, EA0092, EA0119, EA0120, EA0154 |
| 2 | `["ordinary", "lamotrigine", "25", "mg", "1"]` | lamotrigine 25 mg every day | EA0018, EA0045 |
| 2 | `["ordinary", "levetiracetam", "500", "mg", "2"]` | Levetiracetam 500mg bd | EA0092, EA0116 |
| 2 | `["rescue", "levetiracetam", "as_required"]` | levetiracetam | EA0078, EA0093 |
| 1 | `["ordinary", "brivaracetam", "150", "mg", "2"]` | Brivaracetam 150mg bd | EA0111 |
| 1 | `["ordinary", "brivaracetam", "50", "mg", "2"]` | Brivetiracetam 50mg bd | EA0146 |
| 1 | `["ordinary", "carbamazepine", "400", "mg", "2"]` | Carbamazepine is increased to 400mg bd | EA0108 |
| 1 | `["ordinary", "carbamazepine", "600", "mg", "2"]` | carbamazepine 600mg twice a day | EA0078 |
| 1 | `["ordinary", "carbamazepine-controlled-release", "400", "mg", "2"]` | Carbamazepine Controlled Release 400mg bd | EA0114 |
| 1 | `["ordinary", "clobazam", "10-20", "mg", "2"]` | Clobazam 10-20mg bd for seizure clusters | EA0152 |
| 1 | `["ordinary", "clopidogrel", "75", "mg", "1"]` | clopidogrel 75mg OD | EA0073 |
| 1 | `["ordinary", "eplim-chrono", "1000", "mg", "2"]` | Eplim Chrono | EA0136 |
| 1 | `["ordinary", "lamotrigine", "125", "mg", "2"]` | Lamotrigine 125mg twice daily | EA0166 |
| 1 | `["ordinary", "lamotrigine", "150", "mg", "2"]` | Lamotrigine 150mg twice daily | EA0166 |
| 1 | `["ordinary", "lamtorigine", "250", "mg", "2"]` | lamtorigine 250mg | EA0061 |

## Diagnosis

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 20 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0006, EA0035, EA0039, EA0057, EA0106, EA0128, EA0133, EA0137, ... |
| 7 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised-tonic-clonic-seizure | EA0005, EA0021, EA0049, EA0128, EA0161, EA0168, EA0180 |
| 4 | `["Diagnosis", "focal seizures with altered awareness", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizures-with-altered-awareness | EA0008, EA0054, EA0158, EA0167 |
| 3 | `["Diagnosis", "epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epilepsy | EA0062, EA0132, EA0164 |
| 3 | `["Diagnosis", "focal seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0018, EA0110, EA0171 |
| 3 | `["Diagnosis", "focal seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0002, EA0109, EA0133 |
| 3 | `["Diagnosis", "juvenile myoclonic epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | juvenile-myoclonic-epilepsy | EA0085, EA0113, EA0128 |
| 3 | `["Diagnosis", "juvenile myoclonic epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | juvenile-myoclonic-epilepsy | EA0033, EA0049, EA0125 |
| 3 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | tonic-clonic-seizures | EA0111, EA0116, EA0200 |
| 2 | `["Diagnosis", "absence seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | absence-seizures | EA0156, EA0161 |
| 2 | `["Diagnosis", "epilepsy with generalised tonic clonic seizures alone", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epilepsy-with-generalised-tonic-clonic-seizure-alone | EA0005, EA0043 |
| 2 | `["Diagnosis", "epileptic seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epileptic-seizures | EA0043, EA0164 |
| 2 | `["Diagnosis", "epileptic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epileptic-seizures | EA0057 |
| 2 | `["Diagnosis", "secondary generalised seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | secondary-generalised-seizures | EA0137, EA0152 |
| 2 | `["Diagnosis", "temporal lobe epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | temporal-lobe-epilepsy | EA0149, EA0185 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 30 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0019, EA0021, EA0022, EA0040, EA0044, EA0045, EA0054, EA0061, ... |
| 17 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | tonic clonic seizures | EA0020, EA0043, EA0087, EA0108, EA0111, EA0116, EA0123, EA0125, ... |
| 8 | `["Diagnosis", "focal seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal seizures | EA0008, EA0018, EA0054, EA0057, EA0110, EA0116, EA0167, EA0171 |
| 7 | `["Diagnosis", "focal", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal | EA0008, EA0011, EA0054, EA0061, EA0132, EA0152, EA0188 |
| 6 | `["Diagnosis", "focal epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | symptomatic structural focal epilepsy | EA0008, EA0010, EA0054, EA0108, EA0152, EA0186 |
| 4 | `["Diagnosis", "focal epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal epilepsy | EA0002, EA0061, EA0114, EA0188 |
| 2 | `["Diagnosis", "epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epilepsy | EA0035, EA0168 |
| 2 | `["Diagnosis", "focal epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | focal onset epilepsy | EA0110, EA0153 |
| 2 | `["Diagnosis", "focal seizures with altered awareness", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal seizures with altered awareness | EA0143, EA0153 |
| 2 | `["Diagnosis", "focal to bilateral convulsive seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal to bilateral convulsive seizures | EA0126, EA0186 |
| 2 | `["Diagnosis", "generalised", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised | EA0021, EA0127 |
| 2 | `["Diagnosis", "secondary", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | secondary | EA0152, EA0198 |
| 2 | `["Diagnosis", "temporal lobe epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | temporal lobe epilepsy | EA0143, EA0190 |
| 2 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | tonic clonic seizures | EA0168, EA0180 |
| 1 | `["Diagnosis", "complex partial seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | complex partial seizures | EA0157 |

## SeizureFrequency

### Residual By State

| Side | active-rate | seizure-free | unknown |
| --- | ---: | ---: | ---: |
| gold | 5 | 6 | 4 |
| predicted | 45 | 36 | 17 |

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 4 | `[["cui", "C0036572"], "active-rate"]` | seizure | EA0108, EA0117, EA0119, EA0157 |
| 4 | `[["cui", "C0036572"], "seizure-free"]` | seizures | EA0010, EA0137, EA0143, EA0191 |
| 2 | `[["cui", "C0036572"], "unknown"]` | seizures | EA0111, EA0198 |
| 2 | `[["cui", "C1299590"], "seizure-free"]` | seizure-free | EA0127, EA0180 |
| 1 | `[["cui", "C0027066"], "unknown"]` | myoclonic-jerks | EA0128 |
| 1 | `[["cui", "C0494475"], "active-rate"]` | generalised-tonic-clonic-seizure | EA0038 |
| 1 | `[["cui", "C0563606"], "unknown"]` | absences | EA0096 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 10 | `[["cui", "C0036572"], "seizure-free"]` | seizures | EA0063, EA0075, EA0127, EA0142, EA0162, EA0168, EA0171, EA0180, ... |
| 9 | `[["cui", "C0877017"], "seizure-free"]` | Focal to bilateral convulsive seizures | EA0011, EA0046, EA0054, EA0059, EA0061, EA0106, EA0126, EA0133, ... |
| 8 | `[["cui", "C0494475"], "active-rate"]` | generalised tonic clonic seizure | EA0019, EA0025, EA0049, EA0107, EA0139, EA0146, EA0161, EA0162 |
| 7 | `[["cui", "C0270838"], "active-rate"]` | secondary generalised seizures | EA0002, EA0067, EA0137, EA0150, EA0152 |
| 6 | `[["cui", "C0036572"], "unknown"]` | seizures | EA0008, EA0022, EA0059, EA0125, EA0131, EA0136 |
| 5 | `[["cui", "C0494475"], "seizure-free"]` | Generalised tonic clonic seizure | EA0005, EA0020, EA0035, EA0082 |
| 4 | `[["cui", "C0149958"], "active-rate"]` | complex partial seizures | EA0092, EA0150, EA0152 |
| 4 | `[["cui", "C0270834"], "active-rate"]` | focal seizures with altered awareness | EA0008, EA0011, EA0114, EA0132 |
| 3 | `[["cui", "C0016399"], "active-rate"]` | partial motor seizures | EA0056, EA0072, EA0106 |
| 3 | `[["cui", "C0036572"], "active-rate"]` | seizures | EA0074, EA0085, EA0198 |
| 3 | `[["cui", "C0234533"], "active-rate"]` | generalised seizures | EA0047, EA0158 |
| 3 | `[["cui", "C0270834"], "seizure-free"]` | Focal seizures with altered awareness | EA0059, EA0061, EA0190 |
| 3 | `[["cui", "C0563606"], "active-rate"]` | absence like seizures | EA0006, EA0082, EA0124 |
| 3 | `[["cui", "C0877017"], "active-rate"]` | focal to bilateral convulsive seizure | EA0034, EA0121, EA0186 |
| 2 | `[["cui", "C0027066"], "unknown"]` | myoclonic jerks | EA0025, EA0087 |

## Investigations

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 7 | `["EEG", "Yes", "Abnormal"]` | EEG | EA0044, EA0111, EA0117, EA0132, EA0182, EA0200 |
| 4 | `["MRI", "Yes", "Abnormal"]` | MRI | EA0046, EA0061, EA0104, EA0106 |
| 2 | `["EEG", "Yes", "Normal"]` | EEG | EA0102, EA0146 |
| 2 | `["MRI", "Yes", "Normal"]` | MRI | EA0188, EA0197 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 2 | `["EEG", "Yes", "Abnormal"]` | EEG recording | EA0015, EA0102 |
| 2 | `["EEG", "Yes", "Normal"]` | EEG | EA0120, EA0182 |
| 1 | `["EEG", "Yes", "Unknown"]` | Both have been captured on EEG in the past | EA0117 |
| 1 | `["MRI", "Yes", "Abnormal"]` | MRI scan | EA0197 |
| 1 | `["MRI", "Yes", "Normal"]` | MRI 3/4/2018 | EA0106 |
| 1 | `["MRI", "Yes", "Unknown"]` | follow up scan | EA0143 |
