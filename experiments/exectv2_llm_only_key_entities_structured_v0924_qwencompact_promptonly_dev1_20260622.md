# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v0924_qwencompact_promptonly_dev1_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.23_qwen_compact`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `prompt-only`
- Letters: 1

## Gate Summary

- Call failures: 0
- Parse/schema failures: 1
- Clinical events raw: 0
- Mentions raw: 0
- Mentions scored: 0
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Overall Scores

### semantic

- per-item: P=0.000 R=0.000 F1=0.000 (TP=0 FP=0 FN=10)
- per-letter: P=0.000 R=0.000 F1=0.000 (TP=0 FP=0 FN=4)

### benchmark

- per-item: P=0.000 R=0.000 F1=0.000 (TP=0 FP=0 FN=10)
- per-letter: P=0.000 R=0.000 F1=0.000 (TP=0 FP=0 FN=4)

### phrase_only

- per-item: P=0.000 R=0.000 F1=0.000 (TP=0 FP=0 FN=10)
- per-letter: P=0.000 R=0.000 F1=0.000 (TP=0 FP=0 FN=4)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.000 | 0.000 | 0.000 | 0 | 0 | 2 |
| Diagnosis | 0.80 | 0.000 | 0.000 | 0.000 | 0 | 0 | 3 |
| SeizureFrequency | 0.80 | 0.000 | 0.000 | 0.000 | 0 | 0 | 2 |
| Investigations | 0.80 | 0.000 | 0.000 | 0.000 | 0 | 0 | 1 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.000 | 0 | 0 | 10 | 0.000 (0/0) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.000 | 0 | 0.000 (0/0) |
| Diagnosis | 0.000 | 0 | 0.000 (0/0) |
| SeizureFrequency | 0.000 | 0 | 0.000 (0/0) |
| Investigations | 0.000 | 0 | 0.000 (0/0) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.000 | 0.000 |
| Diagnosis | 0.80 | 0.85 | 0.000 | 0.000 |
| SeizureFrequency | 0.80 | 0.66 | 0.000 | 0.000 |
| Investigations | 0.80 | 0.95 | 0.000 | 0.000 |