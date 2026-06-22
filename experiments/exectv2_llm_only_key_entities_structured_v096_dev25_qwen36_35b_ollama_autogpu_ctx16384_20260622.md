# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v096_dev25_qwen36_35b_ollama_autogpu_ctx16384_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.6`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 1
- Clinical events raw: 134
- Mentions raw: 150
- Mentions scored: 144
- Evidence-invalid dropped: 6
- Evidence validity rate: 0.9600

## Overall Scores

### semantic

- per-item: P=0.292 R=0.288 F1=0.290 (TP=42 FP=102 FN=104)
- per-letter: P=0.825 R=0.465 F1=0.595 (TP=33 FP=7 FN=38)

### benchmark

- per-item: P=0.292 R=0.288 F1=0.290 (TP=42 FP=102 FN=104)
- per-letter: P=0.825 R=0.465 F1=0.595 (TP=33 FP=7 FN=38)

### phrase_only

- per-item: P=0.493 R=0.486 F1=0.490 (TP=71 FP=73 FN=75)
- per-letter: P=0.870 R=0.662 F1=0.752 (TP=47 FP=7 FN=24)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.789 | 0.789 | 0.789 | 30 | 8 | 8 |
| Diagnosis | 0.80 | 0.721 | 0.705 | 0.738 | 31 | 13 | 11 |
| SeizureFrequency | 0.80 | 0.643 | 0.600 | 0.692 | 18 | 12 | 8 |
| Investigations | 0.80 | 0.950 | 0.950 | 0.950 | 19 | 1 | 1 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.772 | 112 | 32 | 34 | 0.643 (72/112) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.780 | 32 | 0.812 (26/32) |
| Diagnosis | 0.781 | 41 | 0.488 (20/41) |
| SeizureFrequency | 0.677 | 21 | 0.429 (9/21) |
| Investigations | 0.878 | 18 | 0.944 (17/18) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.195 | 0.500 |
| Diagnosis | 0.80 | 0.85 | 0.305 | 0.706 |
| SeizureFrequency | 0.80 | 0.66 | 0.226 | 0.444 |
| Investigations | 0.80 | 0.95 | 0.537 | 0.727 |