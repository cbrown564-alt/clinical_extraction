# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_v08_full200_currentcode_structured_gpt41mini_20260624.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `full_200_authorized`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 200

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 1406
- Mentions raw: 1425
- Mentions scored: 1396
- Evidence-invalid dropped: 29
- Evidence validity rate: 0.9796

## Overall Scores

### semantic

- per-item: P=0.393 R=0.418 F1=0.406 (TP=549 FP=847 FN=763)
- per-letter: P=0.852 R=0.588 F1=0.696 (TP=356 FP=62 FN=249)

### benchmark

- per-item: P=0.375 R=0.399 F1=0.386 (TP=523 FP=873 FN=789)
- per-letter: P=0.848 R=0.574 F1=0.684 (TP=347 FP=62 FN=258)

### phrase_only

- per-item: P=0.492 R=0.524 F1=0.507 (TP=687 FP=709 FN=625)
- per-letter: P=0.875 R=0.714 F1=0.786 (TP=432 FP=62 FN=173)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.730 P=0.713 R=0.748

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.822 | 0.769 | 0.882 | 240 | 72 | 32 |
| Diagnosis | 0.80 | 0.688 | 0.674 | 0.702 | 295 | 138 | 125 |
| SeizureFrequency | 0.80 | 0.611 | 0.585 | 0.640 | 155 | 110 | 87 |
| Investigations | 0.80 | 0.856 | 0.924 | 0.798 | 146 | 12 | 37 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.728 | 986 | 410 | 326 | 0.733 (723/986) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.685 | 260 | 0.719 (187/260) |
| Diagnosis | 0.743 | 394 | 0.866 (341/394) |
| SeizureFrequency | 0.662 | 181 | 0.282 (51/181) |
| Investigations | 0.886 | 151 | 0.954 (144/151) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.205 | 0.490 |
| Diagnosis | 0.80 | 0.85 | 0.583 | 0.934 |
| SeizureFrequency | 0.80 | 0.66 | 0.208 | 0.438 |
| Investigations | 0.80 | 0.95 | 0.616 | 0.813 |