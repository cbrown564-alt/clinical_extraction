# ExECTv2 Investigations Verifier

- JSONL: `experiments\exectv2_v08_full200_currentcode_investigations_verifier_gpt41mini_20260624.jsonl`
- Prompt version: `exectv2_llm_investigations_verifier_v0.1`
- Pipeline family: `exectv2_llm_investigations_verifier`
- Split: `full_200_authorized`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 200

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Draft Investigations mentions: 158
- Mentions raw: 191
- Mentions scored: 187
- Evidence-invalid dropped: 4
- Evidence validity rate: 0.9791

## Investigations Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.877 | 0.859 | 0.896 | 164 | 27 | 19 |
