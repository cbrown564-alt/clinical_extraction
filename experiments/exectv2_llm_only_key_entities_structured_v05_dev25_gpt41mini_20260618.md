# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v05_dev25_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_llm_only_key_entities_structured_v0.5`
- Pipeline family: `exectv2_llm_only_key_entities_structured`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 146
- Mentions raw: 158
- Mentions scored: 153
- Evidence-invalid dropped: 5
- Evidence validity rate: 0.9684

## Overall Scores

### semantic

- per-item: P=0.359 R=0.377 F1=0.368 (TP=55 FP=98 FN=91)
- per-letter: P=0.837 R=0.578 F1=0.683 (TP=41 FP=8 FN=30)

### benchmark

- per-item: P=0.268 R=0.281 F1=0.274 (TP=41 FP=112 FN=105)
- per-letter: P=0.809 R=0.479 F1=0.602 (TP=34 FP=8 FN=37)

### phrase_only

- per-item: P=0.497 R=0.520 F1=0.508 (TP=76 FP=77 FN=70)
- per-letter: P=0.862 R=0.704 F1=0.775 (TP=50 FP=8 FN=21)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.897 | 0.875 | 0.921 | 35 | 5 | 3 |
| Diagnosis | 0.80 | 0.569 | 0.554 | 0.585 | 31 | 25 | 22 |
| SeizureFrequency | 0.80 | 0.633 | 0.655 | 0.613 | 19 | 10 | 12 |
| Investigations | 0.80 | 0.837 | 0.783 | 0.900 | 18 | 5 | 2 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.729 | 109 | 44 | 37 | 0.752 (82/109) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.727 | 32 | 0.875 (28/32) |
| Diagnosis | 0.667 | 36 | 0.639 (23/36) |
| SeizureFrequency | 0.733 | 22 | 0.591 (13/22) |
| Investigations | 0.884 | 19 | 0.947 (18/19) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.204 | 0.533 |
| Diagnosis | 0.80 | 0.85 | 0.407 | 0.789 |
| SeizureFrequency | 0.80 | 0.66 | 0.433 | 0.714 |
| Investigations | 0.80 | 0.95 | 0.512 | 0.667 |