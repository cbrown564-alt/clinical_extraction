# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v094_dev5_qwen36_35b_ollama_autogpu_ctx16384_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.4`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 5

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 44
- Mentions raw: 47
- Mentions scored: 45
- Evidence-invalid dropped: 2
- Evidence validity rate: 0.9574

## Overall Scores

### semantic

- per-item: P=0.400 R=0.383 F1=0.391 (TP=18 FP=27 FN=29)
- per-letter: P=1.000 R=0.650 F1=0.788 (TP=13 FP=0 FN=7)

### benchmark

- per-item: P=0.400 R=0.383 F1=0.391 (TP=18 FP=27 FN=29)
- per-letter: P=1.000 R=0.650 F1=0.788 (TP=13 FP=0 FN=7)

### phrase_only

- per-item: P=0.644 R=0.617 F1=0.630 (TP=29 FP=16 FN=18)
- per-letter: P=1.000 R=0.700 F1=0.824 (TP=14 FP=0 FN=6)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.824 | 0.875 | 0.778 | 7 | 1 | 2 |
| Diagnosis | 0.80 | 0.783 | 0.750 | 0.818 | 9 | 3 | 2 |
| SeizureFrequency | 0.80 | 0.933 | 1.000 | 0.875 | 7 | 0 | 1 |
| Investigations | 0.80 | 1.000 | 1.000 | 1.000 | 8 | 0 | 0 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.870 | 40 | 5 | 7 | 0.700 (28/40) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.842 | 8 | 0.875 (7/8) |
| Diagnosis | 0.811 | 15 | 0.533 (8/15) |
| SeizureFrequency | 0.900 | 9 | 0.556 (5/9) |
| Investigations | 1.000 | 8 | 1.000 (8/8) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.210 | 0.571 |
| Diagnosis | 0.80 | 0.85 | 0.432 | 1.000 |
| SeizureFrequency | 0.80 | 0.66 | 0.500 | 0.889 |
| Investigations | 0.80 | 0.95 | 0.375 | 0.571 |