# ExECTv2 Clinical-Recovery Error Ledger

- Generated: `2026-06-18`
- JSON: `experiments\exectv2_key_entities_clinical_error_ledger_dev140_20260618.json`
- Split: `dev`
- Letters: 140
- Structured JSONL: `experiments\exectv2_llm_only_key_entities_structured_v05_dev140_gpt41mini_20260618.jsonl`
- Diagnosis JSONL: `experiments\exectv2_llm_diagnosis_verifier_v05_dev140_gpt41mini_20260618.jsonl`
- SeizureFrequency JSONL: `experiments\exectv2_llm_sf_verifier_v03_dev140_gpt41mini_20260618.jsonl`

## Headline Scores

| Entity | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.777 | 0.768 | 0.788 | 152 | 46 | 41 |
| Diagnosis | 0.616 | 0.680 | 0.564 | 208 | 98 | 161 |
| SeizureFrequency | 0.602 | 0.594 | 0.610 | 114 | 78 | 73 |
| Investigations | 0.786 | 0.752 | 0.824 | 112 | 37 | 24 |

## Prescription

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 3 | `["ordinary", "clobazam", "10", "mg", "1"]` | Current-medication:-Clobazam-10mg-on | EA0047, EA0082 |
| 3 | `["ordinary", "lamotrigine", "100", "mg", "2"]` | lamotrigine- | EA0009, EA0127, EA0142 |
| 2 | `["ordinary", "carbamazepine", "200", "mg", "1"]` | Carbamazepine-400mg/400-mg/200mg | EA0038, EA0088 |
| 2 | `["ordinary", "carbamazepine", "400", "mg", "1"]` | Carbamazepine | EA0038 |
| 2 | `["ordinary", "lamotrigine", "150", "mg", "2"]` | Lamotrigine- | EA0104, EA0182 |
| 2 | `["ordinary", "perampanel", "8", "mg", "1"]` | Perampanel- | EA0117, EA0158 |
| 2 | `["ordinary", "sodium-valproate", "500", "mg", "1"]` | -Episenta-500mg | EA0093, EA0124 |
| 2 | `["rescue", "midazolam", "as_required"]` | Midazolam- | EA0121, EA0158 |
| 1 | `["ordinary", "brivaracetam", "50", "mg", "2"]` | ·-Brivaracetam-50mgs-bd | EA0084 |
| 1 | `["ordinary", "carbamazepine", "100", "mg", "1"]` | Medication:-Carbamazepine-100mg-am | EA0088 |
| 1 | `["ordinary", "carbamazepine", "300", "mg", "2"]` | Carbamazepine-300mg-bd | EA0108 |
| 1 | `["ordinary", "carbamazepine", "400", "mg", "2"]` | carbamazepine-400mg-twice-a-day | EA0079 |
| 1 | `["ordinary", "lamotrigine", "125", "mg", "2"]` | Current-antiepileptic-medication:-Lamotrigine-125-milligrams-twice-a-day | EA0004 |
| 1 | `["ordinary", "lamotrigine", "200", "mg", "2"]` | lamotrigine- | EA0150 |
| 1 | `["ordinary", "lamotrigine", "50", "mg", "1"]` | Lamotrigine-50mg-am | EA0087 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 9 | `["ordinary", "lamotrigine", "75", "mg", "2"]` | lamotrigine 75mg bd | EA0008, EA0018, EA0045, EA0062, EA0119, EA0120, EA0141, EA0154, ... |
| 8 | `["ordinary", "lamotrigine", "25", "mg", "1"]` | lamotrigine at 25 mg every day | EA0018, EA0043, EA0045, EA0062, EA0141, EA0153, EA0157, EA0199 |
| 2 | `["ordinary", "carbamazepine", "100", "mg", "2"]` | Carbamazepine 100mg bd | EA0109 |
| 2 | `["ordinary", "levetiracetam", "250", "mg", "1"]` | levetiracetam | EA0008, EA0110 |
| 1 | `["ordinary", "brivaracetam", "50", "mg", "2"]` | Brivetiracetam 50mg bd | EA0146 |
| 1 | `["ordinary", "carbamazepine", "400", "mg", "2"]` | Carbamazepine is increased to 400mg bd | EA0108 |
| 1 | `["ordinary", "carbamazepine", "600", "mg", "2"]` | carbamazepine 600mg twice a day | EA0078 |
| 1 | `["ordinary", "citalopram", "20", "mg", "1"]` | Citalopram 20mg od | EA0135 |
| 1 | `["ordinary", "clobazam", "10-20", "mg", "2"]` | Clobazam 10-20mg bd | EA0152 |
| 1 | `["ordinary", "clopidogrel", "75", "mg", "1"]` | Clopidogrel 75mg od | EA0133 |
| 1 | `["ordinary", "eplim-chrono", "1000", "mg", "2"]` | Eplim Chrono 1000mg bd | EA0136 |
| 1 | `["ordinary", "eslicarbazepine", "1200", "mg", "1"]` | eslicarbazepine | EA0135 |
| 1 | `["ordinary", "eslicarbazepine", "400", "mg", "1"]` | eslicarbazepine 400mg od | EA0132 |
| 1 | `["ordinary", "eslicarbazine", "800", "mg", "1"]` | eslicarbazine 800mg od | EA0052 |
| 1 | `["ordinary", "lamotrigine", "125", "mg", "2"]` | Lamotrigine 125mg twice daily | EA0166 |

## Diagnosis

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 68 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0004, EA0006, EA0007, EA0010, EA0011, EA0033, EA0035, EA0039, ... |
| 11 | `["Diagnosis", "symptomatic structural focal epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | symptomatic-structural-focal-epilepsy | EA0010, EA0046, EA0054, EA0057, EA0059, EA0106, EA0133, EA0150, ... |
| 11 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised-tonic-clonic-seizures | EA0005, EA0006, EA0021, EA0049, EA0123, EA0128, EA0161, EA0168, ... |
| 8 | `["Diagnosis", "focal seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0002, EA0054, EA0109, EA0126, EA0133, EA0158 |
| 6 | `["Diagnosis", "focal epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-epilepsy | EA0002, EA0061, EA0114, EA0142, EA0153, EA0188 |
| 6 | `["Diagnosis", "focal seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0018, EA0022, EA0110, EA0132, EA0153, EA0171 |
| 5 | `["Diagnosis", "epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epilepsy-with-generalised-tonic-clonic-seizure-alone | EA0005, EA0043, EA0062, EA0132, EA0164 |
| 4 | `["Diagnosis", "generalised tonic clonic seizure", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised-tonic-clonic-seizure | EA0038, EA0049, EA0079, EA0087 |
| 4 | `["Diagnosis", "generalised", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised | EA0123, EA0128, EA0183, EA0195 |
| 3 | `["Diagnosis", "epileptic seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epileptic-seizures | EA0043, EA0135, EA0164 |
| 3 | `["Diagnosis", "focal to bilateral convulsive seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-to-bilateral-convulsive-seizures | EA0011, EA0034, EA0061 |
| 3 | `["Diagnosis", "generalised seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised-seizures | EA0047, EA0075, EA0107 |
| 3 | `["Diagnosis", "juvenile myoclonic epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | juvenile-myoclonic-epilepsy | EA0085, EA0113, EA0128 |
| 3 | `["Diagnosis", "juvenile myoclonic epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | juvenile-myoclonic-epilepsy | EA0033, EA0049, EA0125 |
| 3 | `["Diagnosis", "secondary generalised seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | secondary-generalised-seizures | EA0040, EA0150, EA0152 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 14 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | tonic clonic seizures | EA0038, EA0040, EA0043, EA0047, EA0079, EA0108, EA0116, EA0125, ... |
| 7 | `["Diagnosis", "symptomatic structural epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | symptomatic structural epilepsy | EA0046, EA0059, EA0106, EA0133, EA0150, EA0152, EA0158 |
| 5 | `["Diagnosis", "absence seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | absence seizures | EA0006, EA0033, EA0124, EA0161, EA0184 |
| 5 | `["Diagnosis", "absences", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | absences | EA0047, EA0050, EA0082, EA0096, EA0125 |
| 5 | `["Diagnosis", "focal epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal epilepsy | EA0002, EA0061, EA0114, EA0171, EA0188 |
| 3 | `["Diagnosis", "focal seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal seizures | EA0018, EA0143, EA0153 |
| 3 | `["Diagnosis", "secondary generalised tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | secondary generalised tonic clonic seizures | EA0040, EA0104, EA0150 |
| 2 | `["Diagnosis", "absences", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | absences | EA0168, EA0180 |
| 2 | `["Diagnosis", "altered awareness", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal seizures with altered awareness | EA0143, EA0153 |
| 2 | `["Diagnosis", "dissociative seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | dissociative seizures | EA0057, EA0082 |
| 2 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0062, EA0164 |
| 2 | `["Diagnosis", "focal dyscognitive seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal dyscognitive seizures | EA0169, EA0181 |
| 2 | `["Diagnosis", "focal seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal seizures | EA0109, EA0158 |
| 2 | `["Diagnosis", "myoclonus", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | myoclonus | EA0168, EA0180 |
| 2 | `["Diagnosis", "seizure", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | seizure | EA0071 |

## SeizureFrequency

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 16 | `[["cui", "C0036572"], "unknown"]` | seizure | EA0008, EA0050, EA0059, EA0106, EA0108, EA0111, EA0119, EA0121, ... |
| 14 | `[["cui", "C0036572"], "seizure-free"]` | seizures | EA0044, EA0063, EA0068, EA0075, EA0137, EA0143, EA0162, EA0168, ... |
| 9 | `[["cui", "C0036572"], "active-rate"]` | seizures | EA0085, EA0108, EA0113, EA0117, EA0119, EA0151, EA0154, EA0169, ... |
| 5 | `[["cui", "C0494475"], "active-rate"]` | generalised-tonic-clonic-seizures | EA0006, EA0038, EA0049, EA0079, EA0096 |
| 4 | `[["cui", "C0494475"], "unknown"]` | generalised-tonic-clonic-seizures | EA0049, EA0087, EA0123, EA0161 |
| 3 | `[["cui", "C0563606"], "unknown"]` | absence | EA0049, EA0050, EA0082 |
| 3 | `[["cui", "C0877017"], "seizure-free"]` | focal-to-bilateral-convulsive-seizure | EA0011, EA0061, EA0121 |
| 3 | `[["cui", "C1299590"], "seizure-free"]` | seizure-free | EA0127, EA0180, EA0190 |
| 2 | `[["cui", "C0027066"], "active-rate"]` | myoclonic-jerks | EA0049, EA0050 |
| 2 | `[["cui", "C0270834"], "active-rate"]` | focal-seizures-with-altered-awareness | EA0054, EA0158 |
| 2 | `[["cui", "C0270834"], "unknown"]` | dyscognitive-seizures | EA0169, EA0181 |
| 2 | `[["cui", "C0563606"], "active-rate"]` | absences | EA0047, EA0124 |
| 2 | `[["cui", "C0877017"], "active-rate"]` | focal-to-bilateral-convulsive-seizures | EA0054 |
| 1 | `[["cui", "C0016399"], "seizure-free"]` | focal | EA0186 |
| 1 | `[["cui", "C0027066"], "unknown"]` | myoclonic-jerks | EA0049 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 8 | `[["cui", "C0036572"], "active-rate"]` | seizure | EA0027, EA0043, EA0129, EA0142, EA0148, EA0172, EA0182, EA0198 |
| 7 | `[["cui", "C0494475"], "active-rate"]` | Generalised tonic clonic seizure | EA0005, EA0021, EA0043, EA0146, EA0162, EA0183, EA0200 |
| 6 | `[["cui", "C0036572"], "unknown"]` | seizures | EA0040, EA0096, EA0104, EA0117, EA0135, EA0148 |
| 5 | `[["cui", "C1299590"], "seizure-free"]` | seizure free | EA0038, EA0087, EA0104, EA0143 |
| 3 | `[["cui", "C0036572"], "seizure-free"]` | seizure | EA0071, EA0123, EA0171 |
| 3 | `[["cui", "C0877017"], "active-rate"]` | focal to bilateral convulsive seizures | EA0045, EA0121, EA0132 |
| 2 | `[["cui", "C0270834"], "unknown"]` | focal seizures with altered awareness | EA0121, EA0158 |
| 2 | `[["cui", "C0494475"], "unknown"]` | generalised tonic clonic seizures | EA0096, EA0131 |
| 2 | `[["cui", "C0751495"], "active-rate"]` | focal seizures | EA0018, EA0109 |
| 2 | `[["phrase", "episodes"], "active-rate"]` | episodes | EA0149, EA0153 |
| 2 | `[["phrase", "focal dyscognitive seizures"], "active-rate"]` | focal dyscognitive seizures | EA0169, EA0181 |
| 1 | `[["cui", "C0016399"], "active-rate"]` | focal motor seizures | EA0057 |
| 1 | `[["cui", "C0016399"], "unknown"]` | focal motor seizures | EA0186 |
| 1 | `[["cui", "C0027066"], "unknown"]` | myoclonic jerks | EA0087 |
| 1 | `[["cui", "C0149958"], "active-rate"]` | complex partial seizures | EA0092 |

## Investigations

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 7 | `["EEG", "Yes", "Abnormal", null]` | EEG | EA0044, EA0111, EA0117, EA0132, EA0182, EA0200 |
| 6 | `["MRI", "Yes", "Abnormal", null]` | MRI | EA0046, EA0061, EA0104, EA0106, EA0142 |
| 3 | `["MRI", "Yes", "Normal", null]` | MRI-brain | EA0164, EA0188, EA0197 |
| 2 | `["CT", "Yes", "Normal", null]` | CT | EA0073, EA0164 |
| 2 | `["EEG", "Yes", "Normal", null]` | EEG | EA0076, EA0102 |
| 1 | `["CT", "Yes", "Abnormal", null]` | CT-scan | EA0016 |
| 1 | `["CT", "Yes", "Unknown", null]` | CT | EA0062 |
| 1 | `["EEG", "Yes", "Abnormal", "Standard"]` | EEG | EA0026 |
| 1 | `["EEG", "Yes", "Abnormal", "VideoTelemetry"]` | Video-EEG | EA0190 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 11 | `["MRI", "Yes", null, null]` | MR brain | EA0027, EA0039, EA0085, EA0107, EA0109, EA0113, EA0116, EA0139, ... |
| 9 | `["EEG", "Yes", null, null]` | EEG | EA0027, EA0043, EA0045, EA0085, EA0107, EA0113, EA0116, EA0157, ... |
| 5 | `["EEG", "Yes", "Abnormal", null]` | EEG | EA0015, EA0026, EA0102, EA0120, EA0190 |
| 2 | `["EEG", "No", null, null]` | EEG | EA0110, EA0153 |
| 2 | `["MRI", "No", null, null]` | MRI scan | EA0014, EA0153 |
| 2 | `["MRI", null, null, null]` | MRI | EA0110, EA0125 |
| 1 | `["CT", "Yes", null, null]` | CT | EA0062 |
| 1 | `["CT", null, null, null]` | CT brain scan | EA0108 |
| 1 | `["EEG", "Yes", "Normal", null]` | EEG | EA0182 |
| 1 | `["EEG", null, null, null]` | EEG | EA0125 |
| 1 | `["MRI", "Yes", "Abnormal", null]` | MRI scan | EA0197 |
| 1 | `["MRI", "Yes", "Normal", null]` | MRI | EA0106 |
