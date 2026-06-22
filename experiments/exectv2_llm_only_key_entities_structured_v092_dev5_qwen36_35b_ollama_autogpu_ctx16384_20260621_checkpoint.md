# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 5 / 5 letters

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v092_dev5_qwen36_35b_ollama_autogpu_ctx16384_20260621.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.2`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 5

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 37
- Mentions raw: 42
- Mentions scored: 42
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Overall Scores

### semantic

- per-item: P=0.452 R=0.404 F1=0.427 (TP=19 FP=23 FN=28)
- per-letter: P=1.000 R=0.750 F1=0.857 (TP=15 FP=0 FN=5)

### benchmark

- per-item: P=0.452 R=0.404 F1=0.427 (TP=19 FP=23 FN=28)
- per-letter: P=1.000 R=0.750 F1=0.857 (TP=15 FP=0 FN=5)

### phrase_only

- per-item: P=0.595 R=0.532 F1=0.562 (TP=25 FP=17 FN=22)
- per-letter: P=1.000 R=0.750 F1=0.857 (TP=15 FP=0 FN=5)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.889 | 0.889 | 0.889 | 8 | 1 | 1 |
| Diagnosis | 0.80 | 0.417 | 0.385 | 0.455 | 5 | 8 | 6 |
| SeizureFrequency | 0.80 | 0.941 | 0.889 | 1.000 | 8 | 1 | 0 |
| Investigations | 0.80 | 1.000 | 1.000 | 1.000 | 8 | 0 | 0 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.832 | 37 | 5 | 10 | 0.811 (30/37) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.889 | 8 | 1.000 (8/8) |
| Diagnosis | 0.706 | 12 | 0.667 (8/12) |
| SeizureFrequency | 0.857 | 9 | 0.667 (6/9) |
| Investigations | 1.000 | 8 | 1.000 (8/8) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.222 | 0.571 |
| Diagnosis | 0.80 | 0.85 | 0.412 | 1.000 |
| SeizureFrequency | 0.80 | 0.66 | 0.571 | 1.000 |
| Investigations | 0.80 | 0.95 | 0.500 | 0.750 |