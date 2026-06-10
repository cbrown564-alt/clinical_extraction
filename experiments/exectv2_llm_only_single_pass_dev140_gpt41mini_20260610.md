# ExECTv2 LLM-Only Single-Pass — SeizureFrequency

- JSONL: `experiments\exectv2_llm_only_single_pass_dev140_gpt41mini_20260610.jsonl`
- Prompt version: `exectv2_llm_only_single_pass_v0.2`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 199
- Mentions scored (evidence-valid): 195
- Evidence-invalid dropped: 4
- Evidence validity rate: 0.9799

## Scores

### phrase_only

  per-item: P=0.456 R=0.476 F1=0.466 (TP=89 FP=106 FN=98)
  per-letter: P=0.704 R=0.697 F1=0.701 (TP=69 FP=29 FN=30)

### sf_semantic

  per-item: P=0.092 R=0.096 F1=0.094 (TP=18 FP=177 FN=169)
  per-letter: P=0.326 R=0.141 F1=0.197 (TP=14 FP=29 FN=85)

### sf_benchmark

  per-item: P=0.000 R=0.000 F1=0.000 (TP=0 FP=195 FN=187)
  per-letter: P=0.000 R=0.000 F1=0.000 (TP=0 FP=29 FN=99)
