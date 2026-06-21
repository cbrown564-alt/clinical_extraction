# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v09_dev140_gpt41mini_20260621.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 925
- Mentions raw: 941
- Mentions scored: 897
- Evidence-invalid dropped: 44
- Evidence validity rate: 0.9532

## Overall Scores

### semantic

- per-item: P=0.278 R=0.267 F1=0.272 (TP=249 FP=648 FN=685)
- per-letter: P=0.809 R=0.474 F1=0.598 (TP=199 FP=47 FN=221)

### benchmark

- per-item: P=0.263 R=0.253 F1=0.258 (TP=236 FP=661 FN=698)
- per-letter: P=0.803 R=0.457 F1=0.583 (TP=192 FP=47 FN=228)

### phrase_only

- per-item: P=0.505 R=0.485 F1=0.495 (TP=453 FP=444 FN=481)
- per-letter: P=0.863 R=0.705 F1=0.776 (TP=296 FP=47 FN=124)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.751 | 0.785 | 0.720 | 139 | 38 | 54 |
| Diagnosis | 0.80 | 0.591 | 0.613 | 0.571 | 177 | 112 | 133 |
| SeizureFrequency | 0.80 | 0.668 | 0.624 | 0.720 | 121 | 73 | 47 |
| Investigations | 0.80 | 0.855 | 0.916 | 0.801 | 109 | 10 | 27 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.721 | 660 | 237 | 274 | 0.570 (376/660) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.681 | 161 | 0.739 (119/161) |
| Diagnosis | 0.693 | 247 | 0.445 (110/247) |
| SeizureFrequency | 0.692 | 135 | 0.296 (40/135) |
| Investigations | 0.918 | 117 | 0.914 (107/117) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.173 | 0.415 |
| Diagnosis | 0.80 | 0.85 | 0.244 | 0.730 |
| SeizureFrequency | 0.80 | 0.66 | 0.205 | 0.430 |
| Investigations | 0.80 | 0.95 | 0.635 | 0.812 |