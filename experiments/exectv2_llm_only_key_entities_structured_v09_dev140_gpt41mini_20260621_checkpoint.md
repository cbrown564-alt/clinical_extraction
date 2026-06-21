# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 125 / 140 letters

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v09_dev140_gpt41mini_20260621.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 125

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 822
- Mentions raw: 836
- Mentions scored: 793
- Evidence-invalid dropped: 43
- Evidence validity rate: 0.9486

## Overall Scores

### semantic

- per-item: P=0.282 R=0.272 F1=0.277 (TP=224 FP=569 FN=601)
- per-letter: P=0.803 R=0.484 F1=0.604 (TP=179 FP=44 FN=191)

### benchmark

- per-item: P=0.266 R=0.256 F1=0.261 (TP=211 FP=582 FN=614)
- per-letter: P=0.796 R=0.465 F1=0.587 (TP=172 FP=44 FN=198)

### phrase_only

- per-item: P=0.508 R=0.488 F1=0.498 (TP=403 FP=390 FN=422)
- per-letter: P=0.858 R=0.716 F1=0.781 (TP=265 FP=44 FN=105)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.734 | 0.769 | 0.702 | 120 | 36 | 51 |
| Diagnosis | 0.80 | 0.607 | 0.623 | 0.593 | 160 | 97 | 110 |
| SeizureFrequency | 0.80 | 0.665 | 0.620 | 0.716 | 106 | 65 | 42 |
| Investigations | 0.80 | 0.853 | 0.912 | 0.802 | 93 | 9 | 23 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.713 | 577 | 216 | 248 | 0.572 (330/577) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.674 | 143 | 0.734 (105/143) |
| Diagnosis | 0.688 | 218 | 0.454 (99/218) |
| SeizureFrequency | 0.678 | 116 | 0.302 (35/116) |
| Investigations | 0.917 | 100 | 0.910 (91/100) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.189 | 0.443 |
| Diagnosis | 0.80 | 0.85 | 0.252 | 0.741 |
| SeizureFrequency | 0.80 | 0.66 | 0.210 | 0.429 |
| Investigations | 0.80 | 0.95 | 0.624 | 0.800 |