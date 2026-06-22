# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v095_dev25_qwen36_35b_ollama_autogpu_ctx16384_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.5`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 1
- Clinical events raw: 129
- Mentions raw: 145
- Mentions scored: 138
- Evidence-invalid dropped: 7
- Evidence validity rate: 0.9517

## Overall Scores

### semantic

- per-item: P=0.333 R=0.315 F1=0.324 (TP=46 FP=92 FN=100)
- per-letter: P=0.804 R=0.521 F1=0.632 (TP=37 FP=9 FN=34)

### benchmark

- per-item: P=0.333 R=0.315 F1=0.324 (TP=46 FP=92 FN=100)
- per-letter: P=0.804 R=0.521 F1=0.632 (TP=37 FP=9 FN=34)

### phrase_only

- per-item: P=0.514 R=0.486 F1=0.500 (TP=71 FP=67 FN=75)
- per-letter: P=0.839 R=0.662 F1=0.740 (TP=47 FP=9 FN=24)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.778 | 0.824 | 0.737 | 28 | 6 | 10 |
| Diagnosis | 0.80 | 0.659 | 0.651 | 0.667 | 28 | 15 | 14 |
| SeizureFrequency | 0.80 | 0.618 | 0.586 | 0.654 | 17 | 12 | 9 |
| Investigations | 0.80 | 0.950 | 0.950 | 0.950 | 19 | 1 | 1 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.732 | 104 | 34 | 42 | 0.654 (68/104) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.831 | 32 | 0.781 (25/32) |
| Diagnosis | 0.660 | 35 | 0.514 (18/35) |
| SeizureFrequency | 0.633 | 19 | 0.421 (8/19) |
| Investigations | 0.878 | 18 | 0.944 (17/18) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.208 | 0.500 |
| Diagnosis | 0.80 | 0.85 | 0.321 | 0.757 |
| SeizureFrequency | 0.80 | 0.66 | 0.300 | 0.533 |
| Investigations | 0.80 | 0.95 | 0.585 | 0.727 |