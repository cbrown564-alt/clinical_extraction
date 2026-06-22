# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 5 / 5 letters

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v092_short_rationale_dev5_qwen36_35b_ollama_autogpu_ctx16384_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.2`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 5

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 36
- Mentions raw: 38
- Mentions scored: 37
- Evidence-invalid dropped: 1
- Evidence validity rate: 0.9737

## Overall Scores

### semantic

- per-item: P=0.378 R=0.298 F1=0.333 (TP=14 FP=23 FN=33)
- per-letter: P=1.000 R=0.550 F1=0.710 (TP=11 FP=0 FN=9)

### benchmark

- per-item: P=0.378 R=0.298 F1=0.333 (TP=14 FP=23 FN=33)
- per-letter: P=1.000 R=0.550 F1=0.710 (TP=11 FP=0 FN=9)

### phrase_only

- per-item: P=0.595 R=0.468 F1=0.524 (TP=22 FP=15 FN=25)
- per-letter: P=1.000 R=0.650 F1=0.788 (TP=13 FP=0 FN=7)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.800 | 1.000 | 0.667 | 6 | 0 | 3 |
| Diagnosis | 0.80 | 0.500 | 0.462 | 0.545 | 6 | 7 | 5 |
| SeizureFrequency | 0.80 | 0.941 | 0.889 | 1.000 | 8 | 1 | 0 |
| Investigations | 0.80 | 1.000 | 1.000 | 1.000 | 8 | 0 | 0 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.857 | 36 | 1 | 11 | 0.694 (25/36) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.875 | 7 | 0.857 (6/7) |
| Diagnosis | 0.710 | 11 | 0.545 (6/11) |
| SeizureFrequency | 0.952 | 10 | 0.500 (5/10) |
| Investigations | 1.000 | 8 | 1.000 (8/8) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.250 | 0.571 |
| Diagnosis | 0.80 | 0.85 | 0.258 | 0.750 |
| SeizureFrequency | 0.80 | 0.66 | 0.476 | 0.889 |
| Investigations | 0.80 | 0.95 | 0.375 | 0.571 |