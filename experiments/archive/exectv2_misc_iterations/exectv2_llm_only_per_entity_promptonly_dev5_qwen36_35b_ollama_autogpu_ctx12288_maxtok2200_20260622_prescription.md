# ExECTv2 LLM-Only Per-Entity — Prescription

- JSONL: `experiments\exectv2_llm_only_per_entity_promptonly_dev5_qwen36_35b_ollama_autogpu_ctx12288_maxtok2200_20260622_prescription.jsonl`
- Prompt version: `exectv2_llm_only_per_entity_v0.4`
- Entity: `Prescription`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `prompt-only`
- Letters: 5
- Published per-item F1 target: 0.87

## Gate Summary

- Call failures: 0
- Parse/schema failures: 5
- Mentions raw: 0
- Mentions scored (evidence-valid): 0
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Format Layers

| Layer | Item F1 | Item P | Item R | Letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.000 | 0.000 | 0.000 | 0.000 | 0 | 0 | 9 |
| semantic | 0.000 | 0.000 | 0.000 | 0.000 | 0 | 0 | 9 |
| benchmark | 0.000 | 0.000 | 0.000 | 0.000 | 0 | 0 | 9 |

## Source-Near Candidate Diagnostic (format-blind)

- Overlap recall: 0.000 (TP=0 FN=9)
- Overlap F1: 0.000
- Over-emission (overlap FP): 0
- Attribute agreement on overlaps: 0.000 (0/0)
