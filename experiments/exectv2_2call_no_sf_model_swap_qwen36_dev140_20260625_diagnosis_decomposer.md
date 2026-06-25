# ExECTv2 Diagnosis Heading/Narrative Decomposer

- JSONL: `experiments\exectv2_2call_no_sf_model_swap_qwen36_dev140_20260625_diagnosis_decomposer.jsonl`
- Prompt version: `exectv2_hybrid_diagnosis_decomposer_v0.1`
- Pipeline family: `exectv2_hybrid_diagnosis_decomposer`
- Split: `dev140`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 11
- Draft Diagnosis mentions: 292
- Diagnosis spans: 788
- Mentions raw: 390
- Mentions scored: 386
- Evidence-invalid dropped: 4
- Evidence validity rate: 0.9897

## Diagnosis Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.642 | 0.680 | 0.609 | 185 | 87 | 119 |

## Source-Near Diagnostic

- Overlap F1=0.703 R=0.686
