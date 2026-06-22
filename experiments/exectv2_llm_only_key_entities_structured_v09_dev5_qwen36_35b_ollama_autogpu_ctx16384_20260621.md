# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v09_dev5_qwen36_35b_ollama_autogpu_ctx16384_20260621.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 5

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 38
- Mentions raw: 43
- Mentions scored: 41
- Evidence-invalid dropped: 2
- Evidence validity rate: 0.9535

## Overall Scores

### semantic

- per-item: P=0.268 R=0.234 F1=0.250 (TP=11 FP=30 FN=36)
- per-letter: P=1.000 R=0.450 F1=0.621 (TP=9 FP=0 FN=11)

### benchmark

- per-item: P=0.268 R=0.234 F1=0.250 (TP=11 FP=30 FN=36)
- per-letter: P=1.000 R=0.450 F1=0.621 (TP=9 FP=0 FN=11)

### phrase_only

- per-item: P=0.537 R=0.468 F1=0.500 (TP=22 FP=19 FN=25)
- per-letter: P=1.000 R=0.650 F1=0.788 (TP=13 FP=0 FN=7)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.941 | 1.000 | 0.889 | 8 | 0 | 1 |
| Diagnosis | 0.80 | 0.381 | 0.400 | 0.364 | 4 | 6 | 7 |
| SeizureFrequency | 0.80 | 0.778 | 0.700 | 0.875 | 7 | 3 | 1 |
| Investigations | 0.80 | 1.000 | 1.000 | 1.000 | 8 | 0 | 0 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.773 | 34 | 7 | 13 | 0.676 (23/34) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.842 | 8 | 1.000 (8/8) |
| Diagnosis | 0.581 | 9 | 0.222 (2/9) |
| SeizureFrequency | 0.818 | 9 | 0.556 (5/9) |
| Investigations | 1.000 | 8 | 1.000 (8/8) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.210 | 0.571 |
| Diagnosis | 0.80 | 0.85 | 0.000 | 0.000 |
| SeizureFrequency | 0.80 | 0.66 | 0.455 | 0.889 |
| Investigations | 0.80 | 0.95 | 0.500 | 0.750 |