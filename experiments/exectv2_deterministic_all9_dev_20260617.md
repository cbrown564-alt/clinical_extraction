# ExECTv2 Deterministic All-9 Baseline Scorecard

- Generated: `2026-06-17`
- JSON: `experiments\exectv2_deterministic_all9_dev_20260617.json`
- Split: `dev`
- Pipeline family: `exectv2_deterministic_all9`
- Active deterministic entities: Prescription, Investigations, Diagnosis, SeizureFrequency
- Scored entities: BirthHistory, Diagnosis, EpilepsyCause, Investigations, Onset, PatientHistory, Prescription, SeizureFrequency, WhenDiagnosed

## Reliability

- Call failures: 0
- Parse failures: 0
- Schema errors: 0
- Schema repairs: 0
- Evidence-not-substring warnings: 0
- Evidence validity rate: 1.0000
- Mentions emitted: 758
- CUI attachment: 750/758 (0.9894)
- Routed/abstained mentions: 0

## Overall Scores

| Layer | Per-item F1 | Per-letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.3789 | 0.6210 | 424 | 334 | 1056 |
| semantic | 0.3119 | 0.5625 | 349 | 409 | 1131 |
| benchmark | 0.2985 | 0.5528 | 334 | 424 | 1146 |

## Per-Entity Benchmark F1

| Entity | Item F1 | Letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: |
| BirthHistory | 0.0000 | 0.0000 | 0 | 0 | 31 |
| Diagnosis | 0.3351 | 0.7615 | 96 | 72 | 309 |
| EpilepsyCause | 0.0000 | 0.0000 | 0 | 0 | 21 |
| Investigations | 0.2547 | 0.5333 | 41 | 145 | 95 |
| Onset | 0.0000 | 0.0000 | 0 | 0 | 17 |
| PatientHistory | 0.0000 | 0.0000 | 0 | 0 | 466 |
| Prescription | 0.3020 | 0.5223 | 61 | 137 | 145 |
| SeizureFrequency | 0.6921 | 0.9247 | 136 | 70 | 51 |
| WhenDiagnosed | 0.0000 | 0.0000 | 0 | 0 | 11 |

## Prescription Component F1

| Component | Item F1 | Precision | Recall | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| name | 0.9257 | 0.9444 | 0.9078 | 187 | 11 | 19 |
| dose | 0.9343 | 0.9536 | 0.9158 | 185 | 9 | 17 |
| frequency | 0.9307 | 0.9495 | 0.9126 | 188 | 10 | 18 |
| complete | 0.9293 | 0.9485 | 0.9109 | 184 | 10 | 18 |

## Reading

This is the first rules_only all-entity substrate: it scores all nine entities, but only Prescription, Investigations, Diagnosis, and SeizureFrequency have active deterministic extractors. Missing entities are visible as false negatives rather than hidden.
