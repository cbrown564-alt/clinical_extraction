# ExECTv2 Deterministic All-9 Baseline Scorecard

- Generated: `2026-07-14`
- JSON: `experiments/exectv2_deterministic_all9_dev_20260714.json`
- Split: `dev`
- Pipeline family: `exectv2_deterministic_all9`
- Active deterministic entities: Prescription, Investigations, Diagnosis, Onset, WhenDiagnosed, BirthHistory, EpilepsyCause, PatientHistory, SeizureFrequency
- Scored entities: BirthHistory, Diagnosis, EpilepsyCause, Investigations, Onset, PatientHistory, Prescription, SeizureFrequency, WhenDiagnosed

## Reliability

- Call failures: 0
- Parse failures: 0
- Schema errors: 0
- Schema repairs: 0
- Evidence-not-substring warnings: 0
- Evidence validity rate: 1.0000
- Mentions emitted: 1186
- CUI attachment: 1180/1186 (0.9949)
- Routed/abstained mentions: 0

## Overall Scores

| Layer | Per-item F1 | Per-letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.5461 | 0.7904 | 728 | 458 | 752 |
| semantic | 0.3668 | 0.6983 | 489 | 697 | 991 |
| benchmark | 0.3548 | 0.6918 | 473 | 713 | 1007 |

## Per-Entity Benchmark F1

| Entity | Item F1 | Letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: |
| BirthHistory | 0.5574 | 0.7317 | 17 | 13 | 14 |
| Diagnosis | 0.2955 | 0.8158 | 108 | 218 | 297 |
| EpilepsyCause | 0.5000 | 0.5806 | 11 | 12 | 10 |
| Investigations | 0.3220 | 0.5755 | 52 | 135 | 84 |
| Onset | 0.2857 | 0.4167 | 5 | 13 | 12 |
| PatientHistory | 0.2371 | 0.5475 | 76 | 99 | 390 |
| Prescription | 0.2788 | 0.5223 | 58 | 152 | 148 |
| SeizureFrequency | 0.6972 | 0.9305 | 137 | 69 | 50 |
| WhenDiagnosed | 0.8182 | 0.9000 | 9 | 2 | 2 |

## Prescription Clinical Headline

| Score | Item F1 | Precision | Recall | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| clinical_headline | 0.9615 | 0.9524 | 0.9709 | 200 | 10 | 6 |

## Prescription Diagnostics

| Diagnostic | Item F1 | Precision | Recall | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| name | 0.9615 | 0.9524 | 0.9709 | 200 | 10 | 6 |
| dose | 0.9682 | 0.9565 | 0.9802 | 198 | 9 | 4 |
| frequency | 0.9663 | 0.9571 | 0.9757 | 201 | 9 | 5 |
| source_stated_frequency | 0.7547 | 0.6061 | 1.0000 | 120 | 78 | 0 |
| guideline_defaulted_frequency | 0.2449 | 1.0000 | 0.1395 | 12 | 0 | 74 |
| complete | 0.9633 | 0.9517 | 0.9752 | 197 | 10 | 5 |
| ordinary_complete | 0.9630 | 0.9512 | 0.9750 | 195 | 10 | 5 |
| rescue_regimen | 0.9091 | 1.0000 | 0.8333 | 5 | 0 | 1 |
| future_medication | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |
| weight_based_dosing | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 |

## Prescription Benchmark Projection

| Projection layer | Item F1 | Precision | Recall | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_scope | 0.2981 | 0.2952 | 0.3010 | 62 | 148 | 144 |
| semantic_without_cui | 0.2788 | 0.2762 | 0.2816 | 58 | 152 | 148 |
| benchmark_with_cui | 0.2788 | 0.2762 | 0.2816 | 58 | 152 | 148 |
| clinical_medication_identity | 0.9615 | 0.9524 | 0.9709 | 200 | 10 | 6 |
| drugname_cui_projection | 0.8558 | 0.8476 | 0.8641 | 178 | 32 | 28 |
| source_stated_frequency | 0.7547 | 0.6061 | 1.0000 | 120 | 78 | 0 |
| guideline_defaulted_frequency | 0.2449 | 1.0000 | 0.1395 | 12 | 0 | 74 |

## PatientHistory Error Ledger

- Gold mentions: 466
- Predicted mentions: 175
- Predicted with CUI: 175
- Predicted with temporal attributes: 9
- Predicted negated: 36

| Gap family | FN / additional FN | FP / additional FP | Note |
| --- | ---: | ---: | --- |
| phrase_scope_or_missing | 364 | 73 | Phrase-only misses and over-emissions before attributes or CUI. |
| attribute_bundle | 25 | 25 | Temporal, negation, and certainty mismatches after phrase match. |
| cui_projection | 1 | 1 | Benchmark-format gap from CUI/CUIPhrase projection. |

## Reading

This is the first rules_only all-entity substrate: it scores all nine entities. Prescription, Investigations, Diagnosis, Onset, WhenDiagnosed, BirthHistory, EpilepsyCause, and SeizureFrequency now sit beside a conservative PatientHistory substrate with explicit phrase, attribute, and CUI gap families.
