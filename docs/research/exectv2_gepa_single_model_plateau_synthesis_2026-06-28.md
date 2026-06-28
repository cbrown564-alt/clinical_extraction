# Synthesis — the single-model GEPA plateau on ExECTv2 de-dup `clinical_headline`

Status: **REOPENED for SeizureFrequency (2026-06-28).** §4–§5's "genuine recall, hand-rules only"
verdict for SF does not survive the predictions: the SF gap is dominated by the seizure-type-CUI
granularity lottery + gold's exhaustive per-type multiplicity (re-scoring the *same* preds under a
Gan-style state profile lifts SF 0.592→0.713), not recall. See
`docs/research/exectv2_sf_representation_not_recall_2026-06-28.md`. The Diagnosis "consolidation"
finding is the same mechanism, so the "architectural gap" framing is also in question.
Original status: **CLOSED (bounded negative).** Date: 2026-06-28.
Owner: ExECTv2 GEPA workstream.

Companions:
- `docs/plans/exectv2_gepa_multistage_program_scope_2026-06-28.md` (the multi-stage scope this follows from)
- `docs/research/exectv2_gepa_underperformance_investigation_2026-06-27.md` (the prior harness-bug investigation)

## 1. Question

Single-pass GEPA had reached **dev140 `clinical_headline` F1 0.731** (per-family, after the
H1 diff-feedback + H2 minibatch fixes) — beating the hand-tuned single prompt (0.710) but
plateauing **~0.18 below the v08 multi-stage hybrid (0.9155).** This investigation asked
whether that remaining gap is reachable by a *single model*, testing — in order — every
plausible lever, and localizing the gap if not.

## 2. Result: a robust ~0.73 plateau across six configurations

| configuration | dev140 headline F1 | note |
| --- | ---: | --- |
| monolith (single instruction) | 0.702 / 0.719 | H1 / H2 |
| **per-family (4 instructions)** | **0.731** | prior best |
| multi-stage (generate→verify) | 0.7235 | failed kill-criterion (−0.008) |
| uniform recall-weight (F-β=2) | 0.7213 | Dx↑0.700, precision↓ |
| per-family recall-weight (Dx β=2) | 0.7213 | Dx↓0.645, more parsimonious |
| CUI/UMLS normalization (re-score) | 0.709 | hurt (over-collapse) |

The aggregate does not move past **~0.73** under any architecture or objective. Precision
and recall can be traded (recall pushed to 0.771; Diagnosis pushed to 0.700) and points
shuffled between families, but the headline is invariant. This is the central finding.

## 3. What each lever ruled out

- **Multi-stage architecture (Phase 1 of the scope).** An evolvable per-family
  generate→verify program, S0 warm-started from the 0.731 run, scored **0.7235** — failing
  the pre-registered kill-criterion (beat 0.731 by ≥ +0.03). Mechanism (evolved-instruction
  inspection): (a) verify on an already-precision-tuned generator only *filtered*, cutting
  recall (805→783 facts); (b) coarse final-fact credit assignment mis-fed the verifiers —
  the one heavily-evolved verifier drifted into "output a complete corrected list in
  hyphenated-lowercase canonical representation", i.e. *reformatting*, not verifying.

- **Surface-convention normalization.** A maximally convention-tolerant surface
  (span-overlap, ignoring the canonical key) lifts 0.731 only to **0.751 (+0.02).** Both
  0.731 and the 0.9155 hybrid already sit on the lenient `clinical_headline`; convention is
  not where the gap is.

- **CUI/UMLS concept normalization.** Re-scoring through an in-sample CUI normalizer **hurt**
  (overall 0.731→0.709; Diagnosis 0.662→0.605). The gold benchmark's "convention" is a
  *surface/granularity* convention, not a CUI-semantic identity: CUI over-collapses
  distinctions the gold scores separately (e.g. *genetic generalised epilepsy* [3] vs
  *generalised epilepsy* [9]). UMLS would not fix this — it is a gold-vs-ontology granularity
  property. (The CUI infra is also gold-derived/SF-only today; a test-safe version needs real
  UMLS, tracked separately, but the structural conflict stands regardless.)

- **Deterministic exhaustiveness expansion.** Parent-expanding every predicted Diagnosis up
  `DIAGNOSIS_PARENT` (78 added mentions) recovered **0.000** — the scorer already collapses
  parent/child to most-specific on both sides, so the gold's multiplicity is genuinely
  *distinct co-present concepts*, not parent redundancy. No mechanical shortcut exists.

- **Objective weighting (recall).** Uniform F-β=2 did exactly what it should where the gap is
  "emit more co-present concepts" — **Diagnosis 0.662→0.700**, the best Dx in the workstream,
  proving the parsimonious optimum is real and escapable — but it over-emitted on
  precision-sensitive families (Investigations 0.858→0.783) and SF (state, not volume),
  netting flat. The per-family refinement (Dx β=2 only, macro objective) failed to isolate
  the gain and regressed (Dx 0.645).

## 4. Where the gap actually is

The ~0.16 residual to the hybrid is **genuine recall**, characterized on the 0.731 preds
(`experiments/exectv2_genuine_recall_analysis.py`):

- **Diagnosis — 56 genuine misses** (concepts with *no* overlapping prediction; 55/56 in
  letters where the model emitted *other* diagnoses → per-concept omission): 52% specific
  epilepsy syndrome, 20% named seizure type, 14% generic *epilepsy*, 14% other. The model
  **consolidates** where the gold tags every co-present concept (e.g. *"focal
  epilepsy-Probable temporal"* → both focal epilepsy **and** temporal lobe epilepsy).
- **SeizureFrequency — 19 genuine misses:** 53% seizure-free, 32% changed, 16% active. The
  gap is **state detection** (recognizing absence/change), not emission volume.

These are exactly the behaviors the hybrid's hand-tuned `entity_verifier` clinical rules +
worked-examples encode (emit generic epilepsy too; keep named seizure types; don't dedup
separately-supported assertions; seizure-free / drug-change detection).

## 5. Conclusion

**Single-model instruction optimization on the de-dup `clinical_headline` surface plateaus at
~0.73**, ~0.18 below the v08 hybrid (0.9155). The gap is genuine recall — co-present
Diagnosis concepts and SeizureFrequency seizure-free/changed detection — recoverable only by
the hybrid's **hand-curated rule/example corpus**, not by GEPA instruction tuning, program
architecture, semantic/CUI normalization, deterministic projection, or objective weighting.

The hybrid's 0.9155 is therefore **not** primarily convention conformance (only ~+0.02 is
surface convention) but real recall recovery driven by curated per-family verification — i.e.
its edge *is* that corpus. This is a clean boundary on what single-model prompt-evolution can
do on this task.

## 6. Artifacts (this investigation)

Diagnostics (zero-LLM, read-only):
- `experiments/exectv2_convention_tax_analysis.py` — surface ladder + convention tax + CUI headroom
- `experiments/exectv2_genuine_recall_analysis.py` — genuine-recall-miss characterization
- `experiments/exectv2_exhaustiveness_probe.py` — deterministic parent-expansion probe (0.000)

Infra built:
- `src/.../exectv2/gepa/program_multistage.py` — evolvable generate→verify program (+ `tests/test_exectv2_gepa_multistage.py`)
- `src/.../exectv2/deterministic/concept_normalizer.py` — swappable concept-normalizer seam (in-sample stub; UMLS drop-in placeholder)
- `gepa/metric.py` — `recall_beta` (F-β) + `family_beta` (macro per-family) selection objectives
- launchers: `experiments/gepa_multistage_exectv2.py`, `experiments/gepa_recall_exectv2.py`

Runs (dev140, mini): `exectv2_gepa_multistage_dedup_gpt41mini_20260628` (0.7235),
`exectv2_gepa_recall_dedup_gpt41mini_b2p0_20260628` (0.7213),
`exectv2_gepa_recall_perfamily_dedup_gpt41mini_20260628` (0.7213).

## 7. What this leaves open (not pursued here)

- The hybrid's curated corpus is the established way to the gold's exhaustive convention; the
  open strategic question is whether to **accept the hybrid**, **curate the corpus further**,
  or **pivot the evaluation surface** to a clinical-recovery story where the benchmark's
  exhaustive-tagging convention does not dominate (the unowned benchmark-metric pivot).
- A test-safe CUI/UMLS normalizer (real MRCONSO, not the gold-derived stub) remains a
  separate follow-up, but §3 shows CUI is not the lever for this benchmark's granularity.
- `test60` was never touched; all numbers are dev140 (development surface).
