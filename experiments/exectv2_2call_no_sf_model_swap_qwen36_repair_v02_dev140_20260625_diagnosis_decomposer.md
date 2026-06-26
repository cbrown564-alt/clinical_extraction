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
- Draft Diagnosis mentions: 280
- Diagnosis spans: 775
- Mentions raw: 437
- Mentions scored: 437
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Diagnosis Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.691 | 0.687 | 0.694 | 211 | 96 | 93 |

## Source-Near Diagnostic

- Overlap F1=0.765 R=0.795
