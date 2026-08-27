# DeepSeek unknown-competence thread

Date: 2026-07-31  
Status: Phase 2 candidate U **stopped (negative)** — insufficient UNK-slice gain; full-750 scale-up aborted  
Protocol: [gan2026_deepseek_unknown_competence_protocol_2026-07-31.md](../../experiments/gan2026/gan2026_deepseek_unknown_competence_protocol_2026-07-31.md)

## Decision

Open a bounded Gan research thread for **unknown handling** under the author
collaboration constraint:

- **Tune now on hosted DeepSeek V4 Flash** (matched-panel route);
- partner **local** DeepSeek arrives in ~weeks — re-smoke later, do not block
  hosted candidates;
- product arms: **LLM-only** and **LLM-with-rules** only;
- no rules-only arm;
- tune and select on `dev750` only;
- design for Real(300)-like unknown prevalence; do not tune on Real(300).

Current six-model / final-ruleset evidence is **not** collaboration-grade for
that constraint, especially DeepSeek LLM-only.

## Phase 0 result (hosted V4 Flash baseline)

Artifact:
[experiments/gan2026_deepseek_unknown_competence_baseline_dev750_20260731.json](../../experiments/gan2026_deepseek_unknown_competence_baseline_dev750_20260731.json)

On retained matched v0.5 `dev750` DeepSeek traces (gold UNK band n=170):

| Arm | UNK F1 | UNK acc | Over-read | False SF | Gate |
| --- | ---: | ---: | ---: | ---: | --- |
| LLM-only | ~0.70 | ~0.77 | ~0.04 | ~0.07 | Fail (acc &lt; 0.80) |
| LLM-with-rules (frozen panel) | ~0.81 | ~0.88 | ~0.07 | ~0.05 | Fail (acc, over-read, false SF) |
| LLM-with-rules (final-ruleset proxy) | ~0.83 | ~0.87 | ~0.07 | ~0.05 | Fail |

Hosted route only. Local DeepSeek parity is deferred (~weeks).

## Phase 2 result — candidate U stopped

Candidate U (`gan2026_hybrid_structured_events_v0.8_deepseek_unknown`) was
piloted on the gold Purist-UNK slice (n=170) only. Full `validation750`
scale-up was started and then **aborted** because the pilot gain was too small
to justify.

| Arm | Slice Purist | UNK acc | Over-read | False SF |
| --- | ---: | ---: | ---: | ---: |
| A LLM+rules | 148/170 | 0.876 | 0.071 | 0.053 |
| U LLM+rules | 150/170 | 0.882 | 0.083 | 0.036 |
| A LLM-only | — | 0.769 | 0.041 | 0.065 |
| U LLM-only | — | 0.746 | 0.024 | 0.041 |

Delta: **+2** final Purist; LLM-only UNK accuracy **worse**; false SF better;
over-read mixed. Collaboration gates not approached for LLM-only.

Artifact:
[experiments/gan2026_deepseek_unknown_heavy_slice_u_vs_a_20260731.json](../../experiments/gan2026_deepseek_unknown_heavy_slice_u_vs_a_20260731.json).
U rows retained under
`scratch/validation/gan2026_deepseek_unknown_prompt_dev750_20260731/U_deepseek_unknown/`
(**170 only**; incomplete scale-up checkpoints removed).

## Next executable action

Do **not** resume U to 750. Decide whether the unknown thread continues with a
different component (new prompt cycle with a sharper target, or Phase 3
unknown-preserving rules gate) or pauses until local DeepSeek arrives. Keep
sealed `test450` / Real(300) unused for tuning.

## Claim boundary

Development thread for DeepSeek unknown competence. Hosted U pilot is a
bounded negative for this prompt candidate. Not Real(300) evidence, not
holdout tuning, not ExECT transfer, not six-model promotion.
