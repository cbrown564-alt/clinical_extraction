# Gan 2026 Rules-Only: Gate A Parity Result on validation750

Date: 2026-08-10
Status: Gate A **FAILED**. `test450` was not run.
Protocol: [`rules_only_test450_aggregate_protocol_2026-08-10.md`](rules_only_test450_aggregate_protocol_2026-08-10.md)
Artifact: `experiments/gan2026_rules_only_validation750_parity_20260810.json`
Model calls: zero

## Result

Current HEAD does not reproduce the retained 2026-06-07 rules-only reference.

| Measure | Retained (2026-06-07) | HEAD | Delta |
| --- | ---: | ---: | ---: |
| Rows | 750 | 750 | 0 |
| Rendered rows (`final_label != "unknown"`) | 741 | 741 | 0 |
| Null rows (`unknown`) | 9 | 9 | 0 |
| Purist correct of rendered | 688 | 673 | **−15** |
| Pragmatic correct of rendered | 695 | 681 | **−14** |
| Purist correct, all 750 rows | 697 | 682 | **−15** |
| Pragmatic correct, all 750 rows | 704 | 690 | **−14** |
| Evidence-valid rows | 750 | 750 | 0 |

17 rows differ in final label: 15 Purist regressions, 0 gains, 2 score-neutral.

Under the predeclared rule, `test450` is not consumed and no fresh
predeclaration is auto-authorized. This report is the required
validation750-only writeup.

## Root cause: a deliberate decision, not drift

The protocol anticipated refactor drift. That is not what this is.

Every one of the 17 differing rows depends on shorthand notation that the
project deliberately retired. From
`src/clinical_extraction/tasks/seizure_frequency/gan2026/deterministic/rules/gan_shorthand.py`:

> **De-overfitting note (2026-06-09):** the original versions of these rules used
> `GAN2026_SPECIFIC` portability and accepted formatting that was specific to the
> GAN 2026 benchmark dataset — word numbers embedded in compact shorthand
> ("TC nine/mo"), and special separator characters before counts (asterisk, X, ×,
> e.g. "TC *5/wk", "sz X7/mo"). These embellishments matched validation phrasing
> but would not generalise to real clinical notes. […] Rows that depended on the
> benchmark-specific variants are now correctly null/unknown rather than
> extracted via rules that only fire on validation data.

That change is dated **two days after** the retained reference run. The retained
`697/750` was therefore measured on a ruleset the project itself subsequently
judged benchmark-overfitted and rewrote.

The retained per-row evidence confirms the mechanism exactly. All 17 rows, and
nothing else:

| Retained evidence | Rows |
| --- | --- |
| Word number in shorthand (`TC nine/mo`, `TC six/mo`, `six/30 this month`, `sz xfour/wk`, `qtwo - threewk`, `qone to twod`) | 8 |
| Special separator prefix (`TC *5/wk`, `sz X7/mo`, `sz X2/d`, `sz x3/d`, `sz x3/yr`) | 5 |
| Both (`TC Xnine/yr`, `TC ×ten/yr`, `sz ×nine/mo`, `sz *six/mo`, `one - two×/month`) | 4 |

Confirmed directly: `TC 9/mo` extracts via `gan_shorthand.tc_sz_count_rate`,
while `TC nine/mo` yields the `NO_REFERENCE` fallback.

This is **not recoverable by an ablation switch**. The rules were rewritten to
require digit-only counts, not gated. Default `AblationConfig()` already enables
every rule group and portability class including `GAN2026_SPECIFIC`.

Failure shape: 11 of 15 regressions collapse to `no seizure frequency
reference`, 2 to `seizure free for multiple year`, 2 to a wrong rate. The rows
cluster in source-row band 3200–4200 (12 of 48 rows in that band), which appears
to be a shorthand-notation cohort in the Gan corpus.

## Second finding: the two denominators are both correct

The protocol flagged `688/741` vs `697/750` as an unresolved accounting. It is a
genuine denominator convention, and both figures are right.

In the **rules** lane, `rendered` means `final_label != "unknown"`. There are
exactly 9 such `unknown` rows, so `750 − 9 = 741`. All 9 are Purist-correct —
their gold is `multiple per month`, which the Purist projection places in the
same category as `unknown` — so `697 − 9 = 688`. Both the manifest
`result_summary` (`688/741`) and its `verification.expected` block (`697`, `704`,
750 rows) are correct, at different denominators. The registry entry agrees and
records `null_rows: 9` explicitly.

The **LLM** lanes use a different convention: `rendered` means the row produced a
parseable `comparison` block at all (hybrid `748/750`, llm-only `750/750`). The
deterministic lane always emits one, so it cannot use that definition.

| Cell | Convention | Figure | Verified |
| --- | --- | ---: | --- |
| `gan2026_rules_reference` | `final_label != "unknown"` | 688 / 741 | ✅ |
| `gan2026_hybrid_reference` | non-null `comparison` | 661 / 748 | ✅ |
| `gan2026_llm_only_reference` | non-null `comparison` | 581 / 750 | ✅ |

**No manifest correction is required.** An earlier revision of this report
claimed `688/741` was an unreproducible error; that was wrong — it was derived
under the LLM lanes' convention rather than the rules lane's own. The figures
have been left as they stand. The lesson for the protocol is that "rendered" is
lane-specific and every reported Gan figure must name its denominator.

## What this means for the paper

The cited rules-only comparator, `688/741`, describes a **retired** ruleset —
rules the project itself rewrote for benchmark overfitting on 2026-06-09, two
days after the run. Presenting it beside current-architecture LLM rows compares
against extraction behaviour that no longer exists in the codebase.

The honest current-architecture figure is **673/741** rendered (682/750 across
all rows).

The 15-row gap between them is a clean, zero-cost, open-split measurement of
what the benchmark-specific shorthand embellishments were worth — which is
itself a usable result for the portability argument.

## Resolution

The user's decision, 2026-08-10: adopt the current portable ruleset as the
rules-only comparator and re-freeze the architecture. Executed in
[the re-freeze note](rules_only_reference_refresh_2026-08-10.md).

`test450` remains unconsumed. A fresh Gate A, restated against the newly frozen
ruleset, is the precondition for any future holdout run.
