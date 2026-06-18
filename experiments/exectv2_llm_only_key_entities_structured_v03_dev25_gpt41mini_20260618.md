# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v03_dev25_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_llm_only_key_entities_structured_v0.3`
- Pipeline family: `exectv2_llm_only_key_entities_structured`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 148
- Mentions raw: 161
- Mentions scored: 152
- Evidence-invalid dropped: 9
- Evidence validity rate: 0.9441

## Overall Scores

### semantic

- per-item: P=0.276 R=0.288 F1=0.282 (TP=42 FP=110 FN=104)
- per-letter: P=0.825 R=0.465 F1=0.595 (TP=33 FP=7 FN=38)

### benchmark

- per-item: P=0.230 R=0.240 F1=0.235 (TP=35 FP=117 FN=111)
- per-letter: P=0.800 R=0.394 F1=0.528 (TP=28 FP=7 FN=43)

### phrase_only

- per-item: P=0.428 R=0.445 F1=0.436 (TP=65 FP=87 FN=81)
- per-letter: P=0.857 R=0.592 F1=0.700 (TP=42 FP=7 FN=29)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.883 | 0.872 | 0.895 | 34 | 5 | 4 |
| Diagnosis | 0.80 | 0.455 | 0.439 | 0.472 | 25 | 32 | 28 |
| SeizureFrequency | 0.80 | 0.421 | 0.462 | 0.387 | 12 | 14 | 19 |
| Investigations | 0.80 | 0.878 | 0.857 | 0.900 | 18 | 3 | 2 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.718 | 107 | 45 | 39 | 0.654 (70/107) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.703 | 32 | 0.875 (28/32) |
| Diagnosis | 0.661 | 36 | 0.500 (18/36) |
| SeizureFrequency | 0.737 | 21 | 0.333 (7/21) |
| Investigations | 0.878 | 18 | 0.944 (17/18) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.198 | 0.516 |
| Diagnosis | 0.80 | 0.85 | 0.257 | 0.686 |
| SeizureFrequency | 0.80 | 0.66 | 0.246 | 0.455 |
| Investigations | 0.80 | 0.95 | 0.585 | 0.696 |