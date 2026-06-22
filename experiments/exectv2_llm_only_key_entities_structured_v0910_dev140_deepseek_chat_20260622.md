# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v0910_dev140_deepseek_chat_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.10`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `deepseek/deepseek-chat`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 888
- Mentions raw: 912
- Mentions scored: 899
- Evidence-invalid dropped: 13
- Evidence validity rate: 0.9857

## Overall Scores

### semantic

- per-item: P=0.373 R=0.359 F1=0.365 (TP=335 FP=564 FN=599)
- per-letter: P=0.876 R=0.588 F1=0.704 (TP=247 FP=35 FN=173)

### benchmark

- per-item: P=0.355 R=0.342 F1=0.348 (TP=319 FP=580 FN=615)
- per-letter: P=0.872 R=0.567 F1=0.687 (TP=238 FP=35 FN=182)

### phrase_only

- per-item: P=0.577 R=0.556 F1=0.566 (TP=519 FP=380 FN=415)
- per-letter: P=0.900 R=0.748 F1=0.817 (TP=314 FP=35 FN=106)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.866 | 0.819 | 0.917 | 177 | 39 | 16 |
| Diagnosis | 0.80 | 0.685 | 0.676 | 0.694 | 215 | 103 | 95 |
| SeizureFrequency | 0.80 | 0.732 | 0.695 | 0.774 | 130 | 57 | 38 |
| Investigations | 0.80 | 0.906 | 0.967 | 0.853 | 116 | 4 | 20 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.810 | 742 | 157 | 192 | 0.663 (492/742) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.862 | 188 | 0.830 (156/188) |
| Diagnosis | 0.769 | 289 | 0.516 (149/289) |
| SeizureFrequency | 0.761 | 148 | 0.493 (73/148) |
| Investigations | 0.914 | 117 | 0.974 (114/117) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.284 | 0.536 |
| Diagnosis | 0.80 | 0.85 | 0.322 | 0.818 |
| SeizureFrequency | 0.80 | 0.66 | 0.350 | 0.592 |
| Investigations | 0.80 | 0.95 | 0.656 | 0.857 |