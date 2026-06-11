# ExECTv2 Hybrid (candidate + assessment) — SeizureFrequency

- JSONL: `experiments\exectv2_hybrid_v02_dev140_gpt41mini_20260611.jsonl`
- Prompt version: `exectv2_hybrid_candidate_assessment_v0.2`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140

## Gate & routing summary

- Call failures: 0
- Parse/schema failures: 0
- Candidates offered: 639
- Mentions kept by LLM: 288
- Mentions scored (post verify/route): 247
- Routed (excluded): 37
- Routed taxonomy: {'no_frequency_attributes': 7, 'bare_nonzero_count': 29, 'evidence_not_substring': 1}

## Scores

### phrase_only

  per-item: P=0.514 R=0.679 F1=0.585 (TP=127 FP=120 FN=60)
  per-letter: P=0.739 R=0.828 F1=0.781 (TP=82 FP=29 FN=17)

### sf_semantic

  per-item: P=0.287 R=0.380 F1=0.327 (TP=71 FP=176 FN=116)
  per-letter: P=0.642 R=0.525 F1=0.578 (TP=52 FP=29 FN=47)

### sf_benchmark

  per-item: P=0.287 R=0.380 F1=0.327 (TP=71 FP=176 FN=116)
  per-letter: P=0.642 R=0.525 F1=0.578 (TP=52 FP=29 FN=47)
