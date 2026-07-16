# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_six_model_gpt41mini_dev140_20260715_structured.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev140`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 985
- Mentions raw: 982
- Mentions scored: 975
- Evidence-invalid dropped: 7
- Evidence validity rate: 0.9929

## Overall Scores

### semantic

- per-item: P=0.413 R=0.437 F1=0.425 (TP=403 FP=572 FN=519)
- per-letter: P=0.865 R=0.610 F1=0.715 (TP=256 FP=40 FN=164)

### benchmark

- per-item: P=0.394 R=0.416 F1=0.405 (TP=384 FP=591 FN=538)
- per-letter: P=0.862 R=0.593 F1=0.702 (TP=249 FP=40 FN=171)

### phrase_only

- per-item: P=0.511 R=0.540 F1=0.525 (TP=498 FP=477 FN=424)
- per-letter: P=0.885 R=0.731 F1=0.800 (TP=307 FP=40 FN=113)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.744 P=0.736 R=0.752

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.850 | 0.852 | 0.848 | 173 | 30 | 31 |
| Diagnosis | 0.80 | 0.705 | 0.685 | 0.726 | 209 | 94 | 79 |
| SeizureFrequency | 0.80 | 0.604 | 0.577 | 0.634 | 109 | 80 | 63 |
| Investigations | 0.80 | 0.875 | 0.936 | 0.823 | 102 | 7 | 22 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.725 | 688 | 287 | 234 | 0.741 (510/688) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.669 | 176 | 0.710 (125/176) |
| Diagnosis | 0.735 | 275 | 0.873 (240/275) |
| SeizureFrequency | 0.661 | 129 | 0.364 (47/129) |
| Investigations | 0.927 | 108 | 0.907 (98/108) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.198 | 0.500 |
| Diagnosis | 0.80 | 0.85 | 0.596 | 0.945 |
| SeizureFrequency | 0.80 | 0.66 | 0.262 | 0.509 |
| Investigations | 0.80 | 0.95 | 0.661 | 0.806 |