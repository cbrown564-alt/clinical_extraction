# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v0924_qwencompact_dev5_qwen36_35b_ollama_cuda11435_ctx12288_maxtok3000_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24_qwen_compact`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 5

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 40
- Mentions raw: 43
- Mentions scored: 43
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Overall Scores

### semantic

- per-item: P=0.349 R=0.319 F1=0.333 (TP=15 FP=28 FN=32)
- per-letter: P=1.000 R=0.550 F1=0.710 (TP=11 FP=0 FN=9)

### benchmark

- per-item: P=0.349 R=0.319 F1=0.333 (TP=15 FP=28 FN=32)
- per-letter: P=1.000 R=0.550 F1=0.710 (TP=11 FP=0 FN=9)

### phrase_only

- per-item: P=0.581 R=0.532 F1=0.556 (TP=25 FP=18 FN=22)
- per-letter: P=1.000 R=0.700 F1=0.824 (TP=14 FP=0 FN=6)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.889 | 0.889 | 0.889 | 8 | 1 | 1 |
| Diagnosis | 0.80 | 0.857 | 0.900 | 0.818 | 9 | 1 | 2 |
| SeizureFrequency | 0.80 | 0.842 | 0.727 | 1.000 | 8 | 3 | 0 |
| Investigations | 0.80 | 1.000 | 1.000 | 1.000 | 8 | 0 | 0 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.889 | 40 | 3 | 7 | 0.700 (28/40) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 1.000 | 9 | 0.889 (8/9) |
| Diagnosis | 0.812 | 13 | 0.692 (9/13) |
| SeizureFrequency | 0.833 | 10 | 0.400 (4/10) |
| Investigations | 1.000 | 8 | 0.875 (7/8) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.222 | 0.571 |
| Diagnosis | 0.80 | 0.85 | 0.438 | 0.889 |
| SeizureFrequency | 0.80 | 0.66 | 0.333 | 0.750 |
| Investigations | 0.80 | 0.95 | 0.250 | 0.571 |