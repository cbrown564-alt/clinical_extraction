# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v098_qwencompact_dev5_qwen36_35b_ollama_cuda11435_ctx12288_maxtok2500_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.8_qwen_compact`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 5

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 35
- Mentions raw: 44
- Mentions scored: 44
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Overall Scores

### semantic

- per-item: P=0.364 R=0.340 F1=0.352 (TP=16 FP=28 FN=31)
- per-letter: P=1.000 R=0.600 F1=0.750 (TP=12 FP=0 FN=8)

### benchmark

- per-item: P=0.364 R=0.340 F1=0.352 (TP=16 FP=28 FN=31)
- per-letter: P=1.000 R=0.600 F1=0.750 (TP=12 FP=0 FN=8)

### phrase_only

- per-item: P=0.568 R=0.532 F1=0.549 (TP=25 FP=19 FN=22)
- per-letter: P=1.000 R=0.700 F1=0.824 (TP=14 FP=0 FN=6)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 1.000 | 1.000 | 1.000 | 9 | 0 | 0 |
| Diagnosis | 0.80 | 0.727 | 0.727 | 0.727 | 8 | 3 | 3 |
| SeizureFrequency | 0.80 | 0.737 | 0.636 | 0.875 | 7 | 4 | 1 |
| Investigations | 0.80 | 0.800 | 0.667 | 1.000 | 8 | 4 | 0 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.901 | 41 | 3 | 6 | 0.683 (28/41) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 1.000 | 9 | 1.000 (9/9) |
| Diagnosis | 0.824 | 14 | 0.643 (9/14) |
| SeizureFrequency | 0.870 | 10 | 0.400 (4/10) |
| Investigations | 1.000 | 8 | 0.750 (6/8) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.222 | 0.571 |
| Diagnosis | 0.80 | 0.85 | 0.471 | 1.000 |
| SeizureFrequency | 0.80 | 0.66 | 0.348 | 0.750 |
| Investigations | 0.80 | 0.95 | 0.250 | 0.571 |