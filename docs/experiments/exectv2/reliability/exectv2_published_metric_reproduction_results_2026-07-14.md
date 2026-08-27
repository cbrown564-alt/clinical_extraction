# ExECTv2 published-metric reproduction

- Generated: `2026-07-14`
- JSON: `experiments/exectv2_published_metric_reproduction_deterministic_all9_dev140_20260714.json`
- Candidate: `exectv2_deterministic_all9`
- Split: `dev140` (140 rows)
- Entity coverage: `9/9`
- Scorer: `exectv2_published_metrics_v1`
- Mode: `no_call_deterministic_replay`

## Result

| View | Macro per-item F1 | Macro per-letter F1 |
| --- | ---: | ---: |
| normalized_phrase | 0.5687 | 0.7518 |
| cui | 0.7144 | 0.8534 |
| all_features | 0.6020 | 0.7922 |

The paper's original ExECTv2 reference is 0.87 per item and 0.90 per letter across nine entities. This development replay is not a reproduction of the original ExECTv2 system; it reproduces the documented measurement family on the named candidate.

## Per-entity representation layers

| Entity | Phrase F1 | CUI F1 | All-features F1 | Phrase→CUI | CUI→features | Missing CUI gold/pred |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BirthHistory | 0.8852 | 0.9180 | 0.7213 | +0.0328 | -0.1967 | 0/0 |
| Diagnosis | 0.6977 | 0.7332 | 0.3010 | +0.0356 | -0.4323 | 1/0 |
| EpilepsyCause | 0.5909 | 0.6818 | 0.6818 | +0.0909 | +0.0000 | 0/0 |
| Investigations | 0.6006 | 0.4334 | 0.4211 | -0.1672 | -0.0124 | 0/1 |
| Onset | 0.4000 | 0.6286 | 0.5143 | +0.2286 | -0.1143 | 0/0 |
| PatientHistory | 0.3183 | 0.3900 | 0.2871 | +0.0718 | -0.1030 | 0/0 |
| Prescription | 0.2981 | 0.8606 | 0.7692 | +0.5625 | -0.0913 | 0/0 |
| SeizureFrequency | 0.5089 | 0.7837 | 0.7226 | +0.2748 | -0.0611 | 0/5 |
| WhenDiagnosed | 0.8182 | 1.0000 | 1.0000 | +0.1818 | +0.0000 | 0/0 |

## Permitted development-row mechanism examples

Counts: `cui_match_feature_miss`=215, `phrase_match_cui_miss`=52, `phrase_miss_cui_match`=215

| Entity | Category | Letter | Gold → predicted phrase | CUI | Differing features |
| --- | --- | --- | --- | --- | --- |
| Diagnosis | cui_match_feature_miss | EA0002 | secondary generalised seizures → secondary generalised seizures | C0270838 | DiagCategory |
| Prescription | phrase_miss_cui_match | EA0002 | carbamazepine → carbamazepine 400 mg twice a day | C0006949 | — |
| Investigations | phrase_match_cui_miss | EA0004 | eeg → eeg | C0151611 → C0013819 | EEG_Results |
| Investigations | phrase_miss_cui_match | EA0005 | mri 2012 normal → mri | C0436481 | — |
| SeizureFrequency | phrase_miss_cui_match | EA0006 | generalised tonic clonic seizures 2014 → generalised tonic clonic seizures | C0494475 | — |
| Diagnosis | phrase_match_cui_miss | EA0008 | symptomatic structural focal epilepsy → symptomatic structural focal epilepsy | C0472349 → C0014547 | — |
| PatientHistory | cui_match_feature_miss | EA0009 | febrile seizures → febrile seizures | C0009952 | Age, AgeLower, AgeUnit, AgeUpper |
| PatientHistory | phrase_miss_cui_match | EA0009 | cluster of seizure → cluster of seizures | C3203523 | — |
| EpilepsyCause | phrase_miss_cui_match | EA0010 | erinatal insult → perinatal insult | C0005604 | — |
| Prescription | cui_match_feature_miss | EA0011 | eslicarbazepine → eslicarbazepine, 800 mg once a day | C2725260 | DrugName |
| Prescription | phrase_match_cui_miss | EA0012 | tegretol 600 mg daily → tegretol 600 mg daily | C0700087 → C0006949 | DrugName |
| BirthHistory | cui_match_feature_miss | EA0021 | normal birth → normal birth | C3665337 | PrematureBirth |
| SeizureFrequency | cui_match_feature_miss | EA0022 | focal seizures → focal seizures | C0751495 | PointInTime |
| Onset | phrase_miss_cui_match | EA0033 | epileps → epilepsy | C0014544 | — |
| Diagnosis | phrase_miss_cui_match | EA0040 | secondly generalised seizures → secondarily generalised seizures | C0270838 | DiagCategory |
| Onset | cui_match_feature_miss | EA0057 | epilepsy → epilepsy | C0014544 | Age, AgeUnit, NumberOfTimePeriods, TimePeriod |
| PatientHistory | phrase_match_cui_miss | EA0073 | diabetes → diabetes | C0011847 → C0011849 | — |
| WhenDiagnosed | phrase_miss_cui_match | EA0075 | epilepsy → epileps | C0014544 | — |
| Investigations | cui_match_feature_miss | EA0129 | eeg → ct | C0560017 | CT_Performed, CT_Results, EEG_Performed, EEG_Results |
| BirthHistory | phrase_miss_cui_match | EA0133 | prematurely → born prematurely at 32 weeks | C4054482 | — |
| BirthHistory | phrase_match_cui_miss | EA0137 | perinatal injury → perinatal injury | C0005604 → C0456798 | — |

## Existing-score regression

| Existing view | Micro per-item F1 | Micro per-letter F1 |
| --- | ---: | ---: |
| phrase_only_micro | 0.5461 | 0.7904 |
| semantic_micro | 0.3668 | 0.6983 |
| benchmark_micro | 0.3548 | 0.6918 |

## Claim boundary

Development evidence that the repository implements the paper-derived metric family. This is not a reproduction of the original ExECTv2 system's score, independent clinical validation, or holdout evidence.
