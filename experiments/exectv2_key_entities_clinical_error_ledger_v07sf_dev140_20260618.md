# ExECTv2 Clinical-Recovery Error Ledger

- Generated: `2026-06-18`
- JSON: `experiments\exectv2_key_entities_clinical_error_ledger_v07sf_dev140_20260618.json`
- Split: `dev`
- Letters: 140
- Structured JSONL: `experiments\exectv2_llm_med_inv_verifier_v01_dev140_gpt41mini_20260618.jsonl`
- Diagnosis JSONL: `experiments\exectv2_hybrid_diagnosis_reconciler_v01_dev140_gpt41mini_20260618.jsonl`
- SeizureFrequency JSONL: `experiments\exectv2_hybrid_sf_unknown_suppression_v07_dev140_20260618.jsonl`
- Investigations JSONL: `experiments\exectv2_llm_investigations_verifier_v01_dev140_gpt41mini_20260618.jsonl`

## Headline Scores

| Entity | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.817 | 0.773 | 0.865 | 167 | 49 | 26 |
| Diagnosis | 0.658 | 0.658 | 0.658 | 243 | 126 | 126 |
| SeizureFrequency | 0.782 | 0.759 | 0.807 | 151 | 48 | 36 |
| Investigations | 0.872 | 0.869 | 0.875 | 119 | 18 | 17 |

## Prescription

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 3 | `["ordinary", "lamotrigine", "100", "mg", "2"]` | lamotrigine- | EA0009, EA0127, EA0142 |
| 2 | `["ordinary", "clobazam", "10", "mg", "1"]` | Current-medication:-Clobazam-10mg-on | EA0047 |
| 2 | `["ordinary", "lamotrigine", "150", "mg", "2"]` | Lamotrigine- | EA0104, EA0182 |
| 2 | `["ordinary", "perampanel", "8", "mg", "1"]` | Perampanel- | EA0117, EA0158 |
| 2 | `["ordinary", "sodium-valproate", "200", "mg", "2"]` | Sodium-Valproate-200-mg-twice-a-day-(to-be-increased-to-300-mg-BD-in-steps-of-100-mg-every-two-weeks) | EA0047, EA0102 |
| 1 | `["ordinary", "carbamazepine", "100", "mg", "1"]` | Medication:-Carbamazepine-100mg-am | EA0088 |
| 1 | `["ordinary", "carbamazepine", "200", "mg", "1"]` | Carbamazepine | EA0088 |
| 1 | `["ordinary", "carbamazepine", "300", "mg", "2"]` | Carbamazepine-300mg-bd | EA0108 |
| 1 | `["ordinary", "carbamazepine", "400", "mg", "1"]` | Carbamazepine | EA0038 |
| 1 | `["ordinary", "lamotrigine", "200", "mg", "2"]` | lamotrigine- | EA0150 |
| 1 | `["ordinary", "lamotrigine", "50", "mg", "1"]` | Lamotrigine-50mg-am | EA0087 |
| 1 | `["ordinary", "lamotrigine", "50", "mg", "2"]` | Lamotrigine-50-mg-twice-a-day | EA0040 |
| 1 | `["ordinary", "lamotrigine", "75", "mg", "1"]` | Lamotrigine | EA0087 |
| 1 | `["ordinary", "levetiracetam", "1", "g", "1"]` | Levetiracetam | EA0107 |
| 1 | `["ordinary", "perampanel", "50", "mg", "2"]` | Brivetiracetam- | EA0146 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 4 | `["ordinary", "sodium-valproate", "300", "mg", "1"]` | Sodium Valproate (Epilim Chrono) 300mgs once a day | EA0085, EA0113, EA0148 |
| 3 | `["ordinary", "lamotrigine", "75", "mg", "2"]` | lamotrigine 75mg bd | EA0008, EA0119, EA0120 |
| 2 | `["ordinary", "clopidogrel", "75", "mg", "1"]` | clopidogrel 75mg OD | EA0073, EA0133 |
| 2 | `["ordinary", "lamotrigine", "25", "mg", "1"]` | lamotrigine 25 mg once-a-day | EA0043, EA0141 |
| 2 | `["rescue", "midazolam", "as_required"]` | Buccal Midazolam | EA0068, EA0087 |
| 1 | `["ordinary", "brivaracetam", "100", "mg", "2"]` | Brivaracetam 100mgs bd | EA0111 |
| 1 | `["ordinary", "brivaracetam", "50", "mg", "2"]` | Brivetiracetam 50mg bd | EA0146 |
| 1 | `["ordinary", "carbamazepine", "100", "mg", "2"]` | Carbamazepine 100mg bd | EA0109 |
| 1 | `["ordinary", "carbamazepine", "100mg", "mg", "1"]` | Carbamazepine 100mg am, 200mg pm | EA0088 |
| 1 | `["ordinary", "carbamazepine", "200mg", "mg", "1"]` | Carbamazepine 200mg pm | EA0088 |
| 1 | `["ordinary", "carbamazepine", "400", "mg", "2"]` | Carbamazepine is increased to 400mg bd | EA0108 |
| 1 | `["ordinary", "carbamazepine", "600", "mg", "2"]` | carbamazepine 600mg twice a day | EA0078 |
| 1 | `["ordinary", "carbamazepine-controlled-release", "400", "mg", "2"]` | Carbamazepine Controlled Release 400mgs bd | EA0114 |
| 1 | `["ordinary", "citalopram", "20", "mg", "1"]` | Citalopram 20mg od | EA0135 |
| 1 | `["ordinary", "clobazam", "10-20", "mg", "2"]` | Clobazam 10-20mg bd for seizure clusters | EA0152 |

## Diagnosis

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 17 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0006, EA0035, EA0039, EA0057, EA0128, EA0133, EA0137, EA0141, ... |
| 7 | `["Diagnosis", "focal epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-epilepsy | EA0002, EA0061, EA0114, EA0121, EA0142, EA0153, EA0178 |
| 6 | `["Diagnosis", "secondary generalised seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | secondary-generalised-seizures | EA0040, EA0137, EA0150, EA0152, EA0157 |
| 5 | `["Diagnosis", "epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epilepsy-with-generalised-tonic-clonic-seizure-alone | EA0005, EA0043, EA0062, EA0132, EA0164 |
| 5 | `["Diagnosis", "focal seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0002, EA0109, EA0126, EA0133, EA0158 |
| 5 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised-tonic-clonic-seizures | EA0005, EA0049, EA0128, EA0168, EA0180 |
| 4 | `["Diagnosis", "altered awareness", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizures-with-altered-awareness | EA0008, EA0054, EA0158, EA0167 |
| 4 | `["Diagnosis", "focal seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0018, EA0110, EA0153, EA0171 |
| 4 | `["Diagnosis", "generalised", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised | EA0123, EA0128, EA0183, EA0195 |
| 4 | `["Diagnosis", "symptomatic epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | symptomatic-epilepsy | EA0079, EA0108, EA0169, EA0181 |
| 3 | `["Diagnosis", "generalised tonic clonic seizure", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised-tonic-clonic-seizure | EA0087, EA0157, EA0161 |
| 3 | `["Diagnosis", "juvenile myoclonic epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | juvenile-myoclonic-epilepsy | EA0085, EA0113, EA0128 |
| 3 | `["Diagnosis", "juvenile myoclonic epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | juvenile-myoclonic-epilepsy | EA0033, EA0049, EA0125 |
| 3 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | tonic-clonic-seizures | EA0111, EA0116, EA0200 |
| 2 | `["Diagnosis", "dyscognitive seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | dyscognitive-seizures | EA0169, EA0181 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 52 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0002, EA0005, EA0010, EA0019, EA0021, EA0022, EA0034, EA0038, ... |
| 26 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | tonic clonic seizures | EA0020, EA0043, EA0087, EA0104, EA0108, EA0111, EA0116, EA0123, ... |
| 8 | `["Diagnosis", "absence seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | absence seizures | EA0020, EA0050, EA0082, EA0096, EA0124, EA0161, EA0184 |
| 7 | `["Diagnosis", "symptomatic structural focal epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | symptomatic structural focal epilepsy | EA0056, EA0072, EA0079, EA0108, EA0169, EA0181, EA0195 |
| 5 | `["Diagnosis", "focal epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal epilepsy | EA0002, EA0061, EA0114, EA0171, EA0188 |
| 5 | `["Diagnosis", "secondary generalised tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | secondary generalised tonic clonic seizures | EA0104, EA0137, EA0150, EA0157, EA0188 |
| 4 | `["Diagnosis", "focal seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal seizures | EA0018, EA0057, EA0143, EA0153 |
| 3 | `["Diagnosis", "absences", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | absences | EA0033, EA0047, EA0125 |
| 3 | `["Diagnosis", "single seizure", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | single seizure | EA0071, EA0100 |
| 2 | `["Diagnosis", "altered awareness", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal seizures with altered awareness | EA0143, EA0153 |
| 2 | `["Diagnosis", "epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epilepsy | EA0035, EA0168 |
| 2 | `["Diagnosis", "focal dyscognitive seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal dyscognitive seizures | EA0169, EA0181 |
| 2 | `["Diagnosis", "focal seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal seizures | EA0109, EA0158 |
| 2 | `["Diagnosis", "focal to bilateral convulsive seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal to bilateral convulsive seizures | EA0126, EA0186 |
| 2 | `["Diagnosis", "myoclonus", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | myoclonus | EA0168, EA0180 |

## SeizureFrequency

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 5 | `[["cui", "C0036572"], "active-rate"]` | seizure | EA0108, EA0117, EA0119, EA0169, EA0181 |
| 5 | `[["cui", "C0036572"], "seizure-free"]` | seizures | EA0063, EA0137, EA0143, EA0168, EA0191 |
| 3 | `[["cui", "C0494475"], "active-rate"]` | generalised-tonic-clonic-seizures | EA0006, EA0038, EA0096 |
| 3 | `[["cui", "C1299590"], "seizure-free"]` | seizure-free | EA0127, EA0180, EA0190 |
| 2 | `[["cui", "C0027066"], "active-rate"]` | myoclonic-jerks | EA0049, EA0050 |
| 2 | `[["cui", "C0027066"], "unknown"]` | myoclonic-jerks | EA0049, EA0128 |
| 2 | `[["cui", "C0036572"], "unknown"]` | seizures | EA0111, EA0198 |
| 2 | `[["cui", "C0270834"], "active-rate"]` | focal-seizures-with-altered-awareness | EA0054, EA0158 |
| 2 | `[["cui", "C0563606"], "unknown"]` | absence | EA0049, EA0050 |
| 2 | `[["cui", "C0877017"], "active-rate"]` | focal-to-bilateral-convulsive-seizures | EA0054 |
| 2 | `[["cui", "C0877017"], "seizure-free"]` | focal-to-bilateral-convulsive-seizure | EA0011, EA0121 |
| 1 | `[["cui", "C0016399"], "seizure-free"]` | focal | EA0186 |
| 1 | `[["cui", "C0270838"], "active-rate"]` | secondary-generalised-seizures | EA0056 |
| 1 | `[["cui", "C0494475"], "unknown"]` | generalised | EA0087 |
| 1 | `[["cui", "C0563606"], "active-rate"]` | absences | EA0047 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 9 | `[["cui", "C0036572"], "seizure-free"]` | seizure | EA0071, EA0092, EA0113, EA0127, EA0160, EA0171, EA0176, EA0180, ... |
| 5 | `[["cui", "C0036572"], "active-rate"]` | seizures | EA0085, EA0148, EA0153, EA0172, EA0198 |
| 5 | `[["cui", "C0036572"], "unknown"]` | seizures | EA0096, EA0117, EA0135, EA0166, EA0197 |
| 5 | `[["cui", "C1299590"], "seizure-free"]` | seizure free | EA0006, EA0038, EA0087, EA0143 |
| 3 | `[["cui", "C0270834"], "active-rate"]` | focal impaired awareness seizures | EA0114, EA0169, EA0181 |
| 3 | `[["cui", "C0494475"], "active-rate"]` | grand mal | EA0146, EA0162, EA0200 |
| 2 | `[["cui", "C0270834"], "unknown"]` | focal seizures with altered awareness | EA0121, EA0158 |
| 2 | `[["cui", "C0494475"], "unknown"]` | generalised tonic clonic seizures | EA0096, EA0131 |
| 1 | `[["cui", "C0016399"], "active-rate"]` | focal motor seizures | EA0057 |
| 1 | `[["cui", "C0016399"], "unknown"]` | focal motor seizures | EA0158 |
| 1 | `[["cui", "C0027066"], "unknown"]` | myoclonic jerks | EA0087 |
| 1 | `[["cui", "C0149958"], "active-rate"]` | complex partial seizures | EA0092 |
| 1 | `[["cui", "C0270838"], "active-rate"]` | secondarily generalised seizures | EA0143 |
| 1 | `[["cui", "C0494475"], "seizure-free"]` | Generalised tonic clonic seizure | EA0005 |
| 1 | `[["cui", "C0563606"], "unknown"]` | absences | EA0184 |

## Investigations

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 7 | `["EEG", "Yes", "Abnormal", null]` | EEG | EA0044, EA0111, EA0117, EA0132, EA0182, EA0200 |
| 4 | `["MRI", "Yes", "Abnormal", null]` | MRI | EA0046, EA0061, EA0104, EA0106 |
| 3 | `["EEG", "Yes", "Normal", null]` | EEG-she-had-some-of-these-episodes-and-there-was-no-epileptiform-EEG | EA0022, EA0102, EA0146 |
| 2 | `["MRI", "Yes", "Normal", null]` | MRI | EA0188, EA0197 |
| 1 | `["EEG", "Yes", "Abnormal", "Standard"]` | EEG | EA0026 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 4 | `["MRI", "No", null, null]` | MRI scan of the brain | EA0123, EA0149, EA0182, EA0185 |
| 3 | `["EEG", "Yes", "Abnormal", null]` | EEG recording | EA0015, EA0026, EA0102 |
| 2 | `["EEG", "Yes", "Normal", null]` | EEG | EA0120, EA0182 |
| 2 | `["EEG", "Yes", "Unknown", null]` | EEG | EA0054, EA0117 |
| 1 | `["CT", "No", "Unknown", null]` | CT brain scan | EA0108 |
| 1 | `["EEG", "No", null, null]` | EEG | EA0154 |
| 1 | `["EEG", "Yes", "Normal", "VideoTelemetry"]` | video EEG | EA0022 |
| 1 | `["MRI", "No", "Unknown", null]` | MRI scan of his brain | EA0024 |
| 1 | `["MRI", "Yes", "Abnormal", null]` | MRI scan | EA0197 |
| 1 | `["MRI", "Yes", "Normal", null]` | MRI 3/4/2018 | EA0106 |
| 1 | `["MRI", "Yes", "Unknown", null]` | follow up scan | EA0143 |
