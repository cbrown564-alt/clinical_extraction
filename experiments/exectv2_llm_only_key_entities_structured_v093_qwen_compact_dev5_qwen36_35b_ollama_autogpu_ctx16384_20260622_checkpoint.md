# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 5 / 5 letters

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v093_qwen_compact_dev5_qwen36_35b_ollama_autogpu_ctx16384_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.3_qwen_compact`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 5

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 32
- Mentions raw: 34
- Mentions scored: 32
- Evidence-invalid dropped: 2
- Evidence validity rate: 0.9412

## Overall Scores

### semantic

- per-item: P=0.281 R=0.192 F1=0.228 (TP=9 FP=23 FN=38)
- per-letter: P=1.000 R=0.400 F1=0.571 (TP=8 FP=0 FN=12)

### benchmark

- per-item: P=0.250 R=0.170 F1=0.203 (TP=8 FP=24 FN=39)
- per-letter: P=1.000 R=0.400 F1=0.571 (TP=8 FP=0 FN=12)

### phrase_only

- per-item: P=0.562 R=0.383 F1=0.456 (TP=18 FP=14 FN=29)
- per-letter: P=1.000 R=0.650 F1=0.788 (TP=13 FP=0 FN=7)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.875 | 1.000 | 0.778 | 7 | 0 | 2 |
| Diagnosis | 0.80 | 0.210 | 0.250 | 0.182 | 2 | 6 | 9 |
| SeizureFrequency | 0.80 | 0.625 | 0.625 | 0.625 | 5 | 3 | 3 |
| Investigations | 0.80 | 1.000 | 1.000 | 1.000 | 8 | 0 | 0 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.759 | 30 | 2 | 17 | 0.667 (20/30) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.750 | 6 | 1.000 (6/6) |
| Diagnosis | 0.518 | 7 | 0.857 (6/7) |
| SeizureFrequency | 0.900 | 9 | 0.000 (0/9) |
| Investigations | 1.000 | 8 | 1.000 (8/8) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.125 | 0.333 |
| Diagnosis | 0.80 | 0.85 | 0.370 | 1.000 |
| SeizureFrequency | 0.80 | 0.66 | 0.000 | 0.000 |
| Investigations | 0.80 | 0.95 | 0.375 | 0.571 |