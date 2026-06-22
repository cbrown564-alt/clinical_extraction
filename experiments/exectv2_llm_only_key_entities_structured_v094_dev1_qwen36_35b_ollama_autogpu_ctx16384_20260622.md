# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v094_dev1_qwen36_35b_ollama_autogpu_ctx16384_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.4`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 1

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 8
- Mentions raw: 8
- Mentions scored: 7
- Evidence-invalid dropped: 1
- Evidence validity rate: 0.8750

## Overall Scores

### semantic

- per-item: P=0.429 R=0.300 F1=0.353 (TP=3 FP=4 FN=7)
- per-letter: P=1.000 R=0.500 F1=0.667 (TP=2 FP=0 FN=2)

### benchmark

- per-item: P=0.429 R=0.300 F1=0.353 (TP=3 FP=4 FN=7)
- per-letter: P=1.000 R=0.500 F1=0.667 (TP=2 FP=0 FN=2)

### phrase_only

- per-item: P=0.714 R=0.500 F1=0.588 (TP=5 FP=2 FN=5)
- per-letter: P=1.000 R=0.750 F1=0.857 (TP=3 FP=0 FN=1)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.667 | 1.000 | 0.500 | 1 | 0 | 1 |
| Diagnosis | 0.80 | 0.667 | 0.667 | 0.667 | 2 | 1 | 1 |
| SeizureFrequency | 0.80 | 1.000 | 1.000 | 1.000 | 2 | 0 | 0 |
| Investigations | 0.80 | 1.000 | 1.000 | 1.000 | 1 | 0 | 0 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.824 | 7 | 0 | 3 | 0.571 (4/7) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.667 | 1 | 1.000 (1/1) |
| Diagnosis | 0.750 | 3 | 0.000 (0/3) |
| SeizureFrequency | 1.000 | 2 | 1.000 (2/2) |
| Investigations | 1.000 | 1 | 1.000 (1/1) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.000 | 0.000 |
| Diagnosis | 0.80 | 0.85 | 0.000 | 0.000 |
| SeizureFrequency | 0.80 | 0.66 | 1.000 | 1.000 |
| Investigations | 0.80 | 0.95 | 1.000 | 1.000 |