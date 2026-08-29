# Protocol: paired Purist tests on Gan `test450` and Gemini temperature on both splits

Date: 2026-08-29
Status: complete; report
[gan_paired_significance_test450_2026-08-29.md](gan_paired_significance_test450_2026-08-29.md)
Owner: this file

## Question

On locked `test450`, are the two Table 1 claims and the Gemini
thinking ablation distinguishable from paired chance? On the Gemini
temperature ablation, does living 0 versus 1 differ on `test450` or
on `dev750`?

## Why it matters

The results draft ranks cell 3 over standalone rules and over the
all-model cell, then treats temperature and thinking as request
settings that should not replace stage ownership. Table 3 already
shows Gemini temperature on both splits. Those are paired letter
comparisons. A count gap is not a test.

## Contrasts

Four questions. Temperature is one question on two splits.

| Id | Split | A | B | Framing |
| --- | --- | --- | --- | --- |
| `cell3_vs_rules` | `test450` | Living cell-3 select | Promoted three-stage rules | Table 1 vs standalone rules |
| `cell3_vs_cell5` | `test450` | Living cell-3 select | `gan_llm_select_from_extract` | Table 1 vs end-to-end model |
| `gemini_temperature_0_vs_1_test450` | `test450` | Cell 3 at temperature 0 | Same stack at temperature 1 | Gemini only |
| `gemini_temperature_0_vs_1_dev750` | `dev750` | Cell 3 at temperature 0 | Same stack at temperature 1 | Gemini only |
| `gemini_thinking_low_vs_high` | `test450` | Cell-3 select, thinking low | Cell-3 select, thinking high | Extra budget vs living select |

Thinking is **low versus high at select**, not a find-stop test,
not a three-way test, and not low versus medium. High is the
predeclared extra-effort setting (same 2× token cap as medium).
Medium stays a point estimate.

## Data and inspection

| Item | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Splits | locked `test450`; Gemini temperature also on `dev750` |
| Scorer | Purist; micro-F1 equals accuracy |
| Test | exact McNemar on discordant letters; Wald 95% CI on the accuracy difference |
| Row policy | aggregate-only; write 2×2 counts, never letter ids or notes |
| New calls | none |

Cell 3 is the living codebook replay (`gan_llm_extract` →
`gan_rules_encode` → `llm_select_after_codebook`). That vector is
374/450. Table 1 still cites 373/450. Rules are
`phase_c_candidate_config()` (325/450).

## Stop rule

Write the holdout aggregates and both temperature splits. Do not
add adjacent-hybrid, roster, or Grok temperature tests. Do not
retune Table 1 from the one-count cell-3 gap.

## Claim boundary

Holdout evidence for those four paired contrasts only. Not a
per-class test, not an equivalence test, and not a ranking of
hybrids that differ by five letters.
