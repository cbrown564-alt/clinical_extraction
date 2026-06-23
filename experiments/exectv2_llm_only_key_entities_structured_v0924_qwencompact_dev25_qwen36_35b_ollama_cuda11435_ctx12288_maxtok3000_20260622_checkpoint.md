# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 25 / 25 letters

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v0924_qwencompact_dev25_qwen36_35b_ollama_cuda11435_ctx12288_maxtok3000_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24_qwen_compact`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 2
- Clinical events raw: 134
- Mentions raw: 132
- Mentions scored: 127
- Evidence-invalid dropped: 5
- Evidence validity rate: 0.9621

## Overall Scores

### semantic

- per-item: P=0.291 R=0.253 F1=0.271 (TP=37 FP=90 FN=109)
- per-letter: P=0.909 R=0.422 F1=0.577 (TP=30 FP=3 FN=41)

### benchmark

- per-item: P=0.283 R=0.247 F1=0.264 (TP=36 FP=91 FN=110)
- per-letter: P=0.906 R=0.408 F1=0.563 (TP=29 FP=3 FN=42)

### phrase_only

- per-item: P=0.520 R=0.452 F1=0.483 (TP=66 FP=61 FN=80)
- per-letter: P=0.936 R=0.620 F1=0.746 (TP=44 FP=3 FN=27)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.947 | 0.947 | 0.947 | 36 | 2 | 2 |
| Diagnosis | 0.80 | 0.744 | 0.806 | 0.691 | 29 | 7 | 13 |
| SeizureFrequency | 0.80 | 0.667 | 0.680 | 0.654 | 17 | 8 | 9 |
| Investigations | 0.80 | 0.864 | 0.792 | 0.950 | 19 | 5 | 1 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.813 | 111 | 16 | 35 | 0.667 (74/111) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.886 | 35 | 0.914 (32/35) |
| Diagnosis | 0.758 | 36 | 0.500 (18/36) |
| SeizureFrequency | 0.772 | 22 | 0.318 (7/22) |
| Investigations | 0.857 | 18 | 0.944 (17/18) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.177 | 0.429 |
| Diagnosis | 0.80 | 0.85 | 0.232 | 0.625 |
| SeizureFrequency | 0.80 | 0.66 | 0.246 | 0.545 |
| Investigations | 0.80 | 0.95 | 0.571 | 0.727 |