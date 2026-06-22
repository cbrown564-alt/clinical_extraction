# ExECTv2 Clinical-Recovery Error Ledger

- Generated: `2026-06-22`
- JSON: `experiments\exectv2_v0917_qwencompact_residualrepair_dev140_error_ledger_20260622.json`
- Split: `dev`
- Letters: 140
- Structured JSONL: `experiments\exectv2_holistic_finding_assembly_v0917_qwencompact_residualrepair_dev140_20260622.jsonl`
- Diagnosis JSONL: `None`
- SeizureFrequency JSONL: `None`
- Investigations JSONL: `None`

## Headline Scores

| Entity | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.804 | 0.688 | 0.969 | 187 | 85 | 6 |
| Diagnosis | 0.696 | 0.713 | 0.681 | 211 | 85 | 99 |
| SeizureFrequency | 0.878 | 0.838 | 0.923 | 155 | 30 | 13 |
| Investigations | 0.919 | 0.960 | 0.882 | 120 | 5 | 16 |

## Prescription

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 2 | `["ordinary", "lamotrigine", "150", "mg", "2"]` | Lamotrigine- | EA0104, EA0182 |
| 2 | `["ordinary", "sodium-valproate", "200", "mg", "2"]` | Sodium-Valproate-200-mg-twice-a-day-(to-be-increased-to-300-mg-BD-in-steps-of-100-mg-every-two-weeks) | EA0047, EA0102 |
| 1 | `["ordinary", "clobazam", "10", "mg", "1"]` | Current-medication:-Clobazam-10mg-on | EA0047 |
| 1 | `["ordinary", "perampanel", "50", "mg", "2"]` | Brivetiracetam- | EA0146 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 10 | `["ordinary", "lamotrigine", "75", "mg", "2"]` | lamotrigine | EA0008, EA0018, EA0045, EA0062, EA0092, EA0119, EA0120, EA0141, ... |
| 6 | `["ordinary", "lamotrigine", "25", "mg", "1"]` | lamotrigine | EA0045, EA0054, EA0062, EA0141, EA0157, EA0199 |
| 4 | `["ordinary", "levetiracetam", "500", "mg", "2"]` | Levetiracetam | EA0092, EA0110, EA0116, EA0161 |
| 2 | `["ordinary", "carbamazepine", "400", "mg", "2"]` | Carbamazepine | EA0109, EA0114 |
| 2 | `["ordinary", "carbamazepine", "600", "mg", "2"]` | carbamazepine | EA0078, EA0079 |
| 2 | `["ordinary", "lamotrigine", "175", "mg", "2"]` | lamotrigine | EA0054, EA0106 |
| 2 | `["ordinary", "levetiracetam", "250", "mg", "1"]` | Levetiracetam | EA0110, EA0197 |
| 2 | `["ordinary", "levetiracetam", "750", "mg", "2"]` | levetiracetam | EA0008, EA0087 |
| 2 | `["ordinary", "sodium-valproate", "800", "mg", "2"]` | Sodium Valproate | EA0021, EA0183 |
| 2 | `["ordinary", "zonisamide", "25", "mg", "1"]` | zonisamide | EA0169, EA0181 |
| 2 | `["ordinary", "zonisamide", "75", "mg", "2"]` | zonisamide | EA0169, EA0181 |
| 1 | `["ordinary", "brivaracetam", "100", "mg", "2"]` | Brivaracetam | EA0111 |
| 1 | `["ordinary", "brivaracetam", "50", "mg", "2"]` | Brivetiracetam 50mg bd | EA0146 |
| 1 | `["ordinary", "carbamazepine", "100", "mg", "2"]` | Carbamazepine | EA0109 |
| 1 | `["ordinary", "carbamazepine", "300", "mg", "3"]` | carbamazepine | EA0184 |

## Diagnosis

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 35 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0007, EA0010, EA0011, EA0033, EA0035, EA0039, EA0049, EA0056, ... |
| 23 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised-tonic-clonic-seizure | EA0005, EA0006, EA0021, EA0025, EA0038, EA0049, EA0079, EA0082, ... |
| 7 | `["Diagnosis", "focal epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | symptomatic-structural-focal-epilepsy | EA0010, EA0046, EA0056, EA0059, EA0061, EA0114, EA0153 |
| 6 | `["Diagnosis", "focal seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0002, EA0133, EA0185 |
| 4 | `["Diagnosis", "focal seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0018, EA0022, EA0110, EA0171 |
| 4 | `["Diagnosis", "generalised seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised-seizures | EA0047, EA0075, EA0136, EA0158 |
| 3 | `["Diagnosis", "epileptic seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epileptic-seizures | EA0043, EA0135, EA0141 |
| 3 | `["Diagnosis", "focal epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal-onset-epilepsy | EA0045, EA0141, EA0171 |
| 3 | `["Diagnosis", "juvenile myoclonic epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | juvenile-myoclonic-epilepsy | EA0085, EA0113, EA0168 |
| 3 | `["Diagnosis", "temporal lobe epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | temporal-lobe-epilepsy | EA0149, EA0153, EA0185 |
| 3 | `["Diagnosis", "temporal lobe epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | temporal-lobe-epilepsy | EA0002, EA0149, EA0185 |
| 2 | `["Diagnosis", "epilepsy with generalised tonic clonic seizures alone", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epilepsy-with-generalised-tonic-clonic-seizure-alone | EA0005, EA0043 |
| 2 | `["Diagnosis", "epilepsy with generalised tonic clonic seizures alone", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy-with-generalised-tonic-clonic-seizures-alone | EA0005, EA0035 |
| 2 | `["Diagnosis", "epileptic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epileptic-seizures | EA0057 |
| 2 | `["Diagnosis", "focal impaired awareness seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-impaired-awareness-seizures | EA0114, EA0117 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 35 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0002, EA0005, EA0008, EA0019, EA0021, EA0034, EA0040, EA0044, ... |
| 10 | `["Diagnosis", "focal seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal seizures | EA0008, EA0011, EA0016, EA0054, EA0061, EA0110, EA0116, EA0143, ... |
| 9 | `["Diagnosis", "epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epilepsy | EA0004, EA0047, EA0059, EA0132, EA0153, EA0157, EA0180, EA0188 |
| 8 | `["Diagnosis", "focal epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | Focal epilepsy | EA0045, EA0054, EA0072, EA0106, EA0135, EA0152, EA0154 |
| 8 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised tonic clonic seizures | EA0020, EA0108, EA0116, EA0127, EA0162, EA0178, EA0183, EA0195 |
| 6 | `["Diagnosis", "focal seizures with altered awareness", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal seizures with altered awareness | EA0114, EA0117, EA0143, EA0153, EA0169, EA0181 |
| 5 | `["Diagnosis", "focal epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | Symptomatic structural focal epilepsy (probable perinatal insult) | EA0010, EA0059, EA0061, EA0110, EA0188 |
| 3 | `["Diagnosis", "generalised seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised seizures | EA0040, EA0067, EA0137 |
| 3 | `["Diagnosis", "temporal lobe epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | temporal lobe epilepsy | EA0149, EA0185, EA0190 |
| 2 | `["Diagnosis", "complex partial seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | complex partial seizures | EA0179, EA0183 |
| 2 | `["Diagnosis", "focal epilepsy", [["Certainty", "3"], ["Negation", "Affirmed"]]]` | focal epilepsy | EA0114, EA0153 |
| 2 | `["Diagnosis", "generalised epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | Generalised Epilepsy | EA0044, EA0200 |
| 2 | `["Diagnosis", "juvenile myoclonic epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | possible JME | EA0025, EA0026 |
| 2 | `["Diagnosis", "secondary generalised seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | secondary generalised seizures | EA0143, EA0188 |
| 1 | `["Diagnosis", "absence events", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | absence events | EA0124 |

## SeizureFrequency

### Residual By State

| Side | active-rate | seizure-free | unknown |
| --- | ---: | ---: | ---: |
| gold | 2 | 9 | 12 |
| predicted | 33 | 4 | 10 |

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 7 | `[["cui", "C0036572"], "unknown"]` | seizures | EA0022, EA0050, EA0059, EA0108, EA0119, EA0136, EA0178 |
| 5 | `[["cui", "C0036572"], "seizure-free"]` | seizures | EA0044, EA0063, EA0168, EA0191 |
| 2 | `[["cui", "C0494475"], "unknown"]` | generalised-tonic-clonic-seizures | EA0049, EA0161 |
| 1 | `[["cui", "C0027066"], "unknown"]` | myoclonic-jerks | EA0128 |
| 1 | `[["cui", "C0036572"], "active-rate"]` | seizure | EA0119 |
| 1 | `[["cui", "C0234533"], "seizure-free"]` | generalised-convulsions | EA0136 |
| 1 | `[["cui", "C0270834"], "active-rate"]` | focal-seizures-with-altered-awareness | EA0054 |
| 1 | `[["cui", "C0270834"], "seizure-free"]` | focal-seizures-with-altered-awareness | EA0143 |
| 1 | `[["cui", "C0563606"], "unknown"]` | absences | EA0082 |
| 1 | `[["cui", "C0751495"], "unknown"]` | focal-seizures | EA0068 |
| 1 | `[["cui", "C0877017"], "seizure-free"]` | focal-to-bilateral-convulsive-seizure | EA0011 |
| 1 | `[["cui", "C1299590"], "seizure-free"]` | seizure | EA0180 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 10 | `[["cui", "C0036572"], "active-rate"]` | seizures | EA0026, EA0085, EA0109, EA0113, EA0142, EA0148, EA0178, EA0182, ... |
| 4 | `[["cui", "C0494475"], "active-rate"]` | generalised tonic clonic seizures | EA0020, EA0146, EA0161 |
| 3 | `[["cui", "C0270834"], "active-rate"]` | focal impaired awareness seizures | EA0114, EA0132 |
| 3 | `[["cui", "C0563606"], "unknown"]` | absences | EA0006, EA0161, EA0184 |
| 3 | `[["cui", "C0877017"], "active-rate"]` | focal to bilateral convulsive seizure | EA0034, EA0045, EA0057 |
| 2 | `[["cui", "C0016399"], "active-rate"]` | focal motor seizure | EA0072, EA0106 |
| 2 | `[["cui", "C0036572"], "unknown"]` | seizures | EA0063, EA0154 |
| 2 | `[["cui", "C0270838"], "active-rate"]` | Secondary generalised seizures | EA0067, EA0137 |
| 2 | `[["cui", "C0751495"], "unknown"]` | focal seizures | EA0008, EA0158 |
| 1 | `[["cui", "C0027066"], "unknown"]` | myoclonic jerks | EA0050 |
| 1 | `[["cui", "C0036572"], "seizure-free"]` | seizure | EA0123 |
| 1 | `[["cui", "C0494475"], "unknown"]` | generalised tonic clonic seizures | EA0087 |
| 1 | `[["cui", "C0563606"], "active-rate"]` | absences | EA0082 |
| 1 | `[["cui", "C0751495"], "active-rate"]` | focal seizures | EA0054 |
| 1 | `[["cui", "C1299590"], "seizure-free"]` | seizure-free | EA0006 |

## Investigations

### Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 6 | `["EEG", "Yes", "Abnormal"]` | EEG | EA0044, EA0132, EA0137, EA0150, EA0200 |
| 4 | `["MRI", "Yes", "Abnormal"]` | MRI | EA0046, EA0061, EA0142 |
| 2 | `["EEG", "Yes", "Normal"]` | EEG | EA0082, EA0146 |
| 1 | `["CT", "Yes", "Abnormal"]` | CT-scan | EA0016 |
| 1 | `["CT", "Yes", "Normal"]` | CT | EA0073 |
| 1 | `["CT", "Yes", "Unknown"]` | CT | EA0062 |
| 1 | `["MRI", "Yes", "Normal"]` | MRI | EA0188 |

### Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 2 | `["CT", "Yes", "Normal"]` | CT | EA0062, EA0164 |
| 2 | `["MRI", "Yes", "Normal"]` | CT head | EA0164, EA0179 |
| 1 | `["EEG", null, null]` | MRI brain | EA0075 |
