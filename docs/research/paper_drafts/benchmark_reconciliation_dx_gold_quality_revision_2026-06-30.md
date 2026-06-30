# Benchmark-reconciliation revision — Diagnosis joins the gold-quality-ceiling mechanism (2026-06-30)

**Status:** Revision note to the P1 benchmark-reconciliation subsection, extending the
2026-06-29 SF revision (`benchmark_reconciliation_sf_gold_quality_revision_2026-06-29.md`)
to a second entity.
**Trigger:** the Diagnosis canonical row-analysis
(`docs/experiments/exectv2/diagnosis/exectv2_dx_canonical_row_analysis_2026-06-30.md`),
produced while applying `docs/research/predecessor_lessons/` to the current evidence base —
specifically answering the open question
`exectv2_gepa_single_model_plateau_synthesis_2026-06-28.md` reopened on 2026-06-28 and never
followed up: "the Diagnosis 'consolidation' finding is the same mechanism [as SF], so the
'architectural gap' framing is also in question."

## What changed and why

The 2026-06-29 SF revision split the benchmark gap into two mechanisms (A: closeable format
fidelity; B: non-closeable gold-quality ceiling) but treated Diagnosis as purely mechanism A,
alongside Prescription and Investigations. The Diagnosis row-analysis shows that account is
**incomplete for Diagnosis** too — and the effect is larger in absolute terms than SF's.

- **A — Format fidelity** (offset-drift + CUI + attribute-bundle strictness). Closeable
  deterministic engineering, explicitly deprioritised. Now dominant for **Prescription and
  Investigations only**.
- **B — Gold-quality ceiling** (low inter-annotator agreement for SF; annotation-granularity
  convention for Diagnosis). Not closeable by engineering. Dominant for **SeizureFrequency
  and Diagnosis**.

Diagnosis's mechanism-B driver is structurally different from SF's: not inter-annotator
*disagreement* (no IAA figure was computed for Diagnosis here) but annotation-granularity
*convention* — the gold routinely tags both a generic/parent concept and a specific/co-present
concept (or splits one compound diagnostic phrase into atomic fragments) from a single
diagnostic statement, scoring a clinically-reasonable single-tag consolidation as both a miss
and a false positive.

## The numbers (from the canonical row-analysis, official `concept_only` scorer)

- Official scorer wrong on **62.9%** of dev140 letters (88/140 carry a Diagnosis
  disagreement); aggregate F1 **0.6617** (self-validated bit-for-bit against the registry's
  recorded number for this run).
- 209 individual missed/spurious concept disagreements adjudicated (92 missed, 117 spurious).
- **31 (14.8%) genuine model error**, concentrated in two narrow, fixable patterns
  (negation-as-diagnosis, EEG-finding-as-diagnosis); **167 (79.9%) model defensible**
  (gold multiplicity/consolidation, canonicalization mismatch, gold under-annotation);
  **11 (5.3%) genuine ambiguity**.
- Clinically-adjusted aggregate: **F1 0.9501** (P 0.9252, R 0.9764) vs official 0.6617 — a
  **+0.288** gap, larger in raw terms than SF's reconciliation.

## Manuscript locations touched (`paper_manuscript_2026-06-26.md`)

1. **§4.1.2** — the "two distinct mechanisms" opening narrowed from "most entities" to
   "Prescription and Investigations" for mechanism A, and widened mechanism B from
   "SeizureFrequency" to "SeizureFrequency and Diagnosis"; the boxed paper statement
   updated to name both exceptions; **new paragraph "The same mechanism, more lopsided, on
   Diagnosis"** carrying the numbers above, placed immediately after the SF gold-quality
   paragraph.
2. **D.2 "Benchmark-Surface Inversion"** — same narrowing of the mechanism-A entity list;
   **new "fourth finding"** paragraph parallel to the SF "third finding" paragraph.
3. **§6 Contribution 1** — gap explanation reframed from "for most entities... second, for
   SeizureFrequency..." to name both SeizureFrequency and Diagnosis as mechanism-B entities,
   with both sets of numbers.

### NOT changed (flagged, left by decision — same disposition as the SF revision)

- Abstract and §1 still describe the benchmark gap in singular/aggregate fidelity terms.
  This was already an open, deliberate simplification before this revision (the SF revision
  flagged it as "mildly understated for SF"); it is now mildly more understated with
  Diagnosis added, but the aggregate-level framing is still directionally correct (fidelity
  still dominates Prescription/Investigations, which carry real engineering weight in the
  nine-entity surface). Left for an explicit decision on whether to tighten the
  highest-visibility prose, rather than silently rewritten here.
- The IEEE LaTeX draft (`literature/IEEE/IEEE-conference-template-062824/`) was not
  re-synced from this markdown source in this pass — a follow-up step, not done here.

## What did NOT change

- The format-fidelity account for Prescription/Investigations, the offset-drift rationale,
  Table R1, and the rules>hybrid inversion all stand.
- No numbers were re-run for SF; this revision only adds the parallel Diagnosis finding.
- The GEPA workstream's own "0.18 architectural gap is genuine recall" framing
  (`exectv2_gepa_single_model_plateau_synthesis_2026-06-28.md`) is now known to overstate
  genuine model error for Diagnosis in the same way the pre-Phase-7 SF framing did, but that
  doc is a research-workstream artifact, not manuscript prose; it is corrected via a status
  note at its head rather than rewritten (preserve negative-result history per BP9).

## Consequence for the GEPA workstream

The exhaustive co-present-enumeration schema work in
`exectv2_gepa_focused_lanes_recall_plan_2026-06-28.md` Phase 1 (targeting Diagnosis "56
genuine misses") was partly optimizing against a gold-consolidation artifact, not a pure
recall deficit — consistent with that plan's own Phase 3 finding that deterministic Dx
convention re-keying, not more retrieval, bought the larger, cleaner win (Dx 0.703 → 0.792).
No further single-pass Diagnosis "genuine recall" chasing is warranted on the strength of the
GEPA plateau's 56-miss count alone; the more reliable signal is now the per-concept-adjudicated
0.6617 → 0.9501 reconciliation in this doc.
