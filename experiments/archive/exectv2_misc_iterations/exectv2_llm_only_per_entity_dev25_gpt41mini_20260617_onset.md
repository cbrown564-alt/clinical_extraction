# ExECTv2 LLM-Only Per-Entity — Onset

- JSONL: `experiments\exectv2_llm_only_per_entity_dev25_gpt41mini_20260617_onset.jsonl`
- Prompt version: `exectv2_llm_only_per_entity_v0.4`
- Entity: `Onset`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25
- Published per-item F1 target: 0.96

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 21
- Mentions scored (evidence-valid): 19
- Evidence-invalid dropped: 2
- Evidence validity rate: 0.9048

## Format Layers

| Layer | Item F1 | Item P | Item R | Letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.100 | 0.053 | 1.000 | 0.154 | 1 | 18 | 0 |
| semantic | 0.100 | 0.053 | 1.000 | 0.154 | 1 | 18 | 0 |
| benchmark | 0.100 | 0.053 | 1.000 | 0.154 | 1 | 18 | 0 |

## Source-Near Candidate Diagnostic (format-blind)

- Overlap recall: 1.000 (TP=1 FN=0)
- Overlap F1: 0.100
- Over-emission (overlap FP): 18
- Attribute agreement on overlaps: 1.000 (1/1)
