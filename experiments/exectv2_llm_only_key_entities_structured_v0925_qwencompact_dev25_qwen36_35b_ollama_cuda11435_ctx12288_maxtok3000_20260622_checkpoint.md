# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 25 / 25 letters

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v0925_qwencompact_dev25_qwen36_35b_ollama_cuda11435_ctx12288_maxtok3000_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.25_qwen_compact`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 146
- Mentions raw: 141
- Mentions scored: 136
- Evidence-invalid dropped: 5
- Evidence validity rate: 0.9645

## Overall Scores

### semantic

- per-item: P=0.353 R=0.329 F1=0.340 (TP=48 FP=88 FN=98)
- per-letter: P=0.886 R=0.549 F1=0.678 (TP=39 FP=5 FN=32)

### benchmark

- per-item: P=0.338 R=0.315 F1=0.326 (TP=46 FP=90 FN=100)
- per-letter: P=0.881 R=0.521 F1=0.655 (TP=37 FP=5 FN=34)

### phrase_only

- per-item: P=0.522 R=0.486 F1=0.503 (TP=71 FP=65 FN=75)
- per-letter: P=0.904 R=0.662 F1=0.764 (TP=47 FP=5 FN=24)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.921 | 0.921 | 0.921 | 35 | 3 | 3 |
| Diagnosis | 0.80 | 0.791 | 0.773 | 0.809 | 34 | 10 | 8 |
| SeizureFrequency | 0.80 | 0.640 | 0.667 | 0.615 | 16 | 8 | 10 |
| Investigations | 0.80 | 0.950 | 0.950 | 0.950 | 19 | 1 | 1 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.801 | 113 | 23 | 33 | 0.717 (81/113) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.878 | 36 | 0.889 (32/36) |
| Diagnosis | 0.738 | 38 | 0.526 (20/38) |
| SeizureFrequency | 0.737 | 21 | 0.571 (12/21) |
| Investigations | 0.900 | 18 | 0.944 (17/18) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.244 | 0.581 |
| Diagnosis | 0.80 | 0.85 | 0.311 | 0.743 |
| SeizureFrequency | 0.80 | 0.66 | 0.421 | 0.714 |
| Investigations | 0.80 | 0.95 | 0.500 | 0.667 |