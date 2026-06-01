# Gan 2026 Saturated Validation Protocol

## Purpose

When a comparator or candidate is already near ceiling on a validation prefix,
another aggregate validation250 run is usually low-information. It can confirm
output contract health, but it cannot reliably answer whether the candidate
will generalize or improve the dominant failure modes of a saturated baseline.

Use this protocol whenever any of these are true:

- deterministic top, baseline, or candidate is at or above roughly 0.95 on a
  validation prefix;
- the remaining validation errors are fewer than the expected variance from
  prompt/model/cache changes;
- the comparator is known to have a large validation-to-test drop;
- the proposed experiment asks a broad "does this improve?" question rather
  than a targeted failure-mode question.

## Default Decision

Do not spend the next run on another broad validation250 aggregate unless it has
a predeclared targeted learning goal that cannot be answered by a smaller or more
diagnostic surface.

For saturated surfaces, choose one or more of these instead:

1. synthetic hard-case panel;
2. validation hard-slice panel;
3. frozen test generalization audit;
4. adversarial/paraphrase robustness panel;
5. component-stress ablation over the hard panels;
6. calibration/selective-action study, especially for adjudicators.

## Required Experiment Unit

Before running a saturated-surface experiment, write down:

- Saturation evidence: current score, remaining error count, and known
  validation/test gap if any.
- Dominant failure mode being tested, such as temporal selection, seizure-free
  boundary state, no-reference versus unknown, clusters, multiple semiologies,
  uncertainty, negation, medication/status context, or relative dates.
- Comparator and expected mechanism of improvement.
- Surface choice: synthetic hard cases, validation slices, frozen test, or a
  combination.
- What will be inspected after the run: aggregate only, predeclared slices,
  generated-case row review, validation row review, or locked-test row review.
- Stop rule: what result would promote, revise, reject, or trigger a new
  validation-cycle design.

## Surface Choices

### Synthetic Hard-Case Panel

Use generated or curated source-near cases when the question is mechanistic:
"Can the candidate handle the scenario the deterministic stack tends to miss?"

Good panels are small, typed, and intentionally uncomfortable. Include labels
and expected rationales before running the candidate. Suggested scenario axes:

- current versus historical conflict;
- seizure-free statement after a recent count;
- last-event-only versus recurring rate;
- unknown versus no seizure frequency reference;
- cluster cadence versus events-per-cluster burden;
- multiple active semiologies with different burdens;
- negated or hypothetical seizure statements;
- medication/status text that sounds seizure-free but does not state frequency;
- relative-date and elapsed-window arithmetic;
- vague recurrence such as "some", "several", "intermittent", or "most days".

Synthetic panels are not benchmark evidence. They are mechanism probes and
regression tests for error families.

### Validation Hard-Slice Panel

Use validation slices when the question is whether a candidate improves known
development failure families without being swamped by already-easy rows.

Build slices from predeclared metadata, existing validation error analyses, or
textual triggers. Keep slice membership reproducible in an artifact. Report:

- slice definition;
- row count;
- baseline performance;
- candidate performance;
- changed labels;
- baseline-wrong to candidate-correct;
- baseline-correct to candidate-wrong;
- evidence/schema validity;
- examples only from validation rows.

Prefer hard slices over full validation250 when deterministic top is already
near ceiling on the prefix.

### Frozen Test Generalization Audit

Use locked test only when the candidate, prompt, model, scorer, gates, repair
policy, and analysis plan are frozen before the run.

Allowed test reads:

- aggregate Purist and Pragmatic;
- predeclared slice aggregates if slice definitions were fixed without looking
  at test labels or row-level test failures;
- calibration/selective-action summaries fixed before the run.

Avoid row-level test inspection during development. If row-level test review is
explicitly needed after a frozen test run, record it as post-hoc final-evaluation
analysis and do not tune from it. Any fix starts a new validation-cycle candidate.

### Adversarial And Paraphrase Robustness Panel

Use this when validation/test gap suggests brittle surface-pattern fit. Create
minimal pairs that preserve the clinical fact while changing wording, order,
section placement, negation, uncertainty, or distractors. Report consistency
within pairs, not only F1.

### Component-Stress Ablation

For hybrid or LLM-backed candidates, run hard panels through named component
conditions, such as:

- deterministic top;
- raw model final;
- format-only repair;
- conservative gated final;
- full repair stack;
- selected component disabled.

This is where an adjudicator should prove it helps the deterministic stack's
actual hard cases, not merely avoid damaging easy rows.

### Calibration And Selective Action

For adjudicators, ask whether the model should act at all. Report:

- changed-label rate;
- precision of changes;
- abstention/fallback rate;
- wrong-to-correct versus correct-to-wrong transitions;
- confidence or gate features associated with useful changes.

If an adjudicator cannot make high-precision changes on targeted hard slices,
prefer deterministic fallback or a narrower adjudication task.

## Promotion Rules

A saturated-surface candidate should not be promoted because it matches a
saturated validation score. Promotion needs one of:

- improved frozen-test aggregate under a predeclared plan;
- clear improvement on hard validation slices with acceptable regression cost;
- clear mechanism success on synthetic/adversarial hard panels plus a plan for
  frozen evaluation;
- a selective-action profile showing high-precision corrections over the
  comparator's dominant failure modes.

If the result is mostly "same aggregate, a few changed labels," mark it as
diagnostic or revise-only.
