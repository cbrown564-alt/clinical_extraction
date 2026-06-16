# Gan 2026 Evidence-Presentation v0.6 — Predeclaration

Date: 2026-06-15

Cycle 2 of the F1 dynamic workflow
(`docs/research/gan2026_f1_dynamic_workflow_protocol_2026-06-15.md`). Predeclared
**before any run**, per the predeclaration hard gate. This is the candidate
evidence-presentation change that follows Cycle 1's verdict: the live
`llm_only_direct_labeler` v0.5 on `gpt-4.1-mini` is **OVERFIT** on the robustness
battery (Panel A 2/6 pairs both-correct + 3 overfit-only; Panel B 5/7; Panel C
7/8), with the weakest axis = `cluster_axis_retention`.

This file states the exact change, the clinical principle, the expected per-panel
effect (direction + rough magnitude), the regression risk, and the stop rule.
Nothing here is revised after the run.

## The change (what the model is made to SEE / ATTEND TO)

Add a new prompt version `gan2026_llm_only_direct_labeler_v0.6`, gated by a
version selector, leaving v0.5 intact and runnable. The change is to the
**evidence the model attends to**, implemented as a **structured reasoning
scaffold** prepended to the decision task: before emitting a label the model must
first fill in four explicit triage findings about the reported events, and the
prompt ties each finding to a hard labelling consequence. Per the protocol's tier
3, changing what the model is made to attend to *is* the evidence change — we do
not add a new runtime agent, selector gate, or decision contract.

The scaffold adds four fields the model must populate first (carried in the
prompt instructions; the emitted JSON schema is unchanged so scoring/normalization
are untouched):

1. **confound_check** — Are the reported events tied to a removable
   provoking / situational / adherence factor (missed meals, sleep
   deprivation, long-haul travel / jet lag / circadian disruption, alcohol,
   medication-supply gap or non-adherence)? If YES → the count does **not**
   establish a habitual baseline → `unknown`.
2. **window_check** — Is the observation window a usable *habitual baseline*
   (the patient's typical, ongoing pattern), or is it a transient exacerbation
   ("rough patch", "period of decline"), an uncertain/work-up-pending
   classification, or a one-off count in an observation window? If it is NOT a
   usable habitual baseline → `unknown`.
3. **cluster_check** — Do the events arrive in **clusters / runs / groupings**
   (several events over consecutive days, then a gap, recurring every few
   days/weeks)? If YES → label with the **cluster cadence** (`1 cluster per N
   week, multiple per cluster`), and **never** flatten to a plain per-window
   rate and **never** collapse to `unknown` merely because the per-cluster count
   is not logged.
4. **seizure_free_check** — Is there an **asserted continuous seizure-free
   interval** ("free of all seizures for N months", witness-confirmed), or only
   a **last-event date** with no asserted interval / incomplete follow-up? Last
   event only → `unknown`. Asserted interval → `seizure free for N month`.

Only after recording these four findings does the model emit `final_label`. The
prompt states the precedence explicitly: **confound_check OR window_check failing
→ `unknown` wins over any apparent rate** (Yujian's rule: when count or window is
unclear, `unknown` is safer). The genuine-rate path is preserved: if all four
checks are clean (unprovoked, stable habitual window, no clusters, no seizure-free
assertion) and a count-over-window or explicit rate is stated, emit the rate.

## The clinical principle (neurologist-endorsable, distribution-independent)

> An explicit count of events over a time window establishes a *habitual seizure
> frequency* only when the events are the patient's typical, unprovoked baseline
> over a usable observation period. Counts of provoked/situational events, counts
> during a transient exacerbation or pending work-up, and purely descriptive
> semiology do not define a rate and are `unknown`. A cluster pattern must keep
> its cluster axis (clusters per window + events per cluster), never flattened to
> a plain rate nor discarded to `unknown`. An asserted seizure-free interval is a
> duration; a last-event-only date is not — it is `unknown`.

This is core clinical reasoning that transfers identically to real KCL letters;
the GAN-synthetic surface is incidental. It is **not** a validation-mined gate
keyed on saved-row behaviour.

## Why this is an evidence change, not a contract change

Cycle 1's v0.5 already had an `answer_kind` contract and a vague prose nudge about
conditional windows, and still quantified provoked/transient counts and flattened
clusters. The failure is not contract non-compliance; it is that the model never
*forms the finding* that the count is provoked / transient / a cluster before it
labels. The scaffold forces the finding to exist and attaches it to a labelling
consequence — it changes what the model attends to in the evidence. A
contract-only relabelling could not pass the battery (the battery's minimal pairs
share almost all text; only the confound/window/cluster/seizure-free clause
differs).

## Expected effect per panel (direction + rough magnitude)

Baseline (v0.5, Cycle 1): A 2/6 both-correct + 3 overfit-only; B 5/7; C 7/8 (88%).

- **Panel A (minimal pairs).** Expect the three overfit-only pairs to close:
  - A2 (transient/jet-lag): A2a should flip `3 per 6 week` → `unknown`
    (window_check). A2b stays correct (stable pattern → rate). Pair → both-correct.
  - A5 (seizure-free vs last-event): A5b should flip `seizure free for 4 month`
    → `unknown` (seizure_free_check: last-event only). A5a stays. Pair →
    both-correct.
  - A6 (adherence): A6a should flip `2 per 6 week` → `unknown` (confound_check:
    supply gap). A6b stays. Pair → both-correct.
  - A4 (cluster): A4a currently emits `multiple per day` → `unknown` (axis
    collapsed). cluster_check should pull it to the cluster-cadence bucket
    (`1 cluster per 4 to 5 week, multiple per cluster` → Purist
    `seizure_freq_more1mon_less1week`). This is the **weakest axis** and the
    highest-risk fix. A4b (isolated, no cluster) stays a plain rate.
  - **Expected:** ≥ 5/6 pairs both-correct, **target 6/6, zero overfit-only**.
    Rough magnitude: A2/A5/A6 are high-confidence flips (clear single-clause
    triggers the scaffold names explicitly). A4 is the uncertain one.
- **Panel B (source-near).** B3 (last-event/single-recent), B6 (cluster) are the
  two failures. seizure_free_check + the "single recent event = count in a window
  → unknown" wording should fix B3. cluster_check should fix B6's cadence
  bucketing. **Expected:** 6/7 or 7/7 (bar ≥ 6/7). Rough magnitude: B3 high
  confidence; B6 moderate (cadence bucket arithmetic, not just unknown/not).
- **Panel C (KCL OOD).** Only C6 (cluster, ZNS shorthand) failed (went to
  `unknown`). cluster_check should retain the cadence (`1 cluster per 3 week,
  multiple per cluster`). The two genuine-rate positives (C4, C5) and seizure-free
  (C3) must NOT regress to `unknown`. **Expected:** maintain ≥ 7/8 (88%), target
  8/8; **must stay ≥ 80%** (bar). The transfer risk is over-withholding pushing a
  genuine-rate row to unknown — see regression risk.

## Regression risk (the thing that would make this fail honestly)

The scaffold's `unknown`-precedence could **over-withhold**: push a genuine
habitual-rate row (A1b, A2b, A3b, A4b, A5a, A6b, B-none-positive, C3/C4/C5) to
`unknown` because the model over-reads a benign mention (e.g. "sleep + adherence
fine" read as a confound, or a stable rate read as transient). This is the
mirror-image failure and is the primary thing the battery's *positive* sides and
Panel C genuine-rate anchors are there to catch. Concretely:
- If C4 or C5 (clean stable rates) flip to `unknown`, Panel C can drop below 80%
  → candidate fails on its own transfer bar. That is the honest stop signal.
- cluster_check is double-edged: forcing cluster cadence could mis-bucket A4b/B-
  isolated cases or over-trigger on non-cluster prose ("a run of bad days").

Mitigation in the prompt wording: each check is framed as "only when explicitly
indicated"; the genuine-rate path is stated as the default when all checks are
clean; cluster_check requires an explicit grouping/recurrence pattern, not just
plural events.

## Stop rule

- **Gate to proceed to validation750:** the battery must clear **Panel A**
  (every pair both-correct AND zero overfit-only) **AND Panel B** (≥ 6/7,
  trigger-independent) **AND keep Panel C ≥ 80%**. Only then run the authorised
  validation750 live pass + held-out-family CV.
- **If any bar fails:** STOP. Do **not** run validation750. Report the residual
  failing-case ids verbatim and the most likely next evidence change. A battery
  pass is **necessary, not sufficient**, and is not a holdout result.
- No post-hoc bar lowering, no re-running to pick a better seed, no editing the
  scaffold after seeing which case moved. If v0.6 trades one overfit-only pair
  for a new genuine-rate regression, that is a net wash and is reported as such.

## Registration

Battery run registered `mode=live`, `split=validation`,
`evidence_validity` = authored-OOD (NOT Gan rows, NOT holdout, NOT test450),
`decision` = promote only on `transfers`, else `revise`. test450 is never read or
run here.
