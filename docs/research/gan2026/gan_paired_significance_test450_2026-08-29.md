# Paired Purist tests on Gan `test450` and Gemini temperature on both splits

Date: 2026-08-29
Revised: 2026-08-31 (cited cell 5 is 383/450)
Status: complete
Protocol: [gan_paired_significance_test450_protocol_2026-08-29.md](gan_paired_significance_test450_protocol_2026-08-29.md)
Owner: this file
Artifact: `paper_experiments/gan/paired_significance/gemini37flash/test450/comparison.json`

## Answer

On locked `test450`, living Gemini cell 3 (387/450) beats standalone
rules (325/450). Versus all-model cell 5 (383/450) the difference
is compatible with no difference. Gemini
temperature 0 versus 1 is compatible with no difference on both
splits (`test450` select 0.860 vs 0.842; `dev750` 0.875 vs 0.875).
Living thinking versus high (select 0.860 vs 0.844) is also
compatible with no difference. Medium thinking stays a point estimate
on the prior stack.

## Method

Exact two-sided McNemar on paired Purist correctness. Wald 95% CI
on the accuracy difference. No new model calls. Holdout output is
discordant counts only.

Thinking framing: one contrast on `test450`, **low versus high at
cell-3 select**. High is the extra-budget setting. The test asks
whether extra reasoning beat the living select score, not whether
find moved.

Temperature framing: one question, **both splits**. Both splits
replay saved extracts through living `llm_select_after_codebook`.

Cell 3 is the living codebook replay. Table 1 cites 387/450.

## Results

| Contrast | Split | A | B | A only | B only | Δ accuracy (95% CI) | Exact *p* |
| --- | --- | ---: | ---: | ---: | ---: | --- | ---: |
| Cell 3 vs rules | `test450` | 387 | 325 | 99 | 37 | +0.138 [0.089, 0.187] | 1.0×10⁻⁷ |
| Cell 3 vs cell 5 | `test450` | 387 | 383 | 16 | 12 | +0.009 [−0.014, 0.032] | 0.57 |
| Gemini temperature 0 vs 1 | `test450` | 387 | 379 | 19 | 11 | +0.018 [−0.006, 0.042] | 0.20 |
| Gemini temperature 0 vs 1 | `dev750` | 656 | 656 | 13 | 13 | 0.000 [−0.013, 0.013] | 1.00 |
| Gemini thinking low vs high | `test450` | 387 | 380 | 21 | 14 | +0.016 [−0.010, 0.041] | 0.31 |

The holdout Table 1 tests and the two-split temperature family were
predeclared. Holm–Bonferroni does not change which intervals exclude
zero.

## Bound

This is a paired accuracy comparison with the Gan gold. It is not a
claim that later rules are causally necessary on named holdout
letters, that cell 3 is unique among the nearby hybrids, or that
temperature and thinking are equivalent in a formal TOST sense.
The temperature and thinking intervals include both a small gain
and a small loss.
