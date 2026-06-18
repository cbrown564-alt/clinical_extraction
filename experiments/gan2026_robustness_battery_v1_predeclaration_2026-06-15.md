# Gan 2026 Robustness Battery v1 — Predeclaration

Date: 2026-06-15

Cycle 1 of the F1 dynamic workflow
(``). This
predeclares the adversarial/robustness/hard-case battery that is the **primary
pre-test gate**, because `validation750` is saturated (selector oracle ceiling
739/750; live component generation fixed 1/11 no-correct rows). The battery must
discriminate candidates and estimate transfer to unseen King's College London
letters *before* any `test450` run.

This file is written before the battery is scored against any candidate. It states
the principle, the cases, and the pass bars up front.

## The clinical principle under test

Derived from the 11 validation rows that gate the oracle ceiling
(`experiments/_c1_no_correct_rows_extract.json`; the 7 unknown-gold rows are the
core). All 7 share one error: the model converts a reported **event count** into a
habitual seizure **frequency** when it should have returned `unknown`.

**Principle (neurologist-endorsable, distribution-independent):**

> An explicit count of events over a time window establishes a *habitual seizure
> frequency* only when the events are the patient's typical, unprovoked baseline
> over a usable observation period. A count must **not** be quantified into a rate
> when the events are:
> 1. **provoked / situational** — tied to a removable trigger (missed meals,
>    sleep deprivation, long-haul travel/jet lag, alcohol, medication-supply gaps
>    or non-adherence);
> 2. **transient** — described as a recent exacerbation, "period of decline",
>    new/uncertain classification, or work-up pending;
> 3. **descriptive, not quantitative** — the note characterises semiology or a
>    single event without stating a baseline rate;
> 4. and a **cluster** pattern must retain its cluster axis rather than be
>    flattened to a plain per-window rate.
>
> In cases 1–3 the correct Gan label is `unknown` (count and/or denominator do not
> define a habitual rate); in case 4 the label must carry the cluster cadence.

This generalises: distinguishing provoked/situational/transient events from
habitual frequency is core clinical reasoning that applies identically to real
letters. The synthetic surface (clean templated UK letters) is incidental; the
principle is not.

## Why this is an *evidence* problem, not a *contract* problem

The live v0.7 run already had an `ambiguity_classification` contract and still
self-labelled 6321/6368/14025 as `explicit_count_window`. The model is not failing
to follow a contract; it is failing to *see* that the count is provoked/transient.
So the candidate fix (Cycle 2) changes the evidence presentation — surfacing
trigger/transience/denominator cues next to the count — not the decision schema.
The battery is built so a contract-only change cannot pass it.

## Panels and predeclared pass bars

All cases are authored fresh (not Gan rows). Gold is the Gan label; scoring is
Purist via `evaluate.py`. Cases live in
`experiments/gan2026_robustness_battery_v1_cases.json`. A candidate is run live
(`gpt-4.1-mini`, temperature 0) on each note and its emitted label is scored.

### Panel A — synthetic minimal-pair hard-negatives (overfit trap)
Minimally-contrasting pairs that flip the gold. Each pair shares almost all text;
one clause changes the answer (provoked vs habitual; explicit-window-baseline vs
last-event-only; cluster vs plain rate; true seizure-free duration vs
last-event-only).
- **Bar:** a passing candidate gets **both** sides of **every** pair correct.
  **Zero** pairs where only the "easy" (quantify) side is right. Any pair solved
  only on the rate side is the overfit signature and fails the panel.

### Panel B — source-near perturbations (lexical-overfit trap)
The 7 core failure situations, reworded to preserve clinical meaning while
changing surface form (synonyms, reordered clauses, different trigger nouns).
- **Bar:** ≥ 6/7 return `unknown` (or correct cluster label), and the result must
  not depend on the specific trigger word used.

### Panel C — KCL-style out-of-distribution (transfer estimate)
The same clinical situations rewritten as real-letter prose: abbreviations
(`GTCS`, `szs`, `EMU`, `c/o`, `2/52`, `nil`), dictation artefacts, hedging,
non-template structure, mixed current/historical framing, terse problem lists.
- **Bar (transfer):** ≥ 80% correct on Panel C. Below this, the candidate is
  treated as not demonstrated to transfer, regardless of validation/test numbers.

## Verdict rule

The Generalization Adversary returns **transfers** only if all three bars are met.
**transfers** is necessary (not sufficient) for the Freeze Warden to authorise a
`test450` run. A candidate that fails any bar is sent back as `revise`. Results —
including failures — are reported verbatim; failure is the informative outcome.

## Baseline to record first

Run the current best holdout candidate family (V12 fresh-evidence reasoner,
prompt v0.6 / safety v0.9, the post-unknown-policy state) through all three panels
to establish where it stands *before* the Cycle-2 evidence-presentation change.
This baseline is itself a useful result: it quantifies how much of the
component-generation wall is surface-overfit vs genuine clinical gap.
