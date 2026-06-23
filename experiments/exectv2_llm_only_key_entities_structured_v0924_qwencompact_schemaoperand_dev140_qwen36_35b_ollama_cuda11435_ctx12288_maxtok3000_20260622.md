# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v0924_qwencompact_schemaoperand_dev140_qwen36_35b_ollama_cuda11435_ctx12288_maxtok3000_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24_qwen_compact`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 3
- Clinical events raw: 853
- Mentions raw: 866
- Mentions scored: 831
- Evidence-invalid dropped: 35
- Evidence validity rate: 0.9596

## Overall Scores

### semantic

- per-item: P=0.264 R=0.234 F1=0.248 (TP=219 FP=612 FN=715)
- per-letter: P=0.797 R=0.421 F1=0.551 (TP=177 FP=45 FN=243)

### benchmark

- per-item: P=0.244 R=0.217 F1=0.230 (TP=203 FP=628 FN=731)
- per-letter: P=0.787 R=0.395 F1=0.526 (TP=166 FP=45 FN=254)

### phrase_only

- per-item: P=0.492 R=0.438 F1=0.464 (TP=409 FP=422 FN=525)
- per-letter: P=0.859 R=0.655 F1=0.743 (TP=275 FP=45 FN=145)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.841 | 0.822 | 0.860 | 166 | 36 | 27 |
| Diagnosis | 0.80 | 0.592 | 0.607 | 0.577 | 179 | 116 | 131 |
| SeizureFrequency | 0.80 | 0.559 | 0.542 | 0.577 | 97 | 82 | 71 |
| Investigations | 0.80 | 0.763 | 0.769 | 0.757 | 103 | 31 | 33 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.739 | 652 | 179 | 282 | 0.569 (371/652) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.812 | 175 | 0.794 (139/175) |
| Diagnosis | 0.675 | 238 | 0.525 (125/238) |
| SeizureFrequency | 0.705 | 134 | 0.157 (21/134) |
| Investigations | 0.843 | 105 | 0.819 (86/105) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.237 | 0.425 |
| Diagnosis | 0.80 | 0.85 | 0.267 | 0.750 |
| SeizureFrequency | 0.80 | 0.66 | 0.089 | 0.230 |
| Investigations | 0.80 | 0.95 | 0.458 | 0.724 |