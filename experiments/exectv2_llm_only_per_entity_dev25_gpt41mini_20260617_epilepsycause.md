# ExECTv2 LLM-Only Per-Entity — EpilepsyCause

- JSONL: `experiments\exectv2_llm_only_per_entity_dev25_gpt41mini_20260617_epilepsycause.jsonl`
- Prompt version: `exectv2_llm_only_per_entity_v0.4`
- Entity: `EpilepsyCause`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25
- Published per-item F1 target: 0.90

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 7
- Mentions scored (evidence-valid): 7
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Format Layers

| Layer | Item F1 | Item P | Item R | Letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.222 | 0.143 | 0.500 | 0.250 | 1 | 6 | 1 |
| semantic | 0.222 | 0.143 | 0.500 | 0.250 | 1 | 6 | 1 |
| benchmark | 0.222 | 0.143 | 0.500 | 0.250 | 1 | 6 | 1 |

## Source-Near Candidate Diagnostic (format-blind)

- Overlap recall: 1.000 (TP=2 FN=0)
- Overlap F1: 0.444
- Over-emission (overlap FP): 5
- Attribute agreement on overlaps: 0.500 (1/2)
