# Gan 2026 Fresh-Evidence Triage Scaffold (confidence-gated) — Predeclaration

Date: 2026-06-16

Cycle C5 of the F1 workflow. Predeclared BEFORE any regeneration run.

## Goal and baseline

Optimize the V12 fresh-evidence reasoner (the component that scored the measured
holdout **379/450 (0.842)** on gpt-4.1-mini) toward >= 405/450, by closing the
component-generation wall: the 11 validation rows with no Purist-correct component,
which the row-level analysis
(`experiments/gan2026_hybrid_rowlevel_error_analysis_2026-06-16.md`) shows are
dominated by **over-quantification of evidence that does not establish a habitual
rate**. Validation is saturated (only 17 wrong), so the validation gate here is
**non-regression + gap-robustness + battery transfer**, not a big validation lift;
the true gain is measured on test once the candidate clears those gates.

## The change: a confidence-gated triage scaffold in the fresh-evidence reasoner

The fresh-evidence reasoner already has an `ambiguity_classification` contract and
safety gates; the live v0.7 ambiguity run still fixed only 1/11. Contract-layer
changes are exhausted. The untried lever — which took the bare labeler's OOD
battery from 7/8 to 8/8 with **no** rate regression (Cycle 2) — is a **structured
triage reasoning scaffold** that forces the model to evaluate, in order, BEFORE it
renders a label:

1. **confound_check** — are the events provoked/situational (missed meals, sleep
   deprivation, travel/jet-lag, alcohol, medication-supply gaps/non-adherence) or a
   transient exacerbation / new-or-uncertain classification with work-up pending?
2. **window_check** — is the observation window a usable habitual baseline, or a
   single dated last-event / a count over a non-recurring window?
3. **cluster_check** — do events arrive in clusters? If so, keep the cluster
   cadence AND the per-cluster burden; never flatten to a plain or per-burst rate.
4. **seizure_free_check** — is a continuous seizure-free interval ASSERTED, or is
   there only a last-event date with no asserted ongoing interval?

## The confidence gate (the critical guardrail)

The un-gated "coerce to unknown whenever the triage says unknown" regressed the
bare labeler by **-106** on validation750 (Cycle 3) because gpt-4.1-mini emits the
unknown verdict noisily on genuine-rate rows. So the fresh-evidence reasoner may
only DEMOTE its own structured-event answer to `unknown` when the triage emits a
**high-confidence, specific** withholding reason:

- `single_anchor_last_event` — exactly one dated event and no stated recurring
  rate (Cluster 1); OR
- `explicitly_provoked_or_transient` — the count is explicitly tied to a named
  trigger or a stated transient exacerbation (Cluster 2).

It must NOT demote on a bare/low-confidence unknown, on a clearly stated habitual
rate, or when a usable count+window baseline is present. Cluster-retention and
seizure-free-vs-last-event are rendering/precedence fixes and are NOT gated by
confidence (they do not risk demoting genuine rates).

Crucially, the deterministic floor (697/750) and the selector still protect the
bulk of genuine-rate rows; this change only edits the fresh-evidence component on
the hard boundary rows.

## Predeclared expected effect

- The 4 Cluster-1 rows (11216, 11254, 11272, 5534) and ideally the 3 Cluster-2
  rows (6321, 6368, 14025) gain a Purist-correct fresh component (oracle ceiling
  moves above 739/750).
- The 2 Cluster-3 rows (9937, 9943) gain the cluster-axis form.
- **Non-regression bar:** validation750 net Purist gain >= 0 and held-out-family
  CV `gap_robust = True` (no band regresses; changed-band precision clears bar).
  Watch genuine-rate rows for coerce-to-unknown leakage; if net < 0 or any rate
  band regresses, the confidence gate is too loose — tighten or reject.
- **Battery bar:** robustness battery v1 on gpt-4.1-mini must improve the
  seizure-free (A5) and cluster (A4/B6/C6) axes with zero genuine-rate regression
  on Panel A positives.

## Stop rule

Reject if validation750 net Purist < 0 or family-CV not gap_robust or the battery
regresses any genuine-rate case. Revise the confidence gate rather than loosen the
non-regression bar. Only a candidate that is gap-robust AND clears the battery is
eligible for the (user-authorised) test450 run.

## Method

Additive new fresh-evidence prompt version (keep existing versions intact).
Regenerate the fresh-evidence component live on validation750 (gpt-4.1-mini,
temp 0, resumable), reusing the existing structured-event sources. Score Purist +
family-CV; row-level attribution of which of the 11 flip correct and whether any
genuine-rate rows regress; then the battery. No test rows read at this stage.
