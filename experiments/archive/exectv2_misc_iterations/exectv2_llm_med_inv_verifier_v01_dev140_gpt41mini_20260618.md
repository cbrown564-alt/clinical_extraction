# ExECTv2 Prescription/Investigations Verifier

- JSONL: `experiments\exectv2_llm_med_inv_verifier_v01_dev140_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_llm_med_inv_verifier_v0.1`
- Pipeline family: `exectv2_llm_med_inv_verifier`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Draft mentions: 419
- Mentions raw: 384
- Mentions scored: 376
- Evidence-invalid dropped: 8
- Evidence validity rate: 0.9792

## Clinical-Recovery Headlines

| Entity | Target F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.817 | 0.773 | 0.865 | 167 | 49 | 26 |
| Investigations | 0.80 | 0.496 | 0.408 | 0.632 | 86 | 125 | 50 |
