# Pipeline assumption audit — D1 Diagnosis specificity-collapse fix (result)

Date: 2026-07-02. Owner: ExECTv2 workstream.
Plan: `docs/plans/exectv2_pipeline_assumption_audit_plan_2026-07-02.md` (Phase 1b, D1).
Phase 0 inventory: `docs/research/exectv2_pipeline_assumption_audit_2026-07-02.md` (row D1).
Phase 1 (other three bugs): `docs/research/exectv2_pipeline_assumption_audit_phase1_2026-07-02.md`
("Held for a decision: D1").
Hypothesis: `dx_specificity_collapse_cross_contamination_2026-07-02`.

All measurements are dev140 re-scores of the cached predictions for
`exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628` (zero new LLM calls).

## The bug (D1)

`collapse_diagnoses_to_most_specific`
(`deterministic/normalization.py`, ~L288) drops a Diagnosis parent concept when a
descendant is present **on the same side**. In the scoring path
(`scoring/match.py` `_score_concept_identity` → `_concept_keys` →
`collapse_concepts_to_most_specific`) it runs **independently on the gold side and
the prediction side before the intersection**. So when per-side collapse keeps a
*parent* on one side and a *descendant* on the other, the two never meet by exact
key equality and a verbatim-correct diagnosis is scored as a paired FN+FP.

Canonical example (hypothesis statement): gold `[epilepsy]` vs pred
`[epilepsy, focal epilepsy]` → pred-side collapse drops `epilepsy`, leaving
gold `{epilepsy}` vs pred `{focal epilepsy}` → F1 = 0 despite the model emitting
`epilepsy` verbatim. 34/140 dev letters carry a gold parent+child pair.

## The fix

Matching-time reconciliation in the scoring path — **no source annotations are
mutated**, and per-side collapse is unchanged. Two edits:

1. `deterministic/normalization.py` — new `concepts_hierarchically_related(a, b)`:
   `True` iff `a` and `b` are identical or one is an ancestor/descendant of the
   other in `DIAGNOSIS_PARENT`. It **reuses the existing `_has_specific_descendant`
   helper** (called both directions) so the scorer's hierarchy match and the
   per-side collapse share one relation definition.
2. `scoring/match.py` — new `_concept_overlap_count(gold, pred, entity, variant)`
   replaces the inline `sum((gold & home_pred).values())` /
   `sum((gold & recall_pool).values())` in `_score_concept_identity` (used for
   **both** precision and recall). It first counts exact multiset matches, then —
   **only for `entity == "Diagnosis"` and `variant == "concept"`
   (i.e. `clinical_headline` / `concept_only`)** — greedily reconciles the
   *leftover* keys across the hierarchy via `concepts_hierarchically_related`.
   Matching is cardinality-bounded (`min` of remaining counts), so the credited
   count can never exceed either side's unit count, and only true
   ancestor/descendant pairs are reconciled.

Every other `(entity, variant)` — the `concept_negation` and `concept_assertion`
diagnostics, and any non-Diagnosis entity — takes the early return and is
**byte-identical** to the prior exact-intersection behaviour. The GEPA training
metric (`gepa/metric.py`, `run_gepa.py`) scores Diagnosis on `concept_negation`,
so it is unaffected.

## Result (dev140, `exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628`)

Diagnosis `clinical_headline` (`score_concept_identity(...).concept_only`):

| | Precision | Recall | F1 | precision_tp | recall_tp | pred_count | gold_count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **BEFORE** | 0.6355 | 0.6902 | **0.6617** | 204 | 205 | 321 | 297 |
| **AFTER**  | 0.6511 | 0.7071 | **0.6779** | 209 | 210 | 321 | 297 |
| Δ | +0.0156 | +0.0169 | **+0.0162** | +5 | +5 | 0 | 0 |

The BEFORE number reproduces the cited `0.6617` **exactly** (self-validated
before trusting the AFTER number). Denominators are unchanged: the fix converts
5 paired FN+FP into 5 TP (both precision and recall), it does not add or remove
any predicted or gold unit.

### Letters recovered (5)

Each is a genuine ancestor/descendant recovery, and in **every** case the credited
prediction concept was literally present in the gold annotation *before* per-side
collapse (`pred_matched_in_gold_raw = True`) — a pure repair of the collapse
artifact, not an over-credit:

| Letter | gold (collapsed) | pred (collapsed) | reconciled pair (gold ↔ pred) | direction |
| --- | --- | --- | --- | --- |
| **EA0002** | temporal lobe epilepsy, … | focal epilepsy, … | temporal lobe epilepsy ↔ focal epilepsy | gold-side collapse |
| **EA0006** | generalised epilepsy, … | epilepsy, … | generalised epilepsy ↔ epilepsy | gold-side collapse |
| **EA0007** | focal epilepsy | epilepsy, focal seizures | focal epilepsy ↔ epilepsy | gold-side collapse (was 0→1) |
| **EA0035** | generalised epilepsy, … | epilepsy, … | generalised epilepsy ↔ epilepsy | gold-side collapse |
| **EA0153** | temporal lobe epilepsy, … | focal epilepsy, … | temporal lobe epilepsy ↔ focal epilepsy | gold-side collapse |

All five are the *symmetric* (gold-side collapse) form of the bug: gold richly
annotated a parent+child pair, the model emitted the parent verbatim, and gold-side
collapse hid the parent before the intersection. The canonical pred-side example
from the hypothesis statement (pred has parent+child, gold has only the parent)
occurs for only **1** dev140 letter, and on that letter collapse did not destroy a
match, so it is not among the 5.

### "34 → 5": the plan's estimate was an upper bound

34/140 letters carry a gold parent+child pair, but only **5** produce a scoring
artifact. In the other 29 the model either matched the specific child directly or
genuinely missed the concept (no hierarchy-related leftover pair exists to
reconcile) — verified letter-by-letter. The plan's "recover the ~34 paired FN+FP"
was the population of at-risk letters, not the realized defect; the honest measured
impact is +5 TP / +0.0162 F1.

## Kill-criterion verdict: **MET**

Kill criterion: *the hierarchy-aware match must not credit a pred descendant
against an unrelated gold concept (only true ancestor/descendant relations, via
`_has_specific_descendant`, may match); net effect must lower the genuine-model-
error residual, not spuriously raise recall.*

- **Only true ancestor/descendant pairs match** — `concepts_hierarchically_related`
  walks the `DIAGNOSIS_PARENT` chain via `_has_specific_descendant`; siblings
  (e.g. focal epilepsy vs generalised epilepsy) and unrelated concepts return
  `False`. A unit test (`test_diagnosis_headline_does_not_credit_unrelated_sibling_concept`)
  and a direct predicate test lock this in.
- **No spurious cross-credit on the run** — all 5 recovered pairs are true
  ancestor/descendant relations *and* the credited pred concept was in gold
  pre-collapse. Zero unrelated matches.
- **Lowers the genuine-error residual** — the fix converts 5 disagreements into
  matches; it does not touch precision denominators, so it cannot inflate recall
  by manufacturing units. This reinforces (does not threaten) the manuscript's
  Diagnosis "85.2% gold-artifact" framing: the raw baseline the adjustment starts
  from rises 0.6617 → 0.6779, i.e. 5 of the disagreements previously counted as
  needing adjudication are now resolved at the scorer level.

## Regressions

None in scope. Full `tests/test_exectv2_scoring.py` (56) plus the Diagnosis /
normalization / reliability selection (80 total) pass. The `concept_negation`,
`concept_assertion`, and all non-Diagnosis paths are unchanged by construction.

## Blast radius (documented, not acted on here)

Consistent with the Phase 1 finding that the reliability scorecard is
live-computed from the scorer, this Diagnosis change also shifts the
Diagnosis-dependent reliability cells:

- `tests/test_exectv2_final_consolidation.py::test_static_frontend_scorecard_matches_builder_contract`
  is **already red by design** (the Phase 1 Prescription/SF scorer fixes diverge
  the builder from the frozen static cache pending the citation-policy decision).
  This change adds to that same delta; it does not newly break the test.
  Regenerating `frontend/public/mock-data/exectv2/reliability-scorecard.json` (via
  the sanctioned `scripts/build_exectv2_reliability_scorecard_data.py`) is the same
  pending gated step — `frontend/**` is out of scope for this fix.
- The naive `set`-based per-letter decomposition in
  `experiments/exectv2_dx_canonical_row_analysis.py` is hierarchy-unaware, so its
  `decomposition_matches_official` self-check now prints `False` for the 5
  recovered letters (official 0.6779 vs its 0.6617 decomposition). The Diagnosis
  canonical adjudication substrate and the downstream 0.6617→0.9501 adjusted-F1 /
  85.2%-artifact figures are computed off that script and the `_adjudication.csv`;
  regenerating them (and updating the manuscript/dossier citations) is the
  parent-owned citation-update / re-adjudication step, not part of this scorer fix.

## Files changed

- `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/normalization.py`
  — added `concepts_hierarchically_related` (reuses `_has_specific_descendant`).
- `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/scoring/match.py`
  — added `_concept_overlap_count` and `_DIAGNOSIS_ENTITY`; routed
  `_score_concept_identity` precision/recall through it; imported the relation
  helper.
- `tests/test_exectv2_scoring.py` — added 6 tests (relation predicate + two
  recovery directions + unrelated-sibling guard + exact-match regression +
  cardinality-bound).
