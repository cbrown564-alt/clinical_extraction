# ExECTv2 LLM-Only Single-Pass — SeizureFrequency

- JSONL: `experiments\exectv2_llm_only_single_dev25_qwen36_35b_20260615.jsonl`
- Prompt version: `exectv2_llm_only_single_pass_v0.2`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 31
- Mentions scored (evidence-valid): 29
- Evidence-invalid dropped: 2
- Evidence validity rate: 0.9355

## Scores

### phrase_only

  per-item: P=0.552 R=0.516 F1=0.533 (TP=16 FP=13 FN=15)
  per-letter: P=0.750 R=0.800 F1=0.774 (TP=12 FP=4 FN=3)

### sf_semantic

  per-item: P=0.103 R=0.097 F1=0.100 (TP=3 FP=26 FN=28)
  per-letter: P=0.429 R=0.200 F1=0.273 (TP=3 FP=4 FN=12)

### sf_benchmark

  per-item: P=0.000 R=0.000 F1=0.000 (TP=0 FP=29 FN=31)
  per-letter: P=0.000 R=0.000 F1=0.000 (TP=0 FP=4 FN=15)
