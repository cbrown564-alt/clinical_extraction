# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v095_reparse_dev25_qwen36_35b_ollama_autogpu_ctx16384_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.5`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `diagnostic-no-call-reparse`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 133
- Mentions raw: 150
- Mentions scored: 148
- Evidence-invalid dropped: 2
- Evidence validity rate: 0.9867

## Overall Scores

### semantic

- per-item: P=0.324 R=0.329 F1=0.327 (TP=48 FP=100 FN=98)
- per-letter: P=0.796 R=0.549 F1=0.650 (TP=39 FP=10 FN=32)

### benchmark

- per-item: P=0.318 R=0.322 F1=0.320 (TP=47 FP=101 FN=99)
- per-letter: P=0.792 R=0.535 F1=0.639 (TP=38 FP=10 FN=33)

### phrase_only

- per-item: P=0.520 R=0.527 F1=0.524 (TP=77 FP=71 FN=69)
- per-letter: P=0.833 R=0.704 F1=0.763 (TP=50 FP=10 FN=21)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.757 | 0.778 | 0.737 | 28 | 8 | 10 |
| Diagnosis | 0.80 | 0.717 | 0.660 | 0.786 | 33 | 17 | 9 |
| SeizureFrequency | 0.80 | 0.643 | 0.600 | 0.692 | 18 | 12 | 8 |
| Investigations | 0.80 | 0.950 | 0.950 | 0.950 | 19 | 1 | 1 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.755 | 111 | 37 | 35 | 0.640 (71/111) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.835 | 33 | 0.788 (26/33) |
| Diagnosis | 0.708 | 40 | 0.500 (20/40) |
| SeizureFrequency | 0.656 | 20 | 0.400 (8/20) |
| Investigations | 0.878 | 18 | 0.944 (17/18) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.203 | 0.500 |
| Diagnosis | 0.80 | 0.85 | 0.336 | 0.800 |
| SeizureFrequency | 0.80 | 0.66 | 0.295 | 0.533 |
| Investigations | 0.80 | 0.95 | 0.585 | 0.727 |