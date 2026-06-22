# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 1 / 1 letters

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v097_dev1_deepseek_chat_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.7`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `deepseek/deepseek-chat`
- Mode: `live`
- Letters: 1

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 8
- Mentions raw: 9
- Mentions scored: 9
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Overall Scores

### semantic

- per-item: P=0.556 R=0.500 F1=0.526 (TP=5 FP=4 FN=5)
- per-letter: P=1.000 R=1.000 F1=1.000 (TP=4 FP=0 FN=0)

### benchmark

- per-item: P=0.556 R=0.500 F1=0.526 (TP=5 FP=4 FN=5)
- per-letter: P=1.000 R=1.000 F1=1.000 (TP=4 FP=0 FN=0)

### phrase_only

- per-item: P=0.889 R=0.800 F1=0.842 (TP=8 FP=1 FN=2)
- per-letter: P=1.000 R=1.000 F1=1.000 (TP=4 FP=0 FN=0)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 1.000 | 1.000 | 1.000 | 2 | 0 | 0 |
| Diagnosis | 0.80 | 1.000 | 1.000 | 1.000 | 3 | 0 | 0 |
| SeizureFrequency | 0.80 | 1.000 | 1.000 | 1.000 | 2 | 0 | 0 |
| Investigations | 0.80 | 1.000 | 1.000 | 1.000 | 1 | 0 | 0 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.947 | 9 | 0 | 1 | 0.667 (6/9) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 1.000 | 2 | 1.000 (2/2) |
| Diagnosis | 0.889 | 4 | 0.500 (2/4) |
| SeizureFrequency | 1.000 | 2 | 0.500 (1/2) |
| Investigations | 1.000 | 1 | 1.000 (1/1) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.500 | 1.000 |
| Diagnosis | 0.80 | 0.85 | 0.444 | 1.000 |
| SeizureFrequency | 0.80 | 0.66 | 0.500 | 1.000 |
| Investigations | 0.80 | 0.95 | 1.000 | 1.000 |