# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 5 / 5 letters

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v097_qwencompact_dev5_qwen36_35b_ollama_cuda11435_ctx12288_maxtok2500_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.7_qwen_compact`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 5

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 37
- Mentions raw: 41
- Mentions scored: 40
- Evidence-invalid dropped: 1
- Evidence validity rate: 0.9756

## Overall Scores

### semantic

- per-item: P=0.300 R=0.255 F1=0.276 (TP=12 FP=28 FN=35)
- per-letter: P=1.000 R=0.500 F1=0.667 (TP=10 FP=0 FN=10)

### benchmark

- per-item: P=0.275 R=0.234 F1=0.253 (TP=11 FP=29 FN=36)
- per-letter: P=1.000 R=0.500 F1=0.667 (TP=10 FP=0 FN=10)

### phrase_only

- per-item: P=0.525 R=0.447 F1=0.483 (TP=21 FP=19 FN=26)
- per-letter: P=1.000 R=0.700 F1=0.824 (TP=14 FP=0 FN=6)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 1.000 | 1.000 | 1.000 | 9 | 0 | 0 |
| Diagnosis | 0.80 | 0.476 | 0.500 | 0.455 | 5 | 5 | 6 |
| SeizureFrequency | 0.80 | 0.889 | 0.800 | 1.000 | 8 | 2 | 0 |
| Investigations | 0.80 | 1.000 | 1.000 | 1.000 | 8 | 0 | 0 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.851 | 37 | 3 | 10 | 0.676 (25/37) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.889 | 8 | 1.000 (8/8) |
| Diagnosis | 0.710 | 11 | 0.636 (7/11) |
| SeizureFrequency | 0.909 | 10 | 0.200 (2/10) |
| Investigations | 1.000 | 8 | 1.000 (8/8) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.222 | 0.571 |
| Diagnosis | 0.80 | 0.85 | 0.323 | 0.889 |
| SeizureFrequency | 0.80 | 0.66 | 0.182 | 0.571 |
| Investigations | 0.80 | 0.95 | 0.375 | 0.571 |