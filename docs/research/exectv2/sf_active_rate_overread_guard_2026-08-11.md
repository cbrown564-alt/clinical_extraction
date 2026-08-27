# ExECTv2 SeizureFrequency active-rate over-read guard

Date: 2026-08-11
Status: development audit, **net negative** on the predeclared `v1` guard

Protocol: recovered from git history; this report is the answer.
Artifact: [`experiments/exectv2_sf_active_rate_overread_audit_dev140_20260811.json`](../../experiments/exectv2_sf_active_rate_overread_audit_dev140_20260811.json)
Script: `removed in the 2026-08-16 scripts prune; recover from git history (was `scripts/audit_sf_active_rate_overread.py`)`

## Plain answer

The predeclared evidence-marker guard (historical / hypothetical /
descriptive vs. current, frozen before any evidence text was read) is **net
negative** on `dev140`, across all six models, on both selection metrics.
No `test59` holdout confirmation protocol is written as a result — Step 5 is
skipped per the predeclared "only if net positive" gate. Item B stays open.

## Sanity check

The audit reproduces PROJECT_STATUS item B's cited figure exactly: **141
pooled extra `active-rate` keys** across the six retained dev140 sidecars,
matching the reference `build_six_model_hard_slice_error_modes.py` count.

## Why the guard fails: the evidence-marker hypothesis mostly doesn't apply, and mislabels when it does

Of the 574 pooled `active-rate` mentions classified (all active-rate
mentions, not just the 141 extra ones), only 45 (7.8%) matched any
historical/hypothetical/descriptive marker at all — **529 (92.2%) classify
as `current`** under the v1 patterns. So the temporal-language hypothesis
targets a small slice of the problem: most of the 141 extra `active-rate`
emissions carry no historical/hypothetical/descriptive marker in their
evidence span. Whatever is driving the extra emissions (gold multiplicity
convention, wrong seizure-type/CUI keying, genuine over-read without any
temporal tell) is not "the model quoted old or hypothetical language" in the
overwhelming majority of cases.

Worse, within the 45 marked mentions, the guard's precision is poor:

| | Rescue (extra key correctly removed) | Harm (correct key incorrectly dropped) |
| --- | ---: | ---: |
| Pooled | 3 | 25 |

**Harm outnumbers rescue more than 8 to 1.** The dropped-mention examples
show the actual failure mode: markers like "last clinic", "last year", or
"previously" fire on **duration/recency framing of a still-current rate**
("Since her last clinic appointment she has had four secondary generalised
seizures", "around 5 seizures in the last year which is good for him", "He
is getting around 2 seizures per month at the moment... as previously he has
had several seizures per week" — the second half describes the *prior* rate
inside a sentence whose first half is the *current* one, and the mention's
evidence span includes both). Clinical letters routinely frame a current
seizure count as "since last visit" or "in the last N months" — exactly the
vocabulary the guard treats as a historical disqualifier. The predeclared
lexical approach cannot separate "point-in-the-past" language from
"duration-ending-now" language without more structure than a marker regex
provides.

## Numeric rescue/harm table (per model)

| Model | Extra active-rate keys | Marked non-current | Rescue | Harm | Exactness Δ | Micro-F1 Δ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| GPT-4.1-mini | 26 | 7 | 0 | 4 | -0.0286 | -0.0191 |
| GPT-5.6 Luna | 21 | 10 | 2 | 4 | -0.0143 | -0.0090 |
| GPT-5.6 Sol | 19 | 7 | 0 | 4 | -0.0286 | -0.0183 |
| DeepSeek V4 Flash | 12 | 6 | 0 | 5 | -0.0357 | -0.0182 |
| Qwen 3.6 35B | 24 | 7 | 0 | 5 | -0.0357 | -0.0214 |
| Gemma 4 26B | 39 | 8 | 1 | 3 | -0.0143 | -0.0215 |

**All six models regress on both exactness and micro-F1. No model shows a
positive sign.** This is not a mixed or model-compensating result like the
Prescription decomposition's convention-noise rule — it is uniformly
negative.

## Pooled F1 delta

| Metric | Baseline | Guard | Delta |
| --- | ---: | ---: | ---: |
| SeizureFrequency clinical-headline micro-F1 | 0.7377 | 0.7197 | -0.0180 |
| SeizureFrequency clinical-headline clinical F1 (per-letter scorer) | 0.6226 | 0.6011 | -0.0215 |
| Pooled exactness rate | (baseline) | (guard) | -0.0262 |

## Development selection rule: NOT MET

Predeclared bar: pooled exactness delta `>= 0`, pooled micro-F1 delta
`>= +0.005`, at most one model with a micro-F1 sign flip below `-0.005`.

Actual: pooled exactness delta **-0.0262**, pooled micro-F1 delta **-0.0180**,
**6 of 6** models flip negative below `-0.005`. All three conditions fail.
`development_selection.met = false` in the artifact.

## Missed-unknown arm (secondary, diagnostic)

97 pooled missed-`unknown` keys, matching PROJECT_STATUS's cited figure.
Inference (insert an `unknown` mention at the type-key of a guard-dropped
active-rate mention) recovered **0 of 97**. The dropped active-rate mentions
in this audit essentially never share a type-key with a letter's missing
`unknown` key — the two error modes are not mechanically linked through
this guard. The missed-unknown problem needs its own investigation, not a
byproduct of the active-rate guard.

## Decision

**Net negative.** The predeclared `v1` guard is not eligible for a `test59`
holdout confirmation protocol; Step 5 (write the holdout protocol) is
skipped per its own "only if dev140 is net positive" condition. No
exploratory pattern-mining pass was run: the diagnosis above (7.8% marker
coverage, 3:25 rescue:harm ratio, duration-framing false positives) already
explains why a lexical current-vs-historical marker approach is
structurally weak for this problem, and iterating the same regex-family
approach against the same 141 cells' text would be dev-fitting exactly the
pattern the sibling Prescription study flagged as a risk (see
`prescription_lens_v10_holdout_confirmation_2026-08-10.md`'s
discussion of dev-harvested rule sets losing on holdout). A guard that
already loses on the set it was tuned against is not a candidate worth
hand-tuning further inside this study.

## What would be needed instead

The extra-active-rate problem looks structurally different from "quoted old
language": 92% of the extra emissions carry no temporal marker at all. A
more promising next angle (not attempted here) is the seizure-type/CUI
keying and gold-multiplicity mechanism already documented for Diagnosis and
SF elsewhere in this project's evidence base (see the SF canonical
row-adjudication and Dx consolidation findings referenced in
`PROJECT_STATUS.md`), rather than an evidence-span temporal classifier.

## Row policy

Machine-only scoring. No `test59`/`test60` file was read or referenced.
Per-cell evidence excerpts quoted above are drawn from `dev140`, which is
permitted for development review per PROJECT_STATUS.md. No rule, threshold,
or pattern was changed after this run — the classifier used is exactly the
frozen `v1` from the predeclared protocol.

## Claim boundary

Development-only, zero model calls, no-call replay over already-persisted
`dev140` evidence text. This is a negative development result for one
predeclared guard design; it does not establish that no active-rate guard
can work, does not touch `test59`/`test60`, and authorizes no change to
`projection.py` or any production pipeline code.
