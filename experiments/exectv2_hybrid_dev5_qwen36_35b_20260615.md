# ExECTv2 Hybrid (candidate + assessment) — SeizureFrequency

- JSONL: `experiments\exectv2_hybrid_dev5_qwen36_35b_20260615.jsonl`
- Prompt version: `exectv2_hybrid_candidate_assessment_v0.2`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 5

## Gate & routing summary

- Call failures: 0
- Parse/schema failures: 0
- Candidates offered: 40
- Mentions kept by LLM: 16
- Mentions scored (post verify/route): 14
- Routed (excluded): 2
- Routed taxonomy: {'no_frequency_attributes': 2}

## Scores

### phrase_only

  per-item: P=0.429 R=0.545 F1=0.480 (TP=6 FP=8 FN=5)
  per-letter: P=1.000 R=0.600 F1=0.750 (TP=3 FP=0 FN=2)

### sf_semantic

  per-item: P=0.429 R=0.545 F1=0.480 (TP=6 FP=8 FN=5)
  per-letter: P=1.000 R=0.600 F1=0.750 (TP=3 FP=0 FN=2)

### sf_benchmark

  per-item: P=0.429 R=0.545 F1=0.480 (TP=6 FP=8 FN=5)
  per-letter: P=1.000 R=0.600 F1=0.750 (TP=3 FP=0 FN=2)
