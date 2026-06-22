# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v091_reparse_dev5_qwen36_35b_ollama_autogpu_ctx16384_20260621.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.1`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `none; no-call reparse over saved ollama_chat/qwen3.6:35b v0.9.1 raw outputs`
- Mode: `diagnostic_no_call_reparse`
- Letters: 5

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 35
- Mentions raw: 42
- Mentions scored: 42
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Overall Scores

### semantic

- per-item: P=0.357 R=0.319 F1=0.337 (TP=15 FP=27 FN=32)
- per-letter: P=1.000 R=0.600 F1=0.750 (TP=12 FP=0 FN=8)

### benchmark

- per-item: P=0.357 R=0.319 F1=0.337 (TP=15 FP=27 FN=32)
- per-letter: P=1.000 R=0.600 F1=0.750 (TP=12 FP=0 FN=8)

### phrase_only

- per-item: P=0.619 R=0.553 F1=0.584 (TP=26 FP=16 FN=21)
- per-letter: P=1.000 R=0.750 F1=0.857 (TP=15 FP=0 FN=5)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 1.000 | 1.000 | 1.000 | 9 | 0 | 0 |
| Diagnosis | 0.80 | 0.538 | 0.467 | 0.636 | 7 | 8 | 4 |
| SeizureFrequency | 0.80 | 0.875 | 0.875 | 0.875 | 7 | 1 | 1 |
| Investigations | 0.80 | 1.000 | 1.000 | 1.000 | 8 | 0 | 0 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.854 | 38 | 4 | 9 | 0.684 (26/38) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.889 | 8 | 1.000 (8/8) |
| Diagnosis | 0.743 | 13 | 0.462 (6/13) |
| SeizureFrequency | 0.900 | 9 | 0.444 (4/9) |
| Investigations | 1.000 | 8 | 1.000 (8/8) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.222 | 0.571 |
| Diagnosis | 0.80 | 0.85 | 0.286 | 0.889 |
| SeizureFrequency | 0.80 | 0.66 | 0.400 | 0.750 |
| Investigations | 0.80 | 0.95 | 0.500 | 0.750 |