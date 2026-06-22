# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v09_dev1_qwen36_35b_ollama_autogpu_ctx16384_20260621.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 1

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 6
- Mentions raw: 8
- Mentions scored: 8
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Overall Scores

### semantic

- per-item: P=0.500 R=0.400 F1=0.444 (TP=4 FP=4 FN=6)
- per-letter: P=1.000 R=0.750 F1=0.857 (TP=3 FP=0 FN=1)

### benchmark

- per-item: P=0.500 R=0.400 F1=0.444 (TP=4 FP=4 FN=6)
- per-letter: P=1.000 R=0.750 F1=0.857 (TP=3 FP=0 FN=1)

### phrase_only

- per-item: P=0.875 R=0.700 F1=0.778 (TP=7 FP=1 FN=3)
- per-letter: P=1.000 R=1.000 F1=1.000 (TP=4 FP=0 FN=0)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 1.000 | 1.000 | 1.000 | 2 | 0 | 0 |
| Diagnosis | 0.80 | 0.667 | 0.667 | 0.667 | 2 | 1 | 1 |
| SeizureFrequency | 0.80 | 1.000 | 1.000 | 1.000 | 2 | 0 | 0 |
| Investigations | 0.80 | 1.000 | 1.000 | 1.000 | 1 | 0 | 0 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.889 | 8 | 0 | 2 | 0.625 (5/8) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 1.000 | 2 | 1.000 (2/2) |
| Diagnosis | 0.750 | 3 | 0.000 (0/3) |
| SeizureFrequency | 1.000 | 2 | 1.000 (2/2) |
| Investigations | 1.000 | 1 | 1.000 (1/1) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.500 | 1.000 |
| Diagnosis | 0.80 | 0.85 | 0.000 | 0.000 |
| SeizureFrequency | 0.80 | 0.66 | 1.000 | 1.000 |
| Investigations | 0.80 | 0.95 | 1.000 | 1.000 |