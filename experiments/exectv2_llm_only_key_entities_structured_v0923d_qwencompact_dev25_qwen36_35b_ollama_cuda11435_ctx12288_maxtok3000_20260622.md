# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v0923d_qwencompact_dev25_qwen36_35b_ollama_cuda11435_ctx12288_maxtok3000_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.23_qwen_compact`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 1
- Clinical events raw: 129
- Mentions raw: 127
- Mentions scored: 121
- Evidence-invalid dropped: 6
- Evidence validity rate: 0.9528

## Overall Scores

### semantic

- per-item: P=0.265 R=0.219 F1=0.240 (TP=32 FP=89 FN=114)
- per-letter: P=0.844 R=0.380 F1=0.524 (TP=27 FP=5 FN=44)

### benchmark

- per-item: P=0.248 R=0.205 F1=0.225 (TP=30 FP=91 FN=116)
- per-letter: P=0.833 R=0.352 F1=0.495 (TP=25 FP=5 FN=46)

### phrase_only

- per-item: P=0.529 R=0.438 F1=0.479 (TP=64 FP=57 FN=82)
- per-letter: P=0.898 R=0.620 F1=0.733 (TP=44 FP=5 FN=27)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.904 | 0.943 | 0.868 | 33 | 2 | 5 |
| Diagnosis | 0.80 | 0.642 | 0.667 | 0.619 | 26 | 13 | 16 |
| SeizureFrequency | 0.80 | 0.679 | 0.667 | 0.692 | 18 | 9 | 8 |
| Investigations | 0.80 | 0.895 | 0.944 | 0.850 | 17 | 1 | 3 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.801 | 107 | 14 | 39 | 0.617 (66/107) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.892 | 33 | 0.909 (30/33) |
| Diagnosis | 0.729 | 35 | 0.486 (17/35) |
| SeizureFrequency | 0.746 | 22 | 0.136 (3/22) |
| Investigations | 0.895 | 17 | 0.941 (16/17) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.162 | 0.444 |
| Diagnosis | 0.80 | 0.85 | 0.250 | 0.667 |
| SeizureFrequency | 0.80 | 0.66 | 0.102 | 0.273 |
| Investigations | 0.80 | 0.95 | 0.579 | 0.667 |