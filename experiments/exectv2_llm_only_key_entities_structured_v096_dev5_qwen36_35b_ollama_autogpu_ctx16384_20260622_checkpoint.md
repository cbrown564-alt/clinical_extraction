# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 5 / 5 letters

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v096_dev5_qwen36_35b_ollama_autogpu_ctx16384_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.6`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 5

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 34
- Mentions raw: 41
- Mentions scored: 40
- Evidence-invalid dropped: 1
- Evidence validity rate: 0.9756

## Overall Scores

### semantic

- per-item: P=0.475 R=0.404 F1=0.437 (TP=19 FP=21 FN=28)
- per-letter: P=1.000 R=0.750 F1=0.857 (TP=15 FP=0 FN=5)

### benchmark

- per-item: P=0.475 R=0.404 F1=0.437 (TP=19 FP=21 FN=28)
- per-letter: P=1.000 R=0.750 F1=0.857 (TP=15 FP=0 FN=5)

### phrase_only

- per-item: P=0.650 R=0.553 F1=0.598 (TP=26 FP=14 FN=21)
- per-letter: P=1.000 R=0.750 F1=0.857 (TP=15 FP=0 FN=5)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 1.000 | 1.000 | 1.000 | 9 | 0 | 0 |
| Diagnosis | 0.80 | 0.762 | 0.800 | 0.727 | 8 | 2 | 3 |
| SeizureFrequency | 0.80 | 0.875 | 0.875 | 0.875 | 7 | 1 | 1 |
| Investigations | 0.80 | 1.000 | 1.000 | 1.000 | 8 | 0 | 0 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.897 | 39 | 1 | 8 | 0.795 (31/39) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 1.000 | 9 | 1.000 (9/9) |
| Diagnosis | 0.824 | 14 | 0.643 (9/14) |
| SeizureFrequency | 0.842 | 8 | 0.625 (5/8) |
| Investigations | 1.000 | 8 | 1.000 (8/8) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.222 | 0.571 |
| Diagnosis | 0.80 | 0.85 | 0.471 | 1.000 |
| SeizureFrequency | 0.80 | 0.66 | 0.526 | 1.000 |
| Investigations | 0.80 | 0.95 | 0.500 | 0.750 |