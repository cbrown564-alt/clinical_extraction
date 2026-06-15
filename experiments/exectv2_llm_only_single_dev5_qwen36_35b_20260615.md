# ExECTv2 LLM-Only Single-Pass — SeizureFrequency

- JSONL: `experiments\exectv2_llm_only_single_dev5_qwen36_35b_20260615.jsonl`
- Prompt version: `exectv2_llm_only_single_pass_v0.2`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 5

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 8
- Mentions scored (evidence-valid): 8
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Scores

### phrase_only

  per-item: P=0.875 R=0.636 F1=0.737 (TP=7 FP=1 FN=4)
  per-letter: P=1.000 R=1.000 F1=1.000 (TP=5 FP=0 FN=0)

### sf_semantic

  per-item: P=0.125 R=0.091 F1=0.105 (TP=1 FP=7 FN=10)
  per-letter: P=1.000 R=0.200 F1=0.333 (TP=1 FP=0 FN=4)

### sf_benchmark

  per-item: P=0.000 R=0.000 F1=0.000 (TP=0 FP=8 FN=11)
  per-letter: P=0.000 R=0.000 F1=0.000 (TP=0 FP=0 FN=5)
