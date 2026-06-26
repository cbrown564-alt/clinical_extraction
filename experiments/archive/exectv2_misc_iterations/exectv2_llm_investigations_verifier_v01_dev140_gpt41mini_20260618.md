# ExECTv2 Investigations Verifier

- JSONL: `experiments\exectv2_llm_investigations_verifier_v01_dev140_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_llm_investigations_verifier_v0.1`
- Pipeline family: `exectv2_llm_investigations_verifier`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Draft Investigations mentions: 150
- Mentions raw: 138
- Mentions scored: 137
- Evidence-invalid dropped: 1
- Evidence validity rate: 0.9928

## Investigations Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.872 | 0.869 | 0.875 | 119 | 18 | 17 |
