# LLM-vs-hybrid Investigations comparator — results

Date: 2026-07-03. Owner: ExECTv2 workstream.
Hypothesis: `inv_llm_precision_vs_hybrid_inversion_2026-07-03` — **REFUTED.**
Predeclarations: dev140 (this doc) + `exectv2_inv_llm_vs_hybrid_full200_predeclaration_2026-07-03.md`.

## Setup

The best-possible LLM-tuned Investigations extractor: the canonical GEPA
multifamily `investigation` instruction + a **precision-side delta**
(completed-neuro-investigations-only, drop planned/awaited, emit-if-unsure
safety clause — the direct analog of the Rx AED-only precision gate). Run
through the full v08 hybrid assembly with same-day baseline+treatment
isolation (P7 audit method), swapping only the Investigations producer
(`investigations_arbitration_v02`), keeping the `investigations_result_v01`
lens common to both arms.

Model: gpt-4.1-mini, temp 0, cache on. The LLM arm's evidence spans are grounded
to exact note substrings (the assembly's evidence-grounding invariant requires
it; modality tokens are short and unambiguous, so the grounding is more
reliable than the Rx driver's drug-name location dance).

This targets the **precision side** because the recall side (MRI-crowds-EEG)
was already targeted and REFUTED (hypothesis 2026-07-01: the dedicated
anti-anchoring GEPA lane matched but didn't beat an untargeted model swap).
The deterministic producer is a bare surface-token anchor (`EEG|MRI|CT`, no
neuro-investigation scope gate), so an LLM with contextual completion judgment
was the plausible precision-side inversion candidate.

## Results

### dev140

| Producer (Inv `clinical_headline`, v08 assembly) | F1 | P | R | TP/FP/FN |
| --- | ---: | ---: | ---: | --- |
| **Hybrid Inv lane (baseline)** | **0.9132** | 0.9380 | 0.8897 | 121/8/15 |
| LLM-tuned (precision-completed-only) | 0.8949 | 0.9504 | 0.8456 | 115/6/21 |

### full-200 (aggregate-only, frozen protocol)

| Producer (Inv `clinical_headline`, v08 assembly) | F1 | P | R | TP/FP/FN | Overall |
| --- | ---: | ---: | ---: | --- | ---: |
| **Hybrid Inv lane (baseline, currentcode)** | **0.9213** | 0.9480 | 0.8962 | 164/9/19 | **0.8616** |
| LLM-tuned | 0.9080 | 0.9576 | 0.8634 | 158/7/25 | **0.8593** |

## The finding: NO inversion — the hybrid wins on both splits

**Hypothesis REFUTED.** The split-dependent inversion does NOT generalize from
Rx to Investigations. The hybrid Inv lane beats the LLM-tuned extractor on
**both** splits, by a similar margin and with the **identical mechanism**:

- dev140: Δ −0.0183 (LLM precision +0.0124, recall −0.0441)
- full-200: Δ −0.0133 (LLM precision +0.0096, recall −0.0328)

On both splits the LLM precision probe raised precision (FP 8→6 dev, 9→7
full-200) but lost more recall than it gained (FN 15→21 dev, 19→25 full-200).
The precision instruction dropped completed investigations the hybrid captures
— the same over-drop pattern the Rx probe #3 exhibited before its
emit-if-unsure fix, except here the safety clause did not fully prevent it
(modality completion is harder to judge contextually than AED identity).

## Why the inversion is Rx-specific, not general

The Rx inversion worked because of a specific conjunction that does NOT hold
for Investigations:

1. **Rx's deterministic producer had a structural precision weakness** — its
   bare AED lexicon over-captures non-AED comorbidity drugs (cardiac/diabetes
   meds) on the broader full-200 test surface, where such mentions are more
   prevalent. The LLM's contextual AED judgment fixed this **without a recall
   cost** (TP 270→271 on full-200).
2. **Inv's hybrid lane has no analogous exploitable weakness.** Its
   arbitration layer handles BOTH recall (the MRI-crowds-EEG recovery that the
   dedicated LLM lane could not match, hypothesis 2026-07-01) AND precision
   (planned-investigation drops via the convention layer's
   `_PLANNED_INVESTIGATION_EVIDENCE` gate). The LLM precision probe can only
   help precision, and on Inv that help always costs more recall than it gains
   — on both splits.

The mechanism asymmetry: Rx's deterministic producer was a pure deterministic
lane with a lexicon blind spot; Inv's producer is a hybrid lane whose
arbitration already covers the precision surface the LLM was probing. There is
no failure-mode axis where the LLM targets something the hybrid doesn't
already handle.

## Implication for the paper

This **reinforces the 07-03 Rx comparator's caveat** ("the deterministic lane
is competitive with but not strictly better than a tuned LLM on Prescription")
rather than extending it. The Rx inversion is now confirmed to be a
Prescription-specific finding about one family's lexicon blind spot, not a
general property of the v08 architecture's deterministic-vs-LLM lane choice.

The honest paper framing is strengthened: the v08 architecture's hybrid lanes
(Diagnosis, SF, Investigations) are robust to LLM-only replacement on both
splits; only the purely-deterministic Prescription lane has the split-fragile
property, and that traces to a specific lexicon gap (non-AED over-extraction),
not to a general deterministic-vs-LLM tradeoff.

## Provenance

- LLM artifacts: `experiments/exectv2_llm_inv_tuned_extractor_{dev140,full200}_20260703.jsonl`
- Baseline/treatment assemblies: `experiments/exectv2_v08_{dev140,full200}_inv_{hybrid_baseline,llm_tuned_treatment}_20260703.json{l,.json}`
- Reports: `docs/experiments/exectv2/investigations/exectv2_v08_{dev140,full200}_inv_{...}_2026-07-03.md`
- Script: `scripts/run_exectv2_v08_inv_llm_vs_hybrid.py`
- Call counts: dev140 140 calls (then cached), full-200 60 fresh (140 cached).
