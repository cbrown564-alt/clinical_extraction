# ExECTv2 LLM-Only Single-Pass — SeizureFrequency

- JSONL: `experiments\exectv2_llm_only_single_pass_dev140_qwen3635b_20260610.jsonl`
- Prompt version: `exectv2_llm_only_single_pass_v0.2`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 2
- Mentions raw: 200
- Mentions scored (evidence-valid): 189
- Evidence-invalid dropped: 11
- Evidence validity rate: 0.9450

## Scores

### phrase_only

  per-item: P=0.381 R=0.385 F1=0.383 (TP=72 FP=117 FN=115)
  per-letter: P=0.679 R=0.576 F1=0.623 (TP=57 FP=27 FN=42)

### sf_semantic

  per-item: P=0.090 R=0.091 F1=0.090 (TP=17 FP=172 FN=170)
  per-letter: P=0.357 R=0.151 F1=0.213 (TP=15 FP=27 FN=84)

### sf_benchmark

  per-item: P=0.000 R=0.000 F1=0.000 (TP=0 FP=189 FN=187)
  per-letter: P=0.000 R=0.000 F1=0.000 (TP=0 FP=27 FN=99)
