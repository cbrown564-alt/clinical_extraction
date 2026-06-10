# ExECTv2 LLM-Only Single-Pass — SeizureFrequency

- JSONL: `experiments\exectv2_llm_only_single_pass_pilot25_gpt41mini_v02_2026-06-10.jsonl`
- Prompt version: `exectv2_llm_only_single_pass_v0.2`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 29
- Mentions scored (evidence-valid): 29
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Scores

### phrase_only

  per-item: P=0.379 R=0.355 F1=0.367 (TP=11 FP=18 FN=20)
  per-letter: P=0.600 R=0.600 F1=0.600 (TP=9 FP=6 FN=6)

### sf_semantic

  per-item: P=0.000 R=0.000 F1=0.000 (TP=0 FP=29 FN=31)
  per-letter: P=0.000 R=0.000 F1=0.000 (TP=0 FP=6 FN=15)

### sf_benchmark

  per-item: P=0.000 R=0.000 F1=0.000 (TP=0 FP=29 FN=31)
  per-letter: P=0.000 R=0.000 F1=0.000 (TP=0 FP=6 FN=15)

---

## Rescored — D16 gold repair (2026-06-10)

Gold `text` replaced with `CUIPhrase` (clean canonical term) per discovery D16.
The run JSONL and predictions are unchanged; only the matching target is corrected.
Original scores above were against the raw col5 covered span (offset-drift–corrupted).

### phrase_only (rescored)

  per-item: P=0.655 R=0.613 F1=0.633 (TP=19 FP=10 FN=12)
  per-letter: P=0.684 R=0.867 F1=0.765 (TP=13 FP=6 FN=2)

### sf_semantic (rescored)

  per-item: P=0.069 R=0.065 F1=0.067 (TP=2 FP=27 FN=29)
  per-letter: P=0.250 R=0.133 F1=0.174 (TP=2 FP=6 FN=13)

### sf_benchmark (rescored)

  per-item: P=0.000 R=0.000 F1=0.000 (TP=0 FP=29 FN=31)
  per-letter: P=0.000 R=0.000 F1=0.000 (TP=0 FP=6 FN=15)

### Notes

- **phrase_only F1 0.367 → 0.633** per-item (+0.266), **0.600 → 0.765** per-letter (+0.165).
  D16 was masking strong phrase matching: 8 model-correct phrases (e.g. `focal seizures with
  altered awareness`) scored against truncated gold (`focal-seizures-with-altered-awarenes`).
- **phrase_only 0.765 per-letter exceeds the SF benchmark target (0.68)**. Per-item 0.633
  is near the 0.66 per-item target — within reach with attribute improvements.
- **sf_semantic 0.000 → 0.067**: 2 TPs now visible — EA0009 (range + period bundle) and
  EA0025 (FrequencyChange=Frequent). The gap to gold is attribute-convention mismatches
  (MonthDate numeric vs name, range vs single count, extra/missing keys) — not phrase errors.
- **sf_benchmark = 0.000**: LLM does not emit CUI values (expected; D3 — CUI is a
  post-step lookup, not a per-architecture task).
- Deterministic baseline for comparison (dev, repaired gold): phrase_only per-item 0.485 /
  per-letter 0.604. LLM single-pass pilot beats it on both axes at N=25.
