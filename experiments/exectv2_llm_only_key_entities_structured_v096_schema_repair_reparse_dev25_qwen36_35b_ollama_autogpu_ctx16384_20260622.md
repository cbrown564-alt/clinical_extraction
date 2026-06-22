# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v096_schema_repair_reparse_dev25_qwen36_35b_ollama_autogpu_ctx16384_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.6`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `diagnostic-no-call-reparse`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 138
- Mentions raw: 154
- Mentions scored: 148
- Evidence-invalid dropped: 6
- Evidence validity rate: 0.9610

## Overall Scores

### semantic

- per-item: P=0.290 R=0.294 F1=0.292 (TP=43 FP=105 FN=103)
- per-letter: P=0.809 R=0.479 F1=0.602 (TP=34 FP=8 FN=37)

### benchmark

- per-item: P=0.290 R=0.294 F1=0.292 (TP=43 FP=105 FN=103)
- per-letter: P=0.809 R=0.479 F1=0.602 (TP=34 FP=8 FN=37)

### phrase_only

- per-item: P=0.486 R=0.493 F1=0.490 (TP=72 FP=76 FN=74)
- per-letter: P=0.857 R=0.676 F1=0.756 (TP=48 FP=8 FN=23)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.821 | 0.800 | 0.842 | 32 | 8 | 6 |
| Diagnosis | 0.80 | 0.713 | 0.689 | 0.738 | 31 | 14 | 11 |
| SeizureFrequency | 0.80 | 0.643 | 0.600 | 0.692 | 18 | 12 | 8 |
| Investigations | 0.80 | 0.927 | 0.905 | 0.950 | 19 | 2 | 1 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.775 | 114 | 34 | 32 | 0.649 (74/114) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.809 | 34 | 0.824 (28/34) |
| Diagnosis | 0.774 | 41 | 0.488 (20/41) |
| SeizureFrequency | 0.677 | 21 | 0.429 (9/21) |
| Investigations | 0.857 | 18 | 0.944 (17/18) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.214 | 0.552 |
| Diagnosis | 0.80 | 0.85 | 0.302 | 0.706 |
| SeizureFrequency | 0.80 | 0.66 | 0.226 | 0.444 |
| Investigations | 0.80 | 0.95 | 0.524 | 0.696 |