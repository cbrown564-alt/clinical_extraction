# Does gold-consolidation inflate the GEPA-vs-hybrid evidence-recall gap? — Diagnosis check

Status: **CLOSED (H-inflated CONFIRMED, 93.5% >> 50% threshold).** Date: 2026-06-30.
Owner: ExECTv2 GEPA workstream / predecessor-lessons application follow-up.

Executes: `docs/plans/exectv2_gepa_ev_recall_consolidation_reexamination_plan_2026-06-30.md`.

Companions:
- `docs/experiments/exectv2/diagnosis/exectv2_dx_canonical_row_analysis_2026-06-30.md` — the
  Diagnosis gold-quality finding that motivated this plan (85.2% of *scored* `clinical_headline`
  disagreements are gold multiplicity, not genuine model error).
- `docs/research/exectv2_gepa_vs_hybrid_evidence_decomposition_2026-06-28.md` — the doc whose
  central evidence-recall claim this re-examines (GEPA evidence-recall 0.694 vs hybrid 0.883,
  "almost entirely LLM evidence retrieval").

## 1. Question

The evidence-decomposition doc attributed the GEPA→hybrid `clinical_headline` gap (0.731→0.920)
almost entirely to LLM evidence-retrieval, using `source_near` (phrase-substring overlap,
same-entity, greedy 1:1 `used_pred` consumption) as its evidence-presence metric. The Diagnosis
canonical row-adjudication (same date) separately found that 85.2% of the *scored*
`clinical_headline` gap is gold multiplicity (concept-key matching scores a model's reasonable
one-tag consolidation as both a miss and a false positive when gold splits one diagnostic
statement into a generic + specific tag). Because `clinical_headline` and `source_near` use
different matching logic (concept-key identity vs phrase-substring overlap), it was open whether
the same consolidation mechanism also inflates the evidence-recall number, or whether
evidence-recall is measuring a genuinely separate retrieval gap.

## 2. Method

`experiments/exectv2_dx_evidence_recall_consolidation_check.py`, zero new LLM calls, reusing the
cached GEPA per-family run (`exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628`) and the
already-adjudicated `_dx_canonical/_index.json` + `_adjudication.csv` (92 Diagnosis `MISSED`
verdicts from the canonical row-analysis).

For each of the 92 `clinical_headline` Diagnosis missed concepts, mapped back to its underlying
gold `ExectAnnotation`(s), ran the exact `_first_overlapping_prediction` logic `source_near` uses
against home-tagged Diagnosis predictions, twice:

1. **Respecting `used_pred`**, in the same per-letter traversal order `_source_near_entity` uses
   (shared cardinality state across all of a letter's gold Diagnosis annotations) — the official
   mechanism.
2. **Ignoring `used_pred`** (fresh empty set per annotation) — does any home-tagged Diagnosis
   prediction phrase-overlap exist at all, regardless of cardinality.

Classified each missed concept into:
- **H1_CARDINALITY** — overlap exists ignoring `used_pred`, absent respecting it (a
  cardinality/exhaustion artifact: the model's text *was* retrieved, but another gold annotation
  claimed the matching prediction first).
- **H2_GENUINE_DIVERGENCE** — no overlap exists either way.
- **NOT_SOURCE_NEAR_FN** (an unanticipated third bucket the plan's binary framing didn't predict)
  — matched even respecting `used_pred`. This concept is a `clinical_headline` miss (concept-key
  identity didn't match) but is **already a `source_near` true positive** — the looser
  phrase-overlap match credits the evidence despite the concept-key mismatch.

Cross-tabulated each bucket against the existing adjudication verdict (`GOLD_RIGHT` /
`MODEL_DEFENSIBLE` / `BOTH_DEFENSIBLE`) for that exact `(letter, MISSED, concept)` triple.

**Self-validation gate:** the script's own `used_pred`-respecting trace reproduces the official
`source_near_diagnostic` Diagnosis tp/fn exactly (tp=241, fn=164, recall=0.5951) before the Phase 1
classification is trusted — **PASS**.

## 3. Result

2×3 mechanism × verdict cross-tab (92 missed concepts):

| mechanism | GOLD_RIGHT | MODEL_DEFENSIBLE | BOTH_DEFENSIBLE | total |
| --- | ---: | ---: | ---: | ---: |
| H1_CARDINALITY | 1 | 12 | 0 | 13 (14.1%) |
| H2_GENUINE_DIVERGENCE | 6 | 40 | 5 | 51 (55.4%) |
| NOT_SOURCE_NEAR_FN | 0 | 28 | 0 | 28 (30.4%) |
| **TOTAL** | **7** | **80** | **5** | **92** |

(Column totals exactly match the canonical row-analysis's MISSED-direction verdict marginals —
GOLD_RIGHT=7, MODEL_DEFENSIBLE=80, BOTH_DEFENSIBLE=5 — an internal consistency check.)

**The decision number (plan §3 kill-criterion):**

- **H-inflated bucket** (H1_CARDINALITY + NOT_SOURCE_NEAR_FN + H2-but-MODEL_DEFENSIBLE/BOTH_DEFENSIBLE):
  **86/92 = 93.5%**
- **H-genuine bucket** (H2_GENUINE_DIVERGENCE ∩ GOLD_RIGHT, the only unambiguous "real,
  attributable retrieval miss" bucket): **6/92 = 6.5%**

**VERDICT: H-inflated CONFIRMED** (well above the ≥50% threshold). This holds even under the most
conservative read that excludes the unanticipated `NOT_SOURCE_NEAR_FN` bucket entirely from the
denominator (treating it as out of scope rather than folding it into "inflated"): of the remaining
64, H1+H2-defensible = 58/64 = 90.6%, genuine = 6/64 = 9.4%. The result is decisive either way.

Informational, not folded into the split: of the 51 H2_GENUINE_DIVERGENCE cases, 9 had overlapping
text under a *different* entity label than Diagnosis (the model retrieved the phrase but tagged it
elsewhere) — a related, smaller effect, consistent with the broader pattern that most "no overlap"
cases are not the model failing to engage with the text at all.

A worked example (`EA0002`, also cited in the canonical row-analysis): gold splits one diagnosis
line into "focal epilepsy" + "temporal lobe epilepsy"; the model emits "focal epilepsy" (the
generic parent). "Temporal lobe epilepsy" has no phrase-overlap with anything the model predicted,
so it correctly classifies as H2_GENUINE_DIVERGENCE — but the adjudication verdict is
MODEL_DEFENSIBLE (the model's generic tag is clinically a reasonable consolidation, not a retrieval
failure). This is exactly the mechanism the plan's §2 H2 hypothesis predicted: a real phrase-level
divergence that nonetheless correlates with `MODEL_DEFENSIBLE`, not genuine model error.

## 4. Interpretation

The same gold-consolidation mechanism that inflates the *scored* `clinical_headline` Diagnosis gap
also inflates the *evidence-recall* gap, and more thoroughly than the plan's two-bucket hypothesis
anticipated: fully **30.4%** of the 92 "missed" concepts are not source_near false negatives at
all (the looser phrase-overlap match already credits them as retrieved), on top of the 14.1%
cardinality artifacts and the 43.5% (40+5 of 92) genuine-phrase-divergence-but-clinically-defensible
cases. Only **6.5%** of Diagnosis's contribution to GEPA's evidence-recall deficit is an
unambiguous case of "the model did not retrieve this and it should have."

This means the evidence-decomposition doc's Diagnosis-specific framing — "Diagnosis... misses are
dominated by genuine non-retrieval (Dx 56/101)" (§3 of that doc, computed via a coarser, separate
text-overlap-only check with no cardinality distinction and no clinical adjudication) — materially
overstates genuine retrieval failure for Diagnosis. It is not that the evidence-recall metric is
broken; it is that a `clinical_headline`-level miss is a poor proxy for "the model didn't retrieve
this," because gold's habit of splitting one diagnostic statement into multiple concept-key-distinct
tags produces misses whose underlying text was either retrieved-but-claimed-elsewhere (H1),
retrieved-and-already-credited-by-source_near (NOT_SOURCE_NEAR_FN), or genuinely-divergent-text but
clinically-equivalent (H2 + MODEL_DEFENSIBLE).

The same plan's own execution history (`exectv2_gepa_focused_lanes_recall_plan_2026-06-28.md` §6b)
already validated the practical implication of this finding by accident: Phase 1's recall-oriented
producers (the "make Dx retrieve exhaustively" lever this plan's framing motivated) lifted Dx only
modestly (0.662→0.703), while Phase 3's **deterministic re-keying** (no new retrieval at all) bought
the larger, cleaner win (0.703→0.792). That outcome is exactly what this analysis predicts: the
Diagnosis residual was mostly a keying/consolidation-convention problem, not a retrieval problem,
and the cheaper, already-validated lever (consolidation-aware deterministic projection) was the
right one — the "build more retrieval lanes" framing for Diagnosis specifically was the less
efficient bet, even though it happened to also produce a smaller real gain.

## 5. Scope and caveats

- Diagnosis only, dev140, zero new LLM calls — exactly as predeclared. SF/Rx/Inv extension is
  explicitly out of scope here (no adjudication data exists for Rx/Inv; SF's metric does not share
  this matching logic and needs its own mechanism hypothesis, per the plan's §5 Phase 3).
- This is a re-analysis of an *existing* adjudication (today's 92 Diagnosis MISSED verdicts),
  treated as ground truth per the plan's non-goals; if those verdicts are later revised, these
  numbers would need a re-run.
- The `NOT_SOURCE_NEAR_FN` bucket was not anticipated by the plan's binary H1/H2 framing but is
  reported transparently rather than forced into one of the two predeclared buckets, per the
  plan's own instruction to report partial/unexpected results rather than force a binary verdict.
- No deterministic repairs, no GEPA optimization, no prompt changes — pure re-analysis of numbers
  already on disk, per the plan's scope.

## 6. Propagation

Per plan §5 Phase 2 (triggered, H-inflated ≥50%):
- Status-correction note added to
  `docs/research/exectv2_gepa_vs_hybrid_evidence_decomposition_2026-06-28.md` (preserves original
  text, dated correction banner, same pattern as the 2026-06-30 note on the plateau synthesis doc).
- Status-correction note added to `docs/plans/exectv2_gepa_focused_lanes_recall_plan_2026-06-28.md`
  on its Diagnosis-specific framing (§1 and Phase 1 item 2).
- No manuscript change: per the plan, the GEPA workstream's numbers are already scoped as
  development-surface, non-paper-comparable diagnostics; this finding stays inside the
  GEPA-workstream research docs.

## 7. Artifacts

- `experiments/exectv2_dx_evidence_recall_consolidation_check.py` — committed, reusable, zero-LLM.
- `experiments/exectv2_dx_evidence_recall_consolidation_check.json` — committed; full per-concept
  classification + cross-tab (regenerable by re-running the script).
