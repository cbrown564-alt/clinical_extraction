# ExECTv2 Hybrid (candidate + assessment) — SeizureFrequency

- JSONL: `experiments\exectv2_hybrid_dev140_gpt41mini_20260611.jsonl`
- Prompt version: `exectv2_hybrid_candidate_assessment_v0.1`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140

## Gate & routing summary

- Call failures: 0
- Parse/schema failures: 1
- Candidates offered: 639
- Mentions kept by LLM: 290
- Mentions scored (post verify/route): 260
- Routed (excluded): 24
- Routed taxonomy: {'bare_nonzero_count': 19, 'evidence_not_substring': 1, 'no_frequency_attributes': 4}

## Scores

### phrase_only

  per-item: P=0.496 R=0.690 F1=0.577 (TP=129 FP=131 FN=58)
  per-letter: P=0.741 R=0.838 F1=0.787 (TP=83 FP=29 FN=16)

### sf_semantic

  per-item: P=0.200 R=0.278 F1=0.233 (TP=52 FP=208 FN=135)
  per-letter: P=0.580 R=0.404 F1=0.476 (TP=40 FP=29 FN=59)

### sf_benchmark

  per-item: P=0.200 R=0.278 F1=0.233 (TP=52 FP=208 FN=135)
  per-letter: P=0.580 R=0.404 F1=0.476 (TP=40 FP=29 FN=59)
