# ExECTv2 Diagnosis Heading/Narrative Decomposer

- JSONL: `experiments\exectv2_2call_no_sf_model_swap_qwen36_repair_v02_full200_20260626_diagnosis_decomposer.jsonl`
- Prompt version: `exectv2_hybrid_diagnosis_decomposer_v0.1`
- Pipeline family: `exectv2_hybrid_diagnosis_decomposer`
- Split: `full200`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 200

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Draft Diagnosis mentions: 415
- Diagnosis spans: 1087
- Mentions raw: 622
- Mentions scored: 621
- Evidence-invalid dropped: 1
- Evidence validity rate: 0.9984

## Diagnosis Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.666 | 0.666 | 0.666 | 293 | 147 | 147 |

## Source-Near Diagnostic

- Overlap F1=0.769 R=0.802
