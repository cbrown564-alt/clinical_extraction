# Paired Purist tests on Gan `test450` and Gemini temperature on both splits

Date: 2026-08-29
Status: complete
Protocol: [gan_paired_significance_test450_protocol_2026-08-29.md](gan_paired_significance_test450_protocol_2026-08-29.md)
Owner: this file
Artifact: `paper_experiments/gan/paired_significance/gemini37flash/test450/comparison.json`

## Answer

On locked `test450`, living Gemini cell 3 (374/450) beats standalone
rules (325/450) and beats all-model cell 5 (357/450). Gemini
temperature 0 versus 1 is compatible with no difference on both
splits (`test450` select 0.831 vs 0.824; `dev750` 0.865 vs 0.867).
Living thinking versus high (select 0.831 vs 0.818) is also
compatible with no difference. Medium thinking stays a point estimate.

## Method

Exact two-sided McNemar on paired Purist correctness. Wald 95% CI
on the accuracy difference. No new model calls. Holdout output is
discordant counts only.

Thinking framing: one contrast on `test450`, **low versus high at
cell-3 select**. High is the extra-budget setting. The test asks
whether extra reasoning beat the living select score, not whether
find moved.

Temperature framing: one question, **both splits**. `dev750` uses
saved cell-3 rung select flags (649 vs 650).

Cell 3 is the living codebook replay. Table 1 still cites 373/450.
Do not retune from that one-count gap.

## Results

| Contrast | Split | A | B | A only | B only | Δ accuracy (95% CI) | Exact *p* |
| --- | --- | ---: | ---: | ---: | ---: | --- | ---: |
| Cell 3 vs rules | `test450` | 374 | 325 | 92 | 43 | +0.109 [0.059, 0.159] | 3.0×10⁻⁵ |
| Cell 3 vs cell 5 | `test450` | 374 | 357 | 27 | 10 | +0.038 [0.012, 0.064] | 0.0076 |
| Gemini temperature 0 vs 1 | `test450` | 374 | 371 | 16 | 13 | +0.007 [−0.017, 0.030] | 0.71 |
| Gemini temperature 0 vs 1 | `dev750` | 649 | 650 | 12 | 13 | −0.001 [−0.014, 0.012] | 1.00 |
| Gemini thinking low vs high | `test450` | 374 | 368 | 20 | 14 | +0.013 [−0.012, 0.039] | 0.39 |

The holdout Table 1 tests and the two-split temperature family were
predeclared. Holm–Bonferroni does not change which intervals exclude
zero.

## Bound

This is a paired accuracy comparison with the Gan gold. It is not a
claim that later rules are causally necessary on named holdout
letters, that cell 3 is unique among the 0.82 hybrids, or that
temperature and thinking are equivalent in a formal TOST sense.
The temperature and thinking intervals include both a small gain
and a small loss.
