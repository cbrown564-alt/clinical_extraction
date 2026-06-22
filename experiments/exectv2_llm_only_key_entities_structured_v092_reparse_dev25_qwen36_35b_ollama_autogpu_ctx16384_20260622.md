# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v092_reparse_dev25_qwen36_35b_ollama_autogpu_ctx16384_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.2`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `none; no-call reparse over saved ollama_chat/qwen3.6:35b v0.9.1 raw outputs`
- Mode: `diagnostic_no_call_reparse`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 1
- Clinical events raw: 141
- Mentions raw: 148
- Mentions scored: 135
- Evidence-invalid dropped: 13
- Evidence validity rate: 0.9122

## Overall Scores

### semantic

- per-item: P=0.289 R=0.267 F1=0.278 (TP=39 FP=96 FN=107)
- per-letter: P=0.846 R=0.465 F1=0.600 (TP=33 FP=6 FN=38)

### benchmark

- per-item: P=0.289 R=0.267 F1=0.278 (TP=39 FP=96 FN=107)
- per-letter: P=0.846 R=0.465 F1=0.600 (TP=33 FP=6 FN=38)

### phrase_only

- per-item: P=0.496 R=0.459 F1=0.477 (TP=67 FP=68 FN=79)
- per-letter: P=0.885 R=0.648 F1=0.748 (TP=46 FP=6 FN=25)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.789 | 0.849 | 0.737 | 28 | 5 | 10 |
| Diagnosis | 0.80 | 0.539 | 0.511 | 0.571 | 24 | 23 | 18 |
| SeizureFrequency | 0.80 | 0.632 | 0.581 | 0.692 | 18 | 13 | 8 |
| Investigations | 0.80 | 0.950 | 0.950 | 0.950 | 19 | 1 | 1 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.754 | 106 | 29 | 40 | 0.670 (71/106) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.816 | 31 | 0.839 (26/31) |
| Diagnosis | 0.686 | 35 | 0.486 (17/35) |
| SeizureFrequency | 0.698 | 22 | 0.500 (11/22) |
| Investigations | 0.900 | 18 | 0.944 (17/18) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.184 | 0.444 |
| Diagnosis | 0.80 | 0.85 | 0.216 | 0.667 |
| SeizureFrequency | 0.80 | 0.66 | 0.318 | 0.571 |
| Investigations | 0.80 | 0.95 | 0.550 | 0.727 |