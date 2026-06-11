# ExECTv2 Hybrid (candidate + assessment) — SeizureFrequency

- JSONL: `experiments\exectv2_hybrid_v02_dev140_qwen3635b_20260611.jsonl`
- Prompt version: `exectv2_hybrid_candidate_assessment_v0.2`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 50

## Gate & routing summary

- Call failures: 0
- Parse/schema failures: 0
- Candidates offered: 240
- Mentions kept by LLM: 126
- Mentions scored (post verify/route): 89
- Routed (excluded): 21
- Routed taxonomy: {'no_frequency_attributes': 14, 'bare_nonzero_count': 3, 'empty_evidence': 4}

## Scores

### phrase_only

  per-item: P=0.539 R=0.667 F1=0.596 (TP=48 FP=41 FN=24)
  per-letter: P=0.784 R=0.853 F1=0.817 (TP=29 FP=8 FN=5)

### sf_semantic

  per-item: P=0.270 R=0.333 F1=0.298 (TP=24 FP=65 FN=48)
  per-letter: P=0.667 R=0.471 F1=0.552 (TP=16 FP=8 FN=18)

### sf_benchmark

  per-item: P=0.270 R=0.333 F1=0.298 (TP=24 FP=65 FN=48)
  per-letter: P=0.667 R=0.471 F1=0.552 (TP=16 FP=8 FN=18)
