# ExECTv2 LLM-Only Single-Pass — SeizureFrequency

- JSONL: `experiments\exectv2_llm_only_per_entity_dev140_qwen3635b_20260610.jsonl`
- Prompt version: `exectv2_llm_only_per_entity_v0.2`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 205
- Mentions scored (evidence-valid): 197
- Evidence-invalid dropped: 8
- Evidence validity rate: 0.9610

## Scores

### phrase_only

  per-item: P=0.391 R=0.412 F1=0.401 (TP=77 FP=120 FN=110)
  per-letter: P=0.682 R=0.606 F1=0.642 (TP=60 FP=28 FN=39)

### sf_semantic

  per-item: P=0.035 R=0.037 F1=0.036 (TP=7 FP=190 FN=180)
  per-letter: P=0.200 R=0.071 F1=0.104 (TP=7 FP=28 FN=92)

### sf_benchmark

  per-item: P=0.000 R=0.000 F1=0.000 (TP=0 FP=197 FN=187)
  per-letter: P=0.000 R=0.000 F1=0.000 (TP=0 FP=28 FN=99)
