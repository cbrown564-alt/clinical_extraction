# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_2call_no_sf_model_swap_deepseek_full200_20260625_structured.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `full200`
- Model: `deepseek/deepseek-chat`
- Mode: `live`
- Letters: 200

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 1282
- Mentions raw: 1313
- Mentions scored: 1286
- Evidence-invalid dropped: 27
- Evidence validity rate: 0.9794

## Overall Scores

### semantic

- per-item: P=0.478 R=0.469 F1=0.473 (TP=615 FP=671 FN=697)
- per-letter: P=0.876 R=0.633 F1=0.735 (TP=383 FP=54 FN=222)

### benchmark

- per-item: P=0.456 R=0.447 F1=0.451 (TP=586 FP=700 FN=726)
- per-letter: P=0.874 R=0.617 F1=0.723 (TP=373 FP=54 FN=232)

### phrase_only

- per-item: P=0.570 R=0.559 F1=0.564 (TP=733 FP=553 FN=579)
- per-letter: P=0.893 R=0.747 F1=0.814 (TP=452 FP=54 FN=153)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.774 P=0.749 R=0.800

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.848 | 0.792 | 0.912 | 248 | 65 | 24 |
| Diagnosis | 0.80 | 0.726 | 0.707 | 0.745 | 313 | 127 | 107 |
| SeizureFrequency | 0.80 | 0.681 | 0.633 | 0.736 | 178 | 103 | 64 |
| Investigations | 0.80 | 0.909 | 0.981 | 0.847 | 155 | 3 | 28 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.804 | 1045 | 241 | 267 | 0.774 (809/1045) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.842 | 267 | 0.757 (202/267) |
| Diagnosis | 0.784 | 417 | 0.880 (367/417) |
| SeizureFrequency | 0.734 | 205 | 0.424 (87/205) |
| Investigations | 0.915 | 156 | 0.981 (153/156) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.265 | 0.540 |
| Diagnosis | 0.80 | 0.85 | 0.622 | 0.933 |
| SeizureFrequency | 0.80 | 0.66 | 0.297 | 0.537 |
| Investigations | 0.80 | 0.95 | 0.686 | 0.865 |