# ExECTv2 Deterministic All-9 Baseline Scorecard

- Generated: `2026-06-17`
- JSON: `experiments\exectv2_deterministic_all9_dev_20260617.json`
- Split: `dev`
- Pipeline family: `exectv2_deterministic_all9`
- Active deterministic entities: Prescription, Investigations, Diagnosis, Onset, WhenDiagnosed, BirthHistory, EpilepsyCause, SeizureFrequency
- Scored entities: BirthHistory, Diagnosis, EpilepsyCause, Investigations, Onset, PatientHistory, Prescription, SeizureFrequency, WhenDiagnosed

## Reliability

- Call failures: 0
- Parse failures: 0
- Schema errors: 0
- Schema repairs: 0
- Evidence-not-substring warnings: 0
- Evidence validity rate: 1.0000
- Mentions emitted: 835
- CUI attachment: 826/835 (0.9892)
- Routed/abstained mentions: 0

## Overall Scores

| Layer | Per-item F1 | Per-letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.4095 | 0.6774 | 474 | 361 | 1006 |
| semantic | 0.3438 | 0.6146 | 398 | 437 | 1082 |
| benchmark | 0.3309 | 0.6072 | 383 | 452 | 1097 |

## Per-Entity Benchmark F1

| Entity | Item F1 | Letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: |
| BirthHistory | 0.5574 | 0.7317 | 17 | 13 | 14 |
| Diagnosis | 0.3216 | 0.7500 | 91 | 70 | 314 |
| EpilepsyCause | 0.5333 | 0.5806 | 12 | 12 | 9 |
| Investigations | 0.3220 | 0.5755 | 52 | 135 | 84 |
| Onset | 0.2857 | 0.4167 | 5 | 13 | 12 |
| PatientHistory | 0.0000 | 0.0000 | 0 | 0 | 466 |
| Prescription | 0.3020 | 0.5223 | 61 | 137 | 145 |
| SeizureFrequency | 0.6921 | 0.9247 | 136 | 70 | 51 |
| WhenDiagnosed | 0.8182 | 0.9000 | 9 | 2 | 2 |

## Prescription Clinical Headline

| Score | Item F1 | Precision | Recall | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| clinical_headline | 0.9072 | 0.9293 | 0.8860 | 171 | 13 | 22 |

## Prescription Diagnostics

| Diagnostic | Item F1 | Precision | Recall | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| name | 0.9257 | 0.9444 | 0.9078 | 187 | 11 | 19 |
| dose | 0.9343 | 0.9536 | 0.9158 | 185 | 9 | 17 |
| frequency | 0.9307 | 0.9495 | 0.9126 | 188 | 10 | 18 |
| source_stated_frequency | 0.9307 | 0.9495 | 0.9126 | 188 | 10 | 18 |
| guideline_defaulted_frequency | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |
| complete | 0.9293 | 0.9485 | 0.9109 | 184 | 10 | 18 |
| ordinary_complete | 0.9096 | 0.9326 | 0.8877 | 166 | 12 | 21 |
| rescue_regimen | 0.8333 | 0.8333 | 0.8333 | 5 | 1 | 1 |
| future_medication | 0.2609 | 0.2143 | 0.3333 | 3 | 11 | 6 |
| weight_based_dosing | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 5 |

## Prescription Benchmark Projection

| Projection layer | Item F1 | Precision | Recall | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_scope | 0.3069 | 0.3131 | 0.3010 | 62 | 136 | 144 |
| semantic_without_cui | 0.3020 | 0.3081 | 0.2961 | 61 | 137 | 145 |
| benchmark_with_cui | 0.3020 | 0.3081 | 0.2961 | 61 | 137 | 145 |
| clinical_medication_identity | 0.9257 | 0.9444 | 0.9078 | 187 | 11 | 19 |
| drugname_cui_projection | 0.9158 | 0.9343 | 0.8981 | 185 | 13 | 21 |
| source_stated_frequency | 0.9307 | 0.9495 | 0.9126 | 188 | 10 | 18 |
| guideline_defaulted_frequency | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |

## Reading

This is the first rules_only all-entity substrate: it scores all nine entities, but only Prescription, Investigations, Diagnosis, Onset, WhenDiagnosed, BirthHistory, EpilepsyCause, and SeizureFrequency have active deterministic extractors. Missing PatientHistory coverage is visible as false negatives rather than hidden.
