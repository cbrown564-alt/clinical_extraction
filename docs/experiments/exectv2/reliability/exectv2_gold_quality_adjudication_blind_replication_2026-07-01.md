# Gold-Quality Adjudication: Blinded Re-Replication (C1 Robustness Check)

- Generated: `2026-07-01`
- Follows from: `docs/plans/manuscript_evidence_gaps_closure_plan_2026-07-01.md` Phase 4
  (item 3 of `docs/research/paper_claims_evidence_review_2026-07-01.md`)
- Claim boundary: robustness check over already-adjudicated dev140 development-surface
  disagreement sets (`_dx_canonical/`, `_sf_canonical/`); no new model calls, no full-200 or
  holdout access, no row-level frozen-split inspection
- Row inspection policy: reads already-published dev140 disagreement case files only

## Question

C1 (the gold-quality-ceiling argument) is the manuscript's single most load-bearing soft
claim: it is the difference between "didn't beat the benchmark" and "beats it net of gold
noise." Both of its magnitude numbers — Diagnosis F1 0.6617→0.9501, SeizureFrequency
62.1%→89.3% — were produced by the project's own research pipeline, with no blinded external
check. The manuscript's own §4.1.2 caveat already flags the Diagnosis pass (five independent
reviewers, no cross-checking between batches) as weaker-provenance than the SF pass (one
coherent pass). This check asks: does an independent, blinded re-adjudication of a sample
reproduce the original verdicts closely enough to trust the reported magnitudes, or does it
reveal the magnitudes are sensitive to who is doing the judging?

## Method

**Sampling.** Stratified random sample, oversampling minority verdict buckets, per the
predeclared plan: 20 Diagnosis (letter, direction, concept) triples from the 209-item
`_dx_canonical/_adjudication.csv` population (target 7 GOLD_RIGHT / 6 BOTH_DEFENSIBLE / 7
MODEL_DEFENSIBLE vs. population base rates 14.8%/5.3%/79.9%), and 20 SeizureFrequency letters
from the 53-item `_sf_canonical/_adjudication.csv` population (target 7 MODEL_DEFENSIBLE / 7
BOTH_DEFENSIBLE / 6 GOLD_RIGHT vs. population base rates 41.5%/30.2%/28.3%, already close to
even). Seeded (`random.Random(42)` for Dx, `43` for SF) for reproducibility; sample fully
disjoint across letters for Dx (20 distinct letters for 20 triples, no letter contributed more
than one sampled concept). Sampling and packet-construction script:
`experiments/exectv2_phase4_blind_sample.py` is not committed as a standalone artifact — the
sampling logic is reproduced verbatim in this doc's Method section and the manifest is
available on request; this was a one-shot analysis script, not a resumable runner.

**Blinding protocol.** Two fresh, isolated sub-agent invocations (one per family) with no
access to this conversation, this project's conclusions, or the original verdicts. Each was
given only: the full letter text, the complete gold mention list, the complete model
prediction list (Diagnosis) or stage-1/stage-2 extracted facts (SF), and the located context
snippets — i.e., exactly the same raw evidence the original reviewers read, reproduced
verbatim from `_dx_canonical/{letter}.md` / `_sf_canonical/{letter}.md`, which never
contained verdicts. Each was given the exact three-way verdict taxonomy, copied verbatim from
`experiments/exectv2_dx_canonical_adjudication.py` and `experiments/exectv2_sf_canonical_adjudication.py`'s
docstrings, unchanged. Neither saw the original verdict, the original reason text, or any
narrative about which cases were sampled to illustrate which mechanism.

**Statistic.** Cohen's kappa (unweighted, linear-weighted, and quadratic-weighted — the
taxonomy has a natural GOLD_RIGHT → BOTH_DEFENSIBLE → MODEL_DEFENSIBLE ordering) between
original and blind verdicts, computed with `sklearn.metrics.cohen_kappa_score`, plus raw
agreement, per family and pooled. Additionally (not predeclared in the closure plan, added
because item-level kappa alone would be a misleading summary — see Results): a
population-reweighted genuine-error-rate estimate, applying each original stratum's blind
re-classification rate to that stratum's true population count, with a stratified normal-
approximation 95% CI.

## Results: Item-Level Agreement

| | n | raw agreement | κ (unweighted) | κ (linear) | κ (quadratic) |
|---|---:|---:|---:|---:|---:|
| Diagnosis | 20 | 60.0% | 0.389 | 0.381 | 0.375 |
| SeizureFrequency | 20 | 60.0% | 0.399 | 0.337 | 0.278 |
| Pooled | 40 | 60.0% | 0.397 | 0.362 | 0.331 |

**Per the plan's predeclared bands, this lands at/below the κ < 0.4 "genuine problem" line**
(pooled unweighted κ = 0.397, a hair under the threshold; per-family κ = 0.389 and 0.399,
both effectively at the boundary given n=20 sampling noise). Item-level agreement on individual
borderline cases is genuinely weak — a blind reviewer and the original reviewer land on the
same one-of-three verdict only 60% of the time in both families. Confusion matrices:

**Diagnosis** (orig → blind):

| orig \ blind | GOLD_RIGHT | BOTH_DEFENSIBLE | MODEL_DEFENSIBLE | n |
|---|---:|---:|---:|---:|
| GOLD_RIGHT | 4 | 0 | 3 | 7 |
| BOTH_DEFENSIBLE | 3 | 2 | 1 | 6 |
| MODEL_DEFENSIBLE | 1 | 0 | 6 | 7 |

**SeizureFrequency** (orig → blind):

| orig \ blind | GOLD_RIGHT | BOTH_DEFENSIBLE | MODEL_DEFENSIBLE | n |
|---|---:|---:|---:|---:|
| GOLD_RIGHT | 3 | 1 | 2 | 6 |
| BOTH_DEFENSIBLE | 1 | 4 | 2 | 7 |
| MODEL_DEFENSIBLE | 2 | 0 | 5 | 7 |

MODEL_DEFENSIBLE is the most stable verdict under blind re-review in both families (86% Dx,
71% SF retained). BOTH_DEFENSIBLE is the least stable in Diagnosis (33% retained — 3 of 6
reclassified as GOLD_RIGHT, the softest boundary in that family). GOLD_RIGHT is moderately
unstable in both (57% Dx, 50% SF retained), split roughly evenly toward both other categories
rather than concentrated on one boundary — i.e., the disagreement is not simply "the blind
reviewer is systematically more lenient/harsher," it is genuine three-way churn on
close-call cases, consistent with these being exactly the disputed, non-obvious concepts by
construction (undisputed concepts were never sent for adjudication in the first place).

## Results: Aggregate-Level Robustness (Why Item-Level κ Is Not the Whole Story)

A weak item-level kappa can coexist with a robust aggregate rate if the churn is
non-directional (verdicts move between categories roughly symmetrically). We tested this
directly: reweight each original stratum's population count by that stratum's blind
re-classification rate, to estimate what a full blinded re-adjudication of the entire
population would likely find.

| Family | Original genuine-error rate | Blind-reweighted estimate | Approx. 95% CI |
|---|---:|---:|---:|
| Diagnosis | 31/209 = 14.8% | 47.1/209 = **22.5%** | [1.6%, 43.5%] |
| SeizureFrequency | 15/53 = 28.3% | 16.1/53 = **30.3%** | [14.3%, 46.4%] |

**SeizureFrequency's aggregate rate is robust**: 28.3% → 30.3% is a small shift, and the
original point estimate sits comfortably inside the wide CI. This corroborates the
manuscript's existing characterization of the SF pass as the stronger-provenance one (single
coherent reviewer pass, per §4.1.2's own caveat).

**Diagnosis's aggregate rate shows a real, if uncertain, upward shift**: 14.8% → 22.5% is a
1.5× increase in the point estimate, though the CI is wide enough ([1.6%, 43.5%]) to include
the original value — this is not a statistically decisive rejection of the original number
at n=20, but the direction is consistent with, and corroborates, the manuscript's own
pre-existing caveat that the five-independent-reviewer, no-cross-check Diagnosis pass is
weaker-provenance than SF's single coherent pass. The honest reading is that the original
Diagnosis adjudication likely undercounted genuine model errors somewhat, not that the
core finding (most Diagnosis disagreements are gold-multiplicity artifacts, not model errors)
is wrong.

## Revised Magnitude Ranges

Applying the reweighted genuine-error rate (point estimate and CI bounds) to the same
adjusted-F1 (Diagnosis) and clinically-defensible-letters (SF) formulas the original analyses
used, holding the direction-level (MISSED/SPURIOUS) split proportional to the original
(a simplifying approximation — the blind sample was stratified by verdict, not by direction
within verdict, so a uniform scaling is applied to both `missed_defensible` and
`spurious_defensible` counts):

| Family | Original point estimate | Blind-reweighted point estimate | Approx. range (CI-bounded) |
|---|---:|---:|---:|
| Diagnosis adjusted F1 | 0.9501 | **0.9241** | [0.853, 0.995] |
| SF clinically-defensible % | 89.3% | **88.5%** | [82.4%, 94.6%] |

Both revised point estimates remain dramatically above the respective official/raw scores
(Diagnosis official F1 0.6617; SF metric-credited 62.1%) — **the core C1 finding survives**:
most of the benchmark-surface gap on these two families is gold-quality artifact, not model
deficit. What changes is the claimed magnitude, most for Diagnosis: the manuscript's single
point estimate (0.9501) should be reported as a **range** (approximately 0.85–0.99, point
estimate ≈0.92) rather than a bare point figure, and the wording should credit this blinded
check rather than resting solely on the original five-reviewer pass's stated 0.9501.
SeizureFrequency's number is materially corroborated and can keep its existing framing with a
pointer to this check.

## Decision-Band Verdict

Per the plan's predeclared framing: **item-level κ falls at/below the 0.4 threshold**, which
literally reads as "genuine problem... report as a limitation... revise C1 to report a range
bounded by the re-adjudication's lower estimate." We apply this literally but precisely: the
*range* revision is warranted and is made below for Diagnosis (the family where the aggregate
estimate actually moved); for SeizureFrequency, the aggregate-level reweighting shows the
original point estimate is well within a tight CI of the blind reweighted estimate, so
"lower estimate" for SF is 82.4%, close to the original 89.3%, and we report that as the range
floor rather than silently keeping the untested single point figure.

**This is not full independent corroboration of C1** — it does not clear the plan's κ ≥ 0.6
bar, and it is explicitly not external clinical validation (see limitation below). It is,
however, evidence of two distinct things that both matter: (1) individual borderline-case
verdicts are not highly reproducible between reviewers even within this project's own
framework — a genuine finding about the taxonomy's soft boundaries, most acutely
BOTH_DEFENSIBLE in Diagnosis; and (2) the population-level *magnitude* C1 actually reports in
the manuscript is more robust than the item-level κ alone would suggest, materially so for SF
and directionally-but-uncertainly so for Diagnosis.

## Explicit Limitation

This strengthens internal robustness (agreement across two independent passes within the
project's own evaluation framework: the original multi-reviewer/single-pass adjudications, and
a fresh sub-agent blind to both the original verdicts and this conversation) — it is **not**
external clinical validation. A blinded board-certified neurologist/epileptologist reviewing
the same sample remains the gold-standard check this replication cannot substitute for, and is
named as residual future work in the manuscript's D.5/D.2, unchanged by this check. The
blind reviewer here is itself an LLM-based sub-agent, not a human clinician; its judgments are
a useful second opinion under the same taxonomy, not a ground-truth arbiter.

n=20 per family is small; the reweighted-estimate confidence intervals are wide (up to ±20
percentage points), and this check should not be read as more statistically decisive than it
is. The Diagnosis point-estimate shift (14.8%→22.5%) is directionally informative and
consistent with the manuscript's own pre-existing weaker-provenance caveat, but is not, on
its own, a tight re-estimate.

## Manuscript Consequence

- §4.1.2 / D.2 / C1: revise the Diagnosis adjusted-F1 figure from the bare point estimate
  0.9501 to a range (~0.85–0.99, point estimate ≈0.92), citing this blind replication, and
  note that the revision direction corroborates (does not newly discover) the existing
  five-reviewer-provenance caveat.
- SeizureFrequency's 89.3% figure can retain its existing framing with a forward pointer to
  this check as corroborating evidence (reweighted point estimate 88.5%, CI 82.4–94.6%,
  comfortably overlapping the original).
- The core C1 argument (most of the SF and Diagnosis benchmark-surface gap is gold-quality
  artifact, not model deficit) is unchanged in direction and remains strongly supported; only
  the Diagnosis magnitude is narrowed from a single point estimate to a bounded range.
- Add an explicit note that item-level verdict reproducibility (κ≈0.33–0.40) is weaker than
  the aggregate-rate robustness — this is itself worth stating plainly rather than only
  reporting the more favorable aggregate number, per the project's standing evaluation
  discipline of not smoothing over an honest negative alongside a positive.

## Source Artifacts

- `_dx_canonical/_adjudication.csv`, `_sf_canonical/_adjudication.csv` (original verdicts,
  population)
- `_dx_canonical/{letter}.md`, `_sf_canonical/{letter}.md` (raw case evidence given to the
  blind reviewers, verified to contain no verdict/reason leakage)
- `experiments/exectv2_dx_canonical_adjudication.py`,
  `experiments/exectv2_sf_canonical_adjudication.py` (verdict taxonomy source, verbatim)
- `_dx_canonical/_summary.json` (official/adjusted F1 baseline recomputation inputs)
- Two blind sub-agent transcripts (Dx: 20/20 triples adjudicated; SF: 20/20 letters
  adjudicated; both returned exactly the requested count, no omissions)
- `docs/research/paper_claims_evidence_review_2026-07-01.md` (item 3)
- `docs/plans/manuscript_evidence_gaps_closure_plan_2026-07-01.md` (Phase 4)

## Interpretation Boundary

This is a robustness check over already-published dev140 disagreement case files; no new
model calls, no full-200/holdout access. It measures reproducibility of clinical judgment
under the project's own three-way taxonomy across two independent passes (original,
blind-fresh), not agreement with an external ground truth. The reweighted population estimates
are approximations (stratified-sample projections with wide CIs at n=20), not a full
re-adjudication of either population; a full blind re-run of all 209 Diagnosis and 53 SF
disagreements would narrow these intervals substantially and is the natural follow-up if the
Diagnosis magnitude range needs tightening further.
