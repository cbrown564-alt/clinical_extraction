# Project Status

Last updated: 2026-06-18

## Active Objective

ExECTv2 is the forward workstream, focused on the LLM-first essential
clinical-detail question in Plan 11. The corrected readout is conservative: the
single all-entities LLM pass is useful for some families, not a sufficient
LLM-first architecture. Use Gan 2026 closeout discipline: source-near state,
exact evidence, component attribution, benchmark-format ablations, and
family-aware promotion gates.

## Current Dev140 Readout

Primary ExECTv2 essential headline is CUI-free over Prescription,
SeizureFrequency, Diagnosis, EpilepsyCause, and Investigations. Essential F1:
deterministic_all9 `0.604`, hybrid_all_entities `0.550`, llm_only_all_entities
`0.422`. The single LLM pass is useful for Prescription `0.747` and
Investigations `0.748`, weak for Diagnosis concept-only `0.316`, and collapsed
for SeizureFrequency `0.012` and EpilepsyCause `0.000`. Evidence is exact for
`743/743` emitted essential mentions, so the active failure is clinical-detail
selection/coverage rather than citation absence.

## Recent Context

- Plan 11 now separates the five-family primary headline, CUI-projected
  companion score, evidence/error diagnostics, explicit guideline-rule
  certainty projection, and CUI missing mappings.
- Certainty is a deterministic adapter-layer candidate with measured rules:
  List 2 certainty triggers plus default affirmed negation score at
  `0.81`-`1.00` certainty accuracy by guideline-owned family and `0.99`-`1.00`
  negation accuracy. It remains outside the LLM-owned headline.
- CUI is benchmark-format projection for LLM-first claims. The in-sample
  projector reaches coverage `0.753` and correctness `0.944`, with `365`
  missing-mapping mentions across `184` concepts.
- A fresh broad single-call run is not the next step. The current LLM pass is
  the wrong shape for SeizureFrequency; route SF to an event/state schema and
  keep Prescription/Investigations/Diagnosis as reusable LLM-owned components.

## Active Priorities

1. Redesign SeizureFrequency around a structured event/state schema rather than
   another broad all-family prompt.
2. Turn the coarse Plan 11 error taxonomy into row-level miss/selection slices
   for the five essential families.
3. Expand CUI missing mappings only as benchmark-format lexicon work, not as
   LLM-owned clinical reasoning.
4. Keep benchmark-facing full-200 work blocked until dev evidence beats the
   current comparators and a frozen protocol is predeclared.

## Work Board

### Now

- Draft the SF LLM-first event/state schema using the specialist SF candidate
  shape, with CUI/certainty outside the model-owned headline.
- Build a row-level essential-family error ledger splitting candidate misses,
  wrong detail selections, projection gaps, and evidence failures.

### Next

- Predeclare a family-routed LLM-first comparison: single pass for
  Prescription/Investigations/Diagnosis plus SF event/state route.
- Expand the CUI missing-mapping ledger into prioritized lexicon additions and
  mark which are benchmark-format only.
- Add a focused evidence-validity table to the Plan 11 readout by family, not
  only overall.
- Decide whether EpilepsyCause needs a targeted extractor or should remain a
  low-frequency diagnostic family.

### Blocked

- Gan holdout-facing reruns, row-level test analysis, or post-test tuning remain
  blocked without explicit authorization and a frozen protocol.
- New ExECTv2 full-200 audits are blocked until benchmark-beating GPT-first dev
  evidence and a predeclared aggregate readout.
- Full-suite verification is not clean at repo head: current unrelated failures
  are projection-gap total drift and Gan validation path/protocol assertions.

### Done Recently

- 2026-06-18: Completed Plan 11 projection-layer cleanup: essential-only
  CUI-free headline, CUI-projected companion score, explicit guideline-rule
  certainty/negation audit, CUI missing mappings, evidence/error summaries, and
  regression tests.
- 2026-06-18: Completed the candidate-ID action prompt, SF unknown suppression
  v0.7, and the deterministic all-9 ExECTv2 substrate.

## Guardrails

- Do not inspect Gan `test450` row-level failures, rationales, evidence,
  selected events, or transitions for development.
- Keep claims attribution-clean across `rules_only`, `llm_first`, and `hybrid`;
  deterministic certainty/CUI/format repairs are controlled projection layers.

## Core Artifacts

Start with the Plan 11 readout, Plan 11 itself, and the final key-family
architecture synthesis in `docs/research/`.
