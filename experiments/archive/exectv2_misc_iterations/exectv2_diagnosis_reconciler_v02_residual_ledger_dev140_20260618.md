# ExECTv2 Diagnosis Reconciler v0.2 Residual Ledger

- Generated: `2026-06-18`
- JSON: `experiments\exectv2_diagnosis_reconciler_v02_residual_ledger_dev140_20260618.json`
- JSONL: `experiments\exectv2_hybrid_diagnosis_reconciler_v02_dev140_gpt41mini_20260618.jsonl`
- Split: `dev`
- Letters: 140

## Headline

| Component | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| concept_assertion | 0.647 | 0.636 | 0.658 | 243 | 139 | 126 |

## Top Gold Misses

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 15 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0006, EA0035, EA0039, EA0092, EA0128, EA0133, EA0137, EA0141, ... |
| 7 | `["Diagnosis", "focal epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-epilepsy | EA0002, EA0061, EA0114, EA0121, EA0142, EA0153, EA0178 |
| 6 | `["Diagnosis", "focal seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0002, EA0054, EA0109, EA0126, EA0133, EA0158 |
| 5 | `["Diagnosis", "epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | epilepsy-with-generalised-tonic-clonic-seizure-alone | EA0005, EA0043, EA0062, EA0132, EA0164 |
| 5 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised-tonic-clonic-seizures | EA0005, EA0049, EA0128, EA0168, EA0180 |
| 4 | `["Diagnosis", "focal seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal-seizures | EA0018, EA0110, EA0153, EA0171 |
| 4 | `["Diagnosis", "generalised", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised | EA0123, EA0128, EA0183, EA0195 |
| 4 | `["Diagnosis", "symptomatic epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | symptomatic-epilepsy | EA0079, EA0108, EA0169, EA0181 |
| 3 | `["Diagnosis", "generalised tonic clonic seizure", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | generalised-tonic-clonic-seizure | EA0049, EA0079, EA0161 |
| 3 | `["Diagnosis", "juvenile myoclonic epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | juvenile-myoclonic-epilepsy | EA0085, EA0113, EA0128 |
| 3 | `["Diagnosis", "juvenile myoclonic epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | juvenile-myoclonic-epilepsy | EA0033, EA0049, EA0125 |
| 3 | `["Diagnosis", "secondary generalised seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | secondary-generalised-seizures | EA0040, EA0150, EA0152 |
| 3 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | tonic-clonic-seizures | EA0111, EA0116, EA0200 |
| 2 | `["Diagnosis", "altered awareness", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal-seizures-with-altered-awareness | EA0054, EA0158 |
| 2 | `["Diagnosis", "dyscognitive seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | dyscognitive-seizures | EA0169, EA0181 |

## Top Predicted Over-Emissions

| Count | Key | Example | Letters |
| ---: | --- | --- | --- |
| 56 | `["Diagnosis", "epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy | EA0002, EA0004, EA0005, EA0010, EA0012, EA0021, EA0022, EA0034, ... |
| 24 | `["Diagnosis", "tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | tonic clonic seizures | EA0020, EA0038, EA0043, EA0079, EA0087, EA0104, EA0108, EA0111, ... |
| 8 | `["Diagnosis", "absence seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | absence seizures | EA0020, EA0050, EA0082, EA0096, EA0124, EA0161, EA0184 |
| 7 | `["Diagnosis", "symptomatic structural focal epilepsy", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | symptomatic structural focal epilepsy | EA0056, EA0072, EA0079, EA0108, EA0169, EA0181, EA0195 |
| 5 | `["Diagnosis", "focal seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal seizures | EA0018, EA0057, EA0108, EA0143, EA0153 |
| 4 | `["Diagnosis", "focal epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal epilepsy | EA0002, EA0061, EA0114, EA0171 |
| 4 | `["Diagnosis", "secondary generalised tonic clonic seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | secondary generalised tonic clonic seizures | EA0104, EA0150, EA0188 |
| 4 | `["Diagnosis", "tonic clonic seizures alone", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | epilepsy with tonic clonic seizures alone | EA0043, EA0044 |
| 3 | `["Diagnosis", "absences", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | absences | EA0033, EA0047, EA0125 |
| 3 | `["Diagnosis", "seizure", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | seizure | EA0071, EA0182 |
| 3 | `["Diagnosis", "temporal lobe epilepsy", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | temporal lobe epilepsy | EA0109, EA0149, EA0185 |
| 2 | `["Diagnosis", "altered awareness", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal seizures with altered awareness | EA0143, EA0153 |
| 2 | `["Diagnosis", "complex partial seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | complex partial seizures | EA0150, EA0157 |
| 2 | `["Diagnosis", "focal dyscognitive seizures", [["Certainty", "5"], ["Negation", "Affirmed"]]]` | focal dyscognitive seizures | EA0169, EA0181 |
| 2 | `["Diagnosis", "focal seizures", [["Certainty", "4"], ["Negation", "Affirmed"]]]` | focal seizures | EA0109, EA0158 |
