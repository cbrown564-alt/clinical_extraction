# ExECTv2 Diagnosis Heading/Narrative Decomposer

- JSONL: `experiments\exectv2_2call_no_sf_model_swap_qwen36_repair_v02_dev140_20260625_diagnosis_decomposer.jsonl`
- Prompt version: `exectv2_hybrid_diagnosis_decomposer_v0.1`
- Pipeline family: `exectv2_hybrid_diagnosis_decomposer`
- Split: `dev140`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Draft Diagnosis mentions: 75
- Diagnosis spans: 175
- Mentions raw: 125
- Mentions scored: 125
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Diagnosis Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.749 | 0.685 | 0.824 | 61 | 28 | 13 |

## Source-Near Diagnostic

- Overlap F1=0.793 R=0.882
