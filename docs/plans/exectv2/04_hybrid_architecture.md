# Satellite 04 — Hybrid Architecture

Parent: [[00_overarching_implementation_plan]] · Phases 4 & 6
Status: planning. Dev-split only until the Phase 7 audit.

## Purpose

Build the hybrid ExECTv2 extractor — deterministic where representation,
arithmetic, and format belong; LLM where clinical judgment belongs. This is the
architecture that operationalizes the project's central lesson: representation
loss is mostly a normalization/projection problem, not a clinical-judgment
problem. It should be the strongest of the three on the hard entities (SF,
Patient History).

## 1. Shape (reset-native hybrid, ported)

Mirror Gan 2026's `hybrid` (`reset_clinical_assessment_pipeline`):

```
raw letter text
  → deterministic candidate extraction   (rule families → high-recall candidate mentions w/ evidence)
  → LLM clinical assessment              (select/judge among candidates; assign clinical interpretation)
  → deterministic Normalize              (shared epilepsy normalizer → attribute values)
  → Select/Render                        (emit PredictedMention set)
  → Verify / Route                       (evidence + plausibility gate; route the unresolved)
  → adapter → PredictedLetter
```

The LLM's job is **selection and assessment over a pre-extracted candidate set**,
not open-text parsing and not value formatting. Deterministic stages own
candidate recall, normalization, and format.

A second hybrid variant (optional, mirroring `hybrid_structured_events`):
**LLM extracts structured mentions from raw text → deterministic
normalize/render**, no candidate set, no routing. The gap between the two
variants measures LLM-task-design and routing cost — a clean ablation.

## 2. Candidate set (reuse the live-wiring lesson)

Gan 2026 learned to generate candidate sets **live per record** (deterministic
extraction ∪ LLM-extracted candidates), not from a static precomputed file
(plan §8a). Build ExECTv2's candidate stage live from the start:

- deterministic candidate extraction = the satellite-02 Extract stage run in
  high-recall mode (over-generate; the assessment stage prunes)
- optional LLM candidate extractor for recall the rules miss
- union into the candidate set the assessment LLM sees

This avoids the 250-row-scoped surface mistake; every dev letter gets a real
candidate set.

## 3. Clinical assessment stage

The LLM receives the candidate set (with evidence) and, per the closed output
contract:

- selects which candidates are real gold-worthy mentions
- assigns the clinical interpretation (current vs historical, seizure-free vs
  active, cluster vs intra-cluster rate)
- emits `uncertainty_flags` from the closed vocabulary and an
  `aggregation_policy` from its enum, each governed by an in-prompt decision
  table (Gan 2026 Phase 3 pre-conditions B & C)

Prompt language obeys ADR 0015; `PROMPT_VERSION` discipline applies.

## 4. Routing / verification

A lightweight verify stage checks evidence presence/substring and clinically
implausible combinations, and **routes** (does not silently fix) mentions it
cannot resolve. The routed-mention taxonomy is a first-class diagnostic
(satellite 07). No verifier-written labels (guardrail).

## 5. Deliverables & tests

- `hybrid/candidate_set.py` (live union), `hybrid/clinical_assessment.py`,
  reuse of shared normalizer + deterministic render, `hybrid/verify_route.py`
- The optional `hybrid_structured_events`-style variant
- Contract tests on candidate-set shape, assessment output, routing decisions
- Pilot + dev-split runs registered; per-entity dev F1 + routed-row taxonomy

## 6. Exit criteria

- **Phase 4**: hybrid scores SF on dev with live candidate sets, 0 unexplained
  failures; routed-row taxonomy produced; per-item/per-letter F1 reported.
- **Phase 6**: extended to all 9 entities; overall dev F1 reported per model;
  the two hybrid variants compared.
