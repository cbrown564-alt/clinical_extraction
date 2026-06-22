# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 25 / 25 letters

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v091_dev25_qwen36_35b_ollama_autogpu_ctx16384_20260621.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.1`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 2
- Clinical events raw: 136
- Mentions raw: 143
- Mentions scored: 130
- Evidence-invalid dropped: 13
- Evidence validity rate: 0.9091

## Overall Scores

### semantic

- per-item: P=0.269 R=0.240 F1=0.254 (TP=35 FP=95 FN=111)
- per-letter: P=0.833 R=0.422 F1=0.561 (TP=30 FP=6 FN=41)

### benchmark

- per-item: P=0.269 R=0.240 F1=0.254 (TP=35 FP=95 FN=111)
- per-letter: P=0.833 R=0.422 F1=0.561 (TP=30 FP=6 FN=41)

### phrase_only

- per-item: P=0.485 R=0.431 F1=0.457 (TP=63 FP=67 FN=83)
- per-letter: P=0.878 R=0.606 F1=0.717 (TP=43 FP=6 FN=28)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.754 | 0.839 | 0.684 | 26 | 5 | 12 |
| Diagnosis | 0.80 | 0.523 | 0.500 | 0.548 | 23 | 23 | 19 |
| SeizureFrequency | 0.80 | 0.632 | 0.581 | 0.692 | 18 | 13 | 8 |
| Investigations | 0.80 | 0.895 | 0.944 | 0.850 | 17 | 1 | 3 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.732 | 101 | 29 | 45 | 0.653 (66/101) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.784 | 29 | 0.828 (24/29) |
| Diagnosis | 0.673 | 34 | 0.471 (16/34) |
| SeizureFrequency | 0.698 | 22 | 0.500 (11/22) |
| Investigations | 0.842 | 16 | 0.938 (15/16) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.162 | 0.385 |
| Diagnosis | 0.80 | 0.85 | 0.198 | 0.625 |
| SeizureFrequency | 0.80 | 0.66 | 0.318 | 0.571 |
| Investigations | 0.80 | 0.95 | 0.474 | 0.667 |