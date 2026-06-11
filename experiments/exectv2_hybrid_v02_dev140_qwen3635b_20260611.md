# ExECTv2 Hybrid (candidate + assessment) — SeizureFrequency

- JSONL: `experiments\exectv2_hybrid_v02_dev140_qwen3635b_20260611.jsonl`
- Prompt version: `exectv2_hybrid_candidate_assessment_v0.2`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 140

## Gate & routing summary

- Call failures: 0
- Parse/schema failures: 1
- Candidates offered: 639
- Mentions kept by LLM: 313
- Mentions scored (post verify/route): 235
- Routed (excluded): 45
- Routed taxonomy: {'no_frequency_attributes': 25, 'bare_nonzero_count': 13, 'empty_evidence': 5, 'evidence_not_substring': 2}

## Scores

### phrase_only

  per-item: P=0.447 R=0.561 F1=0.498 (TP=105 FP=130 FN=82)
  per-letter: P=0.723 R=0.737 F1=0.730 (TP=73 FP=28 FN=26)

### sf_semantic

  per-item: P=0.204 R=0.257 F1=0.228 (TP=48 FP=187 FN=139)
  per-letter: P=0.569 R=0.374 F1=0.451 (TP=37 FP=28 FN=62)

### sf_benchmark

  per-item: P=0.204 R=0.257 F1=0.228 (TP=48 FP=187 FN=139)
  per-letter: P=0.569 R=0.374 F1=0.451 (TP=37 FP=28 FN=62)
