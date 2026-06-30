# Benchmark-reconciliation revision — the SF gap is two mechanisms, not one (2026-06-29)

**Status:** Revision note to the P1 benchmark-reconciliation subsection
(`benchmark_surface_reconciliation_subsection_2026-06-27.md` → manuscript §4.1.2).
**Trigger:** the SF canonical metric row-analysis
(`docs/experiments/exectv2/seizure_frequency/exectv2_sf_canonical_metric_row_analysis_2026-06-29.md`),
produced after the closing campaign closed (2026-06-27), supplies a gap mechanism the
06-27 subsection did not have.

## What changed and why

The 06-27 reconciliation attributed the **entire** benchmark gap (like-for-like dev140
0.3877/item vs paper 0.87) to **one** mechanism: offset-drift non-reproducibility plus
closeable CUI / attribute-bundle fidelity engineering — i.e. "the gap is closeable
fidelity, not a broken metric." The SF canonical row-analysis shows that account is
**incomplete for SeizureFrequency**, the benchmark's weakest (0.66/item) and
lowest-IAA (0.47) entity.

The benchmark gap is now stated as **two distinct mechanisms**:

- **A — Format fidelity** (offset-drift + CUI + attribute-bundle strictness).
  Closeable deterministic engineering, explicitly deprioritised. Dominant for
  Diagnosis, Prescription, Investigations.
- **B — Gold-quality ceiling** (low inter-annotator agreement). **Not** closeable by
  any engineering. Dominant for SeizureFrequency.

SF is the corpus's cleanest worked example of mechanism B: a clinically-correct reader
is scored wrong on ~⅓ of letters because the gold under-annotates / double-tags.

## The numbers (from the canonical row-analysis, two-stage SF program, state_profile metric)

- Verifier-stage per-letter answer wrong on **37.9%** of dev140 (F1 **0.772**).
- Of 53 metric-errors: **15 (28%) genuine model error**; **22 (42%) model defensible,
  gold under-annotated (13) or redundantly double-tagged (9)**; **16 (30%) genuine
  IAA/convention coin-flips**.
- Counting only genuine model errors: clinically defensible **125/140 = 89.3%** vs
  metric **62.1%** → 27-point gap is gold noise.
- Metric noise: **±0.03 run-to-run**; identical program flips state-set on **41/140**
  letters from temp-0 nondeterminism → report SF as a band, never a single decimal.
- Residual attributable model lever ≈ **15 letters**, rule-shaped (temporal discipline
  + state-evidence discipline), already in the deterministic projection.
- Caveat: 89.3% mildly optimistic (34/53 errors trainset, 19/53 valset); error
  structure consistent across splits.

## Manuscript locations touched (`paper_manuscript_2026-06-26.md`)

1. **§2.1** SF-weakest mention — added "lowest-agreement entity… caps achievable F1…
   dominant component of our SF benchmark gap (§4.1.2)."
2. **§4.1.2** — opening gap sentence rewritten to "two distinct mechanisms"; boxed
   paper statement qualified with the SF gold-quality exception; **new paragraph "A
   second gap mechanism: gold quality, most acutely on SeizureFrequency"** carrying the
   numbers above.
3. **§6 Contribution 1** — gap explanation reframed from one mechanism to two; SF
   gold-quality ceiling stated.

### Coherence-pass follow-up (same session, after full-manuscript read)

4. **§4.1.2** — the new mechanism-B paragraph's first mention of the metric now anchors
   it: "primary SF state-set metric (a per-letter clinical-recovery scorer over
   {active-rate, seizure-free, changed, unknown} — finer than four-family
   `clinical_headline`, not the published-benchmark surface)." Removes the third-surface
   ambiguity.
5. **D.2 "Benchmark-Surface Inversion"** — qualified "the gap is not a measurement
   artifact" to "for most entities…", flagged SF as the exception, and added a third
   paragraph carrying the gold-quality decomposition (28/42/30 split, 89.3% vs 62.1%,
   ±0.03 band). Makes D.2 consistent with §4.1.2 (it previously told the single-mechanism
   story).
6. **D.3 "The Wall"** — added a "Reconciling the wall and the gold-quality ceiling"
   paragraph: the wall (confident over-reading) is the ~28% genuine-error slice; the
   other ~72% is gold-quality noise; both converge on "SF ceiling = task/annotation, not
   system." Also clarifies the 0.9053 adjudicated figure is the `clinical_headline`
   surface / partly in-sample, so it does not contradict the state-set gold ceiling.
   Resolves the C3↔C1 tension the gold-quality edit introduced.

NOT changed (flagged, left by decision): Abstract (`:55`) and §1 (`:104`) still describe
the benchmark gap as singular all-fidelity; correct at the aggregate level where fidelity
dominates, mildly understated for SF.

## What did NOT change

- The format-fidelity account, the offset-drift rationale, Table R1, and the
  rules>hybrid inversion all stand — mechanism A is still dominant for Dx/Rx/Inv.
- No numbers were re-run; this is a framing reconciliation consuming an existing
  artifact.

## Consequence for the SF workstream

SF single-pass `state_profile` optimisation is closed (the ~0.74–0.78 wall is inside
the gold-quality ceiling + ±0.03 noise band). The thesis-facing deliverable is this
two-mechanism reconciliation, not another SF point. The only remaining attributable
model work is the ~15-letter deterministic projection.
