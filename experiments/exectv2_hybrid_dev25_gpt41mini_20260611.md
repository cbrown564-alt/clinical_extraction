# ExECTv2 Hybrid (candidate + assessment) — SeizureFrequency

- JSONL: `experiments\exectv2_hybrid_dev25_gpt41mini_20260611.jsonl`
- Prompt version: `exectv2_hybrid_candidate_assessment_v0.1`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25

## Gate & routing summary

- Call failures: 0
- Parse/schema failures: 0
- Candidates offered: 103
- Mentions kept by LLM: 49
- Mentions scored (post verify/route): 46
- Routed (excluded): 3
- Routed taxonomy: {'bare_nonzero_count': 3}

## Scores

### phrase_only

  per-item: P=0.565 R=0.839 F1=0.675 (TP=26 FP=20 FN=5)
  per-letter: P=0.714 R=1.000 F1=0.833 (TP=15 FP=6 FN=0)

### sf_semantic

  per-item: P=0.239 R=0.355 F1=0.286 (TP=11 FP=35 FN=20)
  per-letter: P=0.600 R=0.600 F1=0.600 (TP=9 FP=6 FN=6)

### sf_benchmark

  per-item: P=0.239 R=0.355 F1=0.286 (TP=11 FP=35 FN=20)
  per-letter: P=0.600 R=0.600 F1=0.600 (TP=9 FP=6 FN=6)
