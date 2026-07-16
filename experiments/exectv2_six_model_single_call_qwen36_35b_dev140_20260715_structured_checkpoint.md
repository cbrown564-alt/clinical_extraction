# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 140 / 140 letters

- JSONL: `experiments\exectv2_six_model_single_call_qwen36_35b_dev140_20260715_structured.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev140`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 5
- Clinical events raw: 766
- Mentions raw: 832
- Mentions scored: 831
- Evidence-invalid dropped: 1
- Evidence validity rate: 0.9988

## Overall Scores

### semantic

- per-item: P=0.434 R=0.387 F1=0.409 (TP=361 FP=470 FN=573)
- per-letter: P=0.830 R=0.569 F1=0.675 (TP=239 FP=49 FN=181)

### benchmark

- per-item: P=0.413 R=0.367 F1=0.389 (TP=343 FP=488 FN=591)
- per-letter: P=0.826 R=0.555 F1=0.664 (TP=233 FP=49 FN=187)

### phrase_only

- per-item: P=0.525 R=0.467 F1=0.494 (TP=436 FP=395 FN=498)
- per-letter: P=0.853 R=0.679 F1=0.756 (TP=285 FP=49 FN=135)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.753 P=0.762 R=0.745

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.879 | 0.857 | 0.903 | 186 | 31 | 20 |
| Diagnosis | 0.80 | 0.678 | 0.696 | 0.660 | 196 | 85 | 101 |
| SeizureFrequency | 0.80 | 0.642 | 0.624 | 0.661 | 111 | 67 | 57 |
| Investigations | 0.80 | 0.871 | 0.964 | 0.794 | 108 | 4 | 28 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.749 | 661 | 170 | 273 | 0.767 (507/661) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.822 | 180 | 0.761 (137/180) |
| Diagnosis | 0.688 | 243 | 0.864 (210/243) |
| SeizureFrequency | 0.686 | 128 | 0.445 (57/128) |
| Investigations | 0.887 | 110 | 0.936 (103/110) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.228 | 0.461 |
| Diagnosis | 0.80 | 0.85 | 0.538 | 0.893 |
| SeizureFrequency | 0.80 | 0.66 | 0.241 | 0.467 |
| Investigations | 0.80 | 0.95 | 0.613 | 0.803 |