# Gan 2026 Clean Policy Attribution Note

Date: 2026-06-01

## Purpose

This note freezes the attribution boundary for the current Gan 2026 structured
LLM line after the clean scorer-facing policy ladder. It is a development-split
research note, not a holdout result or benchmark-comparison claim.

## Attribution Boundary

For clean LLM-first attribution, the prediction-bearing component is the raw
structured model extraction and clinical selection. The scorer-facing layer may
validate evidence substrings, validate schema shape, normalize Gan-compatible
label grammar, and apply the frozen table-backed clean scorer-facing policy.

The clean scorer-facing policy is now limited to the families documented in
`docs/research/gan2026_gold_normalization_policy_question_2026-06-01.md` and
summarized in
`experiments/gan2026_clean_policy_freeze_ladder_v0_2026-06-01.md`: vague
quantity with explicit denominator, period dialect and shorthand, cluster syntax
grammar, and single already-totaled count/window phrasing, with the earlier
table-backed validation examples for cluster-name stripping, vague weekday
cadence, and bare Gan-specific `bimonthly`.

This layer exists to align source-near model output with Gan scorer conventions
while preserving the original trace. It is not a standing license to add new
semantic repair whenever a row would score better.

## Why The Policy Is Frozen

The 50-row same-raw-output freeze ladder showed a useful but bounded effect:

| Condition | Purist | Pragmatic | Parse/schema/label failures |
| --- | ---: | ---: | ---: |
| Raw model selection | 34 / 50 = 0.6800 | 36 / 50 = 0.7200 | 10 |
| Strict format-only | 41 / 50 = 0.8200 | 43 / 50 = 0.8600 | 3 |
| Frozen clean policy | 43 / 50 = 0.8600 | 46 / 50 = 0.9200 | 0 |

Those gains are enough to justify a narrow scorer-facing alignment layer, but
not enough to make normalization creep the main development path. The broader
v0.5 repair-family replay already showed that large metric gains can come from
deterministic modules that change semantic state, compute new labels, or
override model selection. Those modules may be valuable, but they are not clean
LLM-first behavior.

## Route For Further Gains

Future score gains should come through one of two explicit routes:

1. Model-side changes: model selection, prompt/schema design, extraction
   decomposition, or clinical-selection logic that changes the raw structured
   output before scorer-facing normalization.
2. Named deterministic modules: upper-bound handling, diary arithmetic, temporal
   selection, evidence-state classification, cluster reconstruction, and similar
   semantic repairs, each with tests, an ablation condition, and claim language
   that names the deterministic contribution.

Any proposed expansion of the clean scorer-facing policy must first pass a new
direct-citation row-table review on the development surface. The review must
show that the transformation preserves the selected clinical fact, is consistent
with Gan annotation behavior, and belongs in the scorer-facing layer rather than
in a named deterministic module.

## Claim Language

Use language like:

> Structured LLM extraction with raw model clinical selection plus frozen
> scorer-facing Gan normalization reached the reported development-split score.

Avoid language like:

> The LLM solved the task after post-processing.

When named deterministic modules are enabled, describe the result as a hybrid
pipeline and report module ablations alongside the score.
