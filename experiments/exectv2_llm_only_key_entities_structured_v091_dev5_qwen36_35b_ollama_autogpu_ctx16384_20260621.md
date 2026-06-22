# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v091_dev5_qwen36_35b_ollama_autogpu_ctx16384_20260621.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.1`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 5

## Gate Summary

- Call failures: 0
- Parse/schema failures: 1
- Clinical events raw: 27
- Mentions raw: 33
- Mentions scored: 33
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Overall Scores

### semantic

- per-item: P=0.333 R=0.234 F1=0.275 (TP=11 FP=22 FN=36)
- per-letter: P=1.000 R=0.400 F1=0.571 (TP=8 FP=0 FN=12)

### benchmark

- per-item: P=0.333 R=0.234 F1=0.275 (TP=11 FP=22 FN=36)
- per-letter: P=1.000 R=0.400 F1=0.571 (TP=8 FP=0 FN=12)

### phrase_only

- per-item: P=0.576 R=0.404 F1=0.475 (TP=19 FP=14 FN=28)
- per-letter: P=1.000 R=0.550 F1=0.710 (TP=11 FP=0 FN=9)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.875 | 1.000 | 0.778 | 7 | 0 | 2 |
| Diagnosis | 0.80 | 0.348 | 0.333 | 0.364 | 4 | 8 | 7 |
| SeizureFrequency | 0.80 | 0.714 | 0.833 | 0.625 | 5 | 1 | 3 |
| Investigations | 0.80 | 0.857 | 1.000 | 0.750 | 6 | 0 | 2 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.725 | 29 | 4 | 18 | 0.655 (19/29) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.750 | 6 | 1.000 (6/6) |
| Diagnosis | 0.625 | 10 | 0.400 (4/10) |
| SeizureFrequency | 0.778 | 7 | 0.429 (3/7) |
| Investigations | 0.857 | 6 | 1.000 (6/6) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.125 | 0.333 |
| Diagnosis | 0.80 | 0.85 | 0.250 | 0.750 |
| SeizureFrequency | 0.80 | 0.66 | 0.333 | 0.571 |
| Investigations | 0.80 | 0.95 | 0.429 | 0.571 |