# ExECTv2 Clinical-Recovery Error Ledger

- Generated: `2026-06-22`
- JSON: `experiments\exectv2_v0910_qwencompact_residualrepair_dev140_error_ledger_20260622.json`
- Split: `dev`
- Letters: 140
- Structured JSONL: `experiments\exectv2_holistic_finding_assembly_v0910_qwencompact_residualrepair_dev140_20260622.jsonl`
- Diagnosis JSONL: `None`
- SeizureFrequency JSONL: `None`
- Investigations JSONL: `None`

## Headline Scores

| Entity | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.904 | 0.929 | 0.881 | 170 | 13 | 23 |
| Diagnosis | 0.603 | 0.689 | 0.535 | 166 | 75 | 144 |
| SeizureFrequency | 0.594 | 0.605 | 0.583 | 98 | 64 | 70 |
| Investigations | 0.849 | 0.894 | 0.809 | 110 | 13 | 26 |

## Prescription

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 3 | `["ordinary", "sodium-valproate", "200", "mg", "2"]` | Sodium-Valproate-200-mg-twice-a-day-(to-be-increased-to-300-mg-BD-in-steps-of-100-mg-every-two-weeks) | EA0047, EA0102 |
| 2 | `["ordinary", "lamotrigine", "100", "mg", "2"]` | Lamotrigine-100mg | EA0127, EA0160 |
| 2 | `["ordinary", "lamotrigine", "150", "mg", "2"]` | Lamotrigine- | EA0104, EA0182 |
| 2 | `["ordinary", "lamotrigine", "200", "mg", "2"]` | lamotrigine- | EA0150, EA0172 |
| 1 | `["ordinary", "brivaracetam", "100", "mg", "2"]` | Brivaracetam | EA0172 |
| 1 | `["ordinary", "carbamazepine", "200", "mg", "2"]` | Medication:-Carbamazepine-200mg-twice-a-day | EA0149 |
| 1 | `["ordinary", "carbamazepine", "400", "mg", "2"]` | He-is-currently-taking-carbamazepine-(Tegretol-retard)-400mg-twice-a-day-as-well-as-sodium-valproate-400mg-twice-a-day | EA0167 |
| 1 | `["ordinary", "clobazam", "10", "mg", "1"]` | Current-medication:-Clobazam-10mg-on | EA0047 |
| 1 | `["ordinary", "lamotrigine", "75", "mg", "2"]` | He-is-currently-taking-lamotrigine-75mg-twice-a-day | EA0186 |
| 1 | `["ordinary", "levetiracetam", "1500", "mg", "2"]` | levetiracetam- | EA0150 |
| 1 | `["ordinary", "perampanel", "4", "mg", "1"]` | Perampanel | EA0172 |
| 1 | `["ordinary", "perampanel", "50", "mg", "2"]` | Brivetiracetam- | EA0146 |
| 1 | `["ordinary", "pregabalin", "75", "mg", "2"]` | Pregabalin-75-mgms-bd | EA0160 |
| 1 | `["ordinary", "sodium-valproate", "400", "mg", "2"]` | Sodium-valproate) | EA0168 |
| 1 | `["ordinary", "sodium-valproate", "500", "mg", "1"]` | -Episenta-500mg | EA0093 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["ordinary", "brivaracetam", "50", "mg", "2"]` | Brivetiracetam 50mg bd | EA0146 |
| 1 | `["ordinary", "carbamazepine-(tegretol-retard)", "400", "mg", "2"]` | carbamazepine (Tegretol retard) 400mg twice a day | EA0167 |
| 1 | `["ordinary", "carbamazepine-controlled-release", "200", "mg", "1"]` | 200mgs am | EA0114 |
| 1 | `["ordinary", "carbamazepine-controlled-release", "400", "mg", "1"]` | 400mgs pm | EA0114 |
| 1 | `["ordinary", "citalopram", "20", "mg", "1"]` | Citalopram 20mg od | EA0135 |
| 1 | `["ordinary", "eslicarbazine", "800", "mg", "1"]` | switch the carbamazepine to eslicarbazine | EA0052 |
| 1 | `["ordinary", "lamotrigine", "150", "mg", "2"]` | Lamotrigine 150mg twice daily | EA0166 |
| 1 | `["ordinary", "lamotrigine", "unknown", "mg", "1"]` | lamotrigine | EA0129 |
| 1 | `["ordinary", "levetiracetam", "750", "mg", "2"]` | Levetiracetam 1500mg bd | EA0087 |
| 1 | `["ordinary", "phenytoin", "100", "mg", "1"]` | Phenytoin 100mg od | EA0046 |
| 1 | `["rescue", "clobazam", "as_required"]` | clobazam 10 to 20 mg at night for up to 5 days for seizure clusters. | EA0050 |
| 1 | `["rescue", "lamotrigine", "as_required"]` | lamotrigine 200mg | EA0150 |
| 1 | `["rescue", "levetiracetam", "as_required"]` | levetiracetam 1500mg | EA0150 |

## Diagnosis

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 39 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0007, EA0010, EA0011, EA0033, EA0035, EA0039, EA0045, EA0049, ... |
| 27 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised-tonic-clonic-seizure | EA0005, EA0006, EA0021, EA0025, EA0038, EA0049, EA0050, EA0079, ... |
| 14 | `["Diagnosis", "focal to bilateral convulsive seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | bilateral-convulsive-seizure | EA0009, EA0010, EA0011, EA0034, EA0046, EA0054, EA0057, EA0059, ... |
| 10 | `["Diagnosis", "focal epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | symptomatic-structural-focal-epilepsy | EA0010, EA0046, EA0056, EA0059, EA0061, EA0111, EA0114, EA0153, ... |
| 10 | `["Diagnosis", "focal seizures with altered awareness", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizures-with-altered-awareness | EA0008, EA0011, EA0054, EA0059, EA0061, EA0119, EA0132, EA0158, ... |
| 8 | `["Diagnosis", "focal seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0002, EA0034, EA0133, EA0149, EA0185 |
| 7 | `["Diagnosis", "secondary generalised seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | secondary-generalised-seizures | EA0002, EA0056, EA0067, EA0072, EA0137, EA0152, EA0198 |
| 5 | `["Diagnosis", "focal motor seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-motor-seizures | EA0057, EA0106, EA0133, EA0158, EA0186 |
| 4 | `["Diagnosis", "focal seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0018, EA0022, EA0110, EA0171 |
| 4 | `["Diagnosis", "generalised seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised-seizures | EA0047, EA0075, EA0136, EA0158 |
| 3 | `["Diagnosis", "complex partial seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | complex-partial-seizures | EA0092, EA0152, EA0198 |
| 3 | `["Diagnosis", "epileptic seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epileptic-seizures | EA0043, EA0135, EA0141 |
| 3 | `["Diagnosis", "focal epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal-onset-epilepsy | EA0045, EA0141, EA0171 |
| 3 | `["Diagnosis", "juvenile myoclonic epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | juvenile-myoclonic-epilepsy | EA0085, EA0113, EA0168 |
| 3 | `["Diagnosis", "juvenile myoclonic epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | juvenile-myoclonic-epilepsy | EA0033, EA0049, EA0085 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 34 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0002, EA0005, EA0008, EA0019, EA0021, EA0034, EA0040, EA0044, ... |
| 10 | `["Diagnosis", "epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epilepsy | EA0002, EA0004, EA0047, EA0059, EA0132, EA0153, EA0157, EA0180, ... |
| 7 | `["Diagnosis", "focal epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | Focal epilepsy | EA0045, EA0054, EA0106, EA0135, EA0152, EA0154 |
| 5 | `["Diagnosis", "focal epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | Symptomatic structural focal epilepsy (probable perinatal insult) | EA0010, EA0059, EA0061, EA0110, EA0188 |
| 4 | `["Diagnosis", "anxiety", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | Anxiety | EA0024, EA0076, EA0102, EA0180 |
| 4 | `["Diagnosis", "focal seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal seizures | EA0110, EA0116, EA0143, EA0171 |
| 4 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised tonic clonic seizures | EA0020, EA0116, EA0162, EA0195 |
| 2 | `["Diagnosis", "focal epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | focal epilepsy | EA0114, EA0153 |
| 2 | `["Diagnosis", "juvenile myoclonic epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | possible JME | EA0025, EA0026 |
| 1 | `["Diagnosis", "absence events", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | absence events | EA0124 |
| 1 | `["Diagnosis", "chronic migraine", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | Chronic migraine | EA0067 |
| 1 | `["Diagnosis", "complex partial seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | Complex partial seizures with secondary generalised seizures | EA0198 |
| 1 | `["Diagnosis", "complex partial", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | complex partial | EA0157 |
| 1 | `["Diagnosis", "depression", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | Anxiety and depression | EA0180 |
| 1 | `["Diagnosis", "drug refractory epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | drug refractory epilepsy | EA0188 |

## SeizureFrequency

### Residual By State

| Side | active-rate | seizure-free | unknown |
| --- | ---: | ---: | ---: |
| gold | 35 | 29 | 23 |
| predicted | 34 | 19 | 15 |

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 16 | `[["cui", "C0036572"], "active-rate"]` | seizures | EA0007, EA0009, EA0071, EA0085, EA0108, EA0110, EA0111, EA0113, ... |
| 13 | `[["cui", "C0036572"], "seizure-free"]` | seizures | EA0010, EA0034, EA0044, EA0063, EA0093, EA0127, EA0142, EA0162, ... |
| 13 | `[["cui", "C0036572"], "unknown"]` | seizures | EA0022, EA0050, EA0059, EA0106, EA0108, EA0111, EA0119, EA0121, ... |
| 7 | `[["cui", "C0494475"], "active-rate"]` | generalised-tonic-clonic-seizures | EA0006, EA0019, EA0049, EA0079, EA0087, EA0096, EA0139 |
| 6 | `[["cui", "C1299590"], "seizure-free"]` | seizure-free | EA0084, EA0088, EA0102, EA0156, EA0168, EA0180 |
| 4 | `[["cui", "C0270834"], "active-rate"]` | focal-seizures-with-altered-awareness | EA0008, EA0054, EA0158 |
| 4 | `[["cui", "C0877017"], "seizure-free"]` | focal-to-bilateral-convulsive-seizure | EA0011, EA0057, EA0106, EA0190 |
| 3 | `[["cui", "C0027066"], "unknown"]` | myoclonic-jerks | EA0025, EA0049, EA0128 |
| 3 | `[["cui", "C0563606"], "unknown"]` | absence | EA0049, EA0082, EA0096 |
| 2 | `[["cui", "C0270834"], "seizure-free"]` | focal-seizures-with-altered-awareness | EA0143, EA0190 |
| 2 | `[["cui", "C0270838"], "active-rate"]` | secondary-generalised-seizure | EA0152, EA0188 |
| 2 | `[["cui", "C0494475"], "unknown"]` | generalised-tonic-clonic-seizures | EA0049, EA0161 |
| 2 | `[["cui", "C0877017"], "active-rate"]` | focal-to-bilateral-convulsive-seizures | EA0054 |
| 1 | `[["cui", "C0016399"], "active-rate"]` | focal-motor-seizure | EA0072 |
| 1 | `[["cui", "C0016399"], "seizure-free"]` | focal-motor-seizures | EA0057 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 8 | `[["cui", "C0036572"], "seizure-free"]` | seizure | EA0071, EA0084, EA0087, EA0088, EA0102, EA0123, EA0156, EA0180 |
| 5 | `[["cui", "C0036572"], "unknown"]` | seizures | EA0040, EA0063, EA0067, EA0139, EA0154 |
| 4 | `[["cui", "C0036572"], "active-rate"]` | seizures | EA0100, EA0109, EA0148, EA0179 |
| 3 | `[["cui", "C0494475"], "active-rate"]` | generalised tonic clonic seizures | EA0020, EA0146, EA0161 |
| 3 | `[["cui", "C0877017"], "active-rate"]` | focal to bilateral convulsive seizure | EA0034, EA0045, EA0057 |
| 2 | `[["cui", "C0270834"], "active-rate"]` | focal impaired awareness seizures | EA0114, EA0132 |
| 2 | `[["cui", "C0563606"], "unknown"]` | absence like seizures | EA0006, EA0161 |
| 2 | `[["cui", "C0751495"], "unknown"]` | focal seizures | EA0008, EA0158 |
| 1 | `[["cui", "C0494475"], "unknown"]` | generalised tonic clonic seizures | EA0087 |
| 1 | `[["cui", "C0751495"], "active-rate"]` | focal seizures | EA0054 |
| 1 | `[["cui", "C1299590"], "seizure-free"]` | seizure-free | EA0006 |
| 1 | `[["cui", "C4316903"], "seizure-free"]` | typical absences | EA0184 |
| 1 | `[["phrase", "3 or 4 focal to bilateral convulsive seizures"], "active-rate"]` | 3 or 4 focal to bilateral convulsive seizures | EA0010 |
| 1 | `[["phrase", "3 seizures"], "active-rate"]` | 3 seizures | EA0142 |
| 1 | `[["phrase", "a seizure"], "active-rate"]` | a seizure | EA0071 |

## Investigations

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 12 | `["EEG", "Yes", "Abnormal"]` | EEG | EA0044, EA0046, EA0079, EA0111, EA0132, EA0137, EA0149, EA0152, ... |
| 5 | `["MRI", "Yes", "Abnormal"]` | MRI-brain | EA0010, EA0030, EA0046, EA0061 |
| 3 | `["EEG", "Yes", "Normal"]` | EEG | EA0102, EA0146, EA0182 |
| 2 | `["MRI", "Yes", "Normal"]` | MRI-negative | EA0111, EA0188 |
| 1 | `["CT", "Yes", "Abnormal"]` | CT-scan | EA0016 |
| 1 | `["CT", "Yes", "Normal"]` | CT | EA0073 |
| 1 | `["CT", "Yes", "Unknown"]` | CT | EA0062 |
| 1 | `["EEG", "Yes", "Unknown"]` | EEG- | EA0179 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 2 | `["EEG", "Yes", "Abnormal"]` | EEG | EA0102, EA0120 |
| 2 | `["EEG", null, "Normal"]` | EEG | EA0075, EA0156 |
| 2 | `["MRI", "Yes", "Normal"]` | follow up scan | EA0143, EA0164 |
| 2 | `["MRI", null, "Normal"]` | MRI | EA0156, EA0175 |
| 1 | `["CT", "Yes", "Normal"]` | CT head | EA0164 |
| 1 | `["CT", null, "Normal"]` | CT head | EA0189 |
| 1 | `["EEG", null, "Unknown"]` | MRI scan | EA0179 |
| 1 | `["EEG", null, null]` | MRI brain | EA0075 |
| 1 | `["MRI", "Yes", "Abnormal"]` | MRI scan | EA0197 |
