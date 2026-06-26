# ExECTv2 LLM-Only Single-Pass — SeizureFrequency

- JSONL: `experiments\exectv2_llm_only_per_entity_dev140_gpt41mini_20260610.jsonl`
- Prompt version: `exectv2_llm_only_per_entity_v0.2`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 190
- Mentions scored (evidence-valid): 183
- Evidence-invalid dropped: 7
- Evidence validity rate: 0.9632

## Scores

### phrase_only

  per-item: P=0.492 R=0.481 F1=0.486 (TP=90 FP=93 FN=97)
  per-letter: P=0.720 R=0.677 F1=0.698 (TP=67 FP=26 FN=32)

### sf_semantic

  per-item: P=0.137 R=0.134 F1=0.135 (TP=25 FP=158 FN=162)
  per-letter: P=0.422 R=0.192 F1=0.264 (TP=19 FP=26 FN=80)

### sf_benchmark

  per-item: P=0.000 R=0.000 F1=0.000 (TP=0 FP=183 FN=187)
  per-letter: P=0.000 R=0.000 F1=0.000 (TP=0 FP=26 FN=99)
