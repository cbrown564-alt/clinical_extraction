# Does gold-consolidation inflate the GEPA-vs-hybrid evidence-recall gap? — SeizureFrequency check

Status: **CLOSED (H-inflated CONFIRMED under both readings: predeclared-formula 83.3%, plain
verdict-only 61.1% — both >> 50% threshold).** Date: 2026-06-30.
Owner: ExECTv2 GEPA workstream / predecessor-lessons application follow-up.

> **Numbers corrected 2026-07-02 (F2, `docs/research/exectv2_pipeline_assumption_audit_phase4_guardrail_2026-07-02.md`):**
> the official `source_near` scorer's greedy first-overlap matching was fixed to a maximum-cardinality
> match; on this exact run/entity it recovers **1 of the 72 misses below** — `EA0143`'s
> `focal-seizures-with-altered-awareness` (row 54 in `_adjudication.csv`, already adjudicated
> `H1_CARDINALITY` / `MODEL_DEFENSIBLE` with the reason *"greedy matching just credited it to the
> other, generic 'seizure' gold tag instead - pure cardinality artifact"* — the fix mechanically
> resolves exactly the artifact that case's own adjudication named). Corrected self-validation:
> `tp=116/fn=71/recall=0.6203` (was `tp=115/fn=72/recall=0.6150`). Both decision-number readings move
> by less than half a percentage point and the verdict is unchanged: predeclared-formula H-inflated
> `59/71 = 83.1%` (was 83.3%), plain-verdict H-inflated `43/71 = 60.6%` (was 61.1%). The original
> tables below are left as the historical 72-case record; treat the corrected `71`-case denominator as
> current.

Executes: `docs/plans/exectv2_gepa_ev_recall_consolidation_reexamination_plan_2026-06-30.md` Phase 3
(SF extension, fresh predeclaration written into that plan's Phase 3 section same-day, per its own
instruction not to port Phase 1's method directly).

Companions:
- `docs/experiments/exectv2/diagnosis/exectv2_dx_ev_recall_consolidation_check_2026-06-30.md` —
  Phase 1, the Diagnosis check this extends (93.5% H-inflated for Dx).
- `docs/research/exectv2_gepa_vs_hybrid_evidence_decomposition_2026-06-28.md` — the doc whose SF
  evidence-recall framing this re-examines.
- `docs/experiments/exectv2/seizure_frequency/exectv2_sf_canonical_metric_row_analysis_2026-06-29.md`
  (Phase 7) — the SF `state_profile` adjudication this does **not** revise (different metric,
  different model run, different question; see §5).

## 1. Question

Phase 1 found that 93.5% of Diagnosis's `source_near` evidence-recall misses are not genuine
retrieval failures — they are cardinality artifacts (the model's text was retrieved but credited to
a sibling gold annotation) or clinically-defensible consolidation (gold split one fact into several
tags; the model's one tag is reasonable). Does the same mechanism inflate SeizureFrequency's
evidence-recall gap, the other large contributor to the evidence-decomposition doc's headline claim
(SF's FN re-keyable share was already the highest of the four families at 75%, per that doc's §3
table)?

SF has no `clinical_headline`-level intermediate miss list the way Dx's 92 `missed_concepts` did —
`state_profile` is a per-letter, type-agnostic 4-state set, not an annotation-keyed metric — so this
applies the H1/H2 split directly to SF's own `source_near` FN population on the GEPA-best run
(`exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628`, the same run Phase 1 and the
evidence-decomposition doc use), per the fresh predeclaration in the plan's Phase 3 section.

## 2. Method

`experiments/exectv2_sf_evidence_recall_consolidation_check.py` (mechanical split, zero LLM calls)
+ `experiments/exectv2_sf_evidence_recall_finalize.py` (merge + cross-tab).

**Self-validation gate:** the script's own `_first_overlapping_prediction`-respecting trace
reproduces the official `source_near` SeizureFrequency tp=115/fn=72/recall=0.6150 exactly —
**PASS**.

For each of the 72 SeizureFrequency `source_near` FNs (gold mentions with no matching predicted
phrase under the official, cardinality-respecting match), classified the mechanism:

- **H1_CARDINALITY** — an overlapping predicted phrase exists but was claimed by a sibling gold
  annotation first (49/72, 68.1%).
- **H2_GENUINE_DIVERGENCE** — no overlapping predicted phrase exists at all, under any matching
  (23/72, 31.9%; 8 of these had text overlapping a *different*-entity prediction, informational
  only).

Unlike Phase 1, there was no existing per-case clinical verdict for this population (the SF Phase 7
adjudication is letter-level, on a different model run, for a different metric — see §5). A fresh
adjudication was required: each of the 72 cases was given a full substrate (letter text, the missed
gold mention, all gold and predicted SeizureFrequency mentions in that letter, other-entity gold
context) and adjudicated independently by 4 parallel reviewers (general-purpose agents, ~15-22
cases each) using the same 3-way taxonomy as the Dx and SF-Phase-7 adjudications — `GOLD_RIGHT`
(genuine model error) / `MODEL_DEFENSIBLE` (model's output already covers the fact, different
phrasing/consolidation) / `BOTH_DEFENSIBLE` (genuine IAA-level ambiguity or known gold convention) —
explicitly instructed to judge each case fresh from the letter, not from the mechanism label.

## 3. Result

2×3 mechanism × verdict cross-tab (72 cases):

| mechanism | GOLD_RIGHT | MODEL_DEFENSIBLE | BOTH_DEFENSIBLE | total |
| --- | ---: | ---: | ---: | ---: |
| H1_CARDINALITY | 16 | 26 | 7 | 49 (68.1%) |
| H2_GENUINE_DIVERGENCE | 12 | 10 | 1 | 23 (31.9%) |
| **TOTAL** | **28 (38.9%)** | **36 (50.0%)** | **8 (11.1%)** | **72** |

**Two readings of the decision number, reported side by side because they diverge materially (an
unanticipated result, like Phase 1's `NOT_SOURCE_NEAR_FN` bucket):**

- **Predeclared formula** (mirrors Phase 1's Dx formula exactly: all of H1 counts as "inflated" by
  construction, since the model's text was retrieved somewhere; only H2-and-`GOLD_RIGHT` is the
  strict "unambiguous real miss" bucket): **H-inflated = 60/72 = 83.3%**, **H-genuine = 12/72 =
  16.7%**.
- **Plain verdict-only reading** (every `GOLD_RIGHT` case counts as genuine regardless of mechanism,
  since the clinical read is the more direct ground truth than the structural overlap proxy):
  **H-inflated = 44/72 = 61.1%**, **H-genuine = 28/72 = 38.9%**.

**Why they diverge:** 16 of the 49 H1_CARDINALITY cases (32.7%) were still adjudicated `GOLD_RIGHT`
— the model's overlapping text existed somewhere in the letter, but didn't actually capture the
*specific* clinical fact gold tagged separately (e.g. a count escalation 1→3, a distinct second
seizure type, a treatment-response/trend the model's structured output had no field to carry). This
is a much larger genuine-error share within H1 than Dx's (1/13 = 7.7%) — the cardinality mechanism
is necessary but far less sufficient evidence of "not a genuine miss" for SF than it was for Dx.

**Both readings clear the ≥50% H-inflated threshold.** VERDICT: **H-inflated CONFIRMED for SF**,
under either framing.

## 4. Interpretation

The same gold-multiplicity / cardinality-exhaustion mechanism that inflated Diagnosis's
evidence-recall gap also inflates SeizureFrequency's — a majority (61–83%, depending on how
conservatively H1 cases are credited) of SF's 72 `source_near` misses are not "the model never
retrieved this," they are scoring-mechanism artifacts or clinically-defensible consolidation. The
evidence-decomposition doc's §4/§5 framing — "the actionable lever for GEPA is retrieval, not
re-keying" — overstates genuine retrieval failure for SF in the same direction it did for
Diagnosis, though less dramatically (SF retains a much larger genuine-error residual than Dx: 28/72
= 38.9% plain-verdict `GOLD_RIGHT` vs Dx's 7/92 = 7.6%).

This is a **refinement, not a contradiction**, of the SF Phase 7 finding
(`exectv2_sf_canonical_metric_row_analysis_2026-06-29.md`) that SF has a genuine, gold-IAA-bounded
`state_profile` ceiling (~0.74–0.78) with a real ~28%-of-errors genuine-model-error component. Phase
7 adjudicated `state_profile` letter-level disagreements on the two-stage SF-verify run; this phase
adjudicates `source_near` annotation-level misses on the GEPA-best multi-family run — different
metric, different model run, different population — and both independently conclude SF carries a
materially larger genuine-error residual than Diagnosis. The two findings corroborate each other on
that point while correcting a *different* claim: not "is SF's ceiling gold-quality-bounded" (yes,
per Phase 7, unrevised) but "is SF's specific 0.694 `source_near` evidence-recall figure mostly
genuine retrieval failure" (no, mostly inflated by the same mechanism as Dx, per this phase).

**Practical implication for the GEPA-workstream lever priority:** for Diagnosis, Phase 1 showed the
genuine residual is tiny (6.5%) — re-keying/consolidation-aware projection is clearly the right
lever, already validated (0.703→0.792). For SF, the genuine residual is larger (17–39% depending on
reading) — re-keying still captures the *majority* of the apparent gap, but a meaningfully larger
share of SF's evidence-recall deficit than Dx's is real, unretrieved information, consistent with
the evidence-decomposition doc's own §3 table already ranking SF's mis-keyed share highest (75%,
computed by a coarser check) among the four families. A future SF-specific re-keying lever should
expect a real, non-trivial floor of genuine misses to remain — this does not change the closing
synthesis's framing (single-pass GEPA plateau is architectural, multi-lane extraction is the
residual lever) but sharpens which families would benefit most from re-keying vs. more retrieval.

## 5. Scope and caveats

- SeizureFrequency only, dev140, GEPA-best multi-family run, zero new LLM calls for the mechanical
  split. The clinical verdicts required a fresh adjudication pass (not zero-cost like Phase 1's
  reuse of existing verdicts) since no prior per-case `source_near`-population adjudication existed
  for SF — flagged explicitly in the plan's Phase 3 predeclaration as the reason this needed its own
  scoping rather than a direct port of Phase 1's method.
- The fresh adjudication was done by 4 independent parallel reviewers rather than a single pass;
  each reviewer flagged their own "torn calls" transparently (case-level notes preserved in
  `_adjudication.csv` and the reviewers' own reports), consistent with the genuine
  IAA-level ambiguity this domain has (SF human IAA = 0.47, the second-worst entity per Phase 6/7).
  A different reviewer could plausibly move a handful of borderline cases between `GOLD_RIGHT` and
  `BOTH_DEFENSIBLE`; the decision number is robust to this (both readings clear 50% by a wide
  margin, 11–33 percentage points above threshold).
- This does **not** revise the SF Phase 4–7 `state_profile` ceiling findings, which used their own
  adjudication on a different model run and a different metric and reached the
  gold-quality-ceiling conclusion independently (see §4).
- No deterministic repairs, no GEPA optimization, no prompt changes — pure re-analysis plus one
  bounded fresh clinical adjudication, per the plan's scope discipline.

## 6. Propagation

- Status-correction note added to
  `docs/research/exectv2_gepa_vs_hybrid_evidence_decomposition_2026-06-28.md`, extending the
  existing Dx-only correction banner to cover SF's evidence-recall framing too (same pattern,
  preserves original text).
- Status note added to `docs/plans/exectv2_gepa_focused_lanes_recall_plan_2026-06-28.md`'s existing
  correction banner, replacing "no adjudication-based correction has been run there [for SF]" with
  a pointer to this result and the refined (re-keying-still-dominant-but-larger-genuine-residual)
  framing.
- Plan status line in
  `docs/plans/exectv2_gepa_ev_recall_consolidation_reexamination_plan_2026-06-30.md` updated to
  reflect Phase 3 as executed (was: "not pursued, deferred").

## 7. Artifacts

- `experiments/exectv2_sf_evidence_recall_consolidation_check.py` — Phase 0/1 mechanical split +
  substrate dump, committed, reusable, zero-LLM.
- `experiments/exectv2_sf_evidence_recall_finalize.py` — merges adjudication batches, computes the
  cross-tab and both decision-number readings, writes `_sf_ev_recall/_adjudication.csv`.
- `experiments/exectv2_sf_evidence_recall_consolidation_check.json` — full per-case data (mechanism,
  verdict, reason, substrate) and final tallies.
- `docs/research/error_analysis/sf_ev_recall/` — 72 per-case adjudication substrate `.md` files + `_adjudication.csv`
  (case-level CSV: letter, mechanism, verdict, missed text/state, reason).
