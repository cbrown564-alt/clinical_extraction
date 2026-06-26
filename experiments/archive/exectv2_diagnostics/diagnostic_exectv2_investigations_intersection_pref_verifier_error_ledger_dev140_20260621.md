# ExECTv2 Clinical-Recovery Error Ledger

- Generated: `2026-06-21`
- JSON: `experiments\diagnostic_exectv2_investigations_intersection_pref_verifier_error_ledger_dev140_20260621.json`
- Split: `dev`
- Letters: 140
- Structured JSONL: `experiments\exectv2_target_indicators_single_call_v042_live_default_quarantine_dev140_qwen36_35b_ollama_autogpu_ctx16384_20260620.jsonl`
- Diagnosis JSONL: `None`
- SeizureFrequency JSONL: `None`
- Investigations JSONL: `experiments\diagnostic_exectv2_investigations_intersection_pref_verifier_dev140_20260621.jsonl`

## Headline Scores

| Entity | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.821 | 0.809 | 0.834 | 161 | 38 | 32 |
| Diagnosis | 0.595 | 0.659 | 0.542 | 168 | 87 | 142 |
| SeizureFrequency | 0.557 | 0.549 | 0.566 | 95 | 78 | 73 |
| Investigations | 0.800 | 0.979 | 0.676 | 92 | 2 | 44 |

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
| 65 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0007, EA0010, EA0011, EA0033, EA0035, EA0039, EA0043, EA0045, ... |
| 22 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised-tonic-clonic-seizure | EA0005, EA0006, EA0019, EA0021, EA0025, EA0049, EA0079, EA0082, ... |
| 20 | `["Diagnosis", "focal epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-epilepsy | EA0002, EA0010, EA0046, EA0054, EA0057, EA0059, EA0061, EA0106, ... |
| 8 | `["Diagnosis", "focal seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0002, EA0034, EA0109, EA0126, EA0133, EA0185 |
| 6 | `["Diagnosis", "focal to bilateral convulsive seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-to-bilateral-convulsive-seizures | EA0010, EA0011, EA0034, EA0057, EA0061, EA0133 |
| 5 | `["Diagnosis", "secondary generalised seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | secondary-generalised-seizures | EA0040, EA0072, EA0137, EA0152, EA0198 |
| 4 | `["Diagnosis", "epileptic seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epileptic-seizures | EA0043, EA0135, EA0141, EA0164 |
| 4 | `["Diagnosis", "focal seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0022, EA0110, EA0132, EA0171 |
| 4 | `["Diagnosis", "generalised", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised | EA0123, EA0128, EA0183, EA0195 |
| 4 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | generalised-tonic-clonic-seizures | EA0110, EA0111, EA0116, EA0200 |
| 3 | `["Diagnosis", "complex partial seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | complex-partial-seizures | EA0092, EA0152, EA0198 |
| 3 | `["Diagnosis", "focal motor seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-motor-seizures | EA0057, EA0072, EA0108 |
| 3 | `["Diagnosis", "juvenile myoclonic epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | juvenile-myoclonic-epilepsy | EA0085, EA0113, EA0128 |
| 3 | `["Diagnosis", "juvenile myoclonic epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | juvenile-myoclonic-epilepsy | EA0033, EA0049, EA0125 |
| 3 | `["Diagnosis", "temporal lobe epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | temporal-lobe-epilepsy | EA0149, EA0153, EA0185 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 8 | `["Diagnosis", "absences", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised tonic clonic seizures, absences and myoclonic jerks | EA0033, EA0047, EA0049, EA0082, EA0125, EA0161, EA0180, EA0184 |
| 5 | `["Diagnosis", "symptomatic structural epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | symptomatic structural epilepsy | EA0046, EA0106, EA0133, EA0150, EA0152 |
| 5 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | tonic clonic seizures | EA0116, EA0127, EA0162, EA0183, EA0200 |
| 4 | `["Diagnosis", "generalised epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised epilepsy | EA0108, EA0123, EA0178, EA0195 |
| 3 | `["Diagnosis", "complex partial seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | complex partial seizures with secondary generalised tonic clonic seizures | EA0021, EA0157, EA0183 |
| 3 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0015, EA0071, EA0139 |
| 2 | `["Diagnosis", "focal dyscognitive seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal dyscognitive seizures | EA0169, EA0181 |
| 2 | `["Diagnosis", "focal epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal epilepsy | EA0010, EA0109 |
| 2 | `["Diagnosis", "focal seizures with altered awareness", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal seizures with altered awareness | EA0143, EA0153 |
| 2 | `["Diagnosis", "focal seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal seizures | EA0109, EA0185 |
| 2 | `["Diagnosis", "focal seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal seizures | EA0022, EA0119 |
| 2 | `["Diagnosis", "myoclonic jerks", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised tonic clonic seizures, absences and myoclonic jerks | EA0033, EA0125 |
| 2 | `["Diagnosis", "non epileptic psychogenic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | non epileptic psychogenic seizures | EA0056, EA0102 |
| 2 | `["Diagnosis", "secondary generalised tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | complex partial seizures with secondary generalised tonic clonic seizures | EA0021, EA0183 |
| 2 | `["Diagnosis", "single seizure", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | single seizure | EA0100, EA0189 |

## SeizureFrequency

### Residual By State

| Side | active-rate | seizure-free | unknown |
| --- | ---: | ---: | ---: |
| gold | 26 | 39 | 23 |
| predicted | 48 | 24 | 13 |

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 15 | `[["cui", "C0036572"], "active-rate"]` | seizures | EA0004, EA0108, EA0110, EA0111, EA0113, EA0117, EA0119, EA0123, ... |
| 15 | `[["cui", "C0036572"], "seizure-free"]` | seizures | EA0010, EA0034, EA0044, EA0063, EA0068, EA0075, EA0137, EA0143, ... |
| 14 | `[["cui", "C0036572"], "unknown"]` | seizures | EA0050, EA0059, EA0106, EA0108, EA0111, EA0119, EA0123, EA0125, ... |
| 9 | `[["cui", "C1299590"], "seizure-free"]` | seizure-free | EA0084, EA0102, EA0127, EA0156, EA0176, EA0180, EA0190, EA0195 |
| 7 | `[["cui", "C0877017"], "seizure-free"]` | focal-to-bilateral-convulsive-seizure | EA0011, EA0057, EA0059, EA0061, EA0121, EA0133, EA0190 |
| 4 | `[["cui", "C0270834"], "seizure-free"]` | focal-seizures-with-altered-awareness | EA0059, EA0061, EA0143, EA0190 |
| 3 | `[["cui", "C0270834"], "active-rate"]` | focal-seizures-with-altered-awareness | EA0054, EA0158 |
| 3 | `[["cui", "C0494475"], "active-rate"]` | generalised-tonic-clonic-seizures | EA0006, EA0049, EA0184 |
| 3 | `[["cui", "C0563606"], "unknown"]` | absence | EA0049, EA0050, EA0082 |
| 2 | `[["cui", "C0016399"], "seizure-free"]` | focal-motor-seizures | EA0057, EA0186 |
| 2 | `[["cui", "C0270834"], "unknown"]` | dyscognitive-seizures | EA0169, EA0181 |
| 2 | `[["cui", "C0877017"], "active-rate"]` | focal-to-bilateral-convulsive-seizures | EA0054 |
| 1 | `[["cui", "C0016399"], "active-rate"]` | focal-motor-seizure | EA0072 |
| 1 | `[["cui", "C0027066"], "unknown"]` | myoclonic-jerks | EA0049 |
| 1 | `[["cui", "C0270838"], "seizure-free"]` | secondary-generalized-seizures | EA0056 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 9 | `[["cui", "C0036572"], "seizure-free"]` | seizures | EA0038, EA0040, EA0045, EA0046, EA0071, EA0074, EA0121, EA0156, ... |
| 7 | `[["cui", "C0270834"], "active-rate"]` | focal seizures with altered awareness | EA0059, EA0061, EA0114, EA0132, EA0169, EA0181, EA0190 |
| 7 | `[["cui", "C0494475"], "active-rate"]` | generalised tonic clonic seizures | EA0035, EA0110, EA0123, EA0131, EA0157, EA0162, EA0195 |
| 6 | `[["cui", "C0877017"], "active-rate"]` | focal to bilateral convulsive seizures | EA0057, EA0059, EA0061, EA0121, EA0190 |
| 5 | `[["cui", "C0036572"], "active-rate"]` | seizure | EA0085, EA0129, EA0142, EA0173, EA0175 |
| 4 | `[["cui", "C0751494"], "seizure-free"]` | convulsive seizure | EA0046, EA0054, EA0106, EA0126 |
| 3 | `[["cui", "C0036572"], "unknown"]` | seizures | EA0135, EA0172, EA0199 |
| 3 | `[["cui", "C0751495"], "active-rate"]` | focal seizures | EA0109, EA0119 |
| 3 | `[["phrase", "episodes"], "active-rate"]` | episodes | EA0018, EA0040, EA0149 |
| 2 | `[["cui", "C0270834"], "seizure-free"]` | focal seizures with altered awareness | EA0121, EA0188 |
| 2 | `[["cui", "C0270834"], "unknown"]` | focal seizures with altered awareness | EA0121, EA0158 |
| 2 | `[["cui", "C0270838"], "active-rate"]` | secondary generalised seizures | EA0104, EA0157 |
| 2 | `[["cui", "C0494475"], "unknown"]` | generalised tonic clonic seizures | EA0049, EA0111 |
| 1 | `[["cui", "C0016399"], "unknown"]` | focal motor seizures | EA0158 |
| 1 | `[["cui", "C0027066"], "unknown"]` | myoclonic jerks | EA0087 |

## Investigations

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 24 | `["EEG", "Yes", "Abnormal"]` | EEG- | EA0005, EA0026, EA0030, EA0033, EA0044, EA0046, EA0049, EA0050, ... |
| 7 | `["MRI", "Yes", "Normal"]` | MRI | EA0035, EA0044, EA0075, EA0164, EA0171, EA0188, EA0197 |
| 6 | `["MRI", "Yes", "Abnormal"]` | MRI | EA0046, EA0061, EA0104, EA0106, EA0143 |
| 5 | `["EEG", "Yes", "Normal"]` | EEG-she-had-some-of-these-episodes-and-there-was-no-epileptiform-EEG | EA0022, EA0102, EA0146, EA0182 |
| 1 | `["CT", "Yes", "Normal"]` | CT-head | EA0164 |
| 1 | `["EEG", "Yes", "Unknown"]` | EEG- | EA0179 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 1 | `["EEG", "Yes", "Abnormal"]` | EEG | EA0102 |
| 1 | `["EEG", "Yes", "Unknown"]` | Both have been captured on EEG in the past | EA0117 |
