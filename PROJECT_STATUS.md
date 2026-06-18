# Project Status

Last updated: 2026-06-18

## Active Objective

ExECTv2 is the forward workstream, focused on the LLM-first essential
clinical-detail question in
`docs/plans/exectv2/11_llm_first_essential_clinical_evaluation_plan.md`.
Plan 11 is executed as an analysis-only replay, but its corrected interpretation
is conservative: the single all-entities LLM pass is useful for some families,
not a sufficient LLM-first architecture.

Use the Gan 2026 closeout discipline as the template: source-near state, exact
evidence, component attribution, benchmark-format ablations, and family-aware
promotion gates.

## Current Dev140 Readout

Plan 11 now reports the primary ExECTv2 essential headline as CUI-free and
restricted to Prescription, SeizureFrequency, Diagnosis, EpilepsyCause, and
Investigations. Non-essential all-nine families are diagnostic only.

| Architecture | Ownership | Essential F1 | P | R | Notes |
| --- | --- | ---: | ---: | ---: | --- |
| deterministic_all9 | `rules_only` | 0.604 | 0.676 | 0.546 | comparator/projection substrate |
| hybrid_all_entities | `hybrid` | 0.550 | 0.559 | 0.542 | candidate-set + verify |
| llm_only_all_entities | `llm_first` | 0.422 | 0.478 | 0.379 | collapses on SF and EpilepsyCause |

LLM-first per-family F1: Prescription `0.747`, Investigations `0.748`,
Diagnosis concept-only `0.316`, SeizureFrequency `0.012`, EpilepsyCause `0.000`.
Evidence is exact source-substring for `743/743` emitted essential mentions, so
the active failure is clinical-detail selection/coverage rather than evidence
citation absence.

## Recent Context

- Plan 11 originally over-aggregated all-nine headline entities and overclaimed
  certainty/CUI conclusions. The implementation and readouts now separate the
  five-family primary headline, CUI-projected companion score, evidence/error
  diagnostics, and CUI missing mappings.
- Certainty remains a likely deterministic projection layer, but only a
  diagnostic modal/default audit exists so far. Stronger claim language requires
  explicit annotation-guideline projection rules over gold or evidence-correct
  rows.
- CUI is benchmark-format projection for LLM-first claims. The in-sample
  projector reaches coverage `0.753` and correctness `0.944`, with `365`
  missing-mapping mentions across `184` concepts.
- A fresh broad single-call run is not the next step. The current LLM pass is
  the wrong shape for SeizureFrequency; route SF to an event/state schema and
  keep Prescription/Investigations/Diagnosis as reusable LLM-owned components.

## Active Priorities

1. Complete the certainty projection audit with explicit guideline rules.
2. Redesign SeizureFrequency around a structured event/state schema rather than
   another broad all-family prompt.
3. Turn the coarse Plan 11 error taxonomy into row-level miss/selection slices
   for the five essential families.
4. Keep benchmark-facing full-200 work blocked until dev evidence beats the
   current comparators and a frozen protocol is predeclared.

## Work Board

### Now

- Implement per-entity certainty/negation projection rules and score them on
  gold or evidence-correct rows.
- Draft the SF LLM-first event/state schema using the specialist SF candidate
  shape, with CUI/certainty outside the model-owned headline.
- Build a row-level essential-family error ledger splitting candidate misses,
  wrong detail selections, projection gaps, and evidence failures.

### Next

- Expand the CUI missing-mapping ledger into prioritized lexicon additions and
  mark which are benchmark-format only.
- Predeclare a family-routed LLM-first comparison: single pass for
  Prescription/Investigations/Diagnosis plus SF event/state route.
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
  are `test_exectv2_projection_gap_ledger.py` total drift (`340` expected vs
  `343`) and two `test_gan2026_validation_test_gap_protocol.py` path/protocol
  assertions. Full `ruff check .` also reports pre-existing style debt outside
  the touched Plan 11 files.

### Done Recently

- 2026-06-18: Corrected Plan 11 implementation and readouts: essential-only
  CUI-free headline, CUI-projected companion score, diagnostic certainty
  language, explicit CUI missing mappings, evidence/error summaries, updated
  run index, and regression tests.
- 2026-06-18: Completed the candidate-ID action version of the single
  family-conditioned prompt. It matches current per-family prompts on dev140 but
  remains a hybrid comparator because deterministic candidates own generation.
- 2026-06-18: Completed SF unknown suppression v0.7, improving SF dev140
  `0.763` -> `0.782` without active-rate or seizure-free recall regression.
- 2026-06-17: Closed the Gan strand, completed the deterministic all-9 ExECTv2
  substrate, and built the reusable all-entity projection-gap ledger.

## Guardrails

- Do not inspect Gan `test450` row-level failures, rationales, evidence,
  selected events, or transitions for development.
- Keep architecture claims attribution-clean across `rules_only`, `llm_first`,
  and `hybrid`.
- Treat deterministic certainty, CUI, and benchmark-format repairs as controlled
  variables, not hidden implementation detail.
- Treat Diagnosis and SF as architecture-characterization surfaces until a new
  evidence-selection/event-state design is proposed.

## Core Artifacts

Start with
`docs/experiments/exectv2/key_entities/exectv2_llm_first_essential_evaluation_2026-06-18.md`
and
`docs/plans/exectv2/11_llm_first_essential_clinical_evaluation_plan.md`.
The broader synthesis remains
`docs/research/exectv2_final_key_family_architecture_synthesis_2026-06-18.md`.
